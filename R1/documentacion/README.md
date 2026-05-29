# Documentación Completa — Política de Entrenamiento Robot Unitree R1

Documentación maestra del proyecto **R1 Standing / R1 Locomotion** sobre **NVIDIA Isaac Sim + Isaac Lab**. Cubre, desde cero, instalación, creación y *fine-tuning* de políticas RL para el humanoide Unitree R1, política jerárquica (madre + hijas), control por coordenadas (WASD/path-planning), playgrounds con escaleras y terrenos, y todos los códigos validados.

> **Dos sets paralelos**:
> - **Set Windows (este README + docs 01–10)** — para entrenamiento rápido en tu PC Windows.
> - **Set Ubuntu + ROS2** ([`Ubuntu_ROS2/`](./Ubuntu_ROS2/README.md)) — entorno nativo Linux + ROS2 Humble + sim2real bridge para el robot físico.

Repositorios fuente:

- `pandafter/r1_standing` → extensión Isaac Lab con la tarea `R1Standing-Direct-v0` (PPO, RSL-RL / SKRL).
- `pandafter/space_r1` → workspace que contiene `IsaacLab/`, las políticas hijas (`r1_standing`, `r1_locomotion`), el modelo `r1.usd`, el control manual `play_wasd.py` y los `.md` de investigación.

---

## Índice

| #  | Documento | Tema |
|----|-----------|------|
| 01 | [01_Instalacion_Windows.md](./01_Instalacion_Windows.md) | Instalación end-to-end en Windows: Isaac Sim, Isaac Lab, conda env, RSL-RL, SKRL, integración con la extensión `r1_standing`. |
| 02 | [02_Crear_Politica_Basica.md](./02_Crear_Politica_Basica.md) | Cómo se crea una política PPO básica para el R1 (Direct Workflow): recompensas, observaciones, registro Gym. |
| 03 | [03_Politica_Padre_Jerarquica.md](./03_Politica_Padre_Jerarquica.md) | Política **madre** que orquesta sub-políticas (estabilidad → locomoción → percepción YOLO) en niveles jerárquicos. |
| 04 | [04_Fine_Tuning.md](./04_Fine_Tuning.md) | *Resume*, *transfer learning*, congelado de capas, *curriculum* progresivo, KL adaptativo. |
| 05 | [05_Path_Coordenadas_Velocidad.md](./05_Path_Coordenadas_Velocidad.md) | Sistema de comandos por coordenadas (`x*`, `ψ*`), velocidad emergente y adaptación a terreno. |
| 06 | [06_Playground_Terrenos.md](./06_Playground_Terrenos.md) | Construcción del *playground* con escaleras, slopes, gaps, terreno aleatorio + *curriculum* de dificultad. |
| 07 | [07_Codigos_Train_Play.md](./07_Codigos_Train_Play.md) | Comandos exactos de `train.py` y `play.py`, flags, ejemplos por escenario. |
| 08 | [08_Mapa_Rutas_Importantes.md](./08_Mapa_Rutas_Importantes.md) | Mapa de archivos: dónde vive `r1.usd`, dónde se modifican rewards, agents, configs, logs. |
| 09 | [09_Fuentes_Bibliografia.md](./09_Fuentes_Bibliografia.md) | Artículos académicos que sustentan el diseño (de `space_r1/fuentes.md`). |
| 10 | [10_Correcciones_Aplicadas.md](./10_Correcciones_Aplicadas.md) | Bugs detectados en los repos originales y correcciones aplicadas en este *snapshot*. |

### Set paralelo Ubuntu + ROS2 (deploy físico)

| Carpeta | Tema |
|---------|------|
| [Ubuntu_ROS2/](./Ubuntu_ROS2/README.md) | Documentación end-to-end Linux: 11 docs + workspace ROS2 (`r1_msgs`, `r1_inference`, `r1_sim_bridge`, `r1_teleop`, `r1_bringup`) + scripts bash + systemd service para deploy permanente. |
| [Ubuntu_ROS2/06_Sim2Real.md](./Ubuntu_ROS2/06_Sim2Real.md) | Domain randomization completo + calibración + JointCommandLagBuffer + asymmetric actor-critic. |
| [Ubuntu_ROS2/07_Hardware_Interface_R1.md](./Ubuntu_ROS2/07_Hardware_Interface_R1.md) | Conexión Ethernet con el R1, SDK Unitree, mapeo de joints, ganancias PD, FSM seguro, E-stop. |
| [Ubuntu_ROS2/09_Despliegue_Robot_Real.md](./Ubuntu_ROS2/09_Despliegue_Robot_Real.md) | Procedimiento end-to-end: pre-flight, bring-up, dry-run, deploy, systemd. |

