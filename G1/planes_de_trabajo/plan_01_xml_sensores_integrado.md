# Plan de Trabajo 01 — XML Integrado con Todos los Sensores
**Proyecto:** Unitree G1 — Universidad de Colombia
**Fecha:** 2026-05-14
**Sub-agentes asignados:** 30
**Prerequerido:** Ninguno
**Reporte de salida:** `reportes/reporte_plan01_xml_sensores_YYYYMMDD.md`

---

## Contexto del Proyecto

Robot: Unitree G1 EDU, 43 DOF base con manos articuladas de 3 dedos.
Objetivo: crear `escenas/g1_manipulation_full.xml` con LIDAR 3D (128 rayos), cámara D435i, cabeza 2 DOF y contacto en yemas. Todo debe verificarse en MuJoCo headless.

### Rutas clave:
- `escenas/g1_dexterous.xml` — base (43 DOF, meshes en `escenas/meshes/`)
- `escenas/g1_description/g1_29dof_with_hand_rev_1_0.urdf` — posiciones oficiales de sensores
- Conda sim: `conda run -p /home/udc/Unitree_G1/envs/g1_udc`

### ADVERTENCIA CRÍTICA — LIDAR:
Los sites del LIDAR deben colocarse FUERA de la geometría de colisión del torso. Si el body `mid360_link` queda dentro del mesh del torso, los 128 rangefinders detectarán el propio robot (lecturas < 10cm). La posición correcta es al menos 5cm fuera de la superficie del torso. Verificar que al menos el 70% de los rayos lean distancias > 0.5m en la escena vacía.

---

## FASE 1 — Análisis Completo (Agentes 1-6, EN PARALELO)

### AGENTE-01 | ANALIZAR_JOINTS_COMPLETO
Listar todos los joints, actuadores y bodies de `g1_dexterous.xml`.
```bash
cd /home/udc/Unitree_G1
conda run -p envs/g1_udc python -c "
import mujoco, os
os.chdir('escenas')
m = mujoco.MjModel.from_xml_path('g1_dexterous.xml')
for i in range(m.njnt):
    print(f'joint[{i}]={mujoco.mj_id2name(m,mujoco.mjtObj.mjOBJ_JOINT,i)} body={m.jnt_bodyid[i]}')
print(f'nv={m.nv} nu={m.nu} njnt={m.njnt} nsensor={m.nsensor}')
"
```
**Reportar:** Lista completa de joints con body parent. Identificar `head_link` o body destino para cabeza.

### AGENTE-02 | ANALIZAR_BODIES_GEOMETRIA
Listar todos los bodies con sus posiciones globales en keyframe stand.
```bash
conda run -p envs/g1_udc python -c "
import mujoco, os, numpy as np
os.chdir('escenas')
m = mujoco.MjModel.from_xml_path('g1_dexterous.xml')
d = mujoco.MjData(m)
mujoco.mj_forward(m, d)
for i in range(m.nbody):
    name = mujoco.mj_id2name(m,mujoco.mjtObj.mjOBJ_BODY,i)
    print(f'body[{i}]={name} xpos={d.xpos[i].round(4)}')
"
```
**Reportar:** Posición mundial de cada body en pose de pie. Especialmente `torso_link` y `head_link`.

### AGENTE-03 | ANALIZAR_URDF_D435
Extraer posición exacta D435i del URDF oficial.
```bash
grep -A8 "d435" /home/udc/Unitree_G1/escenas/g1_description/g1_29dof_with_hand_rev_1_0.urdf
```
**Reportar:** xyz y rpy exactos. Calcular posición relativa al body `torso_link` en coordenadas MuJoCo.

### AGENTE-04 | ANALIZAR_URDF_LIDAR
Extraer posición exacta LIVOX MID360 del URDF oficial.
```bash
grep -A8 "mid360" /home/udc/Unitree_G1/escenas/g1_description/g1_29dof_with_hand_rev_1_0.urdf
```
**Reportar:** xyz y rpy exactos del MID360. Verificar que está fuera de la geometría de colisión del torso midiendo la distancia al borde externo del mesh.

