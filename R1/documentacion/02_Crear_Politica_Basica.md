# 02 — Cómo crear una política básica para el R1

> Objetivo: explicar paso a paso, con ejemplos del propio repo, **cómo se construye una política PPO** para el R1 dentro de Isaac Lab usando el *Direct Workflow* (sin manager-based).

Una política en Isaac Lab consta de tres bloques:

1. **Env config** (`*_env_cfg.py`) — *qué* se observa, *cuántas* acciones hay, *qué* recompensas se aplican (escalas).
2. **Env logic** (`*_env.py`) — *cómo* se computan las observaciones, *cómo* se aplican acciones al robot, *cómo* se evalúan rewards y *cuándo* termina un episodio.
3. **Agent config** (`agents/rsl_rl_ppo_cfg.py` o `skrl_ppo_cfg.yaml`) — hiperparámetros del optimizador (PPO).

Y un cuarto bloque:

4. **Registro Gym** en `__init__.py` — convierte la tarea en un `gym.make("R1Standing-Direct-v0")`.

---

## 1. Crear el esqueleto con la plantilla de Isaac Lab

Desde `D:\space_r1\IsaacLab`:

```powershell
.\isaaclab.bat --new
```

Responder el wizard así:

| Paso | Respuesta |
|-----|----------|
| Project type | **External** |
| Path | `D:\space_r1` |
| Project name | `r1_standing` (o el que quieras) |
| Workflow | **Direct** *(no `Manager-based` para esta política)* |
| Agent type | Single-agent |
| RL libs | rsl_rl **+** skrl |
| Algorithm | PPO (AMP opcional para fine-tune avanzado) |

Genera:

```
D:\space_r1\r1_standing\
 ├─ scripts\               ← train.py / play.py para cada lib
 └─ source\r1_standing\
    └─ r1_standing\
       ├─ __init__.py
       └─ tasks\direct\r1_standing\
          ├─ __init__.py             ← registra Gym
          ├─ r1_standing_env.py      ← lógica
          ├─ r1_standing_env_cfg.py  ← config
          └─ agents\
             ├─ rsl_rl_ppo_cfg.py
             └─ skrl_ppo_cfg.yaml
```

---

## 2. Diseño de observaciones (`observation_space`)

Para *standing* del R1 usamos **88 dimensiones** (las del repo):

| Bloque | Dim | Significado |
|-------|----:|-------------|
| `projected_gravity_b` | 3 | gravedad en el frame del cuerpo → orientación (cae a 0,0,-1 si erguido) |
| `root_ang_vel_b` | 3 | velocidad angular del torso |
| `root_lin_vel_b` | 3 | velocidad lineal del torso |
| `joint_pos - default_joint_pos` | 26 | desviación respecto a la pose default |
| `joint_vel` | 26 | velocidades articulares |
| `prev_actions` | 26 | acción anterior (estabiliza el aprendizaje) |
| `feet_distance` | 1 | distancia 2D entre tobillos |

> Para **locomotion WASD** se añaden 9 dims más (97 totales) → ver [doc 05](./05_Path_Coordenadas_Velocidad.md).

En el `EnvCfg`:

```python
action_space = 26                                # 26 articulaciones del R1
observation_space = 26 * 2 + 3 + 3 + 3 + 26 + 1  # = 88
state_space = 0
```

---

## 3. Diseño de acciones

El R1 tiene **26 DOF**. Usamos *position targets* relativos a la pose default:

```python
target_positions = (
    self.robot.data.default_joint_pos
    + self.actions * self.cfg.action_scale          # action_scale = 0.025
)
target_positions = torch.clamp(
    target_positions,
    self.robot.data.soft_joint_pos_limits[:, :, 0],
    self.robot.data.soft_joint_pos_limits[:, :, 1],
)
self.robot.set_joint_position_target(target_positions, joint_ids=self._joint_ids)
```

> **Por qué `action_scale = 0.025`**: con 26 DOF y aprendizaje continuo, una escala más alta provoca que el PPO produzca acciones extremas en los primeros miles de iters → el robot vibra y cae. Empezar conservador y subir solo cuando ya esté de pie.

---

## 4. Recompensas — diseño y balance

El robot R1 *standing* combina **rewards positivos** (premiar postura) y **penalties** (castigar inestabilidad). Las escalas viven en `R1StandingEnvCfg`:

