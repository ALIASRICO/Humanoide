#!/bin/bash
# Monitorear estado del robot G1 vía ROS2 + CycloneDDS
# Uso: bash ros2_ws/monitor_g1.sh [interfaz_red]
# Ejemplo: bash ros2_ws/monitor_g1.sh enp7s0

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
NETWORK_IF="${1:-enp7s0}"

if [ ! -f "$REPO_ROOT/ros2_ws/install/setup.bash" ]; then
    echo "ERROR: Mensajes no compilados. Ejecutar: bash ros2_ws/build_msgs.sh"
    exit 1
fi

source /opt/ros/jazzy/setup.bash
source "$REPO_ROOT/ros2_ws/install/setup.bash"
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
export CYCLONEDDS_URI="<CycloneDDS><Domain><General><Interfaces>
                            <NetworkInterface name=\"$NETWORK_IF\" priority=\"default\" multicast=\"default\" />
                        </Interfaces></General></Domain></CycloneDDS>"

echo "=== G1 ROS2 Monitor (Jazzy + CycloneDDS) ==="
echo "Interfaz: $NETWORK_IF"
echo ""
echo "Topics disponibles:"
ros2 topic list 2>/dev/null
echo ""
echo "── IMU (presiona Ctrl+C para salir) ──"
ros2 topic echo /lf/lowstate --field imu_state 2>/dev/null
