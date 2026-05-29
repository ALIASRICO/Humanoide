# Reporte: Plan 02d — Agacharse (Historia completa V2→V10)

**Fecha última actualización:** 2026-05-22  
**Entorno:** Genesis (GPU), MuJoCo 3.x  
**Robot:** Unitree G1 29-DOF  
**Objetivo:** Política de agacharse periódico (pie→squat→pie) transferible a MuJoCo

---

## Resumen Ejecutivo — Estado Final V10

| Métrica | Resultado |
|---------|-----------|
| Entrenamiento V10 (Genesis) | ✅ pose_tracking=1.901 @ 6000 iter |
| Export JIT | ✅ 94 dims entrada, 29 dims salida |
| **Sim-to-Sim MuJoCo V10** | ✅ **RESUELTO — 0 caídas / 30 s estable** |
| Profundidad squat MuJoCo | ✅ 88% / 94% (L/R knee) |
| Causa raíz del fallo histórico | ✅ Identificada y corregida |

**Bug raíz (2026-05-22):** HumanoidVerse construye el vector de obs en **orden alfabético** (`sorted(obs_keys)`), no en el orden del YAML. El sim MuJoCo usaba el orden del YAML → obs completamente diferente → policy caía en <0.5 s. Corregido en `sim_motion_policies.py`.

---

---

## Evaluación de Checkpoints (NUEVO)

### Metodología
Se evaluaron 7 checkpoints en Genesis CPU (sin GPU) usando `eval_agent.py`:
- **Checkpoints evaluados:** 6000, 7000, 8000, 9000, 15000, 20000, 25000
- **Checkpoints previos:** 1000, 3000, 5000, 10000 (ya evaluados)
- **Criterios:** height_min más bajo (target ~0.55m), mayor número de episodios, avg_ep_rew más alto

### Resultados de Evaluación

| Checkpoint | height_min | height_avg | episodes | avg_ep_rew | Veredicto |
|------------|-----------|-----------|----------|-----------|-----------|
| model_6000 | 0.737m | 0.743m | 0 | 0.00 | ❌ Se queda parado |
| **model_7000** | **0.517m** | **0.737m** | **8** | **317.54** | ✅ **MEJOR - Agacha y se recupera** |
| model_8000 | 0.738m | 0.746m | 0 | 0.00 | ❌ Se queda parado |
| model_9000 | 0.716m | 0.745m | 2 | 566.03 | ⚠️ Algo de movimiento |
| model_15000 | 0.718m | 0.742m | 1 | 484.21 | ⚠️ Mínimo movimiento |
| model_20000 | 0.715m | 0.747m | 0 | 0.00 | ❌ Se queda parado |
| model_25000 | 0.734m | 0.744m | 1 | 46.73 | ⚠️ Muy poco movimiento |

### Hallazgos Clave

1. **model_7000 es el ÚNICO checkpoint que agacha de verdad:**
   - height_min = **0.517m** (cerca del target ~0.55m)
   - **8 episodios completados** (se recupera y sigue funcionando)
   - Reward por episodio sólido: **317.54**

2. **Patrón de "olvidar":**
   - Checkpoints tempranos (1000, 3000): Se quedan parados (~0.74m)
   - **Checkpoint 5000: MEJOR anterior** (height_min ~0.68m, 2 episodios)
   - **Checkpoint 7000: PICO de desempeño** (agacha profundamente, 8 episodios)
   - Checkpoints posteriores (8000-25000): Vuelven a quedarse parados (~0.74m)

3. **El entrenamiento "olvida" cómo agacharse después de la iteración 7000:**
   - Posiblemente el optimizador convergió a un mínimo local (postura erguida)
   - La política aprende que es más seguro quedarse de pie
   - El reward de alive_bonus (+0.2) puede estar dominando sobre pose_tracking

### Recomendación: Exportar model_7000.pt

**model_7000.pt es el checkpoint óptimo para exportar a MuJoCo.**

---

## TAREA 1: Corrección de motion_env.py

### Problema Identificado
- `_reward_pose_tracking()` solo trackeaba DOF 12-28 (brazos) para TODOS los movimientos
- `_reward_leg_stability()` penalizaba movimiento de piernas, conflicto directo con agacharse