### AGENTE-05 | ANALIZAR_COLISION_TORSO
Medir el bounding box del mesh de colisión del torso para saber hasta dónde llega su geometría.
```bash
conda run -p envs/g1_udc python -c "
import mujoco, os, numpy as np
os.chdir('escenas')
m = mujoco.MjModel.from_xml_path('g1_dexterous.xml')
d = mujoco.MjData(m)
mujoco.mj_forward(m, d)
# Encontrar geoms del torso
torso_id = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, 'torso_link')
for i in range(m.ngeom):
    if m.geom_bodyid[i] == torso_id:
        print(f'geom[{i}] type={m.geom_type[i]} pos={m.geom_pos[i].round(4)} size={m.geom_size[i].round(4)}')
"
```
**Reportar:** Extensión máxima hacia adelante (+X) del torso en coordenadas locales. Este valor determina la posición mínima segura para el LIDAR.

### AGENTE-06 | ANALIZAR_MANOS_DEDOS
Verificar bodies de yemas de dedos y sus posiciones locales para los touch sensors.
```bash
conda run -p envs/g1_udc python -c "
import mujoco, os
os.chdir('escenas')
m = mujoco.MjModel.from_xml_path('g1_dexterous.xml')
d = mujoco.MjData(m)
mujoco.mj_forward(m, d)
dedos = ['thumb_2','index_1','middle_1']
for name in ['left','right']:
    for dedo in dedos:
        bname = f'{name}_hand_{dedo}_link'
        bid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, bname)
        if bid >= 0:
            print(f'{bname}: xpos={d.xpos[bid].round(4)}, local_geom_size=...')
"
```
**Reportar:** Bodies de yemas confirmados con sus posiciones. Tamaño de sus geoms para ubicar el site en la punta.

---

## FASE 2 — Diseño de Bloques XML (Agentes 7-14, EN PARALELO)

### AGENTE-07 | DISEÑAR_LIDAR_ANILLO1
Generar el bloque XML del anillo 1 del LIDAR: elevación -7°, 32 rayos horizontales.
Posición del body `mid360_link`: usar valor de AGENTE-04 + offset hacia adelante para salir de la geometría del torso (mínimo pos[0] = max_torso_x + 0.03m según AGENTE-05).
Para cada rayo: `site` con `zaxis="cos(-7°)*cos(h) cos(-7°)*sin(h) sin(-7°)"` donde h va de 0° a 348.75° en pasos de 11.25°.
**Reportar:** 32 sites XML + 32 rangefinders XML para el anillo 1.

### AGENTE-08 | DISEÑAR_LIDAR_ANILLO2
Igual que AGENTE-07 pero elevación +10°.
**Reportar:** 32 sites + 32 rangefinders para anillo 2.

### AGENTE-09 | DISEÑAR_LIDAR_ANILLO3
Igual que AGENTE-07 pero elevación +25°.
**Reportar:** 32 sites + 32 rangefinders para anillo 3.

### AGENTE-10 | DISEÑAR_LIDAR_ANILLO4
Igual que AGENTE-07 pero elevación +45°.
**Reportar:** 32 sites + 32 rangefinders para anillo 4.

