"""
deploy_motion.py  —  Desplegador para políticas de movimiento periódico G1 29-DOF
Soporta políticas entrenadas en HumanoidVerse (Genesis/IsaacGym) con fase periódica.

  num_obs=62  →  muñecas: dof_pos[29]+phase[1]+gravity[3]+q_target[29]
  num_obs=94  →  agacharse: ang_vel[3]+dof_pos[29]+dof_vel[29]+phase[1]+gravity[3]+q_target[29]

Control modes:
  hybrid_arms:       DOF 15-28 (brazos) por política; DOF 0-14 fijos en default
  hybrid_legs_waist: DOF 0-14 (piernas+cintura) por política; DOF 15-28 fijos en default
  full:              los 29 DOF por política

Uso:
    python deploy_motion.py <interfaz_red> <config.yaml>
    python deploy_motion.py enp7s0 motion_agacharse.yaml
    python deploy_motion.py enp7s0 motion_munecas.yaml

Secuencia:
    1. Apagar sport_mode desde la app Unitree (⚠️ OBLIGATORIO antes de control bajo nivel)
    2. Robot encendido, colgado o en suelo con arnés de seguridad
    3. Ejecutar script → estado zero torque
    4. START en mando  → mueve a posición default (2 s)
    5. A en mando      → política activa (movimiento periódico, warmup 3 s)
    6. SELECT          → salida suave (modo amortiguamiento)

Capas de seguridad implementadas:
    1. Tilt detection  — parada automática si inclinación > tilt_limit
    2. Joint limits    — target_q clampeado a límites oficiales Unitree URDF
    3. Warmup ramp     — action_scale × 0→1 durante los primeros warmup_s segundos
"""
from pathlib import Path
REPO_ROOT = str(Path(__file__).parent.parent)
import time
import math
import numpy as np
import torch
import yaml

from unitree_sdk2py.core.channel import ChannelPublisher, ChannelFactoryInitialize
from unitree_sdk2py.core.channel import ChannelSubscriber
from unitree_sdk2py.idl.default import (
    unitree_hg_msg_dds__LowCmd_,
    unitree_hg_msg_dds__LowState_,
)
from unitree_sdk2py.idl.unitree_hg.msg.dds_ import LowCmd_   as LowCmdHG
from unitree_sdk2py.idl.unitree_hg.msg.dds_ import LowState_ as LowStateHG
from unitree_sdk2py.utils.crc import CRC

from common.command_helper import create_damping_cmd, create_zero_cmd, init_cmd_hg, MotorMode
from common.rotation_helper import get_gravity_orientation
from common.remote_controller import RemoteController, KeyMap

_G = "\033[92m"; _Y = "\033[93m"; _R = "\033[91m"; _B = "\033[94m"; _E = "\033[0m"

N_DOF = 29

# Nombres de joints en orden de motor 0-28 (igual que G1JointIndex del SDK)
DOF_NAMES = [
    "left_hip_pitch_joint",      "left_hip_roll_joint",       "left_hip_yaw_joint",
    "left_knee_joint",           "left_ankle_pitch_joint",    "left_ankle_roll_joint",
    "right_hip_pitch_joint",     "right_hip_roll_joint",      "right_hip_yaw_joint",
    "right_knee_joint",          "right_ankle_pitch_joint",   "right_ankle_roll_joint",
    "waist_yaw_joint",           "waist_roll_joint",          "waist_pitch_joint",
    "left_shoulder_pitch_joint", "left_shoulder_roll_joint",  "left_shoulder_yaw_joint",
    "left_elbow_joint",          "left_wrist_roll_joint",     "left_wrist_pitch_joint",
    "left_wrist_yaw_joint",
    "right_shoulder_pitch_joint","right_shoulder_roll_joint", "right_shoulder_yaw_joint",
    "right_elbow_joint",         "right_wrist_roll_joint",    "right_wrist_pitch_joint",
    "right_wrist_yaw_joint",
]

# Límites oficiales de articulaciones (fuente: Unitree g1_29dof.urdf)
_Q_MIN = np.array([
    -2.5307, -0.5236, -2.7576, -0.0873, -0.8727, -0.2618,   # L leg
    -2.5307, -2.9671, -2.7576, -0.0873, -0.8727, -0.2618,   # R leg
    -2.618,  -0.52,   -0.52,                                  # waist
    -3.0892, -1.5882, -2.618,  -1.0472, -1.9722, -1.6144, -1.6144,  # L arm
    -3.0892, -2.2515, -2.618,  -1.0472, -1.9722, -1.6144, -1.6144,  # R arm
], np.float32)

