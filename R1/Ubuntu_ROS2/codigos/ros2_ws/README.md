# Workspace ROS2 para R1

Paquetes:

| Paquete | Tipo | Descripción |
|---------|------|-------------|
| `r1_msgs` | ament_cmake | Mensajes custom (`R1Command`, `R1State`, `R1Skill`, `FootContact`). |
| `r1_inference` | ament_python | Nodo principal: ONNX inference + SDK bridge a Unitree. |
| `r1_sim_bridge` | ament_python | Equivalente pero contra Isaac Sim (en lugar del SDK). |
| `r1_teleop` | ament_python | Teleop por teclado (publica `/r1/target_pose`). |
| `r1_bringup` | ament_cmake | Launch files + URDF + configs. |

## Build

```bash
cd ~/r1_workspace/ros2_ws
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
source install/setup.bash
```

## Lanzar (sim)

```bash
ros2 launch r1_bringup sim.launch.py
```

## Lanzar (robot real)

```bash
ros2 launch r1_bringup real.launch.py
```

## Topics

```
/r1/joint_states     [sensor_msgs/JointState]      sub  (sdk_bridge → ros)
/r1/imu              [sensor_msgs/Imu]             sub
/r1/foot_contact     [r1_msgs/FootContact]         sub
/r1/joint_command    [sensor_msgs/JointState]      pub  (inference → sdk)
/r1/target_pose      [geometry_msgs/Pose2D]        sub  (teleop → inference)
/r1/skill            [std_msgs/String]             sub  ("auto"/"stand"/"walk"/"stair")
/r1/diagnostics      [diagnostic_msgs/DiagnosticArray] pub
```
