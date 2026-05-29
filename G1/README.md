# Unitree G1 — UDC Robot

[🇬🇧 English](#english) | [🇪🇸 Español](#español)

---

<a name="english"></a>
## 🇬🇧 English

**Unitree G1** — 29-DOF bipedal humanoid robot. This directory contains all software for training, simulating, and deploying the G1 at Universidad de Colombia.

### Quick Start (3 steps)

```bash
# Step 1 — Activate environment
conda activate /home/udc/Humanoide/G1/envs/g1_udc

# Step 2 — Set DDS variables (required for any DDS script)
export LD_LIBRARY_PATH="/home/udc/Humanoide/humanoide/cyclonedds/install/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export CYCLONEDDS_URI='<CycloneDDS><Domain id="any"><SharedMemory><Enable>false</Enable></SharedMemory></Domain></CycloneDDS>'

# Step 3 — Launch Isaac Sim (pick & place with DEX1 gripper)
cd /home/udc/Humanoide/G1
bash simulacion/isaac_sim/launch_g1.sh cylinder_dex1
```

### Module Navigation

| Directory | Description | Guide |
|-----------|-------------|-------|
| `simulacion/` | Isaac Sim + MuJoCo sim-to-sim validation | [simulacion/README.md](simulacion/README.md) |
| `simulacion/isaac_sim/` | Isaac Sim manipulation scenes (14 aliases) | [simulacion/isaac_sim/README.md](simulacion/isaac_sim/README.md) |
| `simulacion/sdk_bridge/` | MuJoCo with real DDS interface | [simulacion/sdk_bridge/README.md](simulacion/sdk_bridge/README.md) |
| `despliegue/` | Physical robot deployment (low-level SDK) | [despliegue/README.md](despliegue/README.md) |
| `entrenamiento/` | RL training — HumanoidVerse + Isaac RL Lab | [entrenamiento/README.md](entrenamiento/README.md) |
| `codigos/` | High-level modules: imitation, LiDAR, teleop, vision | [codigos/README.md](codigos/README.md) |
| `politicas/` | Trained JIT policies (.pt files) | [politicas/README.md](politicas/README.md) |
| `ros2_ws/` | ROS2 Jazzy + CycloneDDS (LiDAR, SLAM) | `ros2_ws/slam/README.md` |

### Trained Policies

| File | Type | DOF | Description |
|------|------|-----|-------------|
| `motion_agacharse_v10_jit.pt` | Motion (29-DOF) | 0–14 legs+waist | Squat / crouch motion (cyclic) |
| `motion_munecas_DR_jit.pt` | Motion (29-DOF) | 15–28 arms | Wrist rotation with Domain Randomization |
| `motion_estirar_DR_jit.pt` | Motion (29-DOF) | 15–28 arms | Arm stretch motion |
| `motion_saludar_DR_jit.pt` | Motion (29-DOF) | 15–28 arms | Wave / greeting motion |
| `model_7000_jit.pt` | Locomotion (12-DOF) | 0–11 legs | Walking — HumanoidVerse trained |
| `model_DR_jit.pt` | Locomotion (12-DOF) | 0–11 legs | Walking — with Domain Randomization |
| `motion.pt` | Locomotion (12-DOF) | 0–11 legs | Walking — original Unitree policy |

### Conda Environments

| Env | Activate | Use |
|-----|----------|-----|
| `g1_udc` | `conda activate /home/udc/Humanoide/G1/envs/g1_udc` | MuJoCo, deployment, SDK, teleop, imitation |
| `hgen` | `conda activate hgen` | RL training — HumanoidVerse + Genesis |
| `isaaclab` | `conda activate isaaclab` | Isaac Sim + Isaac Lab |

### Hardware

- Robot: Unitree G1 (29 DOF — 12 legs, 3 waist, 14 arms)
- GPU: NVIDIA RTX 5090 (31.35 GB VRAM)
- OS: Ubuntu 24.04 LTS (kernel 6.17)
- Network interface to robot: `enp7s0` (Ethernet, IP: 192.168.123.100)

---

<a name="español"></a>
## 🇪🇸 Español

**Unitree G1** — robot humanoide bípedo de 29 DOF. Este directorio contiene todo el software para entrenar, simular y desplegar el G1 en la Universidad de Colombia.

### Inicio Rápido (3 pasos)

```bash
# Paso 1 — Activar entorno
conda activate /home/udc/Humanoide/G1/envs/g1_udc

# Paso 2 — Variables DDS (obligatorias para cualquier script DDS)
export LD_LIBRARY_PATH="/home/udc/Humanoide/humanoide/cyclonedds/install/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export CYCLONEDDS_URI='<CycloneDDS><Domain id="any"><SharedMemory><Enable>false</Enable></SharedMemory></Domain></CycloneDDS>'

# Paso 3 — Lanzar Isaac Sim (pick & place con garra DEX1)
cd /home/udc/Humanoide/G1
bash simulacion/isaac_sim/launch_g1.sh cylinder_dex1
```

### Navegación de Módulos

| Directorio | Descripción | Guía |
|------------|-------------|------|
| `simulacion/` | Isaac Sim + validación sim-to-sim MuJoCo | [simulacion/README.md](simulacion/README.md) |
| `simulacion/isaac_sim/` | Escenas Isaac Sim (14 alias disponibles) | [simulacion/isaac_sim/README.md](simulacion/isaac_sim/README.md) |
| `simulacion/sdk_bridge/` | MuJoCo con interfaz DDS real | [simulacion/sdk_bridge/README.md](simulacion/sdk_bridge/README.md) |
| `despliegue/` | Despliegue en robot físico (SDK bajo nivel) | [despliegue/README.md](despliegue/README.md) |
| `entrenamiento/` | Entrenamiento RL — HumanoidVerse + Isaac RL Lab | [entrenamiento/README.md](entrenamiento/README.md) |
| `codigos/` | Módulos: imitación, LiDAR, teleoperación, visión | [codigos/README.md](codigos/README.md) |
| `politicas/` | Políticas JIT entrenadas (archivos .pt) | [politicas/README.md](politicas/README.md) |
| `ros2_ws/` | ROS2 Jazzy + CycloneDDS (LiDAR, SLAM) | `ros2_ws/slam/README.md` |

### Políticas Entrenadas

| Archivo | Tipo | DOF | Descripción |
|---------|------|-----|-------------|
| `motion_agacharse_v10_jit.pt` | Movimiento (29-DOF) | 0–14 piernas+cintura | Agacharse cíclicamente |
| `motion_munecas_DR_jit.pt` | Movimiento (29-DOF) | 15–28 brazos | Rotación de muñecas con DR |
| `motion_estirar_DR_jit.pt` | Movimiento (29-DOF) | 15–28 brazos | Estirar brazos |
| `motion_saludar_DR_jit.pt` | Movimiento (29-DOF) | 15–28 brazos | Movimiento de saludo |
| `model_7000_jit.pt` | Locomoción (12-DOF) | 0–11 piernas | Caminar — entrenado en HumanoidVerse |
| `model_DR_jit.pt` | Locomoción (12-DOF) | 0–11 piernas | Caminar — con Domain Randomization |
| `motion.pt` | Locomoción (12-DOF) | 0–11 piernas | Caminar — política original Unitree |

### Entornos Conda

| Entorno | Activar | Uso |
|---------|---------|-----|
| `g1_udc` | `conda activate /home/udc/Humanoide/G1/envs/g1_udc` | MuJoCo, despliegue, SDK, teleop, imitación |
| `hgen` | `conda activate hgen` | Entrenamiento RL — HumanoidVerse + Genesis |
| `isaaclab` | `conda activate isaaclab` | Isaac Sim + Isaac Lab |

### Hardware

- Robot: Unitree G1 (29 DOF — 12 piernas, 3 cintura, 14 brazos)
- GPU: NVIDIA RTX 5090 (31.35 GB VRAM)
- OS: Ubuntu 24.04 LTS (kernel 6.17)
- Interfaz de red al robot: `enp7s0` (Ethernet, IP: 192.168.123.100)
