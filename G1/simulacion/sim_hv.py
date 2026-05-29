"""
Sim-to-sim deploy para política entrenada con HumanoidVerse + Genesis.
Obs de 48 dims (sin phase, con base_lin_vel).

Uso:
    cd /home/udc/Unitree_G1
    python simulacion/sim_hv.py g1_hv.yaml
"""
import time
import sys
import mujoco
import mujoco.viewer
import numpy as np
from pathlib import Path
import torch
REPO_ROOT = str(Path(__file__).parent.parent)
import yaml

_G = "\033[92m"
_Y = "\033[93m"
_R = "\033[91m"
_B = "\033[94m"
_E = "\033[0m"


def get_gravity_orientation(q):
    """Projected gravity vector in body frame (3 dims)."""
    qw, qx, qy, qz = q[0], q[1], q[2], q[3]
    return np.array([
        2 * (-qz * qx + qw * qy),
        -2 * (qz * qy + qw * qx),
        1 - 2 * (qw * qw + qz * qz),
    ], dtype=np.float32)


def quat_rotate_inverse(q, v):
    """Rotate world-frame vector v into body frame. q = [w,x,y,z]."""
    qw, qx, qy, qz = q[0], q[1], q[2], q[3]
    vx, vy, vz = v[0], v[1], v[2]
    return np.array([
        vx*(1-2*(qy*qy+qz*qz)) + vy*2*(qx*qy+qw*qz) + vz*2*(qx*qz-qw*qy),
        vx*2*(qx*qy-qw*qz)     + vy*(1-2*(qx*qx+qz*qz)) + vz*2*(qy*qz+qw*qx),
        vx*2*(qx*qz+qw*qy)     + vy*2*(qy*qz-qw*qx) + vz*(1-2*(qx*qx+qy*qy)),
    ], dtype=np.float32)


def quat_multiply(q1, q2):
    w1,x1,y1,z1 = q1;  w2,x2,y2,z2 = q2
    return np.array([
        w1*w2-x1*x2-y1*y2-z1*z2, w1*x2+x1*w2+y1*z2-z1*y2,
        w1*y2-x1*z2+y1*w2+z1*x2, w1*z2+x1*y2-y1*x2+z1*w2,
    ], dtype=np.float32)


def omega_from_quats(q_prev, q_curr, dt):
    """Body-frame angular velocity via quaternion finite difference."""
    q_prev_inv = np.array([q_prev[0], -q_prev[1], -q_prev[2], -q_prev[3]], np.float32)
    q_delta = quat_multiply(q_curr, q_prev_inv)
    if q_delta[0] < 0:
        q_delta = -q_delta
    omega_world = 2.0 * q_delta[1:4] / dt
    return quat_rotate_inverse(q_curr, omega_world)


def pd_control(target_q, q, kp, dq, kd):
    return (target_q - q) * kp + (0.0 - dq) * kd


