# 05 — Entrenamiento en Ubuntu (mismo flujo, otros caminos)

> Toda la lógica de RL (rewards, jerarquía, fine-tune, playground) es **idéntica** a la doc principal de Windows. Lo que cambia son los comandos. Esta guía es la traducción literal.

> Si vienes de la doc Windows, lee primero `02_Crear_Politica_Basica.md`, `03_Politica_Padre_Jerarquica.md`, `04_Fine_Tuning.md`, `05_Path_Coordenadas_Velocidad.md`, `06_Playground_Terrenos.md`. Aquí solo tienes los comandos para correrlo en Ubuntu.

---

## 1. Conventions

- Workspace root = `~/r1_workspace`.
- Conda env = `env_isaaclab`.
- Isaac Lab launcher = `~/r1_workspace/IsaacLab/isaaclab.sh`.

Helper rápido en `.bashrc`:

```bash
export ISAACLAB=~/r1_workspace/IsaacLab
alias il='${ISAACLAB}/isaaclab.sh -p'
```

> Después: `il scripts/rsl_rl/train.py --task=...` etc.

---

## 2. Recetas

### 2.1 Standing — base

```bash
cd ~/r1_workspace/r1_standing
mamba activate env_isaaclab

${ISAACLAB}/isaaclab.sh -p ./scripts/rsl_rl/train.py \
    --task=R1Standing-Direct-v0 \
    --num_envs=4096 \
    --max_iterations=4000 \
    --seed=42 \
    --headless
```

### 2.2 Standing — push recovery (resume)

```bash
${ISAACLAB}/isaaclab.sh -p ./scripts/rsl_rl/train.py \
    --task=R1Standing-Direct-v0 \
    --num_envs=4096 \
    --max_iterations=15000 \
    --resume \
    --load_run=2026-03-03_15-35-21 \
    --checkpoint=model_3500.pt \
    --headless
```

### 2.3 Locomotion WASD — terreno plano

```bash
${ISAACLAB}/isaaclab.sh -p ./scripts/rsl_rl/train.py \
    --task=R1-Locomotion-Direct-v0 \
    --num_envs=4096 \
    --max_iterations=10000 \
    --headless
```

### 2.4 Locomotion — playground completo (con escaleras)

```bash
${ISAACLAB}/isaaclab.sh -p ./scripts/rsl_rl/train.py \
    --task=R1-Locomotion-Playground-Stairs-Direct-v0 \
    --num_envs=4096 \
    --max_iterations=15000 \
    --resume \
    --load_run=<run_locomotion_plano> \
    --headless
```

### 2.5 Política madre (HRL)

Antes editar `R1HierarchicalEnvCfg.{stand,walk}_ckpt` para apuntar a tus runs reales:

```python
stand_ckpt: str = "/home/usuario/r1_workspace/r1_standing/logs/rsl_rl/r1_standing/2026-03-03_15-35-21/model_3500.pt"
walk_ckpt:  str = "/home/usuario/r1_workspace/r1_standing/logs/rsl_rl/r1_locomotion/2026-04-12_09-12-00/model_8000.pt"
```

Luego:

```bash
${ISAACLAB}/isaaclab.sh -p ./scripts/rsl_rl/train.py \
    --task=R1-Hierarchical-Direct-v0 \
    --num_envs=2048 \
    --max_iterations=5000 \
    --headless
```

### 2.6 Multi-GPU

```bash
torchrun --nproc_per_node=2 ./scripts/rsl_rl/train.py \
    --task=R1Standing-Direct-v0 \
    --num_envs=8192 \
    --max_iterations=8000 \
    --distributed --headless
```

---

## 3. Play

```bash
${ISAACLAB}/isaaclab.sh -p ./scripts/rsl_rl/play.py \
    --task=R1Standing-Direct-v0 \
    --num_envs=2 \
    --real-time
```

Genera `logs/.../exported/policy.pt` y `policy.onnx`. Estos son los artefactos que llevarás al robot real (ver [doc 06](./06_Sim2Real.md), [doc 09](./09_Despliegue_Robot_Real.md)).

### Play con WASD por terminal

> En Ubuntu **no funciona `msvcrt`** del play_wasd.py original. Usa la versión adaptada:

```bash
${ISAACLAB}/isaaclab.sh -p \
    ~/DocumentacionR1Completa/Ubuntu_ROS2/codigos/scripts_bash/play_wasd_linux.py \
    --task=R1-Locomotion-Direct-v0 \
    --checkpoint=$HOME/r1_workspace/policies/walk_v1.pt
```

