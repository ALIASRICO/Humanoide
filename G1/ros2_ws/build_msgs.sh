#!/bin/bash
# Compilar mensajes Unitree (unitree_hg, unitree_go, unitree_api) para ROS2 Jazzy
# Ejecutar desde la raíz del repo: bash ros2_ws/build_msgs.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== Compilando mensajes Unitree para ROS2 Jazzy ==="

# Verificar que ros-jazzy-rmw-cyclonedds-cpp esté instalado
if ! dpkg -l ros-jazzy-rmw-cyclonedds-cpp 2>/dev/null | grep -q "^ii"; then
    echo "ERROR: ros-jazzy-rmw-cyclonedds-cpp no está instalado."
    echo "Ejecutar primero: bash ros2_ws/install_deps.sh"
    exit 1
fi

source /opt/ros/jazzy/setup.bash
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp

cd "$SCRIPT_DIR"
colcon build --packages-select unitree_hg unitree_go unitree_api

echo ""
echo "✓ Mensajes compilados en: ros2_ws/install/"
echo ""
echo "Para usar ROS2 con el robot G1 (conectado por cable):"
echo "  source ros2_ws/setup_g1.sh"
echo ""
echo "Para pruebas locales sin robot:"
echo "  source ros2_ws/setup_local.sh"