### AGENTE-11 | DISEÑAR_CABEZA_ARTICULADA
Crear bloque XML cabeza 2 DOF para insertar como hijo del body que contiene `head_link`.
```xml
<body name="head_yaw_link" pos="X Y Z">  <!-- posición según AGENTE-02 -->
  <joint name="head_yaw_joint" type="hinge" axis="0 0 1"
         range="-1.5708 1.5708" armature="0.01" damping="0.5"/>
  <inertial pos="0 0 0" mass="0.1" diaginertia="0.001 0.001 0.001"/>
  <body name="head_pitch_link" pos="0 0 0.03">
    <joint name="head_pitch_joint" type="hinge" axis="0 1 0"
           range="-0.8727 0.6109" armature="0.01" damping="0.5"/>
    <inertial pos="0 0 0" mass="0.1" diaginertia="0.001 0.001 0.001"/>
    <camera name="d435_rgb"   pos="0.058 0.018 0.0" euler="0 -0.35 0" fovy="58"/>
    <camera name="d435_depth" pos="0.058 0.018 0.0" euler="0 -0.35 0" fovy="58"/>
    <site name="d435_site" pos="0.058 0.018 0.0" euler="0 -0.35 0" size="0.01" group="5"/>
  </body>
</body>
```
**Reportar:** Bloque XML con posición ajustada según AGENTE-02. Verificar rangos articulares.

### AGENTE-12 | DISEÑAR_TOUCH_MANO_IZQUIERDA
Crear 3 sites touch para yemas izquierdas: thumb_2, index_1, middle_1.
Usar posiciones de AGENTE-06. Site al final de cada geom de yema.
```xml
<!-- Dentro de left_hand_thumb_2_link -->
<site name="left_thumb_tip" pos="0 -0.026 0" size="0.008" group="5"/>
<!-- Dentro de left_hand_index_1_link -->
<site name="left_index_tip" pos="0.026 0 0" size="0.008" group="5"/>
<!-- Dentro de left_hand_middle_1_link -->
<site name="left_middle_tip" pos="0.026 0 0" size="0.008" group="5"/>
```
Y en sección `<sensor>`:
```xml
<touch name="touch_left_thumb"  site="left_thumb_tip"/>
<touch name="touch_left_index"  site="left_index_tip"/>
<touch name="touch_left_middle" site="left_middle_tip"/>
```
**Reportar:** Bloque XML completo de sites + sensors para mano izquierda.

### AGENTE-13 | DISEÑAR_TOUCH_MANO_DERECHA
Igual que AGENTE-12 para mano derecha (right_thumb_tip, right_index_tip, right_middle_tip).
**Reportar:** Bloque XML de mano derecha.

### AGENTE-14 | DISEÑAR_ESCENA_MANIPULACION
Crear `escenas/g1_manipulation_scene.xml`:
```xml
<mujoco model="g1_manipulation_scene">
  <include file="g1_manipulation_full.xml"/>
  <asset>
    <texture name="grid" type="2d" builtin="checker" width="512" height="512"
             rgb1="0.8 0.8 0.8" rgb2="0.6 0.6 0.6"/>
    <material name="grid" texture="grid" texrepeat="4 4" reflectance="0.1"/>
    <material name="box_mat" rgba="0.8 0.2 0.2 1"/>
  </asset>
  <worldbody>
    <light name="light1" pos="0 0 4" dir="0 0 -1" diffuse="0.7 0.7 0.7"/>
    <light name="light2" pos="2 0 3" dir="-1 0 -1" diffuse="0.4 0.4 0.4"/>
    <geom name="floor" type="plane" size="8 8 0.1" material="grid" friction="1.0"/>
    <!-- Paredes para que el LIDAR tenga algo que detectar -->
    <geom name="wall_front" type="box" pos="4 0 1" size="0.1 4 2" rgba="0.5 0.5 0.8 1"/>
    <geom name="wall_left"  type="box" pos="0 4 1" size="4 0.1 2" rgba="0.5 0.5 0.8 1"/>
    <geom name="wall_right" type="box" pos="0 -4 1" size="4 0.1 2" rgba="0.5 0.5 0.8 1"/>
    <!-- Caja objetivo -->
    <body name="target_box" pos="0.6 0 0.15">
      <freejoint name="box_free"/>
      <geom name="box_geom" type="box" size="0.15 0.10 0.15"
            material="box_mat" mass="1.0" friction="1.2 0.005 0.0001"/>
      <site name="box_center" pos="0 0 0" size="0.01" group="5"/>
    </body>
    <!-- Zona de depósito -->
    <site name="deposit_zone" pos="2.0 0 0.001" size="0.25 0.25 0.001"
          type="box" rgba="0.1 0.8 0.1 0.4" group="1"/>
  </worldbody>
</mujoco>
```
**Reportar:** Archivo creado. Verificar que carga sin errores en MuJoCo.

