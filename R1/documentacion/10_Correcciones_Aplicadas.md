# 10 — Correcciones aplicadas a los repos originales

> Lista exhaustiva de bugs/inconsistencias/typos detectados en `r1_standing` y `space_r1` y la corrección aplicada en este snapshot. Cada entrada indica: **dónde**, **qué pasaba**, **qué se hace**, **archivo de la doc/código** con la versión correcta.

---

## 1. API obsoleta: `instantaneous_wrench_composer`

### Dónde
`source/r1_standing/r1_standing/tasks/direct/r1_standing/r1_standing_env.py` → `_apply_random_pushes`.

### Problema
```python
self.robot.instantaneous_wrench_composer.set_forces_and_torques(
    forces=forces, torques=torques, body_ids=[self._root_body_id], env_ids=env_ids
)
```
**Esa API no existe** en `Articulation` de Isaac Lab actual. Provoca `AttributeError: 'Articulation' object has no attribute 'instantaneous_wrench_composer'` la primera vez que `push_timer >= push_interval` (típicamente al segundo de simulación).

### Fix
Usar la API soportada `set_external_force_and_torque(...)`:

```python
self.robot.set_external_force_and_torque(
    forces=forces,
    torques=torques,
    body_ids=[self._root_body_id],
    env_ids=env_ids,
)
self.robot.write_data_to_sim()
```

### Aplicado en
- [doc 02 §6](./02_Crear_Politica_Basica.md)
- [`codigos/standing/r1_standing_env.py`](./codigos/standing/r1_standing_env.py)

---

## 2. Inconsistencia en el `task_id`

### Dónde
`commands.md` referencia `Template-R1-Prueba-Direct-v0`, pero el `__init__.py` registra `R1Standing-Direct-v0`. El `list_envs.py` filtra por `"Template-"` en `task_spec.id`.

### Problema
- Si se mantiene `R1Standing-Direct-v0`, **no aparece en `list_envs.py`** (no contiene "Template-").
- Si se cambia el id a `Template-...`, no coincide con el README ni con commands.

### Fix
1. **Cambiar el filtro** en `scripts/list_envs.py`:
   ```python
   if "R1" in task_spec.id and (args_cli.keyword is None or args_cli.keyword in task_spec.id):
   ```
2. **Estandarizar** todas las docs/comandos a `R1Standing-Direct-v0` (es el id real registrado).
3. Marcar `Template-R1-Prueba-Direct-v0` como deprecated.

### Aplicado en
- [doc 01 §6.1](./01_Instalacion_Windows.md)
- [doc 07](./07_Codigos_Train_Play.md) — todas las recetas usan `R1Standing-Direct-v0`.
- [`codigos/scripts/`](./codigos/scripts/) — `list_envs.py` con el filtro correcto.

---

## 3. Posible falta de `R1_CFG` en `isaaclab_assets`

### Dónde
`r1_standing_env_cfg.py`:
```python
from isaaclab_assets.robots.r1 import R1_CFG
```

### Problema
Algunas releases de Isaac Lab **no incluyen** el R1 (es un robot relativamente nuevo). El import falla con `ModuleNotFoundError: No module named 'isaaclab_assets.robots.r1'` o `ImportError: cannot import name 'R1_CFG'`.

### Fix
Crear localmente el cfg si no existe. Añadir al inicio de `r1_standing_env_cfg.py`:

```python
try:
    from isaaclab_assets.robots.r1 import R1_CFG
except (ImportError, ModuleNotFoundError):
    import os
    import isaaclab.sim as sim_utils
    from isaaclab.actuators import ImplicitActuatorCfg
    from isaaclab.assets import ArticulationCfg

    _USD = os.environ.get("R1_USD_PATH",
        r"D:\space_r1\IsaacLab\source\isaaclab_assets\data\Robots\Unitree\R1\r1.usd"
    )

    R1_CFG = ArticulationCfg(
        spawn=sim_utils.UsdFileCfg(
            usd_path=_USD,
            activate_contact_sensors=True,
            rigid_props=sim_utils.RigidBodyPropertiesCfg(
                disable_gravity=False,
                retain_accelerations=False,
                linear_damping=0.0,
                angular_damping=0.0,
                max_linear_velocity=1000.0,
                max_angular_velocity=1000.0,
                max_depenetration_velocity=1.0,
            ),
            articulation_props=sim_utils.ArticulationRootPropertiesCfg(
                enabled_self_collisions=False,
                solver_position_iteration_count=8,
                solver_velocity_iteration_count=4,
            ),
        ),
        init_state=ArticulationCfg.InitialStateCfg(
            pos=(0.0, 0.0, 0.78),
            joint_pos={".*": 0.0},
        ),
        actuators={
            "all": ImplicitActuatorCfg(
                joint_names_expr=[".*"],
                stiffness=80.0,
                damping=2.0,
            ),
        },
    )
```

