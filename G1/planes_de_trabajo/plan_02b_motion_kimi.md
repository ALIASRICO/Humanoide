# Instrucciones — Políticas de Movimiento Simple G1 (para Kimi/OpenCode)

Eres un agente de codificación autónomo. Ejecuta todas las tareas de este documento en orden, de principio a fin, sin pausar a preguntar. Si algo falla, aplica el fix indicado y continúa. Al terminar, genera el reporte y haz el commit.

---

## Contexto del proyecto

**Directorio de trabajo:** `/home/udc/Unitree_G1`  
**Entorno de entrenamiento:** conda `hgen` (Python 3.10, PyTorch 2.11.0, Genesis 0.2.1, CUDA 13.0)  
**Framework RL:** HumanoidVerse (ya instalado en `entrenamiento/humanoidverse/`)  
**Robot:** G1 29-DOF sin manos dextrales — config en `entrenamiento/humanoidverse/config/robot/g1/g1_29dof.yaml`  
**GPU:** RTX 5090 32GB — usar 4096 envs Genesis  

**Objetivo:** Entrenar 4 políticas de movimiento simple (saludar, agacharse, estirar brazos, mover muñecas) y exportarlas como TorchScript JIT.

---

## DOF del G1 29-DOF (referencia)

```
Índices 0-11   → piernas (lower body, 12 DOF)
  0: left_hip_pitch      6: right_hip_pitch
  1: left_hip_roll       7: right_hip_roll
  2: left_hip_yaw        8: right_hip_yaw
  3: left_knee           9: right_knee
  4: left_ankle_pitch   10: right_ankle_pitch
  5: left_ankle_roll    11: right_ankle_roll

Índices 12-28  → cintura + brazos (upper body, 17 DOF)
  12: waist_yaw         19: left_wrist_roll
  13: waist_roll        20: left_wrist_pitch
  14: waist_pitch       21: left_wrist_yaw
  15: left_shoulder_pitch   22: right_shoulder_pitch
  16: left_shoulder_roll    23: right_shoulder_roll
  17: left_shoulder_yaw     24: right_shoulder_yaw
  18: left_elbow            25: right_elbow
                            26: right_wrist_roll
                            27: right_wrist_pitch
                            28: right_wrist_yaw

Pose default (action=0): piernas con rodilla=0.3, hip=-0.1, ankle=-0.2. Upper body todo en 0.
PD gains upper: shoulders kp=90 kd=2, elbows kp=60 kd=1, wrists kp=4 kd=0.2, waist kp=400 kd=5
```

---

## Poses objetivo de los 4 movimientos

```python
# Todos los valores son deltas sobre la pose default (rad)
# Joints no mencionados permanecen en 0 (default upper) o default lower

MOTION_POSES = {
    # MOV-0: SALUDAR — brazo derecho sube, muñeca oscila
    "saludar": {
        "pose_A": {22: -1.2, 23: -0.3, 24: 0.0, 25: 0.8, 27: 0.5},
        "pose_B": {22: -1.2, 23: -0.3, 24: 0.0, 25: 0.8, 27: -0.5},
        "period_s": 1.0,   # oscila entre A y B
        "motion_id": 0,
    },
    # MOV-1: AGACHARSE — flexión de rodillas
    "agacharse": {
        "pose_A": {0: -0.5, 3: 0.8, 4: -0.1, 6: -0.5, 9: 0.8, 10: -0.1},
        "pose_B": {0: 0.0, 3: 0.0, 4: 0.0, 6: 0.0, 9: 0.0, 10: 0.0},  # vuelta a default
        "period_s": 3.0,   # baja 1.5s, sube 1.5s
        "motion_id": 1,
    },
    # MOV-2: ESTIRAR BRAZOS — ambos brazos al frente
    "estirar_brazos": {
        "pose_A": {15: -1.4, 16: 0.1, 18: 0.0, 22: -1.4, 23: -0.1, 25: 0.0},
        "pose_B": {15: -1.4, 16: 0.1, 18: 0.0, 22: -1.4, 23: -0.1, 25: 0.0},  # mantiene
        "period_s": 4.0,
        "motion_id": 2,
    },
    # MOV-3: MOVER MUÑECAS — rotación de muñecas
    "muñecas": {
        "pose_A": {15: -0.6, 18: 0.5, 19: 1.0, 20: 0.4, 22: -0.6, 25: 0.5, 26: -1.0, 27: 0.4},
        "pose_B": {15: -0.6, 18: 0.5, 19: -1.0, 20: -0.4, 22: -0.6, 25: 0.5, 26: 1.0, 27: -0.4},
        "period_s": 1.2,
        "motion_id": 3,
    },
}
```

