# Conversion Tools / Herramientas de Conversión

[🇬🇧 English](#english) | [🇪🇸 Español](#español)

---

<a name="english"></a>
## 🇬🇧 English

Utility scripts for converting and preparing robot models between formats. These are one-off tools — not part of the training or control pipeline.

### Scripts

| Script | Converts | Input → Output |
|--------|----------|----------------|
| `convert_mujoco_to_urdf.py` | MuJoCo XML → URDF (full) | `.xml` → `.urdf` |
| `convert_mujoco_to_urdf_simple.py` | MuJoCo XML → URDF (simplified) | `.xml` → `.urdf` |
| `convert_and_fix_urdf.py` | MuJoCo XML → URDF with joint fixes | `.xml` → fixed `.urdf` |
| `convert_g1_12dof.py` | G1 23-DOF → 12-DOF legs only | full `xml` → 12-DOF `.xml` |
| `convert_urdf_to_usd.py` | URDF → USD for Isaac Sim | `.urdf` → `.usd` |
| `fix_usd_articulation.py` | Fix USD articulation graph | `.usd` → corrected `.usd` |
| `setup_ros2_env.sh` | Sets ROS2 + LiDAR environment variables | shell env setup |

### Typical Conversion Chain (MuJoCo → Isaac Lab)

```bash
# Step 1: XML → URDF (with joint fixes)
python herramientas/convert_and_fix_urdf.py \
  --input escenas/g1_23dof.xml \
  --output escenas/g1.urdf

# Step 2: URDF → USD (requires isaaclab env)
conda activate isaaclab
python herramientas/convert_urdf_to_usd.py \
  --input escenas/g1.urdf \
  --output escenas/g1.usd

# Step 3: Fix articulation graph if Isaac Sim does not detect joints
python herramientas/fix_usd_articulation.py escenas/g1.usd
```

**Environment:** Use `g1_udc` for steps 1–2, `isaaclab` for USD conversion.

---

<a name="español"></a>
## 🇪🇸 Español

Scripts de utilidad para convertir y preparar modelos del robot entre distintos formatos. Son herramientas de uso puntual — no forman parte del pipeline de entrenamiento ni de control.

### Scripts

| Script | Convierte | Entrada → Salida |
|--------|----------|-----------------|
| `convert_mujoco_to_urdf.py` | MuJoCo XML → URDF (completo) | `.xml` → `.urdf` |
| `convert_mujoco_to_urdf_simple.py` | MuJoCo XML → URDF (simplificado) | `.xml` → `.urdf` |
| `convert_and_fix_urdf.py` | MuJoCo XML → URDF con corrección de joints | `.xml` → `.urdf` corregido |
| `convert_g1_12dof.py` | G1 23-DOF → solo 12-DOF de piernas | `.xml` completo → `.xml` 12-DOF |
| `convert_urdf_to_usd.py` | URDF → USD para Isaac Sim | `.urdf` → `.usd` |
| `fix_usd_articulation.py` | Corrige grafo de articulaciones USD | `.usd` → `.usd` corregido |
| `setup_ros2_env.sh` | Configura variables de entorno ROS2 + LiDAR | configuración de shell |

### Cadena de Conversión Típica (MuJoCo → Isaac Lab)

```bash
# Paso 1: XML → URDF (con corrección de joints)
python herramientas/convert_and_fix_urdf.py \
  --input escenas/g1_23dof.xml \
  --output escenas/g1.urdf

# Paso 2: URDF → USD (requiere entorno isaaclab)
conda activate isaaclab
python herramientas/convert_urdf_to_usd.py \
  --input escenas/g1.urdf \
  --output escenas/g1.usd

# Paso 3: Corregir articulaciones si Isaac Sim no detecta los joints
python herramientas/fix_usd_articulation.py escenas/g1.usd
```

**Entorno:** Usar `g1_udc` para pasos 1–2, `isaaclab` para la conversión USD.