### Carpeta `codigos/`

```
codigos/
├── scripts/
│   ├── train_rsl_rl.py          ← Entrenamiento PPO con RSL-RL
│   ├── play_rsl_rl.py           ← Reproducción de checkpoint con export ONNX/JIT
│   ├── play_wasd.py             ← Control manual por coordenadas/WASD (corregido)
│   └── cli_args.py              ← Args CLI compartidos
├── standing/                     ← Política hija de estabilización (push-recovery)
│   ├── r1_standing_env.py       ← Env corregido (API push fix, jit fix)
│   ├── r1_standing_env_cfg.py   ← Config con 88 dims, rewards balanceados
│   └── __init__.py              ← Registro Gym
├── locomotion/                   ← Política hija WASD/coordenadas
│   ├── r1_locomotion_env.py     ← Env con target_pos_w, navegación
│   ├── r1_locomotion_env_cfg.py ← Config con observation_space=97
│   └── __init__.py
├── hierarchical/                 ← Política MADRE (high-level)
│   ├── high_level_planner.py    ← FSM/orquestador
│   ├── hierarchical_env.py      ← Env que envuelve sub-políticas
│   └── README.md                 ← Diagrama jerárquico
├── agents/
│   ├── rsl_rl_ppo_cfg.py        ← Config PPO RSL-RL (4000 iters, [256,128,64])
│   └── skrl_ppo_cfg.yaml        ← Config PPO SKRL (corregido del template)
└── playground/
    ├── stairs_terrain_cfg.py    ← Generador de escaleras
    ├── rough_terrain_cfg.py     ← Terreno aleatorio + slopes
    └── curriculum_cfg.py        ← Curriculum progresivo
```

---

## Stack tecnológico

| Componente | Versión recomendada | Notas |
|-----------|--------------------:|-------|
| Windows | 10 / 11 (x64) | Build ≥ 19045. |
| GPU NVIDIA | Driver ≥ 535 | RTX 3060 mínimo, RTX 4070+ recomendado para 8000 envs. |
| CUDA Toolkit | 12.1 / 12.4 | Coincidir con la versión de PyTorch. |
| Anaconda / Miniconda | 24.x | Aislamiento del entorno `env_isaaclab`. |
| Python | 3.10 / 3.11 | Lo requiere Isaac Lab. |
| Isaac Sim | 4.5.0 / 5.0.0 / 5.1.0 | El proyecto está marcado como compatible. |
| Isaac Lab | `main` (rama estable) | Clonado dentro de `C:\space_r1\IsaacLab` (o `D:\space_r1\IsaacLab`). |
| RSL-RL | `rsl-rl-lib >= 3.0.1` | Requerido por `train.py`. |
| SKRL | última | Alternativo a RSL-RL. |
| PyTorch | 2.4 / 2.5 | Con CUDA. |

---

## Flujo de trabajo recomendado

```
[1] Instalación (doc 01)
        ↓
[2] Verificación: list_envs.py + zero_agent.py + random_agent.py
        ↓
[3] Política base de standing (doc 02)
        ↓
[4] Fine-tune con push-recovery (doc 04)
        ↓
[5] Política de locomotion / WASD coords (doc 05)
        ↓
[6] Playground con terrenos y escaleras (doc 06)
        ↓
[7] Política madre que orquesta hijas (doc 03)
        ↓
[8] Despliegue: play_wasd.py o sim2real
```

---

## Convenciones

- Las rutas se documentan asumiendo `C:\space_r1\` como *workspace root* (tal como aparece en los repos), pero **se recomienda migrar a `D:\space_r1\`** para mejorar el rendimiento de los logs (los checkpoints crecen rápido).
- Cuando se vea `<RL_LIBRARY>` substituir por `rsl_rl` o `skrl`.
- Los nombres de tarea registrados son `R1Standing-Direct-v0` y `R1-Locomotion-Direct-v0`. El alias *legacy* `Template-R1-Prueba-Direct-v0` (presente en `commands.md`) está **deprecado** — ver [doc 10](./10_Correcciones_Aplicadas.md).