_Q_MAX = np.array([
     2.8798,  2.9671,  2.7576,  2.8798,  0.5236,  0.2618,   # L leg
     2.8798,  0.5236,  2.7576,  2.8798,  0.5236,  0.2618,   # R leg
     2.618,   0.52,    0.52,                                   # waist
     2.6704,  2.2515,  2.618,   2.0944,  1.9722,  1.6144,  1.6144,  # L arm
     2.6704,  1.5882,  2.618,   2.0944,  1.9722,  1.6144,  1.6144,  # R arm
], np.float32)


def _dict_to_pose(pose_dict: dict, default_q: np.ndarray) -> np.ndarray:
    """Convierte {joint_name: value} a array 29-dim partiendo de default_q."""
    pose = default_q.copy()
    for name, val in (pose_dict or {}).items():
        pose[DOF_NAMES.index(name)] = float(val)
    return pose


class MotionConfig:
    def __init__(self, path: str):
        with open(path) as f:
            c = yaml.safe_load(f)
        self.policy_path    = c["policy_path"].replace("{REPO_ROOT}", REPO_ROOT)
        self.control_dt     = float(c.get("control_dt", 0.02))
        self.lowcmd_topic   = c.get("lowcmd_topic",   "rt/lowcmd")
        self.lowstate_topic = c.get("lowstate_topic", "rt/lowstate")
        self.num_actions    = int(c["num_actions"])
        self.num_obs        = int(c["num_obs"])
        self.action_scale   = float(c["action_scale"])
        self.action_clip    = float(c.get("action_clip", 1.0))
        self.period_s       = float(c["period_s"])
        self.control_mode   = c.get("control_mode", "full")
        self.kps            = list(c["kps"])
        self.kds            = list(c["kds"])
        self.default_angles = np.array(c["default_angles"], np.float32)
        self.dof_vel_scale  = float(c.get("dof_vel_scale", 0.05))
        self.ang_vel_scale  = float(c.get("ang_vel_scale", 0.25))
        # Parámetros de seguridad
        self.warmup_s   = float(c.get("warmup_s",   3.0))   # ramp action 0→1
        self.tilt_limit = float(c.get("tilt_limit", -0.3))  # gravity_z umbral de caída

        self.pose_A = _dict_to_pose(c.get("pose_A", {}), self.default_angles)
        self.pose_B = _dict_to_pose(c.get("pose_B", {}), self.default_angles)

        if self.control_mode == "hybrid_arms":
            self.policy_dof_idx = list(range(15, 29))
            self.fixed_dof_idx  = list(range(0, 15))
        elif self.control_mode == "hybrid_legs_waist":
            self.policy_dof_idx = list(range(0, 15))
            self.fixed_dof_idx  = list(range(15, 29))
        else:
            self.policy_dof_idx = list(range(N_DOF))
            self.fixed_dof_idx  = []


