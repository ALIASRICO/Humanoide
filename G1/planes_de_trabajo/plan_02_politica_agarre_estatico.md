# Plan de Trabajo 02 — Política de Agarre Estático (Brazos + Dedos)
**Proyecto:** Unitree G1 — Universidad de Colombia  
**Fecha:** 2026-05-14  
**Sub-agentes asignados:** 30  
**Prerequerido:** Plan 01 completado (`escenas/g1_manipulation_full.xml` existe y carga sin errores, `simulacion/g1_constants.py` existe)  
**Reporte de salida:** `reportes/reporte_plan02_agarre_<FECHA>.md`

---

## Contexto del Proyecto

Tenemos el robot Unitree G1 EDU (43 DOF) con manos articuladas de 3 dedos (pulgar 3 DOF + índice 2 DOF + medio 2 DOF por mano = 7 DOF/mano, 14 DOF total de manos). El objetivo de este plan es entrenar una política de agarre estático: el robot permanece de pie inmóvil mientras sus brazos y dedos aprenden a agarrar una caja de 30×20×30 cm que aparece frente a él en posiciones aleatorias.

**IMPORTANTE:** Las piernas permanecen CONGELADAS en posición de pie. Solo se entrenan brazos (5 DOF/lado), muñecas (2 DOF/lado) y dedos (7 DOF/lado) = 14 DOF por lado = 28 DOF totales.

### Archivos clave:
- `escenas/g1_manipulation_full.xml` — modelo completo con 46 DOF, 138 sensores (Plan 01)
- `escenas/g1_manipulation_scene.xml` — escena con caja y zona de depósito
- `simulacion/g1_constants.py` — índices de todos los sensores y joints (Plan 01)
- `politicas/model_DR_jit.pt` — política de locomoción DR (CONGELADA, NO TOCAR)
- Entrenamiento: `conda run -n hgen` (Genesis + HumanoidVerse, Python 3.10, torch 2.11.0+cu130)
- Simulación/validación: `conda run -p /home/udc/Unitree_G1/envs/g1_udc` (MuJoCo 3.8.1)
- GPU disponible: NVIDIA RTX 5090

### Espacio de acción (28 dims):
```
accion = [
  brazo_izq (5): shoulder_pitch, shoulder_roll, shoulder_yaw, elbow, wrist_roll
  muñeca_izq (2): wrist_pitch, wrist_yaw
  dedos_izq (7): thumb_0, thumb_1, thumb_2, index_0, index_1, middle_0, middle_1
  brazo_der (5): shoulder_pitch, shoulder_roll, shoulder_yaw, elbow, wrist_roll
  muñeca_der (2): wrist_pitch, wrist_yaw
  dedos_der (7): thumb_0, thumb_1, thumb_2, index_0, index_1, middle_0, middle_1
]
```

---

## FASE 1 — Análisis Previo (Agentes 1-8, EN PARALELO)

### AGENTE-01 | ANALIZAR_JOINTS_BRAZOS_DEDOS
**Tarea:** Usando el XML creado en el Plan 01, extraer y documentar TODOS los joints de brazos y dedos:
```bash
cd /home/udc/Unitree_G1
conda run -p envs/g1_udc python -c "
import mujoco
m = mujoco.MjModel.from_xml_path('escenas/g1_manipulation_full.xml')
print('=== JOINTS (nombre, id, rango) ===')
for i in range(m.njnt):
    name = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_JOINT, i)
    lo, hi = m.jnt_range[i]
    print(f'  joint[{i:2d}] {name:40s} range=[{lo:.3f}, {hi:.3f}]')
print()
print('=== ACTUADORES (nombre, id, kp) ===')
for i in range(m.nu):
    name = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_ACTUATOR, i)
    kp = m.actuator_gainprm[i, 0]
    print(f'  act[{i:2d}] {name:40s} kp={kp:.1f}')
"
```
**Extraer específicamente:**
- Índices de actuadores de brazo izquierdo (5 DOF)
- Índices de actuadores de muñeca izquierda (2 DOF)
- Índices de actuadores de dedos izquierdo (7 DOF)
- Idem para lado derecho
- Rangos exactos de cada joint de dedos

**Reportar:** Tabla completa con joint_name, joint_id, actuator_id, rango_min, rango_max para los 28 DOF de brazos+dedos.

---

### AGENTE-02 | ANALIZAR_SITIOS_CONTACTO_Y_PALMAS
**Tarea:** Extraer posiciones de los touch sensors y de los cuerpos de las palmas para usarlos en el cálculo del reward:
```bash
cd /home/udc/Unitree_G1
conda run -p envs/g1_udc python -c "
import mujoco, numpy as np
m = mujoco.MjModel.from_xml_path('escenas/g1_manipulation_full.xml')
d = mujoco.MjData(m)
mujoco.mj_resetDataKeyframe(m, d, 0)  # keyframe 'stand'
mujoco.mj_forward(m, d)

print('=== SENSORES DE CONTACTO (touch) ===')
for i in range(m.nsensor):
    name = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_SENSOR, i)
    if name and ('tip' in name or 'touch' in name or 'contact' in name):
        site_id = m.sensor_objid[i]
        site_pos = d.site_xpos[site_id]
        print(f'  sensor[{i}] {name}: site_pos={site_pos}')

print()
print('=== CUERPOS CLAVE PARA PALMAS ===')
palm_bodies = ['left_wrist_yaw_link', 'right_wrist_yaw_link',
               'left_hand_thumb_2_link', 'right_hand_thumb_2_link',
               'left_hand_index_1_link', 'right_hand_index_1_link',
               'left_hand_middle_1_link', 'right_hand_middle_1_link']
for bname in palm_bodies:
    try:
        bid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, bname)
        print(f'  {bname}: body_id={bid}, pos={d.xpos[bid]}')
    except:
        print(f'  {bname}: NO ENCONTRADO')
"
```
**Reportar:** Tabla de sensores de contacto con índices sensordata exactos. Posiciones 3D de palmas y yemas en keyframe stand.

