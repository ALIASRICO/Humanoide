#!/usr/bin/env bash
# install_ros2_humble.sh — instala ROS2 Humble + deps del R1
set -euo pipefail

echo "[1/4] Locale UTF-8..."
sudo apt install -y locales
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8

echo "[2/4] Repo ROS2 Humble..."
sudo apt install -y software-properties-common curl
sudo add-apt-repository universe -y
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key \
    -o /usr/share/keyrings/ros-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] \
http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | \
    sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null

echo "[3/4] Paquetes ROS2 + dev tools..."
sudo apt update
sudo apt install -y \
    ros-humble-desktop \
    ros-dev-tools \
    ros-humble-rmw-fastrtps-cpp \
    ros-humble-rmw-cyclonedds-cpp \
    ros-humble-tf2 ros-humble-tf2-ros ros-humble-tf2-tools \
    ros-humble-controller-manager ros-humble-ros2-control ros-humble-ros2-controllers \
    ros-humble-joint-state-publisher ros-humble-joint-state-publisher-gui \
    ros-humble-xacro ros-humble-robot-state-publisher \
    ros-humble-rqt ros-humble-rqt-graph ros-humble-rqt-tf-tree ros-humble-rqt-plot \
    ros-humble-rviz2 ros-humble-rqt-robot-monitor \
    python3-colcon-common-extensions python3-rosdep python3-vcstool

echo "[4/4] rosdep init..."
sudo rosdep init || true
rosdep update

# .bashrc
if ! grep -q "/opt/ros/humble/setup.bash" ~/.bashrc; then
    cat >> ~/.bashrc << 'EOF'

# ROS2 Humble
source /opt/ros/humble/setup.bash
export ROS_DOMAIN_ID=42
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
EOF
fi

echo ""
echo "=========================================================="
echo "  ROS2 Humble instalado."
echo "  Abrir nuevo terminal y verificar:"
echo "    ros2 doctor"
echo "    ros2 run demo_nodes_cpp talker"
echo "=========================================================="
