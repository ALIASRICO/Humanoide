# Plan de Trabajo 04 — Integración Jerárquica de las 3 Políticas
**Proyecto:** Unitree G1 — Universidad de Colombia  
**Fecha:** 2026-05-14  
**Sub-agentes asignados:** 30  
**Prerequerido:** Planes 02 y 03 completados (`politicas/model_grasp_jit.pt` y `politicas/model_nav_jit.pt` existen)  
**Reporte de salida:** `reportes/reporte_plan04_integracion_<FECHA>.md`

---

## Contexto del Proyecto

Tenemos 3 políticas entrenadas:
1. **`politicas/model_DR_jit.pt`** — Locomoción (48 obs → 12 acc piernas) — CONGELADA
2. **`politicas/model_grasp_jit.pt`** — Agarre (obs_dim → 28 acc brazos+dedos)
3. **`politicas/model_nav_jit.pt`** — Navegación LIDAR (135 obs → 3 acc velocidad)

Este plan integra las 3 en un pipeline controlado por una Máquina de Estados Finitos (FSM) que ejecuta la tarea completa: detectar caja → navegar → agarrar → transportar → depositar.

### FSM de 6 estados:
```
DETECTAR → NAVEGAR_A_CAJA → AGARRAR → TRANSPORTAR → NAVEGAR_A_DEPOSITO → DEPOSITAR → FIN
```

### Flujo de datos:
```
Sensores ──► FSM Orquestador (50 Hz) ──► 3 políticas activas según estado
                    │
        ┌───────────┼────────────────┐
        ▼           ▼                ▼
   model_DR      model_nav      model_grasp
   (piernas)   (velocidad)     (brazos+dedos)
```

---

## FASE 1 — Análisis Pre-Integración (Agentes 1-4, EN PARALELO)

### AGENTE-01 | VERIFICAR_POLITICAS_EXISTENTES
**Tarea:** Verificar que las 3 políticas existen y cargan correctamente con las dimensiones correctas:
```bash
cd /home/udc/Unitree_G1
conda run -p envs/g1_udc python -c "
import torch, numpy as np, os

politicas = {
    'model_DR_jit.pt':    {'obs_dim': 48,  'act_dim': 12},
    'model_grasp_jit.pt': {'obs_dim': None, 'act_dim': 28},  # obs_dim del Plan 02
    'model_nav_jit.pt':   {'obs_dim': 135, 'act_dim': 3},
}

print('=== VERIFICACIÓN POLÍTICAS ===')
for nombre, dims in politicas.items():
    path = f'politicas/{nombre}'
    if not os.path.exists(path):
        print(f'  {nombre}: NO EXISTE')
        continue
    size_kb = os.path.getsize(path) / 1024
    try:
        policy = torch.jit.load(path, map_location='cpu')
        policy.eval()
        # Si obs_dim es None, usar el valor de g1_constants.py
        obs_dim = dims['obs_dim']
        if obs_dim is None:
            import sys; sys.path.insert(0, '.')
            from simulacion.g1_constants import GRASP_OBS_DIM
            obs_dim = GRASP_OBS_DIM
        dummy = torch.zeros(1, obs_dim)
        with torch.no_grad():
            out = policy(dummy)
        print(f'  {nombre}: OK | input=({obs_dim},) | output={out.shape} | range=[{out.min():.3f},{out.max():.3f}] | {size_kb:.1f}KB')
        assert out.shape[1] == dims['act_dim'], f'act_dim incorrecto: {out.shape[1]} != {dims[\"act_dim\"]}'
    except Exception as e:
        print(f'  {nombre}: ERROR - {e}')

print()
print('Verificar también g1_constants.py:')
import sys; sys.path.insert(0, '.')
from simulacion import g1_constants as c
print(f'  GRASP_OBS_DIM = {c.GRASP_OBS_DIM}')
print(f'  GRASP_ACT_DIM = {c.GRASP_ACT_DIM}')
print(f'  NAV_OBS_DIM = {c.NAV_OBS_DIM}')
print(f'  NAV_ACT_DIM = {c.NAV_ACT_DIM}')
"
```
**Reportar:** Estado de cada política. Si alguna no existe, reportar error y NO continuar.

---

### AGENTE-02 | ANALIZAR_CONSTRUCCION_OBS_LOCO_48
**Tarea:** Verificar la construcción del vector de observación de 48 dims para la política de locomoción DR:
```bash
cd /home/udc/Unitree_G1
conda run -p envs/g1_udc python -c "
# La política DR fue entrenada con HumanoidVerse
# obs_keys ordenados ALFABÉTICAMENTE:
# actions(12) | base_ang_vel(3) | base_lin_vel(3) | command_ang_vel(1) | 
# command_lin_vel(2) | dof_pos(12) | dof_vel(12) | projected_gravity(3)
# TOTAL: 12+3+3+1+2+12+12+3 = 48 dims

obs_loco = {
    'actions': 12,           # acciones previas (piernas)
    'base_ang_vel': 3,       # velocidad angular IMU (rad/s)
    'base_lin_vel': 3,       # velocidad lineal body frame (m/s)
    'command_ang_vel': 1,    # wz del comando (de nav policy)
    'command_lin_vel': 2,    # vx, vy del comando (de nav policy)
    'dof_pos': 12,           # posición joints piernas
    'dof_vel': 12,           # velocidad joints piernas
    'projected_gravity': 3,  # gravedad proyectada en body frame
}
total = sum(obs_loco.values())
print('=== OBS LOCOMOCIÓN (48 dims, orden ALFABÉTICO) ===')
for i, (k, v) in enumerate(sorted(obs_loco.items())):
    print(f'  [{sum(list(sorted(obs_loco.values()))[:i]):2d}:{sum(list(sorted(obs_loco.values()))[:i+1]):2d}] {k}: {v} dims')
print(f'TOTAL: {total}')
assert total == 48

# Verificar cómo se concatenan
import numpy as np
actions = np.zeros(12)
base_ang_vel = np.zeros(3)
base_lin_vel = np.zeros(3)
cmd_ang_vel = np.zeros(1)
cmd_lin_vel = np.zeros(2)
dof_pos = np.zeros(12)
dof_vel = np.zeros(12)
proj_gravity = np.array([0, 0, -1.0])  # en stand: gravedad apunta abajo

# Orden ALFABÉTICO (como HumanoidVerse los ordena en línea 524 de legged_robot_base.py)
obs_vec = np.concatenate([actions, base_ang_vel, base_lin_vel, cmd_ang_vel, cmd_lin_vel, dof_pos, dof_vel, proj_gravity])
print(f'obs_vec shape: {obs_vec.shape}')
assert obs_vec.shape == (48,)
print('OBS LOCO CONSTRUCCIÓN OK')
"
```
**Reportar:** Tabla de índices exactos de cada campo en el vector de 48 dims. Confirmar orden alfabético.

