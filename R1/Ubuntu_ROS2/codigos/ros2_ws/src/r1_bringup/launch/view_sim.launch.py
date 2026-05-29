"""view_sim.launch.py — RViz2 + robot_state_publisher para visualizar el sim.

Asume que ya está corriendo r1_sim_bridge.
"""
from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    bringup = get_package_share_directory("r1_bringup")
    urdf_path = os.path.join(bringup, "config/r1.urdf")
    rviz_cfg  = os.path.join(bringup, "config/r1_view.rviz")

    return LaunchDescription([
        Node(
            package="robot_state_publisher",
            executable="robot_state_publisher",
            parameters=[{
                "robot_description": open(urdf_path).read() if os.path.exists(urdf_path) else "",
                "use_sim_time": True,
            }],
        ),
        Node(
            package="rviz2",
            executable="rviz2",
            arguments=["-d", rviz_cfg] if os.path.exists(rviz_cfg) else [],
            output="screen",
        ),
    ])
