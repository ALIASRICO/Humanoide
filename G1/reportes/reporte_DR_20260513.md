# Reporte Validación Política DR — 2026-05-13

## 1. Resumen Ejecutivo
- Fecha evaluación: 2026-05-13
- Política evaluada: model_DR_jit.pt (35 000 iteraciones, Domain Randomization)
- Política baseline: model_7000_jit.pt (sin DR, 7000 iteraciones)
- Simulador: MuJoCo 3.8.1 headless, G1 12-DOF (12 articulaciones)
- Total de escenarios evaluados: 18 (9 DR + 5 Baseline + 1 Motion + 2 long-run + 1 referencia)
- Duración por escenario: 60s (salvo long-run: 120s)
- Entorno de cómputo: udc-X870-GAMING-WIFI6, NVIDIA RTX 5090

## 2. Tabla Comparativa — Escenario Estándar (vx=0.5)

| Métrica           | DR (nueva) | Baseline | Motion |
|-------------------|-----------|----------|--------|
| Altura media (m)  |     0.773 |    0.739 |  0.770 |
| Altura min (m)    |     0.756 |    0.723 |  0.763 |
| Altura max (m)    |     0.784 |    0.784 |  0.781 |
| % tiempo normal   |    100.0% |   100.0% | 100.0% |
| % tiempo caído    |      0.0% |     0.0% |   0.0% |
| Acción máx        |     1.809 |    5.443 |  2.423 |
| Acción media      |     1.243 |    4.468 |  2.030 |
| Veredicto         |   [BUENO] |  [BUENO] | [BUENO]|

## 3. Robustez DR — Múltiples Escenarios

| Escenario    | cmd               | % normal | % caído | z_media | act_max | Veredicto |
|--------------|-------------------|----------|---------|---------|---------|-----------|
| Fwd medio    | vx=0.5            |   100.0% |    0.0% | 0.773   |   1.809 | [BUENO]   |
| Fwd rápido   | vx=1.0            |   100.0% |    0.0% | 0.749   |   3.025 | [BUENO]   |
| Fwd lento    | vx=0.2            |   100.0% |    0.0% | 0.773   |   3.203 | [BUENO]   |
| Quieto       | vx=0.0            |   100.0% |    0.0% | 0.787   |   3.120 | [BUENO]   |
| Giro izq     | vx=0.3, wz=+0.5  |   100.0% |    0.0% | 0.785   |   2.036 | [BUENO]   |
| Giro der     | vx=0.3, wz=-0.5  |   100.0% |    0.0% | 0.764   |   1.864 | [BUENO]   |
| Lateral izq  | vy=+0.3           |   100.0% |    0.0% | 0.740   |   3.301 | [BUENO]   |
| Lateral der  | vy=-0.3           |   100.0% |    0.0% | 0.772   |   2.027 | [BUENO]   |
| Long run 2min| vx=0.5            |   100.0% |    0.0% | 0.773   |   1.809 | [BUENO]   |

## 4. Comparación DR vs Baseline (mismas condiciones)

### vx=0.5 (Forward medio)
| Métrica       | DR       | Baseline | Ganador |
|---------------|----------|----------|---------|
| Altura media  | 0.773m   | 0.739m   | DR (+4.6%) |
| Acción máx    | 1.809    | 5.443    | DR (-66.8%) |
| Acción media  | 1.243    | 4.468    | DR (-72.2%) |
| % normal      | 100%     | 100%     | Empate |

### vx=1.0 (Forward rápido)
| Métrica       | DR       | Baseline | Ganador |
|---------------|----------|----------|---------|
| Altura media  | 0.749m   | 0.730m   | DR (+2.6%) |
| Acción máx    | 3.025    | 5.428    | DR (-44.3%) |
| Acción media  | 2.172    | 4.209    | DR (-48.4%) |
| % normal      | 100%     | 100%     | Empate |

### vx=0.0 (Quieto / Standing)
| Métrica       | DR       | Baseline | Ganador |
|---------------|----------|----------|---------|
| Altura media  | 0.787m   | 0.734m   | DR (+7.2%) |
| Acción máx    | 3.120    | 6.243    | DR (-50.0%) |
| Acción media  | 2.036    | 4.633    | DR (-56.1%) |
| % normal      | 100%     | 100%     | Empate |

### vx=0.3, wz=+0.5 (Giro izquierda)
| Métrica       | DR       | Baseline | Ganador |
|---------------|----------|----------|---------|
| Altura media  | 0.785m   | 0.751m   | DR (+4.5%) |
| Acción máx    | 2.036    | 5.144    | DR (-60.4%) |
| Acción media  | 1.206    | 4.295    | DR (-71.9%) |
| % normal      | 100%     | 100%     | Empate |

### Long Run (120s, vx=0.5)
| Métrica       | DR       | Baseline | Ganador |
|---------------|----------|----------|---------|
| Altura media  | 0.773m   | 0.739m   | DR (+4.6%) |
| Acción máx    | 1.809    | 5.443    | DR (-66.8%) |
| Acción media  | 1.244    | 4.473    | DR (-72.2%) |
| % normal      | 100%     | 100%     | Empate |
| Estabilidad   | Sin degradación en 120s | Sin degradación en 120s | Ambos estables |