---

### AGENTE-03 | ANALIZAR_MAPEO_JOINTS_SDK
**Tarea:** Analizar el mapeo entre índices de joints en MuJoCo y los del SDK Unitree:
```bash
cd /home/udc/Unitree_G1
conda run -p envs/g1_udc python -c "
import mujoco, numpy as np
m = mujoco.MjModel.from_xml_path('escenas/g1_manipulation_full.xml')

print('=== MAPEO JOINTS → ACTUADORES (para d.ctrl) ===')
# En MuJoCo, d.ctrl[i] controla el actuador i
# Los actuadores de posición controlan los joints correspondientes
for i in range(min(m.nu, 45)):
    act_name = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_ACTUATOR, i)
    jnt_id = m.actuator_trnid[i, 0]  # joint que controla
    jnt_name = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_JOINT, jnt_id)
    print(f'  ctrl[{i:2d}] → act={act_name:40s} → joint={jnt_name}')

print()
print('RESUMEN GRUPOS:')
print('  ctrl[0:12]  = PIERNAS (12 DOF)')
print('  ctrl[12:24] = BRAZOS IZQUIERDO (verificar)')
print('  ctrl[24:36] = BRAZOS DERECHO (verificar)')
print('  ctrl[36:43] = DEDOS (verificar)')
print('  ctrl[43:45] = CABEZA (head_yaw, head_pitch)')
"
```
**Reportar:** Mapeo completo ctrl[i] → joint. Confirmar qué índices corresponden a piernas, brazos, dedos, cabeza.

---

### AGENTE-04 | ANALIZAR_TIEMPOS_CICLO_50HZ
**Tarea:** Medir los tiempos de cada componente del pipeline para verificar que cumplen 50Hz:
```bash
cd /home/udc/Unitree_G1
conda run -p envs/g1_udc python -c "
import torch, mujoco, time, numpy as np

m = mujoco.MjModel.from_xml_path('escenas/g1_manipulation_scene.xml')
d = mujoco.MjData(m)
mujoco.mj_resetDataKeyframe(m, d, 0)
mujoco.mj_forward(m, d)

# Cargar políticas
loco = torch.jit.load('politicas/model_DR_jit.pt', map_location='cpu')
nav = torch.jit.load('politicas/model_nav_jit.pt', map_location='cpu')
# grasp: usar obs_dim de g1_constants
import sys; sys.path.insert(0, '.')
from simulacion.g1_constants import GRASP_OBS_DIM
grasp = torch.jit.load('politicas/model_grasp_jit.pt', map_location='cpu')

N = 1000
print('=== BENCHMARK TIEMPOS (N=1000 iteraciones) ===')

# Tiempo de inferencia de cada política
for name, policy, obs_dim in [
    ('LOCO  (48→12)', loco, 48),
    ('NAV   (135→3)', nav, 135),
    (f'GRASP ({GRASP_OBS_DIM}→28)', grasp, GRASP_OBS_DIM),
]:
    obs = torch.zeros(1, obs_dim)
    for _ in range(100): policy(obs)  # warmup
    t0 = time.perf_counter()
    for _ in range(N):
        with torch.no_grad(): policy(obs)
    dt = (time.perf_counter() - t0) / N * 1000
    print(f'  {name}: {dt:.3f} ms/step  ({1000/dt:.0f} Hz)')

# Tiempo de mj_step
t0 = time.perf_counter()
for _ in range(N): mujoco.mj_step(m, d)
dt_mjstep = (time.perf_counter() - t0) / N * 1000
print(f'  mj_step: {dt_mjstep:.3f} ms/step')

# Total pipeline estimado
total = 0.2 + 0.1 + 0.5 + dt_mjstep  # estimado
print()
print(f'Pipeline total estimado: ~{total:.1f} ms')
print(f'Presupuesto a 50Hz: 20ms')
print(f'Margen disponible: {20-total:.1f} ms para sensores y SDK')
"
```
**Reportar:** Tabla de tiempos por componente. ¿Cumple el presupuesto de 20ms para 50Hz?

---

## FASE 2 — Implementación del Orquestador (Agentes 5-12, EN PARALELO)

