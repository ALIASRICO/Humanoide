# Copyright (c) 2022-2026, The Isaac Lab Project Developers.
# SPDX-License-Identifier: BSD-3-Clause

import gymnasium as gym

from . import agents

# Política de LOCOMOCIÓN por coordenadas (WASD)
gym.register(
    id="R1-Locomotion-Direct-v0",
    entry_point=f"{__name__}.r1_locomotion_env:R1LocomotionEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point":    f"{__name__}.r1_locomotion_env_cfg:R1LocomotionEnvCfg",
        "rsl_rl_cfg_entry_point": f"{agents.__name__}.rsl_rl_ppo_cfg:PPORunnerLocomotionCfg",
    },
)

# Variante con playground (rough + slope)
gym.register(
    id="R1-Locomotion-Playground-Direct-v0",
    entry_point=f"{__name__}.r1_locomotion_env:R1LocomotionEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point":    f"{__name__}.r1_locomotion_env_cfg:R1LocomotionPlaygroundEnvCfg",
        "rsl_rl_cfg_entry_point": f"{agents.__name__}.rsl_rl_ppo_cfg:PPORunnerLocomotionCfg",
    },
)

# Variante con escaleras
gym.register(
    id="R1-Locomotion-Playground-Stairs-Direct-v0",
    entry_point=f"{__name__}.r1_locomotion_env:R1LocomotionEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point":    f"{__name__}.r1_locomotion_env_cfg:R1LocomotionStairsEnvCfg",
        "rsl_rl_cfg_entry_point": f"{agents.__name__}.rsl_rl_ppo_cfg:PPORunnerLocomotionCfg",
    },
)
