#!/usr/bin/env python3
"""
Convierte URDF a USD usando Isaac Sim directamente.
"""

import sys
sys.path.insert(0, "/home/udc/IsaacLab/source/isaaclab")
sys.path.insert(0, "/home/udc/miniconda3/envs/isaaclab/lib/python3.10/site-packages")

from isaaclab.app import AppLauncher
app_launcher = AppLauncher({"headless": True})
simulation_app = app_launcher.app

import omni
from isaaclab.sim.converters import UrdfConverter, UrdfConverterCfg

cfg = UrdfConverterCfg(
    asset_path="/home/udc/Unitree_G1/escenas/g1_23dof.urdf",
    usd_dir="/home/udc/Unitree_G1/escenas",
    usd_file_name="g1_23dof_converted.usd",
    fix_base=False,
    joint_drive=None,
    merge_fixed_joints=False,
)

converter = UrdfConverter(cfg)
print(f"USD generado en: {converter.usd_path}")

simulation_app.close()