class MotionController:
    def __init__(self, config: MotionConfig):
        self.cfg = config
        self.remote_controller = RemoteController()

        self.policy = torch.jit.load(config.policy_path)
        self.policy.eval()

        self.qj      = np.zeros(N_DOF, np.float32)
        self.dqj     = np.zeros(N_DOF, np.float32)
        self.action  = np.zeros(config.num_actions, np.float32)
        self.counter = 0

        self.low_cmd       = unitree_hg_msg_dds__LowCmd_()
        self.low_state     = unitree_hg_msg_dds__LowState_()
        self.mode_pr_      = MotorMode.PR
        self.mode_machine_ = 0

        self._lowcmd_pub = ChannelPublisher(config.lowcmd_topic, LowCmdHG)
        self._lowcmd_pub.Init()
        self._lowstate_sub = ChannelSubscriber(config.lowstate_topic, LowStateHG)
        self._lowstate_sub.Init(self._state_handler, 10)

        self._wait_for_state()
        init_cmd_hg(self.low_cmd, self.mode_machine_, self.mode_pr_)

    def _state_handler(self, msg: LowStateHG):
        self.low_state     = msg
        self.mode_machine_ = msg.mode_machine
        self.remote_controller.set(msg.wireless_remote)

    def _send(self):
        self.low_cmd.crc = CRC().Crc(self.low_cmd)
        self._lowcmd_pub.Write(self.low_cmd)

    def _wait_for_state(self):
        while self.low_state.tick == 0:
            time.sleep(self.cfg.control_dt)
        print("Conectado al robot.")

    def _read_joints(self):
        for i in range(N_DOF):
            self.qj[i]  = self.low_state.motor_state[i].q
            self.dqj[i] = self.low_state.motor_state[i].dq

    def _compute_phase(self) -> tuple:
        """Devuelve (phase_sig, q_target) para el timestep actual."""
        t         = self.counter * self.cfg.control_dt
        phase_sig = math.sin(2.0 * math.pi * t / self.cfg.period_s)
        alpha     = (phase_sig + 1.0) / 2.0
        q_target  = (1.0 - alpha) * self.cfg.pose_A + alpha * self.cfg.pose_B
        return phase_sig, q_target

    def _build_obs(self, q_target: np.ndarray, phase_sig: float,
                   gravity: np.ndarray, ang_vel: np.ndarray) -> np.ndarray:
        """
        Construye el vector de obs en orden ALFABÉTICO (HumanoidVerse sorted(obs_keys)).

        62-dim: dof_pos[0:29] | phase[29] | gravity[30:33] | q_target[33:62]
        94-dim: ang_vel[0:3] | dof_pos[3:32] | dof_vel[32:61] | phase[61] | gravity[62:65] | q_target[65:94]
        """
        if self.cfg.num_obs == 62:
            obs = np.empty(62, np.float32)
            obs[0:29]  = self.qj
            obs[29]    = float(phase_sig)
            obs[30:33] = gravity
            obs[33:62] = q_target
        elif self.cfg.num_obs == 94:
            obs = np.empty(94, np.float32)
            obs[0:3]   = ang_vel * self.cfg.ang_vel_scale
            obs[3:32]  = self.qj
            obs[32:61] = self.dqj * self.cfg.dof_vel_scale
            obs[61]    = float(phase_sig)
            obs[62:65] = gravity
            obs[65:94] = q_target
        else:
            raise ValueError(f"num_obs={self.cfg.num_obs} no soportado (usar 62 o 94)")
        return obs

    def _emergency_stop(self, reason: str):
        print(f"\n{_R}⚠ PARADA DE EMERGENCIA: {reason}{_E}")
        create_damping_cmd(self.low_cmd)
        self._send()

    # ── Secuencia de arranque ─────────────────────────────────────────────

    def zero_torque_state(self):
        print("Torque cero. Presiona START para continuar...")
        while self.remote_controller.button[KeyMap.start] != 1:
            create_zero_cmd(self.low_cmd)
            self._send()
            time.sleep(self.cfg.control_dt)

    def move_to_default_pos(self):
        print("Moviendo a posición default (2 s)...")
        steps = int(2.0 / self.cfg.control_dt)
        init  = np.array([self.low_state.motor_state[i].q for i in range(N_DOF)], np.float32)
        for step in range(steps):
            alpha = step / steps
            for i in range(N_DOF):
                tgt = float(init[i] * (1.0 - alpha) + self.cfg.default_angles[i] * alpha)
                self.low_cmd.motor_cmd[i].q   = np.clip(tgt, _Q_MIN[i], _Q_MAX[i])
                self.low_cmd.motor_cmd[i].qd  = 0
                self.low_cmd.motor_cmd[i].kp  = self.cfg.kps[i]
                self.low_cmd.motor_cmd[i].kd  = self.cfg.kds[i]
                self.low_cmd.motor_cmd[i].tau = 0
            self._send()
            time.sleep(self.cfg.control_dt)

    def default_pos_state(self):
        print("Posición default lista. Presiona A para activar movimiento...")
        while self.remote_controller.button[KeyMap.A] != 1:
            for i in range(N_DOF):
                self.low_cmd.motor_cmd[i].q   = float(self.cfg.default_angles[i])
                self.low_cmd.motor_cmd[i].qd  = 0
                self.low_cmd.motor_cmd[i].kp  = self.cfg.kps[i]
                self.low_cmd.motor_cmd[i].kd  = self.cfg.kds[i]
                self.low_cmd.motor_cmd[i].tau = 0
            self._send()
            time.sleep(self.cfg.control_dt)

    # ── Paso de control ───────────────────────────────────────────────────

    def run(self) -> bool:
        """
        Ejecuta un paso de control. Devuelve False si se activa parada de emergencia.

        Capas de seguridad (en orden de ejecución):
          1. Tilt detection  — para si gravity_z > tilt_limit (≈ inclinación > 72°)
          2. Joint limits    — clampea target_q a límites oficiales del URDF
          3. Warmup ramp     — escala acciones 0→1 durante los primeros warmup_s
        """
        self._read_joints()

        # Capa 1: Tilt detection
        quat    = np.array(self.low_state.imu_state.quaternion, np.float32)
        ang_vel = np.array(self.low_state.imu_state.gyroscope,  np.float32)
        gravity = get_gravity_orientation(quat)
        if gravity[2] > self.cfg.tilt_limit:
            self._emergency_stop(
                f"inclinación excesiva (gravity_z={gravity[2]:.2f} > {self.cfg.tilt_limit})"
            )
            return False

        phase_sig, q_target = self._compute_phase()
        obs = self._build_obs(q_target, phase_sig, gravity, ang_vel)

        obs_t = torch.from_numpy(obs).unsqueeze(0)
        with torch.no_grad():
            raw = self.policy(obs_t).squeeze().numpy()
        self.action = np.clip(raw, -self.cfg.action_clip, self.cfg.action_clip)

        # Capa 3: Warmup ramp
        t_elapsed = self.counter * self.cfg.control_dt
        ramp = min(1.0, t_elapsed / self.cfg.warmup_s) if self.cfg.warmup_s > 0 else 1.0

        target_q = q_target + self.action * self.cfg.action_scale * ramp

        # Capa 2: Joint limits
        target_q = np.clip(target_q, _Q_MIN, _Q_MAX)

        for i in self.cfg.policy_dof_idx:
            self.low_cmd.motor_cmd[i].q   = float(target_q[i])
            self.low_cmd.motor_cmd[i].qd  = 0
            self.low_cmd.motor_cmd[i].kp  = self.cfg.kps[i]
            self.low_cmd.motor_cmd[i].kd  = self.cfg.kds[i]
            self.low_cmd.motor_cmd[i].tau = 0

        for i in self.cfg.fixed_dof_idx:
            self.low_cmd.motor_cmd[i].q   = float(self.cfg.default_angles[i])
            self.low_cmd.motor_cmd[i].qd  = 0
            self.low_cmd.motor_cmd[i].kp  = self.cfg.kps[i]
            self.low_cmd.motor_cmd[i].kd  = self.cfg.kds[i]
            self.low_cmd.motor_cmd[i].tau = 0

        self._send()
        self.counter += 1
        time.sleep(self.cfg.control_dt)
        return True


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("net",    type=str, help="interfaz de red (ej. enp7s0)")
    parser.add_argument("config", type=str, help="nombre del config en despliegue/configs/")
    args = parser.parse_args()

    cfg_path = f"{REPO_ROOT}/despliegue/configs/{args.config}"
    config   = MotionConfig(cfg_path)

    print(f"\n{_B}{'='*64}{_E}")
    print(f"{_B}  DEPLOY MOTION G1 29-DOF{_E}")
    print(f"{_B}{'='*64}{_E}")
    print(f"  Política     : {Path(config.policy_path).name}")
    print(f"  num_obs={config.num_obs}   num_actions={config.num_actions}")
    print(f"  control_mode : {config.control_mode}")
    print(f"  period_s={config.period_s}   control_dt={config.control_dt} s  ({1/config.control_dt:.0f} Hz)")
    print(f"  warmup_s={config.warmup_s}   tilt_limit={config.tilt_limit}")
    print(f"{_R}{'='*64}{_E}")
    print(f"{_R}  ⚠  APAGAR sport_mode en la app Unitree ANTES de continuar  ⚠{_E}")
    print(f"{_R}  ⚠  Primera ejecución: usar arnés de seguridad              ⚠{_E}")
    print(f"{_R}{'='*64}{_E}\n")

    ChannelFactoryInitialize(0, args.net)
    ctrl = MotionController(config)

    ctrl.zero_torque_state()
    ctrl.move_to_default_pos()
    ctrl.default_pos_state()

    print(f"\n{_G}Movimiento periódico activo.  SELECT para salir.{_E}")
    print(f"  Warmup: {config.warmup_s} s  |  Tilt stop: gravity_z > {config.tilt_limit}\n")

    while True:
        try:
            ok = ctrl.run()
            if not ok:
                break
            if ctrl.remote_controller.button[KeyMap.select] == 1:
                break
        except KeyboardInterrupt:
            break

    create_damping_cmd(ctrl.low_cmd)
    ctrl._send()
    print(f"\n{_Y}Salida — modo amortiguamiento activo.{_E}")
