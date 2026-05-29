# Re-exporta para que el registro Gym pueda apuntar al cfg PPO.
from ...agents.rsl_rl_ppo_cfg import (  # noqa: F401
    PPORunnerCfg,
    PPORunnerLocomotionCfg,
    PPORunnerHierarchicalCfg,
)

# Aliases que la entry-point string del gym.register espera
rsl_rl_ppo_cfg = __import__("r1_standing.tasks.direct.r1_standing.agents.rsl_rl_ppo_cfg", fromlist=["*"])
