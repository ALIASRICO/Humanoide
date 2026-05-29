# Estado del Proyecto / Project Status

> Última actualización: 2026-05-29 | Last updated: 2026-05-29

---

## Resumen ejecutivo

Proyecto de robótica humanoide con dos robots Unitree: el **G1** (29-DOF, activo y operativo en simulación) y el **R1 EDU** (26-DOF, hardware en camino). El repositorio fue reorganizado de `Unitree_G1/` a `Humanoide/G1/` + `Humanoide/R1/` con documentación bilingüe profesional.

---

## ✅ Lo que está hecho — G1

### Infraestructura y entorno
| Componente | Estado | Notas |
|---|---|---|
| Isaac Sim 5.1 + IsaacLab | ✅ Operativo | RTX 5090, CUDA 12.x |
| MuJoCo (sdk_bridge) | ✅ Operativo | Simulación ligera sin render |
| CycloneDDS (iceoryx-free) | ✅ Fijo | patchelf + LD_LIBRARY_PATH |
| Conda env `isaaclab` | ✅ Listo | Para Isaac Sim |
| Conda env `g1_udc` | ✅ Listo | Para MuJoCo / despliegue |
| ROS2 Jazzy + workspace | ✅ Compilado | unitree_api, unitree_hg, unitree_go |

### Simulación Isaac Sim
| Característica | Estado | Notas |
|---|---|---|
| 14 escenas disponibles | ✅ | pick&place, stack, drawer, move (wholebody) |
| Control por teclado | ✅ | `send_commands_keyboard.py` + DDS vars |
| Cámaras ZMQ (3 cámaras) | ✅ | Ventana Combined Image (frontal + 2 muñecas) |
| Bug binocular corregido | ✅ | `simulacion/cam_config_server.yaml` |
| Smoke tests automáticos | ✅ | `test_all_scenes.sh` — 14/14 PASS |

### Políticas entrenadas (G1)
| Archivo | Tipo | Framework | Estado |
|---|---|---|---|
| `motion_agacharse_v10_jit.pt` | Movimiento | HumanoidVerse | ✅ Validado sim+real |
| `motion_munecas_DR_jit.pt` | Movimiento | HumanoidVerse | ✅ Entrenado con DR |
| `motion_estirar_DR_jit.pt` | Movimiento | HumanoidVerse | ✅ Entrenado con DR |
| `motion_saludar_DR_jit.pt` | Movimiento | HumanoidVerse | ✅ Entrenado con DR |
| `model_7000_jit.pt` | Locomoción | Isaac RL Lab | ✅ Entrena en IsaacLab |
| `model_DR_jit.pt` | Locomoción DR | Isaac RL Lab | ✅ Con domain randomization |

### Despliegue en robot físico
| Tarea | Estado | Notas |
|---|---|---|
| `deploy_motion.py` | ✅ Funcional | Agacharse, muñecas, estirar, saludar |
| Protocolo arnés de seguridad | ✅ Documentado | Ver `G1/despliegue/README.md` |
| Secuencias físicas (saludo, etc.) | ✅ | `G1/codigos/robot_fisico/` |
| LiDAR + RViz | ✅ Operativo | `G1/codigos/lidar/` |

### Documentación
| Documento | Estado |
|---|---|
| READMEs bilingües EN/ES (11 archivos) | ✅ |
| MANUAL_G1.md (índice navegable) | ✅ |
| Guías PDF (instalación, Isaac Lab, MuJoCo) | ✅ |
| Planes de trabajo archivados | ✅ |

---

## ⏳ Lo que falta — G1

| Tarea | Prioridad | Descripción |
|---|---|---|
| Integración YOLO → control robot | 🔴 Alta | El detector existe (`codigos/deteccion/`) pero no está conectado a ninguna política ni pipeline de control |
| Política jerárquica (locomotion + agarre) | 🔴 Alta | `planes_de_trabajo/plan_04` diseñado pero no implementado |
| Validación despliegue locomoción real | 🟡 Media | `model_7000_jit.pt` entrenado pero no probado en robot físico |
| Pipeline imitación LeRobot completo | 🟡 Media | Scripts listos en `codigos/imitacion/`, falta grabar episodios con G1 real |
| SLAM con LiDAR 3D | 🟡 Media | Point-LIO disponible, no integrado con navegación |
| Actualizar `envs/` en `.gitignore` | 🟢 Baja | El conda env no debe versionarse (ya corregido, pero `hgen_backup.yml` podría actualizarse) |

