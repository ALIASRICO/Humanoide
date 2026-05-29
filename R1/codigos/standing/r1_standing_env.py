# Copyright (c) 2022-2026, The Isaac Lab Project Developers.
# SPDX-License-Identifier: BSD-3-Clause
"""Environment R1 Standing — versión corregida.

Correcciones respecto al repo original:
  - Push API: set_external_force_and_torque (doc 10 §1).
  - reward_shaper_scale leído desde cfg (doc 10 §11).
  - DomeLight idiomático (doc 10 §13).
"""
from __future__ import annotations

import torch
from collections.abc import Sequence

import isaaclab.sim as sim_utils
from isaaclab.assets import Articulation
from isaaclab.envs import DirectRLEnv
from isaaclab.sim.spawners.from_files import GroundPlaneCfg, spawn_ground_plane

from .r1_standing_env_cfg import R1StandingEnvCfg


class R1StandingEnv(DirectRLEnv):
    cfg: R1StandingEnvCfg

    # ------------------------------------------------------------------ #
    # Init
    # ------------------------------------------------------------------ #
    def __init__(self, cfg: R1StandingEnvCfg, render_mode: str | None = None, **kwargs):
        super().__init__(cfg, render_mode, **kwargs)

        self._joint_ids, _ = self.robot.find_joints(self.cfg.joint_names)

        self.joint_pos = self.robot.data.joint_pos
        self.joint_vel = self.robot.data.joint_vel

        self._previous_actions = torch.zeros(
            self.num_envs, len(self._joint_ids), device=self.device
        )

        # Push system
        self.push_interval = max(1, int(
            self.cfg.push_interval_s / (self.cfg.sim.dt * self.cfg.decimation)
        ))
        self._push_timer = torch.zeros(self.num_envs, device=self.device)
        self._root_body_id = 0

        # Detección dinámica de joints/bodies (robusto a USD ordering)
        self._left_foot_id,  _ = self.robot.find_bodies(".*left.*ankle.*")
        self._right_foot_id, _ = self.robot.find_bodies(".*right.*ankle.*")

        self._knee_joint_ids, _ = self.robot.find_joints(".*knee.*")
        self._hip_left_ids,   _ = self.robot.find_joints(".*left.*hip.*")
        self._hip_right_ids,  _ = self.robot.find_joints(".*right.*hip.*")
        self._left_leg_ids,  _  = self.robot.find_joints(
            [".*left.*hip.*", ".*left.*knee.*", ".*left.*ankle.*"]
        )
        self._right_leg_ids, _  = self.robot.find_joints(
            [".*right.*hip.*", ".*right.*knee.*", ".*right.*ankle.*"]
        )

        self._left_arm_all_ids,  _ = self.robot.find_joints(
            [".*left.*shoulder.*", ".*left.*elbow.*"]
        )
        self._right_arm_all_ids, _ = self.robot.find_joints(
            [".*right.*shoulder.*", ".*right.*elbow.*"]
        )

    # ------------------------------------------------------------------ #
    # Scene
    # ------------------------------------------------------------------ #
    def _setup_scene(self):
        self.robot = Articulation(self.cfg.robot_cfg)
        spawn_ground_plane(prim_path="/World/GroundPlane", cfg=GroundPlaneCfg())
        self.scene.clone_environments(copy_from_source=False)

        if self.device == "cpu":
            self.scene.filter_collisions(global_prim_paths=[])

        self.scene.articulations["robot"] = self.robot

        light_cfg = sim_utils.DomeLightCfg(intensity=2000.0, color=(0.75, 0.75, 0.75))
        light_cfg.func("/World/Light", light_cfg)

    # ------------------------------------------------------------------ #
    # Push system — API corregida
    # ------------------------------------------------------------------ #
    def _apply_random_pushes(self):
        env_ids = (self._push_timer >= self.push_interval).nonzero(as_tuple=False).flatten()
        if len(env_ids) == 0:
            return

        forces  = torch.zeros((len(env_ids), 1, 3), device=self.device)
        torques = torch.zeros((len(env_ids), 1, 3), device=self.device)

        rng = self.cfg.push_force_max - self.cfg.push_force_min
        forces[:, 0, 0] = torch.rand(len(env_ids), device=self.device) * rng + self.cfg.push_force_min
        forces[:, 0, 1] = torch.rand(len(env_ids), device=self.device) * rng + self.cfg.push_force_min

        signs = torch.randint(0, 2, (len(env_ids), 2), device=self.device) * 2 - 1
        forces[:, 0, :2] *= signs

        # API soportada: set_external_force_and_torque + write_data_to_sim
        self.robot.set_external_force_and_torque(
            forces=forces,
            torques=torques,
            body_ids=[self._root_body_id],
            env_ids=env_ids,
        )
        self.robot.write_data_to_sim()

        self._push_timer[env_ids] = 0

    # ------------------------------------------------------------------ #
    # RL pipeline
    # ------------------------------------------------------------------ #
    def _pre_physics_step(self, actions: torch.Tensor) -> None:
        self.actions = actions.clone()
        self._push_timer += 1
        self._apply_random_pushes()

    def _apply_action(self) -> None:
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

    # ------------------------------------------------------------------ #
    # Observations
    # ------------------------------------------------------------------ #
    def _get_observations(self) -> dict:
        lf = self.robot.data.body_pos_w[:, self._left_foot_id[0]]
        rf = self.robot.data.body_pos_w[:, self._right_foot_id[0]]
        feet_d = torch.norm(lf[:, :2] - rf[:, :2], dim=-1, keepdim=True)

        obs = torch.cat(
            (
                self.robot.data.projected_gravity_b,                              # 3
                self.robot.data.root_ang_vel_b,                                   # 3
                self.robot.data.root_lin_vel_b,                                   # 3
                self.joint_pos - self.robot.data.default_joint_pos,               # 26
                self.joint_vel,                                                    # 26
                self._previous_actions,                                            # 26
                feet_d,                                                            # 1
            ),
            dim=-1,
        )
        return {"policy": obs}

    # ------------------------------------------------------------------ #
    # Rewards
    # ------------------------------------------------------------------ #
    def _get_rewards(self) -> torch.Tensor:
        lf = self.robot.data.body_pos_w[:, self._left_foot_id[0]]
        rf = self.robot.data.body_pos_w[:, self._right_foot_id[0]]
        com_xy = self.robot.data.root_pos_w[:, :2]

        joint_pos_dev = self.joint_pos - self.robot.data.default_joint_pos
        hip_left_pos_dev   = joint_pos_dev[:, self._hip_left_ids]
        hip_right_pos_dev  = joint_pos_dev[:, self._hip_right_ids]
        left_leg_actions   = self.actions[:, self._left_leg_ids]
        right_leg_actions  = self.actions[:, self._right_leg_ids]
        knee_pos_dev       = joint_pos_dev[:, self._knee_joint_ids]
        left_arm_pos_dev   = joint_pos_dev[:, self._left_arm_all_ids]
        right_arm_pos_dev  = joint_pos_dev[:, self._right_arm_all_ids]
        left_arm_actions   = self.actions[:, self._left_arm_all_ids]
        right_arm_actions  = self.actions[:, self._right_arm_all_ids]

        return _compute_rewards(
            self.cfg.rew_scale_alive,
            self.cfg.rew_scale_terminated,
            self.cfg.rew_scale_base_height,
            self.cfg.rew_scale_orientation,
            self.cfg.rew_scale_joint_pos,
            self.cfg.rew_scale_joint_vel,
            self.cfg.rew_scale_action_rate,
            self.cfg.rew_scale_lin_vel,
            self.cfg.rew_scale_ang_vel,
            self.cfg.rew_scale_recovery,
            self.cfg.rew_scale_feet_separation,
            self.cfg.rew_scale_com_support,
            self.cfg.rew_scale_co_activation,
            self.cfg.rew_scale_sync,
            self.cfg.rew_scale_rigidity,
            float(self.cfg.enable_com_reward),
            self.cfg.target_base_height,
            self.cfg.rew_scale_feet_together,
            self.cfg.target_feet_distance,
            self.cfg.rew_scale_foot_lateral_symmetry,
            self.cfg.rew_scale_com_lateral_balance,
            self.cfg.rew_scale_yaw_rate,
            self.cfg.rew_scale_knee_extension,
            self.cfg.rew_scale_return_to_default,
            self.cfg.rew_scale_bilateral_balance,
            self.cfg.rew_scale_torso_yaw,
            self.cfg.rew_scale_left_arm_crossing,
            self.cfg.rew_scale_arm_symmetry,
            self.cfg.rew_scale_arm_movement,
            self.cfg.reward_shaper_scale,
            self.robot.data.root_pos_w[:, 2],
            self.robot.data.projected_gravity_b,
            joint_pos_dev,
            self.joint_vel,
            self.actions,
            self._previous_actions,
            self.robot.data.root_lin_vel_b,
            self.robot.data.root_ang_vel_b,
            lf, rf, com_xy,
            self.reset_terminated,
            hip_left_pos_dev,
            hip_right_pos_dev,
            left_leg_actions,
            right_leg_actions,
            knee_pos_dev,
            left_arm_pos_dev,
            right_arm_pos_dev,
            left_arm_actions,
            right_arm_actions,
        )

    # ------------------------------------------------------------------ #
    # Done
    # ------------------------------------------------------------------ #
    def _get_dones(self):
        self.joint_pos = self.robot.data.joint_pos
        self.joint_vel = self.robot.data.joint_vel

        time_out  = self.episode_length_buf >= self.max_episode_length - 1
        h         = self.robot.data.root_pos_w[:, 2]
        fallen_h  = h < 0.3
        proj_g    = self.robot.data.projected_gravity_b
        fallen_t  = torch.sum(torch.square(proj_g[:, :2]), dim=-1) > 0.5
        return fallen_h | fallen_t, time_out

    # ------------------------------------------------------------------ #
    # Reset
    # ------------------------------------------------------------------ #
    def _reset_idx(self, env_ids: Sequence[int] | None):
        if env_ids is None:
            env_ids = self.robot._ALL_INDICES
        super()._reset_idx(env_ids)

        jp   = self.robot.data.default_joint_pos[env_ids].clone()
        jv   = self.robot.data.default_joint_vel[env_ids].clone()
        root = self.robot.data.default_root_state[env_ids]
        root[:, :3] += self.scene.env_origins[env_ids]
        root[:, 2]   = self.cfg.initial_base_height

        self._push_timer[env_ids]       = 0.0
        self._previous_actions[env_ids] = 0.0

        self.robot.write_root_pose_to_sim(root[:, :7], env_ids)
        self.robot.write_root_velocity_to_sim(root[:, 7:], env_ids)
        self.robot.write_joint_state_to_sim(jp, jv, None, env_ids)


