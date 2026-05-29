"""
G1 Grasp Environment — single-env MuJoCo wrapper for static grasp policy.

Observations (103 dims):
  box_pos_rel(3) + box_quat(4) + q_arm_l(7) + q_arm_r(7) + q_finger_l(7) +
  q_finger_r(7) + dq_arm_l(7) + dq_arm_r(7) + dq_finger_l(7) + dq_finger_r(7) +
  touch_l(6) + touch_r(6) + prev_action(28)

Actions (28 dims): arm_l(7) + finger_l(7) + arm_r(7) + finger_r(7)
"""
import sys
import os
import numpy as np
import mujoco

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from simulacion.g1_constants import (
    ARM_LEFT_ACT_IDS, ARM_RIGHT_ACT_IDS,
    FINGER_LEFT_ACT_IDS, FINGER_RIGHT_ACT_IDS,
    MANIP_ALL_ACT_IDS, MANIP_LEFT_ACT_IDS, MANIP_RIGHT_ACT_IDS,
    LEG_ACT_IDS, WAIST_ACT_IDS, HEAD_ACT_IDS,
    TOUCH_LEFT_ADR, TOUCH_RIGHT_ADR, TOUCH_ALL_ADR,
    IMU_TORSO_GYRO_ADR, IMU_TORSO_ACCEL_ADR,
    FINGER_LEFT_CLOSED, FINGER_RIGHT_CLOSED,
    FINGER_LEFT_OPEN, FINGER_RIGHT_OPEN,
    BOX_BODY_ID, BOX_JOINT_QPOS_ADR,
    GRASP_OBS_DIM, GRASP_ACT_DIM,
)


