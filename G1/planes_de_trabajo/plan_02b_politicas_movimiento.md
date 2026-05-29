# Plan 02b — Políticas de Movimiento Simple G1 (29 DOF sin manos dextrales)

**Proyecto:** Unitree G1 — Universidad de Colombia  
**Fecha:** 2026-05-15  
**Modelo:** G1 29-DOF (`g1_29dof`) — sin manos dextrales  
**Framework:** HumanoidVerse + Genesis (4096 envs paralelos)  
**Objetivo:** Entrenar 4 políticas de movimiento simple: saludar, agacharse, estirar brazos, mover muñecas  
**Subagentes:** 30  

---

## Contexto Técnico

### DOF del G1 29-DOF

**Lower body (12 DOF — piernas):**
```
left_hip_pitch, left_hip_roll, left_hip_yaw, left_knee, left_ankle_pitch, left_ankle_roll
right_hip_pitch, right_hip_roll, right_hip_yaw, right_knee, right_ankle_pitch, right_ankle_roll
```

**Upper body (17 DOF — cintura + brazos):**
```
waist_yaw, waist_roll, waist_pitch                                          (índices 12-14)
left_shoulder_pitch, left_shoulder_roll, left_shoulder_yaw, left_elbow     (índices 15-18)
left_wrist_roll, left_wrist_pitch, left_wrist_yaw                          (índices 19-21)
right_shoulder_pitch, right_shoulder_roll, right_shoulder_yaw, right_elbow (índices 22-25)
right_wrist_roll, right_wrist_pitch, right_wrist_yaw                       (índices 26-28)
```

**Pose default (action=0):** Piernas con leve flexión de rodilla (knee=0.3, hip=-0.1, ankle=-0.2). Cuerpo superior todo en 0.

### PD Gains (g1_29dof.yaml — ya calibrados)
- Cintura: kp=400, kd=5
- Shoulders: kp=90, kd=2
- Elbows: kp=60, kd=1
- Wrists: kp=4, kd=0.2
- Hips/Knees: kp=200, kd=5
- Ankles: kp=20, kd=0.5

### 4 Movimientos y sus Poses Objetivo

**MOV-0: SALUDAR** — brazo derecho sube y muñeca oscila
```yaml
pose_A:  # brazo levantado
  right_shoulder_pitch: -1.2   # hacia adelante-arriba
  right_shoulder_roll: -0.3    # alejado del cuerpo
  right_shoulder_yaw: 0.0
  right_elbow: 0.8             # codo doblado
  right_wrist_pitch: 0.5       # muñeca arriba
pose_B:  # oscilación de muñeca
  right_wrist_pitch: -0.5      # muñeca abajo
  # (pose_A en todo lo demás)
período: 1.0s  # oscila entre A y B
```

**MOV-1: AGACHARSE** — flexión de piernas
```yaml
pose_squat:
  left_hip_pitch: -0.5         # cadera adelante (delta sobre default -0.1)
  right_hip_pitch: -0.5
  left_knee: 0.8               # rodilla doblada (delta sobre default 0.3)
  right_knee: 0.8
  left_ankle_pitch: -0.1       # ajuste tobillo
  right_ankle_pitch: -0.1
  # Cuerpo superior: todo en 0
duración: 2.0s  # baja, mantiene 1s, sube
```

**MOV-2: ESTIRAR BRAZOS** — ambos brazos al frente
```yaml
pose_stretch:
  left_shoulder_pitch: -1.4    # brazos adelante
  right_shoulder_pitch: -1.4
  left_shoulder_roll: 0.1      # leve separación
  right_shoulder_roll: -0.1
  left_elbow: 0.0              # brazos rectos
  right_elbow: 0.0
  # Cintura: todo en 0
duración: 1.5s  # extiende y mantiene
```

**MOV-3: MOVER MUÑECAS** — rotación y flexión de muñecas
```yaml
pose_wrists_A:
  left_shoulder_pitch: -0.6    # brazos al frente (posición intermedia)
  right_shoulder_pitch: -0.6
  left_elbow: 0.5
  right_elbow: 0.5
  left_wrist_roll: 1.0         # rotación muñeca
  right_wrist_roll: -1.0
  left_wrist_pitch: 0.4
  right_wrist_pitch: 0.4
pose_wrists_B:
  left_wrist_roll: -1.0
  right_wrist_roll: 1.0
  left_wrist_pitch: -0.4
  right_wrist_pitch: -0.4
período: 1.2s
```

