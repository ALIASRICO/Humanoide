#!/bin/bash
# Reproducir política G1 entrenada con Isaac Lab (con visor)
# Uso: bash entrenamiento/isaac_rl_lab/launch_g1_play.sh [tarea] [checkpoint]
# Ejemplo: bash entrenamiento/isaac_rl_lab/launch_g1_play.sh velocity

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
RL_LAB_DIR="$REPO_ROOT/entrenamiento/isaac_rl_lab"

TASK_ALIAS="${1:-velocity}"
CHECKPOINT="${2:-}"  # opcional: ruta al .pt

case "$TASK_ALIAS" in
  velocity) TASK="Unitree-G1-29dof-Velocity" ;;
  dance)    TASK="Unitree-G1-29dof-Mimic-Dance-102" ;;
  gangnam)  TASK="Unitree-G1-29dof-Mimic-Gangnam-Style" ;;
  *)        TASK="$TASK_ALIAS" ;;
esac

CHECKPOINT_ARG=""
[ -n "$CHECKPOINT" ] && CHECKPOINT_ARG="--checkpoint $CHECKPOINT"

echo "=== G1 Isaac Lab Play ==="
echo "Tarea: $TASK"
[ -n "$CHECKPOINT" ] && echo "Checkpoint: $CHECKPOINT"
echo ""

conda run -n isaaclab \
  python "$RL_LAB_DIR/scripts/rsl_rl/play.py" \
  --task "$TASK" \
  $CHECKPOINT_ARG
