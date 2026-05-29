# 08 — Nodos ROS2 de inferencia y orquestación

> Aquí cerramos el lazo: leer estado del R1, correr el ONNX exportado, publicar comandos. Y hacer lo mismo con la **política madre** (HRL) si está activa.

---

## 1. Arquitectura final

```
┌────────────────────────────┐    ┌──────────────────────────┐
│  R1 robot (DDS Unitree)    │    │  Operator / planner       │
│   ▲           ▼            │    │   ▼ /r1/target_pose       │
│   │ rt/lowstate            │    │     /r1/skill             │
│   │ rt/lowcmd              │    │                           │
└───┼───────────┼────────────┘    └──────────┬───────────────┘
    │           │                              │
┌───┴───────────┴──────────────────────────────┴─────────────┐
│                  r1_inference (ROS2 node)                   │
│                                                             │
│   sdk_bridge ───▶ /r1/joint_states  ──▶ obs_builder ──▶ ONNX│
│                ──▶ /r1/imu                                  │
│                                                             │
│   ONNX(STAND) ─┐                                            │
│   ONNX(WALK)  ─┼─▶ blender(α) ─▶ joint_targets ─▶ sdk_bridge│
│   ONNX(MADRE) ─┘                                            │
│                                                             │
│   Safety FSM, E-stop watcher, Diagnostics                   │
└─────────────────────────────────────────────────────────────┘
```

Paquetes ROS2 (en [`codigos/ros2_ws/src/`](./codigos/ros2_ws/src/)):

| Paquete | Rol |
|---------|-----|
| `r1_msgs` | mensajes custom (`R1Command`, `R1State`, `R1Skill`, `FootContact`) |
| `r1_inference` | nodo principal: ONNX + blending + sdk_bridge |
| `r1_sim_bridge` | nodo equivalente pero contra Isaac Sim (en lugar del SDK) |
| `r1_teleop` | publica `/r1/target_pose` desde teclado/joystick |
| `r1_bringup` | launch files que coordinan los anteriores |

---

## 2. `r1_msgs` — mensajes custom

Defs en [`codigos/ros2_ws/src/r1_msgs/msg/`](./codigos/ros2_ws/src/r1_msgs/msg/). Ejemplo:

```
# r1_msgs/msg/R1Command.msg
std_msgs/Header header
geometry_msgs/Pose2D target_pose      # x*, y*, ψ*
float32 max_speed                     # m/s opcional
string skill_hint                     # "auto", "stand", "walk", "stair"
```

```
# r1_msgs/msg/R1State.msg
std_msgs/Header header
sensor_msgs/JointState joints
sensor_msgs/Imu imu
geometry_msgs/Pose root_pose
geometry_msgs/Twist root_vel
bool[] foot_contact
float32 base_height
uint8 fsm_state                        # POWER_ON, STANDBY, READY, ...
```

---

## 3. `r1_inference` — nodo principal

Esqueleto:

