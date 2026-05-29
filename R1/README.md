# Unitree R1 EDU — UDC Robot

[🇬🇧 English](#english) | [🇪🇸 Español](#español)

---

<a name="english"></a>
## 🇬🇧 English

**Unitree R1 EDU** — 26-DOF bipedal humanoid robot with optional Jetson Orin compute module and dexterous hands. This directory contains simulation code, trained policy checkpoints, and detailed documentation.

### Hardware Status

> **HARDWARE ARRIVING — Simulation setup is in progress.**
> Code is ready and tested in simulation (Isaac Sim + Isaac Lab). Hardware deployment has not yet been tested on the physical R1.

### Robot Specifications

| Feature | Specification |
|---------|--------------|
| DOF | 26 (bipedal body) |
| Compute (onboard) | Optional NVIDIA Jetson Orin |
| Hands | Dexterous end-effectors (optional) |
| Communication | Unitree SDK2 (DDS) |
| SDK | Same protocol as G1 |

### What Is Available

| Component | Status | Notes |
|-----------|--------|-------|
| URDF model | Ready | `escenas/R1.urdf` |
| MuJoCo XML | Ready | `escenas/R1_C++.xml` |
| Standing policy (push-recovery) | Code ready | 88-dim obs, PPO (RSL-RL) |
| Locomotion policy (WASD) | Code ready | 97-dim obs, coordinate navigation |
| Hierarchical policy (high-level planner) | Code ready | FSM orchestrating sub-policies |
| Hardware deployment | Pending hardware | Will use Unitree SDK2 + ROS2 |

### Directory Structure

```
R1/
├── codigos/
│   ├── scripts/          Training (train_rsl_rl.py) and play (play_rsl_rl.py, play_wasd.py)
│   ├── standing/         Child policy — balance / push-recovery
│   ├── locomotion/       Child policy — WASD / coordinate navigation
│   ├── hierarchical/     Parent policy — FSM orchestrator
│   ├── agents/           PPO config (RSL-RL + SKRL)
│   └── playground/       Terrain configs (stairs, rough, curriculum)
├── documentacion/        Detailed guides (10 docs + Ubuntu/ROS2 set)
│   ├── Ubuntu_ROS2/      Linux deployment guides + ROS2 workspace
│   └── README.md         Full documentation index
└── escenas/
    ├── R1.urdf           R1 URDF model
    ├── R1_C++.xml        R1 MuJoCo XML model
    └── meshes/           Visual and collision meshes
```

### Training (Isaac Sim + Isaac Lab)

```bash
conda activate isaaclab
cd /home/udc/Humanoide/R1

# Train standing policy
python codigos/scripts/train_rsl_rl.py --task R1Standing-Direct-v0

# Train locomotion policy
python codigos/scripts/train_rsl_rl.py --task R1-Locomotion-Direct-v0

# Play / evaluate
python codigos/scripts/play_rsl_rl.py --task R1Standing-Direct-v0 --checkpoint logs/...
```

### Documentation Index

See [documentacion/README.md](documentacion/README.md) for the full guide covering:
- Installation (Windows and Ubuntu)
- Basic policy creation
- Hierarchical policy (parent + children)
- Fine-tuning and transfer learning
- Terrain playgrounds
- Sim-to-real bridge + hardware interface

---

<a name="español"></a>
## 🇪🇸 Español

**Unitree R1 EDU** — robot humanoide bípedo de 26 DOF con módulo de cómputo Jetson Orin opcional y manos dextras. Este directorio contiene código de simulación, checkpoints de políticas y documentación detallada.

### Estado del Hardware

> **HARDWARE EN CAMINO — Configuración de simulación en progreso.**
> El código está listo y probado en simulación (Isaac Sim + Isaac Lab). El despliegue en hardware no se ha probado aún en el R1 físico.

### Especificaciones del Robot

| Característica | Especificación |
|---------------|---------------|
| DOF | 26 (cuerpo bípedo) |
| Cómputo (a bordo) | NVIDIA Jetson Orin (opcional) |
| Manos | Efectores finales dextros (opcional) |
| Comunicación | Unitree SDK2 (DDS) |
| SDK | Mismo protocolo que el G1 |

### Qué Está Disponible

| Componente | Estado | Notas |
|------------|--------|-------|
| Modelo URDF | Listo | `escenas/R1.urdf` |
| XML MuJoCo | Listo | `escenas/R1_C++.xml` |
| Política de standing (push-recovery) | Código listo | 88 dims obs, PPO (RSL-RL) |
| Política de locomoción (WASD) | Código listo | 97 dims obs, navegación por coordenadas |
| Política jerárquica (planificador alto nivel) | Código listo | FSM orquestando sub-políticas |
| Despliegue en hardware | Pendiente de hardware | Usará Unitree SDK2 + ROS2 |

### Estructura del Directorio

```
R1/
├── codigos/
│   ├── scripts/          Entrenamiento (train_rsl_rl.py) y play (play_rsl_rl.py, play_wasd.py)
│   ├── standing/         Política hija — balance / push-recovery
│   ├── locomotion/       Política hija — navegación WASD / coordenadas
│   ├── hierarchical/     Política madre — orquestador FSM
│   ├── agents/           Config PPO (RSL-RL + SKRL)
│   └── playground/       Configs de terrenos (escaleras, rugoso, curriculum)
├── documentacion/        Guías detalladas (10 docs + set Ubuntu/ROS2)
│   ├── Ubuntu_ROS2/      Guías de despliegue Linux + workspace ROS2
│   └── README.md         Índice completo de documentación
└── escenas/
    ├── R1.urdf           Modelo URDF del R1
    ├── R1_C++.xml        XML MuJoCo del R1
    └── meshes/           Mallas visuales y de colisión
```

### Entrenamiento (Isaac Sim + Isaac Lab)

```bash
conda activate isaaclab
cd /home/udc/Humanoide/R1

# Entrenar política de standing
python codigos/scripts/train_rsl_rl.py --task R1Standing-Direct-v0

# Entrenar política de locomoción
python codigos/scripts/train_rsl_rl.py --task R1-Locomotion-Direct-v0

# Reproducir / evaluar
python codigos/scripts/play_rsl_rl.py --task R1Standing-Direct-v0 --checkpoint logs/...
```

### Índice de Documentación

Ver [documentacion/README.md](documentacion/README.md) para la guía completa que cubre:
- Instalación (Windows y Ubuntu)
- Creación de política básica
- Política jerárquica (madre + hijas)
- Fine-tuning y transfer learning
- Playgrounds con terrenos
- Bridge sim-to-real + interfaz de hardware
