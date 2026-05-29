# Documentación R1 — Ubuntu + ROS2 (entorno nativo para robot físico)

Versión paralela de la documentación principal, enfocada en **Ubuntu 22.04 LTS + ROS2 Humble**, que es el entorno nativo recomendado para:

1. Entrenar las políticas en Isaac Sim/Lab a velocidad máxima (Linux es ~25–40% más rápido que Windows en simulación PhysX).
2. **Tender el puente sim2real**: transferir las políticas exportadas (ONNX/JIT) al firmware real del Unitree R1 vía nodos ROS2.
3. Mantener un workspace ROS2 listo para *deployment* en el robot, con teleop, inferencia y bringup automático.

> Si vienes del README principal de la doc, este es el complemento Linux. Los conceptos de RL (rewards, jerarquía, fine-tune, playground) son los mismos — aquí solo cambia el **stack de SO + middleware**.

---

## Índice

| #  | Documento | Tema |
|----|-----------|------|
| 01 | [01_Instalacion_Ubuntu.md](./01_Instalacion_Ubuntu.md) | Instalación de Ubuntu 22.04, drivers NVIDIA, CUDA, conda. |
| 02 | [02_Isaac_Sim_Lab_Ubuntu.md](./02_Isaac_Sim_Lab_Ubuntu.md) | Isaac Sim + Isaac Lab nativos en Linux. |
| 03 | [03_ROS2_Humble_Setup.md](./03_ROS2_Humble_Setup.md) | ROS2 Humble + colcon + workspace + dependencias del R1. |
| 04 | [04_Bridge_IsaacSim_ROS2.md](./04_Bridge_IsaacSim_ROS2.md) | Bridge oficial (`omni.isaac.ros2_bridge`) + ejemplos. |
| 05 | [05_Entrenamiento_Ubuntu.md](./05_Entrenamiento_Ubuntu.md) | Workflow Linux para train/play (mismo flujo, otros caminos). |
| 06 | [06_Sim2Real.md](./06_Sim2Real.md) | Domain randomization, fine-tune con datos reales, calibración. |
| 07 | [07_Hardware_Interface_R1.md](./07_Hardware_Interface_R1.md) | SDK del R1, comunicación Ethernet/USB, tópicos de joints. |
| 08 | [08_Nodos_ROS2_Inferencia.md](./08_Nodos_ROS2_Inferencia.md) | Nodo de inferencia ONNX + publishers/subscribers. |
| 09 | [09_Despliegue_Robot_Real.md](./09_Despliegue_Robot_Real.md) | Procedimiento full de deploy (NUC/Jetson + R1). |
| 10 | [10_Troubleshooting_Ubuntu.md](./10_Troubleshooting_Ubuntu.md) | Errores típicos: NVIDIA, ROS2, Isaac Sim. |

### Carpeta `codigos/`

```
Ubuntu_ROS2/codigos/
├── ros2_ws/                              ← workspace ROS2 listo para colcon build
│   ├── src/
│   │   ├── r1_msgs/                      ← mensajes custom (R1Command, R1State)
│   │   ├── r1_inference/                 ← nodo de inferencia ONNX (publica /joint_targets)
│   │   ├── r1_sim_bridge/                ← bridge Isaac Sim ↔ ROS2
│   │   ├── r1_teleop/                    ← teleop WASD/joystick → /target_pos
│   │   └── r1_bringup/                   ← launch files: sim, real, hybrid
│   └── README.md
├── isaac_sim_ros_bridge/
│   └── ros2_bridge_extension.py          ← script para activar bridge desde Python
├── scripts_bash/
│   ├── install_ubuntu_deps.sh            ← instala drivers, CUDA, deps básicas
│   ├── install_ros2_humble.sh            ← instala ROS2 Humble + colcon
│   └── setup_workspace.sh                ← clona Isaac Lab + crea conda env + ws
└── systemd/
    └── r1_inference.service              ← autoarranque al boot del NUC/Jetson
```

---

## ¿Por qué Ubuntu + ROS2?

| Aspecto | Windows (doc principal) | Ubuntu + ROS2 (este) |
|---------|------------------------|----------------------|
| Velocidad de PhysX | 100% | 125–140% |
| Disponibilidad de Isaac Sim | sí | sí (oficial) |
| Bridge a ROS2 | limitado (FastDDS sí, navegación NO) | nativo (`omni.isaac.ros2_bridge`) |
| SDK Unitree | limitado | oficial (`unitree_sdk2_python`, `unitree_ros2`) |
| Deployment a Jetson Orin | requiere VM | nativo |
| Tiempo real (control 1 kHz) | no | con `PREEMPT_RT` patches |

**Conclusión**: el entrenamiento en Windows es viable; el **deployment al robot físico exige Linux**.

---

## Flujo recomendado

```
[1] Instalar Ubuntu 22.04 + drivers + CUDA (doc 01)
      ↓
[2] Instalar Isaac Sim + Isaac Lab nativos (doc 02)
      ↓
[3] Instalar ROS2 Humble + crear workspace (doc 03)
      ↓
[4] Activar bridge Isaac Sim ↔ ROS2 (doc 04)
      ↓
[5] Entrenar políticas igual que Windows (doc 05)
      ↓
[6] Domain randomization + sim2real (doc 06)
      ↓
[7] Conectar al SDK del Unitree R1 (doc 07)
      ↓
[8] Construir nodo de inferencia ONNX (doc 08)
      ↓
[9] Deploy completo al robot (doc 09)
      ↓
[10] Operar y monitorear (doc 10 si algo falla)
```

---

## Versiones canónicas

| Componente | Versión |
|-----------|--------:|
| Ubuntu | **22.04 LTS** (Jammy) — única soportada por ROS2 Humble |
| Kernel | 5.15+ (6.x con PREEMPT_RT para deploy real) |
| Driver NVIDIA | ≥ 535 |
| CUDA Toolkit | 12.1 / 12.4 |
| Python | 3.10 (de Ubuntu 22.04 base) |
| ROS2 | **Humble Hawksbill** (LTS hasta 2027) |
| Isaac Sim | 4.5.0 / 5.0.0 |
| Isaac Lab | `main` |
| RSL-RL | `rsl-rl-lib >= 3.0.1` |
| Unitree SDK | `unitree_sdk2_python` (rama main) |
| onnxruntime-gpu | 1.18+ |

---

## Convenciones de rutas

Aquí asumimos:

```
~/r1_workspace/
├── IsaacLab/                ← Isaac Lab
├── r1_standing/             ← extensión standing
├── r1_locomotion/           ← extensión locomotion
├── ros2_ws/                 ← workspace ROS2
│   ├── src/                 ← paquetes
│   ├── build/, install/, log/   (colcon)
└── policies/                ← ONNX/JIT exportados
    ├── stand_v1.onnx
    ├── walk_v1.onnx
    └── stair_v1.onnx
```

> **Recomendación**: monta `~/r1_workspace` en un disco SSD/NVMe rápido. Los logs de Isaac Lab crecen rápido (cientos de MB por run).

Próximo → [01_Instalacion_Ubuntu.md](./01_Instalacion_Ubuntu.md).
