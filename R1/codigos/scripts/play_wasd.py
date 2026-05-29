# Copyright (c) 2022-2026, The Isaac Lab Project Developers.
# SPDX-License-Identifier: BSD-3-Clause
"""R1 — Control manual por terminal (coordenadas + WASD).

Correcciones respecto a space_r1/play_wasd.py:
  - Búsqueda de checkpoint en más rutas (incluyendo ENV ISAACLAB).
  - Imports de tasks defensivos (no rompen si falta r1_locomotion).
  - --num_envs configurable.
  - Cierre seguro con KeyboardInterrupt.

Diseño: MAIN THREAD = Isaac Sim (rendering/physics). BG THREAD = teclado.
"""

import argparse
import glob
import importlib
import os
import threading
import queue

# msvcrt es solo Windows; en Linux usar tty/select. En Windows va perfecto.
try:
    import msvcrt
    _HAS_MSVCRT = True
except ImportError:
    _HAS_MSVCRT = False
    msvcrt = None

from isaaclab.app import AppLauncher

# ---- argparse ---- #
parser = argparse.ArgumentParser(description="R1 — control manual por terminal.")
parser.add_argument("--task", type=str, default="R1-Locomotion-Direct-v0")
parser.add_argument("--checkpoint", type=str, default=None,
                    help="Ruta al checkpoint .pt (absoluta o relativa).")
parser.add_argument("--num_envs", type=int, default=1)
parser.add_argument("--step", type=float, default=0.5,
                    help="Tamaño del paso de target por tecla (m).")
AppLauncher.add_app_launcher_args(parser)
args_cli = parser.parse_args()

app_launcher = AppLauncher(args_cli)
simulation_app = app_launcher.app

# ---- post-isaac imports ---- #
import time  # noqa: E402
import torch  # noqa: E402
import gymnasium as gym  # noqa: E402

from rsl_rl.runners import OnPolicyRunner  # noqa: E402
from isaaclab_rl.rsl_rl import RslRlVecEnvWrapper  # noqa: E402
from isaaclab_tasks.utils import parse_env_cfg  # noqa: E402

import isaaclab_tasks  # noqa: F401, E402

# Imports defensivos
for _mod in ("r1_locomotion.tasks", "r1_standing.tasks", "r1_hierarchical.tasks"):
    try:
        importlib.import_module(_mod)
    except ImportError:
        pass


# ====================================================================== #
def find_latest_checkpoint() -> str | None:
    search_globs = [
        os.path.join("IsaacLab", "logs", "rsl_rl", "*", "*", "model_*.pt"),
        os.path.join("logs", "rsl_rl", "*", "*", "model_*.pt"),
    ]
    if "ISAACLAB" in os.environ:
        search_globs.append(
            os.path.join(os.environ["ISAACLAB"], "logs", "rsl_rl", "*", "*", "model_*.pt")
        )
    candidates = []
    for g in search_globs:
        candidates.extend(glob.glob(g))
    if candidates:
        candidates.sort(key=os.path.getmtime)
        return candidates[-1]
    return None


# ====================================================================== #
class SimController:
    """Bridge thread-safe entre input thread y sim thread."""
    def __init__(self, device):
        self.device = device
        self._cmd_queue = queue.Queue()
        self.running = True
        self.robot_xy = [0.0, 0.0]
        self.target_xy = [0.0, 0.0]
        self.distance = 0.0
        self._lock = threading.Lock()
        self._needs_reset = False

    def send_target(self, x, y):    self._cmd_queue.put(("set", x, y))
    def send_delta(self, dx, dy):   self._cmd_queue.put(("delta", dx, dy))
    def send_stop(self):            self._cmd_queue.put(("stop",))
    def send_reset(self):           self._needs_reset = True

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


# ====================================================================== #
def print_status(ctrl):
    rxy, txy, d = ctrl.get_state()
    print(f"\n  Robot:  ({rxy[0]:+.2f}, {rxy[1]:+.2f})")
    print(f"  Target: ({txy[0]:+.2f}, {txy[1]:+.2f})")
    print(f"  Dist:   {d:.2f} m")


