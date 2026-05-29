# Reporte Final: Investigación y Diseño de Sensores y Manipulación para Unitree G1

**Fecha:** 2026-05-14  
**Estado:** Documento de Diseño Técnico (TDD)  
**Objetivo:** Definir el pipeline completo para que el G1 detecte, agarre y transporte una caja, integrando la locomoción DR existente con nuevas capacidades de manipulación.

---

## 1. Implementación de Sensores (MuJoCo)

Para lograr una percepción robusta, se implementarán los siguientes sensores en el XML del modelo:

### 1.1 LIDAR 2D / 3D
- **Implementación:** Uso de sensores `rangefinder`. Para LIDAR 2D, se definen múltiples sitios en un círculo (ya implementado en `lydar.xml`). Para profundidad, se adjunta el `rangefinder` a una `camera`.
- **Configuración XML:** `<rangefinder site="lidar_site" cutoff="10.0" noise="0.01"/>`.
- **Lectura en Python:** Recuperación vía `data.sensordata`. Valor `-1` indica ausencia de impacto.

### 1.2 Cámara RGB-D (Visión)
- **Implementación:** Renderizado offscreen mediante `mujoco.Renderer`.
- **Flujo de Datos:** 
  - `renderer.update_scene(data, camera='head_cam')`
  - `pixels = renderer.render()` $\rightarrow$ RGB
  - `renderer.enable_depth_rendering(True)` $\rightarrow$ Depth map
- **Integración:** Las imágenes alimentarán el detector YOLO para estimar la posición 3D de la caja.

### 1.3 Sensores de Fuerza y Contacto
- **Detección de Agarre:** Uso de `mj_contactForce` para obtener el vector de fuerza 6D en los puntos de contacto.
- **Táctil Simulado:** Implementación de sitios de contacto en las paletas de las manos para obtener señales binarias de contacto.

---

## 2. Estrategia de Grasping (Manos Dexterous de 3 Dedos)

El G1 utiliza manos articuladas con **3 dedos por mano** (pulgar, índice y medio), lo que permite un agarre mucho más versátil y estable que las paletas rígidas. El modelo se encuentra en `escenas/g1_dexterous.xml`.

### 2.1 Cinemática de las Manos
Cada mano añade **7 DOF** al brazo:
- **Pulgar:** 3 articulaciones (`thumb_0`, `thumb_1`, `thumb_2`) para oponerse a los otros dedos.
- **Índice:** 2 articulaciones (`index_0`, `index_1`) para el cierre envolvente.
- **Medio:** 2 articulaciones (`middle_0`, `middle_1`) para estabilizar el agarre.
- **Palm:** La palma actúa como base de soporte durante el contacto.

**Total de DOF de manipulación:** 14 (brazos) + 14 (dedos) = **28 DOF** para ambos brazos.

### 2.2 Reward Shaping para el Agarre (Power Grasp)
La política de brazos se entrenará con recompensas segmentadas por fase, aprovechando la capacidad de cierre envolvente:
1. **Aproximación:** Premiar la reducción de la distancia entre los centros de las palmas y la caja.
2. **Cierre de Dedos:** Recompensa alta cuando los dedos (índice, medio y pulgar) se cierran alrededor de la caja. Se mide por la reducción del ángulo de las articulaciones de los dedos.
3. **Contacto Multipunto:** Premiar el número de puntos de contacto activos entre las yemas de los dedos y la superficie de la caja (usando `mj_contactForce`).
4. **Elevación:** Premiar el incremento de la altura de la caja ($\Delta z$) solo si se detecta un agarre firme (múltiples contactos + fuerza de cierre).
5. **Suavizado:** Penalización al cambio de acción ($-0.01 \times \|a_t - a_{t-1}\|^2$) para evitar oscilaciones y garantizar un cierre suave.

---

## 3. Transporte y Control de Cuerpo Completo (WBC)

### 3.1 Arquitectura de Control Residual
Se propone un enfoque jerárquico para no comprometer la estabilidad de la locomoción:
- **Base:** Política de locomoción DR existente (`model_DR_jit.pt`), congelada.
- **Residual:** Política de brazos y torso que genera correcciones ($\mathbf{a}_t$) sobre la base.
- **Sincronización:** El orquestador coordina el cambio de estados (Detección $\rightarrow$ Aproximación $\rightarrow$ Agarre $\rightarrow$ Transporte).

### 3.2 Estabilidad del CoM y ZMP
Para compensar el desplazamiento del Centro de Masa (CoM) al cargar la caja:
- Se implementará un regularizador basado en el **ZMP (Zero Moment Point)**.
- La política de brazos ajustará la postura del torso para mantener la proyección del CoM dentro de la base de soporte.

---

## 4. Stack Tecnológico y Rendimiento

| Componente | Herramienta | Razón |
|---|---|---|
| **Entrenamiento** | **MuJoCo MJX** | Velocidad extrema ($\sim$2.7M SPS en RTX 5090). |
| **Validación** | **MuJoCo CPU** | Máxima fidelidad física antes del despliegue. |
| **Despliegue** | **Unitree SDK2** | Estándar de comunicación DDS para G1. |
| **Algoritmo RL** | **PPO (RSL-RL)** | Probado y estable en HumanoidVerse. |

---

## 5. Roadmap de Implementación

| Fase | Tarea | Entregable | Tiempo |
|---|---|---|---|
| **1. Modelado** | XML Integrado (`g1_manipulation_full.xml`) basado en `g1_dexterous.xml` | Modelo con Manos Articuladas, LIDAR, Caja y Sensores de Contacto | 1 día |
| **2. Agarre** | Entrenamiento de política de brazos | Modelo `.pt` de agarre estático | 2 días |
| **3. Navegación** | Entrenamiento de política LIDAR $\rightarrow$ Velocidad | Modelo `.pt` de navegación | 2 días |
| **4. Integración** | Orquestador FSM en Python | Script de control jerárquico | 2 días |
| **5. Real** | Despliegue y tuning en robot físico | Validación en hardware real | 2 días |

---

## 6. Riesgos y Mitigaciones

- **Riesgo:** Deslizamiento de la caja por fricción insuficiente en las yemas de los dedos.
- **Mitigación:** Entrenamiento con Domain Randomization agresivo en fricción de contacto (`geom friction`) y fuerzas de cierre de los dedos. Ajuste de los materiales de las yemas en el robot físico.
- **Riesgo:** Inestabilidad al levantar peso debido al cambio de CoM.
- **Mitigación:** Entrenamiento de la política residual con payloads variables y regularización ZMP.
- **Riesgo:** Colisiones auto-inducidas entre dedos durante el cierre.
- **Mitigación:** Penalización por auto-colisiones en la función de recompensa y uso de `contype`/`conaffinity` adecuados en el XML.
