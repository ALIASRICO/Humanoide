# Plan de Implementación: Sensores + Manipulación para Unitree G1

**Fecha:** 2026-05-14  
**Objetivo:** Diseñar un pipeline completo para que el G1 detecte una caja → la agarre → la transporte caminando → la deposite en un punto B, usando políticas entrenadas por RL/IL en simulación.

---

## 1. Resumen Ejecutivo

El G1 tiene 29 DOF (12 piernas + 2 cintura + 3 torso + 14 brazos), manos tipo "rubber_hand" (paletas rígidas, sin dedos articulados), y ya contamos con:

- **Política de locomoción DR validada** (`model_DR_jit.pt`, 12 DOF piernas, 48 obs → 12 acciones)
- **Modelo MuJoCo 23 DOF** (`g1_23dof.xml`) con brazos completos + sensores de posición, velocidad, torque, IMU
- **Modelo MuJoCo 29 DOF** (`lydar.xml`) con LIDAR 2D de 32 rayos + sensores IMU + escena con obstáculos
- **Código de manipulación** (`g1_caja.py`) con secuencias predefinidas de 4 pasos (inicial → abrir → agarre → dejar)
- **YOLO** para detección de objetos + LIDAR 2D ROS2 integrado

**Recomendación principal:** Arquitectura jerárquica con 3 políticas especializadas + integración por orchestrador.

---

## 2. Estado Actual del Hardware Simulado

### 2.1 Modelo G1 23-DOF (`escenas/g1_23dof.xml`)

| Componente | DOF | Articulaciones | Rango Torque (Nm) |
|---|---|---|---|
| Piernas (x2) | 12 | hip_pitch/roll/yaw, knee, ankle_pitch/roll | 50-139 |
| Cintura | 3 | yaw, roll, pitch | 50-88 |
| Brazo Izq | 5 | shoulder_pitch/roll/yaw, elbow, wrist_roll | 25 (brazo), 5 (muñeca) |
| Brazo Der | 5 | shoulder_pitch/roll/yaw, elbow, wrist_roll | 25 (brazo), 5 (muñeca) |

**Sensores ya definidos:**
- 29 sensores `jointpos` (posición angular)
- 29 sensores `jointvel` (velocidad angular)
- 29 sensores `jointactuatorfrc` (torque aplicado)
- 2 IMUs: primaria (pelvis) y secundaria (torso)
- Posición y velocidad del frame mundial

### 2.2 Modelo G1 29-DOF con LIDAR (`escenas/lydar.xml`)

Añade sobre el modelo completo:
- **32 sensores rangefinder** (LIDAR 2D, 360° cada 11.25°, alcance 10m, ruido 1cm)
- **Escena con obstáculos:** 2 mesas, caja, cilindro, segmento de pared
- Muñecas completas (pitch + yaw) con mesh `rubber_hand` por lado
- Cintura desglosada en 3 DOF (yaw/roll/pitch)

### 2.3 Manos "Rubber Hand"

Las manos del G1 son **paletas rígidas sin articulación**. Esto limita el agarre a:
- Agarre lateral por fricción (clamp bilateral entre ambas manos)
- No puede hacer pinza fina ni agarre de precisión
- Requiere contacto con ambas paletas simultáneamente

**Implicación para RL:** El espacio de acción es relativamente simple (posición de ambas muñecas), pero la política debe garantizar contacto bilateral con la caja para sostenerla.

---

## 3. Sensores Disponibles en MuJoCo

### 3.1 Sensores que YA tenemos en XML

| Sensor | Cantidad | Lectura | Uso para manipulación |
|---|---|---|---|
| `jointpos` | 29 | Ángulo articular | Observación base para brazos |
| `jointvel` | 29 | Velocidad angular | Observación base |
| `jointactuatorfrc` | 29 | Torque aplicado | Detección de contacto por torque |
| `framequat` | 2 | Orientación IMU | Balance del robot |
| `gyro` | 2 | Velocidad angular IMU | Estabilidad |
| `accelerometer` | 2 | Aceleración lineal | Estabilidad |
| `rangefinder` | 32 | Distancia por rayo | Navegación + detección de caja |
| `framepos` | 1 | Posición mundial | Localización absoluta |

