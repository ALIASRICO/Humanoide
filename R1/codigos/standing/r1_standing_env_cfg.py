# Copyright (c) 2022-2026, The Isaac Lab Project Developers.
# SPDX-License-Identifier: BSD-3-Clause
"""Config corregida del environment R1 Standing.

Cambios respecto al repo original:
  - Fallback defensivo de R1_CFG si isaaclab_assets no lo trae (doc 10 §3).
  - Comentario de observation_space reescrito (doc 10 §4).
  - reward_shaper_scale expuesto (doc 10 §11).
  - Variante "Play" añadida.
"""
from __future__ import annotations
import os

# ---- R1_CFG defensivo ------------------------------------------------ #
try:
    from isaaclab_assets.robots.r1 import R1_CFG  # noqa: F401
except (ImportError, ModuleNotFoundError):
    import isaaclab.sim as sim_utils
    from isaaclab.actuators import ImplicitActuatorCfg
    from isaaclab.assets import ArticulationCfg

    _USD = os.environ.get(
        "R1_USD_PATH",
        r"D:\space_r1\IsaacLab\source\isaaclab_assets\data\Robots\Unitree\R1\r1.usd",
    )

    R1_CFG = ArticulationCfg(
        spawn=sim_utils.UsdFileCfg(
            usd_path=_USD,
            activate_contact_sensors=True,
            rigid_props=sim_utils.RigidBodyPropertiesCfg(
                disable_gravity=False,
                retain_accelerations=False,
                linear_damping=0.0,
                angular_damping=0.0,
                max_linear_velocity=1000.0,
                max_angular_velocity=1000.0,
                max_depenetration_velocity=1.0,
            ),
            articulation_props=sim_utils.ArticulationRootPropertiesCfg(
                enabled_self_collisions=False,
                solver_position_iteration_count=8,
                solver_velocity_iteration_count=4,
            ),
        ),
        init_state=ArticulationCfg.InitialStateCfg(
            pos=(0.0, 0.0, 0.78),
            joint_pos={".*": 0.0},
        ),
        actuators={
            "all": ImplicitActuatorCfg(
                joint_names_expr=[".*"],
                stiffness=80.0,
                damping=2.0,
            ),
        },
    )

from isaaclab.assets import ArticulationCfg
from isaaclab.envs import DirectRLEnvCfg
from isaaclab.scene import InteractiveSceneCfg
from isaaclab.sim import SimulationCfg
from isaaclab.utils import configclass


@configclass
class R1StandingEnvCfg(DirectRLEnvCfg):
    """Configuración del task R1Standing-Direct-v0."""

    # --- Env timing ---
    decimation        = 2
    episode_length_s  = 20.0

    # --- Spaces ---
    action_space      = 26                          # 26 DOF del R1
    observation_space = 3 + 3 + 3 + 26 + 26 + 26 + 1   # = 88
    # = projected_gravity(3) + root_ang_vel(3) + root_lin_vel(3)
    # + joint_pos_dev(26) + joint_vel(26) + prev_actions(26)
    # + feet_distance(1)
    state_space       = 0

    # --- Simulation ---
    sim: SimulationCfg = SimulationCfg(dt=1 / 120, render_interval=decimation)

    # --- Robot ---
    robot_cfg: ArticulationCfg = R1_CFG.replace(prim_path="/World/envs/env_.*/R1")

    # --- Scene ---
    scene: InteractiveSceneCfg = InteractiveSceneCfg(
        num_envs=8000,
        env_spacing=3.0,
        replicate_physics=True,
    )

    # --- Joint control ---
    joint_names  = [".*joint"]
    action_scale = 0.025                # 0.025 para STANDING, 0.5 para locomotion

    # --- Reward shaping factor ---
    reward_shaper_scale = 0.1            # se multiplica al final de compute_rewards

    # ====================================================== #
    # SCALES (todas etiquetadas con su rol — doc 02 §4)
    # ====================================================== #

    # alive / termination
    rew_scale_alive       =   1.0
    rew_scale_terminated  = -500.0

    # postura
    rew_scale_orientation =  20.0
    rew_scale_base_height =  10.0
    rew_scale_knee_extension = -5.0

    # smoothness
    rew_scale_joint_pos    = -0.02
    rew_scale_joint_vel    = -0.02
    rew_scale_lin_vel      = -0.03
    rew_scale_ang_vel      = -0.05
    rew_scale_action_rate  = -0.03

    # base height
    initial_base_height = 0.75
    target_base_height  = 0.75
    max_tilt_angle      = 0.6

    # PUSH RECOVERY (etapas)
    # Etapa 1 (estática): push_interval_s = 1e9 → OFF
    # Etapa 3 (recovery): push_force_min/max = 5/10 N
    # Etapa 4 (stepping): push_force_min/max = 15/25 N
    push_interval_s = 1.0
    push_force_min  = 5.0
    push_force_max  = 10.0

    # gating de rewards
    enable_com_reward       = 1.0
    enable_feet_penalty_quad = True

    # recovery
    rew_scale_recovery        =  2.0
    rew_scale_feet_separation =  8.0
    rew_scale_com_support     =  1.0

    # pies
    rew_scale_feet_together         = 10.0
    target_feet_distance            = 0.28
    rew_scale_foot_lateral_symmetry = 15.0
    rew_scale_com_lateral_balance   = 12.0

    # giro / yaw
    rew_scale_yaw_rate         = 15.0

    # estructurales
    rew_scale_co_activation    = 0.5
    rew_scale_sync             = 0.3
    rew_scale_rigidity         = 0.05

    # retorno y bilateral
    rew_scale_return_to_default = 6.0
    rew_scale_bilateral_balance = 8.0

    # torso y brazos
    rew_scale_torso_yaw         = 25.0
    rew_scale_left_arm_crossing = 20.0
    rew_scale_arm_symmetry      = 15.0
    rew_scale_arm_movement      =  3.0


@configclass
class R1StandingPlayEnvCfg(R1StandingEnvCfg):
    """Versión 'Play' — pocos envs, sin pushes, para validación visual."""
    def __post_init__(self):
        super().__post_init__() if hasattr(super(), "__post_init__") else None
        self.scene.num_envs    = 4
        self.scene.env_spacing = 3.0
        self.push_interval_s   = 1e9   # OFF
