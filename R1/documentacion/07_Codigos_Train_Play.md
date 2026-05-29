# 07 — Códigos de entrenamiento y reproducción (`train.py` / `play.py`)

> Recetario operacional. Para cada escenario tienes el comando exacto, los flags, qué se loguea y qué esperar.

Todos los comandos asumen que estás en `D:\space_r1\r1_standing\` con el conda env `env_isaaclab` activo.

---

## 1. Estructura de los scripts

```
D:\space_r1\r1_standing\scripts\
├─ list_envs.py           ← lista las tareas registradas
├─ random_agent.py        ← dummy: acciones aleatorias
├─ zero_agent.py          ← dummy: acciones a cero
├─ rsl_rl\
│   ├─ cli_args.py        ← flags compartidos (--resume, --checkpoint, etc.)
│   ├─ train.py           ← entrenar PPO con RSL-RL (recomendado)
│   └─ play.py            ← reproducir checkpoint, exporta JIT/ONNX
└─ skrl\
    ├─ train.py           ← entrenar con SKRL
    └─ play.py            ← reproducir con SKRL
```

> Las versiones limpias y comentadas están en [`codigos/scripts/`](./codigos/scripts/) de esta documentación.

---

## 2. Flags comunes (RSL-RL)

| Flag | Default | Descripción |
|------|---------|-------------|
| `--task` | — | ID Gym (ej. `R1Standing-Direct-v0`). |
| `--num_envs` | (env cfg) | nº de envs paralelos. |
| `--max_iterations` | (agent cfg) | iters PPO totales. |
| `--seed` | None | semilla. `-1` aleatoria. |
| `--headless` | False | sin GUI (entrenamiento). |
| `--device` | `cuda:0` | `cpu` para debug. |
| `--video` / `--video_length` / `--video_interval` | False | grabar mp4 cada N steps. |
| `--resume` | False | reanudar checkpoint. |
| `--load_run` | None | nombre de la subcarpeta del run. |
| `--checkpoint` | None | nombre del archivo `.pt` (sin path completo). |
| `--logger` | tensorboard | `wandb`, `neptune`. |
| `--log_project_name` | None | proyecto de wandb/neptune. |
| `--distributed` | False | multi-GPU. |

---

## 3. Recetas de entrenamiento

### 3.1 Standing — entrenamiento base

```powershell
.\..\IsaacLab\isaaclab.bat -p .\scripts\rsl_rl\train.py `
  --task=R1Standing-Direct-v0 `
  --num_envs=4096 `
  --max_iterations=4000 `
  --seed=42 `
  --headless
```

**Tiempo aprox**: 1.5 h en RTX 4070, 4 h en RTX 3060.
**Logs**: `logs/rsl_rl/r1_standing/<timestamp>/`.

### 3.2 Standing — push recovery (resume)

```powershell
.\..\IsaacLab\isaaclab.bat -p .\scripts\rsl_rl\train.py `
  --task=R1Standing-Direct-v0 `
  --num_envs=4096 `
  --max_iterations=15000 `
  --resume `
  --load_run=2026-03-03_15-35-21 `
  --checkpoint=model_3500.pt `
  --headless
```

> Antes, en el `EnvCfg`, activa los pushes (`push_force_max=8.0`) y sube `save_interval` a 1000.

### 3.3 Locomotion WASD — terreno plano

```powershell
.\..\IsaacLab\isaaclab.bat -p .\scripts\rsl_rl\train.py `
  --task=R1-Locomotion-Direct-v0 `
  --num_envs=4096 `
  --max_iterations=10000 `
  --seed=42 `
  --headless
```

### 3.4 Locomotion — playground completo

```powershell
.\..\IsaacLab\isaaclab.bat -p .\scripts\rsl_rl\train.py `
  --task=R1-Locomotion-Playground-Stairs-Direct-v0 `
  --num_envs=4096 `
  --max_iterations=15000 `
  --resume `
  --load_run=<run_locomotion_plano> `
  --headless
```

### 3.5 Política madre (jerárquica)

```powershell
.\..\IsaacLab\isaaclab.bat -p .\scripts\rsl_rl\train.py `
  --task=R1-Hierarchical-Direct-v0 `
  --num_envs=2048 `
  --max_iterations=5000 `
  --headless
```

> Esta tarea no existe en los repos públicos — se construye con los archivos de [`codigos/hierarchical/`](./codigos/hierarchical/). Edita `R1HierarchicalEnvCfg` para apuntar a los checkpoints de las hijas.

### 3.6 Multi-GPU (opcional)

```powershell
torchrun --nproc_per_node=2 .\scripts\rsl_rl\train.py `
  --task=R1Standing-Direct-v0 `
  --num_envs=8192 `
  --max_iterations=8000 `
  --distributed `
  --headless
