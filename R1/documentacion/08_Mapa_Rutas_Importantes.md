# 08 — Mapa de rutas importantes del proyecto

> Saber **dónde tocar qué** es la mitad del trabajo. Este es el mapa autoritativo del workspace `space_r1` + extensiones.

Todas las rutas se asumen relativas a `D:\space_r1\` (el README sigue diciendo `C:\space_r1\` pero es mejor moverlo a `D:\` por velocidad de I/O y espacio).

---

## 1. Workspace top-level

```
D:\space_r1\
├─ IsaacLab\                          ← clon de NVIDIA-Omniverse/IsaacLab
│  ├─ isaaclab.bat                    ← entry-point (todo se invoca por aquí)
│  ├─ source\
│  │  ├─ isaaclab\                    ← core (envs, sim, scene, sensors)
│  │  ├─ isaaclab_assets\             ← R1_CFG vive aquí
│  │  ├─ isaaclab_rl\                 ← wrappers RSL-RL / SKRL / RL Games
│  │  └─ isaaclab_tasks\              ← tareas de ejemplo (Cartpole, Anymal…)
│  └─ logs\rsl_rl\                    ← TODOS los runs salen aquí
│     ├─ r1_standing\
│     │  ├─ 2026-03-03_15-35-21\      ← un run
│     │  │  ├─ model_500.pt
│     │  │  ├─ model_1000.pt
│     │  │  ├─ params\env.yaml
│     │  │  ├─ params\agent.yaml
│     │  │  └─ exported\
│     │  │     ├─ policy.pt
│     │  │     └─ policy.onnx
│     │  └─ 2026-04-15_10-22-05\      ← otro run
│     ├─ r1_locomotion\
│     └─ r1_hierarchical\
│
├─ r1_standing\                       ← extensión de standing
├─ r1_locomotion\                     ← extensión de locomoción WASD (hermana)
├─ r1.usd                             ← asset del robot (mover a IsaacLab\source\…\Robots\Unitree\R1\r1.usd)
├─ play_wasd.py                       ← control manual por terminal
└─ *.md                               ← notas (fuentes, errores, recomendaciones)
```

---

## 2. Dentro de la extensión `r1_standing`

```
r1_standing\
├─ pyproject.toml                                  ← reglas ruff/pyright
├─ commands.md                                     ← comandos rápidos (deprecado, ver doc 07)
├─ revisionEntrenamiento.md                        ← bitácora de entrenamiento
├─ scripts\
│  ├─ list_envs.py                                 ← listar tareas (filtra por "Template-")
│  ├─ random_agent.py / zero_agent.py              ← dummies para validar env
│  ├─ rsl_rl\
│  │  ├─ cli_args.py                               ← flags compartidos
│  │  ├─ train.py                                  ← entrenar PPO
│  │  └─ play.py                                   ← reproducir + export ONNX/JIT
│  └─ skrl\
│     ├─ train.py
│     └─ play.py
└─ source\r1_standing\
   ├─ pyproject.toml                               ← (interno, build setuptools)
   ├─ setup.py                                     ← lee config\extension.toml
   ├─ config\extension.toml                        ← versión, autor, deps
   └─ r1_standing\                                  ← paquete Python
      ├─ __init__.py                               ← debe importar tasks
      ├─ ui_extension_example.py                   ← UI Omni opcional
      └─ tasks\direct\r1_standing\
         ├─ __init__.py                            ← gym.register(...)  ← ★
         ├─ r1_standing_env.py                     ← ★ lógica del env
         ├─ r1_standing_env_cfg.py                 ← ★ config (rewards, scales)
         └─ agents\
            ├─ __init__.py
            ├─ rsl_rl_ppo_cfg.py                   ← ★ hiperparámetros PPO RSL-RL
            └─ skrl_ppo_cfg.yaml                   ← ★ hiperparámetros PPO SKRL
