"""Genesis GPU-vectorized grasp environment for G1 with 4096 parallel envs."""
import sys
import os
import numpy as np
import torch
import yaml

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import genesis as gs

from simulacion.g1_constants import (
    FINGER_LEFT_CLOSED, FINGER_RIGHT_CLOSED,
    GRASP_OBS_DIM, GRASP_ACT_DIM,
)


class RunningMeanStd:
    def __init__(self, shape, device):
        self.mean = torch.zeros(shape, device=device)
        self.var = torch.ones(shape, device=device)
        self.count = 1e-4

    def update(self, x):
        batch_mean = x.mean(dim=0)
        batch_var = x.var(dim=0)
        n = x.shape[0]
        self.count += n
        delta = batch_mean - self.mean
        self.mean += delta * n / self.count
        delta2 = batch_var - self.var
        self.var += (delta2 + delta * (batch_mean - self.mean)) * n / self.count

    def normalize(self, x):
        return (x - self.mean) / (self.var.sqrt() + 1e-8)


class GenesisGraspEnv:
    XML_PATH = "escenas/g1_manipulation_full.xml"

    def __init__(self, n_envs=4096, curriculum_stage=1, randomize=True,
                 device='cuda', xml_path=None):
        self.n_envs = n_envs
        self.device = device
        self.curriculum_stage = curriculum_stage
        self.randomize = randomize
        self.control_dt = 0.02
        self.episode_len = 300
        self.training = True
        self.step_count = torch.zeros(n_envs, dtype=torch.long, device=device)
        self.prev_action = torch.zeros(n_envs, GRASP_ACT_DIM, device=device)
        self.obs_rms = RunningMeanStd(GRASP_OBS_DIM, device)

        gs.init(backend=gs.gpu)

        xml = xml_path or os.path.join(
            os.path.dirname(__file__), '..', '..', self.XML_PATH)
        xml = os.path.abspath(xml)

        self.scene = gs.Scene(
            sim_options=gs.options.SimOptions(dt=0.002, substeps=1),
            show_viewer=False, show_FPS=False,
        )
        self.robot = self.scene.add_entity(gs.morphs.MJCF(file=xml))
        self.plane = self.scene.add_entity(gs.morphs.Plane())
        self.box = self.scene.add_entity(
            gs.morphs.Box(size=(0.30, 0.20, 0.30), pos=(0.5, 0.0, 0.15)),
        )
        self.scene.build(n_envs=n_envs)

        self._map_joints()
        self._load_curriculum()
        self._set_default_pos()
        self._set_pd_gains()

        self.reset_ids = torch.arange(n_envs, device=device)

    def _map_joints(self):
        jmap = {}
        for j in self.robot.joints:
            jmap[j.name] = j.dof_idx_local

        self.arm_l_dofs = [jmap[n] for n in [
            'left_shoulder_pitch_joint', 'left_shoulder_roll_joint',
            'left_shoulder_yaw_joint', 'left_elbow_joint',
            'left_wrist_roll_joint', 'left_wrist_pitch_joint',
            'left_wrist_yaw_joint'] if n in jmap]
        self.arm_r_dofs = [jmap[n] for n in [
            'right_shoulder_pitch_joint', 'right_shoulder_roll_joint',
            'right_shoulder_yaw_joint', 'right_elbow_joint',
            'right_wrist_roll_joint', 'right_wrist_pitch_joint',
            'right_wrist_yaw_joint'] if n in jmap]
        self.finger_l_dofs = [jmap[n] for n in [
            'left_hand_thumb_0_joint', 'left_hand_thumb_1_joint',
            'left_hand_thumb_2_joint', 'left_hand_middle_0_joint',
            'left_hand_middle_1_joint', 'left_hand_index_0_joint',
            'left_hand_index_1_joint'] if n in jmap]
        self.finger_r_dofs = [jmap[n] for n in [
            'right_hand_thumb_0_joint', 'right_hand_thumb_1_joint',
            'right_hand_thumb_2_joint', 'right_hand_middle_0_joint',
            'right_hand_middle_1_joint', 'right_hand_index_0_joint',
            'right_hand_index_1_joint'] if n in jmap]

        self.manip_dofs = self.arm_l_dofs + self.finger_l_dofs + self.arm_r_dofs + self.finger_r_dofs
        self.leg_dofs = [jmap[n] for n in jmap if 'hip' in n or 'knee' in n or 'ankle' in n]
        self.waist_dofs = [jmap[n] for n in jmap if 'waist' in n]
        self.head_dofs = [jmap[n] for n in jmap if 'head' in n]
        self.frozen_dofs = self.leg_dofs + self.waist_dofs + self.head_dofs

        self.finger_l_closed = torch.tensor(FINGER_LEFT_CLOSED, device=self.device)
        self.finger_r_closed = torch.tensor(FINGER_RIGHT_CLOSED, device=self.device)

        lmap = {}
        for link in self.robot.links:
            lmap[link.name] = link.idx - self.robot.link_start
        self.palm_l_idx = lmap.get('left_wrist_yaw_link', 0)
        self.palm_r_idx = lmap.get('right_wrist_yaw_link', 0)
        self.torso_idx = lmap.get('torso_link', 0)

        link_names_lower = [l.name.lower() for l in self.robot.links]
        self.touch_l_indices = []
        self.touch_r_indices = []
        self.tip_indices = []
        for i, name in enumerate(link_names_lower):
            if 'left' in name and ('thumb_2' in name or 'index_1' in name or 'middle_1' in name):
                self.touch_l_indices.append(i)
            elif 'right' in name and ('thumb_2' in name or 'index_1' in name or 'middle_1' in name):
                self.touch_r_indices.append(i)
            if ('thumb_2' in name or 'index_1' in name or 'middle_1' in name):
                self.tip_indices.append(i)

        self.n_dofs = self.robot.n_dofs

    def _load_curriculum(self):
        cfg_path = os.path.join(
            os.path.dirname(__file__), '..', 'configs', 'grasp_curriculum.yaml')
        if os.path.exists(cfg_path):
            with open(cfg_path) as f:
                cfg = yaml.safe_load(f)
            stage_key = f'stage_{self.curriculum_stage}'
            self.stage_cfg = cfg['curriculum'][stage_key]
            self.dr_cfg = cfg.get('domain_randomization', {})
        else:
            self.stage_cfg = {
                'box_pos_range': {'x': [0.5, 0.5], 'y': [0.0, 0.0], 'z': [0.15, 0.15]},
                'box_orient_range': {'yaw_deg': [0.0, 0.0]},
                'reward_weights': {'approach': 3.0, 'closure': 1.0, 'contact': 0.5, 'lift': 0.0},
            }
            self.dr_cfg = {}

    def _set_default_pos(self):
        self.default_dof_pos = torch.zeros(self.n_dofs, device=self.device)
        for i, d in enumerate(self.arm_l_dofs):
            vals = [0.5, 0.4, 0, 1.28, 0, 0, 0]
            if i < len(vals):
                self.default_dof_pos[d] = vals[i]
        for i, d in enumerate(self.finger_l_dofs):
            vals = [0, 1.05, 0, 0, 0, 0, 0]
            if i < len(vals):
                self.default_dof_pos[d] = vals[i]
        for i, d in enumerate(self.arm_r_dofs):
            vals = [0.5, -0.4, 0, 1.28, 0, 0, 0]
            if i < len(vals):
                self.default_dof_pos[d] = vals[i]
        for i, d in enumerate(self.finger_r_dofs):
            vals = [0, -1.05, 0, 0, 0, 0, 0]
            if i < len(vals):
                self.default_dof_pos[d] = vals[i]

    def _set_pd_gains(self):
        kp = np.zeros(self.n_dofs, dtype=np.float32)
        kd = np.zeros(self.n_dofs, dtype=np.float32)
        for d in self.frozen_dofs:
            kp[d] = 500.0
            kd[d] = 10.0
        for d in self.manip_dofs:
            kp[d] = 500.0
            kd[d] = 10.0
        self.robot.set_dofs_kp(kp)
        self.robot.set_dofs_kv(kd)

    def reset(self, env_ids=None):
        if env_ids is None:
            env_ids = torch.arange(self.n_envs, device=self.device)

        n = len(env_ids)
        all_pos = self.robot.get_dofs_position()
        default_expanded = self.default_dof_pos.unsqueeze(0).expand(n, -1)
        all_pos[env_ids] = default_expanded
        self.robot.set_dofs_position(all_pos)

        pos_range = self.stage_cfg['box_pos_range']
        bx = torch.FloatTensor(n).uniform_(pos_range['x'][0], pos_range['x'][1]).to(self.device)
        by = torch.FloatTensor(n).uniform_(pos_range['y'][0], pos_range['y'][1]).to(self.device)
        bz = torch.FloatTensor(n).uniform_(pos_range['z'][0], pos_range['z'][1]).to(self.device)
        box_pos = torch.stack([bx, by, bz + 0.15], dim=-1)
        self.box.set_pos(box_pos, envs_idx=env_ids)

        orient = self.stage_cfg.get('box_orient_range', {'yaw_deg': [0.0, 0.0]})
        yaw = torch.FloatTensor(n).uniform_(
            np.radians(orient['yaw_deg'][0]),
            np.radians(orient['yaw_deg'][1])).to(self.device)
        box_quat = torch.zeros(n, 4, device=self.device)
        box_quat[:, 0] = torch.cos(yaw / 2)
        box_quat[:, 3] = torch.sin(yaw / 2)
        self.box.set_quat(box_quat, envs_idx=env_ids)

        self.step_count[env_ids] = 0
        self.prev_action[env_ids] = 0.0

        for _ in range(2):
            self.scene.step()

        self._cached = None
        obs_raw = self._get_raw_obs()
        if self.training:
            self.obs_rms.update(obs_raw)
        return self.obs_rms.normalize(obs_raw)

    def _collect_step_data(self):
        links_pos = self.robot.get_links_pos()
        all_dof_pos = self.robot.get_dofs_position()
        all_dof_vel = self.robot.get_dofs_velocity()
        contacts = self.robot.get_links_net_contact_force()
        c_force = contacts.norm(dim=-1)
        box_pos = self.box.get_pos()

        self._cached = {
            'links_pos': links_pos,
            'all_dof_pos': all_dof_pos,
            'all_dof_vel': all_dof_vel,
            'c_force': c_force,
            'box_pos': box_pos,
        }

    def step(self, actions):
        actions = actions.clone()
        actions = actions.clamp(-1.0, 1.0)

        ctrl_pos = self.default_dof_pos.unsqueeze(0).expand(self.n_envs, -1).clone()
        manip_tensor = ctrl_pos[:, self.manip_dofs]
        manip_tensor = manip_tensor + actions * 1.0
        ctrl_pos[:, self.manip_dofs] = manip_tensor
        ctrl_pos[:, self.frozen_dofs] = self.default_dof_pos[self.frozen_dofs]

        self.robot.set_dofs_position(ctrl_pos[:, self.manip_dofs], self.manip_dofs)

        n_substeps = max(1, int(self.control_dt / 0.002))
        for _ in range(n_substeps):
            self.scene.step()

        self._collect_step_data()

        obs_raw = self._get_raw_obs()
        if self.training:
            self.obs_rms.update(obs_raw)
        obs = self.obs_rms.normalize(obs_raw)
        rewards = self._compute_reward()

        self.step_count += 1
        done = (self.step_count >= self.episode_len)
        torso_z = self.robot.get_pos()[:, 2]
        done = done | (torso_z < 0.4)

        reset_ids = done.nonzero(as_tuple=False).flatten()
        if len(reset_ids) > 0:
            self.reset(reset_ids)

        self.prev_action = actions.clone()
        self._cached = None

        info = {'reward_dict': {}}
        return obs, rewards, done, info

    def _get_raw_obs(self):
        c = self._cached
        if c is None:
            self._collect_step_data()
            c = self._cached

        box_pos = c['box_pos']
        links_pos = c['links_pos']
        torso_pos = links_pos[:, self.torso_idx, :]
        box_rel = box_pos - torso_pos
        box_quat = self.box.get_quat()

        all_dof_pos = c['all_dof_pos']
        all_dof_vel = c['all_dof_vel']
        q_arm_l = all_dof_pos[:, self.arm_l_dofs]
        q_arm_r = all_dof_pos[:, self.arm_r_dofs]
        q_fing_l = all_dof_pos[:, self.finger_l_dofs]
        q_fing_r = all_dof_pos[:, self.finger_r_dofs]
        dq_arm_l = all_dof_vel[:, self.arm_l_dofs]
        dq_arm_r = all_dof_vel[:, self.arm_r_dofs]
        dq_fing_l = all_dof_vel[:, self.finger_l_dofs]
        dq_fing_r = all_dof_vel[:, self.finger_r_dofs]

        c_force = c['c_force']
        touch_l = c_force[:, self.touch_l_indices] if self.touch_l_indices else torch.zeros(self.n_envs, 3, device=self.device)
        touch_r = c_force[:, self.touch_r_indices] if self.touch_r_indices else torch.zeros(self.n_envs, 3, device=self.device)

        n_tl = touch_l.shape[1]
        n_tr = touch_r.shape[1]
        touch_l_exp = torch.zeros(self.n_envs, 6, device=self.device)
        touch_r_exp = torch.zeros(self.n_envs, 6, device=self.device)
        for i in range(min(n_tl, 6)):
            touch_l_exp[:, i] = touch_l[:, i]
        for i in range(min(n_tr, 6)):
            touch_r_exp[:, i] = touch_r[:, i]

        parts = [
            box_rel,
            box_quat,
            q_arm_l, q_arm_r, q_fing_l, q_fing_r,
            dq_arm_l, dq_arm_r, dq_fing_l, dq_fing_r,
            touch_l_exp, touch_r_exp,
            self.prev_action,
        ]
        obs = torch.cat(parts, dim=-1)

        if obs.shape[1] != GRASP_OBS_DIM:
            if obs.shape[1] < GRASP_OBS_DIM:
                pad = torch.zeros(self.n_envs, GRASP_OBS_DIM - obs.shape[1], device=self.device)
                obs = torch.cat([obs, pad], dim=-1)
            else:
                obs = obs[:, :GRASP_OBS_DIM]

        return obs

    def _get_obs(self):
        obs_raw = self._get_raw_obs()
        if self.training:
            self.obs_rms.update(obs_raw)
        return self.obs_rms.normalize(obs_raw)

    def _compute_reward(self):
        c = self._cached
        if c is None:
            self._collect_step_data()
            c = self._cached

        links_pos = c['links_pos']
        palm_l = links_pos[:, self.palm_l_idx, :]
        palm_r = links_pos[:, self.palm_r_idx, :]
        box_pos = c['box_pos']

        dist_l = (palm_l - box_pos).norm(dim=-1)
        dist_r = (palm_r - box_pos).norm(dim=-1)
        avg_dist = torch.stack([dist_l, dist_r]).mean(dim=0)
        min_dist = torch.stack([dist_l, dist_r]).min(dim=0).values

        w = self.stage_cfg['reward_weights']
        r_approach = torch.exp(-5.0 * avg_dist) * w.get('approach', 3.0)

        near = (min_dist < 0.15).float()
        all_dof_pos = c['all_dof_pos']
        q_fl = all_dof_pos[:, self.finger_l_dofs]
        q_fr = all_dof_pos[:, self.finger_r_dofs]
        q_closed = torch.cat([self.finger_l_closed, self.finger_r_closed])
        q_fingers = torch.cat([q_fl, q_fr], dim=-1)
        closure_err = (q_fingers - q_closed.unsqueeze(0)).abs().mean(dim=-1)
        r_closure = torch.exp(-3.0 * closure_err) * near * w.get('closure', 1.0)

        c_force = c['c_force']
        tip_forces = c_force[:, self.tip_indices] if self.tip_indices else torch.zeros(self.n_envs, 1, device=self.device)
        n_contacts = (tip_forces > 0.5).sum(dim=-1).float()
        r_contact = (n_contacts / 6.0) * w.get('contact', 0.5)

        box_z = box_pos[:, 2]
        has_contact = (n_contacts >= 4).float()
        r_lift = torch.clamp(box_z - 0.15, min=0.0) * 10.0 * w.get('lift', 0.0) * has_contact

        r_smooth = -0.001 * (self.prev_action ** 2).sum(dim=-1)

        total = r_approach + r_closure + r_contact + r_lift + r_smooth
        return total