---

## TAREA 1 — Verificar límites articulares

Lee `entrenamiento/humanoidverse/config/robot/g1/g1_29dof.yaml`. Extrae `dof_pos_lower_limit_list` y `dof_pos_upper_limit_list`. Verifica que cada valor de las poses objetivo esté dentro de los límites. Si algún valor viola el límite, recórtalo al 90% del límite correspondiente. Usa los valores corregidos en todo el resto de las tareas.

---

## TAREA 2 — Leer el env de locomoción existente

Lee todos los archivos en `entrenamiento/humanoidverse/envs/locomotion/` y `entrenamiento/humanoidverse/envs/legged_base_task/`. Identifica:
- Qué métodos sobreescribir para el nuevo env
- Cómo se obtiene `projected_gravity` del simulator
- Cómo se hace el reset de joints
- Qué imports son necesarios

No crees ningún archivo todavía. Solo aprende la estructura.

---

## TAREA 3 — Crear los archivos de configuración Hydra

Crea estos 5 archivos. Usa los archivos equivalentes de locomotion como referencia de formato.

### 3a. `entrenamiento/humanoidverse/config/motions/motion_poses.yaml`

```yaml
# Keyframes de los 4 movimientos (valores en rad, delta sobre default)
saludar:
  motion_id: 0
  period_s: 1.0
  pose_A:
    right_shoulder_pitch: -1.2
    right_shoulder_roll: -0.3
    right_shoulder_yaw: 0.0
    right_elbow: 0.8
    right_wrist_pitch: 0.5
  pose_B:
    right_shoulder_pitch: -1.2
    right_shoulder_roll: -0.3
    right_shoulder_yaw: 0.0
    right_elbow: 0.8
    right_wrist_pitch: -0.5

agacharse:
  motion_id: 1
  period_s: 3.0
  pose_A:
    left_hip_pitch: -0.5
    left_knee: 0.8
    left_ankle_pitch: -0.1
    right_hip_pitch: -0.5
    right_knee: 0.8
    right_ankle_pitch: -0.1
  pose_B: {}  # vuelta a pose default

estirar_brazos:
  motion_id: 2
  period_s: 4.0
  pose_A:
    left_shoulder_pitch: -1.4
    left_shoulder_roll: 0.1
    left_elbow: 0.0
    right_shoulder_pitch: -1.4
    right_shoulder_roll: -0.1
    right_elbow: 0.0
  pose_B:
    left_shoulder_pitch: -1.4
    left_shoulder_roll: 0.1
    left_elbow: 0.0
    right_shoulder_pitch: -1.4
    right_shoulder_roll: -0.1
    right_elbow: 0.0

muñecas:
  motion_id: 3
  period_s: 1.2
  pose_A:
    left_shoulder_pitch: -0.6
    left_elbow: 0.5
    left_wrist_roll: 1.0
    left_wrist_pitch: 0.4
    right_shoulder_pitch: -0.6
    right_elbow: 0.5
    right_wrist_roll: -1.0
    right_wrist_pitch: 0.4
  pose_B:
    left_shoulder_pitch: -0.6
    left_elbow: 0.5
    left_wrist_roll: -1.0
    left_wrist_pitch: -0.4
    right_shoulder_pitch: -0.6
    right_elbow: 0.5
    right_wrist_roll: 1.0
    right_wrist_pitch: -0.4
```

### 3b. `entrenamiento/humanoidverse/config/obs/motion/motion_obs.yaml`

Crea este archivo siguiendo el formato exacto de `entrenamiento/humanoidverse/config/obs/loco/`. El obs tiene 62 dimensiones:
- `dof_pos` (29): posición actual de todos los joints
- `q_target` (29): pose objetivo interpolada según phase
- `phase_signal` (1): sin(2π·t/period)
- `projected_gravity` (3): vector gravedad en frame del pelvis

### 3c. `entrenamiento/humanoidverse/config/rewards/motion/motion_rewards.yaml`

```yaml
scales:
  pose_tracking: 0.8
  leg_stability: 0.2
  action_smoothness: -0.01
  alive_bonus: 0.1
  fall_penalty: -10.0

params:
  pose_tracking_sigma: 3.0    # exp(-sigma * error)
  leg_stability_sigma: 1.0
  fall_height_threshold: 0.5  # pelvis_z < 0.5m → caída
```

### 3d. `entrenamiento/humanoidverse/config/env/motion.yaml`

