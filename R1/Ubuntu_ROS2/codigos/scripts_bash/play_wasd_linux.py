#!/usr/bin/env python3
# Adaptación Linux de play_wasd.py — usa termios/select en lugar de msvcrt.
"""Control manual del R1 por terminal en Linux.

Uso:
  ./isaaclab.sh -p play_wasd_linux.py \
      --task=R1-Locomotion-Direct-v0 \
      --checkpoint=$HOME/r1_workspace/policies/walk_v1.pt \
      --step=0.5
"""
import argparse
import glob
import importlib
import os
import select
import sys
import termios
import threading
import tty
import queue

from isaaclab.app import AppLauncher

# -------- argparse -------- #
parser = argparse.ArgumentParser(description="R1 — control manual (Linux).")
parser.add_argument("--task", type=str, default="R1-Locomotion-Direct-v0")
parser.add_argument("--checkpoint", type=str, default=None)
parser.add_argument("--num_envs", type=int, default=1)
parser.add_argument("--step", type=float, default=0.5)
AppLauncher.add_app_launcher_args(parser)
args_cli = parser.parse_args()

app_launcher = AppLauncher(args_cli)
simulation_app = app_launcher.app

# -------- post-isaac -------- #
import time  # noqa: E402
import torch  # noqa: E402
import gymnasium as gym  # noqa: E402

from rsl_rl.runners import OnPolicyRunner  # noqa: E402
from isaaclab_rl.rsl_rl import RslRlVecEnvWrapper  # noqa: E402
from isaaclab_tasks.utils import parse_env_cfg  # noqa: E402

import isaaclab_tasks  # noqa: F401, E402

for _mod in ("r1_locomotion.tasks", "r1_standing.tasks", "r1_hierarchical.tasks"):
    try:
        importlib.import_module(_mod)
    except ImportError:
        pass


def find_latest_checkpoint() -> str | None:
    candidates = []
    for g in [
        os.path.expanduser("~/r1_workspace/r1_standing/logs/rsl_rl/*/*/model_*.pt"),
        os.path.expanduser("~/r1_workspace/IsaacLab/logs/rsl_rl/*/*/model_*.pt"),
        "logs/rsl_rl/*/*/model_*.pt",
    ]:
        candidates.extend(glob.glob(g))
    if candidates:
        candidates.sort(key=os.path.getmtime)
        return candidates[-1]
    return None


# ------ termios non-blocking key reader ------ #
class KeyReader:
    def __init__(self):
        self.fd  = sys.stdin.fileno()
        self.old = None

    def __enter__(self):
        self.old = termios.tcgetattr(self.fd)
        tty.setcbreak(self.fd)
        return self

    def __exit__(self, *exc):
        termios.tcsetattr(self.fd, termios.TCSADRAIN, self.old)

    def get_key(self) -> str | None:
        if select.select([sys.stdin], [], [], 0)[0]:
            return sys.stdin.read(1)
        return None


# ------ SimController ------ #
class SimController:
    def __init__(self, device):
        self.device = device
        self._cmd_queue = queue.Queue()
        self.running = True
        self.robot_xy = [0.0, 0.0]
        self.target_xy = [0.0, 0.0]
        self.distance = 0.0
        self._lock = threading.Lock()
        self._needs_reset = False

    def send_target(self, x, y):  self._cmd_queue.put(("set", x, y))
    def send_delta(self, dx, dy): self._cmd_queue.put(("delta", dx, dy))
    def send_stop(self):          self._cmd_queue.put(("stop",))
    def send_reset(self):         self._needs_reset = True

    def process_commands(self, raw_env):
        while not self._cmd_queue.empty():
            try:
                cmd = self._cmd_queue.get_nowait()
                if cmd[0] == "set":
                    raw_env.target_pos_w[0, 0] = cmd[1]
                    raw_env.target_pos_w[0, 1] = cmd[2]
                elif cmd[0] == "delta":
                    raw_env.target_pos_w[0, 0] += cmd[1]
                    raw_env.target_pos_w[0, 1] += cmd[2]
                elif cmd[0] == "stop":
                    raw_env.target_pos_w[0] = raw_env.robot.data.root_pos_w[0, :2].clone()
            except queue.Empty:
                break

    def check_reset(self):
        if self._needs_reset:
            self._needs_reset = False
            return True
        return False

    def update_state(self, raw_env):
        with self._lock:
            rxy = raw_env.robot.data.root_pos_w[0, :2]
            txy = raw_env.target_pos_w[0]
            self.robot_xy = [rxy[0].item(), rxy[1].item()]
            self.target_xy = [txy[0].item(), txy[1].item()]
            self.distance = torch.norm(txy - rxy).item()

    def get_state(self):
        with self._lock:
            return self.robot_xy.copy(), self.target_xy.copy(), self.distance


