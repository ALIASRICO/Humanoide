# Isaac Sim / Isaac Lab — G1 29-DOF

Scripts de utilidad para trabajar con el G1 en Isaac Sim y Isaac Lab.

Entorno requerido: `isaaclab` (instalado en `/home/udc/IsaacLab/`)

---

## Inspeccionar joints del G1

```bash
conda run -n isaaclab python codigos/isaac_sim/inspect_g1_joints.py
```

Muestra todos los joints hinge del G1 con límites y posición default.
Útil para verificar el orden DOF antes de entrenar o exportar políticas.

---

## Simulación de manipulación (Isaac Sim)

Tareas de pick & place / stacking usando la mano DEX1:

```bash
# Desde la raíz del repo
bash simulacion/isaac_sim/launch_g1.sh [tarea]
```

Tareas disponibles:
| Alias              | Task ID                                          |
|--------------------|--------------------------------------------------|
| `pick_place_cylinder` | Isaac-PickPlace-Cylinder-G129-Dex1-Joint      |
| `pick_place_redblock` | Isaac-PickPlace-RedBlock-G129-Dex1-Joint      |
| `stack_blocks`        | Isaac-Stack-RGYBlock-G129-Dex1-Joint          |
| `pick_into_drawer`    | Isaac-PickRedBlockIntoDrawer-G129-Dex1-Joint  |
| `move_cylinder`       | Isaac-MoveCylinder-G129-Dex1-Wholebody-Joint  |

> NOTA: La primera ejecución tarda ~5 min en compilar shaders.

---

## Entrenamiento RL de locomoción (Isaac Lab)

```bash
bash entrenamiento/isaac_rl_lab/launch_g1_train.sh [tarea]
```

Tareas disponibles:
| Alias     | Descripción                              |
|-----------|------------------------------------------|
| `velocity` | Locomoción por velocidad (default)       |
| `dance`    | Imitación de movimiento Dance-102 (BVH)  |
| `gangnam`  | Imitación Gangnam Style (BVH)            |

```bash
# Reproducir política entrenada
bash entrenamiento/isaac_rl_lab/launch_g1_play.sh velocity [ruta/al.pt]
```

---

## Paths de modelos

Los USD del G1 están en `escenas/unitree_model/G1/29dof/usd/`.
`UNITREE_MODEL_DIR` en `entrenamiento/isaac_rl_lab/source/.../assets/robots/unitree.py` ya
apunta a `escenas/unitree_model` relativo a la raíz del repo.

---

## Requisitos

- Isaac Sim 5.1.0 instalado en `/home/udc/IsaacLab/`
- conda env `isaaclab` activo
- GPU con compute capability >= 8.9 (RTX 40xx, RTX 50xx)
- Para RTX 50xx: Isaac Sim >= 5.0.0 (ya cubierto con 5.1.0)