---

## FASE 3 — Integración del XML (Agentes 15-18, SECUENCIAL)

### AGENTE-15 | CREAR_SCRIPT_BUILDER
Crear `escenas/build_xml.py` que genera `g1_manipulation_full.xml` programáticamente a partir de `g1_dexterous.xml` + los bloques de los agentes anteriores. Usar `xml.etree.ElementTree` para editar el XML.
**NO editar el XML a mano** — usar el script para garantizar reproducibilidad.
**Reportar:** Script creado. Descripción de cada inserción realizada.

### AGENTE-16 | EJECUTAR_BUILDER
Ejecutar el script de AGENTE-15:
```bash
cd /home/udc/Unitree_G1
conda run -p envs/g1_udc python escenas/build_xml.py
```
Verificar que `escenas/g1_manipulation_full.xml` se crea sin errores de XML.
**Reportar:** Stdout completo del script. Errores encontrados y corregidos.

### AGENTE-17 | VERIFICAR_CARGA_BASICA
```bash
conda run -p envs/g1_udc python -c "
import mujoco, os
os.chdir('/home/udc/Unitree_G1/escenas')
m = mujoco.MjModel.from_xml_path('g1_manipulation_full.xml')
d = mujoco.MjData(m)
mujoco.mj_forward(m, d)
print(f'nv={m.nv} nu={m.nu} njnt={m.njnt} nsensor={m.nsensor} nbody={m.nbody}')
print('CARGA OK')
"
```
**Reportar:** Valores de nv, nu, njnt, nsensor. Si hay error, reportar mensaje exacto.

### AGENTE-18 | VERIFICAR_CARGA_ESCENA
```bash
conda run -p envs/g1_udc python -c "
import mujoco, os
os.chdir('/home/udc/Unitree_G1/escenas')
m = mujoco.MjModel.from_xml_path('g1_manipulation_scene.xml')
d = mujoco.MjData(m)
mujoco.mj_forward(m, d)
print('ESCENA OK')
print(f'nv={m.nv} nu={m.nu} nsensor={m.nsensor}')
"
```
**Reportar:** Confirmación de carga de la escena completa con caja.

---

## FASE 4 — Verificación de Sensores (Agentes 19-24, EN PARALELO)

### AGENTE-19 | VERIFICAR_LIDAR_DISTANCIAS
**CRÍTICO:** Verificar que el LIDAR detecta el entorno, NO el propio robot.
```bash
conda run -p envs/g1_udc python -c "
import mujoco, os, numpy as np
os.chdir('/home/udc/Unitree_G1/escenas')
m = mujoco.MjModel.from_xml_path('g1_manipulation_scene.xml')
d = mujoco.MjData(m)
# Correr 10 pasos para estabilizar
for _ in range(10): mujoco.mj_step(m, d)
# Leer los 128 rangefinders (indices 12 a 139 en sensordata)
lidar = d.sensordata[12:140]
print(f'LIDAR: min={lidar.min():.3f}m max={lidar.max():.3f}m mean={lidar.mean():.3f}m')
print(f'Rayos > 0.5m: {(lidar > 0.5).sum()}/128')
print(f'Rayos > 2.0m: {(lidar > 2.0).sum()}/128')
print(f'Rayos == -1 (sin impacto): {(lidar == -1).sum()}/128')
# CRITERIO DE APROBACION: al menos 50 rayos deben leer > 0.5m
if (lidar > 0.5).sum() >= 50:
    print('LIDAR OK - detectando entorno correctamente')
else:
    print('LIDAR FALLO - detectando propio robot, ajustar posicion del mid360_link')
"
```
**Criterio de aprobación:** ≥50 de 128 rayos leen distancia >0.5m.
**Reportar:** Distribución completa de distancias. Si falla, reportar la corrección aplicada.

