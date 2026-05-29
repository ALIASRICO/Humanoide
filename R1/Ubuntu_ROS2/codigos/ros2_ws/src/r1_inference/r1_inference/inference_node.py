#!/usr/bin/env python3
"""r1_inference.inference_node — ONNX inference + skill blending.

Subscribe:
  /r1/joint_states  sensor_msgs/JointState
  /r1/imu           sensor_msgs/Imu
  /r1/target_pose   geometry_msgs/Pose2D
  /r1/skill         std_msgs/String

Publish:
  /r1/joint_command sensor_msgs/JointState   (positions = targets)
  /r1/diagnostics   diagnostic_msgs/DiagnosticArray
"""
from __future__ import annotations

import os
import time
import yaml

import numpy as np
import rclpy
from rclpy.node import Node

import onnxruntime as ort

from sensor_msgs.msg import JointState, Imu
from geometry_msgs.msg import Pose2D
from std_msgs.msg import String
from diagnostic_msgs.msg import DiagnosticArray, DiagnosticStatus, KeyValue


class R1InferenceNode(Node):
    def __init__(self):
        super().__init__("r1_inference")

        # ---------- Params ----------
        self.declare_parameter("onnx_stand", "/home/usuario/r1_workspace/policies/stand_v1.onnx")
        self.declare_parameter("onnx_walk",  "/home/usuario/r1_workspace/policies/walk_v1.onnx")
        self.declare_parameter("inference_rate_hz", 50.0)
        self.declare_parameter("action_scale", 0.025)
        self.declare_parameter("walk_action_scale", 0.5)
        self.declare_parameter("joint_order_yaml",
            "/home/usuario/r1_workspace/ros2_ws/src/r1_bringup/config/joint_order_map.yaml")
        self.declare_parameter("default_pose_yaml",
            "/home/usuario/r1_workspace/ros2_ws/src/r1_bringup/config/default_pose.yaml")
        self.declare_parameter("arrival_threshold", 0.3)
        self.declare_parameter("safety_clip", 1.0)
        self.declare_parameter("skill_default", "auto")

        onnx_stand = self.get_parameter("onnx_stand").value
        onnx_walk  = self.get_parameter("onnx_walk").value
        rate       = self.get_parameter("inference_rate_hz").value

        # ---------- ONNX sessions ----------
        providers = ["CUDAExecutionProvider", "CPUExecutionProvider"]
        self.sess_stand = ort.InferenceSession(onnx_stand, providers=providers)
        self.sess_walk  = (
            ort.InferenceSession(onnx_walk, providers=providers)
            if os.path.exists(onnx_walk) else None
        )
        self.get_logger().info(f"ONNX stand: {onnx_stand}")
        self.get_logger().info(f"ONNX walk : {onnx_walk if self.sess_walk else 'N/A'}")
        self.get_logger().info(f"Provider : {ort.get_device()}")

        # ---------- Joint order + default pose ----------
        with open(self.get_parameter("joint_order_yaml").value) as f:
            self.joint_map = yaml.safe_load(f) or {}
        with open(self.get_parameter("default_pose_yaml").value) as f:
            dp = yaml.safe_load(f) or {}
        self.default_q = np.array(
            [dp.get(self.joint_map[i], 0.0) for i in sorted(self.joint_map)],
            dtype=np.float32
        )
        self.num_joints = len(self.default_q)

        # ---------- State ----------
        self.last_joints = None    # (q, dq) arrays sized num_joints
        self.last_imu    = None    # quat, gyro, acc
        self.target      = Pose2D()
        self.skill       = self.get_parameter("skill_default").value
        self.estopped    = False
        self.prev_action = np.zeros(self.num_joints, dtype=np.float32)
        self.root_xy     = np.zeros(2, dtype=np.float32)
        self.root_yaw    = 0.0
        self._last_tick_t = time.time()
        self._actual_rate = 0.0

        # ---------- Pub/Sub ----------
        self.sub_js  = self.create_subscription(JointState, "/r1/joint_states", self._on_js, 100)
        self.sub_imu = self.create_subscription(Imu,        "/r1/imu",          self._on_imu, 100)
        self.sub_tgt = self.create_subscription(Pose2D,     "/r1/target_pose",  self._on_target, 10)
        self.sub_sk  = self.create_subscription(String,     "/r1/skill",        self._on_skill, 10)

        self.pub_cmd  = self.create_publisher(JointState, "/r1/joint_command", 10)
        self.pub_diag = self.create_publisher(DiagnosticArray, "/r1/diagnostics", 10)

        # ---------- Timer ----------
        self.timer = self.create_timer(1.0 / rate, self._tick)
        self.timer_diag = self.create_timer(0.5, self._publish_diag)

    # ---------------------- Callbacks ----------------------
    def _on_js(self, msg: JointState):
        if not msg.position or len(msg.position) < self.num_joints:
            return
        q  = np.array(msg.position[:self.num_joints], dtype=np.float32)
        dq = (np.array(msg.velocity[:self.num_joints], dtype=np.float32)
              if len(msg.velocity) >= self.num_joints
              else np.zeros(self.num_joints, dtype=np.float32))
        self.last_joints = (q, dq)

    def _on_imu(self, msg: Imu):
        from math import atan2
        q = msg.orientation
        # yaw from quaternion (z,w)
        siny_cosp = 2 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1 - 2 * (q.y * q.y + q.z * q.z)
        self.root_yaw = atan2(siny_cosp, cosy_cosp)
        # gravedad proyectada en body
        gx = 2 * (q.x * q.z - q.w * q.y)
        gy = 2 * (q.y * q.z + q.w * q.x)
        gz = 1 - 2 * (q.x * q.x + q.y * q.y)
        self.last_imu = {
            "grav_b": np.array([gx, gy, gz], dtype=np.float32) * (-1.0),
            "ang_vel_b": np.array([msg.angular_velocity.x,
                                    msg.angular_velocity.y,
                                    msg.angular_velocity.z], dtype=np.float32),
            "lin_acc_b": np.array([msg.linear_acceleration.x,
                                    msg.linear_acceleration.y,
                                    msg.linear_acceleration.z], dtype=np.float32),
        }

    def _on_target(self, msg: Pose2D): self.target = msg
    def _on_skill(self, msg: String):  self.skill = msg.data or "auto"

    # ---------------------- Main loop ----------------------
    def _select_skill(self) -> str:
        if self.skill != "auto":
            return self.skill
        d = float(np.hypot(self.target.x - self.root_xy[0],
                           self.target.y - self.root_xy[1]))
        if d < self.get_parameter("arrival_threshold").value or self.sess_walk is None:
            return "stand"
        return "walk"

    def _build_obs_stand(self, q, dq) -> np.ndarray:
        # 88 dims (ver doc 02 §2)
        grav = self.last_imu["grav_b"] if self.last_imu else np.array([0, 0, -1], dtype=np.float32)
        ang  = self.last_imu["ang_vel_b"] if self.last_imu else np.zeros(3, dtype=np.float32)
        lin  = np.zeros(3, dtype=np.float32)   # no se mide directamente; podría venir de odometría
        joint_dev = q - self.default_q
        # feet_dist no lo medimos directamente desde JointState; placeholder
        feet_d = np.array([0.28], dtype=np.float32)
        obs = np.concatenate([grav, ang, lin, joint_dev, dq, self.prev_action, feet_d]).astype(np.float32)
        # padding/trim a 88 si hay desfase
        if obs.shape[0] != 88:
            tmp = np.zeros(88, dtype=np.float32)
            tmp[:min(88, obs.shape[0])] = obs[:88]
            obs = tmp
        return obs

    def _build_obs_walk(self, q, dq) -> np.ndarray:
        # 97 dims = 88 + cmd(9)
        proprio = self._build_obs_stand(q, dq)
        # Comando en body frame
        cy, sy = np.cos(self.root_yaw), np.sin(self.root_yaw)
        diff_w = np.array([self.target.x - self.root_xy[0],
                           self.target.y - self.root_xy[1]], dtype=np.float32)
        target_x_b =  cy * diff_w[0] + sy * diff_w[1]
        target_y_b = -sy * diff_w[0] + cy * diff_w[1]
        yaw_err = (self.target.theta - self.root_yaw)
        yaw_err = (yaw_err + np.pi) % (2 * np.pi) - np.pi
        cmd = np.array([
            target_x_b, target_y_b, yaw_err, 5.0,   # t_remain placeholder
            float(np.linalg.norm(diff_w)),
            0, 0, 0, 0,                              # height placeholders
        ], dtype=np.float32)
        return np.concatenate([proprio, cmd]).astype(np.float32)

    def _tick(self):
        now = time.time()
        self._actual_rate = 1.0 / max(1e-3, now - self._last_tick_t)
        self._last_tick_t = now

        if self.estopped or self.last_joints is None or self.last_imu is None:
            return

        q, dq = self.last_joints
        skill = self._select_skill()

        if skill == "stand":
            obs = self._build_obs_stand(q, dq)[None]
            scale = self.get_parameter("action_scale").value
            sess = self.sess_stand
        else:
            obs = self._build_obs_walk(q, dq)[None]
            scale = self.get_parameter("walk_action_scale").value
            sess = self.sess_walk or self.sess_stand

        try:
            inputs = {sess.get_inputs()[0].name: obs}
            action = sess.run(None, inputs)[0][0]
        except Exception as e:
            self.get_logger().error(f"ONNX run falló: {e}")
            return

        # Safety clip
        clip = self.get_parameter("safety_clip").value
        action = np.clip(action, -clip, clip)
        self.prev_action = action.astype(np.float32)

        # Convertir a target absoluto (default + scale * action)
        target_q = self.default_q + scale * action

        # Reordenar sim → sdk si es necesario (asumimos índice == índice del map)
        # En este esqueleto, los índices ya coinciden con joint_order_map keys.

        # Publicar
        out = JointState()
        out.header.stamp = self.get_clock().now().to_msg()
        out.name     = [self.joint_map[i] for i in sorted(self.joint_map)]
        out.position = target_q.tolist()
        self.pub_cmd.publish(out)

    # ---------------------- Diagnostics ----------------------
    def _publish_diag(self):
        msg = DiagnosticArray()
        msg.header.stamp = self.get_clock().now().to_msg()
        s = DiagnosticStatus()
        s.name  = "r1_inference"
        s.level = DiagnosticStatus.OK if not self.estopped else DiagnosticStatus.ERROR
        s.message = "running" if not self.estopped else "estopped"
        s.values = [
            KeyValue(key="rate_hz",       value=f"{self._actual_rate:.2f}"),
            KeyValue(key="skill_active",  value=self._select_skill()),
            KeyValue(key="estopped",      value=str(self.estopped)),
            KeyValue(key="target_x",      value=f"{self.target.x:.2f}"),
            KeyValue(key="target_y",      value=f"{self.target.y:.2f}"),
            KeyValue(key="action_max",    value=f"{float(np.abs(self.prev_action).max()):.3f}"),
        ]
        msg.status.append(s)
        self.pub_diag.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = R1InferenceNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
