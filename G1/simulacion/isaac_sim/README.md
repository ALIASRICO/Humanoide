# Isaac Sim — G1 Manipulation Simulation / Simulación de Manipulación G1

[🇬🇧 English](#english) | [🇪🇸 Español](#español)

---

<a name="english"></a>
## 🇬🇧 English

NVIDIA Isaac Sim simulation of the Unitree G1 (29-DOF) in manipulation tasks. Uses the same DDS communication protocol as the physical robot — the same control code runs in both simulation and real hardware.

### Prerequisites

```bash
conda activate isaaclab
# DDS variables are set automatically by launch_g1.sh
```

### Available Scenes (14 aliases)

Run with: `bash simulacion/isaac_sim/launch_g1.sh [alias]`

| Alias | Task ID | Description |
|-------|---------|-------------|
| `cylinder_dex1` | `Isaac-PickPlace-Cylinder-G129-Dex1-Joint` | Pick & place cylinder — DEX1 gripper |
| `cylinder_dex3` | `Isaac-PickPlace-Cylinder-G129-Dex3-Joint` | Pick & place cylinder — DEX3 hand |
| `cylinder_inspire` | `Isaac-PickPlace-Cylinder-G129-Inspire-Joint` | Pick & place cylinder — Inspire hand |
| `redblock_dex1` | `Isaac-PickPlace-RedBlock-G129-Dex1-Joint` | Pick & place red block — DEX1 gripper |
| `redblock_dex3` | `Isaac-PickPlace-RedBlock-G129-Dex3-Joint` | Pick & place red block — DEX3 hand |
| `redblock_inspire` | `Isaac-PickPlace-RedBlock-G129-Inspire-Joint` | Pick & place red block — Inspire hand |
| `stack_dex1` | `Isaac-Stack-RgyBlock-G129-Dex1-Joint` | Stack R/G/Y blocks — DEX1 gripper |
| `stack_dex3` | `Isaac-Stack-RgyBlock-G129-Dex3-Joint` | Stack R/G/Y blocks — DEX3 hand |
| `stack_inspire` | `Isaac-Stack-RgyBlock-G129-Inspire-Joint` | Stack R/G/Y blocks — Inspire hand |
| `drawer_dex1` | `Isaac-Pick-Redblock-Into-Drawer-G129-Dex1-Joint` | Place block into drawer — DEX1 gripper |
| `drawer_dex3` | `Isaac-Pick-Redblock-Into-Drawer-G129-Dex3-Joint` | Place block into drawer — DEX3 hand |
| `move_dex1` | `Isaac-Move-Cylinder-G129-Dex1-Wholebody` | Move cylinder — full 29-DOF wholebody |
| `move_dex3` | `Isaac-Move-Cylinder-G129-Dex3-Wholebody` | Move cylinder — full 29-DOF wholebody |
| `move_inspire` | `Isaac-Move-Cylinder-G129-Inspire-Wholebody` | Move cylinder — full 29-DOF wholebody |

> Tasks with `Wholebody` in their name enable locomotion (the robot can walk). Other tasks use a fixed base.

### Launch Commands

```bash
cd /home/udc/Humanoide/G1

# Basic launch (DDS action source — default)
bash simulacion/isaac_sim/launch_g1.sh cylinder_dex1

# Data replay from recorded episode
bash simulacion/isaac_sim/launch_g1.sh drawer_dex3 replay
```

After launch, click `PerspectiveCamera → Cameras → PerspectiveCamera` in the Isaac Sim viewer to see the main scene.

### Keyboard Control

Use `send_commands_keyboard.py` in a **separate terminal** while Isaac Sim runs in DDS mode:

```bash
# Terminal 2 (while Isaac Sim runs in Terminal 1)
conda activate isaaclab
export LD_LIBRARY_PATH="/home/udc/Humanoide/humanoide/cyclonedds/install/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export CYCLONEDDS_URI='<CycloneDDS><Domain id="any"><SharedMemory><Enable>false</Enable></SharedMemory></Domain></CycloneDDS>'
cd /home/udc/Humanoide/G1
python simulacion/isaac_sim/send_commands_keyboard.py
```

| Key | Action |
|-----|--------|
| `W` / `S` | Forward / backward |
| `A` / `D` | Strafe left / right |
| `Z` / `X` | Yaw left / right |
| `C` | Crouch |
| `Q` | Quit |

> Keyboard control only works with `Wholebody` tasks.

### Camera Viewer

The image server starts automatically with Isaac Sim. Open the viewer in another terminal:

```bash
conda activate isaaclab
cd /home/udc/Humanoide/G1
python simulacion/isaac_sim/teleimager/image_client.py --host localhost
```

Displays a **Combined Image** window showing all enabled cameras (head, left wrist, right wrist).  
Press `q` in any OpenCV window to close.

> **Camera config file:** `simulacion/cam_config_server.yaml` — do NOT use the one inside `simulacion/isaac_sim/`.

### How to Close Isaac Sim

```bash
pkill -9 -f "sim_main.py"
# Verify:
pgrep -fl "sim_main.py"   # should return nothing
```

### Known Issues

| Issue | Solution |
|-------|----------|
| First launch takes ~5 minutes | Normal — GPU shader compilation. Do not close the process. |
| Cameras not working | Edit `simulacion/cam_config_server.yaml`, not the one inside `isaac_sim/` |
| Process crashes with `dds_write.c:318` assertion | DDS variables not set. `launch_g1.sh` sets them automatically. |
| Robot not visible after launch | Click `PerspectiveCamera → Cameras → PerspectiveCamera` in the viewer |

---

<a name="español"></a>
## 🇪🇸 Español

Simulación NVIDIA Isaac Sim del Unitree G1 (29-DOF) en tareas de manipulación. Usa el mismo protocolo DDS que el robot físico — el mismo código de control funciona en simulación y en hardware real.

### Prerrequisitos

```bash
conda activate isaaclab
# Las variables DDS se configuran automáticamente dentro de launch_g1.sh
```

### Escenas Disponibles (14 alias)

Lanzar con: `bash simulacion/isaac_sim/launch_g1.sh [alias]`

| Alias | Task ID | Descripción |
|-------|---------|-------------|
| `cylinder_dex1` | `Isaac-PickPlace-Cylinder-G129-Dex1-Joint` | Pick & place cilindro — garra DEX1 |
| `cylinder_dex3` | `Isaac-PickPlace-Cylinder-G129-Dex3-Joint` | Pick & place cilindro — mano DEX3 |
| `cylinder_inspire` | `Isaac-PickPlace-Cylinder-G129-Inspire-Joint` | Pick & place cilindro — mano Inspire |
| `redblock_dex1` | `Isaac-PickPlace-RedBlock-G129-Dex1-Joint` | Pick & place bloque rojo — garra DEX1 |
| `redblock_dex3` | `Isaac-PickPlace-RedBlock-G129-Dex3-Joint` | Pick & place bloque rojo — mano DEX3 |
| `redblock_inspire` | `Isaac-PickPlace-RedBlock-G129-Inspire-Joint` | Pick & place bloque rojo — mano Inspire |
| `stack_dex1` | `Isaac-Stack-RgyBlock-G129-Dex1-Joint` | Apilar bloques R/G/Y — garra DEX1 |
| `stack_dex3` | `Isaac-Stack-RgyBlock-G129-Dex3-Joint` | Apilar bloques R/G/Y — mano DEX3 |
| `stack_inspire` | `Isaac-Stack-RgyBlock-G129-Inspire-Joint` | Apilar bloques R/G/Y — mano Inspire |
| `drawer_dex1` | `Isaac-Pick-Redblock-Into-Drawer-G129-Dex1-Joint` | Meter bloque en cajón — garra DEX1 |
| `drawer_dex3` | `Isaac-Pick-Redblock-Into-Drawer-G129-Dex3-Joint` | Meter bloque en cajón — mano DEX3 |
| `move_dex1` | `Isaac-Move-Cylinder-G129-Dex1-Wholebody` | Mover cilindro — cuerpo completo 29-DOF |
| `move_dex3` | `Isaac-Move-Cylinder-G129-Dex3-Wholebody` | Mover cilindro — cuerpo completo 29-DOF |
| `move_inspire` | `Isaac-Move-Cylinder-G129-Inspire-Wholebody` | Mover cilindro — cuerpo completo 29-DOF |

> Las tareas con `Wholebody` en el nombre permiten locomoción. Las demás tienen base fija.

### Comandos de Lanzado

```bash
cd /home/udc/Humanoide/G1

# Lanzado básico (fuente de acción DDS — por defecto)
bash simulacion/isaac_sim/launch_g1.sh cylinder_dex1

# Reproducir episodio grabado
bash simulacion/isaac_sim/launch_g1.sh drawer_dex3 replay
```

Tras el lanzado, hacer clic en `PerspectiveCamera → Cameras → PerspectiveCamera` en el visor para ver la escena.

### Control por Teclado

Usar `send_commands_keyboard.py` en una **terminal separada** mientras Isaac Sim corre en modo DDS:

```bash
# Terminal 2 (mientras Isaac Sim corre en Terminal 1)
conda activate isaaclab
export LD_LIBRARY_PATH="/home/udc/Humanoide/humanoide/cyclonedds/install/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export CYCLONEDDS_URI='<CycloneDDS><Domain id="any"><SharedMemory><Enable>false</Enable></SharedMemory></Domain></CycloneDDS>'
cd /home/udc/Humanoide/G1
python simulacion/isaac_sim/send_commands_keyboard.py
```

| Tecla | Acción |
|-------|--------|
| `W` / `S` | Avanzar / retroceder |
| `A` / `D` | Desplazar izquierda / derecha |
| `Z` / `X` | Girar izquierda / derecha |
| `C` | Agacharse |
| `Q` | Salir |

> El control por teclado solo funciona con tareas `Wholebody`.

### Visor de Cámaras

El servidor de imágenes arranca automáticamente con Isaac Sim. Abrir el visor en otra terminal:

```bash
conda activate isaaclab
cd /home/udc/Humanoide/G1
python simulacion/isaac_sim/teleimager/image_client.py --host localhost
```

Muestra una ventana **Combined Image** con todas las cámaras habilitadas (cabeza, muñeca izquierda, muñeca derecha).  
Pulsar `q` en cualquier ventana OpenCV para cerrar.

> **Archivo de configuración de cámaras:** `simulacion/cam_config_server.yaml` — NO usar el que está dentro de `simulacion/isaac_sim/`.

### Cómo Cerrar Isaac Sim

```bash
pkill -9 -f "sim_main.py"
# Verificar:
pgrep -fl "sim_main.py"   # no debe devolver nada
```

### Problemas Conocidos

| Problema | Solución |
|----------|----------|
| Primera ejecución tarda ~5 minutos | Normal — compilación de shaders GPU. No cerrar el proceso. |
| Cámaras no funcionan | Editar `simulacion/cam_config_server.yaml`, no el que está en `isaac_sim/` |
| Crash con aserción `dds_write.c:318` | Variables DDS no configuradas. `launch_g1.sh` las pone automáticamente. |
| Robot no visible tras el lanzado | Clic en `PerspectiveCamera → Cameras → PerspectiveCamera` en el visor |