```python
# inference_node.py
import os, time, yaml
import numpy as np
import onnxruntime as ort

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy

from sensor_msgs.msg import JointState, Imu
from geometry_msgs.msg import Pose2D
from std_msgs.msg import String

from r1_msgs.msg import R1State

class R1InferenceNode(Node):
    def __init__(self):
        super().__init__("r1_inference")

        # Params
        self.declare_parameter("onnx_stand", "/home/usuario/r1_workspace/policies/stand_v1.onnx")
        self.declare_parameter("onnx_walk",  "/home/usuario/r1_workspace/policies/walk_v1.onnx")
        self.declare_parameter("inference_rate_hz", 50.0)
        self.declare_parameter("joint_order_yaml",
                               "/home/usuario/r1_workspace/ros2_ws/src/r1_bringup/config/joint_order_map.yaml")

        # Sessions ONNX (CUDA)
        self.sess_stand = ort.InferenceSession(
            self.get_parameter("onnx_stand").value,
            providers=["CUDAExecutionProvider", "CPUExecutionProvider"],
        )
        self.sess_walk = ort.InferenceSession(
            self.get_parameter("onnx_walk").value,
            providers=["CUDAExecutionProvider", "CPUExecutionProvider"],
        )

        # State buffers
        self.last_joint_state = None
        self.last_imu = None
        self.target_pose = Pose2D()
        self.skill = "auto"
        self.estopped = False
        self.prev_actions = np.zeros(26, dtype=np.float32)

        # Joint order map (sim → sdk)
        with open(self.get_parameter("joint_order_yaml").value) as f:
            self.joint_map = yaml.safe_load(f)
        # Construir índice inverso para reordenar
        # ...

        # Subs
        self.sub_js   = self.create_subscription(JointState, "/r1/joint_states", self._on_js, 10)
        self.sub_imu  = self.create_subscription(Imu, "/r1/imu", self._on_imu, 10)
        self.sub_tgt  = self.create_subscription(Pose2D, "/r1/target_pose", self._on_target, 10)
        self.sub_sk   = self.create_subscription(String, "/r1/skill", self._on_skill, 10)

        # Pub
        self.pub_cmd  = self.create_publisher(JointState, "/r1/joint_command", 10)

        # Timer de inferencia
        rate = self.get_parameter("inference_rate_hz").value
        self.timer = self.create_timer(1.0 / rate, self._tick)

        self.get_logger().info(f"r1_inference @ {rate} Hz, listo.")

    def _on_js(self, msg):  self.last_joint_state = msg
    def _on_imu(self, msg): self.last_imu = msg
    def _on_target(self, msg): self.target_pose = msg
    def _on_skill(self, msg):  self.skill = msg.data

    # ---------- Inferencia ----------
    def _build_obs_stand(self):
        # 88 dims: gravedad, ang/lin vel, joint pos/vel, prev_act, feet_dist
        # ... (ver doc 02 §2 Windows)
        ...

    def _build_obs_walk(self):
        # 97 dims: 88 + 9 cmd
        ...

    def _select_skill(self) -> str:
        """FSM auto. Usar self.skill si != 'auto'."""
        if self.skill != "auto":
            return self.skill
        d = np.hypot(
            self.target_pose.x - self.root_xy[0],
            self.target_pose.y - self.root_xy[1],
        )
        if d < 0.3: return "stand"
        return "walk"

    def _tick(self):
        if self.estopped or self.last_joint_state is None or self.last_imu is None:
            return

        skill = self._select_skill()

        if skill == "stand":
            obs = self._build_obs_stand().astype(np.float32)[None]
            action = self.sess_stand.run(None, {"obs": obs})[0][0]
        else:  # walk
            obs = self._build_obs_walk().astype(np.float32)[None]
            action = self.sess_walk.run(None, {"obs": obs})[0][0]

        # Reordenar sim → sdk
        action_sdk = self._reorder_for_sdk(action)

        # Aplicar action_scale + clamp + offset desde default pose
        # ... (idéntico a _apply_action del env)

        # Publicar como JointState (positions = targets)
        out = JointState()
        out.header.stamp = self.get_clock().now().to_msg()
        out.name     = self.joint_names_sdk
        out.position = action_sdk.tolist()
        self.pub_cmd.publish(out)

        self.prev_actions = action

def main(args=None):
    rclpy.init(args=args)
    node = R1InferenceNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
```

> Implementación completa en [`codigos/ros2_ws/src/r1_inference/r1_inference/inference_node.py`](./codigos/ros2_ws/src/r1_inference/r1_inference/inference_node.py).

---

## 4. SDK bridge (Unitree DDS ↔ ROS2)

```python
# sdk_bridge.py
from unitree_sdk2py.core.channel import ChannelPublisher, ChannelSubscriber, ChannelFactoryInitialize
from unitree_sdk2py.idl.unitree_hg.msg.dds_ import LowState_, LowCmd_

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState, Imu

class R1SdkBridge(Node):
    def __init__(self):
        super().__init__("r1_sdk_bridge")
        self.declare_parameter("network_iface", "eth0")
        ChannelFactoryInitialize(0, self.get_parameter("network_iface").value)

        # Pub ROS2
        self.pub_js  = self.create_publisher(JointState, "/r1/joint_states", 10)
        self.pub_imu = self.create_publisher(Imu,        "/r1/imu",          10)

        # Sub ROS2 → DDS
        self.sub_cmd = self.create_subscription(JointState,
            "/r1/joint_command", self._on_cmd, 10)

        # DDS sub
        self.sub_state = ChannelSubscriber("rt/lowstate", LowState_)
        self.sub_state.Init(self._on_state, 10)

        # DDS pub
        self.pub_cmd_dds = ChannelPublisher("rt/lowcmd", LowCmd_)
        self.pub_cmd_dds.Init()

        self._last_lowcmd = LowCmd_()

    def _on_state(self, msg: LowState_):
        # Joint states
        js = JointState()
        js.header.stamp = self.get_clock().now().to_msg()
        js.name = self._joint_names_sdk
        js.position = [m.q  for m in msg.motor_state[:26]]
        js.velocity = [m.dq for m in msg.motor_state[:26]]
        js.effort   = [m.tau_est for m in msg.motor_state[:26]]
        self.pub_js.publish(js)

        # IMU
        imu = Imu()
        imu.header.stamp = self.get_clock().now().to_msg()
        imu.linear_acceleration.x = msg.imu_state.accelerometer[0]
        imu.linear_acceleration.y = msg.imu_state.accelerometer[1]
        imu.linear_acceleration.z = msg.imu_state.accelerometer[2]
        imu.angular_velocity.x = msg.imu_state.gyroscope[0]
        imu.angular_velocity.y = msg.imu_state.gyroscope[1]
        imu.angular_velocity.z = msg.imu_state.gyroscope[2]
        # quaternion
        imu.orientation.w = msg.imu_state.quaternion[0]
        imu.orientation.x = msg.imu_state.quaternion[1]
        imu.orientation.y = msg.imu_state.quaternion[2]
        imu.orientation.z = msg.imu_state.quaternion[3]
        self.pub_imu.publish(imu)

    def _on_cmd(self, msg: JointState):
        # Tomar position como target del PD
        for i, q in enumerate(msg.position[:26]):
            self._last_lowcmd.motor_cmd[i].q   = float(q)
            self._last_lowcmd.motor_cmd[i].dq  = 0.0
            self._last_lowcmd.motor_cmd[i].kp  = self._pd_kp[i]
            self._last_lowcmd.motor_cmd[i].kd  = self._pd_kd[i]
            self._last_lowcmd.motor_cmd[i].tau = 0.0
        self.pub_cmd_dds.Write(self._last_lowcmd)
```