def mode_coord(ctrl):
    print("\n  ── MODO COORDENADA ──")
    print("  'dx dy', 'abs x y', 'stop', 'p', 'q'\n")
    while ctrl.running:
        try:
            cmd = input("  coord> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not cmd or cmd.lower() == "q":
            break
        if cmd.lower() == "p":
            print_status(ctrl); continue
        if cmd.lower() == "stop":
            ctrl.send_stop(); print("  -> stop"); continue
        try:
            parts = cmd.split()
            if parts[0].lower() == "abs" and len(parts) >= 3:
                x, y = float(parts[1]), float(parts[2])
                ctrl.send_target(x, y)
                print(f"  -> abs ({x:+.2f}, {y:+.2f})")
            elif len(parts) >= 2:
                dx, dy = float(parts[0]), float(parts[1])
                rxy, _, _ = ctrl.get_state()
                ctrl.send_target(rxy[0]+dx, rxy[1]+dy)
                print(f"  -> rel +({dx:+.2f},{dy:+.2f}) -> ({rxy[0]+dx:+.2f},{rxy[1]+dy:+.2f})")
            else:
                print("  formato: dx dy | abs x y | stop | p | q")
        except ValueError:
            print("  números inválidos.")


def mode_keyboard(ctrl, step):
    if not _HAS_MSVCRT:
        print("\n  [ERR] msvcrt no disponible — modo teclado solo en Windows.")
        return
    print("\n  ── MODO TECLADO ──")
    print(f"  paso {step} m | W=+X S=-X A=-Y D=+Y | 0=stop P=pos Q=salir\n")
    while ctrl.running:
        if msvcrt.kbhit():
            ch = msvcrt.getwch().lower()
            if ch == "q": break
            elif ch == "w": ctrl.send_delta(step, 0.0)
            elif ch == "s": ctrl.send_delta(-step, 0.0)
            elif ch == "a": ctrl.send_delta(0.0, -step)
            elif ch == "d": ctrl.send_delta(0.0, step)
            elif ch == "0": ctrl.send_stop(); print("\n  stop")
            elif ch == "p": print_status(ctrl)
            else: continue
            rxy, txy, d = ctrl.get_state()
            print(f"\r  [{ch.upper()}] target=({txy[0]:+.2f},{txy[1]:+.2f}) dist={d:.2f}m   ",
                  end="", flush=True)
        else:
            time.sleep(0.02)


def input_thread_fn(ctrl, step):
    time.sleep(3.0)
    print("\n" + "=" * 55)
    print("  R1 -- CONTROL MANUAL POR TERMINAL")
    print("=" * 55)
    while ctrl.running:
        print("\n  ── MENU ── 1=coord 2=teclado 3=pos 4=reset 5=salir")
        try:
            c = input("\n  opcion> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if   c == "1": mode_coord(ctrl)
        elif c == "2": mode_keyboard(ctrl, step)
        elif c == "3": print_status(ctrl)
        elif c == "4": ctrl.send_reset(); print("  reset")
        elif c == "5": break
        else: print("  inválido.")
    ctrl.running = False


# ====================================================================== #
def main():
    if args_cli.checkpoint and os.path.exists(args_cli.checkpoint):
        ckpt = args_cli.checkpoint
    else:
        ckpt = find_latest_checkpoint()
        if ckpt is None:
            print("[ERROR] Sin checkpoint. Pasa --checkpoint <ruta>.")
            return
    print(f"[INFO] checkpoint: {ckpt}")

    env_cfg = parse_env_cfg(args_cli.task, device=args_cli.device, num_envs=args_cli.num_envs)
    env_cfg.scene.num_envs = args_cli.num_envs
    env = gym.make(args_cli.task, cfg=env_cfg)
    env = RslRlVecEnvWrapper(env)

    spec = gym.spec(args_cli.task)
    agent_entry = spec.kwargs.get("rsl_rl_cfg_entry_point")
    mod_path, cls = agent_entry.rsplit(":", 1)
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
    step_count = 0

    print("[INFO] Sim corriendo en main thread. Menu en ~3 s...")
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

            step_count += 1
            if step_count % 30 == 0:
                ctrl.update_state(raw_env)
    except KeyboardInterrupt:
        print("\n[INFO] interrumpido por usuario.")
    finally:
        ctrl.running = False
        env.close()


if __name__ == "__main__":
    main()
    simulation_app.close()
