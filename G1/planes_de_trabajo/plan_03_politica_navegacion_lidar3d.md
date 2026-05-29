# Plan de Trabajo 03 — Política de Navegación con LIDAR 3D
**Proyecto:** Unitree G1 — Universidad de Colombia  
**Fecha:** 2026-05-14  
**Sub-agentes asignados:** 30  
**Prerequerido:** Plan 01 completado (`escenas/g1_manipulation_full.xml`, `simulacion/g1_constants.py`)  
**Nota:** Este plan puede ejecutarse EN PARALELO con el Plan 02  
**Reporte de salida:** `reportes/reporte_plan03_navegacion_<FECHA>.md`

---

## Contexto del Proyecto

La política de navegación recibe datos del LIDAR LIVOX MID360 (simulado como 128 rangefinders en 4 anillos) y genera comandos de velocidad (vx, vy, wz) que se pasan a la política de locomoción DR existente (`politicas/model_DR_jit.pt`, CONGELADA). El objetivo es que el robot camine desde su posición hasta la caja y luego desde la caja hasta la zona de depósito.

### Arquitectura de navegación:
```
LIDAR 3D (128 valores) ──┐
Posición objetivo rel (2)──┤──► Política Navegación ──► [vx, vy, wz]
Distancia al objetivo (1)──┤                                   │
Yaw error (1) ─────────────┤                                   │
Velocidad actual (3) ───────┘                                   ▼
                                                    Política Locomoción DR
                                                    (model_DR_jit.pt, CONGELADA)
                                                                   │
                                                                   ▼
                                                           12 acciones de piernas
```

### Espacio de observación (135 dims):
```
obs_nav = [
  lidar_anillo1 (32),    # -7° elevación, normalizados [0,1]
  lidar_anillo2 (32),    # +10° elevación
  lidar_anillo3 (32),    # +25° elevación
  lidar_anillo4 (32),    # +45° elevación
  pos_objetivo_rel (2),  # (dx, dy) al objetivo en frame del robot
  dist_objetivo (1),     # distancia euclidiana al objetivo
  yaw_error (1),         # error de orientación hacia el objetivo
  vel_actual (3),        # vx, vy, wz actuales del robot
]
# Total: 128 + 2 + 1 + 1 + 3 = 135 dims
```

### Espacio de acción (3 dims):
```
accion_nav = [vx, vy, wz]  # normalizados [-1, 1]
# Escala: vx ∈ [-0.3, 1.0] m/s, vy ∈ [-0.3, 0.3] m/s, wz ∈ [-1.0, 1.0] rad/s
```

---

## FASE 1 — Análisis del LIDAR y Entorno (Agentes 1-4, EN PARALELO)

### AGENTE-01 | ANALIZAR_RANGEFINDERS_XML
**Tarea:** Extraer y documentar todos los 128 rangefinders del XML del Plan 01:
```bash
cd /home/udc/Unitree_G1
conda run -p envs/g1_udc python -c "
import mujoco, numpy as np
m = mujoco.MjModel.from_xml_path('escenas/g1_manipulation_full.xml')
d = mujoco.MjData(m)
mujoco.mj_resetDataKeyframe(m, d, 0)
mujoco.mj_forward(m, d)

print('=== SENSORES RANGEFINDER ===')
rang_sensors = []
for i in range(m.nsensor):
    name = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_SENSOR, i)
    if name and 'lidar' in name.lower():
        rang_sensors.append((i, name))
        
print(f'Total rangefinders encontrados: {len(rang_sensors)}')
print()
# Mostrar primeros 8 de cada anillo
for ring in range(4):
    anillo_sensors = [(i,n) for i,n in rang_sensors if f'ring{ring+1}' in n or f'ring_{ring+1}' in n or f'anillo{ring+1}' in n]
    print(f'Anillo {ring+1}: {len(anillo_sensors)} sensores')
    for s_id, s_name in anillo_sensors[:3]:
        adr = m.sensor_adr[s_id]
        print(f'  sensor[{s_id}] adr={adr} {s_name}: val={d.sensordata[adr]:.3f}m')

print()
# Índices sensordata para los 128 rangefinders
rang_adrs = [m.sensor_adr[i] for i,_ in rang_sensors]
print(f'Índices sensordata rangefinders: [{rang_adrs[0]}..{rang_adrs[-1]}]')
print(f'sensordata shape: {d.sensordata.shape}')
"
```
**Reportar:** Número exacto de rangefinders encontrados. Índices sensordata para los 4 anillos (array de 128 valores). Si no hay 128, reportar cuántos hay y sus nombres. Verificar que coincide con `g1_constants.py`.

---

### AGENTE-02 | ANALIZAR_DIMENSIONES_ESPACIO_LIBRE
**Tarea:** Verificar las dimensiones del espacio libre en la escena de navegación:
```bash
cd /home/udc/Unitree_G1
conda run -p envs/g1_udc python -c "
import mujoco, numpy as np
m = mujoco.MjModel.from_xml_path('escenas/g1_manipulation_scene.xml')
d = mujoco.MjData(m)
mujoco.mj_resetDataKeyframe(m, d, 0)
mujoco.mj_forward(m, d)

print('=== GEOMETRIAS EN LA ESCENA ===')
for i in range(m.ngeom):
    name = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_GEOM, i)
    gtype = m.geom_type[i]
    pos = m.geom_pos[i]
    size = m.geom_size[i]
    print(f'  geom[{i}] {name}: type={gtype} pos={pos} size={size}')

print()
print('=== CUERPOS LIBRES (box, deposito) ===')
for i in range(m.nbody):
    name = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_BODY, i)
    if name and ('box' in name.lower() or 'deposit' in name.lower() or 'zona' in name.lower()):
        print(f'  body[{i}] {name}: pos={d.xpos[i]}')
"
```
**Reportar:** Posición de la caja, posición de la zona de depósito, dimensiones del área libre de navegación (suelo). Verificar que hay espacio suficiente para navegar (>3m entre robot y depósito).

---

