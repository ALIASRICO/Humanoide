#!/usr/bin/env python3
"""
Convierte URDF a USD y aplica ArticulationRootAPI.
"""

import sys
sys.path.insert(0, "/home/udc/IsaacLab/source/isaaclab")

from isaaclab.app import AppLauncher
app_launcher = AppLauncher({"headless": True})
simulation_app = app_launcher.app

import omni
from isaaclab.sim.converters import UrdfConverter, UrdfConverterCfg
from pxr import Usd, UsdPhysics, Gf, Sdf

# Configurar conversión
cfg = UrdfConverterCfg(
    asset_path="/home/udc/Unitree_G1/escenas/g1_23dof.urdf",
    usd_dir="/home/udc/Unitree_G1/escenas",
    usd_file_name="g1_23dof_fixed.usd",
    fix_base=False,
    joint_drive=None,
    merge_fixed_joints=False,
)

# Convertir
converter = UrdfConverter(cfg)
print(f"USD generado en: {converter.usd_path}")

# Abrir el USD generado
stage = Usd.Stage.Open(converter.usd_path)

# Encontrar el prim raíz del robot
root_prim = None
for prim in stage.Traverse():
    if prim.GetTypeName() == "Xform" and prim.GetName() == "g1_humanoid":
        root_prim = prim
        break

if root_prim:
    print(f"Prim raíz encontrado: {root_prim.GetPath()}")
    
    # Aplicar ArticulationRootAPI al prim raíz
    articulation_api = UsdPhysics.ArticulationRootAPI.Apply(root_prim)
    print("ArticulationRootAPI aplicado")
    
    # Guardar el USD modificado
    stage.GetRootLayer().Save()
    print("USD guardado con ArticulationRootAPI")
else:
    print("No se encontró el prim raíz del robot")
    print("Prims disponibles:")
    for prim in stage.Traverse():
        print(f"  {prim.GetPath()} - {prim.GetTypeName()}")

simulation_app.close()
