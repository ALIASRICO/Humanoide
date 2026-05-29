#!/usr/bin/env bash
# setup_workspace.sh — clona Isaac Lab, crea conda env, prepara ros2_ws
set -euo pipefail

WORKSPACE=${WORKSPACE:-$HOME/r1_workspace}
mkdir -p "$WORKSPACE"
cd "$WORKSPACE"

echo "[1/5] Conda env env_isaaclab..."
if ! mamba env list | grep -q env_isaaclab; then
    mamba create -n env_isaaclab python=3.10 -y
fi
source $HOME/miniforge3/etc/profile.d/conda.sh
mamba activate env_isaaclab

echo "[2/5] PyTorch CUDA + Isaac Sim..."
pip install --upgrade pip
pip install torch==2.5.1 torchvision==0.20.1 --index-url https://download.pytorch.org/whl/cu121
pip install --extra-index-url https://pypi.nvidia.com isaacsim==4.5.0.0 \
    isaacsim-extscache-physics==4.5.0.0 \
    isaacsim-extscache-kit==4.5.0.0 \
    isaacsim-extscache-kit-sdk==4.5.0.0
pip install onnxruntime-gpu==1.18.0

echo "[3/5] Isaac Lab..."
if [ ! -d "$WORKSPACE/IsaacLab" ]; then
    git clone https://github.com/isaac-sim/IsaacLab.git "$WORKSPACE/IsaacLab"
fi
cd "$WORKSPACE/IsaacLab"
./isaaclab.sh --install

echo "[4/5] Extensión r1_standing..."
if [ ! -d "$WORKSPACE/r1_standing" ]; then
    git clone https://github.com/pandafter/r1_standing.git "$WORKSPACE/r1_standing"
fi
"$WORKSPACE/IsaacLab/isaaclab.sh" -p -m pip install -e "$WORKSPACE/r1_standing/source/r1_standing"

# Workspace space_r1 (asset r1.usd + play_wasd.py)
if [ ! -d "$WORKSPACE/space_r1" ]; then
    git clone https://github.com/pandafter/space_r1.git "$WORKSPACE/space_r1"
fi
mkdir -p "$WORKSPACE/IsaacLab/source/isaaclab_assets/data/Robots/Unitree/R1"
if [ -f "$WORKSPACE/space_r1/r1.usd" ]; then
    cp "$WORKSPACE/space_r1/r1.usd" \
       "$WORKSPACE/IsaacLab/source/isaaclab_assets/data/Robots/Unitree/R1/r1.usd"
fi

echo "[5/5] Workspace ROS2..."
mkdir -p "$WORKSPACE/ros2_ws/src"
cd "$WORKSPACE/ros2_ws"
source /opt/ros/humble/setup.bash
colcon build --symlink-install

if ! grep -q "ros2_ws/install/setup.bash" ~/.bashrc; then
    echo "source $WORKSPACE/ros2_ws/install/setup.bash" >> ~/.bashrc
fi

mkdir -p "$WORKSPACE/policies"
mkdir -p "$WORKSPACE/sdk"

echo ""
echo "=========================================================="
echo "  Workspace listo en $WORKSPACE"
echo "  Próximos pasos:"
echo "    1) Copiar paquetes ROS2 desde DocumentacionR1Completa:"
echo "       cp -r ~/DocumentacionR1Completa/Ubuntu_ROS2/codigos/ros2_ws/src/* \\"
echo "             $WORKSPACE/ros2_ws/src/"
echo "    2) Compilar:"
echo "       cd $WORKSPACE/ros2_ws && colcon build --symlink-install"
echo "    3) (Para deploy) clonar unitree_sdk2_python en $WORKSPACE/sdk/"
echo "=========================================================="
