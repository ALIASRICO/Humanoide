# 04 — Bridge Isaac Sim ↔ ROS2

> Isaac Sim trae una extensión oficial **`omni.isaac.ros2_bridge`** que publica/suscribe automáticamente los datos del entorno simulado a tópicos ROS2. Es el puente que te permite:
>
> 1. Probar tus nodos ROS2 contra el robot **simulado** antes de tocarlo físico.
> 2. Visualizar/grabar la simulación con `rqt_image_view`, `rosbag`, RViz2.
> 3. Inyectar comandos desde nodos externos al env (lo opuesto: ROS2 → Isaac).

---

## 1. Activar el bridge

### Opción A — desde la GUI

1. Abrir Isaac Sim → `Window` → `Extensions`.
2. En el buscador: `omni.isaac.ros2_bridge`.
3. Toggle ON. **Auto-load** = ON (para que arranque siempre).
4. Reiniciar Isaac Sim.

### Opción B — programática (cuando lanzas Isaac Sim desde Python)

```python
from isaacsim import SimulationApp
sim = SimulationApp({"headless": True})
import omni
ext_manager = omni.kit.app.get_app().get_extension_manager()
ext_manager.set_extension_enabled_immediate("omni.isaac.ros2_bridge", True)
```

Versión completa en [`codigos/isaac_sim_ros_bridge/ros2_bridge_extension.py`](./codigos/isaac_sim_ros_bridge/ros2_bridge_extension.py).

---

## 2. Variables de entorno necesarias

Al lanzar Isaac Sim **el shell debe tener ROS2 en el environment** (`source /opt/ros/humble/setup.bash` ya hecho desde `.bashrc`). Sin eso, las librerías `librmw_*.so` no se encuentran y el bridge queda en estado "warning". Tu `.bashrc` ya lo hace.

Adicional para Cyclone DDS:

```bash
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
export ROS_DOMAIN_ID=42
```

---

## 3. Tópicos que publica Isaac Sim por defecto

Una vez activado, Isaac Sim expone (cuando construyes los Action Graphs adecuados):

| Topic | Tipo | Sentido |
|-------|------|---------|
| `/clock` | `rosgraph_msgs/Clock` | pub |
| `/tf`, `/tf_static` | `tf2_msgs/TFMessage` | pub |
| `/joint_states` | `sensor_msgs/JointState` | pub |
| `/imu` | `sensor_msgs/Imu` | pub |
| `/camera/rgb` | `sensor_msgs/Image` | pub |
| `/camera/depth` | `sensor_msgs/Image` | pub |

Y suscribe:

| Topic | Tipo | Sentido |
|-------|------|---------|
| `/joint_command` | `sensor_msgs/JointState` | sub → mover joints |
| `/cmd_vel` | `geometry_msgs/Twist` | sub → tracked vehicles |

> Para que Isaac publique/suscriba tienes que crear **Action Graphs** desde la GUI. Es engorroso para integración programática — por eso construimos `r1_sim_bridge` que hace lo mismo en código.

---

## 4. `r1_sim_bridge` — bridge programático

El nodo en [`codigos/ros2_ws/src/r1_sim_bridge/`](./codigos/ros2_ws/src/r1_sim_bridge/) **se ejecuta dentro del proceso de Isaac Sim** (al igual que tu `train.py` o `play.py`) y:

1. Abre el environment Gym del R1.
2. Crea un nodo ROS2 (`rclpy`) que:
   - Publica `/r1/joint_states`, `/r1/imu`, `/r1/root_pose` cada step.
   - Suscribe `/r1/target_pose` (para WASD remoto).
   - Suscribe `/r1/joint_command_override` (para test manual de PD).
3. Corre el loop de simulación en main thread; el spin de ROS2 en background thread.

Esquema:

