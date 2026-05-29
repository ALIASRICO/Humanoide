# 06 — Sim2Real: del checkpoint al robot físico

> El paso más difícil del proyecto. Un policy que va perfecto en sim cae al primer push real si no se domain-randomiza. Esta guía cubre la "receta" estándar.

---

## 1. Por qué falla la transferencia

| Fuente del gap | Impacto típico | Mitigación |
|----------------|---------------|-----------|
| Masas, fricción, inercia | grande | DR de masa ±15%, fricción U[0.4, 1.2] |
| Latencia del actuador | medio | Modelar lag 5–20 ms en sim |
| Ruido del IMU | medio | Añadir N(0, 0.01) a obs |
| Backlash en transmisiones | grande | Modelar histéresis + dead-band |
| Saturación de torque | grande | Clipear acciones a soft limits + torque limit real |
| Discretización del encoder | bajo | Round a step del encoder |
| Comm. delay (BMS / SDK) | medio | Buffer FIFO de obs (predict ahead) |
| Gravedad y orientación inicial | bajo | Reset con tilt aleatorio |

---

## 2. Domain Randomization (DR) — receta completa

En `R1StandingEnvCfg` (ya documentado en [doc 04 Windows](../04_Fine_Tuning.md) §5), pero más exhaustivo:

```python
# r1_standing_env_cfg.py — agregar al final
@configclass
class DRCfg:
    # Físico
    mass_torso_range:    tuple = (0.85, 1.15)    # ×nominal
    mass_arms_range:     tuple = (0.90, 1.10)
    mass_legs_range:     tuple = (0.90, 1.10)

    friction_static:     tuple = (0.4, 1.2)
    friction_dynamic:    tuple = (0.4, 1.2)
    restitution:         tuple = (0.0, 0.2)

    # Motor / actuator
    motor_strength_scale:tuple = (0.85, 1.15)    # gain del PD multiplicado
    motor_offset_rad:    tuple = (-0.02, 0.02)   # offset por joint
    motor_velocity_lag_steps: tuple = (1, 4)     # lag en steps de control

    # Sensor
    imu_noise_lin_accel: float = 0.05            # m/s²
    imu_noise_ang_vel:   float = 0.01            # rad/s
    joint_pos_noise:     float = 0.005           # rad
    joint_vel_noise:     float = 0.05            # rad/s

    # Comando
    cmd_lag_steps:       tuple = (0, 3)          # lag en target_pos
    cmd_dropout_prob:    float = 0.02            # se "pierde" un comando 2% del tiempo

    # External
    push_force_range:    tuple = (-15.0, 15.0)   # N
    push_interval_s:     tuple = (4.0, 12.0)
    gravity_perturbation:tuple = (0.95, 1.05)    # ×9.81
```

Aplicarlo en el env (ejemplo):

```python
def _resample_DR(self, env_ids):
    # Masa
    mass_scale = sample_uniform(*self.cfg.dr.mass_torso_range,
                                len(env_ids), self.device)
    self.robot.set_mass_scale(mass_scale, body_names=["torso"], env_ids=env_ids)

    # Fricción
    fr = sample_uniform(*self.cfg.dr.friction_static,
                        len(env_ids), self.device)
    self.scene.terrain.set_friction(fr, env_ids=env_ids)

    # Motor strength
    s = sample_uniform(*self.cfg.dr.motor_strength_scale,
                       (len(env_ids), len(self._joint_ids)), self.device)
    self.robot.set_actuator_gain_scale(s, env_ids=env_ids)
```

Resamplear en `_reset_idx`.

> Activa DR **solo después** de iter ~5000 (cuando ya hay una política base). Antes, el ruido impide el aprendizaje.

---

## 3. Calibración de masas/inercias (medir el real, ajustar el sim)

Para que el USD del Sim refleje al robot real:

1. **Pesar el robot** con balanza industrial.
2. **Medir longitudes** de cada eslabón (regla, calibrador).
3. **Estimar inercias** asumiendo cilindros/cubos.
4. **Editar el URDF** o el USD original (en Blender + Omniverse `Add → Physics → Mass Properties`).
5. **Re-exportar** y reemplazar `r1.usd`.

> Si solo tienes tiempo para una cosa: ajusta la **masa total**. Es la que más afecta.

