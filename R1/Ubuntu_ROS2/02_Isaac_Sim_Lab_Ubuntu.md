# 02 — Isaac Sim + Isaac Lab en Ubuntu

> Misma stack que Windows pero con instalador nativo Linux. Sigue el flujo: Isaac Sim → Isaac Lab → extensión `r1_standing`/`r1_locomotion`.

---

## 1. Isaac Sim (modo pip — recomendado para training)

Activa el conda env primero:

```bash
mamba activate env_isaaclab
```

Instala Isaac Sim:

```bash
pip install --upgrade pip
pip install --extra-index-url https://pypi.nvidia.com \
    isaacsim==4.5.0.0 \
    isaacsim-extscache-physics==4.5.0.0 \
    isaacsim-extscache-kit==4.5.0.0 \
    isaacsim-extscache-kit-sdk==4.5.0.0
```

Primer launch (descarga assets en `~/.local/share/ov/...`):

```bash
isaacsim
```

> Cierra la ventana cuando se cargue. La cache queda persistente.

### Alternativa: Omniverse Launcher (GUI completa, más pesada)

```bash
wget https://install.launcher.omniverse.nvidia.com/installers/omniverse-launcher-linux.AppImage
chmod +x omniverse-launcher-linux.AppImage
./omniverse-launcher-linux.AppImage
```

Desde el Launcher: instalar **Isaac Sim 4.5+**.

---

## 2. Isaac Lab

```bash
cd ~/r1_workspace
git clone https://github.com/isaac-sim/IsaacLab.git
cd IsaacLab
git checkout main      # o un tag estable
./isaaclab.sh --install
```

> Esto corre `pip install -e source/isaaclab[all]` y todas las hermanas. Tarda 10–20 min.

Verifica:

```bash
./isaaclab.sh -p -c "from isaaclab.app import AppLauncher; print('OK')"
```

---

## 3. Extensiones del proyecto

```bash
cd ~/r1_workspace
git clone https://github.com/pandafter/r1_standing.git
git clone https://github.com/pandafter/space_r1.git    # opcional, contiene play_wasd.py + r1.usd
```

Instalar la extensión en el conda env:

```bash
cd ~/r1_workspace/r1_standing
~/r1_workspace/IsaacLab/isaaclab.sh -p -m pip install -e ./source/r1_standing
```

> **Importante**: usa `isaaclab.sh -p` (no `python` directo) para que el editable install se haga en el intérprete correcto que usa Isaac Lab.

### Asset r1.usd

Copia el USD a la ruta canónica:

```bash
mkdir -p ~/r1_workspace/IsaacLab/source/isaaclab_assets/data/Robots/Unitree/R1
cp ~/r1_workspace/space_r1/r1.usd \
   ~/r1_workspace/IsaacLab/source/isaaclab_assets/data/Robots/Unitree/R1/r1.usd
```

> Si tu copia de `isaaclab_assets` ya trae `R1_CFG`, este paso es opcional pero recomendado para que sea autocontenido.

---

## 4. Verificación

```bash
cd ~/r1_workspace/r1_standing
~/r1_workspace/IsaacLab/isaaclab.sh -p ./scripts/list_envs.py
```

Debe imprimir:
```
+------+----------------------------+...
| Task Name                          |
+------+----------------------------+
| R1Standing-Direct-v0               |
| R1-Locomotion-Direct-v0            |
| ...                                |
```

> Si no aparece nada, edita `scripts/list_envs.py` y cambia el filtro de `"Template-"` a `"R1"` (corrección documentada en [doc 10 §2 Windows](../10_Correcciones_Aplicadas.md)). Hay un script ya corregido en [`codigos/scripts/list_envs.py`](../codigos/scripts/list_envs.py) — copiarlo encima.

---

## 5. Smoke test rápido

```bash
~/r1_workspace/IsaacLab/isaaclab.sh -p ./scripts/zero_agent.py \
    --task=R1Standing-Direct-v0 --num_envs=4
```

Abre Isaac Sim y muestra al R1 manteniendo su pose default. Para entrenar:

```bash
~/r1_workspace/IsaacLab/isaaclab.sh -p ./scripts/rsl_rl/train.py \
    --task=R1Standing-Direct-v0 --num_envs=4096 --max_iterations=4000 --headless
```

Ventajas de Linux respecto a Windows:

- Headless 100% offscreen (no abre ventana siquiera) → ~25% más velocidad.
- Multi-GPU con `torchrun` funciona "out of the box".
- Logs en `logs/rsl_rl/r1_standing/<timestamp>/` (equivalente a Windows).

---

## 6. Multi-GPU con torchrun

```bash
torchrun --nproc_per_node=2 ./scripts/rsl_rl/train.py \
    --task=R1Standing-Direct-v0 \
    --num_envs=8192 \
    --max_iterations=8000 \
    --distributed --headless
```

`--nproc_per_node` = nº GPUs. Cada una entrena `num_envs` envs en paralelo.

---

## 7. TensorBoard

```bash
tensorboard --logdir ~/r1_workspace/r1_standing/logs/rsl_rl --bind_all
```

Acceder desde otro equipo: `http://<ip-ubuntu>:6006`.

---

## 8. Diferencias respecto a Windows

| Aspecto | Windows | Ubuntu |
|---------|---------|--------|
| Entry-point | `isaaclab.bat` | `isaaclab.sh` |
| Path separator | `\` | `/` |
| Conda activate | `conda activate env_isaaclab` | `mamba activate env_isaaclab` |
| Velocidad | 100% | 125–140% |
| `play_wasd.py` (msvcrt) | sí | **NO** — usar versión con `tty/select` (ver [doc 08](./08_Nodos_ROS2_Inferencia.md)) |
| Ctrl+C handling | OK | OK |
| GPU | un solo proceso | multi-GPU con `torchrun` |

---

## 9. Anti-patrones específicos de Ubuntu

- **No instalar Isaac Sim como root** (`sudo pip install`). Quedan permisos rotos en `~/.local/share/ov`.
- **No mezclar pip con apt-installed Python** — siempre usar el conda env.
- **No olvidar `./isaaclab.sh -p`** cuando instales paquetes editables (sin esto van al python global).
- **Wayland**: si la GUI de Isaac Sim no abre, cambia a sesión X11 (login screen → engranaje → "Ubuntu on Xorg"). Wayland aún no es 100% compatible con Omni.

Próximo → [03_ROS2_Humble_Setup.md](./03_ROS2_Humble_Setup.md).
