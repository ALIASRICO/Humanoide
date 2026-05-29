# 10 — Troubleshooting (Ubuntu + ROS2 + Sim2Real)

> Lista de errores comunes que hemos visto y cómo resolverlos rápido. Ordenados por capa: SO → CUDA → Isaac → ROS2 → Sim2Real.

---

## 1. Sistema operativo

| Problema | Causa | Fix |
|---------|------|-----|
| Pantalla negra al boot tras instalar driver NVIDIA | Secure Boot bloqueando el módulo. | BIOS → desactivar Secure Boot o firmar el módulo MOK. |
| Wi-Fi no detectado | Driver Realtek/Intel no instalado. | `sudo apt install linux-firmware` y reboot. |
| `disk full` durante entrenamiento | Logs de Isaac Lab grandes (cientos MB/run). | Mover `logs/` a SSD externo o limpiar runs viejos. |
| Cifrado LUKS lento al boot | KDF demasiado pesado. | `cryptsetup luksChangeKey --pbkdf-memory 256000` |

---

## 2. NVIDIA / CUDA

| Problema | Síntoma | Fix |
|---------|---------|-----|
| `nvidia-smi`: command not found | Driver no instalado / mal cargado. | `sudo ubuntu-drivers autoinstall` + reboot. |
| `CUDA driver version is insufficient` | CUDA 12.x con driver < 535. | Actualizar driver. |
| `RuntimeError: CUDA out of memory` | Demasiados envs paralelos. | Bajar `--num_envs`. |
| GPU no detectada en docker | Falta `--gpus all` o `nvidia-container-toolkit`. | `sudo apt install nvidia-container-toolkit`. |
| `libcudnn8` not found | cuDNN no instalado. | `sudo apt install libcudnn8 libcudnn8-dev` |
| `Failed to initialize NVML` | Conflicto driver/userland. | Reboot. Si persiste, `sudo apt purge nvidia-* && reinstalar`. |

---

## 3. Isaac Sim / Isaac Lab

| Problema | Causa | Fix |
|---------|------|-----|
| `ImportError: cannot import name 'R1_CFG'` | Falta el asset / versión Lab antigua. | Usar el fallback defensivo (doc 10 §3 Windows). |
| GUI no abre, ventana negra | Wayland incompatible. | Cambiar a sesión Xorg en login screen. |
| `terrain_type='generator'` falla con `replicate_physics=False` | API forzosa. | `replicate_physics=True`. |
| Render lento headed | VSync de Omni. | `--headless` o desactivar VSync en `~/.local/share/ov/.../user.config.json`. |
| `cannot find isaacsim` tras `pip install` | Conda env equivocado. | `mamba activate env_isaaclab`. |
| Falta del USD `r1.usd` | No se copió tras la instalación. | Copiar de `space_r1/r1.usd` a `IsaacLab/source/isaaclab_assets/data/Robots/Unitree/R1/`. |
| `policy.onnx` no se exporta en `play.py` | Versión `rsl-rl-lib` antigua. | `pip install -U rsl-rl-lib`. |

---

## 4. ROS2

| Problema | Síntoma | Fix |
|---------|---------|-----|
| `ros2: command not found` | Falta source. | `source /opt/ros/humble/setup.bash`. |
| Talker/listener no se ven | DOMAIN_ID o RMW distinto. | Igualar `ROS_DOMAIN_ID` y `RMW_IMPLEMENTATION` en ambos terminales. |
| `colcon build`: paquete no encontrado | `rosdep install` no ejecutado. | `rosdep install --from-paths src --ignore-src -r -y`. |
| `colcon build` con conda env activo falla | Choque python apt vs python conda. | `mamba deactivate` antes de `colcon build`. |
| Mensajes custom no aparecen | Falta source del overlay. | `source install/setup.bash` tras build. |
| `tf` lento o roto | Reloj fuera de sync con `use_sim_time`. | Setear `use_sim_time` consistente en todos los nodos. |
| Discovery no funciona en LAN | Multicast bloqueado por firewall. | Probar `RMW_IMPLEMENTATION=rmw_cyclonedds_cpp` o desactivar UFW. |
| Nodo Python crashea con `rclpy.spin` | Excepción no atrapada en callback. | Envolver callback en try/except. |

---

## 5. Bridge Isaac Sim ↔ ROS2

| Problema | Causa | Fix |
|---------|------|-----|
| No publica nada al activar `omni.isaac.ros2_bridge` | Falta sourcear ROS2 antes de lanzar Isaac Sim. | `source /opt/ros/humble/setup.bash` en el shell, luego `isaacsim`. |
| `librmw_*.so: cannot open shared object` | LD_LIBRARY_PATH no incluye `/opt/ros/humble/lib`. | Source ROS2. |
| Tópicos a 200 Hz pero llegan a 60 | Buffer DDS lleno. | Reducir profundidad de QoS o subir `dds.xml` reliability=BEST_EFFORT. |
| `/clock` no se publica | Action graph mal configurado. | Crear nodo `ROS2 Publish Clock` en Isaac Sim Action Graph. |