---

## 4. Latencia: modelar el lag del actuador

```python
class JointCommandLagBuffer:
    """FIFO que retrasa los comandos por N steps."""
    def __init__(self, num_envs, num_joints, max_lag, device):
        self.buffer = torch.zeros(max_lag + 1, num_envs, num_joints, device=device)
        self.head   = 0
        self.lag    = torch.zeros(num_envs, dtype=torch.long, device=device)

    def push(self, commands):
        self.buffer[self.head] = commands
        self.head = (self.head + 1) % self.buffer.shape[0]

    def pop(self):
        idx = (self.head - 1 - self.lag) % self.buffer.shape[0]
        return self.buffer[idx, torch.arange(self.buffer.shape[1])]
```

Y en `_apply_action`:

```python
self._lag_buf.push(target_positions)
delayed = self._lag_buf.pop()
self.robot.set_joint_position_target(delayed, joint_ids=self._joint_ids)
```

Con `lag = sample_uniform(1, 4)` por env.

---

## 5. Privileged information / asymmetric actor-critic

El crítico puede ver más que el actor (ej. masas reales, fricción real). Ayuda a aprender DR sin que el actor se confunda:

```python
obs_groups = {
    "actor":  ["policy"],                   # solo lo que mide el robot real
    "critic": ["policy", "privileged"],     # incluye masas, fricción, lag
}
```

`privileged` se concatena con la obs normal solo en el critic.

---

## 6. Asymmetric noise schedule

```python
# pseudo-curriculum
def _DR_schedule(self):
    it = self.common_step_counter // 24
    if it < 5000:
        scale = 0.0          # sin DR
    elif it < 8000:
        scale = 0.5          # DR media
    else:
        scale = 1.0          # DR completa
    self.cfg.dr.imu_noise_lin_accel = 0.05 * scale
    self.cfg.dr.motor_strength_scale = (1.0 - 0.15*scale, 1.0 + 0.15*scale)
    # ...
```

---

## 7. Validar el ONNX antes del deploy

```bash
mamba activate env_isaaclab
python - <<'PY'
import onnxruntime as ort, numpy as np
sess = ort.InferenceSession("policies/stand_v1.onnx",
                            providers=["CUDAExecutionProvider"])
obs = np.zeros((1, 88), dtype=np.float32)
out = sess.run(None, {"obs": obs})[0]
print("Output shape:", out.shape, "dtype:", out.dtype)
print("Sample action:", out[0, :8])
PY
```

Debe imprimir `(1, 26)` (acción 26-dim).

---

## 8. Dry-run en bench (sin tocar el suelo)

Antes de lanzarlo a caminar:

1. Suspender el R1 en una **cama elástica de seguridad** o suspensión por correa.
2. Conectar el SDK, encender motores en modo "follow" (sin damping alto).
3. Lanzar el nodo de inferencia (ver [doc 08](./08_Nodos_ROS2_Inferencia.md)).
4. Observar: el robot debe **mantener su pose default sin oscilar**. Si vibra → bajar `action_scale` o subir `damping` en el config del SDK.

---

## 9. Calibración fina: sweeps en el robot real

Una vez en el suelo y caminando torpemente:

1. **Recorre 10 m** y compara distancia real vs. comandada → calibrar `action_scale` final.
2. **Aplica empujones laterales** y mide tiempo de recuperación.
3. **Itera**: re-entrena con el `r1.usd` corregido + DR ajustado a las observaciones reales.

---

## 10. Anti-patrones de sim2real

- **No exportar el ONNX sin normalizer**. Si el actor tenía `obs_normalizer`, debe estar incluido. `play.py` ya lo hace.
- **No olvidar el orden de joints**. El USD puede listar joints en orden distinto al SDK. Mantener un mapeo explícito (`joint_order_map.yaml`).
- **No correr DR muy alto desde iter 0** — la política nunca converge.
- **No omitir `safe joint limits`** en el robot real. El SDK ya los enforce, pero los acciones no clamped pueden saturar.
- **No transferir un policy de standing al robot sin pre-test en el banco**. Caer la primera vez te puede romper el mecanismo.

Próximo → [07_Hardware_Interface_R1.md](./07_Hardware_Interface_R1.md).
