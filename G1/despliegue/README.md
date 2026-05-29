# Deployment / Despliegue — Physical Robot G1

[🇬🇧 English](#english) | [🇪🇸 Español](#español)

---

<a name="english"></a>
## 🇬🇧 English

Scripts for deploying RL policies on the physical Unitree G1 via low-level SDK (DDS).

### Safety — Read Before Any Execution

> **Always use a harness / arnés on the first deployment of any policy.**

Official Unitree procedure:
1. Robot hanging in harness (feet not touching the floor)
2. `L2+R2` on gamepad → damping mode (soft joints)
3. Run the script → zero torque state
4. `START` → robot moves to default pose (2 s)
5. Lower the harness slowly until feet touch the ground
6. `A` → policy activates (3 s warmup ramp)
7. `SELECT` or `Ctrl+C` → soft exit (damping)

> **Mandatory:** Disable `sport_mode` from the Unitree app before any low-level SDK control.

### Environment Setup

```bash
conda activate /home/udc/Humanoide/G1/envs/g1_udc
export LD_LIBRARY_PATH="/home/udc/Humanoide/humanoide/cyclonedds/install/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export CYCLONEDDS_URI='<CycloneDDS><Domain id="any"><SharedMemory><Enable>false</Enable></SharedMemory></Domain></CycloneDDS>'
cd /home/udc/Humanoide/G1
```

### deploy_motion.py — 29-DOF Motion Policies

```bash
# Squat policy (legs + waist)
python despliegue/deploy_motion.py enp7s0 motion_agacharse.yaml

# Wrist policy (arms)
python despliegue/deploy_motion.py enp7s0 motion_munecas.yaml
```

### Available Configs

| Config YAML | Policy file | obs dims | DOF controlled | Description |
|-------------|-------------|----------|----------------|-------------|
| `motion_agacharse.yaml` | `motion_agacharse_v10_jit.pt` | 94 | 0–14 (legs+waist) | Squat / crouch motion |
| `motion_munecas.yaml` | `motion_munecas_DR_jit.pt` | 62 | 15–28 (arms) | Wrist rotation |
| `g1_hv.yaml` | `model_7000_jit.pt` | 48 | 0–11 (legs) | Locomotion — HumanoidVerse |
| `g1_motion.yaml` | `motion.pt` | 47 | 0–11 (legs) | Locomotion — original |

### Gamepad Sequence

| Button | Action |
|--------|--------|
| `START` | Move to default pose (2 s) |
| `A` | Activate policy |
| `SELECT` | Soft exit (damping) |
| L-stick fwd/back | vx (locomotion only) |
| L-stick left/right | vy (locomotion only) |
| R-stick left/right | yaw (locomotion only) |

### Built-in Safety Layers (deploy_motion.py)

| Layer | Behavior | Parameter |
|-------|----------|-----------|
| Tilt detection | Auto-stop if inclination > 72° | `tilt_limit: -0.3` in YAML |
| Joint limits | Clamps targets to official URDF limits | Hard-coded in script |
| Warmup ramp | action_scale ramps 0→1 over N seconds | `warmup_s: 3.0` in YAML |

### Troubleshooting

| Symptom | Solution |
|---------|----------|
| Erratic movement on activation | Verify `sport_mode` is disabled in the app |
| `CycloneDDS error` | Check DDS environment variables |
| No response from robot | Check `ping 192.168.123.161` and network interface |
| Auto-stop (tilt) | Robot inclined >72° — review kp/warmup_s in YAML |
| `Policy output NaN` | Obs out of range — restart the script |

---

<a name="español"></a>
## 🇪🇸 Español

Scripts para desplegar políticas RL en el robot físico Unitree G1 mediante el SDK de bajo nivel (DDS).

### Seguridad — Leer Antes de Cualquier Ejecución

> **Siempre usar arnés en el primer despliegue de cualquier política.**

Procedimiento oficial Unitree:
1. Robot colgado en arnés (pies sin tocar el suelo)
2. `L2+R2` en el mando → modo damping (articulaciones blandas)
3. Ejecutar el script → estado zero torque
4. `START` → robot mueve a posición default (2 s)
5. Bajar lentamente el arnés hasta que los pies toquen el suelo
6. `A` → política activa (warmup de 3 s)
7. `SELECT` o `Ctrl+C` → salida suave (amortiguamiento)

> **Obligatorio:** Apagar `sport_mode` desde la app Unitree antes de cualquier control SDK bajo nivel.

### Configuración del Entorno

```bash
conda activate /home/udc/Humanoide/G1/envs/g1_udc
export LD_LIBRARY_PATH="/home/udc/Humanoide/humanoide/cyclonedds/install/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export CYCLONEDDS_URI='<CycloneDDS><Domain id="any"><SharedMemory><Enable>false</Enable></SharedMemory></Domain></CycloneDDS>'
cd /home/udc/Humanoide/G1
```

### deploy_motion.py — Políticas de Movimiento 29-DOF

```bash
# Política agacharse (piernas + cintura)
python despliegue/deploy_motion.py enp7s0 motion_agacharse.yaml

# Política muñecas (brazos)
python despliegue/deploy_motion.py enp7s0 motion_munecas.yaml
```

### Configuraciones Disponibles

| Config YAML | Política | obs dims | DOF controlados | Descripción |
|-------------|---------|----------|----------------|-------------|
| `motion_agacharse.yaml` | `motion_agacharse_v10_jit.pt` | 94 | 0–14 (piernas+cintura) | Agacharse cíclicamente |
| `motion_munecas.yaml` | `motion_munecas_DR_jit.pt` | 62 | 15–28 (brazos) | Rotación de muñecas |
| `g1_hv.yaml` | `model_7000_jit.pt` | 48 | 0–11 (piernas) | Locomoción — HumanoidVerse |
| `g1_motion.yaml` | `motion.pt` | 47 | 0–11 (piernas) | Locomoción — original |

### Secuencia de Mando

| Botón | Acción |
|-------|--------|
| `START` | Mover a posición default (2 s) |
| `A` | Activar política |
| `SELECT` | Salida suave (amortiguamiento) |
| L-stick adelante/atrás | vx (solo locomoción) |
| L-stick izquierda/derecha | vy (solo locomoción) |
| R-stick izquierda/derecha | yaw (solo locomoción) |

### Capas de Seguridad (deploy_motion.py)

| Capa | Comportamiento | Parámetro |
|------|---------------|-----------|
| Detección de inclinación | Para automáticamente si inclinación > 72° | `tilt_limit: -0.3` en YAML |
| Límites de joints | Clampea targets a límites oficiales del URDF | Constantes en el script |
| Warmup ramp | action_scale sube de 0→1 en N segundos | `warmup_s: 3.0` en YAML |

### Solución de Problemas

| Síntoma | Solución |
|---------|----------|
| Movimiento errático al activar | Verificar que `sport_mode` esté apagado en la app |
| `CycloneDDS error` | Verificar variables de entorno DDS |
| Sin respuesta del robot | Verificar `ping 192.168.123.161` e interfaz de red |
| Parada automática (tilt) | Robot inclinado >72° — revisar kp/warmup_s en YAML |
| `Policy output NaN` | Obs fuera de rango — reiniciar el script |