Y asegurar que `r1.usd` está en la ruta esperada (copiarlo desde `D:\space_r1\r1.usd`).

### Aplicado en
- [doc 01 §7](./01_Instalacion_Windows.md)
- [doc 08 §4](./08_Mapa_Rutas_Importantes.md)
- [`codigos/standing/r1_standing_env_cfg.py`](./codigos/standing/r1_standing_env_cfg.py) — versión defensiva.

---

## 4. Comentario de obs incorrecto en cfg

### Dónde
`r1_standing_env_cfg.py`:
```python
observation_space = 26 * 2 + 3 + 3 + 3 + 26 + 1  # 88 = gravity(3) + ang_vel(3) + lin_vel(3) + joint_pos(26) + joint_vel(26) + prev_actions(26) + feet_distance(1)
```

### Problema
La cuenta es correcta (88) pero el comentario lista 7 bloques y la suma da 26+26+26+3+3+3+1 = 88. La fórmula `26*2 + 3+3+3+26+1` da 52+9+27 = 88 también. **Son equivalentes pero la fórmula es confusa**.

### Fix
Reescribir como:
```python
observation_space = 3 + 3 + 3 + 26 + 26 + 26 + 1  # = 88
# = projected_gravity(3) + root_ang_vel(3) + root_lin_vel(3)
# + joint_pos_dev(26) + joint_vel(26) + prev_actions(26)
# + feet_distance(1)
```

### Aplicado en
- [`codigos/standing/r1_standing_env_cfg.py`](./codigos/standing/r1_standing_env_cfg.py)

---

## 5. SKRL config: `experiment.directory` heredado del template

### Dónde
`agents/skrl_ppo_cfg.yaml`:
```yaml
agent:
  experiment:
    directory: "cartpole_direct"
```

### Problema
Es leftover del template original. Crea logs en `cartpole_direct/` en vez de `r1_standing/`.

### Fix
```yaml
agent:
  experiment:
    directory: "r1_standing"
```

### Aplicado en
- [`codigos/agents/skrl_ppo_cfg.yaml`](./codigos/agents/skrl_ppo_cfg.yaml)

---

## 6. SKRL config: `layers: [32, 32]` insuficiente para R1

### Dónde
`agents/skrl_ppo_cfg.yaml` policy/value networks → `layers: [32, 32]`.

### Problema
Para 26 DOF y 88 obs, una red `[32, 32]` es **subdimensionada**. El RSL-RL del mismo proyecto usa `[256, 128, 64]`. El SKRL queda inferior y no aprende a la misma velocidad.

### Fix
```yaml
network:
  - name: net
    input: OBSERVATIONS
    layers: [256, 128, 64]
    activations: elu
```

### Aplicado en
- [`codigos/agents/skrl_ppo_cfg.yaml`](./codigos/agents/skrl_ppo_cfg.yaml)

---

## 7. SKRL: `timesteps: 4800` muy bajo

### Dónde
`agents/skrl_ppo_cfg.yaml`:
```yaml
trainer:
  timesteps: 4800
```

### Problema
4800 timesteps totales = ~25 iteraciones, insuficiente para standing. RSL-RL tiene `max_iterations=4000`.

### Fix
Subir a `timesteps: 96000` (≈4000 iters × 24 steps_per_env) o más.

```yaml
trainer:
  timesteps: 96000
```

### Aplicado en
- [`codigos/agents/skrl_ppo_cfg.yaml`](./codigos/agents/skrl_ppo_cfg.yaml)

---

## 8. `play_wasd.py` no busca checkpoints en otras rutas

### Dónde
`space_r1/play_wasd.py` → `find_latest_checkpoint`:
```python
search_roots = [
    os.path.join("IsaacLab", "logs", "rsl_rl"),
    os.path.join("logs", "rsl_rl"),
]
```