### AGENTE-05 | IMPLEMENTAR_BUILD_LOCO_OBS
**Tarea:** Implementar `simulacion/obs_builders.py` — función `build_loco_obs()` que construye el vector de 48 dims:
```bash
cat > /home/udc/Unitree_G1/simulacion/obs_builders.py << 'PYEOF'
"""
Constructores de vectores de observación para las 3 políticas del G1.
Usado por el FSM orquestador y los scripts de simulación.
"""
import numpy as np
import mujoco

# Importar constantes
import sys; sys.path.insert(0, '/home/udc/Unitree_G1')
from simulacion.g1_constants import (
    LOCO_JOINT_IDS, GRASP_OBS_DIM, NAV_OBS_DIM,
    LIDAR_SENSOR_START_IDX,
    TOUCH_LEFT_IDS, TOUCH_RIGHT_IDS,
    ARM_LEFT_JOINT_IDS, ARM_RIGHT_JOINT_IDS,
    FINGER_LEFT_JOINT_IDS, FINGER_RIGHT_JOINT_IDS,
    NAV_ACTION_VX_SCALE, NAV_ACTION_VY_SCALE, NAV_ACTION_WZ_SCALE,
)


def build_loco_obs(m, d, cmd_vel, prev_actions_loco):
    """
    Construye el vector de observación de 48 dims para model_DR_jit.pt.
    Orden ALFABÉTICO (HumanoidVerse obs_keys sorted):
      actions(12) | base_ang_vel(3) | base_lin_vel(3) | command_ang_vel(1) |
      command_lin_vel(2) | dof_pos(12) | dof_vel(12) | projected_gravity(3)
    
    Args:
        m: MjModel
        d: MjData
        cmd_vel: array (3,) = [vx, vy, wz] del nav policy (escalados a m/s, rad/s)
        prev_actions_loco: array (12,) acciones previas de locomoción
    Returns:
        obs: array (48,)
    """
    # IMU pelvis: velocidad angular y lineal
    pelvis_id = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, 'pelvis')
    imu_ang_vel = d.cvel[pelvis_id, :3].copy()   # vel angular body frame
    imu_lin_vel = d.cvel[pelvis_id, 3:].copy()   # vel lineal body frame

    # Gravedad proyectada en body frame del pelvis
    R = d.xmat[pelvis_id].reshape(3, 3)
    gravity_world = np.array([0, 0, -1.0])
    proj_gravity = R.T @ gravity_world

    # DOF pos y vel de las piernas
    dof_pos = d.qpos[7:7+12].copy()   # skip freejoint (7 dims)
    dof_vel = d.qvel[6:6+12].copy()   # skip freejoint (6 dims)

    # Comandos de velocidad (de nav policy, escalados)
    vx = np.clip(cmd_vel[0] * NAV_ACTION_VX_SCALE, -0.3, 1.0)
    vy = np.clip(cmd_vel[1] * NAV_ACTION_VY_SCALE, -0.3, 0.3)
    wz = np.clip(cmd_vel[2] * NAV_ACTION_WZ_SCALE, -1.0, 1.0)

    # Concatenar en orden ALFABÉTICO
    obs = np.concatenate([
        prev_actions_loco,   # actions (12)
        imu_ang_vel,         # base_ang_vel (3)
        imu_lin_vel,         # base_lin_vel (3)
        [wz],                # command_ang_vel (1)
        [vx, vy],            # command_lin_vel (2)
        dof_pos,             # dof_pos (12)
        dof_vel,             # dof_vel (12)
        proj_gravity,        # projected_gravity (3)
    ]).astype(np.float32)

    assert obs.shape == (48,), f"build_loco_obs: shape={obs.shape}"
    return obs


def build_nav_obs(m, d, objetivo_pos, prev_vel):
    """
    Construye el vector de observación de 135 dims para model_nav_jit.pt.
    
    Args:
        m: MjModel
        d: MjData
        objetivo_pos: array (3,) posición del objetivo en world frame
        prev_vel: array (3,) velocidad actual [vx, vy, wz]
    Returns:
        obs: array (135,)
    """
    from entrenamiento.utils.lidar_preprocessing import sim_lidar_to_obs
    
    # LIDAR 128 valores
    lidar_obs = sim_lidar_to_obs(d.sensordata, LIDAR_SENSOR_START_IDX)

    # Posición del robot
    robot_pos = d.qpos[:3].copy()  # freejoint position

    # Orientación (yaw) del robot
    quat = d.qpos[3:7].copy()  # [w, x, y, z] del freejoint
    qw, qx, qy, qz = quat
    yaw = np.arctan2(2*(qw*qz + qx*qy), 1 - 2*(qy*qy + qz*qz))

    # Posición objetivo relativa en frame del robot
    dx_world = objetivo_pos[0] - robot_pos[0]
    dy_world = objetivo_pos[1] - robot_pos[1]
    dx_robot = np.cos(-yaw) * dx_world - np.sin(-yaw) * dy_world
    dy_robot = np.sin(-yaw) * dx_world + np.cos(-yaw) * dy_world

    dist = np.sqrt(dx_world**2 + dy_world**2)
    yaw_to_goal = np.arctan2(dy_world, dx_world)
    yaw_error = yaw_to_goal - yaw
    yaw_error = (yaw_error + np.pi) % (2*np.pi) - np.pi

    obs = np.concatenate([
        lidar_obs,           # (128,) LIDAR normalizado
        [dx_robot, dy_robot], # (2,) posición relativa al objetivo
        [dist],              # (1,) distancia euclidiana
        [yaw_error],         # (1,) error de orientación
        prev_vel,            # (3,) [vx, vy, wz] actuales
    ]).astype(np.float32)

    assert obs.shape == (135,), f"build_nav_obs: shape={obs.shape}"
    return obs


def build_grasp_obs(m, d, box_pos_rel, box_quat, prev_actions_grasp):
    """
    Construye el vector de observación para model_grasp_jit.pt.
    
    Args:
        m: MjModel
        d: MjData
        box_pos_rel: array (3,) posición caja en frame torso
        box_quat: array (4,) orientación caja
        prev_actions_grasp: array (28,) acciones previas de agarre
    Returns:
        obs: array (GRASP_OBS_DIM,)
    """
    # Joints de brazos y dedos
    q_arm_l  = d.qpos[ARM_LEFT_JOINT_IDS]
    q_arm_r  = d.qpos[ARM_RIGHT_JOINT_IDS]
    q_fing_l = d.qpos[FINGER_LEFT_JOINT_IDS]
    q_fing_r = d.qpos[FINGER_RIGHT_JOINT_IDS]
    
    dq_arm_l  = d.qvel[ARM_LEFT_JOINT_IDS]
    dq_arm_r  = d.qvel[ARM_RIGHT_JOINT_IDS]
    dq_fing_l = d.qvel[FINGER_LEFT_JOINT_IDS]
    dq_fing_r = d.qvel[FINGER_RIGHT_JOINT_IDS]
    
    # Touch sensors
    touch_l = d.sensordata[TOUCH_LEFT_IDS]
    touch_r = d.sensordata[TOUCH_RIGHT_IDS]

    obs = np.concatenate([
        box_pos_rel,       # (3,)
        box_quat,          # (4,)
        q_arm_l, q_arm_r,  # (7,) + (7,)
        q_fing_l, q_fing_r,# (7,) + (7,)
        dq_arm_l, dq_arm_r,# (7,) + (7,)
        dq_fing_l, dq_fing_r, # (7,) + (7,)
        touch_l, touch_r,  # (6,) + (6,)
        prev_actions_grasp,# (28,)
    ]).astype(np.float32)

    assert obs.shape == (GRASP_OBS_DIM,), f"build_grasp_obs: shape={obs.shape} != ({GRASP_OBS_DIM},)"
    return obs


if __name__ == '__main__':
    print("Test obs_builders.py")
    import mujoco
    m = mujoco.MjModel.from_xml_path('/home/udc/Unitree_G1/escenas/g1_manipulation_scene.xml')
    d = mujoco.MjData(m)
    mujoco.mj_resetDataKeyframe(m, d, 0)
    mujoco.mj_forward(m, d)
    
    obs_loco = build_loco_obs(m, d, np.zeros(3), np.zeros(12))
    print(f'  obs_loco: {obs_loco.shape} OK')
    
    obs_nav = build_nav_obs(m, d, np.array([2.0, 0, 0]), np.zeros(3))
    print(f'  obs_nav: {obs_nav.shape} OK')
    
    obs_grasp = build_grasp_obs(m, d, np.array([0.5, 0, 0.15]), np.array([1,0,0,0]), np.zeros(28))
    print(f'  obs_grasp: {obs_grasp.shape} OK')
    
    print("obs_builders.py OK")
PYEOF
conda run -p /home/udc/Unitree_G1/envs/g1_udc python simulacion/obs_builders.py
```
**Reportar:** Stdout completo del test. Confirmar shapes (48,), (135,), (GRASP_OBS_DIM,).

---