---

### AGENTE-03 | ANALIZAR_POSICION_CAJA_Y_GEOMS
**Tarea:** Verificar que la caja (box) existe en la escena y extraer sus propiedades:
```bash
cd /home/udc/Unitree_G1
conda run -p envs/g1_udc python -c "
import mujoco, numpy as np
m = mujoco.MjModel.from_xml_path('escenas/g1_manipulation_scene.xml')
d = mujoco.MjData(m)
mujoco.mj_resetDataKeyframe(m, d, 0)
mujoco.mj_forward(m, d)

# Buscar el body de la caja
print('=== BODIES (buscar caja/box) ===')
for i in range(m.nbody):
    name = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_BODY, i)
    if name and ('box' in name.lower() or 'caja' in name.lower() or 'object' in name.lower()):
        print(f'  body[{i}] {name}: pos={d.xpos[i]}, mass={m.body_mass[i]:.3f}kg')

print()
print('=== JOINTS LIBRES (freejoint para la caja) ===')
for i in range(m.njnt):
    name = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_JOINT, i)
    if m.jnt_type[i] == 0:  # freejoint
        print(f'  joint[{i}] {name}: tipo=freejoint')

print()
print('nq={m.nq}, nv={m.nv}, nu={m.nu}, nsensor={m.nsensor}')
print(f'nbody={m.nbody}, njnt={m.njnt}')
"
```
**Reportar:** body_id de la caja, joint_id del freejoint, masa, dimensiones del geom (size), índice en qpos para leer posición de la caja.

---

### AGENTE-04 | DISEÑAR_REWARD_FUNCTION
**Tarea:** Diseñar la función de recompensa jerárquica de 4 fases. Implementar y verificar que compila:
```bash
cd /home/udc/Unitree_G1
cat > /tmp/test_reward.py << 'EOF'
import numpy as np

def compute_reward(
    palm_l_pos, palm_r_pos,   # posición de palmas izq/der (3,)
    box_pos,                   # posición de la caja (3,)
    touch_forces,              # fuerzas de contacto (12,): 6 izq + 6 der
    q_fingers,                 # posición joints dedos (14,)
    q_fingers_closed,          # configuración cerrado (14,)
    action_curr,               # acción actual (28,)
    action_prev,               # acción previa (28,)
    torques,                   # torques (28,)
    n_steps_in_contact,        # cuántos pasos con >= 2 dedos en contacto
    has_autocollision,         # bool: hay auto-colisión entre dedos
):
    """Recompensa jerárquica en 4 fases para política de agarre G1."""

    # === FASE 1: Aproximación de palmas a la caja ===
    dist_l = np.linalg.norm(palm_l_pos - box_pos)
    dist_r = np.linalg.norm(palm_r_pos - box_pos)
    r_approach = -np.mean([dist_l, dist_r]) * 1.0  # [-inf, 0], rango esperado [-2, 0]

    # === FASE 2: Cierre de dedos (solo activo si palmas cerca) ===
    near_threshold = 0.15  # 15 cm
    if min(dist_l, dist_r) < near_threshold:
        r_closure = -np.mean(np.abs(q_fingers - q_fingers_closed)) * 2.0
    else:
        r_closure = 0.0

    # === FASE 3: Contacto multipunto en yemas ===
    n_contacts = np.sum(touch_forces > 0.1)  # dedos con contacto real
    r_contact = (n_contacts / 12.0) * 3.0  # [0, 3]

    # === FASE 4: Elevación de la caja (solo si >= 4 contactos) ===
    box_z_target = 0.30  # 30 cm de altura objetivo
    box_z_init = 0.15
    if n_contacts >= 4:
        r_lift = max(0.0, box_pos[2] - box_z_init) * 5.0  # [0, inf]
    else:
        r_lift = 0.0

    # === Regularización ===
    r_smooth = -0.01 * np.sum((action_curr - action_prev) ** 2)
    r_torque = -0.001 * np.sum(torques ** 2)
    r_autocoll = -10.0 if has_autocollision else 0.0

    total = r_approach + r_closure + r_contact + r_lift + r_smooth + r_torque + r_autocoll

    return {
        'total': total,
        'r_approach': r_approach,
        'r_closure': r_closure,
        'r_contact': r_contact,
        'r_lift': r_lift,
        'r_smooth': r_smooth,
        'r_torque': r_torque,
        'r_autocoll': r_autocoll,
    }

# Test
r = compute_reward(
    palm_l_pos=np.array([0.4, 0.1, 0.2]),
    palm_r_pos=np.array([0.4, -0.1, 0.2]),
    box_pos=np.array([0.5, 0.0, 0.15]),
    touch_forces=np.array([0.5, 0.3, 0.4, 0.2, 0.6, 0.1, 0.5, 0.3, 0.4, 0.2, 0.6, 0.1]),
    q_fingers=np.zeros(14),
    q_fingers_closed=np.ones(14) * 0.5,
    action_curr=np.zeros(28),
    action_prev=np.zeros(28),
    torques=np.zeros(28),
    n_steps_in_contact=5,
    has_autocollision=False,
)
print("Test reward:", r)
assert isinstance(r['total'], float), "total debe ser float"
print("REWARD FUNCTION OK")
EOF
conda run -p envs/g1_udc python /tmp/test_reward.py
```
**Reportar:** Stdout completo del test. Valores numéricos de cada componente de reward en el caso de prueba. Justificación de los pesos elegidos.

---