### 3.2 Sensores que PODEMOS añadir

| Sensor | Implementación MuJoCo | Uso |
|---|---|---|
| **Cámara RGB-D** | `<sensor> <camera name="..." .../> </sensor>` o render offscreen | Detección visual de la caja (YOLO) |
| **Fuerza de contacto** | `mj_contactForce(data, contact, force)` en Python | Detectar si la mano toca la caja, magnitud del agarre |
| **Frame position/orientación** de las manos | `<framepos>`/`framequat` en sitios de las rubber_hand | Posición 3D de las manos respecto al mundo |
| **Más rayos LIDAR** | Agregar más sitios `rangefinder` | Cobertura frontal para aproximación |

### 3.3 Matriz de Sensores por Fase de la Tarea

| Fase | Sensores Críticos | Sensores Secundarios |
|---|---|---|
| **Detección** (localizar caja) | LIDAR 32 rayos, Cámara RGB-D | framepos (localización) |
| **Aproximación** (caminar hacia caja) | LIDAR, IMU, jointpos piernas | framevel, jointvel |
| **Agarre** (brazos a caja) | jointpos brazos, contact force, framepos manos | jointvel brazos, torque |
| **Transporte** (caminar con caja) | LIDAR, IMU, jointpos piernas+brazos, contact force | Todos los demás |
| **Depósito** (soltar en punto B) | LIDAR, framepos manos, contact force | jointpos brazos |

---

## 4. Arquitectura Recomendada: Políticas Jerárquicas

### 4.1 Diseño de 3 Capas

```
┌─────────────────────────────────────────────┐
│           ORQUESTADOR (Reglas / FSM)         │
│  - Decide qué política activar               │
│  - Lee: LIDAR, posición, estado de contacto  │
│  - Transiciones: DETECTAR → ACERCARSE →      │
│    AGARRAR → TRANSPORTAR → DEPOSITAR         │
└──────────────┬──────────────────────────────┘
               │
       ┌───────┼───────┐
       ▼       ▼       ▼
┌──────────┐ ┌──────────┐ ┌──────────┐
│ POLÍTICA │ │ POLÍTICA │ │ POLÍTICA │
│ LOCOMOC. │ │ BRAZOS   │ │ NAV+PERC │
│ (12 DOF) │ │ (14 DOF) │ │ (LIDAR + │
│          │ │          │ │  Cámara) │
│ YA EXISTE│ │ NUEVA    │ │ NUEVA    │
│ model_DR │ │ entrenar │ │ entrenar │
│ _jit.pt  │ │          │ │          │
└──────────┘ └──────────┘ └──────────┘
     │             │            │
     ▼             ▼            ▼
  Piernas +     Brazos +     Waypoints +
  cintura       muñecas      Comandos
                (14 DOF)     de velocidad
```

### 4.2 Justificación

1. **Locomoción ya funciona** — La política DR (`model_DR_jit.pt`) controla 12 DOF de piernas con dominio randomization robusto. No reentrenar.
2. **Brazos son un problema independiente** — 14 DOF de brazos (7 por lado) con acción en espacio articular. Se entrena por separado con la política de piernas congelada.
3. **Navegación es percepción, no control** — LIDAR + cámara procesados por una red pequeña que produce waypoints o comandos de velocidad al orquestador.
4. **El orquestador es una FSM** — No necesita RL, son transiciones de estado basadas en condiciones claras (distancia a caja < umbral → transición a agarre).

---

## 5. Detalle de Cada Componente

### 5.1 Política de Locomoción (EXISTENTE)