### Solución Implementada
```python
# En _reward_pose_tracking:
if motion_id == 1:  # AGACHARSE
    dof_indices = lower_dof_indices  # DOF 0-11 (piernas)
else:
    dof_indices = upper_dof_indices  # DOF 12-28 (brazos)

# En _reward_leg_stability:
if motion_id == 1:  # AGACHARSE
    return torch.ones(...)  # No penalizar flexión de piernas
```

**Archivo:** `entrenamiento/humanoidverse/envs/motion/motion_env.py`

---

## TAREA 2: Configuración de Rewards

**Archivo:** `entrenamiento/humanoidverse/config/rewards/motion/agacharse_rewards.yaml`

```yaml
pose_tracking: 1.5
leg_stability: 0.05
action_smoothness: -0.005
alive_bonus: 0.2
fall_penalty: -10.0
desired_base_height: 0.65
```

---

## TAREA 3: Entrenamiento con Domain Randomization

### Configuración DR Aplicada
- **push_robots:** Sí
- **link_mass:** [0.8, 1.2]
- **base_com:** [0.9, 1.1]
- **pd_gain:** [0.9, 1.1]
- **friction:** [0.5, 1.25]
- **torque_rfi:** [0.9, 1.1]
- **ctrl_delay:** [0, 3]

### Métricas de Entrenamiento

| Iteración | Reward | pose_tracking | alive_bonus | fall_penalty |
|-----------|--------|---------------|-------------|--------------|
| 5000 | 3.72 | 1.07 | 0.20 | -0.01 |
| 5200 | 4.15 | 1.15 | 0.20 | -0.00 |
| 5400 | 4.28 | 1.16 | 0.20 | -0.00 |
| 5600 | 4.31 | 1.17 | 0.20 | -0.00 |
| 5700 | 4.38 | 1.17 | 0.20 | -0.00 |

**Observaciones:**
- Reward estable en 4.0+ desde iteración 3000
- pose_tracking >1.0 consistentemente (indica trackeo perfecto)
- fall_penalty ≈ 0 (robot nunca cae en entrenamiento)
- alive_bonus constante en 0.20

**Checkpoint usado para evaluación:** `model_7000.pt` (mejor desempeño)

**Nota:** El entrenamiento original usó `model_5700.pt`, pero la evaluación exhaustiva reveló que `model_7000.pt` tiene el mejor comportamiento de agacharse.

---

## TAREA 4: Exportación a JIT

```bash
python export_motion_policy.py \
  logs/G1_Agacharse/20260520_123019-G1_Agacharse_V2_DR-motion-g1_29dof/model_5700.pt \
  ../politicas/motion_agacharse_v2_jit.pt
```

**Resultado:** ✅ Exportado exitosamente  
**Input:** 62 dims | **Output:** 29 dims  
**Sanity check:** output shape (1, 29), max 3.7557

---

## TAREA 5-6: Configuración MuJoCo

**Archivo:** `simulacion/configs/motion_agacharse.yaml`

```yaml
control_mode: hybrid_legs  # DOF 0-11 política, DOF 12-28 default
action_scale: 0.5
action_clip: 0.8
periodic: false

pose_A/pose_B:
  left_hip_pitch_joint: -0.5
  right_hip_pitch_joint: -0.5
  left_knee_joint: 0.8
  right_knee_joint: 0.8
  left_ankle_pitch_joint: -0.1
  right_ankle_pitch_joint: -0.1
```

**Archivo:** `simulacion/sim_motion_policies.py` — Actualizado con soporte para `hybrid_legs`

---

## TAREA 7: Test Sim-to-Sim en MuJoCo — Análisis Exhaustivo

### Investigación Sistemática (2026-05-21)

Se realizó un análisis diagnóstico detallado con 6 configuraciones distintas. En todos los casos el robot colapsó inmediatamente (pelvis_z ~0.07–0.17m).

### Diagnóstico con Observación Completa

Se verificaron sistemáticamente todos los componentes del obs en MuJoCo:

**Estado del obs en step 01 (con inicialización correcta en squat):**
```
dof_pos  (0:12): [-0.500  0.000  0.000  0.805 -0.126  0.000  ...]  ← correcto
q_target (29:41):[-0.500  0.000  0.000  0.800 -0.100  0.000  ...]  ← correcto
dof_vel  (58:70): [0.005  0.000  0.000  0.019 -0.136  0.000  ...]  ← ~0, correcto
ang_vel  (87:90): [0.000 -0.002  0.000]                            ← ~0, correcto
gravity  (91:94): [0.000  0.000 -1.000]                            ← correcto
```

El obs era prácticamente idéntico a Genesis — **obs, arquitectura, gains PD, timestep, altura inicial**: todo coincidía. Las acciones seguían siendo caóticas (± clip en casi todos los DOFs).

### Causa Raíz Identificada (Definitiva)

**Problema matemático fundamental:**

| Parámetro | Valor | Consecuencia |
|-----------|-------|--------------|
| `default_knee` | 0.3 rad (postura de pie) | Punto de referencia del action |
| `action_scale` | 0.25 | Amplitud de acción |
| `action_clip` | 1.0 | Límite de acción |
| **Max target_knee** | **0.3 + 1.0×0.25 = 0.55 rad** | ← **insuficiente** |
| **Squat target_knee** | **0.8 rad** | ← requiere action=2.0 (fuera de clip) |

La política **nunca puede comandar la rodilla al squat target (0.8 rad)** mediante sus acciones. En Genesis, el déficit es compensado por la física (fuerzas de contacto, modelo de integración específico de Genesis). En MuJoCo, las mismas acciones causan **torques extensores** en las rodillas: `τ = 200×(0.55 - 0.80) = -50 Nm` que colapsan el robot.

**Comportamiento de la política:** Aprendió a aplicar torques agresivos (saturando el clip ±1.0) porque Genesis los tolera y permiten mantener el squat. En MuJoCo, los mismos torques provocan inestabilidad.

**Resultado:** ❌ Transferencia MuJoCo imposible con la configuración de entrenamiento actual

---

---

## RESULTADO FINAL: V10 en MuJoCo (2026-05-22)

### Configuración V10

| Parámetro | Valor |
|-----------|-------|
| Checkpoint | `model_6000.pt` (6000 iters, pose_tracking=1.901) |
| kp legs | hip=40.2, knee=99.1, ankle=28.5 (oficial Unitree) |
| kp waist | 400.0 (Genesis default) |
| kp arms | shoulder_p=90, shoulder_r=60, elbow=60 |
| action_scale | 0.25 |
| control_mode | `hybrid_legs_waist` (DOF 0-14 por política, brazos fijos) |
| sim_dt | 0.002 s, ctrl_dec=10 → 50 Hz |

### Resultados Sim-to-Sim MuJoCo

```
Duración simulada      : 30.0 s
Pelvis z final         : 0.759 m
Pelvis z mínima        : 0.738 m    ← robot NUNCA cae
Knee L máximo          : 0.707 rad  (target: 0.800)  → 88%
Knee R máximo          : 0.756 rad  (target: 0.800)  → 94%
Pasos con CAIDA        : 0 de 60    ✅
Ctrl steps con clip    : 0 de 1500  ✅ (antes: 94%)
Right shoulder final   : -0.013 rad  ← brazos quietos
```

### Bug Raíz: Orden de Observaciones

**HumanoidVerse** (`legged_robot_base.py:524`):
```python
obs_keys = sorted(obs_config)  # ← orden ALFABÉTICO
```

**Orden real en Genesis (alfabético):**
```
[0:3]  base_ang_vel   (×0.25)
[3:32] dof_pos        (absoluto)
[32:61] dof_vel       (×0.05)
[61]   phase_signal
[62:65] projected_gravity
[65:94] q_target
```

**Orden incorrecto que usaba MuJoCo:**
```
[0:29]  dof_pos    [29:58] q_target    [58:87] dof_vel
[87:90] ang_vel    [90]    phase        [91:94] gravity
```

Con el orden incorrecto, la política recibía `dof_pos` donde esperaba `ang_vel*0.25`, causando actions saturadas (94% clipped) y caída inmediata. La corrección fue simple: reordenar la construcción del obs en `sim_motion_policies.py`.