class G1GraspEnv:
    XML_SCENE = "escenas/g1_manipulation_scene.xml"

    def __init__(self, xml_path=None, curriculum_stage=1, randomize=True,
                 control_dt=0.02, episode_len=300):
        xml_path = xml_path or os.path.join(
            os.path.dirname(__file__), '..', '..', self.XML_SCENE)
        self.xml_path = os.path.abspath(xml_path)
        self.model = mujoco.MjModel.from_xml_path(self.xml_path)
        self.data = mujoco.MjData(self.model)
        self.curriculum_stage = curriculum_stage
        self.randomize = randomize
        self.control_dt = control_dt
        self.episode_len = episode_len

        self.model.opt.timestep = 0.002  # 500 Hz physics

        self.arm_act_ids = ARM_LEFT_ACT_IDS + ARM_RIGHT_ACT_IDS       # 14
        self.finger_act_ids = FINGER_LEFT_ACT_IDS + FINGER_RIGHT_ACT_IDS  # 14
        self.all_manip_ids = MANIP_ALL_ACT_IDS                          # 28

        self.frozen_act_ids = LEG_ACT_IDS + WAIST_ACT_IDS + HEAD_ACT_IDS

        mujoco.mj_resetData(self.model, self.data)
        self.default_qpos = self.data.qpos.copy()
        self.default_qpos[2] = 0.79           # pelvis z
        self.default_qpos[3:7] = [1, 0, 0, 0]  # pelvis quat
        self.default_qpos[7:22] = 0.0           # legs + waist
        self.default_qpos[22:29] = [0.5, 0.4, 0, 1.28, 0, 0, 0]
        self.default_qpos[29:36] = [0, 1.05, 0, 0, 0, 0, 0]
        self.default_qpos[36:43] = [0.5, -0.4, 0, 1.28, 0, 0, 0]
        self.default_qpos[43:50] = [0, -1.05, 0, 0, 0, 0, 0]
        self.default_qpos[50:52] = 0.0         # head
        self.default_qpos[52:55] = [0.5, 0, 0.15]  # box xyz
        self.default_qpos[55:59] = [1, 0, 0, 0]    # box quat

        self.data.qpos[:] = self.default_qpos
        mujoco.mj_forward(self.model, self.data)

        self._load_curriculum_config()

        self.prev_action = np.zeros(GRASP_ACT_DIM, dtype=np.float64)
        self.step_count = 0
        self.total_reward = 0.0
        self.reward_log = {k: 0.0 for k in [
            'r_approach', 'r_closure', 'r_contact', 'r_lift',
            'r_smooth', 'r_torque', 'r_autocoll']}

    def _load_curriculum_config(self):
        import yaml
        config_path = os.path.join(
            os.path.dirname(__file__), '..', 'configs', 'grasp_curriculum.yaml')
        if os.path.exists(config_path):
            with open(config_path) as f:
                cfg = yaml.safe_load(f)
            stage_key = f'stage_{self.curriculum_stage}'
            self.stage_cfg = cfg['curriculum'][stage_key]
            self.dr_cfg = cfg.get('domain_randomization', {})
        else:
            self.stage_cfg = {
                'box_pos_range': {'x': [0.5, 0.5], 'y': [0.0, 0.0], 'z': [0.15, 0.15]},
                'box_orient_range': {'yaw_deg': [0.0, 0.0]},
                'reward_weights': {'approach': 3.0, 'closure': 1.0,
                                   'contact': 0.5, 'lift': 0.0},
            }
            self.dr_cfg = {}

    def reset(self):
        mujoco.mj_resetData(self.model, self.data)
        self.data.qpos[:] = self.default_qpos

        pos_range = self.stage_cfg['box_pos_range']
        bx = np.random.uniform(pos_range['x'][0], pos_range['x'][1])
        by = np.random.uniform(pos_range['y'][0], pos_range['y'][1])
        bz = np.random.uniform(pos_range['z'][0], pos_range['z'][1])
        self.data.qpos[BOX_JOINT_QPOS_ADR + 0] = bx
        self.data.qpos[BOX_JOINT_QPOS_ADR + 1] = by
        self.data.qpos[BOX_JOINT_QPOS_ADR + 2] = bz

        orient = self.stage_cfg.get('box_orient_range', {'yaw_deg': [0.0, 0.0]})
        yaw = np.random.uniform(
            np.radians(orient['yaw_deg'][0]),
            np.radians(orient['yaw_deg'][1]))
        half = yaw / 2.0
        self.data.qpos[BOX_JOINT_QPOS_ADR + 3] = np.cos(half)  # qw
        self.data.qpos[BOX_JOINT_QPOS_ADR + 4] = 0.0            # qx
        self.data.qpos[BOX_JOINT_QPOS_ADR + 5] = 0.0            # qy
        self.data.qpos[BOX_JOINT_QPOS_ADR + 6] = np.sin(half)   # qz

        self.data.qvel[BOX_JOINT_QPOS_ADR - 1:BOX_JOINT_QPOS_ADR + 5] = 0.0

        if self.randomize and self.dr_cfg:
            self._apply_domain_randomization()

        mujoco.mj_forward(self.model, self.data)

        self.prev_action = np.zeros(GRASP_ACT_DIM, dtype=np.float64)
        self.step_count = 0
        self.total_reward = 0.0
        self.reward_log = {k: 0.0 for k in self.reward_log}

        return self._get_obs()

    def _apply_domain_randomization(self):
        dr = self.dr_cfg
        if not dr:
            return
        mass_range = dr.get('box_mass_range', [0.3, 3.0])
        self.model.body_mass[BOX_BODY_ID] = np.random.uniform(*mass_range)
        fric_range = dr.get('box_friction_range', [0.4, 1.5])
        for gi in range(self.model.ngeom):
            if self.model.geom_bodyid[gi] == BOX_BODY_ID:
                self.model.geom_friction[gi, 0] = np.random.uniform(*fric_range)

    def step(self, action):
        action = np.clip(action, -1.0, 1.0)
        self._apply_action(action)

        n_substeps = max(1, int(self.control_dt / self.model.opt.timestep))
        for _ in range(n_substeps):
            mujoco.mj_step(self.model, self.data)

        obs = self._get_obs()
        reward_dict = self._compute_reward()
        self.total_reward += reward_dict['total']
        self.step_count += 1

        done = (self.step_count >= self.episode_len) or self._is_terminal()
        info = {
            'reward_dict': reward_dict,
            'total_reward': self.total_reward,
            'step': self.step_count,
            'success': self._check_success(),
        }

        self.prev_action = action.copy()
        return obs, reward_dict['total'], done, info

    def _apply_action(self, action):
        for aid in self.frozen_act_ids:
            self.data.ctrl[aid] = 0.0

        scale = 0.5
        for i, aid in enumerate(MANIP_LEFT_ACT_IDS):
            jnt_adr = self.model.jnt_qposadr[self.model.actuator_trnid[aid, 0]]
            default = self.default_qpos[jnt_adr]
            self.data.ctrl[aid] = default + action[i] * scale

        for i, aid in enumerate(MANIP_RIGHT_ACT_IDS):
            jnt_adr = self.model.jnt_qposadr[self.model.actuator_trnid[aid, 0]]
            default = self.default_qpos[jnt_adr]
            self.data.ctrl[aid] = default + action[14 + i] * scale

    def _get_obs(self):
        d = self.data

        box_pos = d.qpos[BOX_JOINT_QPOS_ADR:BOX_JOINT_QPOS_ADR + 3].copy()
        box_quat = d.qpos[BOX_JOINT_QPOS_ADR + 3:BOX_JOINT_QPOS_ADR + 7].copy()

        torso_id = mujoco.mj_name2id(self.model, mujoco.mjtObj.mjOBJ_BODY, 'torso_link')
        torso_pos = d.xpos[torso_id].copy()
        torso_quat = d.xquat[torso_id].copy()

        box_rel = self._transform_to_local(torso_pos, torso_quat, box_pos)

        obs_parts = [box_rel, box_quat]

        for act_ids in [ARM_LEFT_ACT_IDS, ARM_RIGHT_ACT_IDS,
                        FINGER_LEFT_ACT_IDS, FINGER_RIGHT_ACT_IDS]:
            q = np.array([d.qpos[self.model.jnt_qposadr[self.model.actuator_trnid[a, 0]]]
                          for a in act_ids])
            obs_parts.append(q)

        for act_ids in [ARM_LEFT_ACT_IDS, ARM_RIGHT_ACT_IDS,
                        FINGER_LEFT_ACT_IDS, FINGER_RIGHT_ACT_IDS]:
            dq = np.array([d.qvel[self.model.jnt_dofadr[self.model.actuator_trnid[a, 0]]]
                           for a in act_ids])
            obs_parts.append(dq)

        touch_left = np.array([d.sensordata[adr] for adr in TOUCH_LEFT_ADR])
        touch_right = np.array([d.sensordata[adr] for adr in TOUCH_RIGHT_ADR])
        obs_parts.extend([
            np.full(6, touch_left.sum()),
            np.full(6, touch_right.sum()),
        ])

        obs_parts.append(self.prev_action)

        obs = np.concatenate(obs_parts).astype(np.float32)
        assert obs.shape[0] == GRASP_OBS_DIM, \
            f"obs dim mismatch: {obs.shape[0]} != {GRASP_OBS_DIM}"
        return obs

    def _transform_to_local(self, parent_pos, parent_quat, child_pos):
        diff = child_pos - parent_pos
        q_conj = parent_quat.copy()
        q_conj[1:4] *= -1
        return self._quat_rotate(q_conj, diff)

    @staticmethod
    def _quat_rotate(q, v):
        qv = np.array([0.0, v[0], v[1], v[2]])
        q_conj = np.array([q[0], -q[1], -q[2], -q[3]])
        result = G1GraspEnv._quat_mul(G1GraspEnv._quat_mul(q, qv), q_conj)
        return result[1:4]

    @staticmethod
    def _quat_mul(q1, q2):
        w1, x1, y1, z1 = q1
        w2, x2, y2, z2 = q2
        return np.array([
            w1*w2 - x1*x2 - y1*y2 - z1*z2,
            w1*x2 + x1*w2 + y1*z2 - z1*y2,
            w1*y2 - x1*z2 + y1*w2 + z1*x2,
            w1*z2 + x1*y2 - y1*x2 + z1*w2,
        ])

    def _get_palm_positions(self):
        left_wrist_id = mujoco.mj_name2id(
            self.model, mujoco.mjtObj.mjOBJ_BODY, 'left_wrist_yaw_link')
        right_wrist_id = mujoco.mj_name2id(
            self.model, mujoco.mjtObj.mjOBJ_BODY, 'right_wrist_yaw_link')
        return self.data.xpos[left_wrist_id].copy(), self.data.xpos[right_wrist_id].copy()

    def _compute_reward(self):
        d = self.data
        palm_l, palm_r = self._get_palm_positions()
        box_pos = d.qpos[BOX_JOINT_QPOS_ADR:BOX_JOINT_QPOS_ADR + 3].copy()

        w = self.stage_cfg['reward_weights']

        dist_l = np.linalg.norm(palm_l - box_pos)
        dist_r = np.linalg.norm(palm_r - box_pos)
        r_approach = -np.mean([dist_l, dist_r]) * w.get('approach', 3.0)

        near_threshold = 0.15
        if min(dist_l, dist_r) < near_threshold:
            q_finger_l = np.array([
                d.qpos[self.model.jnt_qposadr[self.model.actuator_trnid[a, 0]]]
                for a in FINGER_LEFT_ACT_IDS])
            q_finger_r = np.array([
                d.qpos[self.model.jnt_qposadr[self.model.actuator_trnid[a, 0]]]
                for a in FINGER_RIGHT_ACT_IDS])
            q_fingers = np.concatenate([q_finger_l, q_finger_r])
            q_closed = np.concatenate([FINGER_LEFT_CLOSED, FINGER_RIGHT_CLOSED])
            r_closure = -np.mean(np.abs(q_fingers - q_closed)) * w.get('closure', 1.0)
        else:
            r_closure = 0.0

        touch_left = np.array([d.sensordata[adr] for adr in TOUCH_LEFT_ADR])
        touch_right = np.array([d.sensordata[adr] for adr in TOUCH_RIGHT_ADR])
        touch_all = np.concatenate([touch_left, touch_right])
        extended_touch = np.zeros(12)
        for i in range(6):
            extended_touch[i] = 1.0 if touch_all[i] > 0.1 else 0.0
            extended_touch[6 + i] = extended_touch[i]
        n_contacts = np.sum(touch_all > 0.1)
        r_contact = (n_contacts / 6.0) * w.get('contact', 0.5)

        box_z = box_pos[2]
        box_z_init = 0.15
        if n_contacts >= 4:
            r_lift = max(0.0, box_z - box_z_init) * w.get('lift', 0.0) * 5.0
        else:
            r_lift = 0.0

        r_smooth = -0.01 * np.sum((self.data.ctrl[self.all_manip_ids] - self.prev_action * 0.5) ** 2)
        r_torque = -0.001 * np.sum(self.data.ctrl[self.all_manip_ids] ** 2)
        r_autocoll = 0.0

        total = r_approach + r_closure + r_contact + r_lift + r_smooth + r_torque + r_autocoll

        return {
            'total': float(total),
            'r_approach': float(r_approach),
            'r_closure': float(r_closure),
            'r_contact': float(r_contact),
            'r_lift': float(r_lift),
            'r_smooth': float(r_smooth),
            'r_torque': float(r_torque),
            'r_autocoll': float(r_autocoll),
        }

    def _check_success(self):
        touch_left = np.array([self.data.sensordata[adr] for adr in TOUCH_LEFT_ADR])
        touch_right = np.array([self.data.sensordata[adr] for adr in TOUCH_RIGHT_ADR])
        n_contacts = np.sum(np.concatenate([touch_left, touch_right]) > 0.1)
        box_z = self.data.qpos[BOX_JOINT_QPOS_ADR + 2]
        return n_contacts >= 4 and box_z > 0.20

    def _is_terminal(self):
        torso_id = mujoco.mj_name2id(self.model, mujoco.mjtObj.mjOBJ_BODY, 'torso_link')
        if self.data.xpos[torso_id, 2] < 0.4:
            return True
        box_z = self.data.qpos[BOX_JOINT_QPOS_ADR + 2]
        if box_z < -0.1:
            return True
        return False

    def get_box_pos(self):
        return self.data.qpos[BOX_JOINT_QPOS_ADR:BOX_JOINT_QPOS_ADR + 3].copy()

    def get_palm_positions(self):
        return self._get_palm_positions()

    def get_contact_forces(self):
        touch_left = np.array([self.data.sensordata[adr] for adr in TOUCH_LEFT_ADR])
        touch_right = np.array([self.data.sensordata[adr] for adr in TOUCH_RIGHT_ADR])
        return np.concatenate([touch_left, touch_right])