### AGENTE-03 | IMPLEMENTAR_LIDAR_PREPROCESSING
**Tarea:** Implementar `entrenamiento/utils/lidar_preprocessing.py` completo con normalización, filtro y conversión real→sim:
```bash
mkdir -p /home/udc/Unitree_G1/entrenamiento/utils
cat > /home/udc/Unitree_G1/entrenamiento/utils/lidar_preprocessing.py << 'PYEOF'
"""
Preprocesamiento del LIDAR LIVOX MID360 para la política de navegación G1.

Funciones:
  sim_lidar_to_obs(sensordata, lidar_indices)  — sim → obs (128,) normalizado
  livox_to_sim_format(pointcloud)             — nube real → (128,) igual que sim
  apply_median_filter(lidar_arr, ring_size)   — filtro por anillo
"""
import numpy as np

# Parámetros del LIDAR simulado (4 anillos × 32 rayos)
N_RINGS = 4
N_RAYS_PER_RING = 32
N_TOTAL = N_RINGS * N_RAYS_PER_RING  # 128
MAX_RANGE = 20.0  # metros (cutoff del rangefinder)

# Ángulos de elevación de los 4 anillos (grados)
RING_ELEVATIONS_DEG = [-7.0, 10.0, 25.0, 45.0]

# Ángulos azimutales: 0° a 348.75°, paso 11.25°
AZIMUTHS_DEG = np.arange(0, 360, 360.0 / N_RAYS_PER_RING)


def sim_lidar_to_obs(sensordata: np.ndarray, lidar_start_idx: int) -> np.ndarray:
    """
    Convierte los datos crudos de los 128 rangefinders de MuJoCo a obs normalizado.
    
    Args:
        sensordata: array completo de sensordata (shape variable)
        lidar_start_idx: índice donde empiezan los 128 rangefinders (de g1_constants.py)
    
    Returns:
        lidar_obs: array (128,) con valores en [0, 1]
                   0 = obstruido (objeto a 0m), 1 = libre (a MAX_RANGE o más)
    """
    raw = sensordata[lidar_start_idx : lidar_start_idx + N_TOTAL].copy()
    # -1 significa sin impacto (libre) → usar MAX_RANGE
    raw[raw < 0] = MAX_RANGE
    # Clip y normalizar
    clipped = np.clip(raw, 0.0, MAX_RANGE)
    normalized = clipped / MAX_RANGE
    # Filtro de mediana por anillo (ventana 3)
    filtered = apply_median_filter(normalized, N_RAYS_PER_RING)
    return filtered.astype(np.float32)


def apply_median_filter(lidar_arr: np.ndarray, ring_size: int) -> np.ndarray:
    """Aplica filtro de mediana con ventana 3 a cada anillo."""
    result = lidar_arr.copy()
    n_rings = len(lidar_arr) // ring_size
    for r in range(n_rings):
        start = r * ring_size
        end = start + ring_size
        ring = lidar_arr[start:end]
        # Ventana circular de tamaño 3
        for i in range(ring_size):
            prev_i = (i - 1) % ring_size
            next_i = (i + 1) % ring_size
            result[start + i] = np.median([ring[prev_i], ring[i], ring[next_i]])
    return result


def add_training_noise(lidar_obs: np.ndarray, sigma: float = 0.02) -> np.ndarray:
    """Añade ruido gaussiano durante entrenamiento (Domain Randomization)."""
    noise = np.random.normal(0, sigma / MAX_RANGE, lidar_obs.shape)
    return np.clip(lidar_obs + noise, 0.0, 1.0).astype(np.float32)


def livox_to_sim_format(
    pointcloud: np.ndarray,
    n_rings: int = N_RINGS,
    n_rays: int = N_RAYS_PER_RING,
    elevation_tol_deg: float = 5.0,
) -> np.ndarray:
    """
    Convierte nube de puntos del LIVOX MID360 real al formato de 128 valores
    compatible con la política entrenada en simulación.
    
    Args:
        pointcloud: array (N, 3) con puntos XYZ del LIVOX (frame del sensor)
        n_rings: número de anillos (default 4)
        n_rays: número de rayos por anillo (default 32)
        elevation_tol_deg: tolerancia ±grados para asignar punto a anillo
    
    Returns:
        lidar_128: array (128,) normalizado [0, 1], mismo formato que sim_lidar_to_obs()
    """
    if pointcloud is None or len(pointcloud) == 0:
        return np.ones(n_rings * n_rays, dtype=np.float32)  # todo libre
    
    result = np.full(n_rings * n_rays, MAX_RANGE, dtype=np.float32)
    
    # Calcular elevación y azimut de cada punto
    x, y, z = pointcloud[:, 0], pointcloud[:, 1], pointcloud[:, 2]
    dist_horiz = np.sqrt(x**2 + y**2)
    dist_total = np.sqrt(x**2 + y**2 + z**2)
    
    elev_deg = np.degrees(np.arctan2(z, dist_horiz))    # ángulo de elevación
    azim_deg = np.degrees(np.arctan2(y, x)) % 360.0     # azimut 0-360°
    
    for r_idx, target_elev in enumerate(RING_ELEVATIONS_DEG):
        # Puntos dentro de la tolerancia de elevación
        mask = np.abs(elev_deg - target_elev) <= elevation_tol_deg
        if not np.any(mask):
            continue
        
        elev_pts_dist = dist_total[mask]
        elev_pts_azim = azim_deg[mask]
        
        for ray_idx, target_azim in enumerate(np.arange(0, 360, 360.0 / n_rays)):
            azim_diffs = np.abs(((elev_pts_azim - target_azim + 180) % 360) - 180)
            sector_mask = azim_diffs <= (180.0 / n_rays)
            if np.any(sector_mask):
                min_dist = np.min(elev_pts_dist[sector_mask])
                result[r_idx * n_rays + ray_idx] = min_dist
    
    # Normalizar igual que en simulación
    clipped = np.clip(result, 0.0, MAX_RANGE)
    return (clipped / MAX_RANGE).astype(np.float32)


if __name__ == '__main__':
    # Test con datos sintéticos
    print("=== TEST lidar_preprocessing.py ===")
    
    # Test 1: sim_lidar_to_obs
    fake_sensordata = np.full(150, -1.0)  # todos sin impacto
    fake_sensordata[12:140] = 5.0  # distancias de 5m (índice 12 = start típico)
    obs = sim_lidar_to_obs(fake_sensordata, lidar_start_idx=12)
    assert obs.shape == (128,), f"shape incorrecto: {obs.shape}"
    assert obs.min() >= 0.0 and obs.max() <= 1.0, f"rango incorrecto: [{obs.min()}, {obs.max()}]"
    print(f"Test 1 sim_lidar_to_obs: shape={obs.shape}, range=[{obs.min():.3f},{obs.max():.3f}] OK")
    
    # Test 2: add_training_noise
    noisy = add_training_noise(obs, sigma=0.02)
    assert noisy.shape == (128,), f"noise shape incorrecto: {noisy.shape}"
    print(f"Test 2 add_training_noise: shape={noisy.shape} OK")
    
    # Test 3: livox_to_sim_format con nube sintética
    N = 500
    theta = np.random.uniform(0, 2*np.pi, N)
    phi = np.random.uniform(-0.2, 0.8, N)
    r = np.random.uniform(1.0, 10.0, N)
    pts = np.stack([r*np.cos(phi)*np.cos(theta), r*np.cos(phi)*np.sin(theta), r*np.sin(phi)], axis=1)
    lidar_real = livox_to_sim_format(pts)
    assert lidar_real.shape == (128,), f"livox shape incorrecto: {lidar_real.shape}"
    print(f"Test 3 livox_to_sim_format: shape={lidar_real.shape}, range=[{lidar_real.min():.3f},{lidar_real.max():.3f}] OK")
    
    print()
    print("TODOS LOS TESTS PASARON")
PYEOF
conda run -p envs/g1_udc python entrenamiento/utils/lidar_preprocessing.py
```
**Reportar:** Stdout completo del test. Verificar que output shape es (128,) y range es [0,1].

