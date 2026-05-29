# 06 — Playground con escaleras y terrenos para test

> Objetivo: tener un entorno donde probar la política con **escaleras, slopes, terreno irregular y gaps**, además de la versión plana de los entrenamientos previos. Isaac Lab incluye `TerrainImporterCfg` que permite construir todo esto de forma procedural.

---

## 1. ¿Por qué un terreno con curriculum?

Dejar al R1 entrenar en plano y luego enfrentarlo a escaleras = **caída inmediata**. La forma correcta:

1. **Generar tipos de terreno** (escaleras, rugoso, slopes, gaps, plano).
2. **Asignar dificultad creciente** (escaleras altas 0.05 m → 0.20 m, slopes 5° → 30°).
3. **Promover envs cuando lo dominan** (paper [arXiv 2209.12827]: *"learn locomotion and local navigation end-to-end"*).

Isaac Lab implementa esto de forma nativa con `TerrainGeneratorCfg`.

---

## 2. Construcción del playground

### 2.1 Escaleras (pyramid stairs)

```python
# codigos/playground/stairs_terrain_cfg.py
from isaaclab.terrains import TerrainImporterCfg, TerrainGeneratorCfg
from isaaclab.terrains.config.rough import HfPyramidStairsTerrainCfg, HfInvertedPyramidStairsTerrainCfg

PYRAMID_STAIRS_CFG = HfPyramidStairsTerrainCfg(
    proportion=0.4,
    border_width=1.0,
    horizontal_scale=0.1,
    vertical_scale=0.005,
    slope_threshold=0.75,
    step_height_range=(0.05, 0.20),     # ← curriculum: empieza bajo
    step_width=0.30,
    platform_width=2.0,
    holes=False,
)

INVERTED_PYRAMID_STAIRS_CFG = HfInvertedPyramidStairsTerrainCfg(
    proportion=0.2,
    border_width=1.0,
    step_height_range=(0.05, 0.20),
    step_width=0.30,
    platform_width=2.0,
    holes=False,
)
```

### 2.2 Terreno rugoso, slopes, gaps

```python
from isaaclab.terrains.config.rough import (
    HfDiscreteObstaclesTerrainCfg,
    HfRandomUniformTerrainCfg,
    HfPyramidSlopedTerrainCfg,
    MeshGapTerrainCfg,
)

ROUGH_TERRAIN_CFG = HfRandomUniformTerrainCfg(
    proportion=0.2,
    horizontal_scale=0.1,
    vertical_scale=0.005,
    border_width=0.25,
    noise_range=(0.02, 0.10),
    noise_step=0.02,
)

SLOPE_CFG = HfPyramidSlopedTerrainCfg(
    proportion=0.1,
    slope_range=(0.0, 0.4),  # rad ≈ 0–22°
    border_width=0.25,
    platform_width=2.0,
)

GAP_CFG = MeshGapTerrainCfg(
    proportion=0.05,
    gap_width_range=(0.05, 0.30),
    platform_width=2.0,
)

OBSTACLES_CFG = HfDiscreteObstaclesTerrainCfg(
    proportion=0.05,
    horizontal_scale=0.1,
    vertical_scale=0.005,
    obstacle_height_range=(0.05, 0.20),
    obstacle_width_range=(0.10, 0.30),
    num_obstacles=10,
    border_width=0.25,
    platform_width=2.0,
)
```

### 2.3 Generador agregado

```python
TERRAIN_GENERATOR_CFG = TerrainGeneratorCfg(
    seed=0,
    size=(8.0, 8.0),     # tamaño de cada sub-terreno
    border_width=20.0,
    num_rows=10,         # 10 niveles de dificultad
    num_cols=20,         # 20 sub-terrenos por dificultad
    horizontal_scale=0.1,
    vertical_scale=0.005,
    slope_threshold=0.75,
    use_cache=False,
    sub_terrains={
        "pyramid_stairs":          PYRAMID_STAIRS_CFG,
        "inverted_pyramid_stairs": INVERTED_PYRAMID_STAIRS_CFG,
        "rough":                   ROUGH_TERRAIN_CFG,
        "slope":                   SLOPE_CFG,
        "gap":                     GAP_CFG,
        "obstacles":               OBSTACLES_CFG,
    },
    curriculum=True,    # ← clave: las filas representan dificultad
)

PLAYGROUND_TERRAIN_CFG = TerrainImporterCfg(
    prim_path="/World/ground",
    terrain_type="generator",
    terrain_generator=TERRAIN_GENERATOR_CFG,
    max_init_terrain_level=5,           # spawnea en filas 0..5 al inicio
    collision_group=-1,
    physics_material=sim_utils.RigidBodyMaterialCfg(
        friction_combine_mode="multiply",
        restitution_combine_mode="multiply",
        static_friction=1.0,
        dynamic_friction=1.0,
    ),
    debug_vis=False,
)
```

> Las **filas** del generador = niveles de dificultad. Las **columnas** = variantes con la misma dificultad. Isaac Lab promueve un env a la fila siguiente cuando supera el `goal_reach_threshold`. Esto es el curriculum automático.

---

## 3. Engancharlo al EnvCfg

```python
# r1_locomotion_env_cfg.py (o derivative)
from isaaclab.scene import InteractiveSceneCfg
from .playground.stairs_terrain_cfg import PLAYGROUND_TERRAIN_CFG

@configclass
class R1LocomotionPlaygroundEnvCfg(R1LocomotionEnvCfg):
    scene: InteractiveSceneCfg = InteractiveSceneCfg(
        num_envs=4096,
        env_spacing=8.0,
        replicate_physics=True,
        terrain=PLAYGROUND_TERRAIN_CFG,   # ← terrain en la escena
    )
```