### AGENTE-06 | IMPLEMENTAR_BOX_DETECTOR
**Tarea:** Implementar `simulacion/box_detector.py`:
```bash
cat > /home/udc/Unitree_G1/simulacion/box_detector.py << 'PYEOF'
"""
Detector de posición de la caja para el G1.
- En simulación: lee directamente data.body('target_box').xpos (ground truth)
- En robot real: YOLO sobre imagen RealSense + depth para obtener xyz
"""
import numpy as np
import mujoco


class BoxDetector:
    """Estima posición 3D de la caja en frame del torso del robot."""

    def __init__(self, m, use_sim_groundtruth=True, box_body_name='target_box'):
        self.m = m
        self.use_sim_groundtruth = use_sim_groundtruth
        self.box_body_id = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, box_body_name)
        self.torso_body_id = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, 'torso_link')
        if self.box_body_id < 0:
            raise ValueError(f"Body '{box_body_name}' no encontrado en el modelo")
        if self.torso_body_id < 0:
            raise ValueError("Body 'torso_link' no encontrado en el modelo")

    def get_box_pos_world(self, d):
        """Posición de la caja en world frame."""
        return d.xpos[self.box_body_id].copy()

    def get_box_pos_relative_torso(self, d):
        """
        Posición de la caja en frame del torso (para obs_grasp y obs_nav).
        Returns: array (3,) = [x, y, z] relativo al torso
        """
        box_pos_world = d.xpos[self.box_body_id].copy()
        torso_pos = d.xpos[self.torso_body_id].copy()
        torso_xmat = d.xmat[self.torso_body_id].reshape(3, 3)
        box_pos_rel = torso_xmat.T @ (box_pos_world - torso_pos)
        return box_pos_rel.astype(np.float32)

    def get_box_quat(self, d):
        """Orientación de la caja (quaternion [w, x, y, z])."""
        return d.xquat[self.box_body_id].copy().astype(np.float32)

    def is_box_in_hands(self, d, min_contacts=4, min_height=0.20):
        """
        Determina si la caja está siendo sostenida por las manos.
        Criterio: >= min_contacts dedos en contacto Y box_z > min_height
        """
        import sys; sys.path.insert(0, '/home/udc/Unitree_G1')
        from simulacion.g1_constants import TOUCH_LEFT_IDS, TOUCH_RIGHT_IDS
        touch_l = d.sensordata[TOUCH_LEFT_IDS]
        touch_r = d.sensordata[TOUCH_RIGHT_IDS]
        n_contacts = np.sum(np.concatenate([touch_l, touch_r]) > 0.1)
        box_z = d.xpos[self.box_body_id, 2]
        return n_contacts >= min_contacts and box_z > min_height


if __name__ == '__main__':
    print("Test box_detector.py")
    m = mujoco.MjModel.from_xml_path('/home/udc/Unitree_G1/escenas/g1_manipulation_scene.xml')
    d = mujoco.MjData(m)
    mujoco.mj_resetDataKeyframe(m, d, 0)
    mujoco.mj_forward(m, d)
    
    detector = BoxDetector(m)
    pos_world = detector.get_box_pos_world(d)
    pos_rel = detector.get_box_pos_relative_torso(d)
    quat = detector.get_box_quat(d)
    in_hands = detector.is_box_in_hands(d)
    
    print(f'  box_pos_world: {pos_world}')
    print(f'  box_pos_rel_torso: {pos_rel}')
    print(f'  box_quat: {quat}')
    print(f'  in_hands: {in_hands}')
    print("box_detector.py OK")
PYEOF
conda run -p /home/udc/Unitree_G1/envs/g1_udc python simulacion/box_detector.py
```
**Reportar:** Stdout completo. Verificar posiciones tienen sentido (caja debe estar ~0.5m frente al robot).

---

### AGENTE-07 | IMPLEMENTAR_HEAD_CONTROLLER
**Tarea:** Implementar `simulacion/head_controller.py`:
```bash
cat > /home/udc/Unitree_G1/simulacion/head_controller.py << 'PYEOF'
"""
Controlador de la cabeza articulada del G1 (2 DOF: yaw + pitch).
Ajusta la orientación de la cámara D435i y el LIDAR según el estado FSM.
"""
import numpy as np


class HeadController:
    """Control de cabeza G1 EDU: yaw ∈ [-90°, 90°], pitch ∈ [-50°, +35°]."""

    # Rangos del hardware (rad)
    YAW_MIN, YAW_MAX = -1.5708, 1.5708   # ±90°
    PITCH_MIN, PITCH_MAX = -0.8727, 0.6109  # -50° a +35°

    # Posiciones predefinidas (pitch, yaw) en radianes
    POSE_NEUTRAL  = (-0.35,  0.0)  # -20° abajo, centrado (default)
    POSE_SCAN     = ( 0.0,   0.0)  # horizontal para escanear
    POSE_NAV_DOWN = (-0.26,  0.0)  # -15° para ver obstáculos cercanos
    POSE_CARRY    = (-0.35,  0.0)  # -20° durante transporte

    def compute_head_target(self, state_name, box_pos_rel=None):
        """
        Calcula (pitch, yaw) objetivo según el estado FSM.

        Args:
            state_name: string del estado FSM ('DETECTAR', 'NAVEGAR_A_CAJA', etc.)
            box_pos_rel: array (3,) posición caja en frame torso (para AGARRAR)
        Returns:
            pitch: float (rad)
            yaw: float (rad)
        """
        if state_name == 'DETECTAR':
            pitch, yaw = self.POSE_SCAN

        elif state_name == 'NAVEGAR_A_CAJA':
            pitch, yaw = self.POSE_NAV_DOWN

        elif state_name == 'AGARRAR':
            if box_pos_rel is not None:
                # Apuntar dinámicamente hacia la caja
                dx, dy, dz = box_pos_rel[0], box_pos_rel[1], box_pos_rel[2]
                dist_horiz = np.sqrt(dx**2 + dy**2)
                pitch = np.arctan2(-dz, dist_horiz)  # negativo porque cámara mira hacia abajo
                yaw = np.arctan2(dy, dx)
            else:
                pitch, yaw = -0.52, 0.0  # -30° fijo hacia la caja

        elif state_name in ('TRANSPORTAR', 'NAVEGAR_A_DEPOSITO'):
            pitch, yaw = self.POSE_CARRY

        elif state_name == 'DEPOSITAR':
            pitch, yaw = -0.52, 0.0  # mirar hacia abajo para depositar

        else:  # FIN, default
            pitch, yaw = self.POSE_NEUTRAL

        # Clip a rangos del hardware
        pitch = np.clip(pitch, self.PITCH_MIN, self.PITCH_MAX)
        yaw = np.clip(yaw, self.YAW_MIN, self.YAW_MAX)
        return float(pitch), float(yaw)

    def smooth_target(self, current_pitch, current_yaw, target_pitch, target_yaw, alpha=0.1):
        """Interpolación suave para evitar movimientos bruscos."""
        new_pitch = current_pitch + alpha * (target_pitch - current_pitch)
        new_yaw = current_yaw + alpha * (target_yaw - current_yaw)
        return float(new_pitch), float(new_yaw)


if __name__ == '__main__':
    print("Test head_controller.py")
    hc = HeadController()
    states = ['DETECTAR', 'NAVEGAR_A_CAJA', 'AGARRAR', 'TRANSPORTAR', 'NAVEGAR_A_DEPOSITO', 'DEPOSITAR']
    box_pos = np.array([0.5, 0.0, -0.1])
    for s in states:
        p, y = hc.compute_head_target(s, box_pos)
        assert HeadController.PITCH_MIN <= p <= HeadController.PITCH_MAX, f"pitch={p} fuera de rango"
        assert HeadController.YAW_MIN <= y <= HeadController.YAW_MAX, f"yaw={y} fuera de rango"
        print(f'  {s:25s}: pitch={np.degrees(p):+6.1f}° yaw={np.degrees(y):+6.1f}°')
    print("head_controller.py OK")
PYEOF
conda run -p /home/udc/Unitree_G1/envs/g1_udc python simulacion/head_controller.py
```
**Reportar:** Stdout completo. Verificar que todos los ángulos están dentro del rango del hardware.

