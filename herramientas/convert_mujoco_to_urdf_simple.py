#!/usr/bin/env python3
"""
Convierte modelo MuJoCo XML a URDF simple para Isaac Sim.
Version simplificada que genera URDF basico.
"""

import mujoco
import xml.etree.ElementTree as ET

def convert_mujoco_to_urdf(mujoco_xml_path, output_urdf_path):
    """Convierte un modelo MuJoCo XML a URDF basico."""
    
    # Cargar modelo MuJoCo
    model = mujoco.MjModel.from_xml_path(mujoco_xml_path)
    
    # Crear estructura URDF
    robot = ET.Element('robot', name='g1_humanoid')
    
    # Obtener nombres de bodies y joints
    body_names = [model.body(i).name for i in range(model.nbody)]
    joint_names = [model.joint(i).name for i in range(model.njnt)]
    
    print(f"Bodies: {body_names}")
    print(f"Joints: {joint_names}")
    
    # Crear links para cada body
    for i in range(model.nbody):
        body_name = model.body(i).name
        if body_name == "world":
            continue
            
        # Crear link
        link = ET.SubElement(robot, 'link', name=body_name)
        
        # Obtener inercia
        mass = model.body(i).mass[0]
        inertia = model.body(i).inertia
        
        # Crear inertial
        inertial = ET.SubElement(link, 'inertial')
        ET.SubElement(inertial, 'mass', value=str(mass))
        ET.SubElement(inertial, 'inertia', 
                     ixx=str(inertia[0]), iyy=str(inertia[1]), izz=str(inertia[2]),
                     ixy='0.0', ixz='0.0', iyz='0.0')
        
        # Agregar visual y collision (simplificado)
        visual = ET.SubElement(link, 'visual')
        ET.SubElement(visual, 'geometry').append(ET.Element('box', size='0.01 0.01 0.01'))
        
        collision = ET.SubElement(link, 'collision')
        ET.SubElement(collision, 'geometry').append(ET.Element('box', size='0.01 0.01 0.01'))
    
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
        
        body_id = model.joint(i).bodyid[0]
        parent_body_id = model.body(body_id).parentid[0]
        parent_body_name = model.body(parent_body_id).name
        child_body_name = model.body(body_id).name
        
        if parent_body_name == "world":
            continue
        
        # Obtener rango y eje
        range_val = model.joint(i).range
        axis = model.joint(i).axis
        
        joint_pos = model.joint(i).pos
        
        # Crear joint
        joint = ET.SubElement(robot, 'joint', name=joint_name, type=joint_type)
        ET.SubElement(joint, 'parent', link=parent_body_name)
        ET.SubElement(joint, 'child', link=child_body_name)
        ET.SubElement(joint, 'origin', 
                     xyz=f"{joint_pos[0]} {joint_pos[1]} {joint_pos[2]}",
                     rpy="0.0 0.0 0.0")
        ET.SubElement(joint, 'axis', xyz=f"{axis[0]} {axis[1]} {axis[2]}")
        ET.SubElement(joint, 'limit', 
                     lower=str(range_val[0]), upper=str(range_val[1]),
                     effort='100', velocity='10')
    
    # Guardar URDF
    tree = ET.ElementTree(robot)
    ET.indent(tree, space='  ')
    tree.write(output_urdf_path, encoding='utf-8', xml_declaration=True)
    print(f"URDF guardado en: {output_urdf_path}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Uso: python convert_mujoco_to_urdf.py <input.xml> <output.urdf>")
        sys.exit(1)
    
    input_xml = sys.argv[1]
    output_urdf = sys.argv[2]
    
    convert_mujoco_to_urdf(input_xml, output_urdf)
