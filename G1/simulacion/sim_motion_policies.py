"""
Visualizador de políticas de movimiento G1 (29 DOF) en MuJoCo.

Uso:
  conda activate /home/udc/Humanoide/G1/envs/g1_udc
  cd /home/udc/Unitree_G1
  python simulacion/sim_motion_policies.py agacharse
  python simulacion/sim_motion_policies.py agacharse --debug
  python simulacion/sim_motion_policies.py agacharse --headless
"""
import argparse
import time
import sys
import numpy as np
import torch
import mujoco
import mujoco.viewer
import yaml
from pathlib import Path

REPO = Path(__file__).parent.parent

DOF_NAMES = [
    "left_hip_pitch_joint",   "left_hip_roll_joint",   "left_hip_yaw_joint",
    "left_knee_joint",        "left_ankle_pitch_joint", "left_ankle_roll_joint",
    "right_hip_pitch_joint",  "right_hip_roll_joint",   "right_hip_yaw_joint",
    "right_knee_joint",       "right_ankle_pitch_joint","right_ankle_roll_joint",
    "waist_yaw_joint",        "waist_roll_joint",        "waist_pitch_joint",
    "left_shoulder_pitch_joint","left_shoulder_roll_joint","left_shoulder_yaw_joint",
    "left_elbow_joint",
    "left_wrist_roll_joint",  "left_wrist_pitch_joint", "left_wrist_yaw_joint",
    "right_shoulder_pitch_joint","right_shoulder_roll_joint","right_shoulder_yaw_joint",
    "right_elbow_joint",
    "right_wrist_roll_joint", "right_wrist_pitch_joint","right_wrist_yaw_joint",
]
DOF_SHORT = [
    "L_hip_p","L_hip_r","L_hip_y","L_knee","L_ank_p","L_ank_r",
    "R_hip_p","R_hip_r","R_hip_y","R_knee","R_ank_p","R_ank_r",
    "W_yaw","W_roll","W_pitch",
    "LS_p","LS_r","LS_y","L_elb","LW_r","LW_p","LW_y",
    "RS_p","RS_r","RS_y","R_elb","RW_r","RW_p","RW_y",
]
DOF_IDX = {name: i for i, name in enumerate(DOF_NAMES)}
N_DOF = 29
LEG_IDX = list(range(12))  # DOF 0-11


def load_config(motion_name):
    cfg_path = REPO / "simulacion" / "configs" / f"motion_{motion_name}.yaml"
    with open(cfg_path) as f:
        cfg = yaml.safe_load(f)
    for key in ["policy_path", "xml_path"]:
        if key in cfg:
            cfg[key] = cfg[key].replace("{REPO_ROOT}", str(REPO))
    return cfg


def pose_to_array(pose_dict, default_angles):
    arr = default_angles.copy()
    if pose_dict:
        for name, val in pose_dict.items():
            if name in DOF_IDX:
                arr[DOF_IDX[name]] = float(val)
    return arr


def quat_rotate_inverse(q, v):
    qw, qx, qy, qz = q[0], q[1], q[2], q[3]
    vx, vy, vz = v[0], v[1], v[2]
    return np.array([
        vx*(1-2*(qy*qy+qz*qz)) + vy*2*(qx*qy+qw*qz) + vz*2*(qx*qz-qw*qy),
        vx*2*(qx*qy-qw*qz)     + vy*(1-2*(qx*qx+qz*qz)) + vz*2*(qy*qz+qw*qx),
        vx*2*(qx*qz+qw*qy)     + vy*2*(qy*qz-qw*qx) + vz*(1-2*(qx*qx+qy*qy)),
    ], dtype=np.float32)


def omega_from_quats(q_prev, q_curr, dt):
    q_inv = np.array([q_prev[0], -q_prev[1], -q_prev[2], -q_prev[3]], np.float32)
    w, x, y, z = q_inv
    w2, x2, y2, z2 = q_curr
    q_delta = np.array([
        w*w2-x*x2-y*y2-z*z2, w*x2+x*w2+y*z2-z*y2,
        w*y2-x*z2+y*w2+z*x2, w*z2+x*y2-y*x2+z*w2,
    ], np.float32)
    if q_delta[0] < 0:
        q_delta = -q_delta
    omega_world = 2.0 * q_delta[1:4] / dt
    return quat_rotate_inverse(q_curr, omega_world)