---

### AGENTE-08 | IMPLEMENTAR_FSM_ORCHESTRATOR
**Tarea:** Implementar `simulacion/fsm_orchestrator.py` — el orquestador completo:
```bash
# Implementar la clase FSMOrquestador con los 6 estados y sus transiciones.
# Debe usar obs_builders.py, box_detector.py y head_controller.py.
# Estados: DETECTAR, NAVEGAR_A_CAJA, AGARRAR, TRANSPORTAR, NAVEGAR_A_DEPOSITO, DEPOSITAR, FIN
# Cada estado debe:
#   1. Construir los obs necesarios con obs_builders.py
#   2. Llamar a las políticas correspondientes
#   3. Retornar (ctrl_piernas, ctrl_brazos, ctrl_cabeza)
#   4. Verificar condiciones de transición al siguiente estado
#
# Transiciones (umbrales iniciales, ajustar en AGENTE-23):
#   DETECTAR → NAVEGAR_A_CAJA: cuando detector.get_box_pos_world() retorna posición válida
#   NAVEGAR_A_CAJA → AGARRAR: cuando dist(robot, caja) < 0.35m
#   AGARRAR → TRANSPORTAR: cuando detector.is_box_in_hands() es True (≥4 contactos, box_z>0.20m)
#   TRANSPORTAR = NAVEGAR_A_DEPOSITO (misma política, objetivo=depósito)
#   NAVEGAR_A_DEPOSITO → DEPOSITAR: cuando dist(robot, depósito) < 0.30m
#   DEPOSITAR → FIN: cuando caja en suelo (box_z < 0.18m) y dedos abiertos (touch < 0.1N)
```
**Verificar:**
```bash
conda run -p envs/g1_udc python -c "
from simulacion.fsm_orchestrator import FSMOrquestador, Estado
print('FSM importado OK')
print(f'Estados: {[e.name for e in Estado]}')
"
```
**Reportar:** Archivo creado. Test de importación OK. Lista de estados y transiciones implementadas.

---

### AGENTE-09 | IMPLEMENTAR_PIPELINE_COMPLETO
**Tarea:** Implementar `simulacion/pipeline_completo.py` — el script principal:
```bash
# El script debe:
# - Cargar las 3 políticas
# - Cargar la escena g1_manipulation_scene.xml
# - Inicializar FSM, BoxDetector, HeadController
# - Loop principal a 50Hz
# - Modos: --headless y normal (con visor)
# - Argumentos: --duration 180 --episodes N --random_positions

# Uso:
# conda run -p /home/udc/Unitree_G1/envs/g1_udc python simulacion/pipeline_completo.py \
#   --headless --duration 180 --episodes 1
```
**Verificar:**
```bash
conda run -p envs/g1_udc python -m py_compile simulacion/pipeline_completo.py && echo "PIPELINE SYNTAX OK"
```
**Reportar:** Archivo creado, test de sintaxis OK. Argumentos disponibles.

---

### AGENTE-10 | IMPLEMENTAR_ESTADO_DETECTAR
**Tarea:** Implementar y probar el estado DETECTAR de forma aislada:
```bash
cd /home/udc/Unitree_G1
conda run -p envs/g1_udc python -c "
import mujoco, numpy as np, sys
sys.path.insert(0, '.')
import mujoco
m = mujoco.MjModel.from_xml_path('escenas/g1_manipulation_scene.xml')
d = mujoco.MjData(m)
mujoco.mj_resetDataKeyframe(m, d, 0)
mujoco.mj_forward(m, d)

from simulacion.box_detector import BoxDetector
detector = BoxDetector(m)

# Test DETECTAR: ¿el detector encuentra la caja?
pos_world = detector.get_box_pos_world(d)
pos_rel = detector.get_box_pos_relative_torso(d)
quat = detector.get_box_quat(d)

print(f'Estado DETECTAR:')
print(f'  Posición caja (world): {pos_world}')
print(f'  Posición caja (rel torso): {pos_rel}')
print(f'  Orientación caja: {quat}')
print(f'  Distancia al robot: {np.linalg.norm(pos_world[:2]):.3f}m')
print(f'  Transición DETECTAR→NAVEGAR: {\"SÍ\" if pos_world is not None else \"NO\"}')
print('ESTADO DETECTAR OK')
"
```
**Reportar:** Posición de la caja detectada. Verificar que está a ~0.6m del robot (posición inicial).

---