- **Archivo:** `politicas/model_DR_jit.pt`
- **Arquitectura:** MLP (48 → 512 → 256 → 128 → 12)
- **Entradas (48):** 12 posiciones + 12 velocidades articulares + 12 acciones previas + 12 proyección gravedad
- **Salidas (12):** Acciones para piernas (hip_pitch/roll/yaw, knee, ankle_pitch/roll × 2)
- **Frecuencia:** 50 Hz
- **Estado:** LISTA para despliegue

**Uso en pipeline:** El orquestador invoca esta política para las fases de APROXIMACIÓN y TRANSPORTE. Los brazos se mantienen en postura fija durante locomoción, o se controlan en paralelo por la política de brazos.

### 5.2 Política de Brazos (NUEVA — Entrenar)

#### Espacio de Observación

| Observación | Dimensión | Fuente |
|---|---|---|
| Posición articular brazos (14) | 14 | `jointpos` sensores |
| Velocidad articular brazos (14) | 14 | `jointvel` sensores |
| Posición del target (caja) relativa al torso | 3 | `framepos` del sitio de la caja |
| Orientación del target relativa | 4 (quat) | Derivada de `framequat` |
| Contacto mano izq (booleano + magnitud) | 2 | `mj_contactForce` |
| Contacto mano der (booleano + magnitud) | 2 | `mj_contactForce` |
| Posición relativa de manos al target | 6 (3+3) | `framepos` de rubber_hand sites |
| Acciones previas | 14 | Buffer interno |
| **Total** | **~57** | |

#### Espacio de Acción

| Acción | Dimensión | Rango |
|---|---|---|
| Brazo izq: shoulder_pitch/roll/yaw, elbow, wrist_roll/pitch/yaw | 7 | [-1, 1] normalizado → rango articular |
| Brazo der: shoulder_pitch/roll/yaw, elbow, wrist_roll/pitch/yaw | 7 | [-1, 1] normalizado → rango articular |
| **Total** | **14** | |

#### Función de Recompensa (Agarre)

```python
# Componentes principales:
r_approach  = -distance(hand_left, box) - distance(hand_right, box)  # Acercarse
r_contact   = contact_left * contact_right * 10.0                     # Contacto bilateral
r_grasp     = -|f_left - f_right| * 0.5                               # Fuerzas balanceadas
r_lift      = box_height * 2.0 if both_contacts else 0               # Levantar caja
r_center    = -|box_x - robot_x| - |box_y - robot_y|                # Mantener centrada
r_alive     = 0.1                                                      # Penalización por caída
r_torque    = -sum(torque_brazos^2) * 0.001                          # Eficiencia
```

#### Entrenamiento

- **Framework:** MuJoCo Playground (MJX) o RSL-RL (lo que ya usa HumanoidVerse)
- **Algoritmo:** PPO (mismo que locomoción)
- **Paralelización:** 4096+ entornos en GPU
- **Duración estimada:** 2-4 horas en RTX 5090
- **Domain Randomization:** Posición de caja (x±0.3, y±0.2, z fija en mesa), tamaño de caja (±20%), fricción, masa de caja

### 5.3 Política de Navegación + Percepción (NUEVA — Entrenar)

#### Espacio de Observación

| Observación | Dimensión | Fuente |
|---|---|---|
| LIDAR 32 rayos | 32 | `rangefinder` sensores |
| Posición robot (x, y) | 2 | `framepos` |
| Orientación robot (yaw) | 1 | `framequat` → euler |
| Vector al objetivo (caja/punto B) | 2 | Calculado |
| **Total** | **~37** | |

Opcionalmente: cámara RGB-D procesada por CNN pequeña (ResNet10 o similar) para detección de la caja cuando está en el campo visual.

#### Espacio de Acción

| Acción | Dimensión | Uso |
|---|---|---|
| Velocidad lineal (x) | 1 | Comando al orquestador |
| Velocidad angular (yaw) | 1 | Comando al orquestador |
| **Total** | **2** | |