### AGENTE-05 | DISEÑAR_CURRICULUM
**Tarea:** Crear `entrenamiento/configs/grasp_curriculum.yaml` con 4 stages:
```bash
cd /home/udc/Unitree_G1
mkdir -p entrenamiento/configs
cat > entrenamiento/configs/grasp_curriculum.yaml << 'EOF'
# Curriculum progresivo para política de agarre G1 EDU
# Stage 1: caja fija (0-5000 iter) - aprender a aproximar palmas
# Stage 2: posición X variable (5000-15000) - aprender profundidad
# Stage 3: XY + orientación (15000-30000) - full 2D + yaw
# Stage 4: full DR (30000-50000) - generalización completa

curriculum:
  stage_1:
    iterations: [0, 5000]
    description: "Caja fija justo enfrente, aprender aproximación"
    box_pos_range:
      x: [0.50, 0.50]
      y: [0.00, 0.00]
      z: [0.15, 0.15]
    box_orient_range:
      yaw_deg: [0.0, 0.0]
    reward_weights:
      approach: 3.0
      closure: 1.0
      contact: 0.5
      lift: 0.0
    success_threshold:
      n_contacts_min: 2

  stage_2:
    iterations: [5000, 15000]
    description: "Posición X variable, orientación pequeña"
    box_pos_range:
      x: [0.40, 0.65]
      y: [0.00, 0.00]
      z: [0.15, 0.15]
    box_orient_range:
      yaw_deg: [-15.0, 15.0]
    reward_weights:
      approach: 2.0
      closure: 2.0
      contact: 1.5
      lift: 0.5
    success_threshold:
      n_contacts_min: 3

  stage_3:
    iterations: [15000, 30000]
    description: "Posición XY + orientación media, altura variable"
    box_pos_range:
      x: [0.40, 0.70]
      y: [-0.20, 0.20]
      z: [0.10, 0.20]
    box_orient_range:
      yaw_deg: [-30.0, 30.0]
    reward_weights:
      approach: 1.0
      closure: 2.0
      contact: 3.0
      lift: 3.0
    success_threshold:
      n_contacts_min: 4
      box_lift_min: 0.03

  stage_4:
    iterations: [30000, 50000]
    description: "Full randomization, full DR"
    box_pos_range:
      x: [0.35, 0.75]
      y: [-0.25, 0.25]
      z: [0.08, 0.25]
    box_orient_range:
      yaw_deg: [-45.0, 45.0]
    reward_weights:
      approach: 1.0
      closure: 1.5
      contact: 3.0
      lift: 5.0
    success_threshold:
      n_contacts_min: 4
      box_lift_min: 0.05

domain_randomization:
  box_mass_range: [0.3, 3.0]
  box_friction_range: [0.4, 1.5]
  finger_kp_scale_range: [0.8, 1.2]
  finger_kd_scale_range: [0.8, 1.2]
  contact_sensor_noise_std: 0.1
  joint_pos_noise_std: 0.005
  joint_vel_noise_std: 0.02
  ctrl_delay_steps: [0, 2]

training:
  episode_length_steps: 300
  control_freq_hz: 50
  n_envs: 4096
EOF
echo "CURRICULUM YAML CREADO"
cat entrenamiento/configs/grasp_curriculum.yaml | head -5
```
**Reportar:** Archivo creado. Justificación de cada stage y los rangos de posición de la caja.

---

### AGENTE-06 | DISEÑAR_ARQUITECTURA_RED
**Tarea:** Crear `entrenamiento/configs/grasp_policy.yaml` con la arquitectura de la red neuronal:
```bash
cd /home/udc/Unitree_G1
mkdir -p entrenamiento/configs
cat > entrenamiento/configs/grasp_policy.yaml << 'EOF'
# Arquitectura de la política de agarre G1

# === DIMENSIONES DE OBSERVACIÓN ===
# pos_caja_relativa_torso (3) + orient_caja_quat (4)
# + q_brazos_izq (5) + q_brazos_der (5)
# + q_muneca_izq (2) + q_muneca_der (2) [incluidas en brazos del XML]
# + q_dedos_izq (7) + q_dedos_der (7)
# + dq_brazos_izq (5) + dq_brazos_der (5)
# + dq_muneca_izq (2) + dq_muneca_der (2)
# + dq_dedos_izq (7) + dq_dedos_der (7)
# + touch_izq (6) + touch_der (6)
# + accion_previa (28)
# TOTAL: 3+4 + 14+14 + 14+14 + 12 + 28 = 103 dims
# (se ajustará a dims exactas tras AGENTE-08)

obs:
  pos_caja_rel: 3
  orient_caja_quat: 4
  q_brazos_izq: 7       # 5 brazo + 2 muñeca
  q_brazos_der: 7
  q_dedos_izq: 7
  q_dedos_der: 7
  dq_brazos_izq: 7
  dq_brazos_der: 7
  dq_dedos_izq: 7
  dq_dedos_der: 7
  touch_izq: 6
  touch_der: 6
  accion_previa: 28
  total: 103  # VERIFICAR con AGENTE-08

actor:
  input_dim: 103
  hidden_dims: [512, 256, 128]
  activation: elu
  output_dim: 28
  output_activation: tanh
  action_scale: 0.5      # escala acciones relativas a posición default

critic:
  input_dim: 103
  hidden_dims: [512, 256, 128]
  activation: elu
  output_dim: 1

ppo:
  num_envs: 4096
  num_steps: 24
  learning_rate: 3.0e-4
  entropy_coef: 0.01
  clip_range: 0.2
  gamma: 0.99
  gae_lambda: 0.95
  max_grad_norm: 1.0
  num_epochs: 5
  minibatch_size: 1024
  total_iterations: 50000
  save_interval: 1000
  log_interval: 100

export:
  output_path: "politicas/model_grasp_jit.pt"
  input_dim: 103
  output_dim: 28
EOF
echo "POLICY YAML CREADO"
```
**Reportar:** Archivo creado. Estimación de parámetros totales de la red. Estimación de tiempo de entrenamiento en RTX 5090.

---