---

## 5. Teleop simple

```python
# r1_teleop/teleop_keyboard.py
import sys, select, termios, tty
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Pose2D

class TeleopNode(Node):
    def __init__(self):
        super().__init__("r1_teleop")
        self.pub = self.create_publisher(Pose2D, "/r1/target_pose", 10)
        self.target = Pose2D()
        self.step = 0.5
        self.timer = self.create_timer(0.1, self._tick)

    def _tick(self):
        if select.select([sys.stdin], [], [], 0)[0]:
            ch = sys.stdin.read(1).lower()
            if ch == "w": self.target.x += self.step
            elif ch == "s": self.target.x -= self.step
            elif ch == "a": self.target.y -= self.step
            elif ch == "d": self.target.y += self.step
            elif ch == "0":
                # detener
                ...
            elif ch == "q":
                rclpy.shutdown()
            self.pub.publish(self.target)
            self.get_logger().info(f"target=({self.target.x:+.2f},{self.target.y:+.2f})")

def main():
    rclpy.init()
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    tty.setcbreak(fd)
    try:
        node = TeleopNode()
        rclpy.spin(node)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)
```

---

## 6. Launch files

`r1_bringup/launch/real.launch.py`:

```python
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(package="r1_inference", executable="sdk_bridge",
             name="r1_sdk_bridge", output="screen"),

        Node(package="r1_inference", executable="inference_node",
             name="r1_inference", output="screen",
             parameters=[{
                 "onnx_stand": "/home/usuario/r1_workspace/policies/stand_v1.onnx",
                 "onnx_walk":  "/home/usuario/r1_workspace/policies/walk_v1.onnx",
                 "inference_rate_hz": 50.0,
             }]),

        Node(package="r1_teleop", executable="teleop_keyboard",
             name="r1_teleop", output="screen", emulate_tty=True),
    ])
```

Lanzar todo:

```bash
ros2 launch r1_bringup real.launch.py
```

---

## 7. Diagnostics y monitoreo

Publicar `/diagnostics` con `diagnostic_msgs`:

```python
from diagnostic_msgs.msg import DiagnosticArray, DiagnosticStatus, KeyValue

# En el inference_node:
def _publish_diag(self):
    msg = DiagnosticArray()
    msg.header.stamp = self.get_clock().now().to_msg()
    s = DiagnosticStatus()
    s.name  = "r1_inference"
    s.level = DiagnosticStatus.OK
    s.message = "running"
    s.values = [
        KeyValue(key="inference_rate_hz", value=f"{self._actual_rate:.2f}"),
        KeyValue(key="skill",             value=self.skill),
        KeyValue(key="estopped",          value=str(self.estopped)),
        KeyValue(key="last_action_max",   value=f"{abs(self.prev_actions).max():.3f}"),
    ]
    msg.status.append(s)
    self.pub_diag.publish(msg)
```

Visualizar:

```bash
ros2 run rqt_robot_monitor rqt_robot_monitor
```

---

## 8. Recording y replay

Antes y durante todo deploy, **graba un rosbag**:

```bash
ros2 bag record -a -o run_$(date +%Y%m%d_%H%M%S)
```

Replay para debug offline:

```bash
ros2 bag play run_20260427_1530
ros2 run rqt_plot rqt_plot /r1/joint_states/position[3]
```

---

## 9. Anti-patrones

- **No publicar a 1 kHz desde Python** — el `sdk_bridge` debe correr al ritmo del SDK (típicamente 500–1000 Hz). Para Python que cumpla, usa `multiprocessing` o C++.
- **No olvidar el `kp/kd`** del PD — si los pones a 0 el robot no responde a posiciones.
- **No publicar comandos sin `header.stamp`** — el SDK puede ignorarlos.
- **No reusar el ONNX session entre threads sin lock** — onnxruntime no es thread-safe en algunos providers.

Próximo → [09_Despliegue_Robot_Real.md](./09_Despliegue_Robot_Real.md).
