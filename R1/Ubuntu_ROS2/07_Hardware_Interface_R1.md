# 07 — Interfaz de hardware con el Unitree R1

> El R1 es un humanoide de 26 DOF de Unitree (la H1 de menor escala / heredera del lineup actual). El SDK oficial expone los joints, IMU y contactos por DDS / ETH. Esta guía describe la conexión y los datos.

> ⚠ Las URLs y nombres de paquetes pueden variar según la fecha — verifica con la documentación oficial de Unitree para tu unidad concreta. La estructura de la interfaz es estable.

---

## 1. Conexión física

| Modo | Cable | Velocidad | Uso |
|------|-------|----------:|-----|
| Ethernet directo | RJ-45 entre NUC/Jetson y robot | 1 Gbps | recomendado para deploy |
| USB-C (debug) | tipo 3.1 | 5 Gbps | bring-up inicial / firmware update |
| Wi-Fi | router AP del robot | 50–100 Mbps | tele-op a distancia (latencia variable) |

**Topología recomendada**:

```
[ NUC / Jetson Orin ]──ETH──[ R1 ]
        │
        └── USB Joystick / Teleop
        └── Battery / Power
```

> El **NUC i7** es el "compute brain" externo: corre el nodo de inferencia ONNX, el bridge a Isaac Sim, y publica/suscribe los tópicos. El R1 expone su SDK por DDS sobre la red.

---

## 2. Configurar la red

Asumiendo la IP del R1 = `192.168.123.161` (default Unitree):

```bash
sudo ip addr add 192.168.123.222/24 dev eth0
sudo ip route add 192.168.123.0/24 dev eth0
ping 192.168.123.161        # debe responder
```

Persistente con NetworkManager:

```bash
sudo nmcli connection add type ethernet ifname eth0 con-name r1-link \
     ipv4.method manual ipv4.addresses 192.168.123.222/24
sudo nmcli connection up r1-link
```

---

## 3. Variables de entorno del SDK

```bash
# en .bashrc
export UNITREE_NETWORK_INTERFACE=eth0
export UNITREE_DOMAIN_ID=42       # debe coincidir con el del robot (consultar la unidad)
export ROS_DOMAIN_ID=42
```

---

## 4. Estructura del SDK Python

```python
# unitree_sdk2_python — ejemplo simplificado
from unitree_sdk2py.core.channel import ChannelPublisher, ChannelSubscriber, ChannelFactoryInitialize
from unitree_sdk2py.idl.unitree_hg.msg.dds_ import LowState_, LowCmd_, MotorState_, MotorCmd_

ChannelFactoryInitialize(0, "eth0")

# Suscripción a estado de bajo nivel
def on_low_state(msg: LowState_):
    print("IMU acc:", msg.imu_state.accelerometer)
    for i, m in enumerate(msg.motor_state):
        print(f"  joint[{i}] q={m.q:+.3f} dq={m.dq:+.3f} torque={m.tau_est:+.2f}")

sub = ChannelSubscriber("rt/lowstate", LowState_)
sub.Init(on_low_state, 10)

# Publisher de comandos
pub = ChannelPublisher("rt/lowcmd", LowCmd_)
pub.Init()

cmd = LowCmd_()
for i in range(26):
    cmd.motor_cmd[i].q   = 0.0       # target pos
    cmd.motor_cmd[i].dq  = 0.0
    cmd.motor_cmd[i].kp  = 50.0
    cmd.motor_cmd[i].kd  = 2.0
    cmd.motor_cmd[i].tau = 0.0       # feedforward torque
pub.Write(cmd)
```

> Los nombres exactos (`unitree_hg`, `LowState_`, `motor_cmd`) pueden variar según la generación. Para la H1/G1/R1 usar el namespace `unitree_hg` (humanoid). Para Go2, `unitree_go`.

---

## 5. Mapeo de joints sim ↔ real

**Crítico**. El orden de joints en el USD puede diferir del que expone el SDK. Crea `joint_order_map.yaml`:

```yaml
# r1_bringup/config/joint_order_map.yaml
# index_sim: nombre_sdk
0:  "left_hip_pitch"
1:  "left_hip_roll"
2:  "left_hip_yaw"
3:  "left_knee"
4:  "left_ankle_pitch"
5:  "left_ankle_roll"
6:  "right_hip_pitch"
7:  "right_hip_roll"
8:  "right_hip_yaw"
9:  "right_knee"
10: "right_ankle_pitch"
11: "right_ankle_roll"
12: "torso_yaw"
13: "left_shoulder_pitch"
14: "left_shoulder_roll"
15: "left_shoulder_yaw"
16: "left_elbow"
17: "left_wrist_yaw"
18: "left_wrist_pitch"
19: "left_wrist_roll"
20: "right_shoulder_pitch"
21: "right_shoulder_roll"
22: "right_shoulder_yaw"
23: "right_elbow"
24: "right_wrist_yaw"
25: "right_wrist_pitch"
# 26: "right_wrist_roll"  ← si tu R1 tiene 26 DOF total
```