Crea siguiendo `entrenamiento/humanoidverse/config/env/locomotion.yaml`. Diferencias clave:
- `_target_`: apunta a `MotionEnv`
- `episode_length_s: 6.0`
- Sin terrain (plano plano)
- `motion_id: 0` (se sobreescribe por CLI)

### 3e. `entrenamiento/humanoidverse/config/exp/motion.yaml`

```yaml
defaults:
  - algo: ppo
  - env: motion
  - _self_

training:
  max_iterations: 5000
  save_interval: 1000
  lr: 3.0e-4
  num_mini_batches: 4
  num_epochs: 5
  clip_param: 0.2

exp_name: "motion_${env.motion_name}"
```

---

## TAREA 4 — Implementar MotionEnv

Crea `entrenamiento/humanoidverse/envs/motion/__init__.py` (vacío) y `entrenamiento/humanoidverse/envs/motion/motion_env.py`:

```python
import torch
import numpy as np
from omegaconf import OmegaConf
from entrenamiento.humanoidverse.envs.legged_base_task.legged_robot import LeggedRobotBase


class MotionEnv(LeggedRobotBase):
    """Env para entrenamiento de movimientos simples del G1 29-DOF."""

    def __init__(self, config, sim):
        super().__init__(config, sim)
        self._load_motion_poses()
        self.phase = torch.zeros(self.num_envs, device=self.device)
        self.prev_actions = torch.zeros(self.num_envs, self.num_dof, device=self.device)

    def _load_motion_poses(self):
        """Carga keyframes del YAML y los convierte a tensores (num_envs, 29)."""
        cfg_path = "entrenamiento/humanoidverse/config/motions/motion_poses.yaml"
        poses_cfg = OmegaConf.load(cfg_path)
        motion_name = self.cfg.env.get("motion_name", "saludar")
        motion = poses_cfg[motion_name]

        self.period_s = float(motion.period_s)
        self.motion_id = int(motion.motion_id)

        # Construir tensores de pose (29 DOF, deltas sobre default)
        dof_names = self.cfg.robot.dof_names  # lista de 29 nombres en orden
        self.q_target_A = self._pose_dict_to_tensor(dict(motion.pose_A), dof_names)
        self.q_target_B = self._pose_dict_to_tensor(dict(motion.pose_B), dof_names)

    def _pose_dict_to_tensor(self, pose_dict, dof_names):
        """Convierte dict {joint_name: value} a tensor (num_envs, 29)."""
        tensor = torch.zeros(self.num_envs, len(dof_names), device=self.device)
        for name, val in pose_dict.items():
            if name in dof_names:
                idx = dof_names.index(name)
                tensor[:, idx] = float(val)
        return tensor

    def _get_current_target(self):
        """Interpola entre pose_A y pose_B según phase actual."""
        t = self.phase  # (num_envs,)
        # alpha va de 0 a 1 (primera mitad) y de 1 a 0 (segunda mitad)
        alpha = 0.5 * (1 - torch.cos(2 * np.pi * t / self.period_s))
        alpha = alpha.unsqueeze(1)  # (num_envs, 1)
        return self.q_target_A * (1 - alpha) + self.q_target_B * alpha

    def compute_observations(self):
        q_actual = self.sim.get_dof_pos()          # (num_envs, 29)
        q_target = self._get_current_target()       # (num_envs, 29)
        phase_signal = torch.sin(
            2 * np.pi * self.phase / self.period_s
        ).unsqueeze(1)                              # (num_envs, 1)
        gravity = self.sim.get_projected_gravity()  # (num_envs, 3)

        self.obs_buf = torch.cat([q_actual, q_target, phase_signal, gravity], dim=1)
        # obs_dim = 29 + 29 + 1 + 3 = 62
        return self.obs_buf

    def compute_rewards(self):
        q_actual = self.sim.get_dof_pos()
        q_target = self._get_current_target()
        default_lower = self._get_default_lower()

        # Error upper body (índices 12-28)
        error_upper = torch.norm(q_actual[:, 12:] - q_target[:, 12:], dim=1)
        reward_pose = torch.exp(-self.cfg.rewards.params.pose_tracking_sigma * error_upper)

        # Estabilidad lower body (índices 0-12)
        error_lower = torch.norm(q_actual[:, :12] - default_lower, dim=1)
        reward_legs = torch.exp(-self.cfg.rewards.params.leg_stability_sigma * error_lower)

        # Suavidad
        smooth_penalty = torch.norm(self.actions - self.prev_actions, dim=1) ** 2

        # Alive bonus / fall penalty
        pelvis_z = self.sim.get_base_pos()[:, 2]
        alive = (pelvis_z > self.cfg.rewards.params.fall_height_threshold).float()
        fall = (1 - alive)

        scales = self.cfg.rewards.scales
        reward = (
            scales.pose_tracking * reward_pose
            + scales.leg_stability * reward_legs
            + scales.action_smoothness * smooth_penalty
            + scales.alive_bonus * alive
            + scales.fall_penalty * fall
        )
        self.prev_actions = self.actions.clone()
        return reward

    def _get_default_lower(self):
        """Retorna tensor (num_envs, 12) con la pose default de las piernas."""
        # Extraído de g1_29dof.yaml default_joint_angles
        default = torch.tensor(
            [-0.1, 0., 0., 0.3, -0.2, 0.,   # left leg
             -0.1, 0., 0., 0.3, -0.2, 0.],  # right leg
            device=self.device
        )
        return default.unsqueeze(0).expand(self.num_envs, -1)

    def check_termination(self):
        pelvis_z = self.sim.get_base_pos()[:, 2]
        self.reset_buf = (pelvis_z < 0.5).long()

    def post_physics_step(self):
        self.phase += self.dt  # avanza el reloj de phase
        self.phase = torch.fmod(self.phase, self.period_s)
        super().post_physics_step()
```

