# SLAM para G1 — Opciones y Estado

---

## LiDAR del G1 (built-in)

El G1 tiene un LiDAR integrado que publica directamente vía CycloneDDS:
- Topic: `/utlidar/cloud` (PointCloud2)
- Frame: `utlidar_lidar`
- Ya funciona con: `source ros2_ws/setup_g1.sh enp7s0`

Para verlo en RViz:
```bash
bash codigos/lidar/launch_g1_lidar.sh enp7s0
```

---

## SLAM con el LiDAR built-in del G1

Para SLAM en ROS2 Jazzy con `/utlidar/cloud`:

### Opción A — kiss-icp (recomendado, fácil)
```bash
sudo apt install ros-jazzy-kiss-icp
source ros2_ws/setup_g1.sh enp7s0
ros2 run kiss_icp_ros odometry_node --ros-args \
    -r pointcloud:=/utlidar/cloud \
    -p max_range:=100.0
```

### Opción B — Fast-LIO2 (más preciso, necesita compilación)
```bash
# Clonar versión ROS2
cd ros2_ws/slam
git clone https://github.com/Ericsii/FAST_LIO --depth 1
# Configurar para utlidar: lid_topic: "/utlidar/cloud"
# Compilar: colcon build --packages-select fast_lio
```

---

## LiDAR externo Unitree L1/L2 (USB o red)

Si conectas un sensor Unitree L1 o L2 externo:

**Driver ROS2:** `ros2_ws/slam/unitree_lidar_ros2`

```bash
# Compilar
source /opt/ros/jazzy/setup.bash
cd /home/udc/Unitree_G1
colcon build --packages-select unitree_lidar_ros2 \
    --base-paths ros2_ws/slam/unitree_lidar_ros2

# Lanzar (editar serial_port o IP según conexión)
source ros2_ws/install/setup.bash
ros2 launch unitree_lidar_ros2 launch.py
```

Publica en `/unilidar/cloud` (diferente del built-in `/utlidar/cloud`).

---

## point_lio_unilidar (ROS1 — solo referencia)

La carpeta `point_lio_unilidar/` es ROS1 y **no compila en ROS2**.
Se mantiene como referencia del algoritmo (configuración del sensor L1/L2).
Para ROS2 usar kiss-icp o Fast-LIO2 con topic remapping.