```
┌──────────────────────────────┐
│   Isaac Sim Process          │
│  ┌─────────────────────┐     │   ROS2 (DDS)
│  │ R1Locomotion env    │◄────┼──── /r1/target_pose      ← teleop / planner externo
│  │ (gym.make)          │─────┼───→ /r1/joint_states
│  │                     │─────┼───→ /r1/imu
│  │ Inference policy    │─────┼───→ /r1/foot_contact
│  └─────────────────────┘     │
│       ▲                      │
│       │ rclpy.spin (BG)      │
│  ┌────┴────────────────┐     │
│  │ R1SimBridgeNode     │     │
│  └─────────────────────┘     │
└──────────────────────────────┘
```

Lanzarlo:

```bash
source /opt/ros/humble/setup.bash
source ~/r1_workspace/ros2_ws/install/setup.bash
mamba activate env_isaaclab

~/r1_workspace/IsaacLab/isaaclab.sh -p \
    ~/r1_workspace/ros2_ws/src/r1_sim_bridge/r1_sim_bridge/sim_bridge_node.py \
    --task=R1-Locomotion-Direct-v0 \
    --checkpoint=~/r1_workspace/policies/walk_v1.pt
```

En otra terminal:

```bash
ros2 topic list
# /r1/joint_states
# /r1/imu
# /r1/target_pose
# /clock
# /tf
```

---

## 5. Visualizar con RViz2

Crear un launch:

```bash
ros2 launch r1_bringup view_sim.launch.py
```

Que carga:
- Modelo URDF del R1 (`urdf/r1.urdf` — extraído del USD).
- TF tree.
- `rviz2` con preset.

Detalles en [`codigos/ros2_ws/src/r1_bringup/launch/view_sim.launch.py`](./codigos/ros2_ws/src/r1_bringup/launch/view_sim.launch.py).

---

## 6. Inyectar comandos al sim desde otra máquina

Sirve para ensayar teleop o planner desde un laptop:

Terminal en el laptop:

```bash
export ROS_DOMAIN_ID=42  # mismo que el PC con Isaac
ros2 topic pub /r1/target_pose geometry_msgs/Pose2D "{x: 2.0, y: 0.0, theta: 0.0}" --once
```

El env del PC con Isaac actualiza `target_pos_w` y el robot va al objetivo.

---

## 7. Latencia típica del bridge

| Hop | Latencia |
|-----|---------:|
| Isaac Sim → DDS (intra-proceso) | ~0.5 ms |
| DDS → ROS2 nodo local | ~1 ms |
| DDS → ROS2 nodo en LAN | ~3–5 ms |
| DDS → ROS2 nodo en Wi-Fi | ~10–30 ms |

Para control 50 Hz, todo lo intra-proceso/LAN es OK. Para 1 kHz hace falta **sin ROS2 entre policy y robot** (ver [doc 09](./09_Despliegue_Robot_Real.md) — la inferencia se mete *en el mismo proceso* que el SDK del robot).

---

## 8. Sincronización temporal (`/clock`)

Como Isaac corre con dt=1/120 (no real-time), publica `/clock` y todos los nodos deben usar `use_sim_time=true`:

```bash
ros2 param set /r1_inference use_sim_time true
```

O en el launch:

```python
Node(
    package='r1_inference',
    executable='inference_node',
    parameters=[{'use_sim_time': True}],
)
```

> Cuando pases al robot real, **`use_sim_time = False`** (default).

---

## 9. Anti-patrones

- **No usar `omni.isaac.ros_bridge`** (sin "2") — es ROS1 deprecated.
- **No spin-bloquear desde el main thread**: Isaac Sim necesita el main para rendering.
- **No publicar imágenes a 60 Hz** sin compresión — saturas DDS. Usa `image_transport` con `compressed`.
- **No mezclar `use_sim_time=true` con relojes reales** — TF se rompe.

Próximo → [05_Entrenamiento_Ubuntu.md](./05_Entrenamiento_Ubuntu.md).
