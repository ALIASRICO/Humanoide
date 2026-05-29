import time
import sys

import mujoco.viewer
import mujoco
import numpy as np
from pathlib import Path
import torch
REPO_ROOT = str(Path(__file__).parent.parent)
import yaml

# ── colores ANSI ──────────────────────────────────────────────────────────────
_G = "\033[92m"   # verde
_Y = "\033[93m"   # amarillo
_R = "\033[91m"   # rojo
_B = "\033[94m"   # azul
_E = "\033[0m"    # reset


def _status_color(z, action_max):
    if z < 0.35 or action_max > 20:
        return _R, "CAIDA/EXPLOSION"
    if z > 1.1 or action_max > 8:
        return _Y, "INESTABLE"
    return _G, "OK"


def get_gravity_orientation(quaternion):
    qw = quaternion[0]
    qx = quaternion[1]
    qy = quaternion[2]
    qz = quaternion[3]

    gravity_orientation = np.zeros(3)

    gravity_orientation[0] = 2 * (-qz * qx + qw * qy)
    gravity_orientation[1] = -2 * (qz * qy + qw * qx)
    gravity_orientation[2] = 1 - 2 * (qw * qw + qz * qz)

    return gravity_orientation


def quat_rotate_inverse(q, v):
    """Rotate vector v from world frame to body frame using quaternion q=[w,x,y,z].

    MuJoCo stores free-joint angular velocity (qvel[3:6]) in world frame.
    IsaacLab trains with root_ang_vel_b = angular velocity in body frame.
    This function matches quat_rotate_inverse from isaaclab.utils.math.
    """
    qw, qx, qy, qz = q[0], q[1], q[2], q[3]
    vx, vy, vz = v[0], v[1], v[2]
    return np.array([
        vx*(1-2*(qy*qy+qz*qz)) + vy*2*(qx*qy+qw*qz) + vz*2*(qx*qz-qw*qy),
        vx*2*(qx*qy-qw*qz) + vy*(1-2*(qx*qx+qz*qz)) + vz*2*(qy*qz+qw*qx),
        vx*2*(qx*qz+qw*qy) + vy*2*(qy*qz-qw*qx) + vz*(1-2*(qx*qx+qy*qy)),
    ], dtype=np.float32)


def pd_control(target_q, q, kp, target_dq, dq, kd):
    """Calculates torques from position commands"""
    return (target_q - q) * kp + (target_dq - dq) * kd


def quat_multiply(q1, q2):
    """Quaternion multiplication q1 * q2, both [w, x, y, z]."""
    w1, x1, y1, z1 = q1
    w2, x2, y2, z2 = q2
    return np.array([
        w1*w2 - x1*x2 - y1*y2 - z1*z2,
        w1*x2 + x1*w2 + y1*z2 - z1*y2,
        w1*y2 - x1*z2 + y1*w2 + z1*x2,
        w1*z2 + x1*y2 - y1*x2 + z1*w2,
    ], dtype=np.float32)


def omega_from_quats(q_prev, q_curr, dt):
    """Body-frame angular velocity from quaternion finite difference.

    MuJoCo's d.qvel[3:6] contains contact-impulse artifacts that can be
    10-20× larger than the actual body rotation rate. Computing omega from
    the quaternion change over the policy step gives the TRUE average body
    angular velocity, free of high-frequency contact noise.
    """
    q_prev_inv = np.array([q_prev[0], -q_prev[1], -q_prev[2], -q_prev[3]], dtype=np.float32)
    q_delta = quat_multiply(q_curr, q_prev_inv)
    if q_delta[0] < 0:
        q_delta = -q_delta
    omega_world = 2.0 * q_delta[1:4] / dt
    return quat_rotate_inverse(q_curr, omega_world)


