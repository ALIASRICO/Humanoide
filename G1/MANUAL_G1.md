# MANUAL G1 — Index & Quick Reference / Índice y Referencia Rápida

[🇬🇧 English](#english) | [🇪🇸 Español](#español)

**Repository:** `/home/udc/Humanoide/G1` | **Updated:** 2026-05-29

---

<a name="english"></a>
## 🇬🇧 English

This file is a navigation hub and quick-reference card. Full details are in each module's README.

### Documentation Map

| Module | README | Description |
|--------|--------|-------------|
| G1 Overview | [README.md](README.md) | Quick start, environments, hardware |
| Simulation (overview) | [simulacion/README.md](simulacion/README.md) | Isaac Sim vs MuJoCo comparison |
| Isaac Sim | [simulacion/isaac_sim/README.md](simulacion/isaac_sim/README.md) | 14 scenes, keyboard control, camera viewer |
| MuJoCo sdk_bridge | [simulacion/sdk_bridge/README.md](simulacion/sdk_bridge/README.md) | DDS bridge for deploy testing |
| Training | [entrenamiento/README.md](entrenamiento/README.md) | HumanoidVerse + Isaac RL Lab |
| Deployment | [despliegue/README.md](despliegue/README.md) | Physical robot, safety, configs |
| Policies | [politicas/README.md](politicas/README.md) | All .pt files, obs dims, DOF |
| Code modules | [codigos/README.md](codigos/README.md) | Imitation, LiDAR, teleop, vision |
| Imitation learning | [codigos/imitacion/README.md](codigos/imitacion/README.md) | LeRobot pipeline |
| Teleoperation | [codigos/teleoperacion/README.md](codigos/teleoperacion/README.md) | Arm IK + episode recording |
| Tools | [../herramientas/README.md](../herramientas/README.md) | Model conversion scripts |

### Quick Reference Card

```bash
# ── ENVIRONMENTS ─────────────────────────────────────────────────────────────
conda activate /home/udc/Humanoide/G1/envs/g1_udc   # MuJoCo, deploy, SDK
conda activate hgen                                   # HumanoidVerse training
conda activate isaaclab                               # Isaac Sim

# ── DDS VARIABLES (required for any DDS script) ───────────────────────────────
export LD_LIBRARY_PATH="/home/udc/Humanoide/humanoide/cyclonedds/install/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export CYCLONEDDS_URI='<CycloneDDS><Domain id="any"><SharedMemory><Enable>false</Enable></SharedMemory></Domain></CycloneDDS>'

# ── ISAAC SIM ─────────────────────────────────────────────────────────────────
bash simulacion/isaac_sim/launch_g1.sh cylinder_dex1        # launch scene
python simulacion/isaac_sim/teleimager/image_client.py --host localhost  # camera viewer
python simulacion/isaac_sim/send_commands_keyboard.py        # keyboard control (separate terminal)
pkill -9 -f "sim_main.py"                                   # force close

# ── MUJOCO SDK BRIDGE ─────────────────────────────────────────────────────────
python simulacion/sdk_bridge/run_g1_bridge.py                # Terminal 1
python despliegue/deploy_motion.py lo motion_agacharse.yaml  # Terminal 2

# ── DIRECT MUJOCO (no DDS) ────────────────────────────────────────────────────
python simulacion/sim_motion_policies.py motion_agacharse.yaml
python simulacion/sim_hv.py g1_hv.yaml

# ── DEPLOY TO PHYSICAL ROBOT ──────────────────────────────────────────────────
python despliegue/deploy_motion.py enp7s0 motion_agacharse.yaml
python despliegue/deploy_motion.py enp7s0 motion_munecas.yaml
python despliegue/deploy_dual.py   enp7s0 g1_hv.yaml

# ── TRAINING ─────────────────────────────────────────────────────────────────
conda activate hgen && cd entrenamiento
bash train_agacharse_v10.sh
tensorboard --logdir logs/

# ── EXPORT POLICY ─────────────────────────────────────────────────────────────
python export_motion_policy.py logs/G1_Motion_DR/.../model_6000.pt ../politicas/out.pt

# ── ROS2 / LIDAR ──────────────────────────────────────────────────────────────
source ros2_ws/setup_g1.sh enp7s0
bash codigos/lidar/launch_g1_lidar.sh enp7s0
```

### Troubleshooting Quick Reference

| Problem | Solution |
|---------|----------|
| `dds_write.c:318` assertion crash | Export DDS variables — LD_LIBRARY_PATH + CYCLONEDDS_URI |
| Isaac Sim cameras not working | Edit `simulacion/cam_config_server.yaml` (NOT the one in `isaac_sim/`) |
| Isaac Sim hangs / won't close | `pkill -9 -f "sim_main.py"` |
| First Isaac Sim launch takes 5 min | Normal — GPU shader compilation. Do not close. |
| Robot falls in MuJoCo in <1 second | Obs vector order must be ALPHABETICAL, not YAML order |
| Actions 100% saturated in MuJoCo | kp too high for MuJoCo — use 5–25x lower than IsaacGym values |
| Erratic robot at deploy activation | Disable `sport_mode` from Unitree app first |
| No DDS topics visible | Check `ping 192.168.123.161` and `enp7s0` interface |
| `ModuleNotFoundError: humanoidverse` | `pip install -e entrenamiento/` in hgen env |
| Camera client shows nothing | Isaac Sim image server not started yet — wait for full boot |

---

<a name="español"></a>
## 🇪🇸 Español

Este archivo es un centro de navegación y tarjeta de referencia rápida. Los detalles completos están en el README de cada módulo.

### Mapa de Documentación

| Módulo | README | Descripción |
|--------|--------|-------------|
| Resumen G1 | [README.md](README.md) | Inicio rápido, entornos, hardware |
| Simulación (resumen) | [simulacion/README.md](simulacion/README.md) | Comparativa Isaac Sim vs MuJoCo |
| Isaac Sim | [simulacion/isaac_sim/README.md](simulacion/isaac_sim/README.md) | 14 escenas, teclado, visor cámaras |
| MuJoCo sdk_bridge | [simulacion/sdk_bridge/README.md](simulacion/sdk_bridge/README.md) | Bridge DDS para test de deploy |
| Entrenamiento | [entrenamiento/README.md](entrenamiento/README.md) | HumanoidVerse + Isaac RL Lab |
| Despliegue | [despliegue/README.md](despliegue/README.md) | Robot físico, seguridad, configs |
| Políticas | [politicas/README.md](politicas/README.md) | Todos los .pt, obs dims, DOF |
| Módulos de código | [codigos/README.md](codigos/README.md) | Imitación, LiDAR, teleop, visión |
| Imitation learning | [codigos/imitacion/README.md](codigos/imitacion/README.md) | Pipeline LeRobot |
| Teleoperación | [codigos/teleoperacion/README.md](codigos/teleoperacion/README.md) | IK brazos + grabación de episodios |
| Herramientas | [../herramientas/README.md](../herramientas/README.md) | Scripts de conversión de modelos |

### Tarjeta de Referencia Rápida

```bash
# ── ENTORNOS ──────────────────────────────────────────────────────────────────
conda activate /home/udc/Humanoide/G1/envs/g1_udc   # MuJoCo, despliegue, SDK
conda activate hgen                                   # Entrenamiento HumanoidVerse
conda activate isaaclab                               # Isaac Sim

# ── VARIABLES DDS (obligatorias para cualquier script DDS) ───────────────────
export LD_LIBRARY_PATH="/home/udc/Humanoide/humanoide/cyclonedds/install/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export CYCLONEDDS_URI='<CycloneDDS><Domain id="any"><SharedMemory><Enable>false</Enable></SharedMemory></Domain></CycloneDDS>'

# ── ISAAC SIM ─────────────────────────────────────────────────────────────────
bash simulacion/isaac_sim/launch_g1.sh cylinder_dex1        # lanzar escena
python simulacion/isaac_sim/teleimager/image_client.py --host localhost  # visor cámaras
python simulacion/isaac_sim/send_commands_keyboard.py        # teclado (terminal separada)
pkill -9 -f "sim_main.py"                                   # forzar cierre

# ── MUJOCO SDK BRIDGE ─────────────────────────────────────────────────────────
python simulacion/sdk_bridge/run_g1_bridge.py                # Terminal 1
python despliegue/deploy_motion.py lo motion_agacharse.yaml  # Terminal 2

# ── MUJOCO DIRECTO (sin DDS) ──────────────────────────────────────────────────
python simulacion/sim_motion_policies.py motion_agacharse.yaml
python simulacion/sim_hv.py g1_hv.yaml

# ── DESPLIEGUE EN ROBOT FÍSICO ────────────────────────────────────────────────
python despliegue/deploy_motion.py enp7s0 motion_agacharse.yaml
python despliegue/deploy_motion.py enp7s0 motion_munecas.yaml
python despliegue/deploy_dual.py   enp7s0 g1_hv.yaml

# ── ENTRENAMIENTO ─────────────────────────────────────────────────────────────
conda activate hgen && cd entrenamiento
bash train_agacharse_v10.sh
tensorboard --logdir logs/

# ── EXPORTAR POLÍTICA ─────────────────────────────────────────────────────────
python export_motion_policy.py logs/G1_Motion_DR/.../model_6000.pt ../politicas/out.pt

# ── ROS2 / LIDAR ──────────────────────────────────────────────────────────────
source ros2_ws/setup_g1.sh enp7s0
bash codigos/lidar/launch_g1_lidar.sh enp7s0
```

### Referencia Rápida de Problemas

| Problema | Solución |
|----------|----------|
| Crash con aserción `dds_write.c:318` | Exportar variables DDS — LD_LIBRARY_PATH + CYCLONEDDS_URI |
| Cámaras de Isaac Sim no funcionan | Editar `simulacion/cam_config_server.yaml` (NO el que está en `isaac_sim/`) |
| Isaac Sim colgado / no cierra | `pkill -9 -f "sim_main.py"` |
| Primera ejecución de Isaac Sim tarda 5 min | Normal — compilación de shaders GPU. No cerrar. |
| Robot cae en MuJoCo en <1 segundo | El orden del vector obs debe ser ALFABÉTICO, no el orden del YAML |
| Acciones 100% saturadas en MuJoCo | kp demasiado alto para MuJoCo — usar 5–25x menor que en IsaacGym |
| Robot errático al activar en despliegue | Apagar `sport_mode` desde la app Unitree primero |
| No se ven topics DDS | Verificar `ping 192.168.123.161` e interfaz `enp7s0` |
| `ModuleNotFoundError: humanoidverse` | `pip install -e entrenamiento/` en entorno hgen |
| Visor de cámaras no muestra nada | El servidor de imágenes de Isaac Sim aún no arrancó — esperar el boot completo |
