# 09 — Despliegue al robot físico

> Procedimiento end-to-end. Desde "tengo el ONNX en la mano" hasta "el R1 camina al objetivo". Sigue los pasos en orden, no saltes.

---

## 1. Pre-flight checklist

- [ ] Política STAND validada en sim (≥ 30 s sin caer en push 10 N).
- [ ] Política WALK validada en sim (alcanza target 5 m con DR completa).
- [ ] ONNX exportados (`stand_v1.onnx`, `walk_v1.onnx`) y movidos a `~/r1_workspace/policies/`.
- [ ] `joint_order_map.yaml` verificado contra `print(robot.joint_names)`.
- [ ] Workspace ROS2 compilado (`colcon build`) y `source install/setup.bash` activo.
- [ ] NUC/Jetson con Ethernet directo al R1 (`ping 192.168.123.161` OK).
- [ ] R1 cargado al 100%, batería verificada.
- [ ] Operador con **botón E-stop físico** en mano.
- [ ] Ambiente despejado en radio de 3 m.

---

## 2. Hardware target (compute brain)

### Opción A — NUC i7 con eGPU (RTX 4060)
- Más potencia para inferencia y debug.
- Tethered via Ethernet.

### Opción B — Jetson Orin Nano / NX
- On-board (montado en el R1).
- ROS2 Humble nativo.
- ONNX Runtime con TensorRT (más rápido que CUDA Provider).

Ambas opciones funcionan. Si vas a Jetson:

```bash
# Convertir ONNX a TensorRT engine
trtexec --onnx=stand_v1.onnx --saveEngine=stand_v1.trt --fp16
```

Y en el `inference_node.py`:
```python
self.sess = ort.InferenceSession("stand_v1.onnx",
    providers=["TensorrtExecutionProvider", "CUDAExecutionProvider", "CPUExecutionProvider"])
```

---

## 3. Bring-up paso a paso

### 3.1 Encender el robot

1. Encender la batería del R1.
2. Esperar el **beep** + LED verde.
3. Verificar que entra en `STANDBY (damping)` por defecto (no debería intentar moverse).

### 3.2 Conectar el NUC

```bash
ping 192.168.123.161           # robot responde
ros2 topic list                # debe estar vacío hasta lanzar bringup
```

### 3.3 Verificar SDK

```bash
mamba activate env_isaaclab
python -c "
from unitree_sdk2py.core.channel import ChannelFactoryInitialize, ChannelSubscriber
from unitree_sdk2py.idl.unitree_hg.msg.dds_ import LowState_

ChannelFactoryInitialize(0, 'eth0')
def cb(m): print('IMU acc:', m.imu_state.accelerometer); exit(0)
sub = ChannelSubscriber('rt/lowstate', LowState_)
sub.Init(cb, 10)
import time; time.sleep(2)
print('Sin datos — chequear cable / domain ID')
"
```

Debe imprimir el accelerometer una vez. Si no → revisar `UNITREE_NETWORK_INTERFACE`, `UNITREE_DOMAIN_ID`.

### 3.4 Lanzar el `sdk_bridge` solo (sin inferencia)

```bash
ros2 run r1_inference sdk_bridge
```

En otro terminal:

```bash
ros2 topic echo /r1/joint_states --once
```

Debes ver 26 joints con `position`, `velocity`, `effort`. Si no → bug en sdk_bridge / mapeo.

### 3.5 Calibración del joint_order_map

```bash
ros2 topic echo /r1/joint_states --once | head -50
# Comparar `name` con tus joint_names del USD del sim.
# Editar joint_order_map.yaml hasta que coincidan en orden.
```

### 3.6 Modo Damping → Ready (con kp suave)

Lanzar un script intermedio que pone kp=10, kd=2 (suave) y target = pose default:

```bash
ros2 run r1_bringup goto_default_pose
```

> Esto es lo más arriesgado del bring-up. **Tener al robot suspendido o sostenido a mano**.

### 3.7 Smoke test del policy STAND (suspendido)

Con el R1 suspendido en cama elástica o sostenido por correa:

```bash
ros2 launch r1_bringup test_stand.launch.py
# -- equivale a:
# ros2 run r1_inference inference_node --ros-args -p skill:="stand"
```

El robot debe **no oscilar**. Las articulaciones se mantienen casi inmóviles. Si vibra:
- Bajar `action_scale` en el cliente del policy (de 0.025 → 0.015).
- Bajar `kp` (de 100 → 80) en el SDK PD.
- Verificar polarity: si los joints se mueven en dirección invertida, hay un mapping con signo equivocado.

### 3.8 Bajar a tierra

Con el policy STAND aún corriendo:

1. Bajar suavemente al suelo. Pies tocan, cuerpo sigue erguido.
2. Soltar la correa (operador con E-stop).
3. Robot debe quedar parado solo.
4. Aplicar push lateral suave de 5–10 N. Debe recuperar.

### 3.9 Lanzar el bringup completo

```bash
ros2 launch r1_bringup real.launch.py
```