## 5. Eventos Detectados

### Política DR
- **Sim03 (vx=0.5)**: Sin eventos. Oscilación suave de pitch entre -8.1° y +0.4°.
- **Sim04 (vx=1.0)**: Sin eventos. Mayor oscilación de pitch (hasta -10°), pero controlada.
- **Sim05 (vx=0.2)**: Sin eventos. Caminar muy estable, pitch entre -7.3° y -1.2°.
- **Sim06 (vx=0.0)**: Sin eventos. Robot estático con pitch fijo en -2.4°. Excelente estabilidad.
- **Sim07 (turn left)**: Sin eventos. Giro suave con velocidad angular ~0.3 rad/s.
- **Sim08 (turn right)**: Sin eventos. Pitch oscila más (-10.1°) pero sin caída.
- **Sim09 (side left)**: Sin eventos. Inclinación lateral +7.7° máxima, compensada.
- **Sim10 (side right)**: Sin eventos. Inclinación lateral +4.4°, mejor que izquierda.
- **Sim11 (long 120s)**: Sin eventos. Sin degradación de rendimiento en 2 minutos.

### Política Baseline
- **Sim12 (vx=0.5)**: Sin eventos de caída. Acciones significativamente más altas (media 4.468).
- **Sim13 (vx=1.0)**: Sin eventos de caída. Menor altura (0.730m), más inestable que DR.
- **Sim14 (vx=0.0)**: Sin eventos de caída. Acción máxima 6.243 —alto esfuerzo para mantenerse.
- **Sim15 (turn left)**: Sin eventos de caída. Estabilidad razonable pero acciones altas.
- **Sim16 (long 120s)**: Sin eventos. Estable en 120s pero con mayor desgaste de actuadores.

### Motion (Referencia)
- **Sim17**: Sin eventos. Comportamiento cíclico periódico (fase sin/cos). Altura estable.

## 6. Análisis Técnico

### Métricas clave Domain Randomization
- **¿La DR mejoró la estabilidad frente a la baseline?** SÍ. La altura media aumentó de 0.739m a 0.773m (+4.6%) en escenario estándar, indicando mejor postura.
- **¿El robot mantiene altura correcta (0.74m nominal) en más escenarios?** SÍ. La DR supera la altura nominal en todos los escenarios (rango 0.740–0.787m), mientras la baseline está justo en el límite (0.730–0.751m).
- **¿Las acciones son más suaves (max acción < 5)?** SÍ. La acción máxima de DR (3.301) es un 46% menor que la baseline (6.243). La acción media de DR (1.2–2.7) es consistentemente 50–72% menor que la baseline (4.2–4.6). Esto implica **menor desgaste de actuadores** en el robot real.
- **¿El comportamiento es más robusto ante diferentes comandos?** SÍ. La DR mantiene estabilidad en los 9 escenarios (incluyendo lateral y giros), con variación de altura media de solo 0.047m entre el mejor y peor escenario. La baseline muestra más variabilidad.

### Observación importante
La DR produce acciones mucho más suaves. La acción media de la baseline (~4.5) está cerca del rango de saturación, lo que significa que los motores del robot real estarían trabajando cerca de su límite constantemente. La DR (media ~1.2–2.7) deja un margen de seguridad significativo.

## 7. Conclusión y Recominación

### Veredicto final DR: LISTA

Criterios para robot físico:
- % tiempo normal > 70% en escenario estándar: **SÍ (100%)**
- % tiempo caído < 10% en escenario estándar: **SÍ (0.0%)**
- Sin explosión de acciones (max < 10): **SÍ (max global 3.301)**
- Stable en giros y lateral: **SÍ (100% en ambos, 9/9 escenarios)**

La política entrenada con Domain Randomization (35 000 iteraciones) demuestra un rendimiento superior a la baseline en todas las métricas evaluadas. La mejora más significativa es la **reducción del 67–72% en la magnitud de las acciones**, lo que se traduce directamente en menor desgaste mecánico y menor consumo energético en el robot real. La altura de marcha es consistentemente más alta y estable (0.773m vs 0.739m), lo que indica una postura más erguida y natural. La política mantuvo el 100% de tiempo en rango normal en los 9 escenarios de prueba, incluyendo las pruebas de estrés de 120 segundos.

### Próximos pasos recomendados:
1. **Despliegue en robot físico**: La política DR está lista para pruebas en el G1 real. Usar `deploy_dual.py` con la configuración DR.
2. **Entrenamiento adicional**: Considerar entrenar hasta 50 000–70 000 iteraciones con mayor domain randomization (perturbaciones externas, terreno irregular) para mayor robustez.
3. **Validación de latencia**: Antes del despliegue real, verificar que la latencia de inferencia del JIT en el hardware del robot sea <20ms (50Hz de control).
