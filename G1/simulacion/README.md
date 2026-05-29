# Simulation / Simulación — G1

[🇬🇧 English](#english) | [🇪🇸 Español](#español)

---

<a name="english"></a>
## 🇬🇧 English

Two simulation options are available for validating G1 policies before running on the physical robot.

### Simulation Options

| Feature | Isaac Sim | MuJoCo sdk_bridge |
|---------|-----------|-------------------|
| Purpose | Manipulation tasks (pick & place, stacking) | Sim-to-sim policy validation + deploy test |
| Interface | Visual, photorealistic | Lightweight, headless capable |
| DDS | Same as real robot | Same as real robot |
| Environment | `isaaclab` | `g1_udc` |
| Launch | `launch_g1.sh` | `run_g1_bridge.py` |
| Guide | [isaac_sim/README.md](isaac_sim/README.md) | [sdk_bridge/README.md](sdk_bridge/README.md) |

### Isaac Sim — Manipulation

```bash
conda activate isaaclab
cd /home/udc/Humanoide/G1
bash simulacion/isaac_sim/launch_g1.sh cylinder_dex1
```

See [isaac_sim/README.md](isaac_sim/README.md) for all 14 scene aliases.

### MuJoCo — Policy Validation (no robot needed)

**Terminal 1 — Start MuJoCo bridge:**
```bash
conda activate /home/udc/Humanoide/G1/envs/g1_udc
export LD_LIBRARY_PATH="/home/udc/Humanoide/humanoide/cyclonedds/install/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export CYCLONEDDS_URI='<CycloneDDS><Domain id="any"><SharedMemory><Enable>false</Enable></SharedMemory></Domain></CycloneDDS>'
python simulacion/sdk_bridge/run_g1_bridge.py
```

**Terminal 2 — Run deploy script against MuJoCo (use `lo` instead of `enp7s0`):**
```bash
conda activate /home/udc/Humanoide/G1/envs/g1_udc
export LD_LIBRARY_PATH="/home/udc/Humanoide/humanoide/cyclonedds/install/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export CYCLONEDDS_URI='<CycloneDDS><Domain id="any"><SharedMemory><Enable>false</Enable></SharedMemory></Domain></CycloneDDS>'
python despliegue/deploy_motion.py lo motion_agacharse.yaml
```

### Direct MuJoCo (no DDS overhead)

```bash
conda activate /home/udc/Humanoide/G1/envs/g1_udc
python simulacion/sim_motion_policies.py motion_agacharse.yaml    # squat 29-DOF
python simulacion/sim_hv.py g1_hv.yaml                            # locomotion 12-DOF
```

---

<a name="español"></a>
## 🇪🇸 Español

Dos opciones de simulación para validar políticas del G1 antes de ejecutarlas en el robot físico.

### Opciones de Simulación

| Característica | Isaac Sim | MuJoCo sdk_bridge |
|---------------|-----------|-------------------|
| Propósito | Tareas de manipulación (pick & place, apilar) | Validación sim-to-sim + test de deploy |
| Interfaz | Visual, fotorrealista | Ligero, puede correr sin ventana |
| DDS | Igual que robot real | Igual que robot real |
| Entorno | `isaaclab` | `g1_udc` |
| Lanzar | `launch_g1.sh` | `run_g1_bridge.py` |
| Guía | [isaac_sim/README.md](isaac_sim/README.md) | [sdk_bridge/README.md](sdk_bridge/README.md) |

### Isaac Sim — Manipulación

```bash
conda activate isaaclab
cd /home/udc/Humanoide/G1
bash simulacion/isaac_sim/launch_g1.sh cylinder_dex1
```

Ver [isaac_sim/README.md](isaac_sim/README.md) para los 14 alias de escenas.

### MuJoCo — Validación de Política (sin robot)

**Terminal 1 — Levantar el bridge MuJoCo:**
```bash
conda activate /home/udc/Humanoide/G1/envs/g1_udc
export LD_LIBRARY_PATH="/home/udc/Humanoide/humanoide/cyclonedds/install/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export CYCLONEDDS_URI='<CycloneDDS><Domain id="any"><SharedMemory><Enable>false</Enable></SharedMemory></Domain></CycloneDDS>'
python simulacion/sdk_bridge/run_g1_bridge.py
```

**Terminal 2 — Correr script de despliegue contra MuJoCo (usar `lo` en vez de `enp7s0`):**
```bash
conda activate /home/udc/Humanoide/G1/envs/g1_udc
export LD_LIBRARY_PATH="/home/udc/Humanoide/humanoide/cyclonedds/install/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export CYCLONEDDS_URI='<CycloneDDS><Domain id="any"><SharedMemory><Enable>false</Enable></SharedMemory></Domain></CycloneDDS>'
python despliegue/deploy_motion.py lo motion_agacharse.yaml
```

### MuJoCo Directo (sin overhead DDS)

```bash
conda activate /home/udc/Humanoide/G1/envs/g1_udc
python simulacion/sim_motion_policies.py motion_agacharse.yaml    # agacharse 29-DOF
python simulacion/sim_hv.py g1_hv.yaml                            # locomoción 12-DOF
```
