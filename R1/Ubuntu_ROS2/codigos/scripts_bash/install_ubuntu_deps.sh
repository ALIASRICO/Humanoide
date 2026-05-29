#!/usr/bin/env bash
# install_ubuntu_deps.sh — preparación base de Ubuntu 22.04 para R1
# Uso: chmod +x install_ubuntu_deps.sh && ./install_ubuntu_deps.sh
set -euo pipefail

echo "[1/6] Apt update + tools básicos..."
sudo apt update
sudo apt full-upgrade -y
sudo apt install -y build-essential cmake git curl wget vim htop tmux \
                    pkg-config libssl-dev libffi-dev python3-dev python3-pip \
                    net-tools openssh-server software-properties-common \
                    cpufrequtils

echo "[2/6] SSH server..."
sudo systemctl enable --now ssh

echo "[3/6] Driver NVIDIA + CUDA 12.1..."
sudo apt install -y ubuntu-drivers-common
sudo ubuntu-drivers autoinstall

if ! command -v nvcc &>/dev/null; then
    cd /tmp
    wget -q https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.1-1_all.deb
    sudo dpkg -i cuda-keyring_1.1-1_all.deb
    sudo apt update
    sudo apt install -y cuda-toolkit-12-1 libcudnn8 libcudnn8-dev
fi

echo "[4/6] Variables de CUDA en .bashrc..."
grep -q 'cuda-12.1/bin' ~/.bashrc || cat >> ~/.bashrc << 'EOF'

# CUDA 12.1
export PATH=/usr/local/cuda-12.1/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/cuda-12.1/lib64:$LD_LIBRARY_PATH
export CUDA_HOME=/usr/local/cuda-12.1
EOF

echo "[5/6] Miniforge + conda env..."
if [ ! -d "$HOME/miniforge3" ]; then
    cd /tmp
    wget -q https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh
    bash Miniforge3-Linux-x86_64.sh -b -p $HOME/miniforge3
    grep -q 'miniforge3/bin' ~/.bashrc || \
        echo 'export PATH="$HOME/miniforge3/bin:$PATH"' >> ~/.bashrc
fi

echo "[6/6] Performance tweaks..."
sudo nvidia-smi -pm 1 || true
sudo cpupower frequency-set -g performance || true

# limits
if ! grep -q "nofile    65536" /etc/security/limits.conf; then
    sudo tee -a /etc/security/limits.conf > /dev/null <<EOF
*    soft    nofile    65536
*    hard    nofile    65536
*    soft    nproc     65536
*    hard    nproc     65536
EOF
fi

# swappiness
echo "vm.swappiness=10" | sudo tee /etc/sysctl.d/99-swappiness.conf > /dev/null
sudo sysctl -p /etc/sysctl.d/99-swappiness.conf

echo ""
echo "=========================================================="
echo "  Instalación base completa."
echo "  Reinicia (sudo reboot), luego ejecuta:"
echo "    bash install_ros2_humble.sh"
echo "    bash setup_workspace.sh"
echo "=========================================================="
