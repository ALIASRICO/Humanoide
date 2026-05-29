# MuJoCo SDK Bridge

Simula el robot G1 en MuJoCo con la **misma interfaz DDS** que el robot físico.
Permite ejecutar `deploy_motion.py` y `deploy_dual.py` contra MuJoCo sin robot.

Fuente: https://github.com/unitreerobotics/unitree_mujoco

---

## Qué hace

Levanta MuJoCo con `scene_29dof.xml` y publica/suscribe los mismos topics DDS
que el robot real:
- `rt/lowstate` → estado de motores e IMU (igual que el físico)
- `rt/lowcmd` ← comandos de torque/posición (igual que el físico)
- `rt/wirelesscontroller` → botones del mando

Esto permite correr el script de despliegue exactamente igual que con el robot:

```
Terminal 1: python simulacion/sdk_bridge/run_g1_bridge.py
Terminal 2: python despliegue/deploy_motion.py lo motion_agacharse.yaml
```

---

## Requisitos

```bash
conda activate /home/udc/Unitree_G1/envs/g1_udc
pip install unitree-sdk2py mujoco pygame
```

---

## Uso

```bash
conda activate /home/udc/Unitree_G1/envs/g1_udc
cd /home/udc/Unitree_G1
python simulacion/sdk_bridge/run_g1_bridge.py
```

En otra terminal (igual que despliegue real, pero con interfaz "lo"):
```bash
conda activate /home/udc/Unitree_G1/envs/g1_udc
export CYCLONEDDS_HOME=/home/udc/Unitree_G1/humanoide/cyclonedds_install
python despliegue/deploy_motion.py lo motion_agacharse.yaml
```

---

## Diferencias vs sim_motion_policies.py

| | `sim_motion_policies.py` | `sdk_bridge` |
|---|---|---|
| Interface | Python MuJoCo directo | DDS (igual que robot real) |
| Para qué | Validar política rápido | Testear script de deploy completo |
| Mando virtual | No | Sí (pygame/joystick) |
| Capas de seguridad | No | Sí (las del deploy_motion.py) |