> Esta versión usa `tty/select` en lugar de `msvcrt`. Está en [`codigos/scripts_bash/play_wasd_linux.py`](./codigos/scripts_bash/play_wasd_linux.py).

### Play conectado a ROS2 (publicar joint_states a tópicos)

```bash
${ISAACLAB}/isaaclab.sh -p \
    ~/r1_workspace/ros2_ws/src/r1_sim_bridge/r1_sim_bridge/sim_bridge_node.py \
    --task=R1-Locomotion-Direct-v0 \
    --checkpoint=$HOME/r1_workspace/policies/walk_v1.pt
```

Después en otra terminal:

```bash
ros2 topic echo /r1/joint_states
ros2 run rqt_plot rqt_plot /r1/imu/linear_acceleration/x
```

---

## 4. TensorBoard remoto

Si entrenas en un servidor por SSH:

```bash
# en el server
tensorboard --logdir logs/rsl_rl --bind_all --port 6006
# en tu laptop
ssh -L 6006:localhost:6006 usuario@server
# Abrir http://localhost:6006
```

---

## 5. Curriculum y resume — script wrapper

Para correr todas las etapas del curriculum sin intervenir manualmente, hay un script:

```bash
#!/usr/bin/env bash
# train_full_curriculum.sh
set -e

cd ~/r1_workspace/r1_standing
mamba activate env_isaaclab

# Etapa 1 — postura estática
${ISAACLAB}/isaaclab.sh -p ./scripts/rsl_rl/train.py \
    --task=R1Standing-Direct-v0 --num_envs=4096 --max_iterations=2000 \
    --run_name=stage1_static --headless

LAST_RUN=$(ls -t logs/rsl_rl/r1_standing/ | head -1)

# Etapa 2 — postura activa
${ISAACLAB}/isaaclab.sh -p ./scripts/rsl_rl/train.py \
    --task=R1Standing-Direct-v0 --num_envs=4096 --max_iterations=4000 \
    --resume --load_run="${LAST_RUN}" \
    --run_name=stage2_active --headless

LAST_RUN=$(ls -t logs/rsl_rl/r1_standing/ | head -1)

# Etapa 3 — push recovery
# (antes editar push_force_max=8.0 en r1_standing_env_cfg.py)
${ISAACLAB}/isaaclab.sh -p ./scripts/rsl_rl/train.py \
    --task=R1Standing-Direct-v0 --num_envs=4096 --max_iterations=10000 \
    --resume --load_run="${LAST_RUN}" \
    --run_name=stage3_push --headless

# ...
```

> En la práctica este script es un esqueleto. Ajustar `push_force_max` etc. requiere modificar el cfg entre runs (no se puede vía CLI). Mejor: usar el callback de curriculum dentro del env (doc 04 §3 de Windows).

---

## 6. Diferencias técnicas con Windows (resumen)

| Aspecto | Linux ventaja |
|---------|--------------|
| PhysX SIMD (AVX2) | mejor optimizado en Linux |
| Allocator (jemalloc opcional) | reduce fragmentación |
| `O_DIRECT` para I/O | logs no satura buffer cache |
| Multi-GPU | `torchrun` funciona out-of-box |
| Profiling | `nvidia-smi --query-gpu`, `nsys profile`, `nvprof` nativos |

Para **profilear** un run:

```bash
nsys profile -o train_profile.qdrep \
    ${ISAACLAB}/isaaclab.sh -p ./scripts/rsl_rl/train.py \
    --task=R1Standing-Direct-v0 --num_envs=4096 --max_iterations=200 --headless
```

Abrir con `nsys-ui train_profile.qdrep`.

---

## 7. Anti-patrones específicos Ubuntu

- **No correr Isaac Sim sobre tmpfs** (`/tmp` en RAM). Los logs y el shader cache son grandes.
- **No usar Wayland** para sesiones GUI con Isaac Sim — cambiar a Xorg.
- **No olvidar `chrt -f 99`** para nodos de control real-time (después). Sin esto, el scheduler los preempta.
- **No correr `colcon build` en el mismo terminal donde activaste el conda env** sin antes deactivate — colcon escribe `setup.py` interpretándolo con el python del env, y eso a veces falla.

Próximo → [06_Sim2Real.md](./06_Sim2Real.md).