### AGENTE-11 | IMPLEMENTAR_ESTADO_NAVEGAR_AGARRAR
**Tarea:** Probar los estados NAVEGAR_A_CAJA y AGARRAR de forma aislada (sin pasar por todo el pipeline):
```bash
cd /home/udc/Unitree_G1
conda run -p envs/g1_udc python -c "
import mujoco, numpy as np, torch, sys
sys.path.insert(0, '.')
from simulacion.obs_builders import build_nav_obs, build_grasp_obs
from simulacion.box_detector import BoxDetector

m = mujoco.MjModel.from_xml_path('escenas/g1_manipulation_scene.xml')
d = mujoco.MjData(m)
mujoco.mj_resetDataKeyframe(m, d, 0)
mujoco.mj_forward(m, d)

detector = BoxDetector(m)
nav_policy = torch.jit.load('politicas/model_nav_jit.pt')
grasp_policy = torch.jit.load('politicas/model_grasp_jit.pt')

# Test NAVEGAR: ¿la política genera comandos de velocidad razonables?
box_pos = detector.get_box_pos_world(d)
obs_nav = build_nav_obs(m, d, box_pos, np.zeros(3))
with torch.no_grad():
    cmd_vel = nav_policy(torch.tensor(obs_nav).unsqueeze(0)).squeeze().numpy()
print(f'Test NAVEGAR_A_CAJA:')
print(f'  obs_nav shape: {obs_nav.shape}')
print(f'  cmd_vel: vx={cmd_vel[0]:.3f}, vy={cmd_vel[1]:.3f}, wz={cmd_vel[2]:.3f}')

# Test AGARRAR: ¿la política genera acciones razonables para los dedos?
box_pos_rel = detector.get_box_pos_relative_torso(d)
box_quat = detector.get_box_quat(d)
from simulacion.g1_constants import GRASP_OBS_DIM
obs_grasp = build_grasp_obs(m, d, box_pos_rel, box_quat, np.zeros(28))
with torch.no_grad():
    actions = grasp_policy(torch.tensor(obs_grasp).unsqueeze(0)).squeeze().numpy()
print()
print(f'Test AGARRAR:')
print(f'  obs_grasp shape: {obs_grasp.shape}')
print(f'  actions brazos izq: {actions[:7]}')
print(f'  actions dedos izq:  {actions[7:14]}')
print(f'  actions rango: [{actions.min():.3f}, {actions.max():.3f}]')
print('ESTADOS NAVEGAR/AGARRAR OK')
"
```
**Reportar:** Stdout completo. Verificar que las acciones están en rango razonable.

---

### AGENTE-12 | VERIFICAR_CTRL_MAPPING
**Tarea:** Verificar que el mapeo ctrl[] → joints es correcto aplicando acciones de prueba:
```bash
cd /home/udc/Unitree_G1
conda run -p envs/g1_udc python -c "
import mujoco, numpy as np
m = mujoco.MjModel.from_xml_path('escenas/g1_manipulation_full.xml')
d = mujoco.MjData(m)
mujoco.mj_resetDataKeyframe(m, d, 0)
mujoco.mj_forward(m, d)

print('=== VERIFICACIÓN CTRL MAPPING ===')
print(f'nu={m.nu} actuadores total')
print()

# Guardar qpos inicial
qpos_init = d.qpos.copy()

# Test: aplicar acción pequeña a brazo izquierdo (ctrl[12])
d.ctrl[:] = 0  # todo a 0
# Piernas en posición de pie (usar qpos del keyframe)
for i in range(12):
    jnt_id = m.actuator_trnid[i, 0]
    d.ctrl[i] = d.qpos[m.jnt_qposadr[jnt_id]]  # mantener posición actual

# Avanzar 10 pasos
for _ in range(10): mujoco.mj_step(m, d)
print(f'Después de 10 pasos sin acción de brazos:')
print(f'  qpos[7:19] (piernas): min={d.qpos[7:19].min():.3f} max={d.qpos[7:19].max():.3f}')
print(f'  ctrl[:12] (piernas): {d.ctrl[:12]}')
print()
print(f'ctrl[40:45] corresponde a (verificar):')
for i in range(40, 45):
    act_name = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_ACTUATOR, i)
    print(f'  ctrl[{i}] = {act_name}')
print('CTRL MAPPING OK')
"
```
**Reportar:** Confirmación de que ctrl[0:12]=piernas, ctrl[43:45]=cabeza. Índices exactos de brazos y dedos.

---

## FASE 3 — Pruebas de Integración por Estado (Agentes 13-20, SECUENCIAL)

### AGENTE-13 | PROBAR_DETECTAR_A_NAVEGAR
**Tarea:** Probar la transición DETECTAR → NAVEGAR_A_CAJA (10 episodios):
```bash
cd /home/udc/Unitree_G1
conda run -p envs/g1_udc python simulacion/pipeline_completo.py \
  --headless --max_state NAVEGAR_A_CAJA --episodes 10 --duration 60
```
**Verificar:** ¿El robot detecta la caja y empieza a moverse hacia ella? ¿Se queda atascado en DETECTAR?  
**Reportar:** Por episodio: ¿llegó a NAVEGAR?, distancia final a la caja, tiempo.

---

### AGENTE-14 | PROBAR_NAVEGAR_A_CAJA_COMPLETO
**Tarea:** Probar hasta llegar a distancia de agarre (10 episodios, máx 90s):
```bash
cd /home/udc/Unitree_G1
conda run -p envs/g1_udc python simulacion/pipeline_completo.py \
  --headless --max_state AGARRAR_START --episodes 10 --duration 90
```
**Métrica clave:** ¿El robot llega a <0.35m de la caja? Si no llega, ¿cuál es la distancia mínima alcanzada?  
**Reportar:** Tabla: ep | dist_inicial | dist_final | ¿llegó (<0.35m)? | tiempo.

---

### AGENTE-15 | PROBAR_ESTADO_AGARRAR
**Tarea:** Probar el agarre con el robot ya posicionado cerca de la caja (10 episodios):
```bash
cd /home/udc/Unitree_G1
# Modificar la escena temporalmente para poner la caja a 0.3m del robot
conda run -p envs/g1_udc python simulacion/pipeline_completo.py \
  --headless --max_state AGARRAR --episodes 10 --duration 60 --box_init_dist 0.30
```
**Verificar:** ¿Los brazos se extienden hacia la caja? ¿Los dedos cierran? ¿Se detectan ≥4 contactos?  
**Reportar:** Por episodio: ¿n_contactos >= 4?, altura máxima caja, fuerzas medias de contacto.

---

### AGENTE-16 | PROBAR_TRANSICION_AGARRAR_TRANSPORTAR
**Tarea:** Probar la transición AGARRAR → TRANSPORTAR (criterio: 4 contactos + box_z > 0.20m):
```bash
cd /home/udc/Unitree_G1
conda run -p envs/g1_udc python simulacion/pipeline_completo.py \
  --headless --max_state TRANSPORTAR --episodes 10 --duration 90 --box_init_dist 0.30
```
**Verificar:** ¿La transición se activa correctamente? ¿El robot mantiene el agarre al empezar a caminar?  
**Reportar:** Por episodio: ¿llegó a TRANSPORTAR?, contactos en el momento de transición.

---

### AGENTE-17 | PROBAR_TRANSPORTE_Y_NAV_DEPOSITO
**Tarea:** Probar TRANSPORTAR → NAVEGAR_A_DEPOSITO (robot camina con caja):
```bash
cd /home/udc/Unitree_G1
conda run -p envs/g1_udc python simulacion/pipeline_completo.py \
  --headless --max_state NAVEGAR_A_DEPOSITO --episodes 10 --duration 120 --box_init_dist 0.30
```
**Verificar:** ¿El robot mantiene el agarre mientras camina? ¿Se cae la caja? ¿Llega al depósito?  
**Reportar:** Por episodio: ¿perdió la caja?, dist_final al depósito, ¿completó NAV_DEPOSITO?