Esto inicia: `sdk_bridge`, `inference_node`, `teleop_keyboard`.

### 3.10 Comandar al robot

En el terminal de teleop:

```
W = adelante 0.5 m
A = izquierda 0.5 m
D = derecha 0.5 m
S = atrás 0.5 m
0 = stop
```

El R1 camina al target. Si va a >0.3 m del target, la FSM cambia a `walk`. Cuando llega, vuelve a `stand`.

---

## 4. systemd para auto-arranque (deploy permanente)

`/etc/systemd/system/r1_inference.service` (también en [`codigos/systemd/r1_inference.service`](./codigos/systemd/r1_inference.service)):

```ini
[Unit]
Description=R1 Inference Stack
After=network-online.target

[Service]
Type=simple
User=usuario
Group=usuario
WorkingDirectory=/home/usuario/r1_workspace/ros2_ws
Environment="HOME=/home/usuario"
Environment="PATH=/home/usuario/miniforge3/envs/env_isaaclab/bin:/usr/bin:/bin"
Environment="ROS_DOMAIN_ID=42"
Environment="UNITREE_NETWORK_INTERFACE=eth0"
ExecStart=/bin/bash -c 'source /opt/ros/humble/setup.bash && \
                      source /home/usuario/r1_workspace/ros2_ws/install/setup.bash && \
                      ros2 launch r1_bringup real.launch.py'
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Activar:

```bash
sudo cp r1_inference.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable r1_inference
sudo systemctl start r1_inference

# Logs
journalctl -u r1_inference -f
```

---

## 5. Real-time priority (importante para 50–100 Hz estables)

```bash
# Dar al usuario permiso de RT
sudo bash -c 'echo "@usuario - rtprio 99" >> /etc/security/limits.conf'
sudo bash -c 'echo "@usuario - memlock unlimited" >> /etc/security/limits.conf'
```

En el `inference_node`, usar `chrt`:

```bash
sudo chrt -f 80 ros2 run r1_inference inference_node
```

O dentro del código:
```python
import os
os.sched_setscheduler(0, os.SCHED_FIFO, os.sched_param(80))
```

---

## 6. Métricas durante operación

```bash
ros2 topic hz /r1/joint_states           # debe estar a 500-1000 Hz
ros2 topic hz /r1/joint_command          # debe estar al inference_rate_hz (50)
ros2 topic hz /r1/imu                    # 200-500 Hz
ros2 run rqt_robot_monitor rqt_robot_monitor
```

---

## 7. Iteración: re-entrenar con datos reales

Tras la primera sesión exitosa:

1. **Grabar** un rosbag de 5 min con caminata variada.
2. Extraer `/r1/joint_states`, `/r1/imu`, `/r1/foot_contact` → CSV.
3. Comparar la distribución vs. los datos de sim. Buscar:
   - Outliers en velocidades de joint que no aparecen en sim.
   - IMU con sesgos sistemáticos (gravedad mal calibrada).
   - Tiempos de contacto distintos.
4. **Ajustar el USD/EnvCfg** del sim para reflejar lo medido.
5. **Re-entrenar** (resume con DR ajustado).

Este loop sim ↔ real es lo que hace que la política mejore con cada iteración.

---

## 8. Procedimiento de cierre seguro

```bash
# 1) Comandar stop
ros2 topic pub /r1/skill std_msgs/String "data: 'stand'" --once

# 2) Esperar que el robot quede parado en posición neutral

# 3) Detener servicios
sudo systemctl stop r1_inference
# o si lo lanzaste con `ros2 launch`, Ctrl+C

# 4) El robot quedará en damping mode automáticamente

# 5) Apagar batería del robot
```

---

## 9. Troubleshooting de campo

| Síntoma | Causa | Acción |
|--------|------|--------|
| Robot vibra al pararse | kp alto / action_scale alto | Bajar ambos un 20% |
| Cae al primer push | DR insuficiente | Re-entrenar con DR más fuerte |
| Camina en círculos | Yaw mal calibrado en obs | Verificar `target_yaw_w` y mapping de IMU quaternion |
| Inferencia va a 30 Hz en lugar de 50 | onnxruntime sin GPU | Verificar `providers=["CUDAExecutionProvider"]` y `nvidia-smi` |
| ROS2 topics vacíos | DOMAIN_ID o RMW desalineados | Verificar `.bashrc` en NUC y robot |
| `unitree_sdk2_python` no compila | Falta `cyclonedds` | `pip install cyclonedds` o seguir docs Unitree |

---

## 10. Anti-patrones

- **No saltarte la cama elástica** en el primer test del policy stand.
- **No olvides** cerrar con damping mode.
- **No corras inferencia y entrenamiento simultáneo** en la misma GPU si el robot está activo — las paradas por OOM son catastróficas.
- **No despliegues sin grabar rosbag**. Sin él, no puedes debuggear post-mortem.

Próximo → [10_Troubleshooting_Ubuntu.md](./10_Troubleshooting_Ubuntu.md).
