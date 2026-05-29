"""real.launch.py — bringup completo contra el R1 físico.

Lanza:
  - sdk_bridge      (DDS Unitree ↔ ROS2)
  - inference_node  (ONNX policies + skill blending)
  - teleop_keyboard (publica /r1/target_pose)
"""
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import LaunchConfiguration, EnvironmentVariable
from launch.actions import DeclareLaunchArgument
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    bringup = get_package_share_directory("r1_bringup")
    home = os.environ.get("HOME", "/home/usuario")

    return LaunchDescription([
        DeclareLaunchArgument("network_iface", default_value="eth0"),
        DeclareLaunchArgument("rate_hz", default_value="50.0"),
        DeclareLaunchArgument("onnx_stand",
            default_value=f"{home}/r1_workspace/policies/stand_v1.onnx"),
        DeclareLaunchArgument("onnx_walk",
            default_value=f"{home}/r1_workspace/policies/walk_v1.onnx"),

        Node(
            package="r1_inference",
            executable="sdk_bridge",
            name="r1_sdk_bridge",
            output="screen",
            parameters=[{
                "network_iface": LaunchConfiguration("network_iface"),
                "kp_default": 60.0,
                "kd_default": 2.0,
            }],
        ),

        Node(
            package="r1_inference",
            executable="inference_node",
            name="r1_inference",
            output="screen",
            parameters=[{
                "onnx_stand": LaunchConfiguration("onnx_stand"),
                "onnx_walk":  LaunchConfiguration("onnx_walk"),
                "inference_rate_hz": LaunchConfiguration("rate_hz"),
                "joint_order_yaml": os.path.join(bringup, "config/joint_order_map.yaml"),
                "default_pose_yaml": os.path.join(bringup, "config/default_pose.yaml"),
                "use_sim_time": False,
            }],
        ),

        Node(
            package="r1_teleop",
            executable="teleop_keyboard",
            name="r1_teleop",
            output="screen",
            emulate_tty=True,
            parameters=[{"step": 0.5}],
        ),
    ])