### Arquitectura de Cada Política

- **obs_dim = 62**: q_actual(29) + q_target(29) + phase_signal(1) + projected_gravity(3)
- **act_dim = 29**: todos los DOF (policy aprende a mantener piernas estables)
- **reward**: `0.8 * exp(-3 * ||q_upper - q_target_upper||) + 0.2 * exp(-1 * ||q_lower - q_default_lower||) - 0.01 * ||action||²`
- **4 políticas separadas**, una por movimiento
- **Entrenamiento**: 5000 iteraciones por movimiento, 4096 envs, ~30 min por política

### Criterios de Aprobación por Movimiento

| Movimiento | Criterio éxito por episodio | Mínimo aprobación |
|---|---|---|
| Saludar | right_shoulder_pitch < -0.8 rad Y wrist_pitch oscila >0.3 rad | ≥16/20 episodios |
| Agacharse | left_knee_delta > 0.5 rad Y pelvis_z baja >3 cm | ≥16/20 episodios |
| Estirar brazos | ambos shoulder_pitch < -1.0 rad simultáneamente | ≥16/20 episodios |
| Mover muñecas | wrist_roll_range > 1.0 rad (max-min en episodio) | ≥16/20 episodios |

---

## Fase 1: Análisis (5 Agentes)

### AGENTE-01 — Verificar límites articulares upper body
**Tarea:** Leer `entrenamiento/humanoidverse/config/robot/g1/g1_29dof.yaml`. Extraer `dof_pos_lower_limit_list` y `dof_pos_upper_limit_list` para los 17 DOF del cuerpo superior (índices 12-28). Verificar que las poses objetivo de los 4 movimientos están dentro de los límites. Si alguna pose viola un límite, ajustarla al 90% del rango disponible. Reportar tabla con: joint_name | lower_lim | target_val | upper_lim | dentro_rango.

**Archivo a leer:** `entrenamiento/humanoidverse/config/robot/g1/g1_29dof.yaml`  
**Output:** Tabla de verificación + poses ajustadas si es necesario

---

### AGENTE-02 — Verificar límites articulares lower body para AGACHARSE
**Tarea:** Para MOV-1 (agacharse), extraer límites de los 12 DOF de piernas. Verificar que las poses objetivo (hip_pitch_delta=-0.5, knee_delta=0.8, ankle_delta=-0.1) más los valores default (-0.1, 0.3, -0.2) están dentro de los límites. Calcular también si la postura resultante mantiene el centro de masa proyectado dentro del polígono de soporte (x entre -0.1 y 0.1 m). Ajustar si es necesario.

**Archivo a leer:** `entrenamiento/humanoidverse/config/robot/g1/g1_29dof.yaml`  
**Output:** Validación de poses de agacharse + ajustes

---

### AGENTE-03 — Analizar estructura del env de locomoción existente
**Tarea:** Leer `entrenamiento/humanoidverse/envs/locomotion/` (el directorio completo). Identificar: (1) qué métodos de `LeggedRobotLocomotion` necesitamos sobrescribir para el motion env, (2) cómo se calcula `projected_gravity` (para incluirlo en obs), (3) cómo se implementa `phase_signal` si existe (para movimientos periódicos como saludar y muñecas), (4) cómo se manejan los resets.

**Archivos a leer:** `entrenamiento/humanoidverse/envs/locomotion/*.py` y `entrenamiento/humanoidverse/envs/legged_base_task/*.py`  
**Output:** Lista de métodos a sobrescribir + snippets de código relevantes

---

### AGENTE-04 — Analizar train_agent.py y configuración Hydra
**Tarea:** Leer `entrenamiento/humanoidverse/train_agent.py` (o el script de entrenamiento principal). Identificar cómo se especifica el experimento via Hydra (`exp=locomotion` → `exp=motion`). Documentar el comando exacto para lanzar el entrenamiento del motion env con 4096 envs. Verificar que el PPO agent en `agents/ppo/` es compatible sin cambios.

**Archivos a leer:** Script de entrenamiento principal + `entrenamiento/humanoidverse/config/base.yaml`  
**Output:** Comando de entrenamiento exacto para cada movimiento

---