### Problema
Si el run vive en `D:\space_r1\IsaacLab\logs\rsl_rl\...` y se ejecuta `play_wasd.py` desde `D:\space_r1\`, el path relativo "IsaacLab\logs\rsl_rl" funciona pero falla si se invoca desde otro cwd. Además solo busca `r1_locomotion*` por glob.

### Fix
Aceptar también path absoluto y buscar todas las experiments:

```python
def find_latest_checkpoint() -> str | None:
    search_globs = [
        os.path.join("IsaacLab", "logs", "rsl_rl", "*", "*", "model_*.pt"),
        os.path.join("logs", "rsl_rl", "*", "*", "model_*.pt"),
        os.path.join(os.environ.get("ISAACLAB", "."), "logs", "rsl_rl", "*", "*", "model_*.pt"),
    ]
    candidates = []
    for g in search_globs:
        candidates.extend(glob.glob(g))
    if candidates:
        candidates.sort(key=os.path.getmtime)
        return candidates[-1]
    return None
```

### Aplicado en
- [`codigos/scripts/play_wasd.py`](./codigos/scripts/play_wasd.py)

---

## 9. `play_wasd.py` importa `r1_locomotion.tasks` que no existe en repos públicos

### Dónde
```python
import r1_locomotion.tasks  # noqa
```

### Problema
La carpeta `space_r1/r1_locomotion` está vacía en GitHub (no se subió el contenido). El import falla.

### Fix
Hacer el import opcional:

```python
try:
    import r1_locomotion.tasks  # noqa: F401
except ImportError:
    try:
        import r1_standing.tasks  # noqa: F401
    except ImportError:
        print("[WARN] No se encontró r1_locomotion ni r1_standing. Asegura `pip install -e source/...`")
```

Y dejar el `--task` por defecto en el que el usuario tenga registrado.

### Aplicado en
- [`codigos/scripts/play_wasd.py`](./codigos/scripts/play_wasd.py)

---

## 10. `r1_standing_env.py`: bug en cálculo de fuerzas

### Dónde
```python
forces[:, 0, 0] = torch.rand(len(env_ids), device=self.device) * (
    self.cfg.push_force_max - self.cfg.push_force_min
) + self.cfg.push_force_min
```

### Problema
La magnitud de fuerza configurada (`push_force_min=0.02`, `push_force_max=0.03`) es **micro-Newton**, ridículamente baja. El comentario habla de "etapa 1: pushes OFF" pero la fuerza está activada con valores mínimos. Inconsistente.

### Fix
- Para "OFF": poner `push_interval_s = 1e9` (efectivamente nunca).
- Para etapas reales:
  - **Etapa 3 (push recovery)**: `push_force_min=5.0`, `push_force_max=10.0`.
  - **Etapa 4 (stepping)**: `push_force_min=15.0`, `push_force_max=25.0`.

### Aplicado en
- [doc 04 §3](./04_Fine_Tuning.md)
- [`codigos/standing/r1_standing_env_cfg.py`](./codigos/standing/r1_standing_env_cfg.py)

---

## 11. Reward final dividido por 10 sin documentar

### Dónde
Final de `compute_rewards` en `r1_standing_env.py`:
```python
return total_reward * 0.1
```

### Problema
La escala 0.1 está hard-codeada — debería ser un hiperparámetro (`reward_scale`) o documentarse explícitamente.

### Fix
- Documentarlo: el `0.1` es el **reward_shaper_scale** (también llamado *reward shaping factor*); SKRL lo expone como `rewards_shaper_scale: 0.1`.
- Mantener consistencia: si se cambia, ajustar también el SKRL yaml.

### Aplicado en
- [`codigos/standing/r1_standing_env.py`](./codigos/standing/r1_standing_env.py) — ahora `total_reward * cfg.reward_shaper_scale` con `reward_shaper_scale=0.1` por defecto.

---

## 12. `_apply_action`: `action_scale` muy alta puede saturar

### Dónde
`r1_standing_env_cfg.py`:
```python
action_scale = 0.025
```

### Problema
Con 26 joints y `action ∈ [-1,1]`, el scale 0.025 da target ±0.025 rad ≈ ±1.4°. Para *stand still* funciona, pero para locomoción lo pondrás en 0.5–1.0. Si subes esto sin documentar, la política diverge.

### Fix
- Documentar que `action_scale` es **per-task**: 0.025 para standing, 0.5 para locomotion.
- Añadir `action_scale_locomotion = 0.5` en cfg si se reusa el env.

### Aplicado en
- [doc 02 §3](./02_Crear_Politica_Basica.md)
- [`codigos/standing/r1_standing_env_cfg.py`](./codigos/standing/r1_standing_env_cfg.py)
- [`codigos/locomotion/r1_locomotion_env_cfg.py`](./codigos/locomotion/r1_locomotion_env_cfg.py)

---

## 13. `_setup_scene`: `DomeLightCfg` instanciado dos veces

### Dónde
`r1_standing_env.py`:
```python
light_cfg = sim_utils.DomeLightCfg(intensity=2000.0, color=(0.75, 0.75, 0.75))
light_cfg.func("/World/Light", light_cfg)
```

### Problema
`light_cfg.func(...)` es válido, pero la convención correcta de Isaac Lab es:

```python
sim_utils.DomeLightCfg(intensity=2000.0, color=(0.75,)*3).func("/World/Light", sim_utils.DomeLightCfg(intensity=2000.0, color=(0.75,)*3))
```

…que está peor escrito. La forma idiomática:

### Fix
```python
def _setup_scene(self):
    self.robot = Articulation(self.cfg.robot_cfg)
    spawn_ground_plane(prim_path="/World/GroundPlane", cfg=GroundPlaneCfg())
    self.scene.clone_environments(copy_from_source=False)
    if self.device == "cpu":
        self.scene.filter_collisions(global_prim_paths=[])
    self.scene.articulations["robot"] = self.robot

    # Iluminación — patrón estándar Isaac Lab
    light_cfg = sim_utils.DomeLightCfg(intensity=2000.0, color=(0.75, 0.75, 0.75))
    light_cfg.func("/World/Light", light_cfg)
