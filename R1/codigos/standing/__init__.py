# Copyright (c) 2022-2026, The Isaac Lab Project Developers.
# SPDX-License-Identifier: BSD-3-Clause

import gymnasium as gym

from . import agents

# Registro Gym de la política de STANDING (push-recovery)
gym.register(
    id="R1Standing-Direct-v0",
    entry_point=f"{__name__}.r1_standing_env:R1StandingEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point":    f"{__name__}.r1_standing_env_cfg:R1StandingEnvCfg",
        "rsl_rl_cfg_entry_point": f"{agents.__name__}.rsl_rl_ppo_cfg:PPORunnerCfg",
        "skrl_cfg_entry_point":   f"{agents.__name__}:skrl_ppo_cfg.yaml",
    },
)

# Variante "Play" — menos envs, más visual
gym.register(
    id="R1Standing-Direct-Play-v0",
    entry_point=f"{__name__}.r1_standing_env:R1StandingEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point":    f"{__name__}.r1_standing_env_cfg:R1StandingPlayEnvCfg",
        "rsl_rl_cfg_entry_point": f"{agents.__name__}.rsl_rl_ppo_cfg:PPORunnerCfg",
        "skrl_cfg_entry_point":   f"{agents.__name__}:skrl_ppo_cfg.yaml",
    },
)