### AGENTE-05 — Calcular obs_dim exacto y verificar compatibilidad con g1_29dof
**Tarea:** Verificar que obs_dim=62 es correcto: q_actual(29) + q_target(29) + phase_signal(1) + projected_gravity(3) = 62. Leer el config de obs de locomoción existente para entender cómo se estructura el obs dict en HumanoidVerse. Diseñar el `obs/motion/motion_obs.yaml` mínimo necesario. Verificar que act_dim=29 es el valor correcto para g1_29dof (igual al número de joints controlables).

**Archivos a leer:** `entrenamiento/humanoidverse/config/obs/` + `entrenamiento/humanoidverse/config/robot/g1/g1_29dof.yaml`  
**Output:** obs_dim confirmado + estructura del obs dict

---

## Fase 2: Implementación (9 Agentes)

### AGENTE-06 — Crear motion_poses.yaml (keyframes de los 4 movimientos)
**Tarea:** Crear `entrenamiento/humanoidverse/config/motions/motion_poses.yaml` con las poses objetivo de los 4 movimientos (usando los valores verificados/ajustados por AGENTE-01 y AGENTE-02). Formato: dict con claves `saludar`, `agacharse`, `estirar_brazos`, `mover_muñecas`. Cada uno con `pose_A`, `pose_B` (para movimientos periódicos), `period_s`, y `motion_id` (0,1,2,3).

**Output:** `entrenamiento/humanoidverse/config/motions/motion_poses.yaml` (CREAR)

---

### AGENTE-07 — Crear motion_obs.yaml
**Tarea:** Crear `entrenamiento/humanoidverse/config/obs/motion/motion_obs.yaml`. El obs dict debe incluir:
- `q_actual`: dof_pos (29 dims, scale=1.0)
- `q_target`: target pose actual según phase (29 dims, scale=1.0)
- `phase_signal`: seno del phase actual (1 dim, scale=1.0)
- `projected_gravity`: vector gravedad en frame del pelvis (3 dims, scale=1.0)
Total: 62 dims. Seguir el formato exacto de `entrenamiento/humanoidverse/config/obs/loco/` como referencia.

**Archivos a leer:** `entrenamiento/humanoidverse/config/obs/loco/*.yaml` (referencia de formato)  
**Output:** `entrenamiento/humanoidverse/config/obs/motion/motion_obs.yaml` (CREAR)

---

### AGENTE-08 — Crear motion_rewards.yaml
**Tarea:** Crear `entrenamiento/humanoidverse/config/rewards/motion/motion_rewards.yaml` con:
```yaml
scales:
  pose_tracking: 0.8       # exp(-3 * ||q_upper - q_target_upper||)
  leg_stability: 0.2       # exp(-1 * ||q_lower - q_default_lower||)
  action_smoothness: -0.01 # -||a_t - a_{t-1}||²
  alive_bonus: 0.1         # +0.1 por step sin caer
  fall_penalty: -10.0      # -10 si pelvis_z < 0.5
```
Seguir formato de `entrenamiento/humanoidverse/config/rewards/loco/` como referencia.

**Archivos a leer:** `entrenamiento/humanoidverse/config/rewards/loco/*.yaml`  
**Output:** `entrenamiento/humanoidverse/config/rewards/motion/motion_rewards.yaml` (CREAR)

---

### AGENTE-09 — Crear env/motion.yaml
**Tarea:** Crear `entrenamiento/humanoidverse/config/env/motion.yaml`. Debe especificar:
- `env_class`: `MotionEnv` (a implementar)
- `robot`: `g1/g1_29dof`
- `num_envs`: 4096
- `episode_length_s`: 6.0 (6 segundos = ~3 ciclos de movimiento)
- `simulator`: genesis
- `obs`: `motion/motion_obs`
- `rewards`: `motion/motion_rewards`
- `motion_id`: configurable (0=saludar, 1=agacharse, 2=estirar, 3=muñecas)
Seguir formato de `entrenamiento/humanoidverse/config/env/locomotion.yaml`.

**Archivos a leer:** `entrenamiento/humanoidverse/config/env/locomotion.yaml`  
**Output:** `entrenamiento/humanoidverse/config/env/motion.yaml` (CREAR)

---

### AGENTE-10 — Crear exp/motion.yaml
**Tarea:** Crear `entrenamiento/humanoidverse/config/exp/motion.yaml`. Debe combinar:
- `defaults: [algo: ppo, env: motion]`
- PPO overrides: `lr=3e-4`, `num_mini_batches=4`, `num_epochs=5`, `clip_param=0.2`
- Logging: `exp_name=motion_${motion_name}`
Seguir formato de `entrenamiento/humanoidverse/config/exp/locomotion.yaml`.