# ============================================================== #
# Reward TorchScript
# ============================================================== #

@torch.jit.script
def _compute_rewards(
    rew_alive_s: float,
    rew_term_s:  float,
    rew_h_s:     float,
    rew_orient_s:float,
    rew_jp_s:    float,
    rew_jv_s:    float,
    rew_ar_s:    float,
    rew_lv_s:    float,
    rew_av_s:    float,
    rew_rec_s:   float,
    rew_fs_s:    float,
    rew_com_s:   float,
    rew_co_s:    float,
    rew_sync_s:  float,
    rew_rig_s:   float,
    enable_com:  float,
    target_h:    float,
    rew_ft_s:    float,
    target_ft_d: float,
    rew_fls_s:   float,
    rew_clb_s:   float,
    rew_yaw_s:   float,
    rew_ke_s:    float,
    rew_rd_s:    float,
    rew_bb_s:    float,
    rew_ty_s:    float,
    rew_lac_s:   float,
    rew_as_s:    float,
    rew_am_s:    float,
    shaper:      float,
    base_h:      torch.Tensor,
    grav:        torch.Tensor,
    jp_dev:      torch.Tensor,
    jv:          torch.Tensor,
    actions:     torch.Tensor,
    prev_act:    torch.Tensor,
    lin_vel:     torch.Tensor,
    ang_vel:     torch.Tensor,
    lf:          torch.Tensor,
    rf:          torch.Tensor,
    com_xy:      torch.Tensor,
    terminated:  torch.Tensor,
    hip_l_dev:   torch.Tensor,
    hip_r_dev:   torch.Tensor,
    leg_l_act:   torch.Tensor,
    leg_r_act:   torch.Tensor,
    knee_dev:    torch.Tensor,
    arm_l_dev:   torch.Tensor,
    arm_r_dev:   torch.Tensor,
    arm_l_act:   torch.Tensor,
    arm_r_act:   torch.Tensor,
):
    # Base
    rew_alive = rew_alive_s * (1.0 - terminated.float())
    rew_term  = rew_term_s  * terminated.float()

    h_err = torch.square(base_h - target_h)
    rew_h = rew_h_s * torch.exp(-h_err / 0.05)

    orient_err = torch.sum(torch.square(grav[:, :2]), dim=-1)
    rew_orient = rew_orient_s * torch.exp(-orient_err / 0.01)

    rew_jp = rew_jp_s * torch.sum(torch.square(jp_dev), dim=-1)
    rew_jv = rew_jv_s * torch.sum(torch.square(jv), dim=-1)
    rew_ar = rew_ar_s * torch.sum(torch.square(actions - prev_act), dim=-1)
    rew_lv = rew_lv_s * torch.sum(torch.square(lin_vel), dim=-1)
    rew_av = rew_av_s * torch.sum(torch.square(ang_vel), dim=-1)

    foot_d = torch.norm(lf[:, :2] - rf[:, :2], dim=-1)
    sup_c  = (lf[:, :2] + rf[:, :2]) / 2.0
    excess = torch.clamp(foot_d - 0.40, min=0.0)
    rew_fs = -rew_fs_s * torch.square(excess)

    com_err = torch.norm(com_xy - sup_c, dim=-1)
    rew_com = rew_com_s * torch.exp(-com_err / 0.15) * enable_com

    rew_rec = rew_rec_s * (1.0 - orient_err)

    hip_sym = torch.sum(hip_l_dev, dim=-1) + torch.sum(hip_r_dev, dim=-1)
    rew_sym = -0.5 * torch.square(hip_sym)

    co = torch.sum(leg_l_act * leg_r_act, dim=-1)
    rew_co   = -rew_co_s   * torch.square(co)
    rew_sync = -rew_sync_s * torch.square(co)

    is_stat = (torch.abs(jv) < 1e-3).float()
    rew_rig = rew_rig_s * torch.sum(is_stat, dim=-1)

    ft_err = torch.square(foot_d - target_ft_d)
    rew_ft = rew_ft_s * torch.exp(-ft_err / 0.05)

    lf_x = lf[:, 0] - com_xy[:, 0]
    rf_x = rf[:, 0] - com_xy[:, 0]
    rew_fls = rew_fls_s * torch.exp(-torch.square(lf_x + rf_x) / 0.15)

    lat_err = torch.abs(com_xy[:, 0] - sup_c[:, 0])
    rew_clb = rew_clb_s * torch.exp(-lat_err / 0.15)

    rew_yaw = -rew_yaw_s * torch.square(ang_vel[:, 2]) * 0.1
    rew_ke  = rew_ke_s * torch.sum(torch.square(knee_dev), dim=-1)

    o_gate = torch.exp(-orient_err / 0.02)
    total_dev = torch.sum(torch.square(jp_dev), dim=-1)
    rew_rd = rew_rd_s * o_gate * torch.exp(-total_dev / 0.5)

    rew_bb = -rew_bb_s * torch.square(lf[:, 2] - rf[:, 2])

    torso_y = torch.abs(grav[:, 0]) + torch.abs(grav[:, 1])
    rew_ty  = -rew_ty_s * torch.square(torso_y)

    arm_l_dev_sum = torch.sum(torch.abs(arm_l_dev), dim=-1)
    arm_l_act_sq  = torch.sum(torch.square(arm_l_act), dim=-1)
    rew_lac = -rew_lac_s * (torch.square(arm_l_dev_sum - 0.5) + arm_l_act_sq)

    rew_as = -rew_as_s * torch.square(
        torch.sum(arm_l_dev, dim=-1) + torch.sum(arm_r_dev, dim=-1)
    )

    rew_am = -rew_am_s * (
        torch.sum(torch.square(arm_l_act), dim=-1) +
        torch.sum(torch.square(arm_r_act), dim=-1)
    )

    total = (
        rew_alive + rew_term + rew_h + rew_orient
        + rew_jp + rew_jv + rew_ar + rew_lv + rew_av
        + rew_fs + rew_com + rew_rec
        + rew_sym + rew_co + rew_sync + rew_rig
        + rew_ft + rew_fls + rew_clb + rew_yaw
        + rew_ke + rew_rd + rew_bb
        + rew_ty + rew_lac + rew_as + rew_am
    )
    return total * shaper