```python
# === ALIVE / TERMINATION ===
rew_scale_alive       =   1.0
rew_scale_terminated  = -500.0

# === POSTURA ===
rew_scale_orientation =  20.0   # gravedad alineada con -Z
rew_scale_base_height =  10.0   # altura objetivo 0.75 m
rew_scale_knee_extension = -5.0 # piernas rectas

# === MOVIMIENTO MÍNIMO ===
rew_scale_joint_pos    = -0.02
rew_scale_joint_vel    = -0.02
rew_scale_action_rate  = -0.03
rew_scale_lin_vel      = -0.03
rew_scale_ang_vel      = -0.05

# === PIES Y SOPORTE ===
rew_scale_feet_separation       =  8.0   # cuadrática: castiga pies muy abiertos
rew_scale_feet_together         = 10.0   # pies en distancia objetivo (~28 cm)
rew_scale_foot_lateral_symmetry = 15.0
rew_scale_com_lateral_balance   = 12.0   # COM centrado
rew_scale_bilateral_balance     =  8.0   # alturas de tobillo simétricas

# === TORSO Y BRAZOS (corrige giro hacia un lado) ===
rew_scale_torso_yaw         = 25.0
rew_scale_left_arm_crossing = 20.0
rew_scale_arm_symmetry      = 15.0
rew_scale_arm_movement      =  3.0

# === PUSH RECOVERY (etapas) ===
rew_scale_recovery     =  2.0
rew_scale_com_support  =  1.0
enable_com_reward      =  1.0   # 1=ON, 0=OFF
push_interval_s        =  1.0
push_force_min/max     =  0.02 / 0.03
```

> Filosofía: **penalizar lo que no quieres ver, premiar exponencialmente lo que quieres ver**. Las recompensas exponenciales (`exp(-error/sigma)`) generan gradientes suaves que llevan al PPO al óptimo sin saltos.

### Curva de etapas para standing puro

| Etapa | Iters | Pushes | `enable_com_reward` | Objetivo |
|------|------:|:-----:|:-------------------:|----------|
| 1 — Postura estática pura | 0–2000 | OFF (`push_interval_s` muy alto) | 0 | Mantener pose default sin caer |
| 2 — Postura activa | 2000–4000 | OFF | 1 | COM sobre soporte, simetría |
| 3 — Push recovery | 4000–10000 | ON, fuerza 5–10 N | 1 | Recuperar tras empujones |
| 4 — Stepping recovery | 10000–15000 | ON, fuerza 15–25 N | 1 | Permitir paso correctivo |

Este *curriculum* lo aplicas **modificando los flags entre runs** y reanudando con `--resume` (ver [doc 04](./04_Fine_Tuning.md)).

---

## 5. Lógica del environment

Esqueleto mínimo (versión limpia y corregida del repo):

