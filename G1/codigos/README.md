# Code Modules / Módulos de Código — G1

[🇬🇧 English](#english) | [🇪🇸 Español](#español)

---

<a name="english"></a>
## 🇬🇧 English

High-level code modules for the G1 robot, organized by function.

| Directory | Description | Guide |
|-----------|-------------|-------|
| `imitacion/` | Imitation learning pipeline — LeRobot (ACT, Diffusion). Record, convert, train, evaluate. | [imitacion/README.md](imitacion/README.md) |
| `isaac_sim/` | Isaac Sim utilities — joint inspection, scene helpers | [isaac_sim/README.md](isaac_sim/README.md) |
| `lidar/` | G1 built-in LiDAR — ROS2 + RViz2 launch script and config | `codigos/lidar/` |
| `teleoperacion/` | Arm teleoperation with IK (pinocchio + casadi) + episode recording for imitation learning | [teleoperacion/README.md](teleoperacion/README.md) |
| `vision/` | Computer vision and object manipulation (YOLO-based detection) | `codigos/vision/` |

### LiDAR Quick Start

```bash
# View G1 built-in LiDAR in RViz2 (robot connected via enp7s0)
source /home/udc/Humanoide/G1/ros2_ws/setup_g1.sh enp7s0
bash codigos/lidar/launch_g1_lidar.sh enp7s0
```

---

<a name="español"></a>
## 🇪🇸 Español

Módulos de código de alto nivel para el robot G1, organizados por función.

| Directorio | Descripción | Guía |
|------------|-------------|------|
| `imitacion/` | Pipeline de imitation learning — LeRobot (ACT, Diffusion). Grabar, convertir, entrenar, evaluar. | [imitacion/README.md](imitacion/README.md) |
| `isaac_sim/` | Utilidades Isaac Sim — inspección de joints, ayudantes de escena | [isaac_sim/README.md](isaac_sim/README.md) |
| `lidar/` | LiDAR integrado del G1 — script de lanzado y configuración ROS2 + RViz2 | `codigos/lidar/` |
| `teleoperacion/` | Teleoperación de brazos con IK (pinocchio + casadi) + grabación de episodios para imitation learning | [teleoperacion/README.md](teleoperacion/README.md) |
| `vision/` | Visión por computador y manipulación de objetos (detección con YOLO) | `codigos/vision/` |

### LiDAR — Inicio Rápido

```bash
# Ver LiDAR integrado del G1 en RViz2 (robot conectado por enp7s0)
source /home/udc/Humanoide/G1/ros2_ws/setup_g1.sh enp7s0
bash codigos/lidar/launch_g1_lidar.sh enp7s0
```
