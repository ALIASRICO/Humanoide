"""
Inspección de joints y DOF del G1 en Isaac Sim.
Muestra todos los joints, límites, posiciones default y orden del DOF.

Uso:
    conda run -n isaaclab python codigos/isaac_sim/inspect_g1_joints.py
"""
import os
import sys

# Asegurar que IsaacLab está en el path
ISAACLAB_PATH = "/home/udc/IsaacLab"
if ISAACLAB_PATH not in sys.path:
    sys.path.insert(0, os.path.join(ISAACLAB_PATH, "source", "isaaclab"))

from isaacsim import SimulationApp
app = SimulationApp({"headless": True})

import torch
import isaaclab.sim as sim_utils
from isaaclab.assets import ArticulationCfg, Articulation
from isaaclab.actuators import ImplicitActuatorCfg
from isaaclab.sim import SimulationContext

# Paths del URDF G1
URDF_PATH = "/home/udc/Humanoide/G1/escenas/g1_29dof.xml"

sim_cfg = sim_utils.SimulationCfg(dt=0.005)
sim = SimulationContext(sim_cfg)

import mujoco
model = mujoco.MjModel.from_xml_path(URDF_PATH)

print("\n" + "="*60)
print(f"G1 — {model.nq} DOF, {model.njnt} joints")
print("="*60)
print(f"{'#':<4} {'Joint':<35} {'Pos min':>10} {'Pos max':>10} {'Default':>10}")
print("-"*60)

for i in range(model.njnt):
    name = mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_JOINT, i)
    if name is None:
        continue
    jnt_type = model.jnt_type[i]
    if jnt_type == mujoco.mjtJoint.mjJNT_FREE:
        continue
    qadr = model.jnt_qposadr[i]
    lower = model.jnt_range[i, 0]
    upper = model.jnt_range[i, 1]
    default = model.qpos0[qadr]
    print(f"{i:<4} {name:<35} {lower:>10.3f} {upper:>10.3f} {default:>10.3f}")

print("="*60)
app.close()