```python
# r1_standing_env.py
from __future__ import annotations
import torch
from collections.abc import Sequence

import isaaclab.sim as sim_utils
from isaaclab.assets import Articulation
from isaaclab.envs import DirectRLEnv
from isaaclab.sim.spawners.from_files import GroundPlaneCfg, spawn_ground_plane

from .r1_standing_env_cfg import R1StandingEnvCfg


class R1StandingEnv(DirectRLEnv):
    cfg: R1StandingEnvCfg

    def __init__(self, cfg, render_mode=None, **kwargs):
        super().__init__(cfg, render_mode, **kwargs)

        # Joint indexing dinámico (robusto a cambios de URDF)
        self._joint_ids, _ = self.robot.find_joints(self.cfg.joint_names)
        self._knee_ids,  _ = self.robot.find_joints(".*knee.*")
        self._left_leg,  _ = self.robot.find_joints([".*left.*hip.*", ".*left.*knee.*", ".*left.*ankle.*"])
        self._right_leg, _ = self.robot.find_joints([".*right.*hip.*", ".*right.*knee.*", ".*right.*ankle.*"])
        self._left_foot, _ = self.robot.find_bodies(".*left.*ankle.*")
        self._right_foot,_ = self.robot.find_bodies(".*right.*ankle.*")

        self._previous_actions = torch.zeros(self.num_envs, len(self._joint_ids), device=self.device)
        self._push_timer       = torch.zeros(self.num_envs, device=self.device)
        self.push_interval     = int(self.cfg.push_interval_s / (self.cfg.sim.dt * self.cfg.decimation))

    # --- Scene ---
    def _setup_scene(self):
        self.robot = Articulation(self.cfg.robot_cfg)
        spawn_ground_plane(prim_path="/World/GroundPlane", cfg=GroundPlaneCfg())
        self.scene.clone_environments(copy_from_source=False)
        if self.device == "cpu":
            self.scene.filter_collisions(global_prim_paths=[])
        self.scene.articulations["robot"] = self.robot
        sim_utils.DomeLightCfg(intensity=2000.0, color=(0.75,)*3).func("/World/Light", sim_utils.DomeLightCfg(intensity=2000.0, color=(0.75,)*3))

    # --- RL pipeline ---
    def _pre_physics_step(self, actions):
        self.actions = actions.clone()
        self._push_timer += 1
        self._apply_random_pushes()

    def _apply_action(self):
        target = self.robot.data.default_joint_pos + self.actions * self.cfg.action_scale
        target = torch.clamp(target,
                             self.robot.data.soft_joint_pos_limits[:, :, 0],
                             self.robot.data.soft_joint_pos_limits[:, :, 1])
        self.robot.set_joint_position_target(target, joint_ids=self._joint_ids)
        self._previous_actions = self.actions.clone()

    def _get_observations(self):
        lf = self.robot.data.body_pos_w[:, self._left_foot[0]]
        rf = self.robot.data.body_pos_w[:, self._right_foot[0]]
        feet_d = torch.norm(lf[:, :2] - rf[:, :2], dim=-1, keepdim=True)
        obs = torch.cat([
            self.robot.data.projected_gravity_b,
            self.robot.data.root_ang_vel_b,
            self.robot.data.root_lin_vel_b,
            self.robot.data.joint_pos - self.robot.data.default_joint_pos,
            self.robot.data.joint_vel,
            self._previous_actions,
            feet_d,
        ], dim=-1)
        return {"policy": obs}

    def _get_rewards(self):
        # -> doc 02 §4 / código completo en codigos/standing/r1_standing_env.py
        ...

    def _get_dones(self):
        time_out = self.episode_length_buf >= self.max_episode_length - 1
        h = self.robot.data.root_pos_w[:, 2]
        fallen_h = h < 0.3
        proj_g = self.robot.data.projected_gravity_b
        fallen_t = torch.sum(torch.square(proj_g[:, :2]), dim=-1) > 0.5
        return fallen_h | fallen_t, time_out

    def _reset_idx(self, env_ids: Sequence[int] | None):
        if env_ids is None:
            env_ids = self.robot._ALL_INDICES
        super()._reset_idx(env_ids)
        jp = self.robot.data.default_joint_pos[env_ids].clone()
        jv = self.robot.data.default_joint_vel[env_ids].clone()
        root = self.robot.data.default_root_state[env_ids]
        root[:, :3] += self.scene.env_origins[env_ids]
        root[:, 2]   = self.cfg.initial_base_height
        self._push_timer[env_ids] = 0.0
        self._previous_actions[env_ids] = 0.0
        self.robot.write_root_pose_to_sim(root[:, :7], env_ids)
        self.robot.write_root_velocity_to_sim(root[:, 7:], env_ids)
        self.robot.write_joint_state_to_sim(jp, jv, None, env_ids)
```

> El archivo completo y corregido está en [`codigos/standing/r1_standing_env.py`](./codigos/standing/r1_standing_env.py).

---

## 6. Push system (corregido)

El repo original usa `self.robot.instantaneous_wrench_composer.set_forces_and_torques(...)` — **esa API no existe** en Isaac Lab moderno y rompe el script. La forma correcta:

```python
def _apply_random_pushes(self):
    env_ids = (self._push_timer >= self.push_interval).nonzero(as_tuple=False).flatten()
    if len(env_ids) == 0:
        return

    forces  = torch.zeros((len(env_ids), 1, 3), device=self.device)
    torques = torch.zeros((len(env_ids), 1, 3), device=self.device)

    forces[:, 0, 0] = torch.empty(len(env_ids), device=self.device).uniform_(
        self.cfg.push_force_min, self.cfg.push_force_max)
    forces[:, 0, 1] = torch.empty(len(env_ids), device=self.device).uniform_(
        self.cfg.push_force_min, self.cfg.push_force_max)
    signs = torch.randint(0, 2, (len(env_ids), 2), device=self.device) * 2 - 1
    forces[:, 0, :2] *= signs

    # API correcta: set_external_force_and_torque
    self.robot.set_external_force_and_torque(
        forces=forces,
        torques=torques,
        body_ids=[self._root_body_id],
        env_ids=env_ids,
    )
    self._push_timer[env_ids] = 0
```

