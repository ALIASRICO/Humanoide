#!/usr/bin/env python3
"""r1_sim_bridge — corre Isaac Sim con env del R1 + publica/suscribe ROS2.

Uso:
  ${ISAACLAB}/isaaclab.sh -p sim_bridge_node.py \
      --task=R1-Locomotion-Direct-v0 \
      --checkpoint=$HOME/r1_workspace/policies/walk_v1.pt

Diseño:
  - MAIN THREAD: Isaac Sim (gym.step + policy inference).
  - BG THREAD: rclpy.spin para callbacks ROS2.
  - Bridge: cada step publica /r1/joint_states, /r1/imu;
    al recibir /r1/target_pose actualiza raw_env.target_pos_w.
"""
from __future__ import annotations

import argparse
import importlib
import os
import threading

from isaaclab.app import AppLauncher

# ---------- argparse ----------
parser = argparse.ArgumentParser()
parser.add_argument("--task", type=str, default="R1-Locomotion-Direct-v0")
parser.add_argument("--checkpoint", type=str, default=None)
parser.add_argument("--num_envs", type=int, default=1)
parser.add_argument("--ros_domain_id", type=int, default=42)
AppLauncher.add_app_launcher_args(parser)
args_cli = parser.parse_args()

os.environ["ROS_DOMAIN_ID"] = str(args_cli.ros_domain_id)

app_launcher = AppLauncher(args_cli)
simulation_app = app_launcher.app

# ---------- post-isaac ----------
import time  # noqa: E402
import torch  # noqa: E402
import gymnasium as gym  # noqa: E402

from rsl_rl.runners import OnPolicyRunner  # noqa: E402
from isaaclab_rl.rsl_rl import RslRlVecEnvWrapper  # noqa: E402
from isaaclab_tasks.utils import parse_env_cfg  # noqa: E402

import isaaclab_tasks  # noqa: F401, E402

for _mod in ("r1_locomotion.tasks", "r1_standing.tasks"):
    try:
        importlib.import_module(_mod)
    except ImportError:
        pass

# ---------- ROS2 ----------
import rclpy  # noqa: E402
from rclpy.node import Node  # noqa: E402
from sensor_msgs.msg import JointState, Imu  # noqa: E402
from geometry_msgs.msg import Pose2D  # noqa: E402


class R1SimBridgeNode(Node):
    def __init__(self, raw_env):
        super().__init__("r1_sim_bridge")
        self.raw_env = raw_env

        self.pub_js  = self.create_publisher(JointState, "/r1/joint_states", 50)
        self.pub_imu = self.create_publisher(Imu,        "/r1/imu", 50)

        self.sub_tgt = self.create_subscription(
            Pose2D, "/r1/target_pose", self._on_target, 10
        )

    def publish_state(self):
        env = self.raw_env
        js = JointState()
        js.header.stamp = self.get_clock().now().to_msg()
        js.position = env.robot.data.joint_pos[0].cpu().numpy().tolist()
        js.velocity = env.robot.data.joint_vel[0].cpu().numpy().tolist()
        # name vendría del USD; placeholder genérico
        js.name = [f"joint_{i}" for i in range(len(js.position))]
        self.pub_js.publish(js)

        imu = Imu()
        imu.header.stamp = js.header.stamp
        q = env.robot.data.root_quat_w[0].cpu().numpy()
        imu.orientation.w = float(q[0])
        imu.orientation.x = float(q[1])
        imu.orientation.y = float(q[2])
        imu.orientation.z = float(q[3])
        ang = env.robot.data.root_ang_vel_b[0].cpu().numpy()
        imu.angular_velocity.x = float(ang[0])
        imu.angular_velocity.y = float(ang[1])
        imu.angular_velocity.z = float(ang[2])
        # acc placeholder (se podría derivar de root_lin_vel)
        self.pub_imu.publish(imu)

    def _on_target(self, msg: Pose2D):
        if hasattr(self.raw_env, "target_pos_w"):
            self.raw_env.target_pos_w[0, 0] = float(msg.x)
            self.raw_env.target_pos_w[0, 1] = float(msg.y)
            if hasattr(self.raw_env, "target_yaw_w"):
                self.raw_env.target_yaw_w[0] = float(msg.theta)


def main():
    # Cargar env y policy
    env_cfg = parse_env_cfg(args_cli.task, device=args_cli.device, num_envs=args_cli.num_envs)
    env_cfg.scene.num_envs = args_cli.num_envs
    env = gym.make(args_cli.task, cfg=env_cfg)
    env = RslRlVecEnvWrapper(env)

    spec = gym.spec(args_cli.task)
    entry = spec.kwargs.get("rsl_rl_cfg_entry_point")
    mod_path, cls = entry.rsplit(":", 1)
    mod = importlib.import_module(mod_path)
    agent_cfg = getattr(mod, cls)()

    runner = OnPolicyRunner(env, agent_cfg.to_dict(), log_dir=None, device=env_cfg.sim.device)
    if args_cli.checkpoint and os.path.exists(args_cli.checkpoint):
        runner.load(args_cli.checkpoint)
        print(f"[INFO] checkpoint cargado: {args_cli.checkpoint}")
    else:
        print("[WARN] sin checkpoint — actor sin entrenar.")
    policy = runner.get_inference_policy(device=env.unwrapped.device)
    raw_env = env.unwrapped

    # Inicializar ROS2 + nodo + spin en BG thread
    rclpy.init()
    node = R1SimBridgeNode(raw_env)
    spin_thread = threading.Thread(target=rclpy.spin, args=(node,), daemon=True)
    spin_thread.start()

    if hasattr(raw_env.cfg, "target_resample_on_arrival"):
        raw_env.cfg.target_resample_on_arrival = False

    obs = env.get_observations()
    n = 0
    print("[INFO] Sim + ROS2 corriendo. Topics:\n  /r1/joint_states\n  /r1/imu\n  /r1/target_pose")
    try:
        while simulation_app.is_running():
            with torch.inference_mode():
                actions = policy(obs)
                obs, _, dones, _ = env.step(actions)
                policy.reset(dones)
            n += 1
            if n % 4 == 0:    # ~30 Hz si dt*decim≈8ms
                node.publish_state()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
        env.close()


if __name__ == "__main__":
    main()
    simulation_app.close()