---

### AGENTE-04 | VERIFICAR_OBS_NAV_135_DIMS
**Tarea:** Calcular y verificar que el obs_nav tiene exactamente 135 dims:
```bash
cd /home/udc/Unitree_G1
conda run -p envs/g1_udc python -c "
import numpy as np

# obs_nav composition
dims = {
    'lidar_ring1': 32,    # anillo -7°
    'lidar_ring2': 32,    # anillo +10°
    'lidar_ring3': 32,    # anillo +25°
    'lidar_ring4': 32,    # anillo +45°
    'pos_objetivo_rel_dx': 1,  # dx en frame robot
    'pos_objetivo_rel_dy': 1,  # dy en frame robot
    'dist_objetivo': 1,
    'yaw_error': 1,
    'vel_vx': 1,
    'vel_vy': 1,
    'vel_wz': 1,
}
total = sum(dims.values())
print('=== OBS NAV DIMS ===')
for k, v in dims.items():
    print(f'  {k:30s}: {v}')
print(f'  TOTAL: {total}')
assert total == 135, f'ERROR: total={total}, esperado 135'
print('TOTAL = 135 OK')
"
```
**Reportar:** Tabla de dimensiones confirmada. Si el total no es 135, proponer corrección.

---

## FASE 2 — Implementación de Entornos y Scripts (Agentes 5-11, EN PARALELO)

### AGENTE-05 | IMPLEMENTAR_G1NAVENV
**Tarea:** Implementar `entrenamiento/envs/g1_nav_env.py` con el entorno de navegación:
```bash
mkdir -p /home/udc/Unitree_G1/entrenamiento/envs
```
La clase `G1NavEnv` debe implementar:
- `__init__(self, xml_path, mode='nav_to_box')` — modos: 'nav_to_box' o 'nav_to_deposit'
- `reset(self)` → posición robot aleatoria, objetivo aleatorio dentro del área
- `step(self, action)` → aplicar [vx, vy, wz] al robot (via locomoción DR), avanzar sim
- `compute_reward(self, data)`:
  - `r_progress = (dist_prev - dist_curr) * 10.0` — acercarse al objetivo
  - `r_heading = -abs(yaw_error) * 0.5` — orientarse hacia objetivo
  - `r_obstacle = sum(max(0, 1.0 - lidar_min/0.5)) * (-2.0)` — penalizar si rayo LIDAR < 0.5m
  - `r_arrival = +50.0` si dist < 0.3m (éxito)
  - `r_timeout = -20.0` si > 200 pasos
  - `r_collision = -100.0` si algún rayo LIDAR < 0.15m
- `_get_obs(self, data)` → construir vector de 135 dims
- `_get_robot_yaw(self, data)` → yaw actual del robot
- `_compute_yaw_error(self, robot_pos, robot_yaw, objetivo_pos)` → error de orientación

**Test de verificación:**
```bash
conda run -p envs/g1_udc python -c "
import sys; sys.path.insert(0, '.')
from entrenamiento.envs.g1_nav_env import G1NavEnv
env = G1NavEnv('escenas/g1_manipulation_scene.xml')
obs = env.reset()
print(f'reset obs shape: {obs.shape}')
assert obs.shape == (135,), f'ERROR: {obs.shape}'
for _ in range(5):
    obs, r, done, info = env.step([0.0, 0.0, 0.0])
print(f'step obs shape: {obs.shape}, reward: {r:.3f}')
print('G1NavEnv OK')
"
```
**Reportar:** Archivo creado, test OK, stdout completo.

---

### AGENTE-06 | CREAR_ESCENA_NAV_EMPTY
**Tarea:** Crear `escenas/nav_scenes/scene_nav_empty.xml` — escena sin obstáculos:
```bash
mkdir -p /home/udc/Unitree_G1/escenas/nav_scenes
cat > /home/udc/Unitree_G1/escenas/nav_scenes/scene_nav_empty.xml << 'EOF'
<?xml version="1.0" encoding="utf-8"?>
<mujoco model="g1_nav_empty">
  <include file="../g1_manipulation_full.xml"/>
  
  <worldbody>
    <!-- Suelo grande para navegación -->
    <geom name="floor" type="plane" size="10 10 0.1" pos="0 0 0"
          rgba="0.7 0.7 0.7 1" contype="1" conaffinity="1" friction="1.0 0.005 0.0001"/>
    
    <!-- Iluminación -->
    <light name="main_light" pos="0 0 5" dir="0 0 -1" diffuse="1 1 1"/>
    
    <!-- Caja objetivo (freejoint para que sea móvil) -->
    <body name="target_box" pos="1.5 0 0.15">
      <freejoint name="box_free"/>
      <geom name="box_geom" type="box" size="0.15 0.10 0.15"
            mass="1.0" rgba="0.9 0.3 0.2 1" friction="1.5 0.005 0.001"
            contype="1" conaffinity="1"/>
    </body>
    
    <!-- Zona de depósito (visual, sin física) -->
    <body name="deposit_zone" pos="3.0 0 0.005">
      <geom name="deposit_geom" type="box" size="0.5 0.5 0.005"
            rgba="0.2 0.9 0.2 0.3" contype="0" conaffinity="0"/>
    </body>
  </worldbody>
</mujoco>
EOF
# Verificar que carga
conda run -p /home/udc/Unitree_G1/envs/g1_udc python -c "
import mujoco
m = mujoco.MjModel.from_xml_path('/home/udc/Unitree_G1/escenas/nav_scenes/scene_nav_empty.xml')
print(f'scene_nav_empty.xml OK: nbody={m.nbody}, ngeom={m.ngeom}')
"
```
**Reportar:** Archivo creado, carga sin errores. Dimensiones y posiciones de caja y depósito.

---