---

## ✅ Lo que está hecho — R1

| Componente | Estado | Notas |
|---|---|---|
| URDF + meshes | ✅ | `R1/escenas/R1.urdf` + `meshes/` |
| MuJoCo XML | ✅ | `R1/escenas/R1_C++.xml` |
| Política standing (código) | ✅ | 88 obs, 18 rewards, bugs corregidos |
| Política locomotion (código) | ✅ | 97 obs, WASD por coordenadas |
| Política jerárquica (código) | ✅ | Madre + hijos congelados |
| Terrain playground | ✅ | Escaleras, rampas, gaps, curriculum |
| Documentación entrenamiento (10 guías) | ✅ | `R1/documentacion/` |
| Workspace ROS2 (código) | ✅ | `R1/Ubuntu_ROS2/` — inference node ONNX |

---

## ⏳ Lo que falta — R1

| Tarea | Prioridad | Descripción |
|---|---|---|
| Importar R1 en Isaac Sim | 🔴 Alta | No existe ninguna tarea R1 en IsaacLab. Adaptar las tareas G1 al URDF R1 (26 DOF) |
| Adaptar stack DDS para R1 | 🔴 Alta | Crear `r1_state.py` / `r1_dds.py` equivalentes a los del G1 |
| Entrenar política standing en IsaacLab | 🔴 Alta | El código existe pero no se ha ejecutado en este entorno |
| Probar cámaras con R1 | 🟡 Media | El sistema ZMQ/teleimager del G1 debería funcionar sin cambios |
| Probar en hardware real | ⬛ Bloqueado | Hardware aún no llegó |

---

## 🗺️ Próximos pasos recomendados

### Antes de que llegue el R1 (ahora)
1. **Crear tarea R1 en Isaac Sim** — Adaptar `G1/simulacion/isaac_sim/tasks/` al URDF R1. Objetivo: que `launch_r1.sh standing` funcione.
2. **Adaptar DDS para R1** — Crear `r1_state.py` copiando el patrón de `g1_state.py` con los joints del R1.
3. **Entrenar standing policy** — Ejecutar `R1/codigos/scripts/train_rsl_rl.py` con `R1Standing-Direct-v0` en IsaacLab.

### Cuando llegue el R1
4. **Verificar conexión DDS** — Conectar por Ethernet, verificar topics con `ddsls`.
5. **Test standing en hardware** — Política básica de balance con arnés de seguridad.
6. **Grabar demostraciones** — Usar el pipeline de imitación para tareas de manipulación con la mano dextra.

### G1 — tareas pendientes de alto impacto
7. **Conectar YOLO a pipeline de control** — Integrar `codigos/deteccion/detector.py` con Isaac Sim para detección de objetos en tiempo real.
8. **Política jerárquica** — Unir locomotion + agarre en una política de alto nivel siguiendo `planes_de_trabajo/plan_04`.

---

## Estructura del repositorio (resumen)

```
Humanoide/
├── G1/          # Robot activo — simulación, entrenamiento, despliegue
├── R1/          # Robot próximo — código listo, hardware en camino
├── humanoide/   # CycloneDDS + MuJoCo (infraestructura compartida)
├── herramientas/# Conversión URDF/USD/XML
├── yolo/        # Detección de objetos
├── dataset/     # Dataset YOLO simulación
└── guias/       # PDFs de instalación y uso
```

---

## Bugs conocidos y workarounds

| Bug | Workaround |
|---|---|
| CycloneDDS iceoryx crash | `export LD_LIBRARY_PATH="/home/udc/Humanoide/humanoide/cyclonedds/install/lib:$LD_LIBRARY_PATH"` + `CYCLONEDDS_URI` |
| `cam_config_server.yaml` doble copia | Editar siempre `G1/simulacion/cam_config_server.yaml` (no el de `isaac_sim/`) |
| Isaac Sim no cierra con Ctrl+C | `pkill -9 -f "sim_main.py"` |
| `--action_source keyboard` inválido | Usar `dds` + correr `send_commands_keyboard.py` en terminal separada |
| Primera ejecución tarda ~5 min | Normal — compilación de shaders RTX |
| Obs vector en HumanoidVerse | El vector es **ALFABÉTICO** (sorted), no el orden del YAML |
