# Copyright (c) 2022-2026, The Isaac Lab Project Developers.
# SPDX-License-Identifier: BSD-3-Clause
"""R1HierarchicalEnv — env de la POLÍTICA MADRE.

La madre actúa cada N steps de la sim (10 Hz). Su acción se traduce en:
  - command vector (vx, vy, wz) que va a la hija WALK
  - alpha (gating) que decide si se mezcla con STAND

Acciones bajas = blend(α) entre STAND.act() y WALK.act().
"""
from __future__ import annotations

import torch
from collections.abc import Sequence

import isaaclab.sim as sim_utils
from isaaclab.assets import Articulation, ArticulationCfg
from isaaclab.envs import DirectRLEnv, DirectRLEnvCfg
from isaaclab.scene import InteractiveSceneCfg
from isaaclab.sim import SimulationCfg
from isaaclab.sim.spawners.from_files import GroundPlaneCfg, spawn_ground_plane
from isaaclab.utils import configclass

from ..standing.r1_standing_env_cfg import R1_CFG


@configclass
class R1HierarchicalEnvCfg(DirectRLEnvCfg):
    decimation = 2
    episode_length_s = 30.0

    action_space      = 4    # 3 cmd + 1 skill gating
    observation_space = 16   # proprio summary + goal + obstacles
    state_space       = 0

    sim: SimulationCfg = SimulationCfg(dt=1 / 120, render_interval=decimation)
    robot_cfg: ArticulationCfg = R1_CFG.replace(prim_path="/World/envs/env_.*/R1")

    scene: InteractiveSceneCfg = InteractiveSceneCfg(
        num_envs=2048, env_spacing=8.0, replicate_physics=True,
    )

    # === Sub-policies (rutas a los checkpoints) ===
    stand_ckpt: str = r"D:\space_r1\IsaacLab\logs\rsl_rl\r1_standing\latest\model.pt"
    walk_ckpt:  str = r"D:\space_r1\IsaacLab\logs\rsl_rl\r1_locomotion\latest\model.pt"

    # === Madre: ratios y umbrales ===
    high_level_period = 10           # actúa cada 10 sim steps (10 Hz si dt*decim=0.0167)
    cmd_scale         = 1.0
    arrival_threshold = 0.3

    # Reward shaping
    rew_progress    = 1.0
    rew_arrival     = 50.0
    rew_smooth      = 0.05
    rew_alive       = 1.0
    rew_terminate   = -200.0
    rew_skill_persist = 0.1

    # Joint control para mezclar
    joint_names  = [".*joint"]
    action_scale = 0.5
    reward_shaper_scale = 0.1


