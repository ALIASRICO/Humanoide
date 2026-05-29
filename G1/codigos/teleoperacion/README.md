# Teleoperación G1 — IK de brazos + Grabación de episodios

Código para teleoperar el G1 y recolectar datos de demostración para imitation learning.

Fuente: https://github.com/unitreerobotics/xr_teleoperate

---

## Contenido

```
teleoperacion/
├── robot_control/
│   ├── robot_arm_ik.py       IK de brazos G1 (pinocchio + casadi)
│   ├── robot_arm.py          Control de brazos vía SDK
│   └── robot_hand_unitree.py Control de mano dextra Unitree
└── utils/
    ├── episode_writer.py     Grabación de episodios (estado + imágenes)
    └── weighted_moving_filter.py  Filtro para suavizar comandos
```

---

## IK de brazos (`robot_arm_ik.py`)

Resuelve la cinemática inversa del G1 para control de brazos:

```python
from codigos.teleoperacion.robot_control.robot_arm_ik import G1_29_ArmIK

ik = G1_29_ArmIK()
# Dar pose cartesiana de la mano (4x4 SE3), recibir ángulos de joints
joint_angles = ik.solve(left_wrist_pose, right_wrist_pose)
```

**Dependencias:**
```bash
pip install pinocchio casadi meshcat
```

Necesita el URDF del G1 (apunta a `assets/g1/g1_body29_hand14.urdf`).
El URDF está en `/home/udc/Unitree_G1/escenas/g1_description/` — ajustar la ruta en `robot_arm_ik.py`.

---

## Grabación de episodios (`episode_writer.py`)

Graba episodios de teleoperación para imitation learning:

```python
from codigos.teleoperacion.utils.episode_writer import EpisodeWriter

writer = EpisodeWriter(
    task_dir="dataset/pick_cup",
    task_goal="Pick up the red cup",
    frequency=30
)

# Durante el episodio:
writer.start_episode()
writer.add_item(
    qpos=joint_positions,   # 29 floats
    qvel=joint_velocities,  # 29 floats
    action=action,          # 29 floats
    images={"front": img}   # dict de cámaras
)
writer.save_episode()       # guardar al terminar
```

---

## Compatibilidad con unitree_lerobot

Los episodios grabados con `episode_writer.py` se convierten al formato LeRobot con:
```bash
python codigos/imitacion/convert_to_lerobot.py dataset/pick_cup
```

---

## Hardware de teleoperación soportado

El IK y grabación funcionan también con:
- Mando inalámbrico (control articular directo)
- Cualquier dispositivo que envíe poses cartesianas a `G1_29_ArmIK`
- Apple Vision Pro / PICO / Meta Quest (requiere app adicional de xr_teleoperate)