Si algún método del sim (e.g. `get_projected_gravity`, `get_dof_pos`) no existe en el simulator base, agrégalo en `entrenamiento/humanoidverse/simulator/genesis/genesis_motion.py` extendiendo el simulator de Genesis existente.

---

## TAREA 5 — Crear genesis_motion.py

Lee todos los archivos en `entrenamiento/humanoidverse/simulator/genesis/`. Crea `genesis_motion.py` que extiende el simulator de Genesis base, sin terrain (plano plano), y que expone `get_projected_gravity()` si no existe en el base.

---

## TAREA 6 — Test de integración (OBLIGATORIO antes de entrenar)

Ejecuta:
```bash
cd /home/udc/Unitree_G1
conda run -n hgen python -c "
import sys
sys.path.insert(0, '.')
# Carga el env con n_envs=4 para test rápido
# Verifica obs.shape == (4, 62)
# Verifica que el robot no cae en 10 steps
# Imprime obs_dim, act_dim, reward medio
print('Test OK')
"
```

Si hay errores de import, shape incorrecto o NaN: corrige los archivos de las Tareas 4 y 5 hasta que el test pase. No pases a la Tarea 7 hasta que este test sea exitoso.

---

## TAREA 7 — Sanity check PPO (50 iteraciones)

```bash
cd /home/udc/Unitree_G1
conda run -n hgen python entrenamiento/humanoidverse/train_agent.py \
  exp=motion env.motion_name=saludar env.num_envs=64 \
  training.max_iterations=50 \
  exp_name=motion_sanity
```

Verifica que no hay NaN en loss ni reward. Si hay NaN: reduce lr a 1e-4 en `exp/motion.yaml` y reintenta. No pases a la Tarea 8 hasta que 50 iters corran sin NaN.

---

## TAREA 8 — Entrenar los 4 movimientos

Ejecuta los 4 entrenamientos en secuencia. Por cada uno, al terminar las 5000 iters, copia el mejor checkpoint a `model_final.pt`:

### 8a. Saludar
```bash
conda run -n hgen python entrenamiento/humanoidverse/train_agent.py \
  exp=motion env.motion_name=saludar env.num_envs=4096 \
  training.max_iterations=5000 training.save_interval=1000 \
  exp_name=motion_saludar
```
**Si el reward al iter 5000 es < 0.4:** Re-entrena 2000 iters más (total 7000). Si sigue < 0.4, anota el problema y continúa con el siguiente movimiento.

### 8b. Agacharse
```bash
conda run -n hgen python entrenamiento/humanoidverse/train_agent.py \
  exp=motion env.motion_name=agacharse env.num_envs=4096 \
  training.max_iterations=5000 training.save_interval=1000 \
  exp_name=motion_agacharse
```
**Si el robot cae constantemente (reward_alive < 0.5):** Agrega override `env.rewards.scales.leg_stability=0.5 env.rewards.scales.pose_tracking=0.5` y re-entrena.

### 8c. Estirar brazos
```bash
conda run -n hgen python entrenamiento/humanoidverse/train_agent.py \
  exp=motion env.motion_name=estirar_brazos env.num_envs=4096 \
  training.max_iterations=5000 training.save_interval=1000 \
  exp_name=motion_estirar
```

