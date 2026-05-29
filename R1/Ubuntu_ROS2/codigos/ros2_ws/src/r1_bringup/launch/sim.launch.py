"""sim.launch.py — bringup contra Isaac Sim (sin robot real).

Lanza:
  - r1_sim_bridge: Isaac Sim env + publica /r1/joint_states, /r1/imu, suscribe target.
  - r1_teleop_keyboard: para mover el target con W/A/S/D.

NOTA: sim_bridge_node debe ejecutarse con isaaclab.sh -p, no con ros2 run.
Este launch SOLO incluye los nodos auxiliares; el bridge lo lanzas a mano.
"""
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package="r1_teleop",
            executable="teleop_keyboard",
            name="r1_teleop",
            output="screen",
            emulate_tty=True,
            parameters=[{"step": 0.5, "use_sim_time": True}],
        ),
    ])