**Archivos a leer:** `entrenamiento/humanoidverse/config/exp/locomotion.yaml`  
**Output:** `entrenamiento/humanoidverse/config/exp/motion.yaml` (CREAR)

---

### AGENTE-11 — Implementar MotionEnv (envs/motion/motion_env.py)
**Tarea:** Crear `entrenamiento/humanoidverse/envs/motion/motion_env.py` que extiende `LeggedRobotBase`. Métodos a implementar:

```python
class MotionEnv(LeggedRobotBase):
    def _init_motion_poses(self):
        # Carga motion_poses.yaml, convierte poses a tensores (n_envs, 29)
        # q_target_A y q_target_B para movimientos periódicos
        
    def _compute_phase(self):
        # phase = 2π * (episode_step * dt) / period_s
        # phase_signal = sin(phase)  → obs
        
    def _get_current_target(self):
        # Para movimientos periódicos: interpola entre pose_A y pose_B según phase
        # Para movimientos no periódicos (agacharse): secuencia temporal fija
        # Retorna q_target (n_envs, 29)
        
    def compute_observations(self):
        # obs = [q_actual, q_target, phase_signal, projected_gravity]
        
    def compute_rewards(self):
        # pose_tracking: compara q_upper con q_target_upper
        # leg_stability: compara q_lower con q_default_lower
        # action_smoothness: ||a_t - a_{t-1}||²
        # alive_bonus + fall_penalty
        
    def check_termination(self):
        # Terminar si pelvis_z < 0.5 (caída)
```

**Archivos a leer:** `entrenamiento/humanoidverse/envs/legged_base_task/*.py` (clase base)  
**Crear también:** `entrenamiento/humanoidverse/envs/motion/__init__.py`  
**Output:** `entrenamiento/humanoidverse/envs/motion/motion_env.py` (CREAR)

---

### AGENTE-12 — Implementar genesis_motion.py (simulator backend)
**Tarea:** Crear `entrenamiento/humanoidverse/simulator/genesis/genesis_motion.py` que extiende el simulator de Genesis existente. La diferencia con locomotion: no hay terrain, no hay heightmap, solo robot en plano plano. Verificar que el robot carga correctamente con `g1_29dof.xml`. Agregar método `get_dof_pos()` y `get_projected_gravity()` si no existen en el base.

**Archivos a leer:** `entrenamiento/humanoidverse/simulator/genesis/` (todos los archivos)  
**Output:** `entrenamiento/humanoidverse/simulator/genesis/genesis_motion.py` (CREAR)

---

### AGENTE-13 — Test de integración: verificar env carga correctamente
**Tarea:** Correr un test headless de 10 steps con el MotionEnv para MOV-0 (saludar):
```bash
conda run -n hgen python -c "
from entrenamiento.humanoidverse.envs.motion.motion_env import MotionEnv
# Cargar config via Hydra
# Crear env con n_envs=4 (test pequeño)
# Verificar: obs.shape == (4, 62), act_space == (4, 29)
# Correr 10 steps, verificar no NaN, robot no cae
print('obs_dim:', obs.shape[1])
print('robot_z:', sim.get_base_pos()[:, 2].mean())
"
```
Si hay errores de import o shape, corregirlos en los archivos de AGENTE-11 y AGENTE-12 hasta que el test pase.

**Output:** Test pasando + correcciones aplicadas

---

### AGENTE-14 — Sanity check: 50 iteraciones PPO en modo test
**Tarea:** Correr 50 iteraciones de entrenamiento para MOV-0 con `n_envs=64` (modo test rápido) para verificar que:
1. PPO loss converge (no NaN)
2. Reward no diverge
3. Robot se mantiene de pie durante el entrenamiento
4. Checkpoint se guarda correctamente

```bash
conda run -n hgen python entrenamiento/humanoidverse/train_agent.py \
  exp=motion env.motion_id=0 env.num_envs=64 \
  training.max_iterations=50 \
  exp_name=motion_sanity_check
```

Si hay errores, corregirlos antes de pasar a la Fase 3.

**Output:** Log de 50 iters sin errores + reward final

---

## Fase 3: Entrenamiento (8 Agentes)