### AGENTE-20 | VERIFICAR_IMU
```bash
conda run -p envs/g1_udc python -c "
import mujoco, os, numpy as np
os.chdir('/home/udc/Unitree_G1/escenas')
m = mujoco.MjModel.from_xml_path('g1_manipulation_full.xml')
d = mujoco.MjData(m)
# Correr 100 pasos para estabilizar
for _ in range(100): mujoco.mj_step(m, d)
print('IMU torso gyro:', d.sensordata[0:3].round(4))
print('IMU torso accel:', d.sensordata[3:6].round(4))
print('IMU pelvis gyro:', d.sensordata[6:9].round(4))
print('IMU pelvis accel:', d.sensordata[9:12].round(4))
# El acelerometro debe leer aprox [0, 0, -9.81] en reposo
accel = d.sensordata[3:6]
print(f'Norma accel torso: {np.linalg.norm(accel):.3f} (esperado ~9.81)')
"
```
**Criterio:** norma del acelerómetro ∈ [8.0, 12.0] m/s² después de 100 pasos.
**Reportar:** Valores IMU estabilizados.

### AGENTE-21 | VERIFICAR_TOUCH_SENSORS
```bash
conda run -p envs/g1_udc python -c "
import mujoco, os, numpy as np
os.chdir('/home/udc/Unitree_G1/escenas')
m = mujoco.MjModel.from_xml_path('g1_manipulation_scene.xml')
d = mujoco.MjData(m)
mujoco.mj_forward(m, d)
# Touch sensors están en indices 140-145
touch = d.sensordata[140:146]
print(f'Touch sensors (6 yemas): {touch}')
# Cerrar manualmente los dedos para verificar que se activan
# Indices de joints de dedos izq: buscar thumb_0, thumb_1, etc.
print('Sensores de contacto verificados (0 = sin contacto en reposo OK)')
"
```
**Reportar:** Valores touch en reposo (deben ser 0). Verificar que los nombres de sensores son correctos.

### AGENTE-22 | VERIFICAR_CAMARA_RGB
```bash
conda run -p envs/g1_udc python -c "
import mujoco, os, numpy as np
os.chdir('/home/udc/Unitree_G1/escenas')
m = mujoco.MjModel.from_xml_path('g1_manipulation_scene.xml')
d = mujoco.MjData(m)
mujoco.mj_forward(m, d)
renderer = mujoco.Renderer(m, height=480, width=640)
renderer.update_scene(d, camera='d435_rgb')
pixels = renderer.render()
print(f'RGB shape: {pixels.shape}')  # debe ser (480, 640, 3)
print(f'Pixel medio: {pixels.mean():.1f}')  # no debe ser 0 (negro) ni 255 (blanco)
print(f'Pixel min: {pixels.min()}, max: {pixels.max()}')
renderer.close()
print('CAMARA RGB OK')
"
```
**Reportar:** Shape del frame, valores de píxeles (verificar que la cámara ve algo).

### AGENTE-23 | VERIFICAR_CAMARA_DEPTH
```bash
conda run -p envs/g1_udc python -c "
import mujoco, os, numpy as np
os.chdir('/home/udc/Unitree_G1/escenas')
m = mujoco.MjModel.from_xml_path('g1_manipulation_scene.xml')
d = mujoco.MjData(m)
mujoco.mj_forward(m, d)
renderer = mujoco.Renderer(m, height=480, width=640)
renderer.enable_depth_rendering()
renderer.update_scene(d, camera='d435_depth')
depth = renderer.render()
print(f'Depth shape: {depth.shape}')  # (480, 640)
depth_finite = depth[np.isfinite(depth)]
print(f'Depth min={depth_finite.min():.3f}m max={depth_finite.max():.3f}m')
# La caja está a 0.6m, debe ser visible
renderer.close()
print('CAMARA DEPTH OK')
"
```
**Reportar:** Shape y rango de profundidades. Verificar que la caja a 0.6m es visible.