> Verificar con `print(robot.data.joint_names)` en sim y comparar contra el nombre que devuelve el SDK al iterar `motor_state[i].name`.

Esto se carga desde el nodo de inferencia para reordenar la salida del policy a la convención del SDK (ver [doc 08](./08_Nodos_ROS2_Inferencia.md)).

---

## 6. Ganancias de PD recomendadas (puntos de partida)

| Joint group | kp | kd |
|-----|---:|---:|
| Hip pitch/roll | 100 | 4 |
| Hip yaw | 60 | 3 |
| Knee | 120 | 5 |
| Ankle pitch/roll | 50 | 2 |
| Torso yaw | 80 | 3 |
| Shoulder | 60 | 2 |
| Elbow / Wrist | 40 | 1.5 |

> Ajustar tras el primer dry-run. Demasiado kp = vibración; demasiado bajo = el robot no llega al target.

---

## 7. Topics ROS2 mapeados al SDK

`r1_inference` traduce DDS Unitree ↔ ROS2:

| DDS Unitree (rt/...) | ROS2 (/r1/...) |
|----------------------|----------------|
| `rt/lowstate` | `/r1/joint_states`, `/r1/imu` |
| `rt/sportmodestate` | `/r1/sport_state` |
| `rt/lowcmd` | (publicado desde inference: `/r1/joint_command` → SDK) |

El bridge SDK ↔ ROS2 vive en [`codigos/ros2_ws/src/r1_inference/r1_inference/sdk_bridge.py`](./codigos/ros2_ws/src/r1_inference/r1_inference/sdk_bridge.py).

---

## 8. Modo "Damping" / "Zero torque" / "Standby"

El SDK expone modos seguros:

```python
from unitree_sdk2py.idl.unitree_api.msg.dds_ import Request_, Response_

# Damping mode (motores frenan, no producen movimiento)
cmd = LowCmd_()
for i in range(26):
    cmd.motor_cmd[i].q  = 0.0
    cmd.motor_cmd[i].kp = 0.0
    cmd.motor_cmd[i].kd = 5.0   # solo damping
pub.Write(cmd)
```

> **SIEMPRE** entrar al robot por **damping mode** antes de soltarlo a tierra. Si el motor tira con kp altos antes de tener buena pose, puede saltar.

---

## 9. Botón de emergencia

El R1 tiene **botón físico** de E-stop. ¡Tenerlo accesible en todo momento!

Cuando se presiona:
- Se cortan los motores.
- El SDK publica `motor_state[*].mode = 0`.
- Tu nodo de inferencia debe **detectar esto y suspender la publicación de comandos**.

Listener del E-stop en `inference_node.py`:

```python
def low_state_callback(msg):
    if any(m.mode == 0 for m in msg.motor_state):
        self.get_logger().warn("E-STOP detectado — suspendiendo inferencia")
        self.estopped = True
```

---

## 10. Estados del robot (FSM seguro)

```
[ POWER_ON ]
      ↓ (inicialización SDK + ROS2)
[ STANDBY (damping) ]
      ↓ (operador valida visualmente)
[ READY (kp suaves) ]
      ↓ (lanzar policy stand)
[ STANDING ]
      ↓ (recibir cmd target_pose)
[ WALKING ]
      ↓ (cmd skill=stand)
[ STANDING ]
      ↓ (operador apaga)
[ STANDBY ]
      ↓
[ POWER_OFF ]
```

Cada transición → log + verificación. Implementado en `r1_bringup/scripts/state_machine.py`.

---

## 11. Anti-patrones

- **No conectar Ethernet con motores energizados** — pueden generar transitorios eléctricos.
- **No publicar lowcmd antes de recibir el primer lowstate** — el SDK necesita sincronía inicial.
- **No ignorar las temperaturas** (`motor_state[i].temperature`). Sobrecalentamiento > 80°C → parar.
- **No saltarte el `damping mode`** al iniciar/finalizar.

Próximo → [08_Nodos_ROS2_Inferencia.md](./08_Nodos_ROS2_Inferencia.md).
