# 04 — Fine-tuning de políticas para el R1

> Fine-tuning aquí significa **partir de un checkpoint ya válido** y mejorarlo: añadir empujones, terrenos, comandos de velocidad, sin destruir lo aprendido. Cubre tanto *resume* simple como *transfer* y *curriculum*.

Los repos guardan los checkpoints en:

```
D:\space_r1\IsaacLab\logs\rsl_rl\<experiment_name>\<YYYY-MM-DD_HH-MM-SS>\
   ├─ model_500.pt        ← cada save_interval
   ├─ model_1000.pt
   ├─ ...
   └─ exported\policy.pt  ← export para inference (lo crea play.py)
```

> El comentario *"`C:\space_r1\IsaacLab\logs\rsl_rl\r1_standing\2026-03-03_15-35-21`… esta es la dirección de la política que funcionó para una estabilización aunque extraña pero sin caídas"* (`revisionEntrenamiento.md`) — ese run es el **baseline a partir del cual se hace fine-tune**.

---

## 1. Resume puro (continuar el mismo entrenamiento)

```powershell
.\..\IsaacLab\isaaclab.bat -p .\scripts\rsl_rl\train.py `
  --task=R1Standing-Direct-v0 `
  --num_envs=4096 `
  --max_iterations=8000 `
  --resume `
  --load_run=2026-03-03_15-35-21 `
  --checkpoint=model_3500.pt `
  --headless
```

- `--resume` → indica al runner que cargue pesos en vez de inicializar.
- `--load_run` → nombre de la subcarpeta dentro de `logs/rsl_rl/r1_standing/`.
- `--checkpoint` → archivo concreto. Si se omite, toma el último.

> Lo que se *resume* incluye: pesos del actor/critic, optimizer state, normalizers. **No** se preserva el contador de iteraciones — para evitar que se detenga, sube `max_iterations`.

---

## 2. Transfer learning (cambiar la tarea, reusar pesos)

Útil cuando:

- Pasaste de `R1Standing-Direct-v0` (88 obs) a `R1-Locomotion-Direct-v0` (97 obs) y quieres aprovechar lo aprendido.
- Cambiaste rewards drásticamente y solo quieres mantener el "saber estar de pie".

Estrategia: **cargar pesos compatibles, reinicializar la última capa**.

```python
# scripts/rsl_rl/train.py — después de crear runner
def transfer_partial(runner, src_ckpt, freeze_first_n_layers=2):
    state = torch.load(src_ckpt, map_location=runner.device)
    actor = runner.alg.actor_critic.actor
    own = actor.state_dict()

    # Filtrar solo claves cuya forma coincide
    loaded = {k: v for k, v in state["model_state_dict"].items()
              if k in own and own[k].shape == v.shape}
    own.update(loaded)
    actor.load_state_dict(own)

    # Congelar primeras N capas
    layers_seen = 0
    for p in actor.parameters():
        if layers_seen < freeze_first_n_layers:
            p.requires_grad_(False)
        layers_seen += 1
    return runner

# Uso:
if args_cli.transfer_from:
    runner = transfer_partial(runner, args_cli.transfer_from, freeze_first_n_layers=4)
```

Y desde CLI:

```powershell
... train.py --task=R1-Locomotion-Direct-v0 --transfer_from="D:\...\model_3500.pt" --max_iterations=10000
```

---

## 3. Curriculum por etapas (para push recovery)

`revisionEntrenamiento.md` ya describe la estrategia: **entrenar primero la postura estática, luego activar pushes, luego permitir stepping**. La forma robusta de hacerlo en Isaac Lab es con un *callback* de curriculum:

```python
# en _pre_physics_step o un nuevo hook
def _curriculum(self):
    it = self.common_step_counter // 24  # iter aprox. (depende de num_steps_per_env)
    if it < 2000:
        self.cfg.push_force_max = 0.0          # pushes OFF
        self.cfg.enable_com_reward = 0.0
    elif it < 4000:
        self.cfg.push_force_max = 0.0
        self.cfg.enable_com_reward = 1.0
    elif it < 10000:
        self.cfg.push_force_max = 8.0          # 5–8 N
        self.cfg.push_force_min = 5.0
    else:
        self.cfg.push_force_max = 25.0         # 15–25 N (stepping)
        self.cfg.push_force_min = 15.0
