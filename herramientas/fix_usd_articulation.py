#!/usr/bin/env python3
"""
Aplica ArticulationRootAPI al USD generado.
"""

import sys
sys.path.insert(0, "/home/udc/IsaacLab/source/isaaclab")
sys.path.insert(0, "/home/udc/miniconda3/envs/isaaclab/lib/python3.10/site-packages")

from isaaclab.app import AppLauncher
app_launcher = AppLauncher({"headless": True})
simulation_app = app_launcher.app

from pxr import Usd, UsdPhysics, Gf

# Abrir el USD
stage = Usd.Stage.Open("/home/udc/Unitree_G1/escenas/g1_23dof_converted.usd")

# Encontrar el prim del robot
robot_prim = stage.GetPrimAtPath("/g1_humanoid")
if not robot_prim:
    print("No se encontró /g1_humanoid, buscando en raíz...")
    for prim in stage.Traverse():
        if prim.GetName() == "g1_humanoid":
            robot_prim = prim
            break

if robot_prim:
    print(f"Prim encontrado: {robot_prim.GetPath()}")
    
    # Aplicar ArticulationRootAPI
    articulation_api = UsdPhysics.ArticulationRootAPI.Apply(robot_prim)
    
    # También aplicar RigidBodyAPI al pelvis
    pelvis_prim = stage.GetPrimAtPath("/g1_humanoid/pelvis")
    if pelvis_prim:
        rigid_body_api = UsdPhysics.RigidBodyAPI.Apply(pelvis_prim)
        print("RigidBodyAPI aplicado a pelvis")
    
    # Guardar
    stage.GetRootLayer().Save()
    print("USD guardado con ArticulationRootAPI")
else:
    print("No se encontró el prim del robot")
    print("Prims en el stage:")
    for prim in stage.Traverse():
        print(f"  {prim.GetPath()}")

simulation_app.close()