### AGENTE-07 | DISEÑAR_POSICION_CERRADO_DEDOS
**Tarea:** Calcular la configuración de los dedos para el agarre (posición "cerrado") basado en los rangos del XML:
```bash
cd /home/udc/Unitree_G1
conda run -p envs/g1_udc python -c "
import mujoco, numpy as np
m = mujoco.MjModel.from_xml_path('escenas/g1_manipulation_full.xml')

print('=== CONFIGURACION AGARRE DEDOS ===')
print('Formato: joint_name | rango | q_open | q_closed | descripcion')
print()

# Joints de dedos - extraer nombres y rangos
finger_joints = []
for i in range(m.njnt):
    name = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_JOINT, i)
    if name and ('thumb' in name or 'index' in name or 'middle' in name):
        lo, hi = m.jnt_range[i]
        # Para un agarre tipo 'power grip', usar 70% del rango
        q_open = lo + 0.1 * (hi - lo)   # casi abierto
        q_closed = lo + 0.7 * (hi - lo) # 70% cerrado
        finger_joints.append((name, lo, hi, q_open, q_closed))
        print(f'{name:45s} range=[{lo:.3f},{hi:.3f}] open={q_open:.3f} closed={q_closed:.3f}')

print()
print(f'Total finger joints: {len(finger_joints)}')
print()
# Configuración separada izq/der
izq = [j for j in finger_joints if 'left' in j[0]]
der = [j for j in finger_joints if 'right' in j[0]]
print(f'Izquierda: {len(izq)} joints')
print(f'Derecha: {len(der)} joints')
"
```
**Reportar:** Tabla completa de joints de dedos con configuración `q_open` y `q_closed`. Verificar que hay exactamente 7 por mano (14 total). Si no hay 14, reportar el número real y los nombres exactos.

---

### AGENTE-08 | VERIFICAR_DIMS_OBS_EXACTAS
**Tarea:** Calcular las dimensiones exactas del espacio de observación usando g1_constants.py:
```bash
cd /home/udc/Unitree_G1
conda run -p envs/g1_udc python -c "
import mujoco, numpy as np

# Importar constantes del Plan 01
import sys; sys.path.insert(0, '.')
try:
    from simulacion.g1_constants import (
        ARM_LEFT_ACT_IDS, ARM_RIGHT_ACT_IDS,
        FINGER_LEFT_ACT_IDS, FINGER_RIGHT_ACT_IDS,
        TOUCH_LEFT_IDS, TOUCH_RIGHT_IDS
    )
    print('g1_constants.py importado correctamente')
    print(f'  ARM_LEFT_ACT_IDS: {ARM_LEFT_ACT_IDS} (n={len(ARM_LEFT_ACT_IDS)})')
    print(f'  ARM_RIGHT_ACT_IDS: {ARM_RIGHT_ACT_IDS} (n={len(ARM_RIGHT_ACT_IDS)})')
    print(f'  FINGER_LEFT_ACT_IDS: {FINGER_LEFT_ACT_IDS} (n={len(FINGER_LEFT_ACT_IDS)})')
    print(f'  FINGER_RIGHT_ACT_IDS: {FINGER_RIGHT_ACT_IDS} (n={len(FINGER_RIGHT_ACT_IDS)})')
    print(f'  TOUCH_LEFT_IDS: {TOUCH_LEFT_IDS} (n={len(TOUCH_LEFT_IDS)})')
    print(f'  TOUCH_RIGHT_IDS: {TOUCH_RIGHT_IDS} (n={len(TOUCH_RIGHT_IDS)})')
except ImportError as e:
    print(f'ERROR: {e}')
    print('ACCION REQUERIDA: verificar que el Plan 01 creó g1_constants.py correctamente')

# Calcular dims del espacio de obs
n_arm_l = 7   # 5 brazo + 2 muñeca = ajustar según AGENTE-01
n_arm_r = 7
n_finger_l = 7
n_finger_r = 7
n_touch = 12  # 6 izq + 6 der = ajustar según AGENTE-02

# obs_grasp dims
dims = {
    'pos_caja_rel': 3,
    'orient_caja_quat': 4,
    'q_arm_l': n_arm_l,
    'q_arm_r': n_arm_r,
    'q_finger_l': n_finger_l,
    'q_finger_r': n_finger_r,
    'dq_arm_l': n_arm_l,
    'dq_arm_r': n_arm_r,
    'dq_finger_l': n_finger_l,
    'dq_finger_r': n_finger_r,
    'touch_l': 6,
    'touch_r': 6,
    'prev_action': 28,
}
total = sum(dims.values())
print()
print('=== DIMENSIONES OBS AGARRE ===')
for k, v in dims.items():
    print(f'  {k:20s}: {v}')
print(f'  TOTAL: {total}')
print()
print(f'Dimensiones de acción: {n_arm_l + n_arm_r + n_finger_l + n_finger_r} (verificar = 28)')
"
```
**Reportar:** Dimensiones exactas del espacio de observación. Si no coinciden con el YAML del AGENTE-06, reportar el valor correcto. La dimensión total del obs debe ser confirmada aquí.

---

## FASE 2 — Implementación (Agentes 9-14, EN PARALELO después de Fase 1)

### AGENTE-09 | IMPLEMENTAR_G1GRASPENV
**Tarea:** Implementar `entrenamiento/envs/g1_grasp_env.py` completo con todas las fases de reward:
```bash
mkdir -p /home/udc/Unitree_G1/entrenamiento/envs
```
El archivo debe implementar la clase `G1GraspEnv` con:
- `__init__(self, xml_path, curriculum_stage=1, randomize=True)`
- `reset(self)` → posición aleatoria de la caja según el stage actual del curriculum
- `step(self, action)` → aplicar acción, avanzar simulación, calcular reward
- `compute_reward(self, data)` → 4 fases: approach + closure + contact + lift + regularización
- `_get_obs(self, data)` → construir vector de observación con las dims confirmadas por AGENTE-08
- `_get_box_pos_relative(self, data)` → posición de la caja relativa al frame del torso
- `check_success(self, data)` → bool: n_contacts >= 4 Y box_z > 0.20m