### AGENTE-07 | CREAR_ESCENAS_NAV_1WALL_2WALLS
**Tarea:** Crear `escenas/nav_scenes/scene_nav_1wall.xml` y `scene_nav_2walls.xml`:
```bash
# scene_nav_1wall.xml: una pared lateral a 1m del robot
cat > /home/udc/Unitree_G1/escenas/nav_scenes/scene_nav_1wall.xml << 'EOF'
<?xml version="1.0" encoding="utf-8"?>
<mujoco model="g1_nav_1wall">
  <include file="../g1_manipulation_full.xml"/>
  <worldbody>
    <geom name="floor" type="plane" size="10 10 0.1" pos="0 0 0" rgba="0.7 0.7 0.7 1"/>
    <light name="main_light" pos="0 0 5" dir="0 0 -1" diffuse="1 1 1"/>
    
    <!-- Pared lateral derecha -->
    <geom name="wall_right" type="box" size="3.0 0.1 1.0" pos="1.5 -1.0 1.0"
          rgba="0.5 0.5 0.9 1" contype="1" conaffinity="1"/>
    
    <body name="target_box" pos="1.5 0 0.15">
      <freejoint name="box_free"/>
      <geom name="box_geom" type="box" size="0.15 0.10 0.15" mass="1.0"
            rgba="0.9 0.3 0.2 1" friction="1.5 0.005 0.001"/>
    </body>
    <body name="deposit_zone" pos="3.0 0 0.005">
      <geom name="deposit_geom" type="box" size="0.5 0.5 0.005" rgba="0.2 0.9 0.2 0.3"
            contype="0" conaffinity="0"/>
    </body>
  </worldbody>
</mujoco>
EOF

# scene_nav_2walls.xml: dos paredes, robot debe rodear
cat > /home/udc/Unitree_G1/escenas/nav_scenes/scene_nav_2walls.xml << 'EOF'
<?xml version="1.0" encoding="utf-8"?>
<mujoco model="g1_nav_2walls">
  <include file="../g1_manipulation_full.xml"/>
  <worldbody>
    <geom name="floor" type="plane" size="10 10 0.1" pos="0 0 0" rgba="0.7 0.7 0.7 1"/>
    <light name="main_light" pos="0 0 5" dir="0 0 -1" diffuse="1 1 1"/>
    
    <!-- Pared derecha -->
    <geom name="wall_right" type="box" size="2.0 0.1 1.0" pos="1.0 -0.8 1.0"
          rgba="0.5 0.5 0.9 1" contype="1" conaffinity="1"/>
    <!-- Pared izquierda desplazada -->
    <geom name="wall_left" type="box" size="1.5 0.1 1.0" pos="2.0 0.8 1.0"
          rgba="0.9 0.5 0.2 1" contype="1" conaffinity="1"/>
    
    <body name="target_box" pos="2.0 0 0.15">
      <freejoint name="box_free"/>
      <geom name="box_geom" type="box" size="0.15 0.10 0.15" mass="1.0"
            rgba="0.9 0.3 0.2 1" friction="1.5 0.005 0.001"/>
    </body>
    <body name="deposit_zone" pos="3.5 0 0.005">
      <geom name="deposit_geom" type="box" size="0.5 0.5 0.005" rgba="0.2 0.9 0.2 0.3"
            contype="0" conaffinity="0"/>
    </body>
  </worldbody>
</mujoco>
EOF

# Verificar ambas
for f in scene_nav_1wall.xml scene_nav_2walls.xml; do
  conda run -p /home/udc/Unitree_G1/envs/g1_udc python -c "
import mujoco
m = mujoco.MjModel.from_xml_path('/home/udc/Unitree_G1/escenas/nav_scenes/$f')
print(f'$f OK: nbody={m.nbody}, ngeom={m.ngeom}')
"
done
```
**Reportar:** Ambos archivos creados y verificados que cargan sin errores.

---

### AGENTE-08 | CREAR_ESCENAS_NAV_FURNITURE_FULL
**Tarea:** Crear `scene_nav_furniture.xml` y `scene_nav_full.xml`:
```bash
# scene_nav_furniture.xml: mesas y sillas tipo oficina
cat > /home/udc/Unitree_G1/escenas/nav_scenes/scene_nav_furniture.xml << 'EOF'
<?xml version="1.0" encoding="utf-8"?>
<mujoco model="g1_nav_furniture">
  <include file="../g1_manipulation_full.xml"/>
  <worldbody>
    <geom name="floor" type="plane" size="10 10 0.1" pos="0 0 0" rgba="0.7 0.7 0.7 1"/>
    <light name="main_light" pos="0 0 5" dir="0 0 -1" diffuse="1 1 1"/>
    
    <!-- Mesa 1 -->
    <body name="table1" pos="1.5 0.8 0.38">
      <geom type="box" size="0.6 0.3 0.38" rgba="0.6 0.4 0.2 1" contype="1" conaffinity="1"/>
    </body>
    <!-- Mesa 2 -->
    <body name="table2" pos="2.5 -0.9 0.38">
      <geom type="box" size="0.6 0.3 0.38" rgba="0.6 0.4 0.2 1" contype="1" conaffinity="1"/>
    </body>
    <!-- Silla 1 -->
    <body name="chair1" pos="1.0 -0.6 0.22">
      <geom type="box" size="0.2 0.2 0.22" rgba="0.4 0.4 0.8 1" contype="1" conaffinity="1"/>
    </body>
    <!-- Silla 2 -->
    <body name="chair2" pos="2.0 0.5 0.22">
      <geom type="box" size="0.2 0.2 0.22" rgba="0.4 0.4 0.8 1" contype="1" conaffinity="1"/>
    </body>
    <!-- Columna central -->
    <body name="column" pos="1.8 0.0 0.75">
      <geom type="cylinder" size="0.1 0.75" rgba="0.7 0.7 0.7 1" contype="1" conaffinity="1"/>
    </body>
    
    <body name="target_box" pos="2.5 0 0.15">
      <freejoint name="box_free"/>
      <geom type="box" size="0.15 0.10 0.15" mass="1.0" rgba="0.9 0.3 0.2 1" friction="1.5 0.005 0.001"/>
    </body>
    <body name="deposit_zone" pos="4.0 0 0.005">
      <geom type="box" size="0.5 0.5 0.005" rgba="0.2 0.9 0.2 0.3" contype="0" conaffinity="0"/>
    </body>
  </worldbody>
</mujoco>
EOF

# scene_nav_full.xml: entorno completo con todos los obstáculos
# Igual que furniture pero con paredes adicionales y caja en posición difícil
cp /home/udc/Unitree_G1/escenas/nav_scenes/scene_nav_furniture.xml \
   /home/udc/Unitree_G1/escenas/nav_scenes/scene_nav_full.xml
# Modificar para añadir paredes perimetrales
# (ajustar el XML manualmente para añadir 4 paredes de perímetro)

# Verificar
for f in scene_nav_furniture.xml scene_nav_full.xml; do
  conda run -p /home/udc/Unitree_G1/envs/g1_udc python -c "
import mujoco
m = mujoco.MjModel.from_xml_path('/home/udc/Unitree_G1/escenas/nav_scenes/$f')
print(f'$f OK: nbody={m.nbody}, ngeom={m.ngeom}')
"
done
```
**Reportar:** Archivos creados y verificados. Lista de obstáculos en cada escena con posiciones.