Estos comandos se traducen a la acción de locomoción (ya sea adaptando el comando de velocidad al input de la política DR, o reentrenando la política de locomoción para aceptar comandos de velocidad).

#### Función de Recompensa (Navegación)

```python
r_goal    = -distance(robot, target)           # Acercarse al objetivo
r_obstacle = -collision_penalty * 10.0         # Evitar obstáculos
r_smooth  = -|cmd_linear - prev_cmd| * 0.1     # Comandos suaves
r_lidar   = -min(lidar_readings[:8]) * 0.5 if min < 0.3 else 0  # Evitar paredes
```

---

## 6. Modelo MuJoCo Integrado: Propuesta

Necesitamos crear un XML que combine lo mejor de ambos modelos existentes:

### Desde `g1_23dof.xml`:
- Cinemática completa 23 DOF con default classes (leg_motor, arm_motor, etc.)
- Sensores de posición, velocidad, torque para los 23 DOF
- 2 IMUs

### Desde `lydar.xml`:
- 32 rangefinders LIDAR
- Escena con mesas, obstáculos
- Manos rubber_hand con muñecas completas (6 DOF por brazo = 29 DOF total)

### Añadir:

```xml
<!-- Caja a agarrar (cuerpo libre para que la física la mueva) -->
<body name="target_box" pos="1.5 0 0.35">
  <freejoint name="box_joint"/>
  <joint name="box_free" type="free"/>
  <geom name="box_geom" type="box" size="0.06 0.06 0.06" 
        mass="0.3" rgba="0.8 0.2 0.2 1" 
        contype="1" conaffinity="1" friction="1.0 0.5 0.5"/>
  <site name="box_center" size="0.01" pos="0 0 0" rgba="1 0 0 1"/>
</body>

<!-- Punto de depósito (marcador visual) -->
<body name="target_zone" pos="-1.5 0 0.0">
  <geom name="target_marker" type="cylinder" size="0.15 0.005" 
        rgba="0 1 0 0.3" contype="0" conaffinity="0"/>
</body>

<!-- Sitios de contacto en las manos para detectar agarre -->
<!-- (añadir dentro de los bodies left/right_rubber_hand) -->
<site name="left_palm_center" pos="0.02 0 0" size="0.025" rgba="1 1 0 0.5"/>
<site name="right_palm_center" pos="0.02 0 0" size="0.025" rgba="1 1 0 0.5"/>

<!-- Sensores de posición de manos -->
<framepos name="left_hand_pos" objtype="site" objname="left_palm_center"/>
<framepos name="right_hand_pos" objtype="site" objname="right_palm_center"/>
<framepos name="box_pos" objtype="site" objname="box_center"/>
```

---

## 7. Flujo de Entrenamiento Propuesto

### Fase 1: Agarre Estático (1-2 días)
**Objetivo:** Brazos agarran la caja con el robot parado.
- Robot inmóvil, caja en posición fija enfrente
- Solo política de brazos (14 DOF)
- Recompensa: aproximación + contacto bilateral + levantar
- Entorno: Mesa con caja, robot de pie

```
Entorno: g1_grip_estatico.xml
Política: brazos (14 acciones)
Obs: 57 dimensiones
Sim: MuJoCo Playground (MJX) en GPU
```

### Fase 2: Locomoción + Brazos Combinados (2-3 días)
**Objetivo:** Robot camina hacia la caja, se detiene, y la agarra.
- Política de locomoción + política de brazos corriendo en paralelo
- Orquestador simple: si distancia < 0.5m → congelar locomoción, activar agarre
- Recompensa: combinada de locomoción + agarre

```
Entorno: g1_walk_and_grasp.xml
Política: locomoción (existente) + brazos (fase 1)
Obs: locomoción (48) + brazos (57) + contexto (5)
Orquestador: FSM simple en Python
```