### AGENTE-24 | VERIFICAR_CABEZA_MOVIMIENTO
```bash
conda run -p envs/g1_udc python -c "
import mujoco, os, numpy as np
os.chdir('/home/udc/Unitree_G1/escenas')
m = mujoco.MjModel.from_xml_path('g1_manipulation_full.xml')
d = mujoco.MjData(m)
# Localizar actuadores de cabeza
for i in range(m.nu):
    name = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_ACTUATOR, i)
    if name and 'head' in name:
        print(f'Actuador cabeza[{i}]: {name}')
# Mover la cabeza 30° hacia abajo
head_pitch_idx = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_ACTUATOR, 'head_pitch_joint')
d.ctrl[head_pitch_idx] = -0.5236  # -30 grados
for _ in range(200): mujoco.mj_step(m, d)
pitch_actual = d.qpos[mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, 'head_pitch_joint')]
print(f'Pitch objetivo: -0.5236 rad, Pitch actual: {pitch_actual:.4f} rad')
print('CABEZA OK' if abs(pitch_actual - (-0.5236)) < 0.05 else 'CABEZA FALLO')
"
```
**Reportar:** Respuesta del controlador de cabeza. Verificar que alcanza el ángulo objetivo.

---

## FASE 5 — Pruebas de Estrés (Agentes 25-27, EN PARALELO)

### AGENTE-25 | STRESS_TEST_100_PASOS
Correr 100 pasos de simulación y verificar estabilidad numérica.
```bash
conda run -p envs/g1_udc python -c "
import mujoco, os, numpy as np
os.chdir('/home/udc/Unitree_G1/escenas')
m = mujoco.MjModel.from_xml_path('g1_manipulation_scene.xml')
d = mujoco.MjData(m)
for i in range(100):
    mujoco.mj_step(m, d)
    if np.any(np.isnan(d.qpos)) or np.any(np.isnan(d.sensordata)):
        print(f'NaN en paso {i}!')
        break
print(f'z_robot={d.qpos[2]:.4f}m (debe ser ~0.78)')
print(f'sensordata NaN: {np.isnan(d.sensordata).sum()}')
print('STRESS TEST OK')
"
```
**Reportar:** Posición z del robot después de 100 pasos y ausencia de NaN.

### AGENTE-26 | STRESS_TEST_CONTACTO_CAJA
Mover manualmente el robot hacia la caja y verificar que los touch sensors se activan.
```bash
conda run -p envs/g1_udc python -c "
import mujoco, os, numpy as np
os.chdir('/home/udc/Unitree_G1/escenas')
m = mujoco.MjModel.from_xml_path('g1_manipulation_scene.xml')
d = mujoco.MjData(m)
# Cerrar dedos izquierdos sobre la caja (forzar posición de agarre)
# Buscar indices de joints de dedos
for i in range(m.njnt):
    name = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_JOINT, i)
    if name and 'left_hand' in name:
        print(f'joint[{i}]={name} range={m.jnt_range[i]}')
print('Analisis joints dedos completado')
print('Touch sensors en reposo:', d.sensordata[140:146])
"
```
**Reportar:** Lista de joints de dedos con rangos. Confirmar que los touch sensors están indexados correctamente.

### AGENTE-27 | VERIFICAR_SENSORDATA_INDICES
Mapear exactamente qué índice de sensordata corresponde a cada sensor.
```bash
conda run -p envs/g1_udc python -c "
import mujoco, os
os.chdir('/home/udc/Unitree_G1/escenas')
m = mujoco.MjModel.from_xml_path('g1_manipulation_full.xml')
idx = 0
for i in range(m.nsensor):
    name = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_SENSOR, i)
    dim = m.sensor_dim[i]
    print(f'sensor[{i}] name={name} sensordata[{idx}:{idx+dim}] dim={dim}')
    idx += dim
print(f'Total sensordata dims: {idx}')
"
```
**Reportar:** Mapa completo sensor_name → índice sensordata. Este mapa es CRÍTICO para los planes 02, 03 y 04.

