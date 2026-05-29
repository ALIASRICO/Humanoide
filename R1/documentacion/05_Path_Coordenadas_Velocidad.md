# 05 — Path planning por coordenadas + velocidad emergente

> Resumen ejecutivo del approach (basado en `recomendaciones_awsd.md`):
>
> *"Cambiar **seguimiento de velocidad** por **formulación de navegación**: cada tecla WASD actualiza una posición objetivo `p*` y una orientación `ψ*`; el robot decide la velocidad para llegar a ella en el tiempo previsto, frenando en terreno difícil y acelerando en plano."*

Este es el cambio de paradigma vs. los locomotion policies clásicos:

| Paradigma viejo | Paradigma nuevo (este proyecto) |
|----------------|------------------------------|
| `cmd = (vx_des, vy_des, wz_des)` | `cmd = (x*, y*, ψ*, t_remain)` |
| Recompensa = error de velocidad | Recompensa = llegar a `p*` |
| Robot va siempre a velocidad fija | Robot **decide** su velocidad |
| Falla en terreno difícil (sigue forzando vel) | Frena automáticamente al detectar dificultad |

---

## 1. Observaciones para locomoción por coordenadas

`observation_space = 97` (88 base de standing + 9 de comando):

| Bloque | Dim | Significado |
|-------|----:|-------------|
| (igual a standing) | 88 | gravedad + ang/lin vel + joint pos/vel + prev actions + feet dist |
| `target_pos_b` | 2 | posición del target en frame del robot (x_b, y_b) |
| `target_yaw_b` | 1 | error de orientación (cos, sin) → 1 dim para diff |
| `target_distance` | 1 | norma del vector target |
| `time_remaining` | 1 | t restante para llegar (s) |
| `terrain_height_under_feet` | 4 | altura debajo de cada esquina del soporte (mide *roughness*) |

Total = 88 + 2 + 1 + 1 + 1 + 4 = **97** ← coincide con `Linear(in_features=97, out_features=256)` que se ve en el log de `play_wasd.py`.

---

## 2. Generación de targets durante el entrenamiento

Para que el robot aprenda **omnidireccionalidad**, los targets deben muestrearse en *coordenadas polares uniformes*:

```python
def _resample_targets(self, env_ids):
    # r ~ U(1, 5) m, phi ~ U(0, 2pi)
    r   = torch.rand(len(env_ids), device=self.device) * 4.0 + 1.0
    phi = torch.rand(len(env_ids), device=self.device) * 2 * torch.pi
    self.target_pos_w[env_ids, 0] = self.robot.data.root_pos_w[env_ids, 0] + r * torch.cos(phi)
    self.target_pos_w[env_ids, 1] = self.robot.data.root_pos_w[env_ids, 1] + r * torch.sin(phi)
    # ψ* aleatorio entre [-π, π]
    self.target_yaw_w[env_ids] = (torch.rand(len(env_ids), device=self.device) - 0.5) * 2 * torch.pi
    # Tiempo objetivo: ajustar para velocidad media ~ 1 m/s
    self.target_t_remain[env_ids] = r / 1.0   # s
```

Llamar en `_reset_idx` y también cuando el robot llega:

```python
arrived = torch.norm(self.robot.data.root_pos_w[:, :2] - self.target_pos_w[:, :2], dim=-1) < 0.3
if self.cfg.target_resample_on_arrival:
    self._resample_targets(arrived.nonzero().flatten())
```

> En `play_wasd.py` ponemos `target_resample_on_arrival = False` para que el target se respete (el usuario lo controla por teclado).

---

## 3. Aumentación de datos por simetría