### Fase 3: Transporte (2-3 días)
**Objetivo:** Robot camina sosteniendo la caja de A a B.
- Ambas políticas activas simultáneamente
- Política de brazos debe MANTENER contacto durante locomoción
- Política de locomoción recibe comandos de velocidad de navegación
- Recompensa: mantener contacto + llegar a destino

```
Entorno: g1_full_pipeline.xml (con LIDAR + mesas + obstáculos)
Política: navegación (2) + locomoción (12) + brazos (14)
Orquestador: FSM con 5 estados
```

### Fase 4: Depósito y Ciclo Completo (1-2 días)
**Objetivo:** Soltar la caja en el punto B y repetir.
- Añadir fase de "abrir manos y retroceder"
- Ciclo completo: DETECTAR → ACERCARSE → AGARRAR → TRANSPORTAR → DEPOSITAR
- Recompensa por ciclo completo exitoso

---

## 8. Stack Tecnológico Recomendado

### Para Entrenamiento (GPU)

| Componente | Recomendación | Alternativa |
|---|---|---|
| Simulador | **MuJoCo Playground (MJX)** | Genesis |
| Framework RL | **RSL-RL** (ya instalado con HumanoidVerse) | MuJoCo Playground built-in |
| Paralelización | MJX (4096+ envs en RTX 5090) | Isaac Lab (si MuJoCo no escala) |
| Entorno | `hgen` (conda) | — |

**Justificación MJX:**
- Ya tenemos experiencia con HumanoidVerse que usa MuJoCo
- MJX soporta GPU parallelization nativa
- Los modelos XML ya existen y funcionan
- MuJoCo Playground tiene manipulation environments probados (PandaPickCube)
- No necesitamos convertir modelos a USD/Isaac format

### Para Validación (CPU)

| Componente | Herramienta |
|---|---|
| Simulador | MuJoCo estándar (CPU) |
| Script | Adaptación de `simulacion/sim_hv.py` |
| Entorno | `g1_udc` (conda) |
| Visualización | Offscreen rendering + guardado de video |

### Para Despliegue (Robot Real)

| Componente | Herramienta |
|---|---|
| Comunicación | Unitree SDK2 (DDS) |
| Script | Adaptación de `despliegue/deploy_dual.py` |
| Sensores reales | LIDAR 2D via ROS2, Cámara RealSense, contact force via torque sensors |
| Entorno | `g1_udc` (conda) |

---

## 9. Curva de Aprendizaje y Dependencias

### Secuencia de Dependencias

```
1. Crear XML integrado (g1_manipulation_full.xml)
   ├── Base: lydar.xml (29 DOF + LIDAR + escena)
   ├── Añadir: caja libre + zona target + sitios de contacto
   └── Añadir: sensores de posición de manos + posición de caja

2. Probar XML en MuJoCo estático
   └── Verificar que el robot no colapsa con brazos

3. Script de prueba: brazos mueven a posiciones predefinidas
   └── Adaptar g1_caja.py para MuJoCo (en lugar de SDK real)

4. Entrenar política de agarre (Fase 1)
   ├── Configurar MuJoCo Playground env para G1 + caja
   ├── Definir obs/act/reward
   └── PPO con DR

5. Entrenar política de navegación (puede ser paralelo a 4)
   ├── LIDAR como entrada
   ├── Comandos de velocidad como salida
   └── Navegación punto a punto en escena con obstáculos

6. Integrar con locomoción existente (Fase 2)
   └── Orquestador FSM

7. Transporte + depósito (Fases 3-4)
   └── Ciclo completo

8. Validar en MuJoCo headless
   └── Script de validación con 16+ escenarios

9. Desplegar en robot real
   └── Adaptación de deploy_dual.py
```

---

