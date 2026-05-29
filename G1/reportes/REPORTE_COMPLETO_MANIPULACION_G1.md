# Reporte Completo: Investigación y Diseño de Pipeline de Sensores y Manipulación para Unitree G1

**Fecha:** 2026-05-14  
**Autor:** Sisyphus (AI Orchestrator)  
**Proyecto:** Unitree G1 - Universidad de Colombia  
**Estado:** Fase de Diseño Técnico Completada, Listo para Implementación  

---

## Tabla de Contenidos

1. [Resumen Ejecutivo](#1-resumen-ejecutivo)
2. [Contexto y Motivación](#2-contexto-y-motivación)
3. [Metodología de Investigación](#3-metodología-de-investigación)
4. [Hallazgos por Área](#4-hallazgos-por-área)
   - 4.1 [Sensores en MuJoCo](#41-sensores-en-mujoco)
   - 4.2 [Modelos de Manos del G1](#42-modelos-de-manos-del-g1)
   - 4.3 [Estrategias de Grasping](#43-estrategias-de-grasping)
   - 4.4 [Transporte y Control de Cuerpo Completo](#44-transporte-y-control-de-cuerpo-completo)
   - 4.5 [Frameworks de Simulación y RL](#45-frameworks-de-simulación-y-rl)
5. [Decisiones de Diseño](#5-decisiones-de-diseño)
6. [Arquitectura del Sistema](#6-arquitectura-del-sistema)
7. [Plan de Implementación](#7-plan-de-implementación)
8. [Riesgos y Mitigaciones](#8-riesgos-y-mitigaciones)
9. [Conclusiones](#9-conclusiones)

---

## 1. Resumen Ejecutivo

Este documento presenta el resultado de una investigación exhaustiva para habilitar al robot humanoide **Unitree G1** con capacidades de manipulación avanzada: **detectar una caja, agarrarla con ambas manos, transportarla caminando y depositarla en un punto objetivo**. 

La investigación abarcó:
- **Sensores:** Cámaras RGB-D, LIDAR 2D, sensores de fuerza de contacto.
- **Manipulación:** Grasping con manos dexterous de 3 dedos (pulgar, índice, medio).
- **Locomoción:** Integración con la política de caminata existente (Domain Randomization).
- **Frameworks:** Comparativa entre MuJoCo MJX, Isaac Lab y Genesis.

**Resultado clave:** Se diseñó una arquitectura jerárquica de 3 políticas (locomoción + brazos + navegación) y se obtuvo el modelo oficial de manos articuladas del G1 desde la MuJoCo Menagerie de Google DeepMind.

---

## 2. Contexto y Motivación

### 2.1 Estado Inicial del Proyecto

Al inicio de esta investigación, el proyecto contaba con:
- **Política de locomoción DR validada:** `model_DR_jit.pt` (12 DOF de piernas, 48 obs → 12 acciones).
- **Modelo MuJoCo 23 DOF:** `g1_23dof.xml` con brazos básicos (sin dedos).
- **Modelo MuJoCo 29 DOF con LIDAR:** `lydar.xml` con 32 rayos LIDAR.
- **Código de manipulación básico:** `g1_caja.py` con secuencias predefinidas de agarre.
- **Infraestructura de visión:** YOLO para detección de objetos.

### 2.2 Problema a Resolver

El objetivo era responder: **"¿Cómo podemos hacer que el G1 agarre una caja y la transporte de A a B usando RL/IL en simulación?"**

Las preguntas específicas eran:
1. ¿Qué sensores necesitamos y cómo se implementan en MuJoCo?
2. ¿Cómo entrenamos una política de agarre si el robot tiene manos complejas?
3. ¿Cómo combinamos locomoción y manipulación sin que se interfieran?
4. ¿Qué simulador/framework es óptimo para entrenar esto en nuestra RTX 5090?

---

## 3. Metodología de Investigación

### 3.1 Primer Intento: Sub-agentes Masivos (Fallido)

Inicialmente se intentó lanzar **25 sub-agentes organizados en 5 grupos** para investigar en paralelo:
- **Grupo 1 (Sensores):** 5 agentes para LIDAR, cámaras, fuerza de contacto.
- **Grupo 2 (Grasping):** 5 agentes para políticas de agarre, reward shaping.
- **Grupo 3 (Transporte):** 5 agentes para whole-body control, navegación.
- **Grupo 4 (Frameworks):** 5 agentes para comparar simuladores.
- **Grupo 5 (Arquitectura):** 5 agentes para diseñar el pipeline de software.

**Resultado:** Todos los agentes `librarian` fallaron con errores de `invalid x-api-key` o `ProviderModelNotFoundError`. Los agentes `oracle` sufrieron timeouts después de 30 minutos.

**Lección aprendida:** La infraestructura de sub-agentes externos no estaba disponible. Se debía adoptar un enfoque híbrido.

### 3.2 Segundo Intento: Enfoque Híbrido (Exitoso)

Se adoptó una estrategia donde:
- **Yo (Sisyphus)** realicé la investigación directa usando herramientas nativas.
- **Fuentes consultadas:**
  - **Context7:** Documentación oficial de MuJoCo y MuJoCo Playground.
  - **Web Search:** Papers de robótica (arXiv), benchmarks de hardware.
  - **GitHub Search:** Implementaciones reales de grasping en MuJoCo.
  - **Repositorio local:** Análisis de los XML existentes (`g1_23dof.xml`, `lydar.xml`).

**Ventaja:** Este enfoque permitió un control total sobre la calidad de la información y la capacidad de cruzar datos entre fuentes.

---

## 4. Hallazgos por Área

### 4.1 Sensores en MuJoCo

#### 4.1.1 LIDAR 2D (Rangefinder)

**Hallazgo:** MuJoCo soporta sensores `rangefinder` que lanzan rayos desde un `site` y miden la distancia al primer obstáculo.

**Implementación en nuestro proyecto:**
- El modelo `lydar.xml` ya tiene **32 sensores rangefinder** dispuestos en círculo (360°, uno cada 11.25°).
- Cada sensor tiene un alcance de 10m y ruido gaussiano de 1cm.
- Lectura en Python: `data.sensordata[idx]` donde `idx` corresponde al sensor.
- Si el rayo no impacta nada, retorna `-1`.

**Decisión:** Reutilizar la configuración LIDAR existente y añadir más rayos frontales para la aproximación a la caja.

#### 4.1.2 Cámara RGB-D

**Hallazgo:** MuJoCo permite renderizado offscreen mediante la clase `mujoco.Renderer`.

**Código de referencia:**
```python
renderer = mujoco.Renderer(model, height=480, width=640)
renderer.update_scene(data, camera='head_cam')
pixels = renderer.render()  # RGB
renderer.enable_depth_rendering(True)
depth = renderer.render()   # Depth map
```

**Decisión:** Usar la cámara frontal del G1 para alimentar el detector YOLO. El mapa de profundidad servirá para estimar la distancia 3D a la caja.

#### 4.1.3 Sensores de Fuerza de Contacto

**Hallazgo:** `mj_contactForce` extrae el vector de fuerza 6D (3 fuerzas + 3 torques) de cada contacto activo en la simulación.

**Aplicación:** Detectar si los dedos están tocando la caja y con qué fuerza. Esto es crítico para:
- Saber cuándo el agarre es firme.
- Evitar aplastar la caja (fuerza excesiva).
- Detectar si la caja se resbala (pérdida de fuerza de fricción).

### 4.2 Modelos de Manos del G1

#### 4.2.1 Confusión Inicial: "Rubber Hands" vs Manos Articuladas

**Hallazgo inicial:** Los XML locales (`g1_23dof.xml`, `lydar.xml`) usaban `left_wrist_roll_rubber_hand.STL`, lo que sugirió que el robot tenía **paletas rígidas sin dedos**.

**Corrección crítica:** El usuario indicó que el robot real tiene **manos de tres dedos**. Esto cambió completamente la estrategia de grasping.

#### 4.2.2 Descubrimiento del Modelo Oficial

**Búsqueda:** Se buscó en el repositorio oficial de Unitree (`unitreerobotics/unitree_ros`) y en la MuJoCo Menagerie de Google DeepMind.

**Hallazgo:** En `mujoco_menagerie/unitree_g1/` existe el archivo **`g1_with_hands.xml`** (también referido como `g1_29dof_with_hand_rev_1_0`).

**Características del modelo:**
- **Pulgar:** 3 articulaciones (`thumb_0`, `thumb_1`, `thumb_2`).
- **Índice:** 2 articulaciones (`index_0`, `index_1`).
- **Medio:** 2 articulaciones (`middle_0`, `middle_1`).
- **Total por mano:** 7 DOF adicionales.
- **Actuadores:** Controladores de posición (`position`) con `kp=500`.

**Decisión:** Descargar e integrar este modelo como base para todo el pipeline de manipulación.

### 4.3 Estrategias de Grasping

#### 4.3.1 Para Manos sin Dedos (Rubber Hands) - Investigación Inicial

Se investigó cómo hacer grasping con paletas rígidas:
- **Técnica:** Agarre por fricción lateral (clamp bilateral).
- **Problema:** Las colisiones malla-a-malla en MuJoCo son inestables.
- **Solución:** Añadir pequeños `box geoms` en los puntos de contacto para crear contactos multipunto estables.
- **Reward:** Contacto bilateral simultáneo + levantamiento.

**Estado:** Esta línea de investigación fue **descartada** tras descubrir las manos articuladas.

#### 4.3.2 Para Manos Dexterous de 3 Dedos (Estrategia Actual)

**Investigación de papers:**
- **Paper clave (arXiv:2109.11234):** Demostró que combinar información de contacto (posición, normal, fuerza) en la recompensa alcanza **95.4% de éxito** para cuboides.
- **Paper clave (arXiv:2306.03484):** Usó recompensas segmentadas: aproximación → contacto con ≥2 dedos → elevación.
- **Paper clave (MuJoCo RL UR5):** Mostró que el reward hacking es inevitable; se necesitan al menos 11 iteraciones de la función de recompensa.

**Estrategia de Reward Shaping seleccionada:**

```python
# Fase 1: Aproximación
r_approach = -distance(palm_center, box_center)

# Fase 2: Cierre de dedos
r_finger_closure = -sum(joint_angle_differences_from_fully_closed)

# Fase 3: Contacto multipunto
r_contact = sum(contact_force_magnitude_for_each_fingertip)

# Fase 4: Elevación (solo si hay suficiente contacto)
r_lift = box_height * 2.0 if num_contacts >= 4 else 0

# Regularización
r_smooth = -0.01 * ||action_t - action_t-1||^2
r_torque = -0.001 * sum(torque^2)
```

**Decisión:** Entrenar una política de "Power Grasp" donde los 3 dedos de cada mano se cierran envolventemente alrededor de la caja.

### 4.4 Transporte y Control de Cuerpo Completo

#### 4.4.1 Problema: Cambio de Dinámica

**Hallazgo:** Cuando el robot sostiene una caja, su Centro de Masa (CoM) se desplaza significativamente. Esto puede hacer que la política de locomoción existente falle.

#### 4.4.2 Solución: Control Residual (Residual Learning)

**Investigación de papers:**
- **IO-WBC (Interaction-Oriented Whole-Body Control):** Arquitectura jerárquica donde un generador de referencias (RG) provee trayectorias y una política RL genera "correcciones residuales" para compensar perturbaciones.
- **ResMimic:** Entrenar una política residual sobre una política base congelada es más estable que fine-tuning.

**Decisión:**
- **Base:** Política de locomoción DR existente (`model_DR_jit.pt`) se mantiene **congelada**.
- **Residual:** Nueva política de brazos y dedos que genera correcciones sobre la base.
- **Ventaja:** El robot mantiene la estabilidad de caminata mientras los brazos se adaptan dinámicamente.

#### 4.4.3 Estabilidad del CoM

**Hallazgo:** Se debe implementar un regularizador basado en el **ZMP (Zero Moment Point)** para asegurar que la proyección del CoM permanezca dentro del polígono de soporte de los pies.

### 4.5 Frameworks de Simulación y RL

#### 4.5.1 Comparativa de Rendimiento (RTX 5090)

| Framework | FPS (Estimado) | Pros | Contras |
|---|---|---|---|
| **MuJoCo MJX** | ~2.7M SPS | Velocidad extrema, código abierto, sim-to-real probado | Colisiones de malla lentas |
| **Isaac Lab** | ~80K-90K FPS | Sensores nativos, renderizado fotorrealista | Mucho más lento, overhead de USD |
| **Genesis** | Variable | Nuevo, generativo | Benchmarks inflados, menos maduro |

**Fuente:** Benchmarks oficiales de Isaac Lab (RTX 5090: 82K FPS) y papers de MJX (2.7M SPS en A100, escalable linealmente).

#### 4.5.2 Decisión del Stack

**Entrenamiento:** **MuJoCo MJX** + **RSL-RL** (PPO).
- Justificación: MJX es ~30x más rápido que Isaac Lab. RSL-RL ya está integrado en HumanoidVerse.
- Para 4096 entornos paralelos en RTX 5090, se estima ~500K-1M SPS.

**Validación:** **MuJoCo CPU** (headless).
- Justificación: Mayor fidelidad física antes del despliegue real.

**Despliegue:** **Unitree SDK2** (DDS).
- Justificación: Es el estándar de comunicación del G1 físico.

---

## 5. Decisiones de Diseño

### 5.1 ¿Por qué manos dexterous en lugar de paletas?

**Contexto:** Inicialmente se asumió paletas (rubber hands) porque los XML locales usaban ese modelo.
**Corrección:** El usuario confirmó que el robot real tiene manos de 3 dedos.
**Impacto:**
- **Positivo:** El agarre es mucho más estable (envolvente vs fricción lateral).
- **Positivo:** Se pueden hacer manipulaciones más complejas en el futuro.
- **Negativo:** El espacio de acción aumenta de 14 a 28 DOF para los brazos.

### 5.2 ¿Por qué arquitectura jerárquica en lugar de una sola política?

**Opción A (Monolítica):** Una sola política de 40+ DOF que controla piernas, brazos y dedos simultáneamente.
- **Contra:** Muy difícil de entrenar. La locomoción ya funciona; no hay por qué reentrenarla.

**Opción B (Jerárquica):** 3 políticas especializadas + orquestador.
- **Pro:** Cada política resuelve un sub-problema manejable.
- **Pro:** La política de locomoción existente se reutiliza sin cambios.
- **Pro:** Más fácil de debuggear y validar por partes.

**Decisión:** Opción B (jerárquica).

### 5.3 ¿Por qué MJX en lugar de Isaac Lab?

**Contexto:** Isaac Lab tiene mejores sensores visuales integrados.
**Contra:** Es 30x más lento y requiere convertir modelos a USD.
**Pro MJX:** Ya tenemos los XML de MuJoCo, el pipeline de exportación JIT funciona, y la velocidad de entrenamiento es crítica para iterar rápido.

### 5.4 ¿Por qué residual learning en lugar de fine-tuning?

**Contexto:** Se necesita que el robot camine mientras manipula.
**Fine-tuning:** Modificar la política de locomoción existente para que también controle brazos.
- **Contra:** Riesgo de "olvidar" cómo caminar (catastrophic forgetting).

**Residual learning:** Congelar la política de locomoción y entrenar una nueva que solo genere correcciones.
- **Pro:** La locomoción se preserva exactamente como está.
- **Pro:** El entrenamiento es más estable porque el espacio de estados es más pequeño.

---

## 6. Arquitectura del Sistema

### 6.1 Diagrama de Alto Nivel

```
┌─────────────────────────────────────────────────────────────┐
│                    ORQUESTADOR (FSM)                         │
│  Estados: DETECTAR → ACERCARSE → AGARRAR → TRANSPORTAR →    │
│           DEPOSITAR                                          │
│  Entradas: LIDAR, posición caja, contacto, IMU              │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
┌──────────────┐ ┌──────────┐ ┌──────────────┐
│  POLÍTICA    │ │ POLÍTICA │ │  POLÍTICA    │
│  NAVEGACIÓN  │ │ BRAZOS   │ │  LOCOMOCIÓN  │
│  (2 DOF)     │ │ (28 DOF) │ │  (12 DOF)    │
│              │ │          │ │              │
│  LIDAR →     │ │  Cámara +│ │  Ya existe:  │
│  v, ω        │ │  Contacto│ │  model_DR_   │
│              │ │  → q_brazos│ │  jit.pt      │
└──────────────┘ └──────────┘ └──────────────┘
```

### 6.2 Especificación de Componentes

#### Orquestador (Finite State Machine)
- **Frecuencia:** 50 Hz (sincronizado con las políticas).
- **Entradas:**
  - Distancia al objetivo (LIDAR/cámara).
  - Estado de contacto (fuerza en dedos).
  - Posición del robot (odometría).
- **Transiciones:**
  - `DETECTAR → ACERCARSE`: Cuando la caja es visible en el LIDAR/cámara.
  - `ACERCARSE → AGARRAR`: Cuando distancia < 0.5m.
  - `AGARRAR → TRANSPORTAR`: Cuando se detecta agarre firme (≥4 puntos de contacto).
  - `TRANSPORTAR → DEPOSITAR`: Cuando distancia al punto B < 0.3m.

#### Política de Navegación
- **Observación:** 32 rayos LIDAR + posición (x,y) + orientación (yaw) + vector al objetivo.
- **Acción:** Velocidad lineal (v) + velocidad angular (ω).
- **Algoritmo:** PPO con MLP pequeño (32+5 → 64 → 32 → 2).

#### Política de Brazos (y Dedos)
- **Observación:** 
  - 28 posiciones articulares (brazos + dedos).
  - 28 velocidades articulares.
  - Posición 3D de la caja relativa al torso.
  - Fuerzas de contacto en las yemas de los dedos (6 valores).
  - Acciones previas.
  - **Total:** ~70 dimensiones.
- **Acción:** 28 valores normalizados [-1, 1] → rangos articulares reales.
- **Algoritmo:** PPO con MLP (70 → 512 → 256 → 128 → 28).

#### Política de Locomoción (EXISTENTE)
- **Archivo:** `politicas/model_DR_jit.pt`.
- **Entradas:** 48 dimensiones (piernas + IMU).
- **Salidas:** 12 acciones (piernas).
- **Estado:** Congelada, no se reentrena.

### 6.3 Pipeline de Datos de Sensores

```
LIDAR (32 rayos) ──► Filtro de ruido ──► Política de Navegación
                                        (produce v, ω)

Cámara RGB ──► YOLO Detector ──► Posición 3D estimada de la caja
                                    │
                                    ▼
                           Política de Brazos
                           (produce ángulos de joints)

Contacto (mj_contactForce) ──► Detector de agarre ──► Orquestador
                                    │
                                    ▼
                           Recompensa de agarre firme
```

---

## 7. Plan de Implementación

### Fase 1: Modelado XML Integrado (1 día)
**Tarea:** Crear `escenas/g1_manipulation_full.xml`.
**Base:** `g1_dexterous.xml` (manos articuladas).
**Añadir:**
- 32 sensores LIDAR (de `lydar.xml`).
- Caja libre como cuerpo dinámico (`freejoint`).
- Zona de depósito (marcador visual).
- Sensores de contacto en las yemas de los dedos.
- Cámara RGB-D en la cabeza.

**Entregable:** XML que carga sin errores en MuJoCo viewer.

### Fase 2: Entrenamiento de Agarre Estático (2 días)
**Tarea:** Robot parado, solo brazos y dedos.
**Entorno:** MuJoCo Playground (MJX) con 4096 entornos paralelos.
**Recompensa:** Aproximación → Cierre de dedos → Contacto → Elevación.
**Entregable:** `politica_agarre_estatico.pt`.

### Fase 3: Entrenamiento de Navegación (2 días)
**Tarea:** LIDAR → comandos de velocidad.
**Entorno:** Escena con obstáculos (mesas, paredes).
**Recompensa:** Acercarse al objetivo + evitar colisiones.
**Entregable:** `politica_navegacion.pt`.

### Fase 4: Integración y Transporte (2 días)
**Tarea:** Combinar las 3 políticas con el orquestador FSM.
**Desafío:** Sincronizar frecuencias y manejar transiciones de estado.
**Entregable:** Script `simulacion/pipeline_completo.py`.

### Fase 5: Validación Headless y Reporte (1 día)
**Tarea:** Ejecutar 16+ escenarios de validación (como se hizo con la política DR).
**Entregable:** `reportes/validacion_manipulacion.md`.

### Fase 6: Despliegue en Robot Real (2 días)
**Tarea:** Adaptar `despliegue/deploy_dual.py` para incluir control de brazos y dedos.
**Entregable:** Validación en hardware físico.

**Tiempo total estimado:** 10 días.

---

## 8. Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|
| **Deslizamiento de la caja** durante transporte | Media | Alto | DR agresivo en fricción de contacto; entrenar con payloads variables (0.1kg - 2kg). |
| **Auto-colisiones** entre dedos al cerrar | Media | Medio | Penalización por auto-colisiones en reward; tuning de `contype`/`conaffinity`. |
| **Inestabilidad de MJX** con contactos de dedos | Media | Alto | Validar primero en MuJoCo CPU; usar `box geoms` en yemas si las mallas son inestables. |
| **Cambio de CoM** rompe la locomoción | Alta | Crítico | Usar residual learning (congelar locomoción); entrenar con ZMP regularization. |
| **Sim-to-real gap** en sensores de contacto | Media | Medio | DR en ruido de sensores; calibrar fuerzas de contacto en el robot real. |
| **Tiempo de entrenamiento excesivo** | Baja | Medio | MJX en RTX 5090 debería ser rápido; si no, reducir resolución de LIDAR o usar CPU vectorizado. |

---

## 9. Conclusiones

1. **El proyecto es técnicamente viable.** Contamos con todos los componentes necesarios: modelo de manos articuladas, infraestructura de sensores, política de locomoción funcional, y frameworks de entrenamiento probados.

2. **La clave del éxito es la arquitectura jerárquica.** Separar locomoción, manipulación y navegación en políticas especializadas reduce drásticamente la complejidad de entrenamiento.

3. **Las manos dexterous de 3 dedos son una ventaja significativa.** Aunque aumentan la dimensionalidad del problema, permiten agarres estables tipo "power grasp" que serían imposibles con paletas rígidas.

4. **MuJoCo MJX es la elección correcta para el entrenamiento.** Su velocidad (millones de pasos por segundo) permite iterar rápido, y la compatibilidad con los XML existentes evita conversiones de formato.

5. **El próximo paso inmediato es crear el XML integrado** (`g1_manipulation_full.xml`) que combine el modelo dexterous con los sensores LIDAR y la caja objetivo.

---

## Apéndice A: Archivos Clave del Proyecto

| Archivo | Rol | Estado |
|---|---|---|
| `escenas/g1_dexterous.xml` | Modelo 43 DOF con manos articuladas | ✅ Guardado |
| `escenas/lydar.xml` | Modelo 29 DOF + LIDAR 32 rayos | ✅ Existente |
| `politicas/model_DR_jit.pt` | Política locomoción DR | ✅ Validada |
| `reportes/reporte_investigacion_manipulacion_G1.md` | Este documento | ✅ Actualizado |
| `codigos/vision/g1_caja.py` | Secuencias de agarre (robot real) | ✅ Existente |
| `simulacion/sim_hv.py` | Simulación headless MuJoCo | ✅ Funcional |

## Apéndice B: Referencias

1. MuJoCo Documentation (Context7): `/google-deepmind/mujoco`
2. MuJoCo Playground (Context7): `/google-deepmind/mujoco_playground`
3. MuJoCo Menagerie - Unitree G1: `github.com/google-deepmind/mujoco_menagerie/tree/main/unitree_g1`
4. Unitree ROS - G1 Description: `github.com/unitreerobotics/unitree_ros/tree/master/robots/g1_description`
5. Paper: "Tactile Sensing for Grasping" (arXiv:2109.11234)
6. Paper: "G-PAYN: Grasping with DRL" (arXiv:2306.03484)
7. Paper: "IO-WBC for Object Transport" (arXiv:2603.03751)
8. Benchmark: Isaac Lab Performance (RTX 5090)
9. Benchmark: MJX vs Isaac Lab (axiomlogica.com)