```

> Los archivos marcados con ★ son **los que tocas constantemente**.

---

## 3. ¿Dónde se modifica qué?

| Quiero cambiar… | Archivo | Símbolo / sección |
|----------------|---------|-------------------|
| **Recompensas** (escalas) | `r1_standing_env_cfg.py` | atributos `rew_scale_*` |
| **Lógica de recompensas** | `r1_standing_env.py` | `_get_rewards` y `compute_rewards` |
| **Observaciones** | `r1_standing_env.py` | `_get_observations` |
| **Acciones** | `r1_standing_env.py` | `_apply_action` |
| **Condiciones de fall** | `r1_standing_env.py` | `_get_dones` |
| **Reset y curriculum** | `r1_standing_env.py` | `_reset_idx` |
| **Push system** | `r1_standing_env.py` | `_apply_random_pushes` |
| **Hiperparámetros PPO** | `agents/rsl_rl_ppo_cfg.py` | `PPORunnerCfg`, `RslRlPpoAlgorithmCfg` |
| **Tamaño del MLP** | `agents/rsl_rl_ppo_cfg.py` | `actor/critic_hidden_dims` |
| **Número de envs / spacing** | `r1_standing_env_cfg.py` | `scene: InteractiveSceneCfg(num_envs=…)` |
| **dt / decimation** | `r1_standing_env_cfg.py` | `sim: SimulationCfg(dt=…)`, `decimation=…` |
| **Episode length** | `r1_standing_env_cfg.py` | `episode_length_s` |
| **Action scale** | `r1_standing_env_cfg.py` | `action_scale` |
| **R1_CFG asset** | `IsaacLab\source\isaaclab_assets\…\Unitree\R1\` | el `R1_CFG` en `__init__.py` |
| **Terreno** | `r1_locomotion_env_cfg.py` (extensión hermana) | `scene.terrain = TerrainImporterCfg(...)` |
| **Política madre / hijas** | `codigos/hierarchical/hierarchical_env.py` | `HierarchicalCfg.{stand,walk,stair}_ckpt` |

---

## 4. ¿Dónde vive el modelo del R1 (`r1.usd`)?

Hay 3 lugares donde puede estar el USD:

| Ruta | Quién la usa | Notas |
|-----|-------------|------|
| `D:\space_r1\r1.usd` | El repo `space_r1` lo deja aquí (raw asset). | Es el archivo "fuente" — relativamente pequeño. |
| `D:\space_r1\IsaacLab\source\isaaclab_assets\data\Robots\Unitree\R1\r1.usd` | Lo lee `R1_CFG` cuando hace `usd_path=os.path.join(ASSETS_DIR, "Robots/Unitree/R1/r1.usd")`. | **Ésta es la ruta que Isaac identifica.** |
| `~\AppData\Local\ov\pkg\isaac-sim-*\extscache\…\R1\r1.usd` | Cache de Omniverse al primer load. | Generado al usar el USD por primera vez. |

### Cómo asegurarse que Isaac lo encuentre

1. Verificar que `R1_CFG` existe:
   ```python
   # IsaacLab/source/isaaclab_assets/isaaclab_assets/robots/r1.py
   R1_CFG = ArticulationCfg(
       spawn=sim_utils.UsdFileCfg(
           usd_path=f"{ISAAC_NUCLEUS_DIR}/Robots/Unitree/R1/r1.usd",
           ...
       ),
       ...
   )
   ```
2. Si no existe, **créalo** copiando el `r1.usd` y registrándolo (ver [doc 10 §3](./10_Correcciones_Aplicadas.md)).

---

## 5. Logs, checkpoints y exports

### Estructura por run

```
logs\rsl_rl\<experiment_name>\<YYYY-MM-DD_HH-MM-SS>[_<run_name>]\
├─ events.out.tfevents.*       ← TensorBoard
├─ git\                        ← snapshot del repo en el commit del run
├─ params\
│  ├─ env.yaml                 ← R1StandingEnvCfg serializado
│  └─ agent.yaml               ← PPORunnerCfg serializado
├─ model_500.pt                ← checkpoint cada save_interval
├─ model_1000.pt
├─ ...
├─ model_<max_iter>.pt         ← último
└─ exported\                   ← creado por play.py
   ├─ policy.pt                ← TorchScript
   └─ policy.onnx              ← ONNX
```

### Cómo identificar tu mejor run

1. `tensorboard --logdir logs/rsl_rl/r1_standing` → ordena por `Reward/Total`.
2. Comparar `mean_episode_length` (debe llegar al máximo del cfg) entre runs.
3. Hacer `play.py --num_envs=2` con cada candidato y comprobar visualmente.

### Cómo guardar el "modelo final" para producción

```powershell
# Copiar checkpoint + exported al directorio de release
$src = "D:\space_r1\IsaacLab\logs\rsl_rl\r1_standing\2026-03-03_15-35-21"
$dst = "D:\space_r1\release\r1_standing_v1"
New-Item -ItemType Directory -Path $dst -Force
Copy-Item "$src\model_3500.pt"   $dst\
Copy-Item "$src\exported\*.pt"   $dst\
Copy-Item "$src\exported\*.onnx" $dst\
Copy-Item "$src\params\env.yaml" $dst\
Copy-Item "$src\params\agent.yaml" $dst\
```

---

## 6. Variables de entorno y configuración global

| Variable | Lugar | Uso |
|----------|-------|-----|
| `ISAAC_NUCLEUS_DIR` | runtime | URL local o nucleus para assets default |
| `OMNI_KIT_PATH` | sistema | path al kit-sdk |
| `PYTHONPATH` | sistema | NO debe contener Isaac Lab manualmente — usar `isaaclab.bat -p` |
| `CUDA_VISIBLE_DEVICES` | shell | restringir GPU |

---

## 7. Convenciones de nombres en este repo

| Patrón | Significado |
|-------|-------------|
| `R1Standing-Direct-v0` | Tarea Direct, versión 0 |
| `R1Standing-Direct-Play-v0` | Versión "play" (menos envs, más visual) — convención Isaac Lab |
| `r1_standing` | nombre del experiment, carpeta de logs |
| `r1.usd` | asset USD del robot |
| `model_*.pt` | checkpoint de RSL-RL |
| `policy.{pt,onnx}` | export de inferencia |

---

## 8. Atajos PowerShell útiles

```powershell
# Alias rápido
$env:ISAACLAB = "D:\space_r1\IsaacLab"
function isaac($script, $task, $num_envs, $extra) {
    & "$env:ISAACLAB\isaaclab.bat" -p ".\scripts\$script" --task=$task --num_envs=$num_envs $extra
}

# Uso:
isaac rsl_rl\train.py R1Standing-Direct-v0 4096 "--max_iterations=4000 --headless"
```

Próximo paso → [09_Fuentes_Bibliografia.md](./09_Fuentes_Bibliografia.md).
