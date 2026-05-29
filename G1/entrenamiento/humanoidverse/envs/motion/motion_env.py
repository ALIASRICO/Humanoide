import torch
import numpy as np
from loguru import logger
from humanoidverse.envs.legged_base_task.legged_robot_base import LeggedRobotBase
from humanoidverse.utils.torch_utils import torch_rand_float


class MotionEnv(LeggedRobotBase):
    """Environment for training simple motion policies (saludar, agacharse, estirar, munecas)."""

    def __init__(self, config, device):
        self.init_done = False
        self.motion_cfg = config.motion
        self.motion_id = self.motion_cfg.motion_id
        super().__init__(config, device)
        self.init_done = True
        logger.info(f"MotionEnv initialized — motion_id={self.motion_id} ({self.motion_name})")

    def _init_buffers(self):
        super()._init_buffers()
        
        # Load motion poses from config
        self._init_motion_poses()
        
        # Phase tracking for periodic motions
        self.phase = torch.zeros(self.num_envs, device=self.device)
        self.phase_signal = torch.zeros(self.num_envs, 1, device=self.device)
        
        # Current target pose (n_envs, num_dof)
        self.q_target = torch.zeros(self.num_envs, self.num_dof, device=self.device)
        
        # Action history for smoothness penalty
        self.last_actions_for_smoothness = torch.zeros(self.num_envs, self.dim_actions, device=self.device)

    def _init_motion_poses(self):
        """Convert motion poses from config to tensors."""
        motions = self.config.motion
        
        # Get motion config based on motion_id
        motion_names = ['saludar', 'agacharse', 'estirar_brazos', 'mover_munecas']
        self.motion_name = motion_names[self.motion_id]
        motion_data = motions[self.motion_name]
        
        self.is_periodic = motion_data.get('periodic', False)
        self.period_s = motion_data.get('period_s', 1.0)
        self.duration_s = motion_data.get('duration_s', 2.0)
        
        # Build default pose (all zeros for upper body, default values for legs)
        default_pose = self.default_dof_pos.clone().squeeze(0)  # (num_dof,)
        
        # Build pose A (for all motions)
        self.pose_A = default_pose.unsqueeze(0).repeat(self.num_envs, 1).clone()
        if 'pose_A' in motion_data:
            for joint_name, angle in motion_data['pose_A'].items():
                idx = self.dof_names.index(joint_name)
                self.pose_A[:, idx] = angle
        
        # Build pose B (for periodic motions)
        self.pose_B = self.pose_A.clone()
        if 'pose_B' in motion_data:
            for joint_name, angle in motion_data['pose_B'].items():
                idx = self.dof_names.index(joint_name)
                self.pose_B[:, idx] = angle
        
        # Build pose target (for non-periodic motions)
        self.pose_target = default_pose.unsqueeze(0).repeat(self.num_envs, 1).clone()
        if 'pose_target' in motion_data:
            for joint_name, angle in motion_data['pose_target'].items():
                idx = self.dof_names.index(joint_name)
                self.pose_target[:, idx] = angle
        
        # Indices for upper body (12-28) and lower body (0-11)
        self.upper_dof_indices = list(range(12, self.num_dof))
        self.lower_dof_indices = list(range(12))

    def _compute_phase(self):
        """Compute phase for periodic motions."""
        if self.is_periodic:
            # phase = 2*pi * (episode_step * dt) / period
            self.phase = 2.0 * np.pi * (self.episode_length_buf.float() * self.dt) / self.period_s
            self.phase_signal = torch.sin(self.phase).unsqueeze(1)
        else:
            # For non-periodic: phase goes 0 -> 1 over duration
            self.phase = (self.episode_length_buf.float() * self.dt) / self.duration_s
            self.phase_signal = torch.sin(self.phase * np.pi).unsqueeze(1)  # 0 -> 1 -> 0

    def _get_current_target(self):
        """Get current target pose based on phase."""
        if self.is_periodic:
            # Interpolate between pose_A and pose_B using sinusoidal phase
            alpha = (self.phase_signal.squeeze(1) + 1.0) / 2.0  # Map sin from [-1,1] to [0,1]
            alpha = alpha.unsqueeze(1)
            self.q_target = self.pose_A * (1.0 - alpha) + self.pose_B * alpha
        else:
            # For non-periodic: hold pose_target
            self.q_target = self.pose_target.clone()

    def _pre_compute_observations_callback(self):
        """Update phase and target before computing observations."""
        super()._pre_compute_observations_callback()
        self._compute_phase()
        self._get_current_target()

    def _get_obs_dof_pos(self):
        return self.simulator.dof_pos

    def _get_obs_q_target(self):
        return self.q_target

    def _get_obs_phase_signal(self):
        return self.phase_signal

    def _get_obs_projected_gravity(self):
        return self.projected_gravity

    # --------------- rewards ---------------

    def _reward_pose_tracking(self):
        """Reward for matching target joints to current pose."""
        if self.motion_id == 1:
            actual = self.simulator.dof_pos[:, self.lower_dof_indices]
            target = self.q_target[:, self.lower_dof_indices]
        else:
            actual = self.simulator.dof_pos[:, self.upper_dof_indices]
            target = self.q_target[:, self.upper_dof_indices]
        error = torch.sum(torch.square(actual - target), dim=1)
        return torch.exp(-0.5 * error)

    def _reward_leg_stability(self):
        """Reward for lower body — tracks target for agacharse, default for others."""
        if self.motion_id == 1:
            return torch.ones(self.num_envs, device=self.device)
        lower_actual = self.simulator.dof_pos[:, self.lower_dof_indices]
        lower_default = self.default_dof_pos[:, self.lower_dof_indices]
        error = torch.sum(torch.square(lower_actual - lower_default), dim=1)
        return torch.exp(-1.0 * error)

    def _reward_action_smoothness(self):
        """Penalty for large action changes."""
        return torch.sum(torch.square(self.actions - self.last_actions_for_smoothness), dim=1)

    def _reward_alive_bonus(self):
        """Bonus for staying alive (not terminated)."""
        return torch.ones(self.num_envs, device=self.device)

    def _reward_fall_penalty(self):
        """Penalty if robot falls (pelvis too low)."""
        pelvis_z = self.simulator.robot_root_states[:, 2]
        fallen = (pelvis_z < 0.5).float()
        return -fallen

    def _post_physics_step_callback(self):
        """Update action history after step."""
        super()._post_physics_step_callback()
        self.last_actions_for_smoothness = self.actions.clone()

    def reset_envs(self, env_ids):
        """Reset environments and action history."""
        super().reset_envs(env_ids)
        self.last_actions_for_smoothness[env_ids] = 0.0