---

## 6. SDK Unitree

| Problema | Síntoma | Fix |
|---------|---------|-----|
| `ChannelFactoryInitialize` cuelga | Iface mal escrita. | Verificar `ip a` y poner `eth0`/`enp...` correcto. |
| Sin datos en `rt/lowstate` | Domain ID distinto al del firmware. | Ver `UNITREE_DOMAIN_ID` en docs de tu unidad. |
| Comandos ignorados | Robot en modo "skill" alto (sport mode). | Pasar a "low-level" mode con `request:setMode` desde la API. |
| Robot vibra en damping | kd muy alto o conflicto de bus. | `kd=2-3` típico. Verificar que ningún otro proceso publique a `rt/lowcmd`. |
| Joint i mueve dirección invertida | Polaridad del USD vs. SDK opuesta. | Multiplicar action[i] *= -1 en el reorderer. |
| `temperature` > 75°C en motores | Inferencia con kp altos por mucho tiempo. | Damping mode entre tests; ventilar. |

---

## 7. ONNX / Inference

| Problema | Causa | Fix |
|---------|------|-----|
| `[ONNXRuntimeError] : 1 : FAIL` al cargar | ONNX exportado con versión distinta. | Re-exportar desde `play.py` con la `onnxruntime` que vas a usar. |
| Inferencia 30 Hz cuando esperabas 100 | CPU provider en lugar de GPU. | `providers=["CUDAExecutionProvider", "CPUExecutionProvider"]` y verificar `ort.get_device() == 'GPU'`. |
| Acción siempre cero | Normalizer no incluido. | Asegurar que `play.py` exportó con `normalizer`. |
| Acción tiene picos enormes | Falta `np.clip(action, -1, 1)`. | Aplicar clip en el inference_node. |
| Output shape (26,) en lugar de (1,26) | Squeeze mal aplicado. | `action = sess.run(None, {"obs": obs})[0]` y `action[0]`. |

---

## 8. Sim2Real

| Síntoma | Causa probable | Solución |
|--------|---------------|----------|
| Funciona en sim, cae al primer paso real | DR insuficiente | Re-entrenar con DR fuerte (doc 06). |
| Robot oscila al pararse | Latencia no modelada | Añadir `JointCommandLagBuffer` en sim. |
| Camina pero "rengo" (asimétrico) | Bias de IMU no calibrado | Calibrar IMU al inicio + restar offset en obs. |
| Brazo se cruza al cuerpo | rew_left_arm_crossing no aplicado en último fine-tune | Añadir reward y re-entrenar. |
| Va más lento que comandado | action_scale mal calibrado | Sweep de `action_scale` ∈ [0.4, 0.7] en pruebas reales. |
| Stuck en escaleras | Heightmap no integrado en obs | Añadir RayCaster (doc 06 Windows). |

---

## 9. Logs útiles

```bash
# Logs de systemd
journalctl -u r1_inference -f
journalctl -u r1_inference -n 200 --no-pager

# Nodo ROS2 corriendo
ros2 node info /r1_inference

# Latencia de un tópico
ros2 topic delay /r1/joint_states

# Debug DDS
export RCUTILS_LOGGING_USE_STDOUT=1
export RCUTILS_LOGGING_BUFFERED_STREAM=0
export RCUTILS_CONSOLE_OUTPUT_FORMAT="[{severity}] [{time}] [{name}]: {message}"
```

---

## 10. Cuándo pedir ayuda

Si tras 30 min de troubleshooting no avanzas:

1. **Capturar logs**: `journalctl`, `ros2 bag record -a`, salida de `nvidia-smi`, `lsmod | grep nvidia`.
2. **Aislar el problema**: ¿es sim, ROS2, SDK, o policy?
3. **Reproducir minimal**: nodo ROS2 mínimo que muestre el bug.
4. **Comunidad**:
   - [forums.developer.nvidia.com](https://forums.developer.nvidia.com/c/agx-autonomous-machines/isaac/77) — Isaac Sim/Lab
   - [discourse.ros.org](https://discourse.ros.org) — ROS2
   - GitHub Issues de `IsaacLab`, `unitree_sdk2_python`

---

Si llegaste hasta aquí: tienes un robot R1 controlado por una política RL entrenada y desplegada en hardware real, comandable por WASD/coordenadas y orquestado por una política madre HRL. ¡Eso es la línea de meta!