## 10. Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|
| Rubber hand no puede sostener la caja durante locomoción | Alta | Crítico | Entrenar con DR en fricción, considerar agregar velcro/espuma en manos reales |
| Política de brazos y locomoción interfieren entre sí | Media | Alto | Entrenar con la política de locomoción CONGELADA; brazos operan en espacio residual |
| MJX no escala a 29 DOF + objetos dinámicos | Baja | Medio | Caer a MuJoCo CPU con vectorización (256 envs) o Isaac Lab |
| Gap sim-real en sensores (LIDAR real vs simulado) | Media | Medio | DR agresivo en ruido y resolución del LIDAR |
| Caja se escapa del agarre por vibración de caminata | Alta | Alto | Recompensa de "mantener contacto" continua; penalizar pérdida de contacto fuertemente |

---

## 11. Estimación de Esfuerzo

| Fase | Tiempo | Esfuerzo |
|---|---|---|
| Crear XML integrado + script de prueba | 1 día | Medio |
| Entrenar agarre estático (Fase 1) | 1-2 días | Medio |
| Entrenar navegación (paralelo) | 1-2 días | Medio |
| Integrar locomoción + brazos (Fase 2) | 2-3 días | Alto |
| Transporte + ciclo completo (Fases 3-4) | 2-3 días | Alto |
| Validación headless + reporte | 1 día | Bajo |
| **Total estimado** | **8-12 días** | |

---

## 12. Próximos Pasos Inmediatos

1. **Crear `escenas/g1_manipulation_full.xml`** — Fusionar `lydar.xml` (29 DOF + LIDAR) con la caja libre, zona target, y sitios de contacto en manos
2. **Script de validación** — Adaptar `sim_hv.py` para el modelo 29 DOF con LIDAR y verificar que corre headless
3. **Configurar MuJoCo Playground** — Crear un env custom para G1 basado en `PandaPickCube` pero con el modelo G1
4. **Entrenar Fase 1** — Agarre estático con brazos, robot parado

---

## Apéndice A: Mapeo de MuJoCo Playground → G1

| Playground Env | Acción | Observación | Equivalente G1 |
|---|---|---|---|
| `PandaPickCube` | 7 (joint vel) | jointpos + cube_pos | Brazo izq (7 DOF) → caja |
| `LeapCubeReorient` | 16 (LEAP DOF) | jointpos + object | 2 brazos (14 DOF) → reorientar |
| `AlohaHandOver` | 14 (dual arm) | jointpos + obj | 2 brazos G1 (14 DOF) → pasar objeto |
| **Nuestro caso** | **14 (dual arm)** | **57 (joints + contacts + target)** | **G1 dual arm + caja + locomoción** |

## Apéndice B: Índices de Articulaciones (referencia de `g1_caja.py`)

```python
# Piernas: 0-11
# Cintura: 12-14
# Brazo Izq: 15-21 (shoulder_pitch/roll/yaw, elbow, wrist_roll/pitch/yaw)
# Brazo Der: 22-28 (shoulder_pitch/roll/yaw, elbow, wrist_roll/pitch/yaw)
# kNotUsedJoint: 29 (liberación de seguridad SDK)
```

## Apéndice C: Archivos Clave

| Archivo | Rol | Estado |
|---|---|---|
| `escenas/g1_23dof.xml` | Modelo 23 DOF con sensores completos | Funcional |
| `escenas/lydar.xml` | Modelo 29 DOF + LIDAR + escena | Funcional |
| `codigos/vision/g1_caja.py` | Secuencias de agarre (robot real) | Funcional |
| `politicas/model_DR_jit.pt` | Política locomoción DR | LISTA |
| `simulacion/sim_hv.py` | Simulación headless MuJoCo | Funcional |
| `entrenamiento/export_politica.py` | Export JIT | Funcional |
| `codigos/deteccion/detector.py` | YOLO detección | Funcional |
| `codigos/lidar/lidar_2d.py` | LIDAR ROS2 | Funcional |
