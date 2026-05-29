# Copyright (c) 2022-2026, The Isaac Lab Project Developers.
# SPDX-License-Identifier: BSD-3-Clause
"""R1 Locomotion — control por coordenadas (target_pos_w + ψ* + t_remain).

Diseño basado en arXiv:2209.12827 + recomendaciones_awsd.md.
"""
from __future__ import annotations

import torch
from collections.abc import Sequence

import isaaclab.sim as sim_utils
from isaaclab.assets import Articulation
from isaaclab.envs import DirectRLEnv
from isaaclab.sim.spawners.from_files import GroundPlaneCfg, spawn_ground_plane
from isaaclab.utils.math import quat_from_euler_xyz, yaw_from_quat

from .r1_locomotion_env_cfg import R1LocomotionEnvCfg


class R1LocomotionEnv(DirectRLEnv):
    cfg: R1LocomotionEnvCfg

    def __init__(self, cfg: R1LocomotionEnvCfg, render_mode: str | None = None, **kwargs):
        super().__init__(cfg, render_mode, **kwargs)

        self._joint_ids, _   = self.robot.find_joints(self.cfg.joint_names)
        self._left_foot_id,  _ = self.robot.find_bodies(".*left.*ankle.*")
        self._right_foot_id, _ = self.robot.find_bodies(".*right.*ankle.*")

        self._previous_actions = torch.zeros(self.num_envs, len(self._joint_ids), device=self.device)

        # ===== Comando =====
        # target_pos_w en world frame
        self.target_pos_w  = torch.zeros(self.num_envs, 2, device=self.device)
        self.target_yaw_w  = torch.zeros(self.num_envs, device=self.device)
        self.target_t_rem  = torch.zeros(self.num_envs, device=self.device)
        self._init_pos     = torch.zeros(self.num_envs, 2, device=self.device)
        self._iter_id      = 0

    # ---------------------------------------------------- #
    def _setup_scene(self):
        self.robot = Articulation(self.cfg.robot_cfg)
        if not hasattr(self.scene, "terrain") or self.scene.terrain is None:
            spawn_ground_plane(prim_path="/World/GroundPlane", cfg=GroundPlaneCfg())
        self.scene.clone_environments(copy_from_source=False)

        if self.device == "cpu":
            self.scene.filter_collisions(global_prim_paths=[])

        self.scene.articulations["robot"] = self.robot

        light_cfg = sim_utils.DomeLightCfg(intensity=2000.0, color=(0.75, 0.75, 0.75))
        light_cfg.func("/World/Light", light_cfg)

    # ---------------------------------------------------- #
    def _resample_targets(self, env_ids: torch.Tensor):
        if len(env_ids) == 0:
            return
        r   = torch.rand(len(env_ids), device=self.device) * (
            self.cfg.target_radius_max - self.cfg.target_radius_min
        ) + self.cfg.target_radius_min
        phi = torch.rand(len(env_ids), device=self.device) * 2 * torch.pi

        rxy = self.robot.data.root_pos_w[env_ids, :2]
        self.target_pos_w[env_ids, 0] = rxy[:, 0] + r * torch.cos(phi)
        self.target_pos_w[env_ids, 1] = rxy[:, 1] + r * torch.sin(phi)

        self.target_yaw_w[env_ids] = (torch.rand(len(env_ids), device=self.device) - 0.5) * 2 * torch.pi
        self.target_t_rem[env_ids] = r / max(0.1, self.cfg.target_speed_for_eta)
        self._init_pos[env_ids] = rxy

    # ---------------------------------------------------- #
    def _pre_physics_step(self, actions):
        self.actions = actions.clone()
        # Actualizar t_remain
        self.target_t_rem = torch.clamp(
            self.target_t_rem - self.cfg.sim.dt * self.cfg.decimation, min=0.0
        )

    def _apply_action(self):
        target = (
            self.robot.data.default_joint_pos
            + self.actions * self.cfg.action_scale
        )
        target = torch.clamp(
            target,
            self.robot.data.soft_joint_pos_limits[:, :, 0],
            self.robot.data.soft_joint_pos_limits[:, :, 1],
        )
        self.robot.set_joint_position_target(target, joint_ids=self._joint_ids)
        self._previous_actions = self.actions.clone()

    # ---------------------------------------------------- #
    def _get_observations(self) -> dict:
        # Body frame yaw
        root_quat = self.robot.data.root_quat_w
        yaw = yaw_from_quat(root_quat)
        cos_y, sin_y = torch.cos(yaw), torch.sin(yaw)

        # Vector target en body frame (rotación inversa)
        rxy = self.robot.data.root_pos_w[:, :2]
        diff = self.target_pos_w - rxy
        target_x_b =  cos_y * diff[:, 0] + sin_y * diff[:, 1]
        target_y_b = -sin_y * diff[:, 0] + cos_y * diff[:, 1]

        target_dist = torch.norm(diff, dim=-1, keepdim=True)
        target_yaw_err = (self.target_yaw_w - yaw)
        target_yaw_err = (target_yaw_err + torch.pi) % (2 * torch.pi) - torch.pi

        cmd = torch.stack([
            target_x_b,
            target_y_b,
            target_yaw_err,
            self.target_t_rem,
        ], dim=-1)
        # +1 dummy para alcanzar 9 dims (placeholder para terrain_height futuro x4)
        cmd = torch.cat([
            cmd,
            target_dist,
            torch.zeros(self.num_envs, 4, device=self.device),
        ], dim=-1)  # (N, 9)

        # Standing-style proprio (88)
        lf = self.robot.data.body_pos_w[:, self._left_foot_id[0]]
        rf = self.robot.data.body_pos_w[:, self._right_foot_id[0]]
        feet_d = torch.norm(lf[:, :2] - rf[:, :2], dim=-1, keepdim=True)

        proprio = torch.cat([
            self.robot.data.projected_gravity_b,
            self.robot.data.root_ang_vel_b,
            self.robot.data.root_lin_vel_b,
            self.robot.data.joint_pos - self.robot.data.default_joint_pos,
            self.robot.data.joint_vel,
            self._previous_actions,
            feet_d,
        ], dim=-1)

        obs = torch.cat([proprio, cmd], dim=-1)  # 88 + 9 = 97

        if self.cfg.add_obs_noise:
            obs = obs + 0.01 * torch.randn_like(obs)

        return {"policy": obs}

    # ---------------------------------------------------- #
    def _get_rewards(self) -> torch.Tensor:
        rxy = self.robot.data.root_pos_w[:, :2]
        diff = self.target_pos_w - rxy
        dist = torch.norm(diff, dim=-1)
        terminated = self.reset_terminated.float()

        # Arrival
        arrived = (dist < self.cfg.target_arrival_threshold).float()
        rew_arrival = self.cfg.rew_scale_arrival * arrived

        # Move-to (solo iters tempranos)
        target_dir = diff / (dist.unsqueeze(-1) + 1e-6)
        vel_xy = self.robot.data.root_lin_vel_w[:, :2]
        vel_proj = (vel_xy * target_dir).sum(dim=-1)
        early_phase = float(self._iter_id < 150)
        rew_move = self.cfg.rew_scale_move_to * vel_proj * early_phase

        # Stand still al llegar
        near = (dist < 0.4).float()
        rew_still = -self.cfg.rew_scale_stand_still * near * torch.norm(vel_xy, dim=-1)

        # Yaw track
        root_quat = self.robot.data.root_quat_w
        yaw = yaw_from_quat(root_quat)
        yaw_err = (self.target_yaw_w - yaw)
        yaw_err = (yaw_err + torch.pi) % (2 * torch.pi) - torch.pi
        rew_yaw = self.cfg.rew_scale_yaw * torch.exp(-torch.square(yaw_err) / 0.5)

        # Speed shortfall
        required = dist / torch.clamp(self.target_t_rem, min=0.1)
        shortfall = torch.clamp(required - vel_proj, min=0.0)
        rew_short = -self.cfg.rew_scale_speed_shortfall * shortfall

        # Smoothness
        rew_ar = -self.cfg.rew_scale_action_rate * torch.sum(
            torch.square(self.actions - self._previous_actions), dim=-1
        )

        # Postura mínima
        proj_g = self.robot.data.projected_gravity_b
        orient_err = torch.sum(torch.square(proj_g[:, :2]), dim=-1)
        rew_orient = self.cfg.rew_scale_orientation * torch.exp(-orient_err / 0.05)

        h_err = torch.square(self.robot.data.root_pos_w[:, 2] - self.cfg.target_base_height)
        rew_h = self.cfg.rew_scale_base_height * torch.exp(-h_err / 0.1)

        # Alive / terminate
        rew_alive = self.cfg.rew_scale_alive * (1 - terminated)
        rew_term  = self.cfg.rew_scale_terminated_fall * terminated

        # Resample on arrival
        if self.cfg.target_resample_on_arrival:
            arrived_ids = (dist < self.cfg.target_arrival_threshold).nonzero(as_tuple=False).flatten()
            self._resample_targets(arrived_ids)

        total = (
            rew_arrival + rew_move + rew_still + rew_yaw + rew_short
            + rew_ar + rew_orient + rew_h + rew_alive + rew_term
        )
        return total * self.cfg.reward_shaper_scale

    # ---------------------------------------------------- #
    def _get_dones(self):
        time_out = self.episode_length_buf >= self.max_episode_length - 1
        h        = self.robot.data.root_pos_w[:, 2]
        fallen_h = h < 0.3
        proj_g   = self.robot.data.projected_gravity_b
        fallen_t = torch.sum(torch.square(proj_g[:, :2]), dim=-1) > 0.5
        return fallen_h | fallen_t, time_out

    # ---------------------------------------------------- #
    def _reset_idx(self, env_ids: Sequence[int] | None):
        if env_ids is None:
            env_ids = self.robot._ALL_INDICES
        super()._reset_idx(env_ids)

        jp = self.robot.data.default_joint_pos[env_ids].clone()
        jv = self.robot.data.default_joint_vel[env_ids].clone()
        root = self.robot.data.default_root_state[env_ids]
        root[:, :3] += self.scene.env_origins[env_ids]
        root[:, 2]   = 0.78

        self._previous_actions[env_ids] = 0.0

        self.robot.write_root_pose_to_sim(root[:, :7], env_ids)
        self.robot.write_root_velocity_to_sim(root[:, 7:], env_ids)
        self.robot.write_joint_state_to_sim(jp, jv, None, env_ids)

        # Generar nuevos targets
        if isinstance(env_ids, torch.Tensor):
            self._resample_targets(env_ids)
        else:
            self._resample_targets(torch.as_tensor(list(env_ids), device=self.device, dtype=torch.long))