---

### AGENTE-18 | PROBAR_DEPOSITAR
**Tarea:** Probar el estado DEPOSITAR (abrir dedos):
```bash
cd /home/udc/Unitree_G1
conda run -p envs/g1_udc python simulacion/pipeline_completo.py \
  --headless --max_state FIN --episodes 5 --duration 30 --start_state DEPOSITAR
```
**Verificar:** ¿Los dedos se abren gradualmente? ¿La caja cae controladamente al suelo?  
**Reportar:** Descripción del comportamiento de apertura de dedos. Posición final de la caja.

---

### AGENTE-19 | PROBAR_PIPELINE_COMPLETO_5_EPISODIOS
**Tarea:** Smoke test del pipeline COMPLETO (5 episodios de 180s):
```bash
cd /home/udc/Unitree_G1
conda run -p envs/g1_udc python simulacion/pipeline_completo.py \
  --headless --duration 180 --episodes 5
```
**Por episodio:** Estado final alcanzado, tiempo en cada estado, ¿completó la tarea?  
**Reportar:** Tabla de 5 episodios con estado final y tiempos.

---

### AGENTE-20 | PROBAR_PIPELINE_COMPLETO_10_EPISODIOS
**Tarea:** Prueba completa de 10 episodios con posiciones aleatorias de la caja:
```bash
cd /home/udc/Unitree_G1
conda run -p envs/g1_udc python simulacion/pipeline_completo.py \
  --headless --duration 180 --episodes 10 --random_positions
```
**Por episodio registrar:**
- Estado final (DETECTAR/NAVEGAR/AGARRAR/TRANSPORTAR/NAV_DEPOSITO/DEPOSITAR/FIN)
- Tiempo en cada estado
- ¿Completó la tarea?
- Incidentes observados (caída, pérdida de caja, timeout)  
**Reportar:** Tabla detallada de 10 episodios.

---

## FASE 4 — Análisis y Ajuste (Agentes 21-27, SECUENCIAL)

### AGENTE-21 | ANALIZAR_FALLOS_Y_BOTTLENECKS
**Tarea:** Analizar los logs de los 10 episodios para identificar los bottlenecks principales:
```bash
cd /home/udc/Unitree_G1
conda run -p envs/g1_udc python -c "
# Leer logs de pipeline_completo.py
# Identificar:
# 1. ¿En qué estado se atasca más el robot? (tiempo medio por estado)
# 2. ¿Cuál es el estado con mayor tasa de fallo? (no llega al siguiente)
# 3. ¿Se pierde la caja durante el transporte?
# 4. ¿El robot se cae en algún episodio?
import json, os
log_files = sorted([f for f in os.listdir('/tmp') if f.startswith('pipeline_ep')])
for lf in log_files:
    with open(f'/tmp/{lf}') as f:
        data = json.load(f)
    print(f'{lf}: estado_final={data[\"estado_final\"]}')
"
```
**Reportar:** Lista priorizada de bottlenecks. Recomendaciones de ajuste de umbrales.

---

### AGENTE-22 | MEDIR_OVERHEAD_ORQUESTADOR
**Tarea:** Medir el overhead del orquestador FSM completo (tiempo por ciclo a 50Hz):
```bash
cd /home/udc/Unitree_G1
conda run -p envs/g1_udc python -c "
import mujoco, numpy as np, torch, time, sys
sys.path.insert(0, '.')
from simulacion.fsm_orchestrator import FSMOrquestador, Estado
from simulacion.box_detector import BoxDetector
from simulacion.head_controller import HeadController

m = mujoco.MjModel.from_xml_path('escenas/g1_manipulation_scene.xml')
d = mujoco.MjData(m)
mujoco.mj_resetDataKeyframe(m, d, 0)
mujoco.mj_forward(m, d)

# Cargar políticas
loco = torch.jit.load('politicas/model_DR_jit.pt')
nav = torch.jit.load('politicas/model_nav_jit.pt')
grasp = torch.jit.load('politicas/model_grasp_jit.pt')
detector = BoxDetector(m)
head = HeadController()

fsm = FSMOrquestador(loco, nav, grasp, detector, head)

N = 500
times = []
for _ in range(N):
    t0 = time.perf_counter()
    # Simular un ciclo completo del orquestador
    # (sin mj_step para medir solo el overhead del FSM)
    ctrl_piernas, ctrl_brazos, ctrl_cabeza = fsm.step(m, d)
    times.append(time.perf_counter() - t0)

times_ms = np.array(times) * 1000
print(f'Overhead orquestador FSM (N={N}):')
print(f'  Media: {times_ms.mean():.2f} ms')
print(f'  P95:   {np.percentile(times_ms, 95):.2f} ms')
print(f'  Max:   {times_ms.max():.2f} ms')
print(f'  Presupuesto 50Hz: 20ms')
print(f'  Margen: {20 - times_ms.mean():.1f} ms para mj_step y sensores')
"
```
**Reportar:** Latencia del orquestador. ¿Cumple el presupuesto de 20ms?

---

### AGENTE-23 | AJUSTAR_UMBRALES_TRANSICION
**Tarea:** Basándose en AGENTE-21, ajustar los umbrales de transición de la FSM:
- Si robot intenta agarrar demasiado lejos → reducir umbral NAVEGAR→AGARRAR (0.35m → 0.30m)
- Si no detecta la transición AGARRAR→TRANSPORTAR → reducir min_contacts (4 → 3)
- Si pierde la caja durante transporte → aumentar threshold de monitoreo de contactos
- Si no llega al depósito → aumentar umbral NAVEGAR_DEPOSITO→DEPOSITAR (0.30m → 0.40m)

Documentar cada ajuste con **antes** y **después** y justificación.  
**Reportar:** Lista de parámetros ajustados. Cambios en `fsm_orchestrator.py`.

---

### AGENTE-24 | VALIDAR_DESPUES_AJUSTES_5_EPISODIOS
**Tarea:** Repetir 5 episodios con los umbrales ajustados:
```bash
cd /home/udc/Unitree_G1
conda run -p envs/g1_udc python simulacion/pipeline_completo.py \
  --headless --duration 180 --episodes 5
```
**Comparar:** Resultados pre-ajuste vs post-ajuste.  
**Reportar:** Tabla comparativa. ¿Mejoraron los resultados?

---