**Debe usar:**
- Índices exactos de AGENTE-01 y AGENTE-02
- Configuración de dedos cerrados de AGENTE-07
- Dims de obs de AGENTE-08

**Reportar:** Archivo creado. Test de importación:
```bash
conda run -p envs/g1_udc python -c "from entrenamiento.envs.g1_grasp_env import G1GraspEnv; print('OK')"
```

---

### AGENTE-10 | IMPLEMENTAR_SIM_GRASP
**Tarea:** Implementar `simulacion/sim_grasp.py` para validación headless post-entrenamiento:
```bash
# El script debe:
# 1. Cargar g1_manipulation_scene.xml
# 2. Cargar la política (TorchScript JIT)
# 3. Correr N episodios headless
# 4. Reportar: tasa de éxito, altura máxima caja, fuerzas de contacto, tiempo hasta agarre
# 5. Imprimir tabla de resultados

# Uso:
# conda run -p /home/udc/Unitree_G1/envs/g1_udc python simulacion/sim_grasp.py \
#   --policy politicas/model_grasp_jit.pt --headless --episodes 10
```
**Reportar:** Archivo creado. Test de sintaxis:
```bash
conda run -p envs/g1_udc python -m py_compile simulacion/sim_grasp.py && echo "SIM_GRASP SYNTAX OK"
```

---

### AGENTE-11 | IMPLEMENTAR_TRAIN_GRASP
**Tarea:** Implementar `entrenamiento/train_grasp.py` que usa el entorno G1GraspEnv con PPO de HumanoidVerse:
```bash
# El script debe:
# --config: ruta al yaml de configuración
# --stage: 1, 2, 3 o 4
# --max_iter: número de iteraciones
# --log_dir: directorio de logs
# --resume: checkpoint para continuar entrenamiento (opcional)

# Estructura mínima:
# 1. Parsear args
# 2. Cargar config YAML
# 3. Inicializar G1GraspEnv vectorizado (4096 envs)
# 4. Inicializar PPO trainer (HumanoidVerse o similar)
# 5. Loop de entrenamiento con log cada 100 iter
# 6. Guardar checkpoint cada 1000 iter
# 7. Imprimir reward medio, tasa de éxito, altura máxima
```
**Reportar:** Archivo creado. Test de importación:
```bash
conda run -n hgen python -m py_compile entrenamiento/train_grasp.py && echo "TRAIN_GRASP SYNTAX OK"
```

---

### AGENTE-12 | IMPLEMENTAR_EXPORT_POLITICA
**Tarea:** Verificar que `entrenamiento/export_politica.py` existe y funciona para exportar la política de agarre:
```bash
cd /home/udc/Unitree_G1
conda run -p envs/g1_udc python -c "
import os
# Verificar si existe export_politica.py
if os.path.exists('entrenamiento/export_politica.py'):
    print('export_politica.py EXISTE')
    with open('entrenamiento/export_politica.py') as f:
        print(f.read()[:500])
else:
    print('CREAR entrenamiento/export_politica.py')
"
```
Si no existe, crear `entrenamiento/export_politica.py`:
```python
# Script genérico para exportar cualquier política a TorchScript JIT
# Uso: conda run -n hgen python entrenamiento/export_politica.py <input.pt> <output_jit.pt> <obs_dim> <act_dim>
import sys, torch

def export(input_path, output_path, obs_dim, act_dim):
    model = torch.load(input_path, map_location='cpu')
    # Intentar extraer el actor
    if hasattr(model, 'actor'):
        actor = model.actor
    else:
        actor = model
    actor.eval()
    dummy = torch.zeros(1, obs_dim)
    jit_model = torch.jit.trace(actor, dummy)
    out = jit_model(dummy)
    assert out.shape == (1, act_dim), f"Output shape {out.shape} != (1, {act_dim})"
    torch.jit.save(jit_model, output_path)
    print(f"Exportado: {output_path}")
    print(f"  Input: ({obs_dim},) -> Output: ({act_dim},)")
    print(f"  Output range: [{out.min():.3f}, {out.max():.3f}]")

if __name__ == '__main__':
    export(sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
```
**Reportar:** Archivo verificado o creado. Test de importación OK.

---

### AGENTE-13 | CREAR_GENESIS_WRAPPER
**Tarea:** Crear `entrenamiento/envs/g1_grasp_genesis_wrapper.py` que adapta G1GraspEnv a la API vectorizada de Genesis/HumanoidVerse:
```bash
# El wrapper debe:
# - Inicializar N instancias de G1GraspEnv en paralelo (usando torch para vectorización)
# - Implementar reset_batch(), step_batch()
# - Calcular rewards de forma vectorizada
# - Compatible con el PPO trainer de HumanoidVerse
# NOTA: Si Genesis no soporta MuJoCo directamente, usar multiprocessing con N workers
```
**Reportar:** Archivo creado. Test básico con 4 envs en paralelo.

---

### AGENTE-14 | VERIFICAR_INTEGRACION_COMPLETA_PRE_ENTRENAMIENTO
**Tarea:** Verificar que todos los componentes de la Fase 2 se integran correctamente antes de entrenar:
```bash
cd /home/udc/Unitree_G1
conda run -p envs/g1_udc python -c "
import sys; sys.path.insert(0, '.')
from entrenamiento.envs.g1_grasp_env import G1GraspEnv
import numpy as np

# Test básico de 1 episodio
env = G1GraspEnv('escenas/g1_manipulation_scene.xml', curriculum_stage=1)
obs = env.reset()
print(f'reset() obs shape: {obs.shape}')
assert obs.ndim == 1, 'obs debe ser 1D'

for step in range(10):
    action = np.random.uniform(-0.1, 0.1, 28)
    obs, reward, done, info = env.step(action)
    if step == 0:
        print(f'step() obs shape: {obs.shape}, reward: {reward:.4f}')
        print(f'  info keys: {list(info.keys())}')

print('INTEGRACION PRE-ENTRENAMIENTO OK')
print(f'obs_dim={obs.shape[0]}, act_dim=28')
"
```
**Reportar:** Stdout completo. Si hay errores, reportarlos con traceback completo. Confirmar obs_dim exacta.