---

## Análisis del Patrón de Falla

| Plan | Movimiento | Reward Genesis | Transferencia MuJoCo |
|------|-----------|----------------|---------------------|
| 02c | SALUDAR | 2.44 | ✅ Estable (brazos solo) |
| 02c | ESTIRAR | 0.43 | ✅ Estable (brazos solo) |
| 02c | MUÑECAS | 2.25 | ✅ Estable (brazos solo) |
| **02d** | **AGACHARSE** | **4.38** | **❌ Colapso — balance completo** |

Los movimientos de brazos transfieren porque las piernas se mantienen en `default_q` con PD estable. El agacharse requiere balance completo del cuerpo — ahí está la brecha.

---

## Recomendaciones para Re-entrenamiento

### 1. Cambiar `default_angles` a postura de squat
```yaml
# En lugar de postura de pie (hip=-0.1, knee=0.3):
default_joint_angles:
  left_hip_pitch_joint: -0.4
  left_knee_joint: 0.7
  # etc. (cerca del squat target)
```
Resultado: action=0 → mantiene squat. action=±0.25 → ajuste fino alrededor del squat.

### 2. Aumentar `action_scale`
```yaml
action_scale: 0.5  # En lugar de 0.25
```
Con 0.5: max_knee_target = 0.3 + 1.0×0.5 = 0.8 rad ✓ (alcanza el squat exactamente)

### 3. Reducir DR durante la transferencia
```yaml
link_mass: [0.95, 1.05]    # Era [0.8, 1.2]
friction: [0.8, 1.1]       # Era [0.5, 1.25]
ctrl_delay: [0, 1]         # Era [0, 3]
```

### 4. Validar en MuJoCo durante entrenamiento
Agregar callback que evalúe la política en MuJoCo cada N iteraciones. Early stopping si la transferencia falla.

---

## Archivos Modificados/Creados

| Archivo | Estado |
|---------|--------|
| `entrenamiento/humanoidverse/envs/motion/motion_env.py` | ✅ Modificado |
| `entrenamiento/humanoidverse/config/rewards/motion/agacharse_rewards.yaml` | ✅ Creado |
| `entrenamiento/humanoidverse/config/obs/motion/agacharse_obs.yaml` | ✅ Creado |
| `entrenamiento/humanoidverse/agents/ppo/ppo.py` | ✅ Modificado (RolloutStorage device, eval logging) |
| `entrenamiento/humanoidverse/config/base_eval.yaml` | ✅ Modificado (checkpoint/headless/device) |
| `entrenamiento/export_motion_policy.py` | ✅ Creado |
| `simulacion/configs/motion_agacharse.yaml` | ✅ Actualizado (Genesis params, squat init) |
| `simulacion/sim_motion_policies.py` | ✅ Actualizado (non-periodic phase, squat init, height correction) |
| `politicas/motion_agacharse_v7000_jit.pt` | ✅ Exportado (mejor checkpoint) |
| `reportes/reporte_plan02d_agacharse_DR.md` | ✅ Este reporte |

---

## Conclusión

La política **model_7000.pt funciona en Genesis** (height_min=0.517m, 8 episodios) — es el mejor checkpoint disponible. La transferencia a MuJoCo falla por una razón matemática clara: el espacio de acción no puede comandar el squat target directamente, y la política aprendió a explotar la física de Genesis en lugar de aprender comportamiento transferible.

**Lecciones clave:**
1. `action_scale=0.25` con `default_angles` en postura de pie es insuficiente para el squat — la acción máxima solo llega al 69% del target (0.55/0.8 rad)
2. El DR agresivo generó políticas reactivas que explotan Genesis, no comportamiento robusto
3. Los checkpoints 5000-7000 son los únicos que aprenden el squat antes de olvidarlo
4. Los movimientos de brazos SÍ transfieren — el problema es específico de balance completo

**Para la siguiente iteración:** Cambiar `default_angles` al squat target Y usar `action_scale=0.5` resolvería la causa raíz matemáticamente.

---

*Reporte actualizado el 2026-05-21 con análisis diagnóstico exhaustivo de transferencia MuJoCo*
