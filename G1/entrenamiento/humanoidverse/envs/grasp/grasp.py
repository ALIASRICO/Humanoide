import torch
from loguru import logger
from humanoidverse.envs.legged_base_task.legged_robot_base import LeggedRobotBase
from humanoidverse.utils.torch_utils import torch_rand_float
from humanoidverse.simulator.genesis.tmp_gs_utils import gs_inv_quat, gs_transform_by_quat


class GraspEnv(LeggedRobotBase):

    def __init__(self, config, device):
        self.init_done = False
        super().__init__(config, device)
        self.init_done = True
        logger.info(f"GraspEnv initialized — table_z={self.table_z:.3f}  box_default={self.box_default_pos}")

    def _init_buffers(self):
        super()._init_buffers()

        self.left_hand_idx = self.simulator.find_rigid_body_indice("left_wrist_yaw_link")
        self.right_hand_idx = self.simulator.find_rigid_body_indice("right_wrist_yaw_link")

        grasp = self.config.grasp
        self.box_default_pos = torch.tensor(grasp.box_default_pos, device=self.device)
        self.table_z = grasp.table_pos[2] + grasp.table_size[2] / 2.0
        self.box_rand_range = grasp.box_randomization_range

        self.box_pos = torch.zeros(self.num_envs, 3, device=self.device)
        self.box_vel = torch.zeros(self.num_envs, 3, device=self.device)
        self.box_pos_rel = torch.zeros(self.num_envs, 3, device=self.device)
        self.left_hand_to_box = torch.zeros(self.num_envs, 3, device=self.device)
        self.right_hand_to_box = torch.zeros(self.num_envs, 3, device=self.device)
        self.contact_left = torch.zeros(self.num_envs, 3, device=self.device)
        self.contact_right = torch.zeros(self.num_envs, 3, device=self.device)

    def _pre_compute_observations_callback(self):
        super()._pre_compute_observations_callback()

        self.box_pos = self.simulator.box_pos.clone()
        self.box_vel = self.simulator.box_vel.clone()

        left_hand_pos = self.simulator._rigid_body_pos[:, self.left_hand_idx, :]
        right_hand_pos = self.simulator._rigid_body_pos[:, self.right_hand_idx, :]
        self.left_hand_to_box = self.box_pos - left_hand_pos
        self.right_hand_to_box = self.box_pos - right_hand_pos

        base_pos = self.simulator.base_pos
        base_quat_wxyz = self.simulator.robot.get_quat()
        inv_quat = gs_inv_quat(base_quat_wxyz)
        self.box_pos_rel = gs_transform_by_quat(self.box_pos - base_pos, inv_quat)

        self.contact_left = self.simulator.contact_forces[:, self.left_hand_idx, :].clone()
        self.contact_right = self.simulator.contact_forces[:, self.right_hand_idx, :].clone()

    def _update_reset_buf(self):
        super()._update_reset_buf()
        box_z = self.box_pos[:, 2]
        self.reset_buf |= (box_z < self.table_z - 0.1)

    def _reset_robot_states_callback(self, env_ids, target_states=None):
        super()._reset_robot_states_callback(env_ids, target_states)
        n = len(env_ids)
        if n == 0:
            return
        box_pos = self.box_default_pos.unsqueeze(0).expand(n, -1).clone()
        box_pos[:, 0] += torch_rand_float(-self.box_rand_range, self.box_rand_range, (n, 1), device=self.device).squeeze(1)
        box_pos[:, 1] += torch_rand_float(-self.box_rand_range, self.box_rand_range, (n, 1), device=self.device).squeeze(1)
        self.simulator.reset_box(env_ids, box_pos)

    # --------------- observations ---------------

    def _get_obs_box_pos_rel(self):
        return self.box_pos_rel

    def _get_obs_left_hand_to_box(self):
        return self.left_hand_to_box

    def _get_obs_right_hand_to_box(self):
        return self.right_hand_to_box

    def _get_obs_contact_left(self):
        return self.contact_left

    def _get_obs_contact_right(self):
        return self.contact_right

    # --------------- rewards ---------------

    def _reward_hand_distance(self):
        left_dist = torch.norm(self.left_hand_to_box, dim=-1)
        right_dist = torch.norm(self.right_hand_to_box, dim=-1)
        min_dist = torch.minimum(left_dist, right_dist)
        avg_dist = (left_dist + right_dist) / 2.0
        close_reward = torch.exp(-2.0 * min_dist)
        avg_reward = torch.exp(-2.0 * avg_dist)
        return 0.7 * close_reward + 0.3 * avg_reward

    def _reward_contact(self):
        left_f = torch.norm(self.contact_left, dim=-1)
        right_f = torch.norm(self.contact_right, dim=-1)
        return (left_f > 0.5).float() + (right_f > 0.5).float()

    def _reward_lift(self):
        box_z = self.box_pos[:, 2]
        return torch.clip(box_z - self.table_z - 0.05, min=0.0)

    def _reward_grasp_hold(self):
        box_z = self.box_pos[:, 2]
        lifted = (box_z > self.table_z + 0.05).float()
        left_c = (torch.norm(self.contact_left, dim=-1) > 0.5).float()
        right_c = (torch.norm(self.contact_right, dim=-1) > 0.5).float()
        return lifted * left_c * right_c

    def _reward_penalty_leg_movement(self):
        leg_pos = self.simulator.dof_pos[:, self.lower_dof_indices]
        leg_default = self.default_dof_pos[:, self.lower_dof_indices]
        return torch.sum(torch.square(leg_pos - leg_default), dim=1)

    def _reward_base_height(self):
        base_height = self.simulator.robot_root_states[:, 2]
        return torch.square(base_height - self.config.rewards.desired_base_height)