---

## FASE 3 — Entrenamiento Curriculum (Agentes 15-22, SECUENCIAL)

### AGENTE-15 | ENTRENAR_STAGE1_0_5000
**Tarea:** Ejecutar Stage 1 del curriculum (0-5000 iteraciones, caja fija):
```bash
cd /home/udc/Unitree_G1
conda run -n hgen python entrenamiento/train_grasp.py \
  --config entrenamiento/configs/grasp_policy.yaml \
  --curriculum entrenamiento/configs/grasp_curriculum.yaml \
  --stage 1 \
  --max_iter 5000 \
  --log_dir entrenamiento/logs/grasp/stage1
```
**Ejecutar SOLO cuando Agentes 09-14 hayan completado con éxito.**  
**Reportar:** Stdout completo. Reward medio a las iteraciones: 500, 1000, 2000, 3000, 4000, 5000. Si falla, traceback completo.

---

### AGENTE-16 | ANALIZAR_CONVERGENCIA_STAGE1
**Tarea:** Analizar los logs del Stage 1 y verificar convergencia:
```bash
cd /home/udc/Unitree_G1
conda run -n hgen python -c "
import os, json, numpy as np
log_dir = 'entrenamiento/logs/grasp/stage1'
# Leer logs y analizar
log_files = sorted([f for f in os.listdir(log_dir) if f.endswith('.json') or f.endswith('.txt')])
print(f'Archivos de log encontrados: {log_files}')
# Extraer métricas de reward
# ...imprimir tabla de iter vs reward vs tasa_exito
"
```
**Criterio de éxito Stage 1:** Reward medio al final > -0.5 (palmas están cerca de la caja).  
Si no converge, reportar con análisis de causa y sugerir ajuste de hiperparámetros.  
**Reportar:** Tabla de métricas, gráfica ASCII de la curva de reward, veredicto de convergencia.

---

### AGENTE-17 | VALIDAR_STAGE1_MUJOCO
**Tarea:** Validar la política Stage 1 en MuJoCo headless (10 episodios):
```bash
cd /home/udc/Unitree_G1
conda run -p envs/g1_udc python simulacion/sim_grasp.py \
  --policy entrenamiento/logs/grasp/stage1/model_5000.pt \
  --headless --episodes 10
```
**Métricas a registrar por episodio:** ¿alcanzaron las palmas la caja (< 15cm)? Reward medio. Altura máxima de la caja.  
**Reportar:** Tabla de 10 episodios con métricas. Veredicto: ¿Stage 1 OK para continuar con Stage 2?

---

### AGENTE-18 | ENTRENAR_STAGE2_5000_15000
**Tarea:** Continuar entrenamiento Stage 2 (5000-15000 iter, posición X variable):
```bash
cd /home/udc/Unitree_G1
conda run -n hgen python entrenamiento/train_grasp.py \
  --config entrenamiento/configs/grasp_policy.yaml \
  --curriculum entrenamiento/configs/grasp_curriculum.yaml \
  --stage 2 \
  --resume entrenamiento/logs/grasp/stage1/model_5000.pt \
  --max_iter 15000 \
  --log_dir entrenamiento/logs/grasp/stage2
```
**Ejecutar SOLO cuando AGENTE-17 haya aprobado Stage 1.**  
**Reportar:** Reward a iteraciones: 6000, 8000, 10000, 12000, 15000. Tasa de éxito de cierre de dedos (% episodios con ≥3 contactos).

---

### AGENTE-19 | ANALIZAR_Y_VALIDAR_STAGE2
**Tarea:** Analizar convergencia Stage 2 y validar en MuJoCo (10 episodios):
```bash
cd /home/udc/Unitree_G1
conda run -p envs/g1_udc python simulacion/sim_grasp.py \
  --policy entrenamiento/logs/grasp/stage2/model_15000.pt \
  --headless --episodes 10
```
**Criterio de éxito Stage 2:** ≥ 50% de episodios con 3+ contactos.  
**Reportar:** Tabla de 10 episodios, veredicto, comparativa Stage1 vs Stage2.

---

### AGENTE-20 | ENTRENAR_STAGE3_15000_30000
**Tarea:** Stage 3 (15000-30000 iter, XY completo + orientación):
```bash
cd /home/udc/Unitree_G1
conda run -n hgen python entrenamiento/train_grasp.py \
  --config entrenamiento/configs/grasp_policy.yaml \
  --curriculum entrenamiento/configs/grasp_curriculum.yaml \
  --stage 3 \
  --resume entrenamiento/logs/grasp/stage2/model_15000.pt \
  --max_iter 30000 \
  --log_dir entrenamiento/logs/grasp/stage3
```
**Ejecutar SOLO cuando AGENTE-19 haya aprobado Stage 2.**  
**Reportar:** Reward cada 2000 iter (de 15000 a 30000). Tasa de elevación (% episodios con box_z > 0.18m).

---

### AGENTE-21 | ANALIZAR_Y_VALIDAR_STAGE3
**Tarea:** Analizar convergencia Stage 3 y validar en MuJoCo (15 episodios):
```bash
cd /home/udc/Unitree_G1
conda run -p envs/g1_udc python simulacion/sim_grasp.py \
  --policy entrenamiento/logs/grasp/stage3/model_30000.pt \
  --headless --episodes 15
```
**Criterio Stage 3:** ≥ 50% de episodios con caja elevada > 5cm (box_z > 0.20m).  
**Reportar:** Tabla de 15 episodios con alturas máximas, veredicto.

