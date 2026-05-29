# Copyright (c) 2022-2026, The Isaac Lab Project Developers.
# SPDX-License-Identifier: BSD-3-Clause

import gymnasium as gym

from . import agents

# Política MADRE: orquesta sub-políticas (standing + locomotion + stairs)
gym.register(
    id="R1-Hierarchical-Direct-v0",
    entry_point=f"{__name__}.hierarchical_env:R1HierarchicalEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point":    f"{__name__}.hierarchical_env:R1HierarchicalEnvCfg",
        "rsl_rl_cfg_entry_point": f"{agents.__name__}.rsl_rl_ppo_cfg:PPORunnerHierarchicalCfg",
    },
)