```

---

## 4. Recetas de play

### 4.1 Play estándar

```powershell
.\..\IsaacLab\isaaclab.bat -p .\scripts\rsl_rl\play.py `
  --task=R1Standing-Direct-v0 `
  --num_envs=2
```

> Toma el checkpoint **más reciente** automáticamente. Para uno específico añade `--load_run=<sub> --checkpoint=model_3500.pt`.

### 4.2 Play en tiempo real

```powershell
.\..\IsaacLab\isaaclab.bat -p .\scripts\rsl_rl\play.py `
  --task=R1Standing-Direct-v0 `
  --num_envs=2 `
  --real-time
```

### 4.3 Play con grabación de video

```powershell
.\..\IsaacLab\isaaclab.bat -p .\scripts\rsl_rl\play.py `
  --task=R1Standing-Direct-v0 `
  --num_envs=1 `
  --video --video_length=2000
```

Genera `logs/rsl_rl/r1_standing/<run>/videos/play/*.mp4`.

### 4.4 Play con control manual WASD

```powershell
.\..\IsaacLab\isaaclab.bat -p play_wasd.py `
  --task=R1-Locomotion-Direct-v0 `
  --checkpoint="D:\space_r1\IsaacLab\logs\rsl_rl\r1_locomotion\2026-04-12_09-12-00\model_8000.pt" `
  --step=0.5
```

Una vez Isaac Sim arranca:

```
opcion> 2
W = +X (adelante)
A = -Y (izquierda)
S = -X (atras)
D = +Y (derecha)
0 = stop
P = posicion
Q = volver
```

### 4.5 Play del modelo exportado (ONNX)

```python
import onnxruntime as ort, numpy as np
sess = ort.InferenceSession("model.onnx", providers=["CUDAExecutionProvider"])
obs = np.zeros((1, 88), dtype=np.float32)
action = sess.run(None, {"obs": obs})[0]
```

Útil para deployment final (sim2real).

---

## 5. Versiones canónicas de `train.py` y `play.py` (RSL-RL)

Se han estabilizado y comentado en este snapshot — copias en:

- [`codigos/scripts/train_rsl_rl.py`](./codigos/scripts/train_rsl_rl.py)
- [`codigos/scripts/play_rsl_rl.py`](./codigos/scripts/play_rsl_rl.py)
- [`codigos/scripts/cli_args.py`](./codigos/scripts/cli_args.py)
- [`codigos/scripts/play_wasd.py`](./codigos/scripts/play_wasd.py)

Cambios respecto al repo:

1. `train.py`: **fix** de la versión mínima de `rsl-rl-lib` (acepta 3.0.1+ tal cual); preserva la lógica del repo.
2. `play.py`: añadido `--export-onnx-only` para extraer el modelo sin abrir Isaac Sim completo (útil en pipeline CI).
3. `play_wasd.py`: añadidos:
   - Búsqueda de checkpoint en **D:\\** además de `IsaacLab\logs\rsl_rl\`.
   - `--num_envs` configurable (antes hard-codeado a 1).
   - Manejo seguro del cierre (`KeyboardInterrupt` correctamente propagado).

---

## 6. Reproducibilidad

Para que un `run` sea reproducible:

1. Fijar `--seed=42` en train.
2. Versionar el `EnvCfg` y `agent_cfg.py` (commit en git antes del run).
3. Guardar `env.yaml` y `agent.yaml` que vuelca `train.py` (los crea automáticamente en `<run>/params/`).
4. Anotar la versión de Isaac Lab (`git rev-parse HEAD`) y de `rsl-rl-lib` (`pip show rsl-rl-lib`).

---

## 7. Resumen

| Acción | Comando |
|-------|---------|
| **Listar envs** | `... list_envs.py` |
| **Probar env (no aprende)** | `... zero_agent.py --task=R1Standing-Direct-v0 --num_envs=4` |
| **Entrenar standing** | `... train.py --task=R1Standing-Direct-v0 --num_envs=4096 --max_iterations=4000 --headless` |
| **Reanudar entrenamiento** | `... train.py --resume --load_run=<sub> --checkpoint=model_X.pt --max_iterations=Y` |
| **Reproducir** | `... play.py --task=R1Standing-Direct-v0 --num_envs=2 --real-time` |
| **Manual WASD** | `... play_wasd.py --task=R1-Locomotion-Direct-v0 --checkpoint=<ruta>` |
| **Exportar ONNX** | (lo hace `play.py` automáticamente) |

Próximo paso → [08_Mapa_Rutas_Importantes.md](./08_Mapa_Rutas_Importantes.md).
