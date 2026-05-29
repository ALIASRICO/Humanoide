# Copyright (c) 2022-2026, The Isaac Lab Project Developers.
# SPDX-License-Identifier: BSD-3-Clause
"""Lista las tareas registradas relacionadas con R1.

Cambio respecto al repo: filtra por "R1" en lugar de "Template-".
"""
import argparse

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description="List Isaac Lab environments.")
parser.add_argument("--keyword", type=str, default=None)
args_cli = parser.parse_args()

app_launcher = AppLauncher(headless=True)
simulation_app = app_launcher.app

import gymnasium as gym  # noqa: E402
from prettytable import PrettyTable  # noqa: E402

for _mod in ("r1_standing.tasks", "r1_locomotion.tasks", "r1_hierarchical.tasks"):
    try:
        __import__(_mod)
    except ImportError:
        pass


def main():
    table = PrettyTable(["S. No.", "Task Name", "Entry Point", "Config"])
    table.title = "R1 Environments registrados en Isaac Lab"
    table.align["Task Name"]   = "l"
    table.align["Entry Point"] = "l"
    table.align["Config"]      = "l"

    idx = 0
    for spec in gym.registry.values():
        if "R1" in spec.id and (args_cli.keyword is None or args_cli.keyword in spec.id):
            cfg = spec.kwargs.get("env_cfg_entry_point", "")
            table.add_row([idx + 1, spec.id, spec.entry_point, cfg])
            idx += 1
    print(table)


if __name__ == "__main__":
    try:
        main()
    finally:
        simulation_app.close()