def input_thread_fn(ctrl: SimController, step: float):
    time.sleep(3.0)
    print("\n=========================================================")
    print("  R1 -- CONTROL MANUAL (Linux)")
    print("  W=+X  S=-X  A=-Y  D=+Y  0=stop  P=pos  R=reset  Q=salir")
    print("=========================================================\n")
    with KeyReader() as kr:
        while ctrl.running:
            ch = kr.get_key()
            if ch:
                ch = ch.lower()
                if ch == "q":
                    ctrl.running = False; break
                elif ch == "w": ctrl.send_delta(step, 0.0)
                elif ch == "s": ctrl.send_delta(-step, 0.0)
                elif ch == "a": ctrl.send_delta(0.0, -step)
                elif ch == "d": ctrl.send_delta(0.0, step)
                elif ch == "0": ctrl.send_stop()
                elif ch == "p":
                    rxy, txy, d = ctrl.get_state()
                    print(f"\n  Robot ({rxy[0]:+.2f},{rxy[1]:+.2f}) Target ({txy[0]:+.2f},{txy[1]:+.2f}) dist={d:.2f}")
                elif ch == "r": ctrl.send_reset()
                if ch in "wasd0":
                    rxy, txy, d = ctrl.get_state()
                    print(f"\r  [{ch.upper()}] target=({txy[0]:+.2f},{txy[1]:+.2f}) dist={d:.2f}m   ",
                          end="", flush=True)
            else:
                time.sleep(0.02)


def main():
    if args_cli.checkpoint and os.path.exists(args_cli.checkpoint):
        ckpt = args_cli.checkpoint
    else:
        ckpt = find_latest_checkpoint()
        if ckpt is None:
            print("[ERROR] sin checkpoint.")
            return
    print(f"[INFO] checkpoint: {ckpt}")

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
    runner.load(ckpt)
    policy = runner.get_inference_policy(device=env.unwrapped.device)

    raw_env = env.unwrapped
    ctrl = SimController(device=raw_env.device)
    t = threading.Thread(target=input_thread_fn, args=(ctrl, args_cli.step), daemon=True)
    t.start()

    if hasattr(raw_env.cfg, "target_resample_on_arrival"):
        raw_env.cfg.target_resample_on_arrival = False
    obs = env.get_observations()
    n = 0
    try:
        while ctrl.running and simulation_app.is_running():
            with torch.inference_mode():
                ctrl.process_commands(raw_env)
                if ctrl.check_reset():
                    env.reset()
                    obs = env.get_observations()
                    if hasattr(raw_env.cfg, "target_resample_on_arrival"):
                        raw_env.cfg.target_resample_on_arrival = False
                    continue
                actions = policy(obs)
                obs, _, dones, _ = env.step(actions)
                policy.reset(dones)
            n += 1
            if n % 30 == 0:
                ctrl.update_state(raw_env)
    except KeyboardInterrupt:
        pass
    finally:
        ctrl.running = False
        env.close()


if __name__ == "__main__":
    main()
    simulation_app.close()
