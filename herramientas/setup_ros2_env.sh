#!/bin/bash
# Configura el entorno ROS2 para LIDAR

echo "Configurando entorno ROS2 para LIDAR..."

if [ -z "$ROS_DISTRO" ]; then
    if [ -f "/opt/ros/humble/setup.bash" ]; then
        source /opt/ros/humble/setup.bash
        echo "[OK] ROS2 Humble sourceado"
    else
        echo "[ERROR] No se encontró ROS2 Humble en /opt/ros/humble"
        exit 1
    fi
else
    echo "[OK] ROS2 ya está sourceado ($ROS_DISTRO)"
fi

echo "[INFO] Dominio ROS: ${ROS_DOMAIN_ID:-0}"
echo "[INFO] Topics disponibles:"
ros2 topic list 2>/dev/null || echo "  (Isaac Sim no está corriendo aún)"

echo ""
echo "Entorno listo. Ahora puedes:"
echo "  1. Lanzar Isaac Sim: python3 codigos/isaac_amo_runtime_lidar.py"
echo "  2. Lanzar RViz2: rviz2 -d codigos/lidar_config.rviz"
echo "  3. Monitorear topics: python3 codigos/monitor_lidar.py"
