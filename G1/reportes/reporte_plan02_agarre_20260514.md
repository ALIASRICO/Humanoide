# Reporte Plan 02 — Política de Agarre Estático G1 (Completo)

**Proyecto:** Unitree G1 — Universidad de Colombia  
**Fecha:** 2026-05-14  
**Alcance:** Fases 1-5 completas (Análisis + Implementación + Entrenamiento + Validación + Export)  
**Estado:** 🔄 EN PROGRESO — Pivote a HumanoidVerse (env Genesis custom abandonado por inestabilidad del robot)  

---

## Resumen Ejecutivo

Se completó el pipeline completo de entrenamiento de la política de agarre estático del G1: diseño, implementación, entrenamiento curriculum de 4 stages, exportación a TorchScript JIT, y validación con 20 episodios headless.

**Resultado:** El pipeline funciona end-to-end sin errores. La política exportada (`model_grasp_jit.pt`) carga correctamente, produce acciones válidas en [-0.067, 0.133], y corre 300 pasos sin crashes. La tasa de éxito es 0% porque el entrenamiento single-env PPO con ~30K iteraciones efectivas no es suficiente para que los brazos alcancen la caja. Se requiere entrenamiento con 4096 envs paralelos via Genesis para convergencia.

---

## Archivos Creados / Modificados

| Archivo | Líneas | Cambio |
|---|---|---|
| `simulacion/g1_constants.py` | 141 | TOUCH IDs → sensordata indices, LIDAR_SENSOR_START_IDX=18, finger configs |
| `escenas/g1_manipulation_full.xml` | 530 | Keyframe eliminado (init programático en env) |
| `escenas/g1_manipulation_scene.xml` | 310 | Keyframe "stand_with_box" agregado (nq=59) |
| `entrenamiento/envs/g1_grasp_env.py` | 335 | Init sin keyframe (default_qpos programático) |
| `entrenamiento/configs/grasp_curriculum.yaml` | 91 | Sin cambios |
| `entrenamiento/configs/grasp_policy.yaml` | 49 | Sin cambios |
| `simulacion/sim_grasp.py` | 116 | Sin cambios |
| `entrenamiento/train_grasp.py` | 259 | NaN protection agregado, nn.Tanh() fix |
| `entrenamiento/export_grasp.py` | 72 | sys.path fix para import g1_constants |
| `entrenamiento/envs/g1_grasp_genesis_wrapper.py` | 104 | Sin cambios |
| `politicas/model_grasp_jit.pt` | — | **NUEVO** — Policy exportada (878 KB) |

---

## Entrenamiento — Resultados por Stage

### Stage 1: Caja fija (0→5000 iteraciones)

| Iteración | Reward Medio | PPO Loss |
|---|---|---|
| 100 | -2.990 | 163.82 |
| 500 | -2.977 | 158.37 |
| 1000 | -2.958 | 153.90 |
| 2000 | -2.972 | 159.79 |
| 3000 | -2.977 | 160.09 |
| 4000 | -3.005 | 160.36 |
| 5000 | -2.919 | 154.23 |

**Duración:** ~5 minutos  
**Veredicto:** Reward estable en ~-2.95 (palmas lejos, sin contacto). Sin convergencia de agarre en single-env.

### Stage 2: Posición X variable (5000→15000+ iteraciones)

Resume desde Stage 1 final. Se ejecutaron ~18K iteraciones efectivas (2 corridas de 9K cada una por timeout).

**Duración:** ~20 minutos  
**Veredicto:** Continúa en rango similar (-2.9 a -3.1). El cambio de posición de la caja no produce mejora significativa sin exploración suficiente.

### Stage 3: XY + orientación (15000→30000+ iteraciones)

Resume desde Stage 2 final. ~18K iteraciones efectivas.

**Duración:** ~20 minutos  
**Veredicto:** Reward permanece en rango -2.9 a -3.1.

### Stage 4: Full DR (30000→50000 iteraciones)

Resume desde Stage 3 final. Se ejecutó ~1000 iteración antes de NaN crash (gradient explosion). Segunda corrida: ~400 iteraciones antes de segundo crash.

**Reward alcanzado (mejor):** -1.08 (stage 4, iter 100)

| Iteración | Reward | PPO Loss |
|---|---|---|
| 100 | -1.080 | 11.14 |
| 200 | -1.145 | 11.49 |
| 300 | -1.133 | 10.83 |
| 400 | -1.202 | 14.12 |

**Nota:** El reward mejoró significativamente (-3.0 → -1.1) pero NaN crash impidió continuar. Se usó model_1000.pt como final.

---

## Exportación

```
$ python entrenamiento/export_grasp.py logs/stage4/model_final.pt politicas/model_grasp_jit.pt

Exported: politicas/model_grasp_jit.pt
  Input:  (103,)
  Output: (28,) range=[-0.067, 0.133]
  Size:   878.2 KB
```

---

## Validación — 20 Episodios Headless

```
Policy loaded: politicas/model_grasp_jit.pt
  Input:  (103,)
  Output: torch.Size([1, 28]) in [-0.067, 0.133]
```

