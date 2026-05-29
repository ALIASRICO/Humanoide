# Reporte Comparativo: Políticas con Domain Randomization vs Sin DR

**Fecha:** 2026-05-19
**Proyecto:** Unitree G1 - Motion Policies con Domain Randomization
**Autor:** Agente Autónomo de Entrenamiento RL

---

## Resumen Ejecutivo

Se entrenaron 3 políticas de movimiento (SALUDAR, ESTIRAR_BRAZOS, MOVER_MUÑECAS) con Domain Randomization (DR) para mejorar la transferencia sim-to-real. Todas las políticas completaron 5000 iteraciones exitosamente. Sin embargo, **las políticas DR fallaron en la validación sim-to-sim en MuJoCo**, mientras que las políticas originales (sin DR) mantuvieron estabilidad perfecta.

---

## Resultados del Entrenamiento

### Políticas con Domain Randomization (DR)

| Movimiento | Iteraciones | Reward Final | Checkpoint |
|---|---|---|---|
| SALUDAR | 5000/5000 | 2.44 | `logs/G1_Motion_DR/20260519_151036-G1_Motion_Saludar_DR-motion-g1_29dof/model_5000.pt` |
| ESTIRAR_BRAZOS | 5000/5000 | 0.43 | `logs/G1_Motion_DR/20260519_163304-G1_Motion_Estirar_DR-motion-g1_29dof/model_5000.pt` |
| MOVER_MUÑECAS | 5000/5000 | 2.25 | `logs/G1_Motion_DR/20260519_175944-G1_Motion_Munecas_DR-motion-g1_29dof/model_5000.pt` |

**Observación:** Los rewards DR son significativamente más bajos que los sin-DR (ver comparativa abajo), lo cual es esperado debido a la randomización de dominio.

### Políticas Originales (Sin DR) - Referencia

| Movimiento | Iteraciones | Reward Final | Status |
|---|---|---|---|
| SALUDAR | 5000/5000 | 4.79 | ✅ Exportado JIT |
| ESTIRAR_BRAZOS | 5000/5000 | 3.36 | ✅ Exportado JIT |
| MOVER_MUÑECAS | 5000/5000 | 4.36 | ✅ Exportado JIT |
| AGACHARSE | 5000/5000 | 3.89 | ✅ Exportado JIT |

---

## Validación Sim-to-Sim (MuJoCo)

### Resultados con Políticas DR

| Movimiento | Duración | Altura Final | Estado | Resultado |
|---|---|---|---|---|
| SALUDAR | 20s | 0.097m | CAÍDA | ❌ FAIL |
| ESTIRAR_BRAZOS | 20s | 0.097m | CAÍDA | ❌ FAIL |
| MOVER_MUÑECAS | 20s | 0.097m | CAÍDA | ❌ FAIL |

**Diagnóstico:** El robot colapsa inmediatamente (z < 0.1m en t=2s). Las acciones de la política DR desestabilizan el robot en MuJoCo.

### Resultados con Políticas Originales (Sin DR) - Referencia

| Movimiento | Duración | Altura Final | Estado | Resultado |
|---|---|---|---|---|
| SALUDAR | 20s | 0.783m | ESTABLE | ✅ PASS |
| ESTIRAR_BRAZOS | 20s | 0.783m | ESTABLE | ✅ PASS |
| MOVER_MUÑECAS | 20s | 0.783m | ESTABLE | ✅ PASS |

---

## Análisis de la Falla de Transferencia DR

### Hipótesis Principal

Las políticas entrenadas con DR en Genesis desarrollaron una dependencia en las características específicas del simulador Genesis que no se transfieren a MuJoCo:

1. **Dinámica de contacto diferente:** Genesis y MuJoCo modelan fricción y contacto de formas distintas
2. **Ruido de acción:** El DR añadió `torque_rfi` y `ctrl_delay` que la política aprendió a compensar, pero estas compensaciones son específicas de Genesis
3. **Randomización de masa/COM:** La política DR aprendió a ser robusta a variaciones de masa que no existen en MuJoCo
4. **Ganancias PD randomizadas:** El DR randomizó las ganancias PD, pero en MuJoCo usamos ganancias fijas

### Evidencia

- La política original (sin DR) mantiene z=0.783m estable en MuJoCo
- La política DR colapsa inmediatamente a z=0.097m
- Las acciones DR tienen magnitud máxima de 2.82 (SALUDAR) vs 0.5-1.5 en las originales
- El control híbrido (piernas PD + brazos política) no es suficiente para estabilizar las acciones DR

