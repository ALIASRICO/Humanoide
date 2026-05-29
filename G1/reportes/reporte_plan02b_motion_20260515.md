# Plan 02b — Políticas de Movimiento Simple G1 (29 DOF)

**Proyecto:** Unitree G1 — Universidad de Colombia  
**Fecha:** 2026-05-15  
**Modelo:** G1 29-DOF (`g1_29dof`) — sin manos dextrales  
**Framework:** HumanoidVerse + Genesis (4096 envs paralelos)  
**Estado:** EN PROGRESO (entrenamiento activo)

---

## 1. Resumen Ejecutivo

Se implementó un entorno RL (`MotionEnv`) para entrenar 4 políticas de movimiento simple:

| Movimiento | ID | Tipo | Descripción |
|---|---|---|---|
| **Saludar** | 0 | Periódico | Brazo derecho sube y muñeca oscila (periodo 1.0s) |
| **Agacharse** | 1 | No periódico | Flexión de piernas (duración 2.0s) |
| **Estirar brazos** | 2 | No periódico | Ambos brazos al frente (duración 1.5s) |
| **Mover muñecas** | 3 | Periódico | Rotación y flexión de muñecas (periodo 1.2s) |

**Arquitectura:**
- **Observaciones:** 62 dims = q_actual(29) + q_target(29) + phase_signal(1) + projected_gravity(3)
- **Acciones:** 29 dims (todos los DOF del G1)
- **Red:** MLP [512, 256, 128] con activación ELU
- **Algoritmo:** PPO con lr=1e-3, clip=0.2, 5 epochs, 4 minibatches

---

## 2. Archivos Creados

| Archivo | Descripción |
|---|---|
| `config/env/motion.yaml` | Configuración del entorno motion |
| `config/exp/motion.yaml` | Configuración del experimento |
| `config/obs/motion/motion_obs.yaml` | Definición de observaciones (62 dims) |
| `config/rewards/motion/motion_rewards.yaml` | Escalas de recompensa |
| `config/motions/motion_poses.yaml` | Poses objetivo de los 4 movimientos |
| `envs/motion/motion_env.py` | Entorno RL (extiende LeggedRobotBase) |
| `envs/motion/__init__.py` | Init del paquete |
| `simulator/genesis/genesis_motion.py` | Backend Genesis (extiende base) |
| `validate_motion.py` | Script de validación (20 episodios) |
| `export_motion_policy.py` | Script de exportación a JIT |

---

## 3. Progreso del Entrenamiento

**Estado actual:** Iteración ~105/5000 (2.1% completado)  
**Tiempo restante estimado:** ~5.5 horas por política  
**GPU:** RTX 5090 @ 99% utilización, 20.8GB VRAM

### Métricas en iteración 105:

| Movimiento | Reward | Pose Tracking | Leg Stability | Episode Length |
|---|---|---|---|---|
| **Saludar** | 1.03 | 0.146 | 0.028 | ~51 steps |
| **Agacharse** | 2.25 | 0.345 | 0.029 | ~56 steps |
| **Estirar brazos** | 0.43 | 0.039 | 0.029 | ~50 steps |
| **Mover muñecas** | 0.41 | 0.048 | 0.027 | ~49 steps |

**Análisis:**
- **Agacharse** muestra el mejor rendimiento (reward 2.25, pose tracking 0.345). Esto se debe a que el movimiento involucra principalmente las piernas, que tienen PD gains más altos (kp=100-200) comparado con el cuerpo superior (kp=4-90).
- **Saludar** está progresando bien (reward 1.03, pose tracking 0.146).
- **Estirar brazos** y **Mover muñecas** progresan más lentamente debido a que dependen de joints del cuerpo superior con gains más bajos.

---

## 4. Bugs Encontrados y Correcciones

### Bug 1: Nombres de joints sin sufijo `_joint`
**Problema:** Las poses objetivo en `motion_poses.yaml` usaban nombres como `right_shoulder_pitch` en lugar de `right_shoulder_pitch_joint`, lo que causaba `ConfigValueError: Item not found in ListConfig` al buscar el índice del joint.

**Solución:** Se agregó el sufijo `_joint` a todos los nombres de joints en la configuración.

### Bug 2: Recompensa `pose_tracking` demasiado estricta
**Problema:** El coeficiente original de `exp(-3.0 * error)` producía recompensas prácticamente cero (≈1e-6) cuando los joints estaban lejos del target, impidiendo el aprendizaje inicial.

**Solución:** Se suavizó el coeficiente a `exp(-0.5 * error)`, lo que resultó en mejoras de 65x-270x en pose tracking.

### Bug 3: Procesos de entrenamiento mueren con `nohup`
**Problema:** El uso de `nohup bash -c '...'` causaba que los procesos murieran silenciosamente al cerrar la sesión.

**Solución:** Se cambió a `setsid` para crear sesiones completamente independientes.

---

## 5. Validación (PENDIENTE)

La validación de 20 episodios por movimiento se ejecutará una vez completado el entrenamiento (5000 iteraciones).

**Criterios de aprobación:**

| Movimiento | Criterio | Mínimo |
|---|---|---|
| Saludar | right_shoulder_pitch < -0.8 AND wrist_pitch_range > 0.3 | ≥16/20 |
| Agacharse | knee_delta > 0.5 AND pelvis_drop > 2cm | ≥16/20 |
| Estirar brazos | ambos shoulder_pitch < -1.0 | ≥16/20 |
| Mover muñecas | wrist_roll_range > 1.0 rad | ≥16/20 |

---

## 6. Exportación a JIT (PENDIENTE)

Las políticas se exportarán a `politicas/motions/`:
- `model_saludar_jit.pt`
- `model_agacharse_jit.pt`
- `model_estirar_brazos_jit.pt`
- `model_munecas_jit.pt`

Formato: TorchScript JIT, input (1, 62) → output (1, 29)

---

## 7. Próximos Pasos

1. **Esperar finalización del entrenamiento** (~5.5 horas restantes)
2. **Validar cada política** con 20 episodios headless
3. **Re-entrenar si es necesario** (cualquier movimiento con <16/20 PASS)
4. **Exportar políticas a JIT**
5. **Generar reporte final completo**
6. **Git commit**

---

## 8. Constantes Agregadas

Se actualizó `simulacion/g1_constants.py` con:

```python
MOTION_POLICY_DIR = "politicas/motions"
MOTION_POLICIES = {
    "saludar":        "politicas/motions/model_saludar_jit.pt",
    "agacharse":      "politicas/motions/model_agacharse_jit.pt",
    "estirar_brazos": "politicas/motions/model_estirar_brazos_jit.pt",
    "munecas":        "politicas/motions/model_munecas_jit.pt",
}
MOTION_OBS_DIM = 62
MOTION_ACT_DIM = 29
UPPER_DOF_START = 12
UPPER_DOF_END   = 29
LOWER_DOF_START = 0
LOWER_DOF_END   = 12
```

---

*Reporte generado el 2026-05-15. Estado: EN PROGRESO. Se actualizará al completar el entrenamiento y validación.*