def get_gravity_orientation(quat):
    qw, qx, qy, qz = quat.astype(np.float32)
    return np.array([
        2*(-qz*qx + qw*qy),
        -2*(qz*qy + qw*qx),
        1 - 2*(qw*qw + qz*qz),
    ], dtype=np.float32)


def get_foot_contacts(model, data):
    """Fuerza de contacto vertical en pies (L y R)."""
    foot_names = ["left_ankle_roll_joint", "right_ankle_roll_joint"]
    forces = {"L": 0.0, "R": 0.0}
    for i in range(data.ncon):
        c = data.contact[i]
        geom1_body = model.geom_bodyid[c.geom1]
        geom2_body = model.geom_bodyid[c.geom2]
        for body_id in [geom1_body, geom2_body]:
            body_name = mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_BODY, body_id) or ""
            if "left" in body_name and "ankle" in body_name:
                forces["L"] += abs(c.dist)
            elif "right" in body_name and "ankle" in body_name:
                forces["R"] += abs(c.dist)
    return forces


def print_obs_snapshot(label, q, q_target, dof_vel, ang_vel, phase_sig, gravity,
                        action, raw_target, default_q, tau, num_obs=94):
    """Imprime un snapshot completo del estado para debugging."""
    print(f"\n{'─'*70}")
    print(f"  SNAPSHOT: {label}")
    print(f"{'─'*70}")
    print(f"  {'DOF':<14} {'q_actual':>9} {'q_target':>9} {'action':>8} {'target_pos':>10} {'tau':>8}")
    print(f"  {'─'*14} {'─'*9} {'─'*9} {'─'*8} {'─'*10} {'─'*8}")
    show_idx = list(range(N_DOF)) if num_obs == 62 else LEG_IDX
    for i in show_idx:
        marker = " ◄" if abs(q[i] - q_target[i]) > 0.15 else ""
        print(f"  {DOF_SHORT[i]:<14} {q[i]:>+9.4f} {q_target[i]:>+9.4f} "
              f"{action[i]:>+8.4f} {raw_target[i]:>+10.4f} {tau[i]:>+8.2f}{marker}")
    if num_obs == 94:
        print(f"\n  ang_vel   = [{ang_vel[0]:+.3f}, {ang_vel[1]:+.3f}, {ang_vel[2]:+.3f}]  [obs[0:3], pre-escala]")
        print(f"  phase_sig = {phase_sig[0]:+.4f}  [obs[61]]")
        print(f"  gravity   = [{gravity[0]:+.3f}, {gravity[1]:+.3f}, {gravity[2]:+.3f}]  [obs[62:65]]")
        print(f"  # obs: ang_vel[0:3] dof_pos[3:32] dof_vel[32:61] phase[61] grav[62:65] q_tgt[65:94]")
    else:
        print(f"\n  phase_sig = {phase_sig[0]:+.4f}  [obs[29]]")
        print(f"  gravity   = [{gravity[0]:+.3f}, {gravity[1]:+.3f}, {gravity[2]:+.3f}]  [obs[30:33]]")
        print(f"  # obs (62): dof_pos[0:29] phase[29] grav[30:33] q_tgt[33:62]")
    print(f"  action range legs: [{action[:12].min():+.3f}, {action[:12].max():+.3f}]")
    print(f"  action range arms: [{action[15:].min():+.3f}, {action[15:].max():+.3f}]")
    print(f"{'─'*70}\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("motion", choices=["saludar", "agacharse", "estirar_brazos", "munecas"])
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--duration", type=float, default=30.0)
    parser.add_argument("--debug", action="store_true",
                        help="Snapshot detallado en pasos 0, 1, 5, 25, 50")
    args = parser.parse_args()

    cfg          = load_config(args.motion)
    policy_path  = Path(cfg["policy_path"])
    xml_path     = Path(cfg["xml_path"])
    sim_dt       = cfg["simulation_dt"]
    ctrl_dec     = cfg["control_decimation"]
    kps          = np.array(cfg["kps"],            dtype=np.float32)
    kds          = np.array(cfg["kds"],            dtype=np.float32)
    default_q    = np.array(cfg["default_angles"], dtype=np.float32)
    torque_limits = np.array(cfg["torque_limits"], dtype=np.float32) if "torque_limits" in cfg else None
    action_scale = cfg["action_scale"]
    action_clip  = cfg.get("action_clip", 0.8)
    control_mode = cfg.get("control_mode", "hybrid_arms")
    num_obs      = cfg.get("num_obs", 62)
    dof_vel_sc   = cfg.get("dof_vel_scale", 0.05)
    ang_vel_sc   = cfg.get("ang_vel_scale", 0.25)
    period       = cfg["period_s"]
    pose_A       = pose_to_array(cfg.get("pose_A"), default_q)
    pose_B       = pose_to_array(cfg.get("pose_B"), default_q)
    periodic_cfg  = cfg.get("periodic", False)
    init_at_default = cfg.get("init_at_default", False)

    if not policy_path.exists():
        print(f"ERROR: política no encontrada en {policy_path}")
        sys.exit(1)

    print(f"\n{'='*65}")
    print(f"  Movimiento  : {args.motion.upper()}")
    print(f"  Política    : {policy_path.name}")
    print(f"  action_scale: {action_scale}  |  clip: ±{action_clip}")
    print(f"  Periódico   : {periodic_cfg}  |  period: {period}s")
    print(f"  control_mode: {control_mode}  |  num_obs: {num_obs}")
    print(f"  sim_dt      : {sim_dt}s  |  ctrl_dec: {ctrl_dec} ({1/(sim_dt*ctrl_dec):.0f} Hz)")
    print(f"  Duración    : {args.duration}s")
    print(f"{'='*65}\n")

    model = mujoco.MjModel.from_xml_path(str(xml_path))
    data  = mujoco.MjData(model)
    model.opt.timestep = sim_dt

    # Inicializar en pose_A (o default_q si init_at_default=True) con altura correcta
    init_pose = default_q if init_at_default else pose_A
    mujoco.mj_resetData(model, data)
    mujoco.mj_forward(model, data)
    default_base_z = data.qpos[2]
    for i in range(N_DOF):
        data.qpos[7 + i] = init_pose[i]
    mujoco.mj_forward(model, data)
    try:
        floor_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_GEOM, "floor")
    except Exception:
        floor_id = -1
    min_geom_z = min(data.geom_xpos[i, 2] for i in range(model.ngeom) if i != floor_id)
    init_base_z = default_base_z - min_geom_z
    data.qpos[2]   = init_base_z
    data.qpos[3]   = 1.0
    data.qpos[4:7] = 0.0
    for i in range(N_DOF):
        data.qpos[7 + i] = init_pose[i]
    data.qvel[:] = 0.0
    mujoco.mj_forward(model, data)
    print(f"  Init base_z : {init_base_z:.4f}m  (XML default: {default_base_z:.4f}m)")

    # Pose A vs B info
    print(f"\n  Pose A (standing) → Pose B (squat) para piernas:")
    for i in LEG_IDX:
        delta = pose_B[i] - pose_A[i]
        if abs(delta) > 0.001:
            max_cmd = action_clip * action_scale
            feasible = "✓" if abs(delta) <= max_cmd + 0.001 else f"✗ (max={max_cmd:.2f})"
            print(f"    {DOF_SHORT[i]:<12}: A={pose_A[i]:+.3f}  B={pose_B[i]:+.3f}  Δ={delta:+.3f}  {feasible}")

    policy = torch.jit.load(str(policy_path))
    policy.eval()

    total_steps = int(args.duration / sim_dt)
    target_pos  = pose_A.copy()
    obs         = np.zeros(num_obs, dtype=np.float32)
    quat_prev   = np.array([1., 0., 0., 0.], dtype=np.float32)
    step        = 0
    t           = 0.0
    ctrl_step   = 0

    # Métricas acumuladas
    min_pelvis_z   = init_base_z
    max_knee_L     = 0.0
    max_knee_R     = 0.0
    fall_count     = 0
    action_clip_count = 0
    total_ctrl_steps  = 0
    squat_depth_hist  = []  # pelvis_z vs t cada 0.5s

    # ── tabla de seguimiento de piernas ──────────────────────────────────────
    print(f"\n  {'t(s)':>5}  {'z_pelv':>7}  {'alpha':>6}  {'L_knee':>7}  {'R_knee':>7}  "
          f"{'err_Lk':>7}  {'err_Rk':>7}  {'L_cont':>7}  {'R_cont':>7}  estado")
    print(f"  {'─'*95}")

    debug_ctrl_steps = {0, 1, 5, 25, 50} if args.debug else set()

    def sim_loop(get_running, sync_viewer):
        nonlocal step, t, target_pos, obs, ctrl_step
        nonlocal min_pelvis_z, max_knee_L, max_knee_R, fall_count
        nonlocal action_clip_count, total_ctrl_steps

        for _ in range(total_steps):
            if not get_running():
                break

            t_start = time.time()

            q   = data.qpos[7:7+N_DOF].astype(np.float32)
            dq  = data.qvel[6:6+N_DOF].astype(np.float32)
            tau = kps * (target_pos - q) - kds * dq
            if torque_limits is not None:
                tau = np.clip(tau, -torque_limits, torque_limits)
            data.ctrl[:N_DOF] = tau
            mujoco.mj_step(model, data)
            step += 1
            t = step * sim_dt

            # Métricas pasivas
            z = data.qpos[2]
            if z < min_pelvis_z:
                min_pelvis_z = z
            if data.qpos[7 + 3] > max_knee_L:
                max_knee_L = data.qpos[7 + 3]
            if data.qpos[7 + 9] > max_knee_R:
                max_knee_R = data.qpos[7 + 9]

            if step % ctrl_dec == 0:
                ctrl_step += 1
                total_ctrl_steps += 1

                quat    = data.qpos[3:7].astype(np.float32)
                gravity = get_gravity_orientation(quat)
                dt_ctrl = sim_dt * ctrl_dec
                ang_vel = omega_from_quats(quat_prev, quat, dt_ctrl) * ang_vel_sc
                quat_prev[:] = quat

                # Señal de fase y q_target — fórmula exacta de Genesis MotionEnv:
                #   phase_signal = sin(2π*t/T)  → rango [-1, 1]
                #   alpha = (phase_signal + 1) / 2  → rango [0, 1], empieza en 0.5
                if periodic_cfg:
                    phase_sig_val = np.sin(2 * np.pi * t / period)
                    phase_sig = np.array([phase_sig_val], dtype=np.float32)
                    alpha     = (phase_sig_val + 1.0) / 2.0
                    q_target  = (1 - alpha) * pose_A + alpha * pose_B
                else:
                    alpha    = 0.0
                    q_target = pose_A.copy()
                    duration = cfg.get("duration_s", period)
                    phase_val = min(t / duration, 1.0)
                    phase_sig = np.array([np.sin(phase_val * np.pi)], dtype=np.float32)

                q_now = data.qpos[7:7+N_DOF].astype(np.float32)
                dof_vel = data.qvel[6:6+N_DOF].astype(np.float32) * dof_vel_sc

                if num_obs == 94:
                    # Orden ALFABÉTICO de obs_keys (sorted en HumanoidVerse):
                    # base_ang_vel(3) + dof_pos(29) + dof_vel(29) + phase_signal(1) + projected_gravity(3) + q_target(29)
                    obs[0:3]   = ang_vel                      # base_ang_vel (ya escalado ×0.25)
                    obs[3:32]  = q_now                        # dof_pos (absoluto)
                    obs[32:61] = dof_vel                      # dof_vel (ya escalado ×0.05)
                    obs[61]    = phase_sig[0]                 # phase_signal
                    obs[62:65] = gravity                      # projected_gravity
                    obs[65:94] = q_target.astype(np.float32) # q_target
                else:
                    # num_obs=62: [dof_pos, phase_signal, projected_gravity, q_target] (ALFABÉTICO)
                    # motion_obs.yaml: [dof_pos, q_target, phase_signal, projected_gravity]
                    # sorted → dof_pos(29) + phase_signal(1) + projected_gravity(3) + q_target(29)
                    obs[0:29]  = q_now                        # dof_pos (absoluto)
                    obs[29]    = phase_sig[0]                 # phase_signal
                    obs[30:33] = gravity                      # projected_gravity
                    obs[33:62] = q_target.astype(np.float32) # q_target

                obs_t = torch.from_numpy(obs).unsqueeze(0)
                with torch.no_grad():
                    action_raw = policy(obs_t).numpy().squeeze()

                clipped = np.abs(action_raw) > action_clip
                action_clip_count += int(clipped.any())
                action = action_raw.clip(-action_clip, action_clip)

                raw_target = action * action_scale + default_q
                if control_mode == "hybrid_legs":
                    target_pos[:12] = raw_target[:12]
                    target_pos[12:] = default_q[12:]
                elif control_mode == "hybrid_legs_waist":
                    target_pos[:15] = raw_target[:15]
                    target_pos[15:] = default_q[15:]
                elif control_mode == "full":
                    target_pos[:] = raw_target[:]
                else:
                    target_pos[:15] = default_q[:15]
                    target_pos[15:] = raw_target[15:]

                # Debug snapshot (pasos específicos)
                if ctrl_step - 1 in debug_ctrl_steps:
                    tau_now = kps * (target_pos - q_now) - kds * data.qvel[6:6+N_DOF].astype(np.float32)
                    print_obs_snapshot(
                        f"ctrl_step={ctrl_step-1}  t={t:.3f}s  α={alpha:.3f}",
                        q_now, q_target, dof_vel, ang_vel, phase_sig, gravity,
                        action, raw_target, default_q, tau_now, num_obs,
                    )

                # Tabla resumen cada 0.5s (cada 25 ctrl steps a 50 Hz)
                if ctrl_step % 25 == 0:
                    z_now    = data.qpos[2]
                    L_knee   = data.qpos[7 + 3]
                    R_knee   = data.qpos[7 + 9]
                    err_Lk   = L_knee - q_target[3]
                    err_Rk   = R_knee - q_target[9]
                    contacts = get_foot_contacts(model, data)
                    estado   = "OK   " if z_now > 0.5 else "CAIDA"
                    if z_now <= 0.5:
                        fall_count += 1
                    squat_depth_hist.append((t, z_now, alpha))
                    print(f"  {t:>5.1f}  {z_now:>7.3f}m  {alpha:>6.3f}  "
                          f"{L_knee:>+7.3f}  {R_knee:>+7.3f}  "
                          f"{err_Lk:>+7.3f}  {err_Rk:>+7.3f}  "
                          f"{contacts['L']:>7.4f}  {contacts['R']:>7.4f}  {estado}")

            sync_viewer()
            elapsed = time.time() - t_start
            remaining = sim_dt - elapsed
            if remaining > 0 and not args.headless:
                time.sleep(remaining)

    if args.headless:
        sim_loop(lambda: True, lambda: None)
    else:
        try:
            with mujoco.viewer.launch_passive(model, data) as viewer:
                sim_loop(viewer.is_running, viewer.sync)
        except Exception:
            pass

    # ── Resumen final ─────────────────────────────────────────────────────────
    print(f"\n{'='*65}")
    print(f"  RESUMEN FINAL")
    print(f"{'='*65}")
    print(f"  Duración simulada      : {t:.1f}s")
    print(f"  Pelvis z final         : {data.qpos[2]:.3f}m")
    print(f"  Pelvis z mínima        : {min_pelvis_z:.3f}m")
    print(f"  Knee L máximo          : {max_knee_L:.3f} rad  (target squat: {pose_B[3]:.3f})")
    print(f"  Knee R máximo          : {max_knee_R:.3f} rad  (target squat: {pose_B[9]:.3f})")
    squat_reach_pct_L = min(max_knee_L / pose_B[3] * 100, 100) if pose_B[3] > 0 else 0
    squat_reach_pct_R = min(max_knee_R / pose_B[9] * 100, 100) if pose_B[9] > 0 else 0
    print(f"  Squat alcanzado (L/R)  : {squat_reach_pct_L:.0f}% / {squat_reach_pct_R:.0f}%")
    print(f"  Pasos con CAIDA        : {fall_count} de {len(squat_depth_hist)}")
    print(f"  Ctrl steps con clip    : {action_clip_count} de {total_ctrl_steps}")
    print(f"  Right shoulder final   : {data.qpos[7+22]:.3f} rad")
    if squat_depth_hist:
        min_z_t = min(squat_depth_hist, key=lambda x: x[1])
        print(f"  Pelvis z mínima en t   : {min_z_t[0]:.1f}s (z={min_z_t[1]:.3f}m, α={min_z_t[2]:.3f})")
    print(f"{'='*65}\n")


if __name__ == "__main__":
    main()