```

Llamar `self._curriculum()` en `_pre_physics_step`. Detalle: como `cfg` es un dataclass, los cambios en runtime aplican porque `_apply_random_pushes` los lee cada step.

`save_interval = 1000` para etapas largas (recovery). El comentario del repo:

> *"el push-recovery necesita un entrenamiento más pesado: vamos a utilizar entonces 15.000 iteraciones y el save interval cambia a 1000"*

Ajustar:

```python
# rsl_rl_ppo_cfg.py
max_iterations = 15000
save_interval  = 1000
```

---

## 4. Hiperparámetros que sí mover en fine-tune

| Hiperparámetro | Valor base | Valor fine-tune | Por qué |
|---|---:|---:|---|
| `learning_rate` | 1e-3 | **2e-4 a 5e-4** | Bajar 2–5× evita que el resume "olvide". |
| `desired_kl` | 0.01 | **0.005** | KL más estricto preserva la política base. |
| `entropy_coef` | 0.005 | **0.001** | Menos exploración: queremos refinar, no descubrir. |
| `clip_param` | 0.2 | **0.1** | Updates más conservadores. |
| `init_noise_std` | 1.0 | **0.4–0.7** | Importante: si no bajas el `std` la política diverge en los primeros 50 steps tras el resume. |
| `num_steps_per_env` | 24 | **48** | Rollouts más largos para tareas con horizon mayor (push recovery, locomotion). |

**Importante**: estos cambios solo afectan al optimizer del *resume*; los pesos cargados se preservan.

---

## 5. Domain Randomization (esencial para sim2real)

Antes de cerrar el fine-tune, aplica DR para que la política sea robusta. En `R1StandingEnvCfg`:

```python
# Masa del torso ± 15%
event_cfg = isaaclab.envs.mdp.events.RandomizationCfg(
    add_body_mass={
        "asset_cfg": SceneEntityCfg("robot", body_names="torso"),
        "mass_distribution_params": (-0.15, 0.15),
        "operation": "scale",
        "interval": 4.0,
    },
)

# Fricción del suelo U[0.4, 1.2]
# Fuerza de empujón: ya cubierto en _apply_random_pushes
# Latencia de obs ~ 5-15 ms
# Ruido en joint encoders ~ N(0, 0.01)
```

DR de **observaciones**:

```python
def _get_observations(self):
    obs = ...  # como en doc 02
    if self.cfg.add_obs_noise:
        obs = obs + 0.01 * torch.randn_like(obs)
    return {"policy": obs}
```

> Consejo: activa DR **solo después** de tener una política estable (~iter 5000). Si la metes desde iter 0 el PPO no aprende.

---

## 6. Métricas de TensorBoard que sí importan

```
Reward / Total                ← debe subir y estabilizar
Reward / rew_orientation       ← debe acercarse a +20
Reward / rew_termination       ← debe ir a 0 (no se cae)
Loss / value                   ← debe bajar y estabilizar
Loss / policy                  ← oscila pero centrada en 0
Loss / surrogate               ← clip ratio aceptable
Loss / mean_kl                 ← cerca de desired_kl (0.01)
Episode_Reward / mean_episode_length ← debe llegar al límite (max_episode_length)
```

Si `mean_kl` se sale de [0.005, 0.02] → bajar LR. Si oscila demasiado → bajar `clip_param` a 0.1.

---

## 7. Export a ONNX/JIT al terminar

`scripts/rsl_rl/play.py` ya hace export automático en `<run>/exported/`:

- `policy.pt` — TorchScript (compatible con `torch.jit.load` en C++/embebido).
- `policy.onnx` — ONNX (para deployment en TensorRT, OpenVINO, etc.).

Estos artefactos son los que usaría el firmware real del robot para inference.

---

## 8. Checklist de cierre de fine-tune

1. [ ] Run completo sin "explosiones" en `Total Reward`.
2. [ ] `mean_episode_length == max_episode_length` (no se cae).
3. [ ] `rew_termination` ≈ 0.
4. [ ] DR activado y la política sigue rindiendo.
5. [ ] Test en `play.py --num_envs=4` visual: el robot mantiene postura, recupera de empujones, sigue comandos.
6. [ ] Export ONNX/JIT generado.
7. [ ] Backup de `model_*.pt` y del `agent.yaml` / `env.yaml` del run.

Próximo paso → [05_Path_Coordenadas_Velocidad.md](./05_Path_Coordenadas_Velocidad.md).
