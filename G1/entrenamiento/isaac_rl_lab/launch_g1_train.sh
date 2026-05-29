#!/bin/bash
# Entrenar política G1 con Isaac Lab (locomotion o imitación de movimiento)
# Uso: bash entrenamiento/isaac_rl_lab/launch_g1_train.sh [tarea]
# Ejecutar desde la raíz del repo: /home/udc/Unitree_G1
#
# Tareas disponibles:
#   velocity    → locomoción por velocidad (default)
#   dance       → imitación baile Dance-102 (BVH)
#   gangnam     → imitación Gangnam Style (BVH)

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
RL_LAB_DIR="$REPO_ROOT/entrenamiento/isaac_rl_lab"

TASK_ALIAS="${1:-velocity}"
HEADLESS="${2:---headless}"  # --headless por default, pasar "" para visor

case "$TASK_ALIAS" in
  velocity) TASK="Unitree-G1-29dof-Velocity" ;;
  dance)    TASK="Unitree-G1-29dof-Mimic-Dance-102" ;;
  gangnam)  TASK="Unitree-G1-29dof-Mimic-Gangnam-Style" ;;
  *)        TASK="$TASK_ALIAS" ;;
esac

echo "=== G1 Isaac Lab RL Training ==="
echo "Tarea: $TASK"
echo "Modo: ${HEADLESS:-(con visor)}"
echo ""

conda run -n isaaclab \
  python "$RL_LAB_DIR/scripts/rsl_rl/train.py" \
  --task "$TASK" \
  $HEADLESS
