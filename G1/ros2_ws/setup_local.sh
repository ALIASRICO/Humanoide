#!/bin/bash
# Configurar entorno ROS2 Jazzy para pruebas locales (sin robot físico, loopback)
# Uso: source ros2_ws/setup_local.sh

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "Setup ROS2 Jazzy + G1 (modo local, sin robot)"

source /opt/ros/jazzy/setup.bash
source "$REPO_ROOT/ros2_ws/install/setup.bash"

export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
export CYCLONEDDS_URI='<CycloneDDS><Domain><General><Interfaces>
                            <NetworkInterface name="lo" priority="default" multicast="default" />
                        </Interfaces></General></Domain></CycloneDDS>'

echo "✓ RMW: rmw_cyclonedds_cpp (loopback)"
