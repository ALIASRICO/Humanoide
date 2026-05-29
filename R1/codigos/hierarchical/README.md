# Política madre (HRL) — uso

Diagrama y filosofía → ver [doc 03](../../03_Politica_Padre_Jerarquica.md).

## Archivos

- `__init__.py` — registra `R1-Hierarchical-Direct-v0` en Gym.
- `high_level_planner.py` — `HighLevelPolicy` (MLP madre), `FrozenChild` (wrapper hijas), `FSMHighLevel` (alternativa determinista).
- `hierarchical_env.py` — env Direct que carga las hijas y mezcla acciones.

## Pre-requisitos

1. Tener entrenadas las dos hijas:
   - `r1_standing` → `D:\space_r1\IsaacLab\logs\rsl_rl\r1_standing\<run>\model_*.pt`
   - `r1_locomotion` → `D:\space_r1\IsaacLab\logs\rsl_rl\r1_locomotion\<run>\model_*.pt`
2. Editar `R1HierarchicalEnvCfg.stand_ckpt` y `R1HierarchicalEnvCfg.walk_ckpt` en `hierarchical_env.py`.

## Train

```powershell
.\..\IsaacLab\isaaclab.bat -p .\scripts\rsl_rl\train.py `
  --task=R1-Hierarchical-Direct-v0 `
  --num_envs=2048 `
  --max_iterations=5000 `
  --seed=42 `
  --headless
```

## Play

```powershell
.\..\IsaacLab\isaaclab.bat -p .\scripts\rsl_rl\play.py `
  --task=R1-Hierarchical-Direct-v0 `
  --num_envs=2 `
  --real-time
```

## Usar la FSM determinista (sin entrenar madre)

Si no quieres entrenar la madre, usa `FSMHighLevel` en `play_wasd.py` modificado:

```python
from r1_hierarchical.high_level_planner import FSMHighLevel
fsm = FSMHighLevel(arrival_threshold=0.3)
skill, cmd = fsm.step(target_xy, robot_xy, is_falling, is_on_stairs)
# Selecciona la hija según `skill` y aplica la acción.
```

## Notas

- La madre solo actualiza su acción cada `high_level_period = 10` steps (≈10 Hz). Las hijas operan a 50 Hz.
- El gating es **soft** (sigmoid α). Para hard switch, redondear α a {0,1}.
- El `rew_skill_persist` evita oscilación STAND↔WALK.