### AGENTE-25 | PROBAR_MANEJO_ERRORES
**Tarea:** Probar comportamiento ante errores específicos:
```bash
# Test 1: caja no visible (LIDAR obstruido por obstáculo entre robot y caja)
# Test 2: robot pierde la caja durante TRANSPORTAR (fuerza externa simula apertura de dedos)
# Test 3: caja cae durante navegación
```
**Verificar:** ¿La FSM maneja estos casos graciosamente? ¿Qué estado adopta?  
**Reportar:** Comportamiento observado en cada caso de error.

---

### AGENTE-26 | PROBAR_5_POSICIONES_DISTINTAS_CAJA
**Tarea:** Probar el pipeline con 5 posiciones fijas de la caja para verificar generalización:
```bash
for pos in "1.0 0.0" "0.8 0.2" "0.8 -0.2" "1.2 0.15" "1.0 -0.15"; do
  conda run -p envs/g1_udc python simulacion/pipeline_completo.py \
    --headless --duration 180 --episodes 2 --box_pos $pos
done
```
**Reportar:** Por posición: ¿completó la tarea? Estado final alcanzado.

---

### AGENTE-27 | VALIDACION_FINAL_20_EPISODIOS
**Tarea:** Validación final de 20 episodios con posiciones aleatorias:
```bash
cd /home/udc/Unitree_G1
conda run -p envs/g1_udc python simulacion/pipeline_completo.py \
  --headless --duration 180 --episodes 20 --random_positions \
  --output_log /tmp/validacion_final_plan04.json
```
**Reportar:** Tabla completa de 20 episodios:
```
| Ep | Estado final | t_detect | t_nav | t_agarre | t_transport | ¿Completó? |
```

---

## FASE 5 — Finalización (Agentes 28-30)

### AGENTE-28 | CREAR_SCRIPT_CONVENIENCE
**Tarea:** Crear `simulacion/run_pipeline.sh` — script de conveniencia para ejecutar el pipeline:
```bash
cat > /home/udc/Unitree_G1/simulacion/run_pipeline.sh << 'EOF'
#!/bin/bash
# Ejecuta el pipeline completo de manipulación G1
# Uso: ./simulacion/run_pipeline.sh [--headless] [--episodes N] [--duration T]
cd /home/udc/Unitree_G1
conda run -p /home/udc/Unitree_G1/envs/g1_udc python simulacion/pipeline_completo.py "$@"
EOF
chmod +x simulacion/run_pipeline.sh
echo "run_pipeline.sh creado"
# Test
bash simulacion/run_pipeline.sh --headless --episodes 1 --duration 10
```
**Reportar:** Script creado y funcionando.

---

### AGENTE-29 | VERIFICAR_COHERENCIA_G1_CONSTANTS
**Tarea:** Verificar que todos los índices en `g1_constants.py` son coherentes con el XML actual:
```bash
cd /home/udc/Unitree_G1
conda run -p envs/g1_udc python -c "
import mujoco, numpy as np, sys
sys.path.insert(0, '.')
m = mujoco.MjModel.from_xml_path('escenas/g1_manipulation_full.xml')
d = mujoco.MjData(m)
mujoco.mj_resetDataKeyframe(m, d, 0)
mujoco.mj_forward(m, d)

from simulacion import g1_constants as c

print('=== VERIFICACIÓN g1_constants.py ===')

# Verificar LIDAR
lidar_end = c.LIDAR_SENSOR_START_IDX + 128
assert lidar_end <= len(d.sensordata), f'LIDAR fuera de sensordata: {lidar_end} > {len(d.sensordata)}'
print(f'LIDAR indices [{c.LIDAR_SENSOR_START_IDX}:{lidar_end}]: OK')

# Verificar TOUCH
for tname, tids in [('TOUCH_LEFT', c.TOUCH_LEFT_IDS), ('TOUCH_RIGHT', c.TOUCH_RIGHT_IDS)]:
    assert max(tids) < len(d.sensordata), f'{tname} fuera de sensordata'
    print(f'{tname} indices {tids}: OK')

# Verificar GRASP_OBS_DIM
print(f'GRASP_OBS_DIM={c.GRASP_OBS_DIM} (confirmar con Plan 02)')
print(f'NAV_OBS_DIM={c.NAV_OBS_DIM} (debe ser 135)')
assert c.NAV_OBS_DIM == 135

print()
print('g1_constants.py COHERENTE')
"
```
**Reportar:** Resultado de la verificación. Si hay inconsistencias, corregir `g1_constants.py`.

---

### AGENTE-30 | REPORTE_FINAL_Y_COMMIT
**Tarea:** Generar el reporte completo del Plan 04 y hacer el commit:

Crear `/home/udc/Unitree_G1/reportes/reporte_plan04_integracion_<FECHA>.md` con:
```
# Reporte Plan 04 — Integración Jerárquica 3 Políticas G1
## Fecha y hora
## Resumen ejecutivo (¿funciona el pipeline completo?)
## Resultado de cada agente (01-30):
   - Comando exacto ejecutado
   - Stdout/stderr completo
   - Errores y soluciones
## Diagrama FSM implementada (estados + umbrales exactos de transición)
## Tabla de validación final (20 episodios):
   | Ep | Estado_final | t_detectar(s) | t_navegar(s) | t_agarrar(s) | t_transport(s) | ¿Completó? |
## Tasa de éxito por estado (% episodios que llegan a cada estado)
## Benchmark tiempos:
   | Componente | Latencia (ms) | ¿Cumple 50Hz? |
## Umbrales FSM ajustados (AGENTE-23):
   | Parámetro | Valor original | Valor ajustado | Justificación |
## Archivos creados:
   - simulacion/obs_builders.py
   - simulacion/fsm_orchestrator.py
   - simulacion/box_detector.py
   - simulacion/head_controller.py
   - simulacion/pipeline_completo.py
   - simulacion/run_pipeline.sh
## Problemas encontrados y soluciones
## Conclusión: ¿sistema listo para robot físico?
## Próximos pasos (Plan 05)
```

Luego ejecutar:
```bash
cd /home/udc/Unitree_G1
git add simulacion/obs_builders.py
git add simulacion/fsm_orchestrator.py
git add simulacion/box_detector.py
git add simulacion/head_controller.py
git add simulacion/pipeline_completo.py
git add simulacion/run_pipeline.sh
git add simulacion/g1_constants.py
git add reportes/reporte_plan04_integracion_*.md
git commit -m "$(cat <<'EOF'
feat: pipeline FSM jerarquico 3 politicas G1 manipulacion

30 sub-agentes: FSM 6 estados, obs builders, deteccion caja,
controlador cabeza, validacion 20 episodios headless.
Transiciones: DETECTAR→NAV→AGARRAR→TRANSPORT→DEPOSITAR.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```
**Reportar:** Reporte completo creado. Hash del commit.