if __name__ == "__main__":
    # get config file name from command line
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("config_file", type=str, help="config file name in the config folder")
    parser.add_argument("--headless", action="store_true", help="Sin ventana gráfica, solo métricas por stdout")
    args = parser.parse_args()
    config_file = args.config_file
    headless = args.headless
    with open(f"{REPO_ROOT}/simulacion/configs/{config_file}", "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
        policy_path = config["policy_path"].replace("{REPO_ROOT}", REPO_ROOT)
        xml_path = config["xml_path"].replace("{REPO_ROOT}", REPO_ROOT)

        simulation_duration = config["simulation_duration"]
        simulation_dt = config["simulation_dt"]
        control_decimation = config["control_decimation"]

        kps = np.array(config["kps"], dtype=np.float32)
        kds = np.array(config["kds"], dtype=np.float32)

        default_angles = np.array(config["default_angles"], dtype=np.float32)

        ang_vel_scale = config["ang_vel_scale"]
        dof_pos_scale = config["dof_pos_scale"]
        dof_vel_scale = config["dof_vel_scale"]
        action_scale = config["action_scale"]
        cmd_scale = np.array(config["cmd_scale"], dtype=np.float32)

        num_actions = config["num_actions"]
        num_obs = config["num_obs"]
        
        cmd = np.array(config["cmd_init"], dtype=np.float32)

    # optional parameters with defaults
    vel_clip    = config.get("vel_clip",    40.0)   # rad/s clip before EMA
    vel_smooth  = config.get("vel_smooth",  0.0)    # EMA alpha (0=no smoothing)
    warmup_steps = config.get("warmup_steps", 0)    # policy steps to hold default before enabling policy
    debug_steps  = config.get("debug_steps", 0)     # print obs for first N policy steps

    # define context variables
    action = np.zeros(num_actions, dtype=np.float32)
    target_dof_pos = default_angles.copy()
    obs = np.zeros(num_obs, dtype=np.float32)
    dqj_prev      = np.zeros(num_actions, dtype=np.float32)  # for EMA smoothing
    omega_prev    = np.zeros(3,           dtype=np.float32)  # for EMA smoothing
    quat_prev     = np.array([1., 0., 0., 0.], dtype=np.float32)  # for omega finite diff
    dt_policy     = simulation_dt * control_decimation

    counter = 0

    # Load robot model
    m = mujoco.MjModel.from_xml_path(xml_path)
    d = mujoco.MjData(m)
    m.opt.timestep = simulation_dt

    # Set initial pose: z=0.780 is the correct height for g1_12dof.xml with
    # default_angles (knee=0.30, ankle=-0.20).  At z=0.74 the feet penetrate
    # the ground by ~4 cm, causing a violent contact impulse on the first
    # physics step that corrupts observations → policy collapses immediately.
    # (Verified: foot_min_z = 0.0008 m at z=0.780 with default_angles.)
    d.qpos[0] = 0.0
    d.qpos[1] = 0.0
    d.qpos[2] = 0.780
    d.qpos[3] = 1.0   # quaternion w
    d.qpos[4] = 0.0   # quaternion x
    d.qpos[5] = 0.0   # quaternion y
    d.qpos[6] = 0.0   # quaternion z
    d.qpos[7 : 7 + num_actions] = default_angles
    d.qvel[:] = 0.0
    mujoco.mj_forward(m, d)

    # load policy
    policy = torch.jit.load(policy_path)

    # ── header de configuración ──────────────────────────────────────────────
    print(f"\n{_B}{'='*62}{_E}")
    print(f"{_B}  DEPLOY  {config_file}{_E}")
    print(f"{_B}{'='*62}{_E}")
    print(f"  Política : {policy_path.split('/')[-1]}")
    print(f"  XML      : {xml_path.split('/')[-1]}")
    print(f"  sim_dt   : {simulation_dt}s  |  decimation: {control_decimation}  "
          f"→  policy_hz: {1/(simulation_dt*control_decimation):.0f} Hz")
    print(f"  num_obs  : {num_obs}  |  num_actions: {num_actions}")
    print(f"  cmd      : vx={cmd[0]:.2f}  vy={cmd[1]:.2f}  wz={cmd[2]:.2f}")
    print(f"  kps      : {kps.tolist()}")
    print(f"  kds      : {kds.tolist()}")
    print(f"{_B}{'='*62}{_E}\n")
    print(f"  {'t(s)':>6}  {'z(m)':>6}  {'pitch°':>7}  "
          f"{'vx':>5}  {'act_max':>7}  {'fase':>6}  estado")
    print(f"  {'-'*58}")

    # ── historial para resumen final ─────────────────────────────────────────
    _hist_z   = []
    _hist_act = []
    _events   = []   # (t, mensaje)
    _policy_step = 0
    _fell = False

    def _sim_loop(get_running, sync_viewer):
        global counter, _policy_step, _fell, action, target_dof_pos
        total_steps = int(simulation_duration / simulation_dt)
        for _s in range(total_steps):
            if not get_running():
                break
            step_start = time.time()
            tau = pd_control(target_dof_pos, d.qpos[7:], kps, np.zeros_like(kds), d.qvel[6:], kds)
            d.ctrl[:] = tau
            # mj_step can be replaced with code that also evaluates
            # a policy and applies a control signal before stepping the physics.
            mujoco.mj_step(m, d)

            counter += 1
            if counter % control_decimation == 0:
                # Apply control signal here.

                # create observation
                quat = d.qpos[3:7]
                qj_raw = d.qpos[7:]
                # 1) joint velocities: clip then EMA-smooth to remove contact spikes
                dqj_raw = np.clip(d.qvel[6:], -vel_clip, vel_clip)
                dqj_raw = vel_smooth * dqj_prev + (1.0 - vel_smooth) * dqj_raw
                dqj_prev[:] = dqj_raw
                # 2) angular velocity: finite-difference of quaternion over policy step.
                # d.qvel[3:6] from MuJoCo contains contact-impulse artifacts that are
                # 10-20× the actual body rotation rate. Finite diff gives the true omega.
                omega_raw = omega_from_quats(quat_prev, quat, dt_policy)
                quat_prev[:] = quat

                qj = (qj_raw - default_angles) * dof_pos_scale
                dqj = dqj_raw * dof_vel_scale
                gravity_orientation = get_gravity_orientation(quat)
                omega = np.clip(omega_raw, -10.0, 10.0) * ang_vel_scale

                period = 0.8
                count = counter * simulation_dt
                phase = count % period / period
                sin_phase = np.sin(2 * np.pi * phase)
                cos_phase = np.cos(2 * np.pi * phase)

                obs[:3] = omega
                obs[3:6] = gravity_orientation
                obs[6:9] = cmd * cmd_scale
                obs[9 : 9 + num_actions] = qj
                obs[9 + num_actions : 9 + 2 * num_actions] = dqj
                obs[9 + 2 * num_actions : 9 + 3 * num_actions] = action
                obs[9 + 3 * num_actions : 9 + 3 * num_actions + 2] = np.array([sin_phase, cos_phase])

                # debug: print obs summary for first N policy steps
                if debug_steps > 0 and _policy_step < debug_steps:
                    dqj_max = float(np.abs(dqj_raw).max())
                    print(f"  [DBG step={_policy_step:3d}] "
                          f"omega={np.abs(omega).max():.3f}  "
                          f"grav_z={gravity_orientation[2]:.3f}  "
                          f"qj_max={np.abs(qj).max():.3f}  "
                          f"dqj_raw_max={dqj_max:.1f}  "
                          f"dqj_obs_max={np.abs(dqj).max():.3f}  "
                          f"phase=({sin_phase:.2f},{cos_phase:.2f})",
                          flush=True)

                obs_tensor = torch.from_numpy(obs).unsqueeze(0)

                # policy inference — skip during warmup to let MuJoCo settle
                if _policy_step >= warmup_steps:
                    action = policy(obs_tensor).detach().numpy().squeeze()
                    target_dof_pos = action * action_scale + default_angles

                # ── verificador en tiempo real ───────────────────────────────
                _policy_step += 1
                sim_t     = counter * simulation_dt
                z         = d.qpos[2]
                lin_vel   = d.qvel[0]
                qw,qx,qy,qz_ = d.qpos[3],d.qpos[4],d.qpos[5],d.qpos[6]
                pitch_deg = np.degrees(np.arctan2(2*(qw*qy - qz_*qx),
                                                   1 - 2*(qx*qx + qy*qy)))
                action_max = float(np.abs(action).max())

                _hist_z.append(z)
                _hist_act.append(action_max)

                # detectar eventos
                if z < 0.35 and not _fell:
                    _fell = True
                    _events.append((sim_t, f"{_R}CAIDA detectada z={z:.3f}m{_E}"))
                if action_max > 20 and len(_events) < 10:
                    _events.append((sim_t, f"{_R}EXPLOSION acciones max={action_max:.1f}{_E}"))
                if z > 1.1 and len(_events) < 10:
                    _events.append((sim_t, f"{_Y}SALTO z={z:.3f}m{_E}"))

                # imprimir cada 50 policy steps (~1s)
                if _policy_step % 50 == 0:
                    color, estado = _status_color(z, action_max)
                    print(f"  {sim_t:>6.1f}  {z:>6.3f}  {pitch_deg:>+7.1f}  "
                          f"{lin_vel:>+5.2f}  {action_max:>7.3f}  "
                          f"{phase:>5.2f}π  {color}{estado}{_E}",
                          flush=True)

            sync_viewer()
            time_until_next_step = m.opt.timestep - (time.time() - step_start)
            if time_until_next_step > 0 and not headless:
                time.sleep(time_until_next_step)

    if headless:
        _sim_loop(lambda: True, lambda: None)
    else:
        with mujoco.viewer.launch_passive(m, d) as viewer:
            _sim_loop(viewer.is_running, viewer.sync)

    # ── resumen final ────────────────────────────────────────────────────────
    total_t = counter * simulation_dt
    print(f"\n{_B}{'='*62}{_E}")
    print(f"{_B}  RESUMEN  ({total_t:.1f}s simulados,  {_policy_step} pasos de política){_E}")
    print(f"{_B}{'='*62}{_E}")
    if _hist_z:
        z_arr  = np.array(_hist_z)
        a_arr  = np.array(_hist_act)
        print(f"  Altura z  :  min={z_arr.min():.3f}m  max={z_arr.max():.3f}m  "
              f"media={z_arr.mean():.3f}m  (nominal 0.74m)")
        print(f"  Acción    :  min={a_arr.min():.3f}  max={a_arr.max():.3f}  "
              f"media={a_arr.mean():.3f}")

        # diagnóstico
        print()
        pct_ok   = np.mean((z_arr > 0.5) & (z_arr < 1.0)) * 100
        pct_fall = np.mean(z_arr < 0.35) * 100
        pct_jump = np.mean(z_arr > 1.1)  * 100
        color_ok = _G if pct_ok > 60 else (_Y if pct_ok > 20 else _R)
        print(f"  Tiempo en rango normal (0.5–1.0m): {color_ok}{pct_ok:.1f}%{_E}")
        print(f"  Tiempo caído   (<0.35m): {(_R if pct_fall>5 else _G)}{pct_fall:.1f}%{_E}")
        print(f"  Tiempo saltando (>1.1m): {(_Y if pct_jump>5 else _G)}{pct_jump:.1f}%{_E}")

        # veredicto
        print()
        if a_arr.max() > 20:
            print(f"  {_R}[MALO]  Acciones explosivas — política degenerada.{_E}")
            print(f"           Solución: retrain con rewards anti-salto más fuertes.")
        elif pct_fall > 30:
            print(f"  {_Y}[REGULAR]  Robot cae con frecuencia.{_E}")
            print(f"              Puede mejorar con más iteraciones de entrenamiento.")
        elif pct_ok > 60:
            print(f"  {_G}[BUENO]  Robot se mantiene de pie la mayor parte del tiempo.{_E}")
        else:
            print(f"  {_Y}[MARGINAL]  Robot inestable pero no explota.{_E}")

    if _events:
        print(f"\n  Eventos detectados:")
        for et, emsg in _events[:15]:
            print(f"    t={et:.1f}s  {emsg}")

    print(f"{_B}{'='*62}{_E}\n")
