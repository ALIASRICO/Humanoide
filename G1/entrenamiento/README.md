# Training / Entrenamiento — G1 RL Policies

[🇬🇧 English](#english) | [🇪🇸 Español](#español)

---

<a name="english"></a>
## 🇬🇧 English

RL training for the Unitree G1 using two frameworks depending on the policy type.

### Frameworks

| Framework | Policy type | Simulator | Script |
|-----------|-------------|-----------|--------|
| **HumanoidVerse** | Motion policies (29-DOF): squat, wrists, stretch, wave | Genesis / IsaacGym | `train_agacharse_v10.sh` |
| **Isaac RL Lab** | Locomotion (12-DOF) + grasp | Isaac Sim / Isaac Lab | `isaac_rl_lab/launch_g1_train.sh` |

### HumanoidVerse — Motion Policy Training

```bash
conda activate hgen
cd /home/udc/Humanoide/G1/entrenamiento

# Train squat policy (V10)
bash train_agacharse_v10.sh

# Or run manually:
python humanoidverse/train_agent.py \
  +simulator=genesis \
  +exp=motion \
  +domain_rand=motion_DR \
  +rewards=motion/agacharse_rewards_v5 \
  +robot=g1/g1_29dof \
  +terrain=terrain_base \
  +obs=motion/agacharse_obs \
  num_envs=4096 \
  project_name=G1_Motion_DR \
  experiment_name=G1_Agacharse_V10
```

**Evaluate a saved checkpoint:**
```bash
bash eval_agacharse_v10.sh
```

**Export to TorchScript JIT (for deployment):**
```bash
python export_motion_policy.py \
  logs/G1_Motion_DR/G1_Agacharse_V10/model_6000.pt \
  ../politicas/motion_agacharse_v10_jit.pt
```

### Isaac RL Lab — Locomotion / Grasp

```bash
conda activate isaaclab
cd /home/udc/Humanoide/G1/entrenamiento

bash isaac_rl_lab/launch_g1_train.sh   # train
bash isaac_rl_lab/launch_g1_play.sh    # evaluate
```

### Where Logs Are Saved

```
entrenamiento/logs/
├── G1Locomotion/       12-DOF locomotion checkpoints
└── G1_Motion_DR/       29-DOF motion policies with Domain Randomization
```

Monitor training:
```bash
conda activate hgen
tensorboard --logdir entrenamiento/logs/
# Open http://localhost:6006
```

### CRITICAL: Observation Vector Order

> **WARNING: The observation vector in HumanoidVerse is built in ALPHABETICAL order** (`sorted(obs_keys)`), not in the order they appear in the YAML file.
>
> This is the root cause of most sim-to-sim failures — if the obs order is wrong, the robot falls in under 1 second in MuJoCo.

Correct order for squat policy (94 dims):
```
base_ang_vel [3] → dof_pos [29] → dof_vel [29] → phase_signal [1] → projected_gravity [3] → q_target [29]
```

Correct order for wrist policy (62 dims):
```
dof_pos [29] → phase_signal [1] → projected_gravity [3] → q_target [29]
```

---

<a name="español"></a>
## 🇪🇸 Español

Entrenamiento por RL del G1 usando dos frameworks según el tipo de política.

### Frameworks

| Framework | Tipo de política | Simulador | Script |
|-----------|-----------------|-----------|--------|
| **HumanoidVerse** | Políticas de movimiento (29-DOF): agacharse, muñecas, estirar, saludar | Genesis / IsaacGym | `train_agacharse_v10.sh` |
| **Isaac RL Lab** | Locomoción (12-DOF) + agarre | Isaac Sim / Isaac Lab | `isaac_rl_lab/launch_g1_train.sh` |

### HumanoidVerse — Entrenamiento de Política de Movimiento

```bash
conda activate hgen
cd /home/udc/Humanoide/G1/entrenamiento

# Entrenar política agacharse (V10)
bash train_agacharse_v10.sh

# O manualmente:
python humanoidverse/train_agent.py \
  +simulator=genesis \
  +exp=motion \
  +domain_rand=motion_DR \
  +rewards=motion/agacharse_rewards_v5 \
  +robot=g1/g1_29dof \
  +terrain=terrain_base \
  +obs=motion/agacharse_obs \
  num_envs=4096 \
  project_name=G1_Motion_DR \
  experiment_name=G1_Agacharse_V10
```

**Evaluar un checkpoint guardado:**
```bash
bash eval_agacharse_v10.sh
```

**Exportar a TorchScript JIT (para despliegue):**
```bash
python export_motion_policy.py \
  logs/G1_Motion_DR/G1_Agacharse_V10/model_6000.pt \
  ../politicas/motion_agacharse_v10_jit.pt
```

### Isaac RL Lab — Locomoción / Agarre

```bash
conda activate isaaclab
cd /home/udc/Humanoide/G1/entrenamiento

bash isaac_rl_lab/launch_g1_train.sh   # entrenar
bash isaac_rl_lab/launch_g1_play.sh    # evaluar
```

### Dónde se Guardan los Logs

```
entrenamiento/logs/
├── G1Locomotion/       Checkpoints de locomoción 12-DOF
└── G1_Motion_DR/       Políticas de movimiento 29-DOF con Domain Randomization
```

Monitorear entrenamiento:
```bash
conda activate hgen
tensorboard --logdir entrenamiento/logs/
# Abrir http://localhost:6006
```

### CRITICO: Orden del Vector de Observaciones

> **ADVERTENCIA: El vector de observaciones en HumanoidVerse se construye en orden ALFABÉTICO** (`sorted(obs_keys)`), no en el orden en que aparecen en el archivo YAML.
>
> Esta es la causa raíz de la mayoría de los fallos sim-to-sim — si el orden de obs es incorrecto, el robot cae en menos de 1 segundo en MuJoCo.

Orden correcto para agacharse (94 dims):
```
base_ang_vel [3] → dof_pos [29] → dof_vel [29] → phase_signal [1] → projected_gravity [3] → q_target [29]
```

Orden correcto para muñecas (62 dims):
```
dof_pos [29] → phase_signal [1] → projected_gravity [3] → q_target [29]
```

### Solución de Problemas

| Síntoma | Solución |
|---------|----------|
| `CUDA out of memory` | Reducir `num_envs` (ej. 2048) |
| Robot cae en <1 s en MuJoCo | Verificar orden ALFABÉTICO de obs |
| Genesis no inicia | `python -c "import genesis"` — verificar drivers NVIDIA |
| `ModuleNotFoundError: humanoidverse` | `pip install -e entrenamiento/` en entorno hgen |
