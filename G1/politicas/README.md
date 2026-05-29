# Trained Policies / Políticas Entrenadas — G1

[🇬🇧 English](#english) | [🇪🇸 Español](#español)

---

<a name="english"></a>
## 🇬🇧 English

All policies are TorchScript JIT files (`.pt`). Located at `/home/udc/Humanoide/G1/politicas/`.

### Policy Table

| File | Type | obs dims | DOF | Framework | Description |
|------|------|----------|-----|-----------|-------------|
| `motion_agacharse_v10_jit.pt` | Motion 29-DOF | 94 | 0–14 (legs+waist) | HumanoidVerse / Genesis | Squat / crouch cyclic motion |
| `motion_munecas_DR_jit.pt` | Motion 29-DOF | 62 | 15–28 (arms) | HumanoidVerse / IsaacGym | Wrist rotation with Domain Randomization |
| `motion_estirar_DR_jit.pt` | Motion 29-DOF | 62 | 15–28 (arms) | HumanoidVerse / IsaacGym | Arm stretch motion |
| `motion_saludar_DR_jit.pt` | Motion 29-DOF | 62 | 15–28 (arms) | HumanoidVerse / IsaacGym | Wave / greeting motion |
| `model_7000_jit.pt` | Locomotion 12-DOF | 48 | 0–11 (legs) | HumanoidVerse / Genesis | Walking — checkpoint 7000 |
| `model_DR_jit.pt` | Locomotion 12-DOF | 48 | 0–11 (legs) | HumanoidVerse / Genesis | Walking — with Domain Randomization |
| `motion.pt` | Locomotion 12-DOF | 47 | 0–11 (legs) | unitree_rl_gym | Walking — original Unitree policy |

### How to Deploy

```bash
conda activate /home/udc/Humanoide/G1/envs/g1_udc
export LD_LIBRARY_PATH="/home/udc/Humanoide/humanoide/cyclonedds/install/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export CYCLONEDDS_URI='<CycloneDDS><Domain id="any"><SharedMemory><Enable>false</Enable></SharedMemory></Domain></CycloneDDS>'
cd /home/udc/Humanoide/G1

# Motion policies (29-DOF) — use deploy_motion.py + config YAML
python despliegue/deploy_motion.py enp7s0 motion_agacharse.yaml
python despliegue/deploy_motion.py enp7s0 motion_munecas.yaml

# Locomotion (12-DOF) — use deploy_dual.py + config YAML
python despliegue/deploy_dual.py enp7s0 g1_hv.yaml     # model_7000_jit.pt
python despliegue/deploy_dual.py enp7s0 g1_motion.yaml  # motion.pt
```

See [despliegue/README.md](../despliegue/README.md) for full safety procedure.

---

<a name="español"></a>
## 🇪🇸 Español

Todas las políticas son archivos TorchScript JIT (`.pt`). Ubicadas en `/home/udc/Humanoide/G1/politicas/`.

### Tabla de Políticas

| Archivo | Tipo | obs dims | DOF | Framework | Descripción |
|---------|------|----------|-----|-----------|-------------|
| `motion_agacharse_v10_jit.pt` | Movimiento 29-DOF | 94 | 0–14 (piernas+cintura) | HumanoidVerse / Genesis | Agacharse cíclicamente |
| `motion_munecas_DR_jit.pt` | Movimiento 29-DOF | 62 | 15–28 (brazos) | HumanoidVerse / IsaacGym | Rotación de muñecas con DR |
| `motion_estirar_DR_jit.pt` | Movimiento 29-DOF | 62 | 15–28 (brazos) | HumanoidVerse / IsaacGym | Estirar brazos |
| `motion_saludar_DR_jit.pt` | Movimiento 29-DOF | 62 | 15–28 (brazos) | HumanoidVerse / IsaacGym | Movimiento de saludo |
| `model_7000_jit.pt` | Locomoción 12-DOF | 48 | 0–11 (piernas) | HumanoidVerse / Genesis | Caminar — checkpoint 7000 |
| `model_DR_jit.pt` | Locomoción 12-DOF | 48 | 0–11 (piernas) | HumanoidVerse / Genesis | Caminar — con Domain Randomization |
| `motion.pt` | Locomoción 12-DOF | 47 | 0–11 (piernas) | unitree_rl_gym | Caminar — política original Unitree |

### Cómo Desplegar

```bash
conda activate /home/udc/Humanoide/G1/envs/g1_udc
export LD_LIBRARY_PATH="/home/udc/Humanoide/humanoide/cyclonedds/install/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export CYCLONEDDS_URI='<CycloneDDS><Domain id="any"><SharedMemory><Enable>false</Enable></SharedMemory></Domain></CycloneDDS>'
cd /home/udc/Humanoide/G1

# Políticas de movimiento (29-DOF) — usar deploy_motion.py + YAML
python despliegue/deploy_motion.py enp7s0 motion_agacharse.yaml
python despliegue/deploy_motion.py enp7s0 motion_munecas.yaml

# Locomoción (12-DOF) — usar deploy_dual.py + YAML
python despliegue/deploy_dual.py enp7s0 g1_hv.yaml     # model_7000_jit.pt
python despliegue/deploy_dual.py enp7s0 g1_motion.yaml  # motion.pt
```

Ver [despliegue/README.md](../despliegue/README.md) para el procedimiento de seguridad completo.
