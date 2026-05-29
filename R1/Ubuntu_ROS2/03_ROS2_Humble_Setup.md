# 03 — ROS2 Humble: instalación, workspace y dependencias del R1

> Sin ROS2 no hay control del robot real. Esta guía instala ROS2 Humble Hawksbill (LTS hasta 2027), crea el workspace `ros2_ws` y deja listas todas las dependencias para el R1.

---

## 1. Instalación oficial

### 1.1 Locale UTF-8

```bash
sudo apt update && sudo apt install -y locales
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
export LANG=en_US.UTF-8
```

### 1.2 Repos de ROS2

```bash
sudo apt install -y software-properties-common
sudo add-apt-repository universe -y

sudo apt update && sudo apt install -y curl
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key \
    -o /usr/share/keyrings/ros-archive-keyring.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] \
    http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | \
    sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null
```

### 1.3 Instalar ROS2 Humble (desktop full)

```bash
sudo apt update
sudo apt install -y ros-humble-desktop
sudo apt install -y ros-dev-tools
```

> **Versión "ros-base"** si solo necesitas runtime sin RViz/Gazebo (recomendado para Jetson):
> `sudo apt install -y ros-humble-ros-base`

### 1.4 Source en `.bashrc`

```bash
echo 'source /opt/ros/humble/setup.bash' >> ~/.bashrc
source ~/.bashrc
```

Verifica:

```bash
ros2 --help
ros2 doctor                 # comprueba el estado
```

---

## 2. Dependencias adicionales para el R1

### 2.1 Mensajes y herramientas

```bash
sudo apt install -y \
    ros-humble-rmw-fastrtps-cpp \
    ros-humble-rmw-cyclonedds-cpp \
    ros-humble-tf2 ros-humble-tf2-ros ros-humble-tf2-tools \
    ros-humble-controller-manager ros-humble-ros2-control ros-humble-ros2-controllers \
    ros-humble-joint-state-publisher ros-humble-joint-state-publisher-gui \
    ros-humble-xacro ros-humble-robot-state-publisher \
    ros-humble-rqt ros-humble-rqt-graph ros-humble-rqt-tf-tree ros-humble-rqt-plot \
    ros-humble-rviz2
```

### 2.2 Python deps

```bash
sudo apt install -y python3-colcon-common-extensions python3-rosdep python3-vcstool \
                    python3-pip python3-numpy python3-yaml
sudo rosdep init || true
rosdep update
```

### 2.3 SDK de Unitree

```bash
mkdir -p ~/r1_workspace/sdk
cd ~/r1_workspace/sdk
git clone https://github.com/unitreerobotics/unitree_sdk2_python.git
cd unitree_sdk2_python
pip install -e .
```

> Reemplazar la URL si Unitree publica un repo específico para R1. La interfaz **`unitree_sdk2_python`** está orientada a Go2/H1; el R1 puede compartir bus o tener variante propia. Verifica con tu unidad.

```bash
cd ~/r1_workspace/sdk
git clone https://github.com/unitreerobotics/unitree_ros2.git
```

### 2.4 ONNX Runtime GPU (para inferencia)

```bash
pip install onnxruntime-gpu==1.18.0
python -c "import onnxruntime as ort; print(ort.get_device())"
# CUDA
```

---

## 3. Crear el workspace

```bash
mkdir -p ~/r1_workspace/ros2_ws/src
cd ~/r1_workspace/ros2_ws
colcon build --symlink-install
```

> El primer `colcon build` con un `src/` vacío crea las carpetas `build/`, `install/`, `log/`.

`source` del overlay:

```bash
echo 'source ~/r1_workspace/ros2_ws/install/setup.bash' >> ~/.bashrc
source ~/.bashrc
```

> A partir de aquí los paquetes que pongas en `ros2_ws/src/` (los de [`codigos/ros2_ws/src/`](./codigos/ros2_ws/src/)) se construyen con un nuevo `colcon build`.

---

## 4. Copiar los paquetes del R1 desde la doc

```bash
cp -r ~/DocumentacionR1Completa/Ubuntu_ROS2/codigos/ros2_ws/src/* \
      ~/r1_workspace/ros2_ws/src/
cd ~/r1_workspace/ros2_ws
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
source install/setup.bash
```

Verifica que están registrados:

```bash
ros2 pkg list | grep r1_
# r1_bringup
# r1_inference
# r1_msgs
# r1_sim_bridge
# r1_teleop
```

---

## 5. RMW (DDS) — elegir implementación

Por defecto Humble usa **FastRTPS**. Para multi-host con shared memory rápida:

```bash
echo 'export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp' >> ~/.bashrc
```

> Cyclone DDS suele ser más estable en redes wifi del laboratorio. Si tienes problemas con discovery, vuelve a FastRTPS.

`ROS_DOMAIN_ID` para aislar de otras máquinas:

```bash
echo 'export ROS_DOMAIN_ID=42' >> ~/.bashrc
source ~/.bashrc
```

---

## 6. Probar comunicación

Terminal 1:

```bash
ros2 run demo_nodes_cpp talker
```

Terminal 2:

```bash
ros2 run demo_nodes_py listener
```

Si oyes mensajes "I heard: 'Hello World: 1'…" → DDS OK.

---

## 7. Tópicos esperados del R1

Lo que tu nodo de inferencia debe **suscribir** y **publicar**:

| Topic | Tipo | Sentido | Quien |
|-------|------|---------|-------|
| `/r1/joint_states` | `sensor_msgs/JointState` | sub | leído desde el robot/Sim |
| `/r1/imu` | `sensor_msgs/Imu` | sub | IMU del torso |
| `/r1/foot_contact` | `r1_msgs/FootContact` | sub | (custom) |
| `/r1/joint_targets` | `sensor_msgs/JointState` (positions) | pub | salida de inferencia |
| `/r1/target_pose` | `geometry_msgs/Pose2D` | sub | comando WASD/coordenadas |
| `/r1/skill` | `std_msgs/String` | sub/pub | "stand" / "walk" / "stair" |
| `/r1/diagnostics` | `diagnostic_msgs/DiagnosticArray` | pub | salud del robot |

Las definiciones custom viven en [`codigos/ros2_ws/src/r1_msgs/`](./codigos/ros2_ws/src/r1_msgs/).

---

## 8. Tips de productividad ROS2

```bash
# Listar tópicos activos
ros2 topic list

# Ver tipo de un tópico
ros2 topic info /r1/joint_states

# Eco de mensajes a 1 Hz
ros2 topic echo /r1/joint_states --once

# Frecuencia y throughput
ros2 topic hz /r1/joint_states
ros2 topic bw /r1/joint_states

# Ver nodos
ros2 node list
ros2 node info /r1_inference

# Grafo de TF
ros2 run tf2_tools view_frames

# Bag (grabar y reproducir)
ros2 bag record -a -o run01
ros2 bag play run01
```

---

## 9. Anti-patrones

- **No mezclar `setup.bash` de varias distros** — fuente solo Humble en `.bashrc`.
- **No olvidar `source install/setup.bash`** después de cada `colcon build` (en sesiones nuevas viene del `.bashrc`).
- **No publicar a 100 Hz por debug** sin necesidad — el bridge a Isaac Sim se atasca. Limita a 50 Hz.
- **No usar el mismo `ROS_DOMAIN_ID` que tus compañeros** si comparten LAN — se "ven" entre sí.

Próximo → [04_Bridge_IsaacSim_ROS2.md](./04_Bridge_IsaacSim_ROS2.md).