Y en `_setup_scene` del env, **eliminar** el `spawn_ground_plane` — ya no aplica:

```python
def _setup_scene(self):
    self.robot = Articulation(self.cfg.robot_cfg)
    # NO: spawn_ground_plane(...)
    self.scene.terrain = self.cfg.scene.terrain  # se importa automáticamente
    self.scene.clone_environments(copy_from_source=False)
    ...
```

---

## 4. Curriculum dinámico (env-based)

Para que cada env *suba de fila* cuando lo supera:

```python
# En _reset_idx, después del super().reset:
def _update_terrain_levels(self, env_ids):
    if not hasattr(self.scene, "terrain"):
        return
    # Si caminó >50% del sub-terreno → sube de nivel
    distance_walked = torch.norm(
        self.robot.data.root_pos_w[env_ids, :2] -
        self._init_pos[env_ids, :2], dim=-1
    )
    move_up   = distance_walked > self.cfg.scene.terrain.cfg.size[0] / 2
    move_down = distance_walked < self.cfg.scene.terrain.cfg.size[0] / 4
    self.scene.terrain.update_env_origins(env_ids, move_up, move_down)
```

> El método `update_env_origins` ya está en `TerrainImporter` de Isaac Lab y reasigna el origen del env al terrain de la fila siguiente/anterior.

---

## 5. Heightmap sensor (lo necesita la política)

Como mencionamos en [doc 05 §7](./05_Path_Coordenadas_Velocidad.md), el robot necesita un **RayCaster** para "ver" el terreno y modular su velocidad:

```python
# en R1LocomotionPlaygroundEnvCfg
height_scanner: RayCasterCfg = RayCasterCfg(
    prim_path="/World/envs/env_.*/R1/torso",
    update_period=1/50.0,
    offset=RayCasterCfg.OffsetCfg(pos=(0.0, 0.0, 1.0)),
    attach_yaw_only=True,
    pattern_cfg=patterns.GridPatternCfg(
        resolution=0.1,
        size=(1.6, 1.0),  # frente 1.6 m, ancho 1.0 m
    ),
    debug_vis=False,
    mesh_prim_paths=["/World/ground"],
)
```

Esto añade ~150 dims a la observación (16×10 grid). Modifica `observation_space` accordingly.

---

## 6. Comandos para entrenar en playground

### Etapa A — Plano (resume del run de standing)

```powershell
... train.py --task=R1-Locomotion-Direct-v0 --num_envs=4096 --max_iterations=4000 --headless
```

### Etapa B — Playground sin escaleras (rough + slope)

```powershell
... train.py --task=R1-Locomotion-Playground-Direct-v0 --num_envs=4096 --max_iterations=8000 --resume --load_run=<runA>
```

### Etapa C — Playground completo con escaleras

```powershell
... train.py --task=R1-Locomotion-Playground-Stairs-Direct-v0 --num_envs=4096 --max_iterations=15000 --resume --load_run=<runB>
```

Las tres tareas comparten `R1LocomotionEnv` con distintos `EnvCfg` (cambia solo `scene.terrain` y, en C, el `proportion` de pyramid_stairs).

---

## 7. Probar el playground manualmente

```powershell
.\..\IsaacLab\isaaclab.bat -p .\scripts\rsl_rl\play.py `
  --task=R1-Locomotion-Playground-Stairs-Direct-v0 `
  --num_envs=2 `
  --checkpoint=D:\...\model_15000.pt
```

O con control manual (teclado):

```powershell
.\..\IsaacLab\isaaclab.bat -p play_wasd.py `
  --task=R1-Locomotion-Playground-Stairs-Direct-v0 `
  --checkpoint=D:\...\model_15000.pt `
  --step=0.5
```

Y mover el target hacia las escaleras para verificar que sube y baja sin caer.

---

## 8. Métricas extra para el playground

```
TerrainLevel/mean         ← nivel medio de dificultad alcanzado
TerrainLevel/max          ← nivel máximo
Reward / rew_terrain_clear ← (opcional) custom reward por superar terreno
Foot_clearance / mean     ← altura media del paso (relevante para escaleras)
```

`Foot_clearance` se calcula como:

```python
foot_h = torch.stack([self.robot.data.body_pos_w[:, lf, 2],
                      self.robot.data.body_pos_w[:, rf, 2]], dim=-1)
foot_clearance = (foot_h - self._terrain_height_under_foot).max(dim=-1).values
```

> Para escaleras de 0.20 m, la `foot_clearance` debe llegar a ≥ 0.22 m de forma consistente.

---

## 9. Anti-patrones

- **No mezclar terreno con `replicate_physics=False`** — Isaac Lab espera replicate_physics=True para `terrain="generator"`.
- **No olvidar `mesh_prim_paths`** del RayCaster con `/World/ground` — sin eso el ray no detecta nada.
- **No subir directamente a `step_height_range=(0.20, 0.30)`** sin curriculum — el robot no aprende a flexionar la rodilla; usa filas progresivas.
- **No usar `env_spacing` pequeño con terrain.size=8** — los envs se solapan. Mantén `env_spacing >= size + border_width`.

Próximo paso → [07_Codigos_Train_Play.md](./07_Codigos_Train_Play.md).