### AGENTE-15 — Entrenar MOV-0: SALUDAR (5000 iteraciones)
**Tarea:** Entrenar la política de saludo con 4096 envs:
```bash
conda run -n hgen python entrenamiento/humanoidverse/train_agent.py \
  exp=motion env.motion_id=0 env.num_envs=4096 \
  training.max_iterations=5000 \
  exp_name=motion_saludar \
  training.save_interval=1000
```
Monitorear reward cada 500 iters. El reward debe subir de ~0.2 a >0.6 para Stage 1 saludando.

**Checkpoint esperado:** `entrenamiento/humanoidverse/logs/motion_saludar/model_5000.pt`  
**Reward mínimo al final:** >0.5 (pose_tracking component)

---

### AGENTE-16 — Validación intermedia MOV-0: SALUDAR
**Tarea:** Cargar `model_5000.pt` del saludar y correr 5 episodios headless. Para cada episodio verificar:
- `right_shoulder_pitch` alcanza < -0.8 rad
- `right_wrist_pitch` oscila entre -0.4 y +0.4 rad
- Robot se mantiene de pie (pelvis_z > 0.6 m) durante todo el episodio

Si ≥3/5 episodios pasan, continuar. Si no, re-entrenar 2000 iters más (hasta 7000 total) antes de continuar.

**Output:** Tabla de 5 episodios + decisión continuar/re-entrenar

---

### AGENTE-17 — Entrenar MOV-1: AGACHARSE (5000 iteraciones)
**Tarea:** Entrenar la política de agacharse con 4096 envs:
```bash
conda run -n hgen python entrenamiento/humanoidverse/train_agent.py \
  exp=motion env.motion_id=1 env.num_envs=4096 \
  training.max_iterations=5000 \
  exp_name=motion_agacharse \
  training.save_interval=1000
```
Este movimiento es el más difícil porque involucra las piernas. El reward de leg_stability tiene que permanecer alto. Si el robot empieza a caerse (reward_alive cae), reducir `env.rewards.scales.pose_tracking` a 0.5.

**Checkpoint esperado:** `entrenamiento/humanoidverse/logs/motion_agacharse/model_5000.pt`  
**Reward mínimo:** >0.4

---

### AGENTE-18 — Validación intermedia MOV-1: AGACHARSE
**Tarea:** Cargar `model_5000.pt` del agacharse y correr 5 episodios headless. Verificar:
- `left_knee` sube >0.5 rad del default (es decir, knee_actual > 0.8 rad total)
- `pelvis_z` baja >2 cm respecto al inicio
- Robot se mantiene de pie (no cae)

Si ≥3/5 pasan, continuar. Si no, ajustar reward: aumentar `leg_stability` a 0.4 y re-entrenar.

**Output:** Tabla de 5 episodios + decisión

---

### AGENTE-19 — Entrenar MOV-2: ESTIRAR BRAZOS (5000 iteraciones)
**Tarea:** Entrenar la política de estirar brazos:
```bash
conda run -n hgen python entrenamiento/humanoidverse/train_agent.py \
  exp=motion env.motion_id=2 env.num_envs=4096 \
  training.max_iterations=5000 \
  exp_name=motion_estirar \
  training.save_interval=1000
```
Este es el movimiento más simple (solo brazos al frente). Reward debe converger rápido.

**Checkpoint esperado:** `entrenamiento/humanoidverse/logs/motion_estirar/model_5000.pt`  
**Reward mínimo:** >0.65

---

### AGENTE-20 — Validación intermedia MOV-2: ESTIRAR BRAZOS
**Tarea:** 5 episodios headless. Verificar:
- Ambos `shoulder_pitch` < -1.0 rad simultáneamente en ≥70% de los steps del episodio
- Cuerpo inferior estable (piernas en default ±0.1 rad)

**Output:** Tabla de 5 episodios + decisión

---

### AGENTE-21 — Entrenar MOV-3: MOVER MUÑECAS (5000 iteraciones)
**Tarea:** Entrenar la política de muñecas:
```bash
conda run -n hgen python entrenamiento/humanoidverse/train_agent.py \
  exp=motion env.motion_id=3 env.num_envs=4096 \
  training.max_iterations=5000 \
  exp_name=motion_muñecas \
  training.save_interval=1000
```
Las muñecas tienen kp=4 (muy bajo) — el movimiento será más suave pero más lento. Esto es esperado.