### 8d. Mover muñecas
```bash
conda run -n hgen python entrenamiento/humanoidverse/train_agent.py \
  exp=motion env.motion_name=muñecas env.num_envs=4096 \
  training.max_iterations=5000 training.save_interval=1000 \
  exp_name=motion_muñecas
```

---

## TAREA 9 — Validar 20 episodios por movimiento

Para cada movimiento, escribe y ejecuta un script de validación headless que:
1. Carga el `model_final.pt` del movimiento
2. Corre 20 episodios de 300 pasos cada uno
3. Para cada episodio registra la métrica de éxito específica
4. Imprime la tabla y el resumen

**Criterios de éxito por episodio:**

| Movimiento | Criterio PASS |
|---|---|
| Saludar | `right_shoulder_pitch_min < -0.8` Y `right_wrist_pitch_range > 0.3 rad` |
| Agacharse | `knee_delta_max > 0.5` Y `pelvis_z_drop > 0.02 m` Y robot no cayó |
| Estirar brazos | Ambos `shoulder_pitch < -1.0` simultáneamente en ≥60% de steps |
| Mover muñecas | `wrist_roll_range > 1.0 rad` en ambas muñecas |

**Si un movimiento tiene < 16/20 PASS:** Re-entrena ese movimiento 3000 iters más y vuelve a validar.

---

## TAREA 10 — Exportar 4 políticas a TorchScript JIT

```bash
mkdir -p /home/udc/Unitree_G1/politicas/motions

conda run -n hgen python -c "
import torch, os

movements = ['saludar', 'agacharse', 'estirar_brazos', 'muñecas']
log_base = 'entrenamiento/humanoidverse/logs'
out_base = 'politicas/motions'

for name in movements:
    checkpoint = f'{log_base}/motion_{name}/model_final.pt'
    out_path = f'{out_base}/model_{name}_jit.pt'
    
    model = torch.load(checkpoint, map_location='cpu')
    actor = model['actor'] if isinstance(model, dict) else model.actor
    actor.eval()
    
    example = torch.zeros(1, 62)
    jit_model = torch.jit.trace(actor, example)
    torch.jit.save(jit_model, out_path)
    
    # Verificar
    loaded = torch.jit.load(out_path)
    out = loaded(example)
    size_kb = os.path.getsize(out_path) / 1024
    print(f'{name}: input(62,) -> output{tuple(out.shape)} | {size_kb:.1f} KB')
"
```

Si el checkpoint tiene estructura diferente (dict, wrapper, etc.), adapta el código de carga según sea necesario.

---

## TAREA 11 — Actualizar simulacion/g1_constants.py

Agrega al final de `simulacion/g1_constants.py`:

```python
# ── Motion Policies (Plan 02b) ────────────────────────────────
MOTION_POLICIES = {
    "saludar":        "politicas/motions/model_saludar_jit.pt",
    "agacharse":      "politicas/motions/model_agacharse_jit.pt",
    "estirar_brazos": "politicas/motions/model_estirar_brazos_jit.pt",
    "muñecas":        "politicas/motions/model_muñecas_jit.pt",
}
MOTION_OBS_DIM = 62   # q_actual(29) + q_target(29) + phase(1) + gravity(3)
MOTION_ACT_DIM = 29

# Índices DOF upper body en el vector de 29
UPPER_DOF_START = 12
UPPER_DOF_END   = 29
LOWER_DOF_START = 0
LOWER_DOF_END   = 12

# Índices específicos (para validación y control)
IDX_R_SHOULDER_PITCH = 22
IDX_R_WRIST_PITCH    = 27
IDX_L_KNEE           = 3
IDX_R_KNEE           = 9
IDX_L_SHOULDER_PITCH = 15
IDX_L_WRIST_ROLL     = 19
IDX_R_WRIST_ROLL     = 26
```

---

## TAREA 12 — Generar reporte y hacer git commit

Genera `reportes/reporte_plan02b_motion_20260515.md` con:
- Resumen ejecutivo (qué funcionó, qué no)
- Tabla de validación por movimiento (20 episodios c/u: tasa de éxito, reward medio, métrica clave)
- Tamaños de los 4 modelos JIT exportados
- Lista de todos los archivos creados/modificados
- Bugs encontrados y cómo se corrigieron
- Próximos pasos

Luego:
```bash
cd /home/udc/Unitree_G1
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
git push
```

---

## Criterio de aprobación

El plan está completo cuando:
1. Los 4 archivos JIT existen en `politicas/motions/` con input(62,) → output(29,)
2. Cada movimiento tiene ≥16/20 episodios PASS en la validación
3. El commit está en el repositorio
4. El reporte existe en `reportes/`
