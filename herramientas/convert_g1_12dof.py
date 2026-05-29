#!/usr/bin/env python3
"""
Convierte g1_12dof.urdf → g1_12dof.usd para IsaacLab.
Garantiza que training y MuJoCo deploy usen el mismo modelo.

Ejecutar con:
    cd ~/IsaacLab && ./isaaclab.sh -p /home/udc/Unitree_G1/convert_g1_12dof.py
"""
import sys
sys.path.insert(0, "/home/udc/IsaacLab/source/isaaclab")

from isaaclab.app import AppLauncher

app_launcher = AppLauncher({"headless": True})
simulation_app = app_launcher.app

from isaaclab.sim.converters import UrdfConverter, UrdfConverterCfg

URDF_PATH = "/home/udc/Unitree_G1/unitree_rl_gym/resources/robots/g1_description/g1_12dof.urdf"
USD_DIR   = "/home/udc/Unitree_G1/unitree_rl_gym/resources/robots/g1_description"
USD_NAME  = "g1_12dof.usd"

cfg = UrdfConverterCfg(
    asset_path=URDF_PATH,
    usd_dir=USD_DIR,
    usd_file_name=USD_NAME,
    fix_base=False,
    merge_fixed_joints=True,   # simplifica el modelo (torso/cabeza fijos → merge)
    joint_drive=None,          # sin drives en USD; IsaacLab los gestiona via ActuatorCfg
)

print(f"Convirtiendo: {URDF_PATH}")
print(f"Destino     : {USD_DIR}/{USD_NAME}")
converter = UrdfConverter(cfg)
print(f"[OK] USD generado en: {converter.usd_path}")

simulation_app.close()