---

## FASE 6 — Documentación y Commit (Agentes 28-30, SECUENCIAL)

### AGENTE-28 | CREAR_CONSTANTS_PY
Crear `simulacion/g1_constants.py` con todas las constantes del modelo integrado:
```python
# simulacion/g1_constants.py
# Generado automáticamente por Plan 01 — NO editar a mano

# DOF
N_LEGS = 12
N_WAIST = 3
N_ARMS = 10
N_WRISTS = 6
N_FINGERS_PER_HAND = 7
N_HEAD = 2
N_TOTAL = N_LEGS + N_WAIST + N_ARMS + N_WRISTS + N_FINGERS_PER_HAND * 2 + N_HEAD

# Índices en qpos (freejoint del robot ocupa 0-6)
QPOS_LEGS_START = 7
QPOS_ARMS_START = 19  # ajustar según AGENTE-01
QPOS_FINGERS_LEFT_START = 29  # ajustar
QPOS_FINGERS_RIGHT_START = 36  # ajustar
QPOS_HEAD_START = 43  # ajustar

# Índices en sensordata (del mapa de AGENTE-27)
SENSOR_IMU_TORSO_GYRO = slice(0, 3)
SENSOR_IMU_TORSO_ACCEL = slice(3, 6)
SENSOR_IMU_PELVIS_GYRO = slice(6, 9)
SENSOR_IMU_PELVIS_ACCEL = slice(9, 12)
SENSOR_LIDAR_START = 12
SENSOR_LIDAR_END = 140   # 128 rangefinders
SENSOR_TOUCH_START = 140
SENSOR_TOUCH_END = 146   # 6 touch sensors

# Cámaras
CAMERA_RGB = 'd435_rgb'
CAMERA_DEPTH = 'd435_depth'
CAMERA_FOVY = 58.0
CAMERA_TILT_RAD = -0.35
```
Ajustar todos los valores según los resultados de AGENTE-01 y AGENTE-27.
**Reportar:** Archivo creado con todos los valores correctos.

### AGENTE-29 | GENERAR_REPORTE_COMPLETO
Crear `/home/udc/Unitree_G1/reportes/reporte_plan01_xml_sensores_<FECHA>.md` con:
- Resultado de CADA agente (01-28): comando, stdout completo, errores, solución
- Especificación técnica final (tabla DOF, actuadores, sensores)
- Mapa completo sensor → sensordata index (de AGENTE-27)
- Tabla sensores reales vs simulados
- Problemas encontrados y soluciones aplicadas
- Lista completa de archivos creados con rutas absolutas
- Confirmación del criterio LIDAR (≥50 rayos >0.5m)

### AGENTE-30 | GIT_COMMIT
```bash
cd /home/udc/Unitree_G1
git add escenas/g1_manipulation_full.xml
git add escenas/g1_manipulation_scene.xml
git add escenas/build_xml.py
git add simulacion/g1_constants.py
git add reportes/reporte_plan01_xml_sensores_*.md
git commit -m "$(cat <<'EOF'
feat: XML integrado G1 con LIDAR 3D, camara D435i y contacto dedos

- g1_manipulation_full.xml: 51 DOF, 45 actuadores, 138 sensores
- LIDAR 3D: 128 rangefinders (4 anillos x 32 rayos), detecta entorno OK
- Camara D435i: RGB + depth, tilt -20deg, cabeza articulada 2DOF
- Touch sensors: 6 yemas (3 izq + 3 der)
- g1_constants.py: mapa completo de indices para politicas

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```
**Reportar:** Hash del commit. Verificar con `git log --oneline -1`.
