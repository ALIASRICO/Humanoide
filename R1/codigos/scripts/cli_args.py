# Copyright (c) 2022-2026, The Isaac Lab Project Developers.
# SPDX-License-Identifier: BSD-3-Clause
"""CLI args compartidos por train.py / play.py de RSL-RL."""
from __future__ import annotations

import argparse
import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from isaaclab_rl.rsl_rl import RslRlBaseRunnerCfg


def add_rsl_rl_args(parser: argparse.ArgumentParser):
    g = parser.add_argument_group("rsl_rl", description="Arguments for RSL-RL agent.")
    g.add_argument("--experiment_name", type=str, default=None,
                   help="Nombre del experimento (override del cfg).")
    g.add_argument("--run_name", type=str, default=None, help="Sufijo del run.")
    g.add_argument("--resume", action="store_true", default=False,
                   help="Reanudar desde checkpoint.")
    g.add_argument("--load_run", type=str, default=None,
                   help="Subcarpeta del run a reanudar.")
    g.add_argument("--checkpoint", type=str, default=None,
                   help="Archivo de checkpoint (model_X.pt) o ruta absoluta.")
    g.add_argument("--logger", type=str, default=None,
                   choices={"wandb", "tensorboard", "neptune"})
    g.add_argument("--log_project_name", type=str, default=None)
    g.add_argument("--transfer_from", type=str, default=None,
                   help="Ruta a checkpoint de otra tarea para transfer learning.")
    g.add_argument("--freeze_layers", type=int, default=0,
                   help="Congelar las primeras N capas (en transfer).")


def parse_rsl_rl_cfg(task_name: str, args_cli: argparse.Namespace) -> "RslRlBaseRunnerCfg":
    from isaaclab_tasks.utils.parse_cfg import load_cfg_from_registry
    cfg = load_cfg_from_registry(task_name, "rsl_rl_cfg_entry_point")
    return update_rsl_rl_cfg(cfg, args_cli)


def update_rsl_rl_cfg(agent_cfg, args_cli: argparse.Namespace):
    if hasattr(args_cli, "seed") and args_cli.seed is not None:
        if args_cli.seed == -1:
            args_cli.seed = random.randint(0, 10000)
        agent_cfg.seed = args_cli.seed
    if args_cli.resume is not None:
        agent_cfg.resume = args_cli.resume
    if args_cli.load_run is not None:
        agent_cfg.load_run = args_cli.load_run
    if args_cli.checkpoint is not None:
        agent_cfg.load_checkpoint = args_cli.checkpoint
    if args_cli.run_name is not None:
        agent_cfg.run_name = args_cli.run_name
    if args_cli.logger is not None:
        agent_cfg.logger = args_cli.logger
    if agent_cfg.logger in {"wandb", "neptune"} and args_cli.log_project_name:
        agent_cfg.wandb_project = args_cli.log_project_name
        agent_cfg.neptune_project = args_cli.log_project_name
    if args_cli.experiment_name is not None:
        agent_cfg.experiment_name = args_cli.experiment_name
    return agent_cfg
