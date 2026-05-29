"""
deploy_real_dual.py  —  Desplegador dual para robot físico G1
Soporta dos políticas seleccionadas por config:

  policy_type: "motion"  →  47 dims (legged_gym original, sin/cos phase)
  policy_type: "hv"      →  48 dims (HumanoidVerse, base_lin_vel, orden alfabético)

Uso:
    python deploy_real_dual.py <interfaz_red> <config.yaml>
    python deploy_real_dual.py eth0 g1_motion.yaml
    python deploy_real_dual.py eth0 g1_hv.yaml

Secuencia:
    1. Robot encendido, colgado o tumbado en suelo plano
    2. Ejecutar script → estado zero torque
    3. START en mando  → se mueve a posición inicial (2 s)
    4. A en mando      → política activa
    5. L-stick fwd/back=vx  L-stick left/right=vy  R-stick left/right=wz
    6. SELECT          → salida suave (modo amortiguamiento)
"""
from pathlib import Path
import sys
REPO_ROOT = str(Path(__file__).parent.parent)
import time
import numpy as np
import torch
import yaml

from unitree_sdk2py.core.channel import ChannelPublisher, ChannelFactoryInitialize
from unitree_sdk2py.core.channel import ChannelSubscriber
from unitree_sdk2py.idl.default import (
    unitree_hg_msg_dds__LowCmd_,
    unitree_hg_msg_dds__LowState_,
    unitree_go_msg_dds__LowCmd_,
    unitree_go_msg_dds__LowState_,
)
from unitree_sdk2py.idl.unitree_hg.msg.dds_ import LowCmd_ as LowCmdHG
from unitree_sdk2py.idl.unitree_go.msg.dds_ import LowCmd_ as LowCmdGo
from unitree_sdk2py.idl.unitree_hg.msg.dds_ import LowState_ as LowStateHG
from unitree_sdk2py.idl.unitree_go.msg.dds_ import LowState_ as LowStateGo
from unitree_sdk2py.utils.crc import CRC

from common.command_helper import (
    create_damping_cmd, create_zero_cmd,
    init_cmd_hg, init_cmd_go, MotorMode,
)
from common.rotation_helper import get_gravity_orientation, transform_imu_data
from common.remote_controller import RemoteController, KeyMap

_G = "\033[92m"; _Y = "\033[93m"; _R = "\033[91m"; _B = "\033[94m"; _E = "\033[0m"

# Constante de tiempo del integrador de velocidad lineal (política HV).
# Con control_dt=0.02 y DECAY=0.95: τ ≈ dt/(1-decay) = 0.4 s — suficiente
# para seguir pasos pero evitar drift acumulado durante varias decenas de segundos.
_LINVEL_DECAY = 0.95


class DualConfig:
    def __init__(self, path: str):
        with open(path) as f:
            c = yaml.safe_load(f)
        root = REPO_ROOT
        self.policy_type               = c["policy_type"]
        self.control_dt                = c["control_dt"]
        self.msg_type                  = c["msg_type"]
        self.imu_type                  = c.get("imu_type", "pelvis")
        self.weak_motor                = c.get("weak_motor", [])
        self.lowcmd_topic              = c["lowcmd_topic"]
        self.lowstate_topic            = c["lowstate_topic"]
        self.policy_path               = c["policy_path"].replace("{REPO_ROOT}", root)
        self.leg_joint2motor_idx       = c["leg_joint2motor_idx"]
        self.kps                       = c["kps"]
        self.kds                       = c["kds"]
        self.default_angles            = np.array(c["default_angles"], np.float32)
        self.arm_waist_joint2motor_idx = c["arm_waist_joint2motor_idx"]
        self.arm_waist_kps             = c["arm_waist_kps"]
        self.arm_waist_kds             = c["arm_waist_kds"]
        self.arm_waist_target          = np.array(c["arm_waist_target"], np.float32)
        self.ang_vel_scale             = c["ang_vel_scale"]
        self.dof_pos_scale             = c["dof_pos_scale"]
        self.dof_vel_scale             = c["dof_vel_scale"]
        self.action_scale              = c["action_scale"]
        self.num_actions               = c["num_actions"]
        self.num_obs                   = c["num_obs"]
        self.max_cmd                   = np.array(c["max_cmd"], np.float32)
        # motion-only
        self.cmd_scale = np.array(c.get("cmd_scale", [1.0, 1.0, 1.0]), np.float32)
        # hv-only
        self.lin_vel_scale = float(c.get("lin_vel_scale", 2.0))