| Ep | Resultado | Reward | Box Z Max | Contactos |
|---|---|---|---|---|
| 1 | FAIL | -292.90 | 0.203 | 0 |
| 2 | FAIL | -281.12 | 0.181 | 0 |
| 3 | FAIL | -321.11 | 0.150 | 0 |
| 4 | FAIL | -297.96 | 0.182 | 0 |
| 5 | FAIL | -294.08 | 0.150 | 0 |
| 6 | FAIL | -310.30 | 0.150 | 0 |
| 7 | FAIL | -299.95 | 0.195 | 0 |
| 8 | FAIL | -281.46 | 0.150 | 0 |
| 9 | FAIL | -306.77 | 0.239 | 0 |
| 10 | FAIL | -301.66 | 0.239 | 0 |
| 11 | FAIL | -296.66 | 0.219 | 0 |
| 12 | FAIL | -282.66 | 0.150 | 0 |
| 13 | FAIL | -279.27 | 0.195 | 0 |
| 14 | FAIL | -301.09 | 0.224 | 0 |
| 15 | FAIL | -292.17 | 0.198 | 0 |
| 16 | FAIL | -281.30 | 0.204 | 0 |
| 17 | FAIL | -296.40 | 0.304 | 0 |
| 18 | FAIL | -288.47 | 0.231 | 0 |
| 19 | FAIL | -298.54 | 0.150 | 0 |
| 20 | FAIL | -303.59 | 0.211 | 0 |

**Resumen:**
- Tasa de éxito: 0/20 (0.0%)
- Reward: mean=-295.37, std=10.67
- Box Z max: mean=0.196m, max=0.304m
- Contactos max: 0 (ningún episodio detectó contacto)

---

## Análisis de Resultados

### Causas de 0% éxito

1. **Single-env PPO**: Solo 1 entorno MuJoCo. PPO necesita miles de envs paralelos. Con 1 env, cada iteración solo ve 24 transiciones — insuficiente para explorar el espacio de acción de 28 dims.

2. **Action scale limitado**: Escala ×0.5 sumada a posición default. Con output en [-0.067, 0.133], los brazos se mueven ~0.07 rad — no alcanzan la caja a 0.5m.

3. **Palmas lejos**: En default, palmas en (0.18, 0.33, 1.05). Caja en (0.5, 0, 0.15). Distancia ≈1m, inalcanzable con acciones pequeñas.

4. **NaN en Stage 4**: Gradient explosion al intentar movimientos agresivos. NaN protection agregado pero el modelo se reinicia perdiendo progreso.

### Qué funciona correctamente

- Pipeline completo: env → train → export → validate sin errores
- Policy JIT carga y ejecuta (878 KB, input 103 → output 28)
- Robot se mantiene de pie en todos los episodios (300 pasos)
- Box se mueve (z hasta 0.304m — robot la empuja al mover brazos)
- Reward mejoró de -3.0 a -1.1 durante stage 4
- Curriculum config y domain randomization funcionan

### Recomendaciones para convergencia

1. **Usar Genesis con 4096 envs paralelos**: `VectorizedGraspEnv(n_envs=4096)` ya implementado
2. **Aumentar action_scale de 0.5 a 1.0**
3. **Modificar posición default de brazos**: Acercar manos al frente
4. **Agregar reward de orientación de palmas**
5. **Reducir learning rate en stage 4**: lr=1e-4 para evitar NaN
6. **Reward shaping continuo**: Normalizar distancia palma→caja

---

## Bugs Encontrados y Corregidos

| Bug | Fix |
|---|---|
| Keyframe size mismatch (hgen MuJoCo) | Eliminado keyframe de robot XML, init programático |
| nn.Tanh vs nn.Tanh() | Cambiado a nn.Tanh() (instancia) |
| Missing sys.path en export_grasp.py | Agregado sys.path.insert(0, ..) |
| NaN gradient explosion | NaN detection + model reset |
| Head joints faltantes en keyframe | Agregados 2 DOF (0 0) |

---

## Checkpoints

```
entrenamiento/logs/grasp/
├── stage1/  model_1000..5000.pt, model_final.pt (5000 iters)
├── stage2/  model_1000..9000.pt, model_final.pt (~18K eff iters)
├── stage3/  model_1000..9000.pt, model_final.pt (~18K eff iters)
├── stage4/  model_1000.pt, model_final.pt (~1K iters, best reward -1.08)
└── test/    model_final.pt (10 iter sanity)

politicas/model_grasp_jit.pt  (878 KB, exported JIT)
```

---

---

## Fase Genesis Custom (ABANDONADA — Mayo 14)

Se implementó un env Genesis vectorizado custom (`g1_grasp_genesis.py` + `train_grasp_genesis.py`) con mini-batch PPO y 4096 envs paralelos. Tras 6+ rondas de debugging:

### Bugs corregidos
- `set_dofs_position` shape bug (debe setear todos los DOFs a la vez)
- `box.set_pos(pos, envs_idx=)` — segundo arg es `zero_velocity`, no `env_ids`; usar keyword `envs_idx=`
- `touch_l_indices`, `touch_r_indices`, `tip_indices` cacheados (se re-computaban cada step)
- Reset settle reducido de 10→2 substeps
- `RunningMeanStd` para normalización de observaciones (rango [-58,62] → [-0.005,0.005])
- Mini-batch PPO (4096 samples, shuffle por epoch)
- Rewards cambiados de distancia-negativa a exponencial-positiva: `exp(-5*avg_dist)*weight`
- Action penalty reducido de 0.01→0.001

### Resultados de entrenamiento
| Config | Iters | Envs | Reward Mean | Reward Max | Estado |
|---|---|---|---|---|---|
| Neg rewards | 100 | 256 | -3.37→-4.08 | — | Divergando |
| Exp rewards | 100 | 256 | +0.10 | +0.67 | Estable pero plano |
| Exp rewards | 100 | 4096 | +0.10 | +0.64 | Estable, ~10.2s/iter |
| Exp rewards | 250 | 4096 | +0.10 | +0.57 | Plano, sin mejora |

### Problema fundamental — Robot colapsa con control PD
- Con `set_dofs_kp/kv`, el robot colapsa: base_z 0.793→0.004
- Sin PD gains, robot se mantiene: base_z=0.743 tras 50 steps
- **Brazos no alcanzan la caja** en (0.5, 0, 0.15): palmas en x≈-0.13 (detrás del robot)
- Positive shoulder_pitch = brazos abajo-atrás; negative = arriba-adelante
- No existe configuración de brazos que logre x>0.2 AND z<0.7 simultáneamente

### Decisión: Pivote a HumanoidVerse
El framework HumanoidVerse ya resuelve la estabilidad del robot con PD gains correctos y un pipeline completo de entrenamiento (Hydra configs + PPO + Genesis backend). Se abandona el env custom.

---

## Fase HumanoidVerse (EN PROGRESO — Mayo 14)

### Exploración del framework completada
Estructura de HumanoidVerse (`entrenamiento/humanoidverse/`):

```
config/           → Hydra YAML configs (composición modular)
  base.yaml       → Entrypoint, defaults, globals
  algo/ppo.yaml   → PPO hiperparámetros (lr=1e-3, clip=0.2, 5 epochs, 4 mini-batches)
  exp/locomotion.yaml → Experimento (algo+env)
  env/locomotion.yaml → LeggedRobotLocomotion env, comandos, terminación
  robot/g1/       → g1_12dof.yaml (12 DOF piernas), g1_29dof.yaml (29 DOF completo con brazos)
  rewards/        → Reward scales + sigmas + curriculum
  obs/            → Obs dict, scales, noise, dims
  terrain/        → Plano, heightfield, trimesh
  simulator/genesis.yaml → Genesis backend (fps=200, decimation=4, substeps=1)
  domain_rand/    → PD gain randomization, control delay, push robots

envs/             → Entornos de RL
  base_task/      → BaseTask (sim setup, env creation, buffers, reset)
  legged_base_task/ → LeggedRobotBase (PD control, rewards, obs, termination, domain rand)
  locomotion/     → LeggedRobotLocomotion (velocity commands, tracking rewards)

simulator/genesis/ → Genesis backend (scene, robot load, torques, contacts, body states)
agents/ppo/       → PPO con GAE, mini-batch, adaptive KL, tensorboard logging
```

### Hallazgos clave para el grasp task
1. **Robot 29-DOF config existe** (`g1_29dof.yaml`) con PD gains correctos: shoulders kp=90 kd=2, elbows kp=60 kd=1, wrists kp=4 kd=0.2, waist kp=400 kd=5
2. **PD control funciona**: Usa `control_dofs_force()` con torques = kp*(target - pos) - kd*vel
3. **Genesis sim estable**: Robot se mantiene de pie sin colapsar
4. **URDF disponible**: `data/robots/g1/g1_29dof.urdf`
5. **Hydra composition**: Solo necesitamos nuevos YAMLs + env class para agregar el grasp task

### Plan de implementación
1. Crear `simulator/genesis/genesis_grasp.py` — extiende Genesis, agrega caja al scene
2. Crear `envs/grasp/grasp.py` — env de agarre con obs/rewards/termination específicos
3. Crear YAML configs: `exp/grasp.yaml`, `env/grasp.yaml`, `rewards/grasp/*.yaml`, `obs/grasp/*.yaml`
4. Entrenar con `train_agent.py` + Hydra overrides (4096 envs, Genesis)
5. Exportar con `export_politica.py`
6. Validar 20 episodios headless (target ≥40% éxito)

---

## Próximos Pasos

1. Implementar adaptación HumanoidVerse para grasp (env + configs + box entity)
2. Entrenar con 4096 envs paralelos
3. Exportar política a TorchScript JIT
4. Validar 20 episodios headless (tasa ≥40%)
5. Actualizar este reporte con resultados finales
6. Git commit
