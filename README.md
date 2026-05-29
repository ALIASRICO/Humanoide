# Humanoid Robotics — UDC / Humanoide UDC

[🇬🇧 English](#english) | [🇪🇸 Español](#español)

---

<a name="english"></a>
## 🇬🇧 English

Research and development project for humanoid robots at **Universidad de Colombia (UDC)**.  
This repository covers RL training, simulation, deployment, perception, and imitation learning for Unitree platforms.

### Robots

| Robot | Status | DOF | Description |
|-------|--------|-----|-------------|
| **G1** | Active — fully operational | 29 | Unitree G1 bipedal humanoid, trained and deployed |
| **R1 EDU** | Hardware arriving | 26 | Unitree R1 EDU, simulation ready, hardware not yet available |

### Repository Structure

```
Humanoide/
├── G1/                   Unitree G1 — all code, policies, simulation, deployment
│   ├── codigos/          High-level modules (imitation, LiDAR, teleop, vision)
│   ├── despliegue/       Physical robot deployment via low-level SDK
│   ├── entrenamiento/    RL training (HumanoidVerse + Isaac RL Lab)
│   ├── escenas/          MuJoCo / URDF / USD robot models
│   ├── politicas/        Trained JIT policies (.pt)
│   ├── reportes/         Experiment reports
│   ├── ros2_ws/          ROS2 Jazzy workspace + CycloneDDS
│   ├── simulacion/       Isaac Sim + MuJoCo sim-to-sim validation
│   └── MANUAL_G1.md      Quick-reference hub
│
├── R1/                   Unitree R1 EDU — simulation and documentation
│   ├── codigos/          RL training code (standing, locomotion, hierarchical)
│   ├── documentacion/    Detailed training and deployment guides
│   └── escenas/          R1 URDF and MuJoCo XML models
│
├── herramientas/         Model conversion scripts (MuJoCo → URDF → USD)
├── humanoide/            Shared Unitree SDKs and CycloneDDS library
├── context/              Research context and references
└── dataset/              YOLO datasets and demonstration episodes
```

### Quick Links

- [G1 Robot Guide](G1/README.md)
- [R1 Robot Guide](R1/README.md)
- [Conversion Tools](herramientas/README.md)

### System Requirements

| Component | Version | Purpose |
|-----------|---------|---------|
| Ubuntu | 24.04 LTS | Base OS |
| NVIDIA Driver | >= 570 | RTX 50xx (Blackwell) GPU |
| CUDA | 12.x / 13.x | Training + Isaac Sim |
| Isaac Sim | 5.1.0 | Manipulation simulation |
| MuJoCo | 3.2.3 | Sim-to-sim validation |
| ROS2 | Jazzy | LiDAR, SLAM, DDS topics |

### Shared CycloneDDS (required for all DDS scripts)

```bash
export LD_LIBRARY_PATH="/home/udc/Humanoide/humanoide/cyclonedds/install/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export CYCLONEDDS_URI='<CycloneDDS><Domain id="any"><SharedMemory><Enable>false</Enable></SharedMemory></Domain></CycloneDDS>'
```

---

<a name="español"></a>
## 🇪🇸 Español

Proyecto de investigación y desarrollo para robots humanoides en la **Universidad de Colombia (UDC)**.  
Cubre entrenamiento por RL, simulación, despliegue, percepción e imitation learning para plataformas Unitree.

### Robots

| Robot | Estado | DOF | Descripción |
|-------|--------|-----|-------------|
| **G1** | Activo — completamente operativo | 29 | Unitree G1 humanoide bípedo, entrenado y desplegado |
| **R1 EDU** | Hardware en camino | 26 | Unitree R1 EDU, simulación lista, hardware aún no disponible |

### Estructura del Repositorio

```
Humanoide/
├── G1/                   Unitree G1 — código, políticas, simulación, despliegue
│   ├── codigos/          Módulos de alto nivel (imitación, LiDAR, teleop, visión)
│   ├── despliegue/       Despliegue en robot físico vía SDK de bajo nivel
│   ├── entrenamiento/    Entrenamiento RL (HumanoidVerse + Isaac RL Lab)
│   ├── escenas/          Modelos del robot (MuJoCo / URDF / USD)
│   ├── politicas/        Políticas JIT entrenadas (.pt)
│   ├── reportes/         Informes de experimentos
│   ├── ros2_ws/          Workspace ROS2 Jazzy + CycloneDDS
│   ├── simulacion/       Isaac Sim + validación sim-to-sim MuJoCo
│   └── MANUAL_G1.md      Índice de referencia rápida
│
├── R1/                   Unitree R1 EDU — simulación y documentación
│   ├── codigos/          Código RL (standing, locomotion, jerárquico)
│   ├── documentacion/    Guías detalladas de entrenamiento y despliegue
│   └── escenas/          URDF y XML MuJoCo del R1
│
├── herramientas/         Scripts de conversión de modelos (MuJoCo → URDF → USD)
├── humanoide/            SDKs Unitree compartidos y librería CycloneDDS
├── context/              Contexto de investigación y referencias
└── dataset/              Datasets YOLO y episodios de demostración
```

### Enlaces Rápidos

- [Guía Robot G1](G1/README.md)
- [Guía Robot R1](R1/README.md)
- [Herramientas de Conversión](herramientas/README.md)

### Requisitos del Sistema

| Componente | Versión | Para qué |
|------------|---------|---------|
| Ubuntu | 24.04 LTS | SO base |
| Driver NVIDIA | >= 570 | GPU RTX 50xx (Blackwell) |
| CUDA | 12.x / 13.x | Entrenamiento + Isaac Sim |
| Isaac Sim | 5.1.0 | Simulación de manipulación |
| MuJoCo | 3.2.3 | Validación sim-to-sim |
| ROS2 | Jazzy | LiDAR, SLAM, topics DDS |

### CycloneDDS compartido (obligatorio para todos los scripts DDS)

```bash
export LD_LIBRARY_PATH="/home/udc/Humanoide/humanoide/cyclonedds/install/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export CYCLONEDDS_URI='<CycloneDDS><Domain id="any"><SharedMemory><Enable>false</Enable></SharedMemory></Domain></CycloneDDS>'
```