---

### AGENTE-22 | ENTRENAR_STAGE4_30000_50000
**Tarea:** Stage 4 — full DR, 30000-50000 iteraciones:
```bash
cd /home/udc/Unitree_G1
conda run -n hgen python entrenamiento/train_grasp.py \
  --config entrenamiento/configs/grasp_policy.yaml \
  --curriculum entrenamiento/configs/grasp_curriculum.yaml \
  --stage 4 \
  --resume entrenamiento/logs/grasp/stage3/model_30000.pt \
  --max_iter 50000 \
  --log_dir entrenamiento/logs/grasp/stage4
```
**Ejecutar SOLO cuando AGENTE-21 haya aprobado Stage 3.**  
**Reportar:** Reward y tasa de éxito cada 2000 iter (de 30000 a 50000). Checkpoint del mejor modelo (mayor tasa de elevación).

---

## FASE 4 — Validación Extendida (Agentes 23-27, EN PARALELO después de Stage 4)

### AGENTE-23 | VALIDAR_20_POSICIONES_ALEATORIAS
**Tarea:** 20 episodios headless con posiciones completamente aleatorias:
```bash
cd /home/udc/Unitree_G1
conda run -p envs/g1_udc python simulacion/sim_grasp.py \
  --policy entrenamiento/logs/grasp/stage4/model_best.pt \
  --headless --episodes 20 --random_pos
```
**Métricas por episodio:** posición inicial de caja, ¿contacto ≥4?, ¿elevó ≥5cm?, altura máxima, tiempo hasta agarre.  
**Reportar:** Tabla de 20 episodios. Tasa de éxito final.

---

### AGENTE-24 | VALIDAR_3_MASAS_DISTINTAS
**Tarea:** Probar robustez con 3 masas de caja (10 episodios cada una):
```bash
# 10 episodios con caja 0.5kg
conda run -p envs/g1_udc python simulacion/sim_grasp.py \
  --policy entrenamiento/logs/grasp/stage4/model_best.pt \
  --headless --episodes 10 --box_mass 0.5

# 10 episodios con caja 1.5kg
conda run -p envs/g1_udc python simulacion/sim_grasp.py \
  --policy entrenamiento/logs/grasp/stage4/model_best.pt \
  --headless --episodes 10 --box_mass 1.5

# 10 episodios con caja 2.5kg
conda run -p envs/g1_udc python simulacion/sim_grasp.py \
  --policy entrenamiento/logs/grasp/stage4/model_best.pt \
  --headless --episodes 10 --box_mass 2.5
```
**Reportar:** Tabla comparativa: masa | tasa_éxito | fuerza_contacto_media | altura_máxima.

---

### AGENTE-25 | VALIDAR_4_ORIENTACIONES
**Tarea:** Validar con 4 orientaciones de la caja (10 episodios cada una):
- 0°: caja alineada con el robot
- 15°: rotada 15° yaw
- 30°: rotada 30° yaw
- 45°: rotada 45° yaw
```bash
for yaw in 0 15 30 45; do
  conda run -p envs/g1_udc python simulacion/sim_grasp.py \
    --policy entrenamiento/logs/grasp/stage4/model_best.pt \
    --headless --episodes 10 --box_yaw $yaw
done
```
**Reportar:** Tabla: orientación | tasa_éxito | comportamiento_observado.

---

### AGENTE-26 | ANALIZAR_CALIDAD_AGARRE
**Tarea:** Analizar la calidad del agarre: distribución de fuerzas de contacto y simetría izq/der:
```bash
cd /home/udc/Unitree_G1
conda run -p envs/g1_udc python -c "
import mujoco, numpy as np, sys
sys.path.insert(0, '.')
from entrenamiento.envs.g1_grasp_env import G1GraspEnv

env = G1GraspEnv('escenas/g1_manipulation_scene.xml', curriculum_stage=4)
# Cargar política y correr 5 episodios completos registrando fuerzas de contacto
# Calcular:
# 1. Distribución de fuerzas izq vs der (¿simétrico?)
# 2. Qué dedos contribuyen más al agarre
# 3. ¿Hay algún dedo con contacto 0 consistentemente?
# 4. Fuerza total media vs tiempo
print('Analizando calidad del agarre...')
"
```
**Reportar:** Distribución de fuerzas por dedo (tabla). Análisis de simetría. ¿Hay dedos que no participan?

---

### AGENTE-27 | VALIDAR_RESISTENCIA_PERTURBACIONES
**Tarea:** Verificar si el agarre resiste perturbaciones externas (golpe a la caja):
```bash
cd /home/udc/Unitree_G1
conda run -p envs/g1_udc python -c "
import mujoco, numpy as np, torch, sys
sys.path.insert(0, '.')

# Script: 5 episodios donde:
# 1. Robot agarra la caja con éxito
# 2. A los 100 pasos, aplicar xfrc_applied[box_id] = [0, 0, -5, 0, 0, 0] (fuerza hacia abajo 5N)
# 3. Registrar si mantiene el agarre (touch_forces siguen > 0.1N)
print('Test de resistencia a perturbaciones...')
# Implementar el test completo
"
```
**Reportar:** ¿Cuántos de 5 episodios mantienen el agarre bajo perturbación? Fuerza máxima resistida.

---

## FASE 5 — Export y Reporte (Agentes 28-30)

