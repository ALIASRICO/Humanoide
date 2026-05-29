#!/bin/bash
# Lanzar simulación G1 en Isaac Sim
# Uso: bash simulacion/isaac_sim/launch_g1.sh [tarea] [mano] [accion]
# Ejecutar desde la raíz del repo: /home/udc/Unitree_G1
#
# ── PICK & PLACE ──────────────────────────────────────────────────────────────
#   cylinder_dex1       → Isaac-PickPlace-Cylinder-G129-Dex1-Joint    (default)
#   cylinder_dex3       → Isaac-PickPlace-Cylinder-G129-Dex3-Joint
#   cylinder_inspire    → Isaac-PickPlace-Cylinder-G129-Inspire-Joint
#   redblock_dex1       → Isaac-PickPlace-RedBlock-G129-Dex1-Joint
#   redblock_dex3       → Isaac-PickPlace-RedBlock-G129-Dex3-Joint
#   redblock_inspire    → Isaac-PickPlace-RedBlock-G129-Inspire-Joint
#
# ── STACK BLOQUES R/G/Y ────────────────────────────────────────────────────────
#   stack_dex1          → Isaac-Stack-RgyBlock-G129-Dex1-Joint
#   stack_dex3          → Isaac-Stack-RgyBlock-G129-Dex3-Joint
#   stack_inspire       → Isaac-Stack-RgyBlock-G129-Inspire-Joint
#
# ── METER EN CAJON ────────────────────────────────────────────────────────────
#   drawer_dex1         → Isaac-Pick-Redblock-Into-Drawer-G129-Dex1-Joint
#   drawer_dex3         → Isaac-Pick-Redblock-Into-Drawer-G129-Dex3-Joint
#
# ── MOVER CILINDRO (cuerpo completo, 29-DOF) ──────────────────────────────────
#   move_dex1           → Isaac-Move-Cylinder-G129-Dex1-Wholebody
#   move_dex3           → Isaac-Move-Cylinder-G129-Dex3-Wholebody
#   move_inspire        → Isaac-Move-Cylinder-G129-Inspire-Wholebody
#
# ── FUENTE DE ACCION (opcional, 3er argumento) ────────────────────────────────
#   dds       → control externo por DDS (default, igual que el robot real)
#   replay    → reproducir episodio grabado
#   keyboard  → teclado (solo pruebas)
#
# EJEMPLO:
#   bash simulacion/isaac_sim/launch_g1.sh redblock_dex1
#   bash simulacion/isaac_sim/launch_g1.sh drawer_dex3 replay
#   bash simulacion/isaac_sim/launch_g1.sh move_dex1

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ISAAC_SIM_DIR="$REPO_ROOT/simulacion/isaac_sim"

TASK_ALIAS="${1:-cylinder_dex1}"
ACTION_SOURCE="${2:-dds}"

# Determinar mano y flag DDS según tarea
case "$TASK_ALIAS" in
  # Pick & place — cilindro
  cylinder_dex1)        TASK="Isaac-PickPlace-Cylinder-G129-Dex1-Joint";   HAND="--enable_dex1_dds" ;;
  cylinder_dex3)        TASK="Isaac-PickPlace-Cylinder-G129-Dex3-Joint";   HAND="--enable_dex3_dds" ;;
  cylinder_inspire)     TASK="Isaac-PickPlace-Cylinder-G129-Inspire-Joint";HAND="--enable_inspire_dds" ;;
  # Pick & place — bloque rojo
  redblock_dex1)        TASK="Isaac-PickPlace-RedBlock-G129-Dex1-Joint";   HAND="--enable_dex1_dds" ;;
  redblock_dex3)        TASK="Isaac-PickPlace-RedBlock-G129-Dex3-Joint";   HAND="--enable_dex3_dds" ;;
  redblock_inspire)     TASK="Isaac-PickPlace-RedBlock-G129-Inspire-Joint";HAND="--enable_inspire_dds" ;;
  # Stack bloques R/G/Y
  stack_dex1)           TASK="Isaac-Stack-RgyBlock-G129-Dex1-Joint";       HAND="--enable_dex1_dds" ;;
  stack_dex3)           TASK="Isaac-Stack-RgyBlock-G129-Dex3-Joint";       HAND="--enable_dex3_dds" ;;
  stack_inspire)        TASK="Isaac-Stack-RgyBlock-G129-Inspire-Joint";    HAND="--enable_inspire_dds" ;;
  # Meter bloque en cajón
  drawer_dex1)          TASK="Isaac-Pick-Redblock-Into-Drawer-G129-Dex1-Joint"; HAND="--enable_dex1_dds" ;;
  drawer_dex3)          TASK="Isaac-Pick-Redblock-Into-Drawer-G129-Dex3-Joint"; HAND="--enable_dex3_dds" ;;
  # Mover cilindro — cuerpo completo 29-DOF
  move_dex1)            TASK="Isaac-Move-Cylinder-G129-Dex1-Wholebody";    HAND="--enable_dex1_dds" ;;
  move_dex3)            TASK="Isaac-Move-Cylinder-G129-Dex3-Wholebody";    HAND="--enable_dex3_dds" ;;
  move_inspire)         TASK="Isaac-Move-Cylinder-G129-Inspire-Wholebody"; HAND="--enable_inspire_dds" ;;
  # Nombre completo directo
  *)                    TASK="$TASK_ALIAS"; HAND="--enable_dex1_dds" ;;
esac

echo "=== G1 Isaac Sim ==="
echo "Tarea:        $TASK"
echo "Accion:       $ACTION_SOURCE"
echo "Entorno:      isaaclab"
echo ""
echo "NOTA: Primera ejecución tarda ~5 min (compilación de shaders)."
echo "NOTA RTX 50xx: Isaac Sim >= 5.0.0 requerido (instalado: 5.1.0)"
echo ""

export PYTHONPATH="$ISAAC_SIM_DIR${PYTHONPATH:+:$PYTHONPATH}"

# Activar entorno directamente para ver stdout/stderr en tiempo real
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate isaaclab

# Usar CycloneDDS local (iceoryx-free) para evitar el crash de aserción
# dds_write.c:318 cuando no hay RouDi corriendo
CYCLONEDDS_NO_IOX_LIB="/home/udc/Humanoide/humanoide/cyclonedds/install/lib"
export LD_LIBRARY_PATH="${CYCLONEDDS_NO_IOX_LIB}${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export CYCLONEDDS_URI='<CycloneDDS><Domain id="any"><SharedMemory><Enable>false</Enable></SharedMemory></Domain></CycloneDDS>'

python "$ISAAC_SIM_DIR/sim_main.py" \
  --task "$TASK" \
  --action_source "$ACTION_SOURCE" \
  --enable_cameras \
  $HAND \
  --robot_type g129