Documentado y aplicado en [doc 10](./10_Correcciones_Aplicadas.md) y en [`codigos/standing/r1_standing_env.py`](./codigos/standing/r1_standing_env.py).

---

## 7. Registro Gym

En `tasks/direct/r1_standing/__init__.py`:

```python
import gymnasium as gym
from . import agents

gym.register(
    id="R1Standing-Direct-v0",
    entry_point=f"{__name__}.r1_standing_env:R1StandingEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point":     f"{__name__}.r1_standing_env_cfg:R1StandingEnvCfg",
        "rsl_rl_cfg_entry_point":  f"{agents.__name__}.rsl_rl_ppo_cfg:PPORunnerCfg",
        "skrl_cfg_entry_point":    f"{agents.__name__}:skrl_ppo_cfg.yaml",
    },
)
```

Y en `r1_standing/__init__.py` (paquete root) hay que importar `tasks` para que el registro corra al hacer `import r1_standing`. Si no, `gym.make` no encontrará la tarea.

```python
# source/r1_standing/r1_standing/__init__.py
from . import tasks  # noqa: F401
```

---

## 8. Hiperparámetros PPO base (RSL-RL)

```python
# agents/rsl_rl_ppo_cfg.py
class PPORunnerCfg(RslRlOnPolicyRunnerCfg):
    num_steps_per_env = 24
    max_iterations    = 4000
    save_interval     = 500
    experiment_name   = "r1_standing"
    obs_groups        = {"actor": ["policy"], "critic": ["policy"]}

    policy = RslRlPpoActorCriticCfg(
        init_noise_std=1.0,
        actor_obs_normalization=False,
        critic_obs_normalization=False,
        actor_hidden_dims=[256, 128, 64],
        critic_hidden_dims=[256, 128, 64],
        activation="elu",
    )
    algorithm = RslRlPpoAlgorithmCfg(
        value_loss_coef=1.0,
        use_clipped_value_loss=True,
        clip_param=0.2,
        entropy_coef=0.005,
        num_learning_epochs=5,
        num_mini_batches=4,
        learning_rate=1.0e-3,
        schedule="adaptive",
        gamma=0.99,
        lam=0.95,
        desired_kl=0.01,
        max_grad_norm=1.0,
    )
```

Sentido de cada hiperparámetro:

| Param | Valor | Por qué |
|------|------:|---------|
| `num_steps_per_env` | 24 | Rollout corto → updates frecuentes; tareas reactivas como standing prefieren 24–32. |
| `max_iterations` | 4000 | Suficiente para *standing*. Para push-recovery subir a 15000. |
| `actor/critic_hidden_dims` | [256,128,64] | Profundidad media — captura simetrías del cuerpo sin sobreajuste. |
| `entropy_coef` | 0.005 | Bajo: la tarea es determinista, no queremos exploración alta. |
| `learning_rate` | 1e-3 + `schedule="adaptive"` | KL-adaptive auto-baja el LR si la KL diverge → estable. |
| `desired_kl` | 0.01 | Target KL clásico de PPO. |
| `gamma` | 0.99 | Episodios de 20 s × 60 Hz = horizonte largo. |

---

## 9. Lanzar el entrenamiento

```powershell
.\..\IsaacLab\isaaclab.bat -p .\scripts\rsl_rl\train.py `
  --task=R1Standing-Direct-v0 `
  --num_envs=4096 `
  --max_iterations=4000 `
  --headless
```

Logs en `logs/rsl_rl/r1_standing/<timestamp>/`. TensorBoard:

```powershell
tensorboard --logdir logs/rsl_rl/r1_standing
```

---

## 10. Anti-patrones comunes

- **No usar `Manager-based`** para tareas con observaciones tan personalizadas y curriculum interno — *Direct* da más control.
- **No mezclar SKRL y RSL-RL** en el mismo run; cada uno escribe en su propio subdirectorio (`logs/rsl_rl/...` y `logs/skrl/...`) pero los formatos de checkpoint no son intercambiables.
- **No declarar `observation_space`** y luego concatenar dims que no sumen. Si en `_get_observations` produces 91 dims pero `observation_space=88`, PPO crashea.
- **No subir `action_scale` antes de tener una política estable**. Empezar en 0.025 y solo subir tras ver curvas de reward suaves.

Próximo paso → [03_Politica_Padre_Jerarquica.md](./03_Politica_Padre_Jerarquica.md).