**Checkpoint esperado:** `entrenamiento/humanoidverse/logs/motion_muñecas/model_5000.pt`  
**Reward mínimo:** >0.5

---

### AGENTE-22 — Validación intermedia MOV-3: MOVER MUÑECAS
**Tarea:** 5 episodios headless. Verificar:
- `left_wrist_roll` oscila con rango >0.8 rad (max-min en el episodio)
- `right_wrist_roll` oscila con rango >0.8 rad
- Brazos en posición intermedia correcta (shoulder_pitch ≈ -0.6 rad)

**Output:** Tabla de 5 episodios + decisión

---

## Fase 4: Validación Completa (5 Agentes)

### AGENTE-23 — Validación 20 episodios: SALUDAR
**Tarea:** Cargar `model_saludar_final.pt` y correr 20 episodios headless con variación de pose inicial (±5° ruido en joints). Para cada episodio registrar:

| Ep | right_shoulder_pitch_min | wrist_pitch_range | pelvis_z_min | Resultado |
|---|---|---|---|---|
| 1 | ... | ... | ... | PASS/FAIL |

**Criterio PASS:** right_shoulder_pitch < -0.8 AND wrist_pitch_range > 0.3  
**Aprobación:** ≥16/20 PASS

---

### AGENTE-24 — Validación 20 episodios: AGACHARSE
**Tarea:** 20 episodios headless, registrar:

| Ep | knee_delta_max | pelvis_z_drop | robot_stood | Resultado |
|---|---|---|---|---|

**Criterio PASS:** knee_delta > 0.5 AND pelvis_z_drop > 0.02m AND robot_stood (no cayó)  
**Aprobación:** ≥16/20 PASS

---

### AGENTE-25 — Validación 20 episodios: ESTIRAR BRAZOS
**Tarea:** 20 episodios headless, registrar:

| Ep | left_shoulder_pitch_min | right_shoulder_pitch_min | legs_stable | Resultado |
|---|---|---|---|---|

**Criterio PASS:** ambos shoulder_pitch < -1.0 simultáneamente  
**Aprobación:** ≥16/20 PASS

---

### AGENTE-26 — Validación 20 episodios: MOVER MUÑECAS
**Tarea:** 20 episodios headless, registrar:

| Ep | left_wrist_roll_range | right_wrist_roll_range | arms_in_position | Resultado |
|---|---|---|---|---|

**Criterio PASS:** ambos wrist_roll_range > 1.0 rad  
**Aprobación:** ≥16/20 PASS

---

### AGENTE-27 — Análisis de calidad: suavidad y estabilidad
**Tarea:** Para cada política, calcular métricas de calidad sobre los 20 episodios de validación:

1. **Suavidad de trayectoria:** `jerk = ||a_t - 2*a_{t-1} + a_{t-2}||` (promedio por episodio) — debe ser < 0.5
2. **Tiempo de convergencia:** steps hasta que el joint principal llega a ≥80% del target
3. **Estabilidad:** std de pelvis_z durante episodio (debe ser < 0.02 m)
4. **Eficiencia energética:** torque_rms promedio

Reportar tabla comparativa de los 4 movimientos.

**Output:** Tabla de métricas de calidad

---

## Fase 5: Export y Cierre (3 Agentes)

### AGENTE-28 — Exportar 4 políticas a TorchScript JIT
**Tarea:** Exportar cada política al formato JIT:
```bash
# Para cada movimiento en [saludar, agacharse, estirar, muñecas]:
conda run -n hgen python -c "
import torch
model = torch.load('entrenamiento/humanoidverse/logs/motion_NOMBRE/model_final.pt')
model.eval()
example_input = torch.zeros(1, 62)
jit_model = torch.jit.trace(model.actor, example_input)
torch.jit.save(jit_model, 'politicas/motions/model_NOMBRE_jit.pt')
# Verificar:
loaded = torch.jit.load('politicas/motions/model_NOMBRE_jit.pt')
out = loaded(example_input)
print(f'NOMBRE: input(62,) -> output{out.shape}')
"
```
Crear directorio `politicas/motions/` si no existe.

**Output:** 4 archivos `.pt` en `politicas/motions/`:
- `model_saludar_jit.pt`
- `model_agacharse_jit.pt`
- `model_estirar_brazos_jit.pt`
- `model_muñecas_jit.pt`

---