```

### Aplicado en
- [`codigos/standing/r1_standing_env.py`](./codigos/standing/r1_standing_env.py)

---

## 14. Falta `__init__.py` en root del paquete que importa `tasks`

### Dónde
`source/r1_standing/r1_standing/__init__.py` — vacío en algunos snapshots.

### Problema
Si no contiene `from . import tasks`, los `gym.register(...)` no se ejecutan al `import r1_standing`, y `gym.make("R1Standing-Direct-v0")` lanza `gym.error.UnregisteredEnv`.

### Fix
```python
# source/r1_standing/r1_standing/__init__.py
from . import tasks  # noqa: F401
```

### Aplicado en
- [doc 02 §7](./02_Crear_Politica_Basica.md)
- [`codigos/standing/__init__.py`](./codigos/standing/__init__.py)

---

## 15. `revisionEntrenamiento.md`: typos de texto (no funcional)

| Original | Corregido |
|---------|-----------|
| "Trainging" | "Training" |
| "antinatural" | (es válido — "anti-natural") |
| "iteracino" | "iteración" |
| "Heirarchical" | "Hierarchical" |
| "High-level Policys" | "High-level Policies" |
| "Capas de detenerse" | "Capaz de detenerse" |
| "estbilidad" | "estabilidad" |
| "reonomiento" | "reconocimiento" |

### Aplicado en
- [doc 03](./03_Politica_Padre_Jerarquica.md) — todos los textos pasan por revisión ortográfica.

---

## Resumen — checklist de aplicación

- [x] §1  push API → `set_external_force_and_torque`
- [x] §2  task ID consistente `R1Standing-Direct-v0`
- [x] §3  fallback `R1_CFG` defensivo
- [x] §4  comentario de obs claro
- [x] §5  SKRL `experiment.directory = "r1_standing"`
- [x] §6  SKRL hidden_dims = [256,128,64]
- [x] §7  SKRL `timesteps = 96000`
- [x] §8  `play_wasd.py` busca en más rutas
- [x] §9  imports opcionales en `play_wasd.py`
- [x] §10 fuerzas de push en N reales
- [x] §11 `reward_shaper_scale` documentado
- [x] §12 `action_scale` per-task
- [x] §13 `_setup_scene` idiomático
- [x] §14 `__init__.py` importa `tasks`
- [x] §15 typos corregidos

Todas las correcciones se aplican en los archivos de [`codigos/`](./codigos/) y se reflejan en los demás documentos.