---

### AGENTE-09 | IMPLEMENTAR_TRAIN_NAVIGATION
**Tarea:** Implementar `entrenamiento/train_navigation.py`:
```bash
# El script debe:
# --config: yaml de política de navegación
# --scene: ruta al XML de la escena
# --max_iter: número máximo de iteraciones
# --log_dir: directorio de logs
# --resume: checkpoint para continuar (opcional)
# --mode: 'nav_to_box' o 'nav_to_deposit' (default nav_to_box)
```
**Verificar:**
```bash
conda run -n hgen python -m py_compile entrenamiento/train_navigation.py && echo "OK"
```
**Reportar:** Archivo creado, test de importación OK.

---

### AGENTE-10 | CREAR_NAV_POLICY_YAML
**Tarea:** Crear `entrenamiento/configs/nav_policy.yaml`:
```bash
cat > /home/udc/Unitree_G1/entrenamiento/configs/nav_policy.yaml << 'EOF'
# Política de navegación G1 con LIDAR 3D

obs:
  lidar: 128           # 4 anillos × 32 rayos, normalizados [0,1]
  pos_objetivo_rel: 2  # dx, dy en frame robot
  dist_objetivo: 1
  yaw_error: 1
  vel_actual: 3        # vx, vy, wz del robot
  total: 135

actor:
  input_dim: 135
  hidden_dims: [256, 256, 128]
  activation: elu
  output_dim: 3         # [vx, vy, wz] normalizados [-1, 1]
  output_activation: tanh

critic:
  input_dim: 135
  hidden_dims: [256, 256, 128]
  activation: elu
  output_dim: 1

action_scale:
  vx: 1.0    # m/s ([-0.3, 1.0] con asimetría: bias hacia adelante)
  vy: 0.3    # m/s
  wz: 1.0    # rad/s

ppo:
  num_envs: 4096
  num_steps: 32
  learning_rate: 3.0e-4
  entropy_coef: 0.005
  clip_range: 0.2
  gamma: 0.99
  gae_lambda: 0.95
  max_grad_norm: 0.5
  num_epochs: 5
  minibatch_size: 1024
  total_iterations: 50000
  save_interval: 2000
  log_interval: 200

episode:
  max_steps: 200
  success_dist_threshold: 0.30  # metros
  collision_threshold: 0.15     # metros (rayo LIDAR < 15cm = colisión)
  safety_dist: 0.50             # metros (penalizar si < 50cm de obstáculo)

domain_randomization:
  lidar_noise_std: 0.02     # σ en metros (normalizado: 0.02/20=0.001)
  vel_noise_std: 0.05       # ruido en velocidad percibida
  pos_noise_std: 0.02       # ruido en posición del objetivo
  yaw_noise_std: 0.01       # ruido en orientación

export:
  output_path: "politicas/model_nav_jit.pt"
  input_dim: 135
  output_dim: 3
EOF
echo "NAV_POLICY YAML CREADO"
```
**Reportar:** Archivo creado. Justificación de los hiperparámetros PPO para navegación.

---

### AGENTE-11 | IMPLEMENTAR_SIM_NAV_SCRIPTS
**Tarea:** Crear `simulacion/sim_nav.py` y `simulacion/sim_nav_loco_integrated.py` para validación:
```bash
# sim_nav.py: valida solo la política de navegación (sin locomoción DR)
#   conda run -p envs/g1_udc python simulacion/sim_nav.py \
#     --policy politicas/model_nav_jit.pt --headless --episodes 30

# sim_nav_loco_integrated.py: valida nav + locomoción DR integradas
#   conda run -p envs/g1_udc python simulacion/sim_nav_loco_integrated.py \
#     --nav_policy politicas/model_nav_jit.pt \
#     --loco_policy politicas/model_DR_jit.pt \
#     --headless --episodes 10
```
**Test de sintaxis:**
```bash
conda run -p envs/g1_udc python -m py_compile simulacion/sim_nav.py && echo "OK"
conda run -p envs/g1_udc python -m py_compile simulacion/sim_nav_loco_integrated.py && echo "OK"
```
**Reportar:** Ambos archivos creados y sintaxis OK.

---

## FASE 3 — Entrenamiento Curriculum (Agentes 12-19, SECUENCIAL)

### AGENTE-12 | ENTRENAR_STAGE1_CAMPO_LIBRE_0_10000
**Tarea:** Stage 1 — Aprender a navegar al objetivo en campo libre (0-10000 iter):
```bash
cd /home/udc/Unitree_G1
conda run -n hgen python entrenamiento/train_navigation.py \
  --config entrenamiento/configs/nav_policy.yaml \
  --scene escenas/nav_scenes/scene_nav_empty.xml \
  --max_iter 10000 \
  --log_dir entrenamiento/logs/nav/stage1
```
**Ejecutar SOLO cuando Agentes 05-11 hayan completado con éxito.**  
**Reportar:** Reward cada 1000 iter (tabla). Tasa de llegada al objetivo a las 10000 iter.

---

### AGENTE-13 | ANALIZAR_STAGE1_NAVEGACION
**Tarea:** Analizar convergencia del Stage 1 y validar en MuJoCo (10 episodios headless):
```bash
cd /home/udc/Unitree_G1
conda run -p envs/g1_udc python simulacion/sim_nav.py \
  --policy entrenamiento/logs/nav/stage1/model_10000.pt \
  --headless --episodes 10
```
**Criterio Stage 1:** Tasa de llegada > 70% en campo libre.  
**Reportar:** Tabla de 10 episodios: ¿llegó? tiempo, distancia recorrida. Veredicto.

---

### AGENTE-14 | ENTRENAR_STAGE2_PAREDES_10000_25000
**Tarea:** Stage 2 — Evasión de obstáculos simples con 2 paredes (10000-25000 iter):
```bash
cd /home/udc/Unitree_G1
conda run -n hgen python entrenamiento/train_navigation.py \
  --config entrenamiento/configs/nav_policy.yaml \
  --scene escenas/nav_scenes/scene_nav_2walls.xml \
  --resume entrenamiento/logs/nav/stage1/model_10000.pt \
  --max_iter 25000 \
  --log_dir entrenamiento/logs/nav/stage2
```
**Ejecutar SOLO cuando AGENTE-13 haya aprobado Stage 1.**  
**Reportar:** Reward cada 2000 iter (10000→25000). Tasa de llegada al final. Colisiones por episodio.

