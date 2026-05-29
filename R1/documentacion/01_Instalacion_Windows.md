# 01 — Instalación end-to-end en Windows

> Objetivo: dejar listo el entorno para entrenar y reproducir políticas del **Unitree R1** sobre **Isaac Sim + Isaac Lab + RSL-RL/SKRL**, partiendo de Windows 10/11 limpio.

---

## 1. Preparativos

### 1.1 Hardware

- GPU NVIDIA con ≥ **8 GB VRAM** (RTX 3060 = mínimo). El entorno por defecto crea **8000 envs en paralelo**; con menos VRAM bajar a `--num_envs 1024` o menos.
- ≥ **32 GB RAM**, ≥ **100 GB libres** en disco para `Isaac Sim` + caché + logs.
- CPU con AVX2 (cualquier i5/Ryzen5 de 2017 en adelante).

### 1.2 Drivers y CUDA

1. Driver NVIDIA ≥ **535** (verificar con `nvidia-smi`).
2. **CUDA Toolkit 12.1** o **12.4** desde [developer.nvidia.com/cuda-downloads](https://developer.nvidia.com/cuda-downloads).
3. Instalar **MS Visual C++ Build Tools 2022** (necesario para `pip install` de algunas deps de Isaac Lab).
4. **Git for Windows** ([git-scm.com](https://git-scm.com)).
5. **Anaconda** o **Miniconda** ([docs.anaconda.com/miniconda](https://docs.anaconda.com/miniconda)).

### 1.3 Variables de entorno (PowerShell, ejecutar como admin)

```powershell
[Environment]::SetEnvironmentVariable("CUDA_PATH", "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.1", "Machine")
[Environment]::SetEnvironmentVariable("PYTHONUTF8", "1", "User")
```

> Reiniciar la terminal después.

---

## 2. Estructura de directorios

Se recomienda fijarse a la convención del repo `space_r1`. Crear:

```
C:\space_r1\
 ├─ IsaacLab\           ← clon de NVIDIA-Omniverse/IsaacLab
 ├─ r1_standing\        ← clon de pandafter/r1_standing
 ├─ r1_locomotion\      ← extensión hermana (locomotion WASD)
 ├─ r1.usd              ← modelo del robot (asset)
 └─ play_wasd.py        ← control manual por terminal
```

> Si tu disco principal es chico, monta el árbol en `D:\space_r1\` y cambia las rutas. **No uses rutas con espacios o tildes** (Isaac Sim falla).

```powershell
New-Item -ItemType Directory -Path D:\space_r1
Set-Location D:\space_r1
```

---

## 3. Isaac Sim (Omniverse)

### Opción recomendada: Pip-install (Isaac Sim 4.5+ permite *headless* desde Python)

Crear el entorno conda:

```powershell
conda create -n env_isaaclab python=3.11 -y
conda activate env_isaaclab
```

Instalar PyTorch con CUDA 12.1:

```powershell
pip install torch==2.5.1 torchvision==0.20.1 --index-url https://download.pytorch.org/whl/cu121
```

Instalar Isaac Sim:

```powershell
pip install --upgrade pip
pip install --extra-index-url https://pypi.nvidia.com isaacsim==4.5.0.0 isaacsim-extscache-physics==4.5.0.0 isaacsim-extscache-kit==4.5.0.0 isaacsim-extscache-kit-sdk==4.5.0.0
```

> Si quieres GUI completa (Omniverse Launcher) descarga el instalador desde [developer.nvidia.com/isaac-sim](https://developer.nvidia.com/isaac-sim) y selecciona Isaac Sim 4.5/5.0. Documentación oficial: <https://docs.isaacsim.omniverse.nvidia.com>.

Verifica:

```powershell
python -c "import isaacsim; print(isaacsim.__version__)"
```

---

## 4. Isaac Lab

```powershell
Set-Location D:\space_r1
git clone https://github.com/isaac-sim/IsaacLab.git
Set-Location IsaacLab
git checkout main   # o un tag estable, p.ej. v2.1.0
```

Bootstrap (instala todas las deps en el conda activo):

```powershell
.\isaaclab.bat --install
```

> Esto puede tardar 10–20 minutos. Internamente corre `pip install -e source/isaaclab`, `source/isaaclab_assets`, `source/isaaclab_rl`, `source/isaaclab_tasks`, `source/isaaclab_mimic`.

Verifica:

```powershell
.\isaaclab.bat -p -c "from isaaclab.app import AppLauncher; print('OK')"
```

---

## 5. Clonar la extensión `r1_standing`

```powershell
Set-Location D:\space_r1
git clone https://github.com/pandafter/r1_standing.git
Set-Location r1_standing
```

Instálala en modo *editable* dentro del mismo conda env:

```powershell
python -m pip install -e .\source\r1_standing
```

> ⚠ Si `python` no apunta al intérprete de Isaac Lab, usa la ruta absoluta:
> `D:\space_r1\IsaacLab\isaaclab.bat -p -m pip install -e .\source\r1_standing`

---

## 6. Verificación

### 6.1 Listar tareas registradas

```powershell
.\..\IsaacLab\isaaclab.bat -p .\scripts\list_envs.py
```

> Debe imprimir una tabla con `R1Standing-Direct-v0`. Si no aparece, edita `scripts/list_envs.py` y cambia el filtro `"Template-"` por `"R1"` (ver [doc 10](./10_Correcciones_Aplicadas.md)).

### 6.2 Probar agente cero (no entrena, solo valida la simulación)

```powershell
.\..\IsaacLab\isaaclab.bat -p .\scripts\zero_agent.py --task=R1Standing-Direct-v0 --num_envs=4
```

Debe abrir Isaac Sim y mostrar al R1 manteniendo su pose default.

### 6.3 Probar agente random

```powershell
.\..\IsaacLab\isaaclab.bat -p .\scripts\random_agent.py --task=R1Standing-Direct-v0 --num_envs=4
```

El robot caerá y se reseteará — eso es lo esperado.

---

## 7. Asset `r1.usd`

`isaaclab_assets.robots.r1.R1_CFG` referencia internamente al USD del robot. Si tu instalación lo busca y no lo encuentra:

1. Copia `r1.usd` (que está en `space_r1/r1.usd`) a `D:\space_r1\IsaacLab\source\isaaclab_assets\data\Robots\Unitree\R1\r1.usd`.
2. Asegúrate que el `R1_CFG` apunte a esa ruta (`usd_path=`). Si no lo trae, ver [doc 08](./08_Mapa_Rutas_Importantes.md) — sección "Inyectar el USD del R1".

> ⚠ **Corrección importante**: Algunas versiones de `isaaclab_assets` no traen `R1_CFG`. Ver [doc 10 §3](./10_Correcciones_Aplicadas.md).

---

## 8. IDE (opcional, recomendado)

VSCode + extensión Python + Pylance:

1. Abrir `D:\space_r1\r1_standing` en VSCode.
2. `Ctrl+Shift+P` → `Tasks: Run Task` → `setup_python_env`.
3. Pegar la ruta absoluta a tu Isaac Sim (ej. `D:\Anaconda3\envs\env_isaaclab\Lib\site-packages\isaacsim`).
4. Esto crea `.vscode/.python.env` con todas las rutas de las extensiones de Isaac Sim.

`.vscode/settings.json` recomendado:

```json
{
  "python.defaultInterpreterPath": "D:\\Anaconda3\\envs\\env_isaaclab\\python.exe",
  "python.analysis.extraPaths": [
    "D:\\space_r1\\r1_standing\\source\\r1_standing"
  ]
}
```

---

## 9. Smoke test de entrenamiento (5 min)

```powershell
.\..\IsaacLab\isaaclab.bat -p .\scripts\rsl_rl\train.py `
  --task=R1Standing-Direct-v0 `
  --num_envs=64 `
  --max_iterations=50 `
  --headless
```

Si llega a iter 50 sin crash y ves `mean_reward` subiendo → la pila está OK.

---

## 10. Troubleshooting

| Síntoma | Causa probable | Fix |
|--------|---------------|-----|
| `ModuleNotFoundError: r1_standing` | No se hizo `pip install -e source/r1_standing`. | Reinstalar en editable. |
| Pylance no indexa Omni | Extensiones gigantes. | Comentar `omni.anim.*`, `omni.kit.*` en `python.analysis.extraPaths`. |
| `ImportError: cannot import name 'R1_CFG'` | El asset R1 no está en `isaaclab_assets` | Crear el `R1_CFG` localmente. Ver [doc 10](./10_Correcciones_Aplicadas.md). |
| `CUDA out of memory` | Demasiados envs. | Bajar `--num_envs`. |
| `instantaneous_wrench_composer` no existe | API obsoleta del *push system*. | Reemplazar por `set_external_force_and_torque`. Ver [doc 10 §1](./10_Correcciones_Aplicadas.md). |
| El robot vibra/cae al iter 0 | DT muy alto o action_scale exagerado. | `sim.dt = 1/120`, `action_scale = 0.025`. |
| Pre-commit falla | Falta toml. | `pip install pre-commit toml`. |

---

## 11. Resumen — Cheatsheet de instalación

```powershell
# (1) Conda env
conda create -n env_isaaclab python=3.11 -y
conda activate env_isaaclab

# (2) PyTorch CUDA
pip install torch==2.5.1 torchvision==0.20.1 --index-url https://download.pytorch.org/whl/cu121

# (3) Isaac Sim
pip install --extra-index-url https://pypi.nvidia.com isaacsim==4.5.0.0

# (4) Isaac Lab
git clone https://github.com/isaac-sim/IsaacLab.git D:\space_r1\IsaacLab
cd D:\space_r1\IsaacLab
.\isaaclab.bat --install

# (5) Extensión r1_standing
git clone https://github.com/pandafter/r1_standing.git D:\space_r1\r1_standing
cd D:\space_r1\r1_standing
python -m pip install -e .\source\r1_standing

# (6) Verificación
.\..\IsaacLab\isaaclab.bat -p .\scripts\list_envs.py
.\..\IsaacLab\isaaclab.bat -p .\scripts\zero_agent.py --task=R1Standing-Direct-v0 --num_envs=4
```

Próximo paso → [02_Crear_Politica_Basica.md](./02_Crear_Politica_Basica.md).
