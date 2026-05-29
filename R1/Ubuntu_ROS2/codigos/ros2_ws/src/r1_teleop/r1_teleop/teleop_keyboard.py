#!/usr/bin/env python3
"""r1_teleop/teleop_keyboard — Teleop por teclado.

W/A/S/D mueven target_pose en frame world (xy en metros).
0     = stop (target = robot pos actual, requiere /r1/joint_states)
+/-   = ajustar paso ±0.1 m
Q     = quit

Publica /r1/target_pose (geometry_msgs/Pose2D) y /r1/skill (std_msgs/String).
"""
from __future__ import annotations

import select
import sys
import termios
import tty

import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Pose2D
from std_msgs.msg import String
from sensor_msgs.msg import Imu


class R1Teleop(Node):
    def __init__(self):
        super().__init__("r1_teleop")
        self.declare_parameter("step", 0.5)
        self.step = float(self.get_parameter("step").value)

        self.target = Pose2D()
        self.skill_msg = String(data="auto")

        self.pub_tgt   = self.create_publisher(Pose2D, "/r1/target_pose", 10)
        self.pub_skill = self.create_publisher(String, "/r1/skill", 10)

        # Para "stop": usar IMU/joint_states no es estrictamente necesario;
        # podemos solo congelar el target o resetear a (0,0).
        self.timer = self.create_timer(0.05, self._tick)

        # Setup terminal
        self._fd = sys.stdin.fileno()
        self._old_attr = termios.tcgetattr(self._fd)
        tty.setcbreak(self._fd)

        self._print_help()

    def _print_help(self):
        print("\n=========================================")
        print(" R1 TELEOP — control por teclado")
        print(" W=+X  A=-Y  S=-X  D=+Y")
        print(" 0=stop (target=0,0)")
        print(" +/-=ajustar paso  Q=salir")
        print(" 1=skill 'auto'  2='stand'  3='walk'  4='stair'")
        print("=========================================\n")

    def _tick(self):
        if select.select([sys.stdin], [], [], 0)[0]:
            ch = sys.stdin.read(1).lower()
            if   ch == "q":
                self.get_logger().info("quit"); rclpy.shutdown(); return
            elif ch == "w": self.target.x += self.step
            elif ch == "s": self.target.x -= self.step
            elif ch == "a": self.target.y -= self.step
            elif ch == "d": self.target.y += self.step
            elif ch == "0": self.target = Pose2D()
            elif ch == "+": self.step *= 1.5; print(f"  step={self.step:.2f}")
            elif ch == "-": self.step /= 1.5; print(f"  step={self.step:.2f}")
            elif ch == "1": self.skill_msg.data = "auto"; self.pub_skill.publish(self.skill_msg); print(" skill=auto")
            elif ch == "2": self.skill_msg.data = "stand"; self.pub_skill.publish(self.skill_msg); print(" skill=stand")
            elif ch == "3": self.skill_msg.data = "walk"; self.pub_skill.publish(self.skill_msg); print(" skill=walk")
            elif ch == "4": self.skill_msg.data = "stair"; self.pub_skill.publish(self.skill_msg); print(" skill=stair")
            else:
                return
            self.pub_tgt.publish(self.target)
            print(f"  target=({self.target.x:+.2f}, {self.target.y:+.2f})")

    def destroy_node(self):
        try:
            termios.tcsetattr(self._fd, termios.TCSADRAIN, self._old_attr)
        except Exception:
            pass
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = R1Teleop()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
