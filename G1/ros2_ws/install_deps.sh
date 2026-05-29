#!/bin/bash
# Instalar dependencias ROS2 Jazzy para comunicación con G1
# Ejecutar UNA VEZ con: bash ros2_ws/install_deps.sh

set -e

echo "=== Instalando dependencias ROS2 Jazzy + CycloneDDS para G1 ==="

sudo apt update
sudo apt install -y \
    ros-jazzy-rmw-cyclonedds-cpp \
    ros-jazzy-rosidl-generator-dds-idl \
    libyaml-cpp-dev

echo ""
echo "✓ Dependencias instaladas."
echo ""
echo "Siguiente paso — compilar mensajes Unitree:"
echo "  bash ros2_ws/build_msgs.sh"
