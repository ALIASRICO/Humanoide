# 01 — Instalación de Ubuntu 22.04 (base para todo)

> Objetivo: dejar el SO listo para Isaac Sim/Lab + ROS2 Humble + entrenamiento RL + deploy. Asumiremos que partes de un equipo *vacío* (instalación limpia) o de un dual boot con Windows.

---

## 1. Pre-requisitos

- PC con **GPU NVIDIA** (mínimo RTX 3060, recomendado RTX 4070+ para 4096+ envs).
- ≥ 32 GB RAM, ≥ 200 GB libres en disco para Ubuntu (recomendado SSD NVMe).
- BIOS con **Secure Boot deshabilitado** (necesario para drivers NVIDIA propietarios sin firmas).
- Conexión a Internet por cable durante la instalación (Wi-Fi a veces requiere drivers extra).

---

## 2. Instalación de Ubuntu 22.04 LTS

> Por qué exactamente 22.04: ROS2 **Humble** solo soporta 22.04. Si usas 24.04 tendrás que ir a ROS2 Jazzy y muchas herramientas del ecosistema Isaac/Unitree aún no están portadas.

### 2.1 ISO y bootable USB

```bash
# Descargar la ISO
wget https://releases.ubuntu.com/22.04/ubuntu-22.04.5-desktop-amd64.iso
# Verificar SHA-256
sha256sum ubuntu-22.04.5-desktop-amd64.iso
# Comparar con la SHA del sitio oficial
```

Crear USB booteable con `dd` (Linux) o **Rufus / Balena Etcher** (Windows).

### 2.2 Particionado recomendado

| Mount | Tamaño | Tipo |
|-------|-------:|------|
| `/boot/efi` | 512 MB | EFI System |
| `/`         | 60 GB  | ext4 |
| `/home`     | resto  | ext4 (en SSD/NVMe) |
| `swap`      | 16 GB  | swap (o `/swapfile`) |

Si haces dual boot con Windows: **encoge la partición de Windows desde Windows** (Disk Management) antes de bootear el USB.

### 2.3 Tras la instalación

```bash
sudo apt update
sudo apt full-upgrade -y
sudo apt install -y build-essential cmake git curl wget vim htop tmux \
                    pkg-config libssl-dev libffi-dev python3-dev python3-pip \
                    net-tools openssh-server gdebi software-properties-common
```

Configurar SSH (importante para deploy en robot remoto):
```bash
sudo systemctl enable --now ssh
```

---

## 3. Drivers NVIDIA y CUDA

### 3.1 Driver NVIDIA

```bash
sudo apt install -y ubuntu-drivers-common
ubuntu-drivers devices               # ver el recomendado
sudo ubuntu-drivers autoinstall      # instalar el `recommended`
sudo reboot
```

Verifica:
```bash
nvidia-smi
```

> Debe mostrar Driver Version >= 535 y tu GPU. Si no, instala manual:
> ```bash
> sudo add-apt-repository ppa:graphics-drivers/ppa
> sudo apt update
> sudo apt install -y nvidia-driver-550
> ```

### 3.2 CUDA Toolkit 12.1

```bash
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo apt update
sudo apt install -y cuda-toolkit-12-1
```

`~/.bashrc`:
```bash
export PATH=/usr/local/cuda-12.1/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/cuda-12.1/lib64:$LD_LIBRARY_PATH
export CUDA_HOME=/usr/local/cuda-12.1
```

Verifica:
```bash
source ~/.bashrc
nvcc --version
```

### 3.3 cuDNN (necesario para `onnxruntime-gpu`)

```bash
sudo apt install -y libcudnn8 libcudnn8-dev
```

---

## 4. Conda / Miniforge

```bash
wget https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh
bash Miniforge3-Linux-x86_64.sh -b -p $HOME/miniforge3
echo 'export PATH="$HOME/miniforge3/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
mamba init bash
```

Crear el environment para Isaac Lab:
```bash
mamba create -n env_isaaclab python=3.10 -y
mamba activate env_isaaclab
```

PyTorch CUDA:
```bash
pip install torch==2.5.1 torchvision==0.20.1 \
    --index-url https://download.pytorch.org/whl/cu121
```

Verifica:
```bash
python -c "import torch; print(torch.cuda.is_available(), torch.cuda.get_device_name(0))"
```

---

## 5. Estructura de directorios

```bash
mkdir -p ~/r1_workspace/{IsaacLab,r1_standing,r1_locomotion,ros2_ws/src,policies}
cd ~/r1_workspace
```

> A diferencia de Windows, en Linux es perfectamente seguro tener todo bajo `~/` (sin permisos de admin).

---

## 6. Performance tweaks para entrenamiento

### 6.1 Powermizer NVIDIA — máximo rendimiento

```bash
sudo nvidia-smi -pm 1
sudo nvidia-smi --auto-boost-default=0
sudo nvidia-smi -pl 320     # ajustar al TDP de tu GPU
```

### 6.2 CPU governor performance

```bash
sudo apt install -y cpufrequtils
sudo cpupower frequency-set -g performance
```

Persistente en `/etc/default/cpufrequtils`:
```
GOVERNOR="performance"
```

### 6.3 Aumentar limits para muchos envs paralelos

`/etc/security/limits.conf`:
```
*    soft    nofile    65536
*    hard    nofile    65536
*    soft    nproc     65536
*    hard    nproc     65536
```

### 6.4 Swappiness bajo (más uso de RAM)

`/etc/sysctl.d/99-swappiness.conf`:
```
vm.swappiness=10
```

```bash
sudo sysctl -p /etc/sysctl.d/99-swappiness.conf
```

---

## 7. Ubuntu Real-Time (PREEMPT_RT) — solo si vas a controlar el robot real

Para **inference en el robot** con jitter < 1 ms, instala el kernel low-latency:

```bash
sudo apt install -y linux-lowlatency
sudo update-grub
sudo reboot
# Tras reboot:
uname -r          # debe terminar en -lowlatency
```

> Para latencia aún menor (< 100 µs) se necesita kernel con parches PREEMPT_RT compilado a mano. Ubuntu Pro lo trae preempaquetado (`Ubuntu Pro real-time kernel`) y es la opción recomendada para deploy serio.

---

## 8. Smoke test

```bash
nvidia-smi                      # GPU OK
nvcc --version                  # CUDA OK
python -c "import torch; print(torch.cuda.is_available())"
# True
gcc --version                   # build tools OK
git --version                   # git OK
```

Si todo OK → `next: 02_Isaac_Sim_Lab_Ubuntu.md`.

---

## 9. Script de instalación automática

Está empaquetado en [`codigos/scripts_bash/install_ubuntu_deps.sh`](./codigos/scripts_bash/install_ubuntu_deps.sh) — ejecutarlo automatiza pasos 2.3, 3, 4 y 5.

```bash
chmod +x codigos/scripts_bash/install_ubuntu_deps.sh
./codigos/scripts_bash/install_ubuntu_deps.sh
```

Próximo → [02_Isaac_Sim_Lab_Ubuntu.md](./02_Isaac_Sim_Lab_Ubuntu.md).
