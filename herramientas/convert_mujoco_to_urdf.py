#!/usr/bin/env python3
"""
Convierte modelo MuJoCo XML a URDF para importar en Isaac Sim.
"""

import mujoco
import numpy as np
from urdf_parser_py.urdf import URDF, Link, Joint, Inertial, Visual, Collision, Mesh, Material, JointDynamics
from urdf_parser_py.urdf import Box as URDFBox
import xml.etree.ElementTree as ET

def convert_mujoco_to_urdf(mujoco_xml_path, output_urdf_path):
    """Convierte un modelo MuJoCo XML a URDF."""
    
    # Cargar modelo MuJoCo
    model = mujoco.MjModel.from_xml_path(mujoco_xml_path)
    data = mujoco.MjData(model)
    
    # Crear estructura URDF
    robot = URDF(name="g1_humanoid")
    
    # Obtener nombres de bodies y joints
    body_names = [model.body(i).name for i in range(model.nbody)]
    joint_names = [model.joint(i).name for i in range(model.njnt)]
    
    print(f"Bodies: {body_names}")
    print(f"Joints: {joint_names}")
    
    # Crear links para cada body
    links = {}
    for i in range(model.nbody):
        body_name = model.body(i).name
        if body_name == "world":
            continue
            
        # Crear link
        link = Link(name=body_name)
        
        # Obtener inercia
        mass = model.body(i).mass[0]
        inertia = model.body(i).inertia
        
        # Crear inertial
        inertial = Inertial(
            mass=mass,
            inertia={
                'ixx': inertia[0],
                'iyy': inertia[1],
                'izz': inertia[2],
                'ixy': 0.0,
                'ixz': 0.0,
                'iyz': 0.0
            }
        )
        link.inertial = inertial
        
        # Agregar visual y collision (simplificado)
        visual = Visual(
            geometry=URDFBox(size='0.01 0.01 0.01'),
            material=Material(name='gray', color='0.5 0.5 0.5 1.0')
        )
        link.visual = [visual]
        
        collision = Collision(
            geometry=URDFBox(size='0.01 0.01 0.01')
        )
        link.collision = [collision]
        
        links[body_name] = link
        robot.add_link(link)
    
    # Crear joints
    for i in range(model.njnt):
        joint_name = model.joint(i).name
        joint_type_num = model.joint(i).type
        
        # Determinar tipo de joint
        if joint_type_num == mujoco.mjtJoint.mjJNT_FREE:
            continue  # Skip free joint (base)
        elif joint_type_num == mujoco.mjtJoint.mjJNT_HINGE:
            joint_type = 'revolute'
        elif joint_type_num == mujoco.mjtJoint.mjJNT_SLIDE:
            joint_type = 'prismatic'
        else:
            joint_type = 'fixed'
        
        # Obtener body padre e hijo
        body_id = model.joint(i).bodyid[0]
        parent_body_name = model.body(model.body(body_id).parentid[0]).name
        child_body_name = model.body(body_id).name
        
        # Obtener rango y eje
        range_val = model.joint(i).range
        axis = model.joint(i).axis
        
        # Crear joint
        joint = Joint(
            name=joint_name,
            parent=parent_body_name,
            child=child_body_name,
            joint_type=joint_type,
            axis=f"{axis[0]} {axis[1]} {axis[2]}",
            limit={'lower': str(range_val[0]), 'upper': str(range_val[1]), 'effort': '100', 'velocity': '10'},
            dynamics=JointDynamics(damping='0.1', friction='0.1')
        )
        
        robot.add_joint(joint)
    
    # Guardar URDF
    with open(output_urdf_path, 'w') as f:
        f.write(robot.to_xml_string())
    print(f"URDF guardado en: {output_urdf_path}")
    
    return robot

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Uso: python convert_mujoco_to_urdf.py <input.xml> <output.urdf>")
        sys.exit(1)
    
    input_xml = sys.argv[1]
    output_urdf = sys.argv[2]
    
    convert_mujoco_to_urdf(input_xml, output_urdf)
