#!/usr/bin/env python3
"""sdk_bridge — Puente entre Unitree DDS y ROS2.

Subscribe (DDS Unitree):
  rt/lowstate  → /r1/joint_states + /r1/imu

Publish (DDS Unitree):
  rt/lowcmd    ← /r1/joint_command

Notas:
  - Importa unitree_sdk2_python defensivamente para que el paquete compile
    aunque el SDK no esté instalado todavía.
  - PD gains configurables por param.
"""
from __future__ import annotations

import os
import threading

import numpy as np
import rclpy
from rclpy.node import Node

from sensor_msgs.msg import JointState, Imu

# ----- Import defensivo del SDK ----- #
try:
    from unitree_sdk2py.core.channel import (
        ChannelFactoryInitialize,
        ChannelPublisher,
        ChannelSubscriber,
    )
    from unitree_sdk2py.idl.unitree_hg.msg.dds_ import LowState_, LowCmd_  # type: ignore
    HAS_SDK = True
except Exception as e:
    HAS_SDK = False
    _SDK_ERR = str(e)


class R1SdkBridge(Node):
    def __init__(self):
        super().__init__("r1_sdk_bridge")

        self.declare_parameter("network_iface", os.environ.get("UNITREE_NETWORK_INTERFACE", "eth0"))
        self.declare_parameter("domain_id",     int(os.environ.get("UNITREE_DOMAIN_ID", "0")))
        self.declare_parameter("num_joints",    26)
        # Ganancias PD (por defecto suaves; subir tras calibración)
        self.declare_parameter("kp_default", 60.0)
        self.declare_parameter("kd_default", 2.0)

        n = int(self.get_parameter("num_joints").value)
        self.num_joints = n
        self.kp = np.full(n, self.get_parameter("kp_default").value, dtype=np.float32)
        self.kd = np.full(n, self.get_parameter("kd_default").value, dtype=np.float32)

        # ---------- Pub ROS2 ----------
        self.pub_js  = self.create_publisher(JointState, "/r1/joint_states", 100)
        self.pub_imu = self.create_publisher(Imu,        "/r1/imu", 100)

        # ---------- Sub ROS2 ----------
        self.sub_cmd = self.create_subscription(
            JointState, "/r1/joint_command", self._on_cmd, 100
        )

        # ---------- DDS ----------
        if not HAS_SDK:
            self.get_logger().error(
                f"unitree_sdk2_python no disponible: {_SDK_ERR}. "
                "El nodo correrá pero NO se comunicará con el robot real."
            )
            self._sdk_ok = False
            return

        iface = self.get_parameter("network_iface").value
        domain = int(self.get_parameter("domain_id").value)
        try:
            ChannelFactoryInitialize(domain, iface)
            self._sub_state = ChannelSubscriber("rt/lowstate", LowState_)
            self._sub_state.Init(self._on_lowstate, 10)
            self._pub_cmd_dds = ChannelPublisher("rt/lowcmd", LowCmd_)
            self._pub_cmd_dds.Init()
            self._sdk_ok = True
            self._lowcmd = LowCmd_()
            self._lock = threading.Lock()
            self.get_logger().info(f"SDK Unitree init OK on {iface} (domain={domain})")
        except Exception as e:
            self.get_logger().error(f"SDK init falló: {e}")
            self._sdk_ok = False

    # ----------------------------------------------------- #
    def _on_lowstate(self, msg):
        # Joint state
        try:
            n = self.num_joints
            js = JointState()
            js.header.stamp = self.get_clock().now().to_msg()
            js.position = [float(msg.motor_state[i].q)       for i in range(n)]
            js.velocity = [float(msg.motor_state[i].dq)      for i in range(n)]
            js.effort   = [float(msg.motor_state[i].tau_est) for i in range(n)]
            self.pub_js.publish(js)

            # IMU
            imu = Imu()
            imu.header.stamp = js.header.stamp
            acc = msg.imu_state.accelerometer
            gyr = msg.imu_state.gyroscope
            quat = msg.imu_state.quaternion
            imu.linear_acceleration.x = float(acc[0])
            imu.linear_acceleration.y = float(acc[1])
            imu.linear_acceleration.z = float(acc[2])
            imu.angular_velocity.x = float(gyr[0])
            imu.angular_velocity.y = float(gyr[1])
            imu.angular_velocity.z = float(gyr[2])
            imu.orientation.w = float(quat[0])
            imu.orientation.x = float(quat[1])
            imu.orientation.y = float(quat[2])
            imu.orientation.z = float(quat[3])
            self.pub_imu.publish(imu)
        except Exception as e:
            self.get_logger().warn(f"_on_lowstate: {e}")

    def _on_cmd(self, msg: JointState):
        if not self._sdk_ok:
            return
        n = min(self.num_joints, len(msg.position))
        with self._lock:
            for i in range(n):
                self._lowcmd.motor_cmd[i].q   = float(msg.position[i])
                self._lowcmd.motor_cmd[i].dq  = 0.0
                self._lowcmd.motor_cmd[i].kp  = float(self.kp[i])
                self._lowcmd.motor_cmd[i].kd  = float(self.kd[i])
                self._lowcmd.motor_cmd[i].tau = 0.0
            self._pub_cmd_dds.Write(self._lowcmd)


def main(args=None):
    rclpy.init(args=args)
    node = R1SdkBridge()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
