# Copyright (c) 2022-2026, The Isaac Lab Project Developers.
# SPDX-License-Identifier: BSD-3-Clause
"""Config para R1-Locomotion-Direct-v0 (control por coordenadas).

observation_space = 88 (standing) + 9 (comando) = 97.
"""
from __future__ import annotations

from isaaclab.assets import ArticulationCfg
from isaaclab.envs import DirectRLEnvCfg
from isaaclab.scene import InteractiveSceneCfg
from isaaclab.sim import SimulationCfg
from isaaclab.utils import configclass

from ..standing.r1_standing_env_cfg import R1_CFG  # mismo asset


@configclass
class R1LocomotionEnvCfg(DirectRLEnvCfg):
    """Política WASD: target = (x*, y*, ψ*), velocidad emergente."""

    # --- Timing ---
    decimation       = 2
    episode_length_s = 30.0       # episodios más largos para navegación

    # --- Spaces ---
    action_space      = 26
    observation_space = 88 + 9    # 97
    state_space       = 0

    # --- Sim ---
    sim: SimulationCfg = SimulationCfg(dt=1 / 120, render_interval=decimation)

    # --- Robot ---
    robot_cfg: ArticulationCfg = R1_CFG.replace(prim_path="/World/envs/env_.*/R1")

    # --- Scene ---
    scene: InteractiveSceneCfg = InteractiveSceneCfg(
        num_envs=4096,
        env_spacing=8.0,
        replicate_physics=True,
    )

    # --- Joint control ---
    joint_names  = [".*joint"]
    action_scale = 0.5            # mucho más alto que standing (0.025)

    # --- Reward shaping ---
    reward_shaper_scale = 0.1

    # ===================================================== #
    # COMANDO POR COORDENADAS
    # ===================================================== #
    target_resample_on_arrival = True
    target_radius_min = 1.0
    target_radius_max = 5.0
    target_arrival_threshold = 0.3
    target_speed_for_eta = 1.0    # m/s — para t_remain inicial

    # ===================================================== #
    # REWARDS DE LOCOMOCIÓN (doc 05 §4)
    # ===================================================== #
    rew_scale_arrival       = 50.0
    rew_scale_move_to       =  2.0    # solo iters < 150
    rew_scale_stand_still   =  5.0
    rew_scale_yaw           = 10.0
    rew_scale_action_rate   =  0.05
    rew_scale_alive         =  1.0
    rew_scale_terminated    = 200.0
    rew_scale_speed_shortfall = 1.0

    # NO penalizar lin_vel — la velocidad es la herramienta
    rew_scale_lin_vel = 0.0
    rew_scale_ang_vel = -0.05

    # Mantener postura mínima
    rew_scale_orientation = 5.0
    rew_scale_base_height = 5.0
    target_base_height    = 0.75
    rew_scale_terminated_fall = -200.0

    # Domain Randomization (activar tras iter 5000 vía resume)
    add_obs_noise = False


@configclass
class R1LocomotionPlaygroundEnvCfg(R1LocomotionEnvCfg):
    """Locomoción + terreno rugoso/slopes (sin escaleras)."""
    def __post_init__(self):
        if hasattr(super(), "__post_init__"):
            super().__post_init__()
        # Importar terreno solo si está disponible
        try:
            from ..playground.rough_terrain_cfg import ROUGH_PLAYGROUND_TERRAIN_CFG
            self.scene.terrain = ROUGH_PLAYGROUND_TERRAIN_CFG
        except ImportError:
            pass


@configclass
class R1LocomotionStairsEnvCfg(R1LocomotionEnvCfg):
    """Locomoción + playground completo con escaleras."""
    def __post_init__(self):
        if hasattr(super(), "__post_init__"):
            super().__post_init__()
        try:
            from ..playground.stairs_terrain_cfg import PLAYGROUND_TERRAIN_CFG
            self.scene.terrain = PLAYGROUND_TERRAIN_CFG
        except ImportError:
            pass