### AGENTE-28 | EXPORTAR_POLITICA_AGARRE
**Tarea:** Exportar el mejor checkpoint a TorchScript JIT:
```bash
cd /home/udc/Unitree_G1
# Verificar qué checkpoint es el mejor (mayor tasa de éxito)
ls -la entrenamiento/logs/grasp/stage4/
# Exportar
conda run -n hgen python entrenamiento/export_politica.py \
  entrenamiento/logs/grasp/stage4/model_best.pt \
  politicas/model_grasp_jit.pt \
  <OBS_DIM_CONFIRMADO_POR_AGENTE08> \
  28
# Verificar
conda run -p envs/g1_udc python -c "
import torch
m = torch.jit.load('politicas/model_grasp_jit.pt')
m.eval()
import numpy as np
obs_dim = <OBS_DIM_CONFIRMADO>
dummy = torch.zeros(1, obs_dim)
out = m(dummy)
print(f'Input: ({obs_dim},) -> Output: {out.shape}')
print(f'Output range: [{out.min():.3f}, {out.max():.3f}]')
import os
size_kb = os.path.getsize('politicas/model_grasp_jit.pt') / 1024
print(f'Tamaño: {size_kb:.1f} KB')
assert out.shape == (1, 28), f'ERROR: shape incorrecto {out.shape}'
print('EXPORTACION OK')
"
```
**Reportar:** Stdout completo. Confirmar input_dim, output_dim, tamaño del archivo.

---

### AGENTE-29 | CREAR_G1_GRASP_CONSTANTS
**Tarea:** Actualizar `simulacion/g1_constants.py` con los índices específicos del agarre:
```bash
cd /home/udc/Unitree_G1
# Añadir al final de simulacion/g1_constants.py:
cat >> simulacion/g1_constants.py << 'EOF'

# ============================================================
# INDICES POLÍTICA DE AGARRE (añadidos en Plan 02)
# ============================================================

# Índices de actuadores para brazos (verificados por AGENTE-01 del Plan 02)
ARM_LEFT_JOINT_IDS = []   # LLENAR con valores reales de AGENTE-01
ARM_RIGHT_JOINT_IDS = []  # LLENAR con valores reales de AGENTE-01
FINGER_LEFT_JOINT_IDS = []  # LLENAR
FINGER_RIGHT_JOINT_IDS = []  # LLENAR

# Configuración de dedos para agarre tipo power grip
# (calculada por AGENTE-07 del Plan 02)
FINGER_LEFT_OPEN = []    # LLENAR con valores de AGENTE-07
FINGER_LEFT_CLOSED = []  # LLENAR con valores de AGENTE-07
FINGER_RIGHT_OPEN = []   # LLENAR con valores de AGENTE-07
FINGER_RIGHT_CLOSED = [] # LLENAR con valores de AGENTE-07

# Dimensiones del espacio de observación de la política de agarre
GRASP_OBS_DIM = 103  # AJUSTAR según AGENTE-08
GRASP_ACT_DIM = 28
EOF
echo "g1_constants.py actualizado"
```
**IMPORTANTE:** Reemplazar todos los `[]` con los valores reales obtenidos por AGENTE-01 y AGENTE-07.  
**Reportar:** Contenido final de la sección añadida a g1_constants.py con todos los valores reales.

---

### AGENTE-30 | REPORTE_FINAL_Y_COMMIT
**Tarea:** Generar el reporte completo del Plan 02 y hacer el commit:

Crear `/home/udc/Unitree_G1/reportes/reporte_plan02_agarre_<FECHA>.md` con:
```
# Reporte Plan 02 — Política de Agarre Estático G1
## Fecha y duración total del entrenamiento
## Resumen ejecutivo
## Resultado de cada agente (01-30):
   - Comando exacto ejecutado
   - Stdout/stderr completo (sin truncar)
   - Errores encontrados y soluciones
## Dimensiones confirmadas: obs_dim=X, act_dim=28
## Arquitectura final de la red (capas, activaciones, parámetros)
## Curvas de entrenamiento por stage (tabla iter | reward_medio | tasa_exito):
   Stage 1 (0-5000): ...
   Stage 2 (5000-15000): ...
   Stage 3 (15000-30000): ...
   Stage 4 (30000-50000): ...
## Tabla de validación extendida:
   | Escenario | Episodios | Tasa éxito | Altura máx | Contactos medios |
   | Posiciones aleatorias | 20 | X% | Xm | X |
   | Masa 0.5kg | 10 | X% | Xm | X |
   | Masa 1.5kg | 10 | X% | Xm | X |
   | Masa 2.5kg | 10 | X% | Xm | X |
   | Orientación 0° | 10 | X% | Xm | X |
   | Orientación 15° | 10 | X% | Xm | X |
   | Orientación 30° | 10 | X% | Xm | X |
   | Orientación 45° | 10 | X% | Xm | X |
## Análisis de calidad del agarre (distribución fuerzas por dedo)
## Análisis de resistencia a perturbaciones
## Política exportada: politicas/model_grasp_jit.pt
   - Input: (obs_dim,) → Output: (28,) en [-1, 1]
   - Tamaño: X KB
## Problemas encontrados y soluciones
## Próximos pasos (Plan 03)
```

Luego ejecutar:
```bash
cd /home/udc/Unitree_G1
git add politicas/model_grasp_jit.pt
git add entrenamiento/envs/g1_grasp_env.py
git add entrenamiento/envs/g1_grasp_genesis_wrapper.py
git add entrenamiento/configs/grasp_policy.yaml
git add entrenamiento/configs/grasp_curriculum.yaml
git add entrenamiento/train_grasp.py
git add simulacion/sim_grasp.py
git add simulacion/g1_constants.py
git add reportes/reporte_plan02_agarre_*.md
git commit -m "$(cat <<'EOF'
feat: politica agarre estatico G1 50000 iter curriculum 4-stages

30 sub-agentes: analisis joints, reward 4 fases, curriculum DR,
entrenamiento stage1-4, validacion 100+ episodios, export JIT.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```
**Reportar:** Reporte completo creado. Hash del commit.
