# Copyright (c) 2022-2026, The Isaac Lab Project Developers.
# SPDX-License-Identifier: BSD-3-Clause
"""Configuración PPO para RSL-RL — versión limpia."""

from isaaclab.utils import configclass
from isaaclab_rl.rsl_rl import (
    RslRlOnPolicyRunnerCfg,
    RslRlPpoActorCriticCfg,
    RslRlPpoAlgorithmCfg,
)


@configclass
class PPORunnerCfg(RslRlOnPolicyRunnerCfg):
    """Hiperparámetros base para STANDING.

    Para push-recovery / stepping, sobreescribir desde CLI:
        --max_iterations=15000

    Para fine-tune (resume), bajar:
        learning_rate -> 2.5e-4
        entropy_coef  -> 0.001
        clip_param    -> 0.1
        init_noise_std -> 0.5
    """
    num_steps_per_env = 24
    max_iterations    = 4000
    save_interval     = 500
    experiment_name   = "r1_standing"

    obs_groups = {"actor": ["policy"], "critic": ["policy"]}

    actor = {
        "class_name":         "rsl_rl.models.MLPModel",
        "hidden_dims":        [256, 128, 64],
        "activation":         "elu",
        "obs_normalization":  False,
        "stochastic":         True,
        "init_noise_std":     1.0,
    }
    critic = {
        "class_name":        "rsl_rl.models.MLPModel",
        "hidden_dims":       [256, 128, 64],
        "activation":        "elu",
        "obs_normalization": False,
    }

    policy = RslRlPpoActorCriticCfg(
        init_noise_std=1.0,
        actor_obs_normalization=False,
        critic_obs_normalization=False,
        actor_hidden_dims=[256, 128, 64],
        critic_hidden_dims=[256, 128, 64],
        activation="elu",
    )

    algorithm = RslRlPpoAlgorithmCfg(
        value_loss_coef=1.0,
        use_clipped_value_loss=True,
        clip_param=0.2,
        entropy_coef=0.005,
        num_learning_epochs=5,
        num_mini_batches=4,
        learning_rate=1.0e-3,
        schedule="adaptive",
        gamma=0.99,
        lam=0.95,
        desired_kl=0.01,
        max_grad_norm=1.0,
    )


@configclass
class PPORunnerLocomotionCfg(PPORunnerCfg):
    """Hiperparámetros para LOCOMOTION (WASD coordenadas)."""
    num_steps_per_env = 48
    max_iterations    = 10000
    save_interval     = 500
    experiment_name   = "r1_locomotion"

    policy = RslRlPpoActorCriticCfg(
        init_noise_std=1.0,
        actor_obs_normalization=False,
        critic_obs_normalization=False,
        actor_hidden_dims=[512, 256, 128],
        critic_hidden_dims=[512, 256, 128],
        activation="elu",
    )

    algorithm = RslRlPpoAlgorithmCfg(
        value_loss_coef=1.0,
        use_clipped_value_loss=True,
        clip_param=0.2,
        entropy_coef=0.01,
        num_learning_epochs=5,
        num_mini_batches=4,
        learning_rate=5.0e-4,
        schedule="adaptive",
        gamma=0.99,
        lam=0.95,
        desired_kl=0.01,
        max_grad_norm=1.0,
    )


@configclass
class PPORunnerHierarchicalCfg(PPORunnerCfg):
    """Hiperparámetros para la POLÍTICA MADRE (high-level)."""
    num_steps_per_env = 96      # rollouts más largos: madre actúa cada 100 ms
    max_iterations    = 5000
    save_interval     = 500
    experiment_name   = "r1_hierarchical"

    policy = RslRlPpoActorCriticCfg(
        init_noise_std=0.5,
        actor_obs_normalization=False,
        critic_obs_normalization=False,
        actor_hidden_dims=[128, 64],
        critic_hidden_dims=[128, 64],
        activation="elu",
    )

    algorithm = RslRlPpoAlgorithmCfg(
        value_loss_coef=1.0,
        use_clipped_value_loss=True,
        clip_param=0.15,
        entropy_coef=0.003,
        num_learning_epochs=5,
        num_mini_batches=4,
        learning_rate=3.0e-4,
        schedule="adaptive",
        gamma=0.995,            # horizon largo
        lam=0.95,
        desired_kl=0.008,
        max_grad_norm=1.0,
    )