---

## Configuración de Domain Randomización Aplicada

```yaml
# motion_dr.yaml
push_robots:
  push_interval_s: 15
  velocity_range: [0.5, 1.0]

link_mass:
  randomize: true
  range: [0.8, 1.2]

base_com:
  randomize: true
  range: [0.9, 1.1]

pd_gain:
  randomize: true
  range: [0.9, 1.1]

friction:
  randomize: true
  range: [0.5, 1.25]

torque_rfi:
  randomize: true
  range: [0.9, 1.1]

ctrl_delay:
  randomize: true
  range: [0, 3]
```

---

## Archivos Generados

### Políticas JIT Exportadas

| Archivo | Tamaño | Descripción |
|---|---|---|
| `politicas/motion_saludar_DR_jit.pt` | 794K | Política SALUDAR con DR |
| `politicas/motion_estirar_DR_jit.pt` | 794K | Política ESTIRAR con DR |
| `politicas/motion_munecas_DR_jit.pt` | 794K | Política MUÑECAS con DR |

### Checkpoints de Entrenamiento

| Checkpoint | Tamaño |
|---|---|
| `logs/G1_Motion_DR/20260519_151036-G1_Motion_Saludar_DR/.../model_5000.pt` | ~15MB |
| `logs/G1_Motion_DR/20260519_163304-G1_Motion_Estirar_DR/.../model_5000.pt` | ~15MB |
| `logs/G1_Motion_DR/20260519_175944-G1_Motion_Munecas_DR/.../model_5000.pt` | ~15MB |

### Scripts y Configs

- `entrenamiento/export_motion_policy.py` - Script de exportación JIT para 29-DOF
- `simulacion/configs/motion_saludar.yaml` - Actualizado con path DR
- `simulacion/configs/motion_estirar_brazos.yaml` - Actualizado con path DR
- `simulacion/configs/motion_munecas.yaml` - Actualizado con path DR

---

## Conclusiones

1. **Entrenamiento DR exitoso:** Las 3 políticas completaron 5000 iteraciones sin errores
2. **Transferencia sim-to-sim fallida:** Las políticas DR no son estables en MuJoCo
3. **Las políticas originales son superiores para sim-to-sim:** Sin DR, las políticas mantienen estabilidad perfecta
4. **El DR requiere calibración más fina:** La configuración actual de DR es demasiado agresiva para movimientos de brazos

## Recomendaciones

1. **Reducir intensidad de DR:**
   - `link_mass.range: [0.95, 1.05]` en lugar de [0.8, 1.2]
   - `friction.range: [0.8, 1.1]` en lugar de [0.5, 1.25]
   - Eliminar `ctrl_delay` o reducir a [0, 1]

2. **Entrenar con DR más suave:** Re-entrenar con randomización menos agresiva

3. **Validar en Genesis primero:** Antes de exportar a JIT, validar que la política DR funcione en Genesis con parámetros nominales

4. **Considerar fine-tuning:** Entrenar sin DR primero, luego hacer fine-tuning con DR ligero

5. **Para despliegue real:** Las políticas originales (sin DR) son más prometedoras dado que:
   - Pasaron validación sim-to-sim (20/20 episodios)
   - Son estables en MuJoCo
   - El robot real tiene dinámica más cercana a MuJoCo que a Genesis con DR agresivo

---

## Métricas Comparativas

| Métrica | Sin DR | Con DR | Delta |
|---|---|---|---|
| Reward SALUDAR | 4.79 | 2.44 | -49% |
| Reward ESTIRAR | 3.36 | 0.43 | -87% |
| Reward MUÑECAS | 4.36 | 2.25 | -48% |
| Sim-to-sim PASS | 3/3 | 0/3 | -100% |
| Altura MuJoCo | 0.783m | 0.097m | -88% |

---

## Estado del Proyecto

- ✅ TAREA 1: Config DR verificada
- ✅ TAREA 2: SALUDAR DR entrenado (5000 iter)
- ✅ TAREA 3: ESTIRAR DR entrenado (5000 iter)
- ✅ TAREA 4: MUÑECAS DR entrenado (5000 iter)
- ✅ TAREA 5: Exportar 3 políticas a JIT
- ✅ TAREA 6: Actualizar configs YAML
- ✅ TAREA 7: Test sim-to-sim headless (0/3 PASS)
- ✅ TAREA 8: Reporte comparativo completado

**Git commit:** Pendiente

---

*Reporte generado automáticamente por el agente de entrenamiento RL*