class DualController:
    def __init__(self, config: DualConfig):
        self.config = config
        self.remote_controller = RemoteController()

        self.policy = torch.jit.load(config.policy_path)
        self.policy.eval()

        self.qj          = np.zeros(config.num_actions, np.float32)
        self.dqj         = np.zeros(config.num_actions, np.float32)
        self.action      = np.zeros(config.num_actions, np.float32)
        self.obs         = np.zeros(config.num_obs,     np.float32)
        self.counter     = 0
        self.lin_vel_est = np.zeros(3, np.float32)   # solo usada por HV

        if config.msg_type == "hg":
            self.low_cmd       = unitree_hg_msg_dds__LowCmd_()
            self.low_state     = unitree_hg_msg_dds__LowState_()
            self.mode_pr_      = MotorMode.PR
            self.mode_machine_ = 0
            self._lowcmd_pub = ChannelPublisher(config.lowcmd_topic, LowCmdHG)
            self._lowcmd_pub.Init()
            self._lowstate_sub = ChannelSubscriber(config.lowstate_topic, LowStateHG)
            self._lowstate_sub.Init(self._hg_handler, 10)
        elif config.msg_type == "go":
            self.low_cmd   = unitree_go_msg_dds__LowCmd_()
            self.low_state = unitree_go_msg_dds__LowState_()
            self._lowcmd_pub = ChannelPublisher(config.lowcmd_topic, LowCmdGo)
            self._lowcmd_pub.Init()
            self._lowstate_sub = ChannelSubscriber(config.lowstate_topic, LowStateGo)
            self._lowstate_sub.Init(self._go_handler, 10)
        else:
            raise ValueError(f"msg_type desconocido: {config.msg_type}")

        self._wait_for_state()

        if config.msg_type == "hg":
            init_cmd_hg(self.low_cmd, self.mode_machine_, self.mode_pr_)
        else:
            init_cmd_go(self.low_cmd, weak_motor=config.weak_motor)

    # ── SDK handlers ─────────────────────────────────────────────────────

    def _hg_handler(self, msg: LowStateHG):
        self.low_state     = msg
        self.mode_machine_ = msg.mode_machine
        self.remote_controller.set(msg.wireless_remote)

    def _go_handler(self, msg: LowStateGo):
        self.low_state = msg
        self.remote_controller.set(msg.wireless_remote)

    def _send(self):
        self.low_cmd.crc = CRC().Crc(self.low_cmd)
        self._lowcmd_pub.Write(self.low_cmd)

    def _wait_for_state(self):
        while self.low_state.tick == 0:
            time.sleep(self.config.control_dt)
        print("Conectado al robot.")

    # ── Estados de arranque ───────────────────────────────────────────────

    def zero_torque_state(self):
        print("Torque cero. Presiona START para continuar...")
        while self.remote_controller.button[KeyMap.start] != 1:
            create_zero_cmd(self.low_cmd)
            self._send()
            time.sleep(self.config.control_dt)

    def move_to_default_pos(self):
        print("Moviendo a posición inicial (2 s)...")
        steps  = int(2.0 / self.config.control_dt)
        d_idx  = self.config.leg_joint2motor_idx + self.config.arm_waist_joint2motor_idx
        kps    = self.config.kps + self.config.arm_waist_kps
        kds    = self.config.kds + self.config.arm_waist_kds
        target = np.concatenate([self.config.default_angles, self.config.arm_waist_target])
        init   = np.array([self.low_state.motor_state[i].q for i in d_idx], np.float32)
        for step in range(steps):
            alpha = step / steps
            for j, idx in enumerate(d_idx):
                self.low_cmd.motor_cmd[idx].q   = float(init[j] * (1 - alpha) + target[j] * alpha)
                self.low_cmd.motor_cmd[idx].qd  = 0
                self.low_cmd.motor_cmd[idx].kp  = kps[j]
                self.low_cmd.motor_cmd[idx].kd  = kds[j]
                self.low_cmd.motor_cmd[idx].tau = 0
            self._send()
            time.sleep(self.config.control_dt)

    def default_pos_state(self):
        print("Posición inicial lista. Presiona A para activar política...")
        while self.remote_controller.button[KeyMap.A] != 1:
            for i, idx in enumerate(self.config.leg_joint2motor_idx):
                self.low_cmd.motor_cmd[idx].q   = float(self.config.default_angles[i])
                self.low_cmd.motor_cmd[idx].qd  = 0
                self.low_cmd.motor_cmd[idx].kp  = self.config.kps[i]
                self.low_cmd.motor_cmd[idx].kd  = self.config.kds[i]
                self.low_cmd.motor_cmd[idx].tau = 0
            for i, idx in enumerate(self.config.arm_waist_joint2motor_idx):
                self.low_cmd.motor_cmd[idx].q   = float(self.config.arm_waist_target[i])
                self.low_cmd.motor_cmd[idx].qd  = 0
                self.low_cmd.motor_cmd[idx].kp  = self.config.arm_waist_kps[i]
                self.low_cmd.motor_cmd[idx].kd  = self.config.arm_waist_kds[i]
                self.low_cmd.motor_cmd[idx].tau = 0
            self._send()
            time.sleep(self.config.control_dt)

    # ── Constructores de observación ──────────────────────────────────────

    def _read_joints_and_imu(self):
        """Lee articulaciones e IMU; aplica transformación si IMU está en torso."""
        for i, idx in enumerate(self.config.leg_joint2motor_idx):
            self.qj[i]  = self.low_state.motor_state[idx].q
            self.dqj[i] = self.low_state.motor_state[idx].dq
        quat    = np.array(self.low_state.imu_state.quaternion,  np.float32)
        ang_vel = np.array(self.low_state.imu_state.gyroscope,   np.float32)
        if self.config.imu_type == "torso":
            waist_idx = self.config.arm_waist_joint2motor_idx[0]
            wy  = self.low_state.motor_state[waist_idx].q
            wdy = self.low_state.motor_state[waist_idx].dq
            quat, ang_vel = transform_imu_data(
                waist_yaw=wy, waist_yaw_omega=wdy,
                imu_quat=quat, imu_omega=ang_vel.reshape(1, 3),
            )
        return quat, ang_vel.flatten()

    def _build_obs_motion(self, quat, ang_vel) -> np.ndarray:
        """47-dim obs en orden original de legged_gym (motion.pt)."""
        cfg    = self.config
        gravity = get_gravity_orientation(quat)
        qj_obs  = (self.qj  - cfg.default_angles) * cfg.dof_pos_scale
        dqj_obs = self.dqj  * cfg.dof_vel_scale
        av_obs  = ang_vel   * cfg.ang_vel_scale
        phase   = (self.counter * cfg.control_dt % 0.8) / 0.8
        sin_ph  = np.sin(2 * np.pi * phase)
        cos_ph  = np.cos(2 * np.pi * phase)

        cmd = np.array([
             self.remote_controller.ly,
            -self.remote_controller.lx,
            -self.remote_controller.rx,
        ], np.float32) * cfg.cmd_scale * cfg.max_cmd

        n   = cfg.num_actions
        obs = np.empty(47, np.float32)
        obs[0:3]         = av_obs
        obs[3:6]         = gravity
        obs[6:9]         = cmd
        obs[9:9+n]       = qj_obs
        obs[9+n:9+2*n]   = dqj_obs
        obs[9+2*n:9+3*n] = self.action
        obs[9+3*n]       = sin_ph
        obs[9+3*n+1]     = cos_ph
        return obs

    def _build_obs_hv(self, quat, ang_vel) -> np.ndarray:
        """
        48-dim obs en orden ALFABÉTICO según sorted(obs_config) de
        legged_robot_base.py línea 524 (HumanoidVerse model_7000_jit.pt):
          actions(12), base_ang_vel(3), base_lin_vel(3), command_ang_vel(1),
          command_lin_vel(2), dof_pos(12), dof_vel(12), projected_gravity(3)

        Velocidad lineal: el SDK no la provee directamente; se estima con un
        integrador con fuga sobre el acelerómetro.  LINVEL_DECAY=0.95 da τ≈0.4 s,
        suficiente para capturar el ritmo del paso sin acumular deriva.
        """
        cfg     = self.config
        gravity = get_gravity_orientation(quat)
        qj_obs  = (self.qj - cfg.default_angles)           * cfg.dof_pos_scale
        dqj_obs = np.clip(self.dqj,    -40.0, 40.0)        * cfg.dof_vel_scale
        av_obs  = np.clip(ang_vel,     -10.0, 10.0)        * cfg.ang_vel_scale

        # Estimación de velocidad lineal en body frame
        accel  = np.array(self.low_state.imu_state.accelerometer, np.float32)
        # accel_imu = a_translacional - g_body  →  a_translacional = accel_imu + g_body
        # get_gravity_orientation devuelve [0,0,-1] cuando el robot está de pie,
        # por lo que g_body = gravity * 9.81 = [0,0,-9.81] m/s²
        g_body = gravity * 9.81
        self.lin_vel_est = (
            self.lin_vel_est * _LINVEL_DECAY
            + (accel + g_body) * cfg.control_dt
        )
        lv_obs = np.clip(self.lin_vel_est, -10.0, 10.0) * cfg.lin_vel_scale

        cmd_vx =  self.remote_controller.ly  * cfg.max_cmd[0]
        cmd_vy = -self.remote_controller.lx  * cfg.max_cmd[1]
        cmd_wz = -self.remote_controller.rx  * cfg.max_cmd[2]
        cmd_lin = np.array([cmd_vx, cmd_vy], np.float32)
        cmd_ang = np.array([cmd_wz],         np.float32)

        return np.concatenate([
            self.action,   # actions          (12) × 1.0
            av_obs,        # base_ang_vel      (3) × 0.25
            lv_obs,        # base_lin_vel      (3) × 2.0
            cmd_ang,       # command_ang_vel   (1) × 1.0
            cmd_lin,       # command_lin_vel   (2) × 1.0
            qj_obs,        # dof_pos          (12) × 1.0
            dqj_obs,       # dof_vel          (12) × 0.05
            gravity,       # projected_gravity (3) × 1.0
        ])

    # ── Paso de control ───────────────────────────────────────────────────

    def run(self):
        self.counter += 1
        quat, ang_vel = self._read_joints_and_imu()

        if self.config.policy_type == "motion":
            self.obs = self._build_obs_motion(quat, ang_vel)
        else:
            self.obs = self._build_obs_hv(quat, ang_vel)

        obs_t = torch.from_numpy(self.obs).unsqueeze(0)
        with torch.no_grad():
            self.action = self.policy(obs_t).squeeze().numpy()

        target_dof_pos = self.config.default_angles + self.action * self.config.action_scale

        for i, idx in enumerate(self.config.leg_joint2motor_idx):
            self.low_cmd.motor_cmd[idx].q   = float(target_dof_pos[i])
            self.low_cmd.motor_cmd[idx].qd  = 0
            self.low_cmd.motor_cmd[idx].kp  = self.config.kps[i]
            self.low_cmd.motor_cmd[idx].kd  = self.config.kds[i]
            self.low_cmd.motor_cmd[idx].tau = 0

        for i, idx in enumerate(self.config.arm_waist_joint2motor_idx):
            self.low_cmd.motor_cmd[idx].q   = float(self.config.arm_waist_target[i])
            self.low_cmd.motor_cmd[idx].qd  = 0
            self.low_cmd.motor_cmd[idx].kp  = self.config.arm_waist_kps[i]
            self.low_cmd.motor_cmd[idx].kd  = self.config.arm_waist_kds[i]
            self.low_cmd.motor_cmd[idx].tau = 0

        self._send()
        time.sleep(self.config.control_dt)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("net",    type=str, help="interfaz de red (ej. eth0)")
    parser.add_argument("config", type=str, help="config en deploy_real/configs/",
                        default="g1_motion.yaml")
    args = parser.parse_args()

    cfg_path = f"{REPO_ROOT}/despliegue/configs/{args.config}"
    config   = DualConfig(cfg_path)

    print(f"\n{_B}{'='*58}{_E}")
    print(f"{_B}  DEPLOY DUAL G1  —  política: {config.policy_type.upper()}{_E}")
    print(f"{_B}{'='*58}{_E}")
    print(f"  Archivo  : {config.policy_path.split('/')[-1]}")
    print(f"  num_obs={config.num_obs}   num_act={config.num_actions}")
    print(f"  control_dt={config.control_dt} s  ({1/config.control_dt:.0f} Hz)")
    print(f"{_B}{'='*58}{_E}\n")

    ChannelFactoryInitialize(0, args.net)
    ctrl = DualController(config)

    ctrl.zero_torque_state()
    ctrl.move_to_default_pos()
    ctrl.default_pos_state()

    print(f"\n{_G}Política activa.  SELECT para salir.{_E}")
    print("  L-stick fwd/back = vx  |  L-stick left/right = vy  |  R-stick = wz\n")

    while True:
        try:
            ctrl.run()
            if ctrl.remote_controller.button[KeyMap.select] == 1:
                break
        except KeyboardInterrupt:
            break

    create_damping_cmd(ctrl.low_cmd)
    ctrl._send()
    print(f"\n{_Y}Salida — modo amortiguamiento activo.{_E}")