---

### AGENTE-15 | ANALIZAR_STAGE2_EVASION
**Tarea:** Analizar el comportamiento de evasión en Stage 2 (10 episodios headless):
```bash
cd /home/udc/Unitree_G1
conda run -p envs/g1_udc python simulacion/sim_nav.py \
  --policy entrenamiento/logs/nav/stage2/model_25000.pt \
  --headless --episodes 10
```
**Analizar:** ¿El robot rodea las paredes o choca? ¿Qué rayos LIDAR activan el comportamiento de evasión?  
**Criterio Stage 2:** Tasa llegada > 60% con paredes, colisiones < 1 por episodio.  
**Reportar:** Tabla de 10 episodios, análisis del comportamiento de evasión observado.

---

### AGENTE-16 | ENTRENAR_STAGE3_ENTORNO_COMPLETO_25000_40000
**Tarea:** Stage 3 — Entorno completo con muebles (25000-40000 iter):
```bash
cd /home/udc/Unitree_G1
conda run -n hgen python entrenamiento/train_navigation.py \
  --config entrenamiento/configs/nav_policy.yaml \
  --scene escenas/nav_scenes/scene_nav_full.xml \
  --resume entrenamiento/logs/nav/stage2/model_25000.pt \
  --max_iter 40000 \
  --log_dir entrenamiento/logs/nav/stage3
```
**Ejecutar SOLO cuando AGENTE-15 haya aprobado Stage 2.**  
**Reportar:** Reward cada 2000 iter (25000→40000). Tasa de llegada. Distancia media recorrida por episodio.

---

### AGENTE-17 | ANALIZAR_STAGE3_ENTORNO_COMPLETO
**Tarea:** Analizar comportamiento en entorno completo (15 episodios headless):
```bash
cd /home/udc/Unitree_G1
conda run -p envs/g1_udc python simulacion/sim_nav.py \
  --policy entrenamiento/logs/nav/stage3/model_40000.pt \
  --headless --episodes 15
```
**Criterio Stage 3:** Tasa llegada > 50% con muebles. Tiempo máximo 200 pasos.  
**Reportar:** Tabla 15 episodios, análisis cualitativo del comportamiento.

---

### AGENTE-18 | ENTRENAR_STAGE4_NAV_A_DEPOSITO_40000_50000
**Tarea:** Stage 4 — Navegar desde la caja hasta la zona de depósito (40000-50000 iter):
```bash
cd /home/udc/Unitree_G1
conda run -n hgen python entrenamiento/train_navigation.py \
  --config entrenamiento/configs/nav_policy.yaml \
  --scene escenas/nav_scenes/scene_nav_full.xml \
  --mode nav_to_deposit \
  --resume entrenamiento/logs/nav/stage3/model_40000.pt \
  --max_iter 50000 \
  --log_dir entrenamiento/logs/nav/stage4
```
**Ejecutar SOLO cuando AGENTE-17 haya aprobado Stage 3.**  
**Reportar:** Reward y tasa de llegada cada 2000 iter (40000→50000).

---

### AGENTE-19 | ANALIZAR_STAGE4_NAV_DEPOSITO
**Tarea:** Analizar Stage 4 y comparar nav_to_box vs nav_to_deposit (10 episodios cada uno):
```bash
cd /home/udc/Unitree_G1
# nav_to_box
conda run -p envs/g1_udc python simulacion/sim_nav.py \
  --policy entrenamiento/logs/nav/stage4/model_best.pt \
  --mode nav_to_box --headless --episodes 10

# nav_to_deposit  
conda run -p envs/g1_udc python simulacion/sim_nav.py \
  --policy entrenamiento/logs/nav/stage4/model_best.pt \
  --mode nav_to_deposit --headless --episodes 10
```
**Reportar:** Tabla comparativa. ¿La política generaliza bien a ambos modos?

---

## FASE 4 — Validación (Agentes 20-27, EN PARALELO después de Stage 4)

### AGENTE-20 | VALIDAR_30_EPISODIOS_HEADLESS
**Tarea:** Validación principal: 30 episodios headless en escenas aleatorias:
```bash
cd /home/udc/Unitree_G1
conda run -p envs/g1_udc python simulacion/sim_nav.py \
  --policy entrenamiento/logs/nav/stage4/model_best.pt \
  --headless --episodes 30 --random_scene
```
**Por episodio:** ¿llegó?, tiempo (pasos), distancia recorrida, colisiones detectadas (rayos < 0.15m).  
**Reportar:** Tabla de 30 episodios + estadísticas: tasa éxito, tiempo medio, colisiones totales.

---

### AGENTE-21 | VALIDAR_NAV_TO_DEPOSIT_15_EPISODIOS
**Tarea:** 15 episodios validando navegación al depósito en escenas aleatorias:
```bash
cd /home/udc/Unitree_G1
conda run -p envs/g1_udc python simulacion/sim_nav.py \
  --policy entrenamiento/logs/nav/stage4/model_best.pt \
  --mode nav_to_deposit --headless --episodes 15 --random_scene
```
**Reportar:** Tabla de 15 episodios. Comparativa con nav_to_box.

---

### AGENTE-22 | VALIDAR_INTEGRACION_NAV_LOCO_DR
**Tarea:** Validar pipeline completo: política navegación + política locomoción DR (10 episodios):
```bash
cd /home/udc/Unitree_G1
conda run -p envs/g1_udc python simulacion/sim_nav_loco_integrated.py \
  --nav_policy politicas/model_nav_jit.pt \
  --loco_policy politicas/model_DR_jit.pt \
  --headless --episodes 10
```
**Verificar:** ¿El robot camina establemente mientras navega? ¿Se cae? ¿Llega al objetivo?  
**Reportar:** 10 episodios con estado de locomoción (estable/inestable/caído) por episodio.

---