class R1HierarchicalEnv(DirectRLEnv):
    cfg: R1HierarchicalEnvCfg

    def __init__(self, cfg: R1HierarchicalEnvCfg, render_mode: str | None = None, **kwargs):
        super().__init__(cfg, render_mode, **kwargs)

        self._joint_ids, _ = self.robot.find_joints(self.cfg.joint_names)

        self.target_pos_w = torch.zeros(self.num_envs, 2, device=self.device)
        self._prev_skill   = torch.zeros(self.num_envs, device=self.device)
        self._high_level_step_counter = 0
        self._last_high_action = torch.zeros(self.num_envs, self.cfg.action_space, device=self.device)
        self._previous_actions = torch.zeros(self.num_envs, len(self._joint_ids), device=self.device)

        # Hijas (frozen)
        self.stand_child = None
        self.walk_child  = None
        self._init_children()

    def _init_children(self):
        """Carga las hijas en inferencia. Lazy import para evitar dep circular."""
        try:
            import os
            from .high_level_planner import FrozenChild
            from ..agents.rsl_rl_ppo_cfg import PPORunnerCfg, PPORunnerLocomotionCfg

            if os.path.exists(self.cfg.stand_ckpt):
                self.stand_child = FrozenChild(
                    self.cfg.stand_ckpt, PPORunnerCfg(), self, str(self.device)
                )
            if os.path.exists(self.cfg.walk_ckpt):
                self.walk_child = FrozenChild(
                    self.cfg.walk_ckpt, PPORunnerLocomotionCfg(), self, str(self.device)
                )
        except Exception as e:
            print(f"[WARN] No se pudieron cargar las hijas: {e}")
            print("[WARN] La madre operará con sub-políticas dummy (zeros).")

    # ----------------------------------------------------- #
    def _setup_scene(self):
        self.robot = Articulation(self.cfg.robot_cfg)
        spawn_ground_plane(prim_path="/World/GroundPlane", cfg=GroundPlaneCfg())
        self.scene.clone_environments(copy_from_source=False)
        if self.device == "cpu":
            self.scene.filter_collisions(global_prim_paths=[])
        self.scene.articulations["robot"] = self.robot
        light_cfg = sim_utils.DomeLightCfg(intensity=2000.0, color=(0.75, 0.75, 0.75))
        light_cfg.func("/World/Light", light_cfg)

    # ----------------------------------------------------- #
    def _pre_physics_step(self, actions: torch.Tensor):
        # La madre solo actualiza su acción cada high_level_period
        if self._high_level_step_counter % self.cfg.high_level_period == 0:
            self._last_high_action = actions.clone()
        self._high_level_step_counter += 1
        self.actions = self._last_high_action

    def _apply_action(self):
        cmd   = self.actions[:, :3] * self.cfg.cmd_scale
        alpha = torch.sigmoid(self.actions[:, 3:4])  # (N, 1)

        # Construir obs para hijas (88 dims standing + 9 dims walk)
        obs_stand = self._build_stand_obs()                        # (N, 88)
        obs_walk  = self._build_walk_obs(cmd)                      # (N, 97)

        # Inferencia de hijas (sin gradientes)
        if self.stand_child is not None:
            a_stand = self.stand_child.act({"policy": obs_stand})
        else:
            a_stand = torch.zeros(self.num_envs, len(self._joint_ids), device=self.device)
        if self.walk_child is not None:
            a_walk = self.walk_child.act({"policy": obs_walk})
        else:
            a_walk = a_stand

        # Soft gating
        a_low = (1 - alpha) * a_stand + alpha * a_walk

        # Aplicar al robot
        target = (
            self.robot.data.default_joint_pos
            + a_low * self.cfg.action_scale
        )
        target = torch.clamp(
            target,
            self.robot.data.soft_joint_pos_limits[:, :, 0],
            self.robot.data.soft_joint_pos_limits[:, :, 1],
        )
        self.robot.set_joint_position_target(target, joint_ids=self._joint_ids)
        self._previous_actions = a_low

    # ----------------------------------------------------- #
    def _build_stand_obs(self) -> torch.Tensor:
        lf, _ = self.robot.find_bodies(".*left.*ankle.*")
        rf, _ = self.robot.find_bodies(".*right.*ankle.*")
        lp = self.robot.data.body_pos_w[:, lf[0]]
        rp = self.robot.data.body_pos_w[:, rf[0]]
        feet_d = torch.norm(lp[:, :2] - rp[:, :2], dim=-1, keepdim=True)
        return torch.cat([
            self.robot.data.projected_gravity_b,
            self.robot.data.root_ang_vel_b,
            self.robot.data.root_lin_vel_b,
            self.robot.data.joint_pos - self.robot.data.default_joint_pos,
            self.robot.data.joint_vel,
            self._previous_actions,
            feet_d,
        ], dim=-1)

    def _build_walk_obs(self, cmd: torch.Tensor) -> torch.Tensor:
        proprio = self._build_stand_obs()  # 88
        # Rellenar 9 dims de comando: (vx, vy, wz, dummy_t, dummy_dist, 4 dummies)
        cmd_pad = torch.cat([
            cmd,
            torch.zeros(self.num_envs, 6, device=self.device),
        ], dim=-1)
        return torch.cat([proprio, cmd_pad], dim=-1)

    # ----------------------------------------------------- #
    def _get_observations(self):
        rxy = self.robot.data.root_pos_w[:, :2]
        diff = self.target_pos_w - rxy
        dist = torch.norm(diff, dim=-1, keepdim=True)
        proj_g = self.robot.data.projected_gravity_b

        # Obs reducida (madre solo necesita resumen)
        obs = torch.cat([
            proj_g,                                     # 3
            self.robot.data.root_ang_vel_b,             # 3
            self.robot.data.root_lin_vel_b,             # 3
            diff,                                        # 2
            dist,                                        # 1
            self.target_pos_w,                           # 2
            self.robot.data.root_pos_w[:, 2:3],         # 1
            self._prev_skill.unsqueeze(-1),             # 1
        ], dim=-1)  # = 16
        return {"policy": obs}

    # ----------------------------------------------------- #
    def _get_rewards(self) -> torch.Tensor:
        rxy  = self.robot.data.root_pos_w[:, :2]
        diff = self.target_pos_w - rxy
        dist = torch.norm(diff, dim=-1)
        terminated = self.reset_terminated.float()

        rew_progress  = -self.cfg.rew_progress * dist
        arrived       = (dist < self.cfg.arrival_threshold).float()
        rew_arrival   = self.cfg.rew_arrival * arrived

        smoothness    = torch.sum(torch.square(self.actions - self._last_high_action), dim=-1)
        rew_smooth    = -self.cfg.rew_smooth * smoothness

        # skill persistence: penaliza cambios de gating
        cur_skill   = (self.actions[:, 3] > 0.0).float()
        skill_chg   = (cur_skill != self._prev_skill).float()
        rew_persist = -self.cfg.rew_skill_persist * skill_chg
        self._prev_skill = cur_skill

        rew_alive   = self.cfg.rew_alive * (1 - terminated)
        rew_term    = self.cfg.rew_terminate * terminated

        total = rew_progress + rew_arrival + rew_smooth + rew_persist + rew_alive + rew_term
        return total * self.cfg.reward_shaper_scale

    # ----------------------------------------------------- #
    def _get_dones(self):
        time_out = self.episode_length_buf >= self.max_episode_length - 1
        h        = self.robot.data.root_pos_w[:, 2]
        fallen_h = h < 0.3
        proj_g   = self.robot.data.projected_gravity_b
        fallen_t = torch.sum(torch.square(proj_g[:, :2]), dim=-1) > 0.5
        return fallen_h | fallen_t, time_out

    # ----------------------------------------------------- #
    def _reset_idx(self, env_ids: Sequence[int] | None):
        if env_ids is None:
            env_ids = self.robot._ALL_INDICES
        super()._reset_idx(env_ids)

        jp = self.robot.data.default_joint_pos[env_ids].clone()
        jv = self.robot.data.default_joint_vel[env_ids].clone()
        root = self.robot.data.default_root_state[env_ids]
        root[:, :3] += self.scene.env_origins[env_ids]
        root[:, 2]   = 0.78

        self.robot.write_root_pose_to_sim(root[:, :7], env_ids)
        self.robot.write_root_velocity_to_sim(root[:, 7:], env_ids)
        self.robot.write_joint_state_to_sim(jp, jv, None, env_ids)

        # Sample target ~ U(disk(2, 5m))
        n = len(env_ids) if isinstance(env_ids, (list, tuple, torch.Tensor)) else self.num_envs
        r   = torch.rand(n, device=self.device) * 3.0 + 2.0
        phi = torch.rand(n, device=self.device) * 2 * torch.pi
        rxy = self.robot.data.root_pos_w[env_ids, :2]
        self.target_pos_w[env_ids, 0] = rxy[:, 0] + r * torch.cos(phi)
        self.target_pos_w[env_ids, 1] = rxy[:, 1] + r * torch.sin(phi)
        self._prev_skill[env_ids] = 0.0
