# 03 — Política madre (jerárquica) que orquesta sub-políticas

> Idea central tomada de `revisionEntrenamiento.md`:
>
> *"Para orquestar las políticas de estabilidad, locomoción y YOLO… queremos una política madre (high-level) que llame a hijas según el contexto."*

Y el diagrama original:

```
YOLO → Target Vector
        ↓
High-Level Planner          ← política MADRE
        ↓
Locomotion Policy           ← política HIJA (WASD/coordenadas)
        ↓
Stability Controller        ← política HIJA (standing/push-recovery)
        ↓
Actuadores
```

Este documento desarrolla **cómo se materializa esa jerarquía dentro de Isaac Lab** y cómo se entrena la madre cuando ya tienes hijas entrenadas (`r1_standing`, `r1_locomotion`).

---

## 1. Tipos de jerarquía: ¿cuál usar?

| Enfoque | Cuándo conviene | Costo de entrenamiento |
|--------|-----------------|------------------------|
| **HRL clásico (Options Framework / FeUdal Networks)** | Tareas long-horizon con objetivos abstractos. | Alto — requiere entrenar madre e hijas en *joint training*. |
| **HRL con sub-políticas pre-entrenadas (frozen)** | Tienes *experts* (standing, walking) y solo entrenas la *madre* que decide cuándo activarlos. | Bajo — la madre es pequeña, se entrena en horas. |
| **FSM / Behavior Tree + sub-policies** | Lógica determinista clara (parado → caminar → escaleras). | Casi cero — no hay aprendizaje en la madre. |
| **Behavioral Foundation Model (BFM)** *(arXiv 2504.11054)* | Quieres *zero-shot* en tareas nuevas. | Muy alto al pre-entrenar; cero al desplegar. |

**Para el caso del R1 con políticas ya entrenadas → usar la opción 2: HRL con sub-políticas congeladas.** La madre es un MLP/transformer pequeño que selecciona qué política hija activar y le pasa un *command vector* (target xy, velocidad deseada, etc.).