### AGENTE-23 | ANALIZAR_COMPORTAMIENTO_EVASION_LIDAR
**Tarea:** Análisis detallado del comportamiento de evasión: qué rayos LIDAR son más informativos:
```bash
cd /home/udc/Unitree_G1
conda run -p envs/g1_udc python -c "
import torch, numpy as np, sys
sys.path.insert(0, '.')
from entrenamiento.utils.lidar_preprocessing import sim_lidar_to_obs, N_RINGS, N_RAYS_PER_RING

# Cargar la política
policy = torch.jit.load('politicas/model_nav_jit.pt')
policy.eval()

# Crear obs de prueba: obstáculo a diferentes ángulos del anillo frontal
print('=== ANÁLISIS DE RESPUESTA A OBSTÁCULOS ===')
for obstacle_ray in [0, 4, 8, 12, 16]:  # anillo 0: frente, laterales
    obs = np.ones(135, dtype=np.float32) * 0.9  # todo libre
    # Poner obstáculo a 1m (0.05 normalizado) en el rayo especificado del anillo 1
    obs[obstacle_ray] = 0.05  # obstáculo muy cerca
    # Objetivo: 2m al frente
    obs[128] = 2.0  # dx
    obs[129] = 0.0  # dy
    obs[130] = 2.0  # dist
    obs[131] = 0.0  # yaw_error
    obs[132:135] = [0.3, 0.0, 0.0]  # velocidad actual
    
    with torch.no_grad():
        action = policy(torch.tensor(obs).unsqueeze(0)).squeeze().numpy()
    azim = obstacle_ray * 11.25  # grados
    print(f'  Obstáculo a azim={azim:.0f}° → cmd=[{action[0]:.3f}, {action[1]:.3f}, {action[2]:.3f}]')
"
```
**Reportar:** Análisis de respuesta. ¿La política gira apropiadamente al detectar obstáculos?

---

### AGENTE-24 | ANALIZAR_PREPROCESSING_LIDAR_SIM_REAL
**Tarea:** Analizar el gap sim-to-real del preprocesamiento LIDAR:
```bash
cd /home/udc/Unitree_G1
conda run -p envs/g1_udc python -c "
import numpy as np, sys
sys.path.insert(0, '.')
from entrenamiento.utils.lidar_preprocessing import livox_to_sim_format, sim_lidar_to_obs

print('=== ANÁLISIS GAP SIM→REAL LIDAR ===')

# Simular una nube de puntos del LIVOX real con densidad alta
N = 5000  # LIVOX MID360 genera ~200k puntos/seg, ~5000 por scan
np.random.seed(42)
theta = np.random.uniform(0, 2*np.pi, N)
# Distribución realista: muchos puntos en elevaciones bajas, pocos arriba
phi = np.random.choice(
    [np.radians(-7), np.radians(10), np.radians(25), np.radians(45)],
    N, p=[0.4, 0.3, 0.2, 0.1]
) + np.random.normal(0, np.radians(3), N)
r = np.random.uniform(0.5, 15.0, N)

pts = np.stack([r*np.cos(phi)*np.cos(theta), r*np.cos(phi)*np.sin(theta), r*np.sin(phi)], axis=1)

lidar_sim_format = livox_to_sim_format(pts)

print(f'Puntos entrada: {N}')
print(f'Salida shape: {lidar_sim_format.shape}')
print(f'Rango: [{lidar_sim_format.min():.3f}, {lidar_sim_format.max():.3f}]')
print(f'Media: {lidar_sim_format.mean():.3f}')
print(f'Rayos \"libres\" (>0.9): {(lidar_sim_format>0.9).sum()}/128')
print(f'Rayos \"obstruidos\" (<0.1): {(lidar_sim_format<0.1).sum()}/128')

# Verificar que el formato coincide con sim
print()
print('Distribución por anillo:')
for r_idx in range(4):
    ring = lidar_sim_format[r_idx*32:(r_idx+1)*32]
    print(f'  Anillo {r_idx+1}: mean={ring.mean():.3f} std={ring.std():.3f}')
"
```
**Reportar:** Distribución por anillo. Análisis de si el preprocesamiento es válido para datos reales.

---

### AGENTE-25 | VALIDAR_CON_RUIDO_LIDAR_DOBLE
**Tarea:** Probar robustez con ruido LIDAR aumentado al doble (σ=0.1 en vez de 0.05):
```bash
cd /home/udc/Unitree_G1
# Modificar temporalmente lidar_preprocessing.py para usar sigma=0.1
# Luego correr 15 episodios
conda run -p envs/g1_udc python simulacion/sim_nav.py \
  --policy entrenamiento/logs/nav/stage4/model_best.pt \
  --headless --episodes 15 --lidar_noise 0.1
```
**Comparar:** Tasa de éxito con ruido normal vs ruido doble.  
**Reportar:** Tabla comparativa. ¿La política es robusta al ruido aumentado?

---

### AGENTE-26 | MEDIR_LATENCIA_INFERENCIA_NAV
**Tarea:** Medir la latencia de inferencia de la política de navegación (debe ser <2ms):
```bash
cd /home/udc/Unitree_G1
conda run -p envs/g1_udc python -c "
import torch, time, numpy as np

policy = torch.jit.load('politicas/model_nav_jit.pt')
policy.eval()
obs = torch.zeros(1, 135)

# Warmup
for _ in range(100): policy(obs)

# Medición CPU
with torch.no_grad():
    start = time.perf_counter()
    for _ in range(10000): policy(obs)
    elapsed = time.perf_counter() - start

ms_per_call = (elapsed / 10000) * 1000
hz = 1000 / ms_per_call
print(f'Latencia inferencia NAV policy:')
print(f'  Media: {ms_per_call:.4f} ms/llamada')
print(f'  Frecuencia: {hz:.0f} Hz')
print(f'  Requerimiento: < 2ms (50Hz budget)')
print(f'  Cumple: {\"SI\" if ms_per_call < 2.0 else \"NO\"}')
"
```
**Reportar:** Latencia exacta en ms. ¿Cumple el requerimiento de <2ms para robot real (CPU)?

---

### AGENTE-27 | VALIDAR_LIVOX_TO_SIM_FORMAT_COMPLETO
**Tarea:** Validar la función `livox_to_sim_format` con datos sintéticos que simulan escenarios reales:
```bash
cd /home/udc/Unitree_G1
conda run -p envs/g1_udc python -c "
import numpy as np, sys
sys.path.insert(0, '.')
from entrenamiento.utils.lidar_preprocessing import livox_to_sim_format

print('=== VALIDACIÓN livox_to_sim_format ===')

# Escenario 1: pared frontal a 2m
N = 1000
theta = np.random.uniform(-np.pi/4, np.pi/4, N)  # frente ±45°
phi = np.random.uniform(-np.radians(10), np.radians(50), N)
r = np.full(N, 2.0)
pts_wall = np.stack([r*np.cos(phi)*np.cos(theta), r*np.cos(phi)*np.sin(theta), r*np.sin(phi)], axis=1)
result = livox_to_sim_format(pts_wall)
print(f'Escenario 1 (pared frontal 2m): rayos frontales [0-8]={result[:8].mean():.3f} (esperado ~0.1)')

# Escenario 2: espacio abierto
pts_open = np.random.randn(1000, 3) * 15
pts_open = pts_open[np.linalg.norm(pts_open, axis=1) > 8]  # todos lejos
result2 = livox_to_sim_format(pts_open)
print(f'Escenario 2 (espacio abierto): mean={result2.mean():.3f} (esperado ~0.9)')

# Escenario 3: sin puntos (LIDAR falla)
result3 = livox_to_sim_format(None)
print(f'Escenario 3 (sin datos): mean={result3.mean():.3f} (esperado 1.0)')

print()
print('VALIDACIÓN COMPLETADA')
"
```
**Reportar:** Resultados de los 3 escenarios. ¿La función se comporta correctamente en cada caso?

