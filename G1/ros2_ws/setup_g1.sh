#!/bin/bash
# Configurar entorno ROS2 Jazzy para comunicación con robot G1 físico
# Uso: source ros2_ws/setup_g1.sh [interfaz_red]
# Ejemplo: source ros2_ws/setup_g1.sh enp7s0

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
NETWORK_IF="${1:-enp7s0}"

echo "Setup ROS2 Jazzy + G1 (interfaz: $NETWORK_IF)"

source /opt/ros/jazzy/setup.bash
source "$REPO_ROOT/ros2_ws/install/setup.bash"

export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
export CYCLONEDDS_URI="<CycloneDDS><Domain><General><Interfaces>
                            <NetworkInterface name=\"$NETWORK_IF\" priority=\"default\" multicast=\"default\" />
                        </Interfaces></General></Domain></CycloneDDS>"

echo "✓ RMW: rmw_cyclonedds_cpp"
echo "✓ Interfaz: $NETWORK_IF"
echo ""
echo "Verificar topics del robot:"
echo "  ros2 topic list"
echo "  ros2 topic echo /lf/lowstate --field imu_state"