El paper de fuente (`Learning Agile Locomotion on Risky Terrains`, [revistas.udistrital](https://revistas.udistrital.edu.co/index.php/Tecnura/article/view/8152/10423)) advierte que las políticas **se sesgan a una dirección** si no se hace simetría artificial.

Solución: **mirror augmentation**.

```python
# En el rollout buffer del PPO, después de recoger experiencia:
def mirror_batch(obs, actions):
    """Reflejar L<->R: invierte joint_pos de izquierda↔derecha y signo de Y."""
    # Construir índices de joints simétricos (precomputado por nombre)
    # left_indices, right_indices (cada uno len = 13)
    obs_m = obs.clone()
    obs_m[:, JOINT_POS_SLICE][:, left_indices]  =  obs[:, JOINT_POS_SLICE][:, right_indices]
    obs_m[:, JOINT_POS_SLICE][:, right_indices] =  obs[:, JOINT_POS_SLICE][:, left_indices]
    # Reflejar Y (lateral) en gravedad y velocidades
    obs_m[:, GRAV_Y_IDX] *= -1
    obs_m[:, ANG_X_IDX]  *= -1
    obs_m[:, ANG_Z_IDX]  *= -1
    obs_m[:, LIN_Y_IDX]  *= -1
    obs_m[:, TARGET_Y_B] *= -1
    obs_m[:, TARGET_YAW_B] *= -1

    actions_m = actions.clone()
    actions_m[:, left_indices]  = actions[:, right_indices]
    actions_m[:, right_indices] = actions[:, left_indices]
    return obs_m, actions_m

# Luego en el loop de PPO:
obs_aug = torch.cat([obs, mirror_batch(obs, actions)[0]], dim=0)
act_aug = torch.cat([actions, mirror_batch(obs, actions)[1]], dim=0)
```

Resultado: el dataset efectivo es 2× sin más simulación. Quita el sesgo direccional en ~30% menos iters.

> Para 4× (left/right + forward/back) hace falta también invertir X. Ojo con la consistencia entre obs y actions.

---

## 4. Función de recompensa para WASD

```python
# === TASK REWARD: llegada al target ===
dist_xy = torch.norm(self.target_pos_w[:, :2] - self.robot.data.root_pos_w[:, :2], dim=-1)
arrived = (dist_xy < 0.3).float()
rew_arrival = self.cfg.rew_scale_arrival * arrived  # +50.0 al llegar

# === EXPLORATION REWARD (solo iters 0–150): "move in direction" ===
target_dir = (self.target_pos_w[:, :2] - self.robot.data.root_pos_w[:, :2])
target_dir = target_dir / (torch.norm(target_dir, dim=-1, keepdim=True) + 1e-6)
vel_xy = self.robot.data.root_lin_vel_w[:, :2]
vel_proj = (vel_xy * target_dir).sum(dim=-1)  # componente hacia el target
rew_move_to = self.cfg.rew_scale_move_to * vel_proj * (self.iter_id < 150).float()

# === STAND STILL REWARD (al llegar) ===
near = (dist_xy < 0.4).float()
rew_stand_still = -self.cfg.rew_scale_stand_still * near * torch.norm(vel_xy, dim=-1)

# === ORIENTATION TRACK ===
yaw_err = (self.target_yaw_w - self._compute_yaw())
yaw_err = (yaw_err + torch.pi) % (2 * torch.pi) - torch.pi  # wrap
rew_yaw = self.cfg.rew_scale_yaw * torch.exp(-torch.square(yaw_err) / 0.5)

# === SMOOTHNESS ===
rew_action_rate = -self.cfg.rew_scale_action_rate * torch.square(self.actions - self._previous_actions).sum(-1)

# === ALIVE / TERMINATION ===
rew_alive       =  self.cfg.rew_scale_alive * (1 - terminated.float())
rew_terminate   = -self.cfg.rew_scale_terminated * terminated.float()
```

Suma de escalas:

```python
rew_scale_arrival      = 50.0
rew_scale_move_to      =  2.0
rew_scale_stand_still  =  5.0
rew_scale_yaw          = 10.0
rew_scale_action_rate  =  0.05
rew_scale_alive        =  1.0
rew_scale_terminated   = 200.0
```

---

## 5. Velocidad emergente y adaptación a terreno

Si el robot tiene `time_remaining` y `target_distance` como inputs, **la velocidad emerge**: aprende que con t bajo y dist alta debe acelerar, y al revés. La clave es **no penalizar la velocidad alta** (no usar `rew_scale_lin_vel` negativo en este env). Solo penalizar **falta de progreso**:

```python
# Penalty si no progresa lo suficiente para llegar a tiempo
required_speed = dist_xy / torch.clamp(self.target_t_remain, min=0.1)
actual_speed   = vel_proj
shortfall = torch.clamp(required_speed - actual_speed, min=0.0)
rew_speed_shortfall = -1.0 * shortfall
```

En **terrenos difíciles** (rough, escaleras), la observación `terrain_height_under_feet` provoca que el actor reduzca acciones grandes → menor velocidad. Es comportamiento *emergente* — no se programa.

---

## 6. Control manual: `play_wasd.py`

Ya está en `space_r1/play_wasd.py`. Resumen de su funcionamiento:

```
MAIN THREAD          BG THREAD
(Isaac Sim)          (input)
   │                    │
   │  ←──── target ────┤  msvcrt: lee teclas WASD
   │                    │  queue.Queue thread-safe
   │  policy(obs)       │
   │  env.step(act)     │
   │                    │
   ├──── state ───────→ │  (robot_xy, target_xy, dist)
```

Modos:

1. **Coordenadas**: `coord> 1.0 0.5` → mueve el target +1m X, +0.5m Y desde el robot.
2. **Teclado** (msvcrt): `W/A/S/D` → delta target ±0.5 m, `0` = stop, `P` = print pos, `Q` = volver.
3. **Posición**: muestra robot/target/dist.
4. **Reset**: vuelve a (0,0).
5. **Salir**.

Uso:

```powershell
.\..\IsaacLab\isaaclab.bat -p play_wasd.py `
  --task=R1-Locomotion-Direct-v0 `
  --checkpoint=D:\space_r1\IsaacLab\logs\rsl_rl\r1_locomotion\2026-04-12_09-12-00\model_8000.pt `
  --step=0.5
```

> **Bug del repo arreglado** en este snapshot: `find_latest_checkpoint()` busca solo en `IsaacLab/logs/rsl_rl/` y `logs/rsl_rl/`; si tu run está en otra ruta, **pasa `--checkpoint`** explícito. Ver [doc 10](./10_Correcciones_Aplicadas.md).

---

## 7. Adaptación a terreno: heightmap como obs (extensión)

Para que el robot vea el terreno, agrega un `RayCaster` en el `EnvCfg`:

```python
from isaaclab.sensors import RayCasterCfg, patterns

ray_cfg = RayCasterCfg(
    prim_path="/World/envs/env_.*/R1/torso",
    update_period=1/50.0,
    offset=RayCasterCfg.OffsetCfg(pos=(0.0, 0.0, 1.0)),
    attach_yaw_only=True,
    pattern_cfg=patterns.GridPatternCfg(
        resolution=0.1,
        size=(1.6, 1.0),  # 1.6m frente, 1.0m ancho
    ),
    debug_vis=False,
    mesh_prim_paths=["/World/ground", "/World/envs/env_.*/Terrain"],
)
```

Y consumirla en `_get_observations`:

```python
heightmap = self._raycaster.data.ray_hits_w[:, :, 2] - self.robot.data.root_pos_w[:, 2:3]
heightmap = torch.clamp(heightmap, -0.5, 0.5)
```

> Esto es la base para la política de escaleras de [doc 06](./06_Playground_Terrenos.md).

---

## 8. Hiperparámetros recomendados para locomotion

| Param | Valor |
|------|------:|
| `num_envs` | 4096 |
| `num_steps_per_env` | 48 |
| `max_iterations` | 10000 |
| `actor/critic_hidden_dims` | [512, 256, 128] |
| `learning_rate` | 5e-4 |
| `entropy_coef` | 0.01 |
| `clip_param` | 0.2 |
| `desired_kl` | 0.01 |
| `gamma` | 0.99 |
| `lam` | 0.95 |
| `init_noise_std` | 1.0 |

---

## 9. Anti-patrones

- **No penalizar `lin_vel`** (como sí hacemos en standing). En locomotion la velocidad es la herramienta.
- **No usar `target_resample_on_arrival = True` en play**: el robot persigue eternamente.
- **No olvidar** que `target_pos_w` está en *world frame*; al pasarla a la red, hay que convertirla a *body frame* (rotar por el yaw del robot).
- **No usar contains** (terreno mesh) sin RayCaster — el robot no "ve" obstáculos invisibles.

Próximo paso → [06_Playground_Terrenos.md](./06_Playground_Terrenos.md).