---

## FASE 5 — Export y Reporte (Agentes 28-30)

### AGENTE-28 | EXPORTAR_POLITICA_NAV_JIT
**Tarea:** Exportar la política de navegación a TorchScript JIT:
```bash
cd /home/udc/Unitree_G1
conda run -n hgen python entrenamiento/export_politica.py \
  entrenamiento/logs/nav/stage4/model_best.pt \
  politicas/model_nav_jit.pt \
  135 \
  3
# Verificar
conda run -p envs/g1_udc python -c "
import torch, numpy as np, os
m = torch.jit.load('politicas/model_nav_jit.pt')
m.eval()
obs = torch.zeros(1, 135)
with torch.no_grad():
    out = m(obs)
print(f'Input: (135,) -> Output: {out.shape}')
print(f'Output range: [{out.min():.3f}, {out.max():.3f}]')
assert out.shape == (1, 3), f'ERROR: {out.shape}'
size_kb = os.path.getsize('politicas/model_nav_jit.pt') / 1024
print(f'Tamaño: {size_kb:.1f} KB')
print('EXPORT NAV OK')
"
```
**Reportar:** Stdout completo. Confirmar input=(135,), output=(3,), rango [-1,1].

---

### AGENTE-29 | ACTUALIZAR_G1_CONSTANTS_NAV
**Tarea:** Actualizar `simulacion/g1_constants.py` con las constantes de navegación:
```bash
cd /home/udc/Unitree_G1
cat >> simulacion/g1_constants.py << 'EOF'

# ============================================================
# CONSTANTES POLÍTICA DE NAVEGACIÓN (añadidas en Plan 03)
# ============================================================

# Índices del obs_nav (135 dims)
NAV_OBS_LIDAR_START = 0    # índice 0-127: LIDAR 4 anillos × 32 rayos
NAV_OBS_LIDAR_END   = 128
NAV_OBS_POS_OBJ_REL = 128  # índices 128-129: (dx, dy) en frame robot
NAV_OBS_DIST_OBJ    = 130  # índice 130: distancia al objetivo (m)
NAV_OBS_YAW_ERROR   = 131  # índice 131: error de orientación (rad)
NAV_OBS_VEL_START   = 132  # índices 132-134: velocidad (vx, vy, wz)
NAV_OBS_DIM         = 135

# Índices de anillos LIDAR en obs_nav
NAV_LIDAR_RING1_START = 0   # anillo -7°,  índices 0-31
NAV_LIDAR_RING2_START = 32  # anillo +10°, índices 32-63
NAV_LIDAR_RING3_START = 64  # anillo +25°, índices 64-95
NAV_LIDAR_RING4_START = 96  # anillo +45°, índices 96-127

# Escala de acciones de navegación
NAV_ACTION_VX_SCALE = 1.0   # m/s ([-0.3, 1.0])
NAV_ACTION_VY_SCALE = 0.3   # m/s
NAV_ACTION_WZ_SCALE = 1.0   # rad/s

# Dimensiones
NAV_ACT_DIM = 3
EOF
echo "g1_constants.py actualizado con constantes NAV"
conda run -p envs/g1_udc python -c "
import sys; sys.path.insert(0, '.')
from simulacion.g1_constants import NAV_OBS_DIM, NAV_ACT_DIM
print(f'NAV_OBS_DIM={NAV_OBS_DIM}, NAV_ACT_DIM={NAV_ACT_DIM}')
assert NAV_OBS_DIM == 135
print('OK')
"
```
**Reportar:** Sección añadida, test de importación OK.

---

### AGENTE-30 | REPORTE_FINAL_Y_COMMIT
**Tarea:** Generar el reporte completo del Plan 03 y hacer el commit:

Crear `/home/udc/Unitree_G1/reportes/reporte_plan03_navegacion_<FECHA>.md` con:
```
# Reporte Plan 03 — Política de Navegación LIDAR 3D G1
## Fecha y duración total
## Resumen ejecutivo
## Resultado de cada agente (01-30):
   - Comando ejecutado
   - Stdout/stderr completo
   - Errores y soluciones
## Verificación LIDAR (AGENTE-01): N rangefinders, índices sensordata
## Preprocesamiento LIDAR (AGENTE-03): normalización, filtro mediana, livox_to_sim_format
## Curvas de entrenamiento por stage:
   | Iter | Reward_medio | Tasa_llegada | Colisiones/ep |
   Stage 1 (0-10000 campo libre): ...
   Stage 2 (10000-25000 paredes): ...
   Stage 3 (25000-40000 full): ...
   Stage 4 (40000-50000 depósito): ...
## Tabla de validación 30 episodios headless:
   | Ep | Escena | ¿Llegó? | Pasos | Distancia(m) | Colisiones |
## Validación integración NAV + DR Locomoción (10 episodios):
   | Ep | ¿Llegó? | ¿Estable? | ¿Se cayó? |
## Análisis gap sim→real LIDAR (AGENTE-24)
## Validación livox_to_sim_format (3 escenarios, AGENTE-27)
## Benchmark latencia inferencia NAV policy (AGENTE-26)
## Política exportada: politicas/model_nav_jit.pt
   - Input: (135,) → Output: (3,) en [-1, 1]
   - Tamaño: X KB
## Problemas encontrados y soluciones
## Próximos pasos (Plan 04)
```

Luego ejecutar:
```bash
cd /home/udc/Unitree_G1
git add politicas/model_nav_jit.pt
git add entrenamiento/envs/g1_nav_env.py
git add entrenamiento/utils/lidar_preprocessing.py
git add entrenamiento/configs/nav_policy.yaml
git add entrenamiento/train_navigation.py
git add simulacion/sim_nav.py
git add simulacion/sim_nav_loco_integrated.py
git add simulacion/g1_constants.py
git add escenas/nav_scenes/
git add reportes/reporte_plan03_navegacion_*.md
git commit -m "$(cat <<'EOF'
feat: politica navegacion LIDAR 3D G1 50000 iter curriculum

30 sub-agentes: analisis lidar, preprocessing sim→real,
4 escenas nav, curriculum stage1-4, validacion 55+ episodios,
livox_to_sim_format, integracion DR locomotion, export JIT.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```
**Reportar:** Reporte completo creado. Hash del commit.