Equivalente al *Locomotion + Local Navigation* end-to-end del paper [arXiv:2209.12827](https://arxiv.org/pdf/2209.12827) — referencia explícita en `space_r1/fuentes.md`.

---

## 2. Arquitectura propuesta

```
                ┌─────────────────────────────────────────┐
                │      MADRE (High-level Planner)         │
                │    π_M: (obs_world, goal) → (k, c)      │
                │                                         │
                │   Inputs:                               │
                │     - target world (x*, y*, ψ*)         │
                │     - LIDAR / depth o YOLO targets      │
                │     - propio-velocidad, altura          │
                │   Output:                               │
                │     - k ∈ {STAND, WALK, STAIR, …}       │
                │     - c = command vector (vx, vy, wz)   │
                │   Frecuencia: 10 Hz (cada 0.1 s)        │
                └────────────┬────────────────────────────┘
                             │
                ┌────────────▼─────────────┐
                │  Selector / Mixer         │   ← Gating layer
                │  α_k = softmax(logits_k)  │   (opcional: blend en lugar de hard switch)
                └────────────┬─────────────┘
            ┌────────────────┼─────────────────────┐
            │                │                     │
   ┌────────▼─────┐  ┌───────▼──────┐    ┌─────────▼──────┐
   │ STAND policy │  │ WALK policy  │    │ STAIR policy   │  ← HIJAS (frozen)
   │ π_stand      │  │ π_walk       │    │ π_stair        │     50 Hz
   └────────┬─────┘  └───────┬──────┘    └─────────┬──────┘
            └────────────────┼─────────────────────┘
                             ▼
                       Joint targets (26 DOF)
                             ▼
                          Robot R1
```

Frecuencias jerárquicas (lo que en RL se llama *temporal abstraction*):

- Madre: **10 Hz** (decide cada 100 ms, similar al *option duration*).
- Hijas: **50 Hz** (control bajo). En Isaac Lab, eso = `decimation=2` con `sim.dt=1/120` aprox.

---

## 3. Implementación en Isaac Lab

### 3.1 Cargar las hijas entrenadas en *inference mode*

```python
# codigos/hierarchical/hierarchical_env.py
from rsl_rl.runners import OnPolicyRunner

class FrozenChild:
    """Wrapper que carga un checkpoint y expone solo .act(obs)."""
    def __init__(self, checkpoint_path, agent_cfg, env, device):
        runner = OnPolicyRunner(env, agent_cfg.to_dict(), log_dir=None, device=device)
        runner.load(checkpoint_path)
        self.policy = runner.get_inference_policy(device=device)
        for p in runner.alg.get_policy().parameters():
            p.requires_grad_(False)

    @torch.inference_mode()
    def act(self, obs):
        return self.policy(obs)
```

Las hijas viven en disco (esa carpeta `logs/rsl_rl/r1_standing/2026-03-03_15-35-21` mencionada en `revisionEntrenamiento.md` es el primer checkpoint que ya funcionaba). El path se pasa por config:

```python
@configclass
class HierarchicalCfg:
    stand_ckpt: str = r"D:\space_r1\IsaacLab\logs\rsl_rl\r1_standing\2026-03-03_15-35-21\model_3500.pt"
    walk_ckpt:  str = r"D:\space_r1\IsaacLab\logs\rsl_rl\r1_locomotion\2026-04-12_09-12-00\model_8000.pt"
    stair_ckpt: str = r"D:\space_r1\IsaacLab\logs\rsl_rl\r1_stairs\2026-04-20_14-45-32\model_12000.pt"
```

### 3.2 Madre como política PPO de tamaño pequeño

```python
class HighLevelPolicyCfg(RslRlPpoActorCriticCfg):
    init_noise_std        = 0.5
    actor_hidden_dims     = [128, 64]   # mucho más pequeña que las hijas
    critic_hidden_dims    = [128, 64]
    activation            = "elu"
```

Output de la madre = **3 + 1** dims:

- 3 commands (`vx_des, vy_des, wz_des`) en `[-1, 1]` (luego escalados).
- 1 logit de gating (sigmoid → α ∈ [0,1]) para mezclar STAND vs. WALK.

> Para 3+ hijas, el output es `n_skills` logits → softmax → α_k.

### 3.3 Loop de entrenamiento (madre)

```python
def _apply_action(self):
    # 1) Madre produce: command + alpha
    cmd = self.actions[:, :3] * self.cfg.cmd_scale       # (N, 3)
    alpha = torch.sigmoid(self.actions[:, 3:4])           # (N, 1)

    # 2) Construir obs para cada hija (concatenar cmd a obs raw)
    stand_obs = self._build_stand_obs()                   # 88 dims
    walk_obs  = self._build_walk_obs(cmd)                 # 88 + 9 = 97 dims

    # 3) Hijas inferencia (sin gradientes)
    a_stand = self.stand.act({"policy": stand_obs})
    a_walk  = self.walk.act({"policy": walk_obs})

    # 4) Mezclar (soft gating) → control bajo
    actions_low = (1 - alpha) * a_stand + alpha * a_walk

    # 5) Aplicar al robot (igual que en r1_standing_env)
    target = self.robot.data.default_joint_pos + actions_low * self.cfg.action_scale
    target = torch.clamp(target, ...)
    self.robot.set_joint_position_target(target, joint_ids=self._joint_ids)
```

> **Nota crítica**: el *blend* entre `a_stand` y `a_walk` solo es sensato si ambas hijas operan en el mismo *action space* (joint position targets en 26 DOF). Eso lo hemos garantizado en doc 02. Si difieren (p.ej. una usa torque), aplicar **hard switch** en lugar de blend.

### 3.4 Recompensa de la madre

La madre **no se entrena con los rewards de las hijas**. Tiene su propia función:

```python
# Reward = alcanzar el target con seguridad
rew_progress  = -dist_to_goal * 1.0                              # progreso
rew_arrival   = (dist_to_goal < 0.3).float() * 50.0              # llegada
rew_smoothness = -torch.square(self.actions - self._prev).mean() # transiciones suaves
rew_alive     = 1.0 - terminated.float()
rew_terminate = -200.0 * terminated.float()
rew_skill_persist = -0.1 * (alpha_changed_flag.float())          # no oscilar entre skills
total = rew_progress + rew_arrival + rew_smoothness + rew_alive + rew_terminate + rew_skill_persist
```

> **`rew_skill_persist`** es clave: sin él, la madre alterna 50 veces por segundo entre STAND y WALK y el robot vibra. Es el *option-cost* del paper de FeUdal Networks.

### 3.5 Reset y curriculum

- Spawnear el robot en `(0, 0)` y muestrear `target ~ U(disk(1m, 5m))`. Al llegar (dist < 0.3), resamplear sin reset físico → entrenamiento eficiente.
- Curriculum: empezar con targets cercanos (1–2 m), subir a 5 m al iter 2000, terreno plano → escaleras al iter 5000.

---

## 4. Alternativa más simple: FSM determinista + sub-policies

Si no quieres entrenar otra red, puedes implementar la madre como un **state machine** y **olvidarte del PPO** en el high-level:

```python
class FSMHighLevel:
    STAND, WALK, RECOVER, STAIR = range(4)

    def step(self, target_xy, robot_xy, robot_state):
        d = torch.norm(target_xy - robot_xy)
        if robot_state.is_falling: return self.RECOVER, None
        if d < 0.3:                return self.STAND,   None
        if robot_state.is_on_stairs: return self.STAIR, target_xy - robot_xy
        return self.WALK, (target_xy - robot_xy)
```

Y el env aplica la hija correspondiente. Es lo que permite el `play_wasd.py` ya existente — el target se establece por teclado, la hija de locomoción lo persigue, y si se cae se reactiva la de standing.

**Cuándo usar FSM**: para un demo o controlador final ya determinista.
**Cuándo usar madre RL**: cuando quieres que el robot *aprenda* cuándo cambiar de skill (escaleras vs. terreno, evitar obstáculos detectados por YOLO, etc.).

---

## 5. Integrar percepción (YOLO / depth)

La madre puede recibir un *target_vector* generado por YOLO o un planificador externo. La interfaz:

```python
@dataclass
class HighLevelObs:
    proprio: torch.Tensor          # (N, 9)   gravedad + ang_vel + lin_vel
    goal_xy: torch.Tensor          # (N, 2)   meta absoluta
    yolo_target: torch.Tensor      # (N, 3)   (x, y, class_id)
    nearest_obstacle: torch.Tensor # (N, 2)   distancia al obstáculo más cercano
    feet_contact: torch.Tensor     # (N, 2)   bool por pie
```

La perception puede correr **fuera** de Isaac Sim (ROS2 bridge, real-time inference) y publicar el target. La madre solo lo consume.

---

## 6. Estrategia de entrenamiento end-to-end

1. **Pre-train hijas (separadas)** — doc 02 + doc 04.
2. **Congelar las hijas** (`requires_grad=False`).
3. **Entrenar la madre** con sus propias rewards de navegación, durante **2000–5000 iters**, en terreno plano con targets aleatorios.
4. **Curriculum**: añadir terreno rugoso → escaleras → obstáculos.
5. **Joint-tune (opcional)**: descongelar las hijas con LR muy bajo (1e-5) y entrenar 500 iters más para que se *afinen* al estilo de la madre. Ojo: arriesga catastrophic forgetting; backup primero.

---

## 7. Código de referencia

Plantillas en este repo de docs:

- [`codigos/hierarchical/high_level_planner.py`](./codigos/hierarchical/high_level_planner.py) — clase `HighLevelPolicy` con MLP pequeño.
- [`codigos/hierarchical/hierarchical_env.py`](./codigos/hierarchical/hierarchical_env.py) — env Direct que carga hijas, mezcla actions.
- [`codigos/hierarchical/README.md`](./codigos/hierarchical/README.md) — diagrama, comandos de train/play.

Próximo paso → [04_Fine_Tuning.md](./04_Fine_Tuning.md).