if __name__ == "__main__":
    import argparse as _ap
    _parser = _ap.ArgumentParser()
    _parser.add_argument("config", nargs="?", default="g1_hv.yaml")
    _parser.add_argument("--headless", action="store_true", help="Sin ventana gráfica, solo métricas por stdout")
    _pargs = _parser.parse_args()
    parser_args = _pargs.config
    headless = _pargs.headless
    cfg_path = f"{REPO_ROOT}/simulacion/configs/{parser_args}"
    with open(cfg_path) as f:
        cfg = yaml.safe_load(f)

    policy_path   = cfg["policy_path"].replace("{REPO_ROOT}", REPO_ROOT)
    xml_path      = cfg["xml_path"].replace("{REPO_ROOT}", REPO_ROOT)
    sim_dur       = cfg["simulation_duration"]
    sim_dt        = cfg["simulation_dt"]
    ctrl_dec      = cfg["control_decimation"]
    kps           = np.array(cfg["kps"], np.float32)
    kds           = np.array(cfg["kds"], np.float32)
    default_q     = np.array(cfg["default_angles"], np.float32)
    lin_vel_scale = cfg["lin_vel_scale"]
    ang_vel_scale = cfg["ang_vel_scale"]
    dof_pos_scale = cfg["dof_pos_scale"]
    dof_vel_scale = cfg["dof_vel_scale"]
    action_scale  = cfg["action_scale"]
    num_act       = cfg["num_actions"]
    num_obs       = cfg["num_obs"]   # must be 48
    cmd           = np.array(cfg["cmd_init"], np.float32)
    dt_policy     = sim_dt * ctrl_dec

    assert num_obs == 48, f"Este script espera 48 obs, config dice {num_obs}"

    action      = np.zeros(num_act, np.float32)
    target_q    = default_q.copy()
    quat_prev   = np.array([1., 0., 0., 0.], np.float32)
    counter     = 0
    policy_step = 0
    fell        = False
    hist_z, hist_act, events = [], [], []

    # Heading controller: mantiene el yaw inicial con P-control sobre cmd[2]
    heading_kp   = cfg.get("heading_kp",   0.0)   # 0 = desactivado
    yaw_target   = None                            # se fija en el primer paso

    # Torque limits from g1_12dof (hip=88, knee=139, ankle=50)
    torque_limits = np.array([88, 88, 88, 139, 50, 50, 88, 88, 88, 139, 50, 50], np.float32)

    m = mujoco.MjModel.from_xml_path(xml_path)
    d = mujoco.MjData(m)
    m.opt.timestep = sim_dt

    d.qpos[0] = 0.0;  d.qpos[1] = 0.0;  d.qpos[2] = 0.780
    d.qpos[3] = 1.0;  d.qpos[4] = 0.0;  d.qpos[5] = 0.0;  d.qpos[6] = 0.0
    d.qpos[7:7+num_act] = default_q
    d.qvel[:] = 0.0
    mujoco.mj_forward(m, d)

    policy = torch.jit.load(policy_path)
    policy.eval()

    print(f"\n{_B}{'='*62}{_E}")
    print(f"{_B}  DEPLOY HumanoidVerse → MuJoCo  ({parser_args}){_E}")
    print(f"{_B}{'='*62}{_E}")
    print(f"  Política : {policy_path.split('/')[-1]}")
    print(f"  sim_dt={sim_dt}s  dec={ctrl_dec}  →  {1/dt_policy:.0f} Hz")
    print(f"  num_obs={num_obs}  num_act={num_act}")
    print(f"  cmd: vx={cmd[0]:.2f} vy={cmd[1]:.2f} wz={cmd[2]:.2f}")
    print(f"{_B}{'='*62}{_E}\n")
    print(f"  {'t(s)':>6}  {'z(m)':>6}  {'pitch°':>7}  {'vx':>5}  {'vel_err':>7}  estado")
    print(f"  {'-'*55}")

    def _step_body():
        """Un paso de simulación + política. Devuelve False si el episodio debe parar."""
        nonlocal_state[0] += 1   # counter
        tau = pd_control(target_q[0], d.qpos[7:], kps, d.qvel[6:], kds)
        tau = np.clip(tau, -torque_limits, torque_limits)
        d.ctrl[:] = tau
        mujoco.mj_step(m, d)

        if nonlocal_state[0] % ctrl_dec == 0:
            quat = d.qpos[3:7].astype(np.float32)
            lin_vel_world = np.clip(d.qvel[0:3].astype(np.float32), -10.0, 10.0)
            lin_vel_body  = quat_rotate_inverse(quat, lin_vel_world) * lin_vel_scale
            ang_vel_raw   = omega_from_quats(quat_prev, quat, dt_policy)
            ang_vel       = np.clip(ang_vel_raw, -10.0, 10.0) * ang_vel_scale
            quat_prev[:]  = quat
            gravity       = get_gravity_orientation(quat)

            # Heading controller dinámico
            qw_,qx_,qy_,qz__ = quat[0],quat[1],quat[2],quat[3]
            yaw_now = np.arctan2(2*(qw_*qz__+qx_*qy_), 1-2*(qy_*qy_+qz__*qz__))
            if yaw_target[0] is None:
                yaw_target[0] = yaw_now
            if heading_kp > 0.0:
                yaw_err = yaw_now - yaw_target[0]
                # normalizar a [-π, π]
                yaw_err = (yaw_err + np.pi) % (2*np.pi) - np.pi
                cmd[2] = float(np.clip(-heading_kp * yaw_err, -1.0, 1.0))

            cmd_lin       = cmd[:2];   cmd_ang = cmd[2:3]
            dof_pos       = (d.qpos[7:].astype(np.float32) - default_q) * dof_pos_scale
            dof_vel       = np.clip(d.qvel[6:].astype(np.float32), -40.0, 40.0) * dof_vel_scale
            obs = np.concatenate([action[0], ang_vel, lin_vel_body, cmd_ang, cmd_lin,
                                  dof_pos, dof_vel, gravity])
            obs_t = torch.from_numpy(obs).unsqueeze(0)
            with torch.no_grad():
                action[0]  = policy(obs_t).squeeze().numpy()
            target_q[0]    = action[0] * action_scale + default_q

            nonlocal_state[1] += 1   # policy_step
            sim_t     = nonlocal_state[0] * sim_dt
            z         = float(d.qpos[2])
            vx_actual = float(d.qvel[0])
            vel_err   = abs(cmd[0] - vx_actual)
            qw,qx,qy,qz_ = d.qpos[3],d.qpos[4],d.qpos[5],d.qpos[6]
            pitch_deg = np.degrees(np.arctan2(2*(qw*qy - qz_*qx),
                                               1 - 2*(qx*qx + qy*qy)))
            act_max   = float(np.abs(action[0]).max())
            hist_z.append(z);  hist_act.append(act_max)
            if z < 0.35 and not fell[0]:
                fell[0] = True
                events.append((sim_t, f"{_R}CAIDA z={z:.3f}m{_E}"))
            if act_max > 20 and len(events) < 10:
                events.append((sim_t, f"{_R}EXPLOSION act={act_max:.1f}{_E}"))
            if nonlocal_state[1] % 50 == 0:
                if z < 0.35 or act_max > 20:   col, est = _R, "CAIDA/EXPLOSION"
                elif z > 1.1 or act_max > 8:   col, est = _Y, "INESTABLE"
                else:                           col, est = _G, "OK"
                print(f"  {sim_t:>6.1f}  {z:>6.3f}  {pitch_deg:>+7.1f}  "
                      f"{vx_actual:>+5.2f}  {vel_err:>7.3f}  {col}{est}{_E}", flush=True)

    # contenedores mutables para estado compartido con _step_body
    nonlocal_state = [counter, policy_step]   # [0]=counter  [1]=policy_step
    action   = [action]    # wrapping en lista para asignación dentro de función
    target_q = [target_q]
    fell     = [fell]
    yaw_target = [yaw_target]

    total_steps = int(sim_dur / sim_dt)
    if headless:
        for _ in range(total_steps):
            _step_body()
    else:
        with mujoco.viewer.launch_passive(m, d) as viewer:
            start = time.time()
            while viewer.is_running() and time.time() - start < sim_dur:
                step_start = time.time()
                _step_body()
                viewer.sync()
                sleep_t = m.opt.timestep - (time.time() - step_start)
                if sleep_t > 0:
                    time.sleep(sleep_t)

    counter      = nonlocal_state[0]
    policy_step  = nonlocal_state[1]
    action       = action[0]
    fell         = fell[0]

    # resumen
    total_t = counter * sim_dt
    print(f"\n{_B}{'='*62}{_E}")
    print(f"{_B}  RESUMEN  ({total_t:.1f}s,  {policy_step} pasos){_E}")
    print(f"{_B}{'='*62}{_E}")
    if hist_z:
        za = np.array(hist_z);  aa = np.array(hist_act)
        print(f"  Altura  : min={za.min():.3f}  max={za.max():.3f}  media={za.mean():.3f}m")
        print(f"  Acción  : min={aa.min():.3f}  max={aa.max():.3f}  media={aa.mean():.3f}")
        pct_ok   = np.mean((za > 0.5) & (za < 1.0)) * 100
        pct_fall = np.mean(za < 0.35) * 100
        col_ok   = _G if pct_ok > 60 else (_Y if pct_ok > 20 else _R)
        print(f"  Tiempo en rango normal: {col_ok}{pct_ok:.1f}%{_E}")
        print(f"  Tiempo caído (<0.35m): {(_R if pct_fall>5 else _G)}{pct_fall:.1f}%{_E}")
        print()
        if aa.max() > 20:
            print(f"  {_R}[MALO] Acciones explosivas.{_E}")
        elif pct_fall > 30:
            print(f"  {_Y}[REGULAR] Cae con frecuencia.{_E}")
        elif pct_ok > 60:
            print(f"  {_G}[BUENO] Se mantiene de pie.{_E}")
        else:
            print(f"  {_Y}[MARGINAL] Inestable.{_E}")
    if events:
        print(f"\n  Eventos:")
        for et, em in events[:10]:
            print(f"    t={et:.1f}s  {em}")
    print(f"{_B}{'='*62}{_E}\n")