### AGENTE-29 — Actualizar g1_constants.py
**Tarea:** Agregar al archivo `simulacion/g1_constants.py` las siguientes constantes:

```python
# ── Motion Policies ──────────────────────────────────────────
MOTION_POLICY_DIR = "politicas/motions"
MOTION_POLICIES = {
    "saludar":        "politicas/motions/model_saludar_jit.pt",
    "agacharse":      "politicas/motions/model_agacharse_jit.pt",
    "estirar_brazos": "politicas/motions/model_estirar_brazos_jit.pt",
    "muñecas":        "politicas/motions/model_muñecas_jit.pt",
}
MOTION_OBS_DIM = 62   # q_actual(29) + q_target(29) + phase(1) + gravity(3)
MOTION_ACT_DIM = 29   # todos los DOF del g1_29dof

# ── Upper body DOF indices (en el vector de 29 DOF) ──────────
UPPER_DOF_START = 12  # waist_yaw es el primer DOF upper body
UPPER_DOF_END   = 29  # 17 DOF upper (3 waist + 7 left arm + 7 right arm)
LOWER_DOF_START = 0
LOWER_DOF_END   = 12

# ── Índices específicos por joint (en el vector de 29) ────────
IDX_R_SHOULDER_PITCH = 22
IDX_R_SHOULDER_ROLL  = 23
IDX_R_ELBOW          = 25
IDX_R_WRIST_ROLL     = 26
IDX_R_WRIST_PITCH    = 27
IDX_L_KNEE           = 3
IDX_R_KNEE           = 9
```

**Output:** `simulacion/g1_constants.py` actualizado

---

### AGENTE-30 — Reporte final y git commit
**Tarea:** Generar reporte completo en `reportes/reporte_plan02b_motion_20260515.md` con:

1. Resumen ejecutivo (resultados de los 4 movimientos)
2. Tabla de validación por movimiento (20 episodios c/u)
3. Tabla de métricas de calidad (suavidad, convergencia, estabilidad)
4. Tamaños de los 4 modelos exportados
5. Bugs encontrados y corregidos durante implementación
6. Próximos pasos (Plan 03: navegación LIDAR)

Luego hacer git add y commit:
```bash
git add entrenamiento/humanoidverse/envs/motion/ \
        entrenamiento/humanoidverse/simulator/genesis/genesis_motion.py \
        entrenamiento/humanoidverse/config/env/motion.yaml \
        entrenamiento/humanoidverse/config/exp/motion.yaml \
        entrenamiento/humanoidverse/config/rewards/motion/ \
        entrenamiento/humanoidverse/config/obs/motion/ \
        entrenamiento/humanoidverse/config/motions/ \
        politicas/motions/ \
        simulacion/g1_constants.py \
        reportes/reporte_plan02b_motion_20260515.md
git commit -m "feat: Plan 02b — políticas de movimiento simple G1 (saludar/agacharse/estirar/muñecas)"
```

**Output:** Commit exitoso + link al reporte

---

## Resumen de Archivos a Crear

| Archivo | Agente | Tipo |
|---|---|---|
| `config/motions/motion_poses.yaml` | 06 | Config keyframes |
| `config/obs/motion/motion_obs.yaml` | 07 | Config obs |
| `config/rewards/motion/motion_rewards.yaml` | 08 | Config rewards |
| `config/env/motion.yaml` | 09 | Config env |
| `config/exp/motion.yaml` | 10 | Config experimento |
| `envs/motion/motion_env.py` | 11 | Env RL |
| `envs/motion/__init__.py` | 11 | Init |
| `simulator/genesis/genesis_motion.py` | 12 | Backend Genesis |
| `politicas/motions/model_saludar_jit.pt` | 28 | Política export |
| `politicas/motions/model_agacharse_jit.pt` | 28 | Política export |
| `politicas/motions/model_estirar_brazos_jit.pt` | 28 | Política export |
| `politicas/motions/model_muñecas_jit.pt` | 28 | Política export |
| `reportes/reporte_plan02b_motion_20260515.md` | 30 | Reporte |

## Criterio de Aprobación Global

**APROBADO** si los 4 movimientos pasan su validación de 20 episodios (≥16/20 PASS cada uno) Y las 4 políticas JIT están exportadas correctamente (input 62 → output 29).

**DESAPROBADO** si algún movimiento tiene <16/20 PASS — se re-entrena ese movimiento específico con 3000 iters adicionales antes de volver a validar.
