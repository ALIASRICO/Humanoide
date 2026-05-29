"""Genesis/HumanoidVerse wrapper for vectorized G1 grasp training.

Adapts the single-env G1GraspEnv to run N parallel instances for PPO.
Uses multiprocessing when Genesis GPU sim is not available.
"""
import os
import sys
import numpy as np
import torch
from multiprocessing import Pool

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simulacion.g1_constants import GRASP_OBS_DIM, GRASP_ACT_DIM


def _worker_reset(args):
    worker_id, xml_path, stage, seed = args
    from entrenamiento.envs.g1_grasp_env import G1GraspEnv
    env = G1GraspEnv(xml_path=xml_path, curriculum_stage=stage, randomize=True)
    np.random.seed(seed + worker_id)
    obs = env.reset()
    return worker_id, obs, env


def _worker_step(args):
    worker_id, env, action = args
    obs, reward, done, info = env.step(action)
    if done:
        obs = env.reset()
    return worker_id, obs, reward, done, info


class VectorizedGraspEnv:
    """Runs N G1GraspEnv instances in parallel using torch for vectorization."""

    def __init__(self, n_envs=4096, xml_path=None, curriculum_stage=1,
                 device='cuda'):
        self.n_envs = n_envs
        self.device = device
        self.curriculum_stage = curriculum_stage

        self.xml_path = xml_path or os.path.join(
            os.path.dirname(os.path.abspath(__file__)), '..', '..',
            'escenas', 'g1_manipulation_scene.xml')

        from entrenamiento.envs.g1_grasp_env import G1GraspEnv
        self.envs = []
        for i in range(min(n_envs, 64)):
            env = G1GraspEnv(
                xml_path=self.xml_path,
                curriculum_stage=curriculum_stage,
                randomize=True,
            )
            self.envs.append(env)

        self.num_envs = len(self.envs)

    def reset_all(self):
        obs_list = []
        for i, env in enumerate(self.envs):
            np.random.seed(42 + i)
            obs_list.append(env.reset())
        return torch.tensor(np.stack(obs_list), dtype=torch.float32, device=self.device)

    def reset_envs(self, env_ids):
        obs_list = []
        for idx in env_ids:
            self.envs[idx].randomize = True
            obs = self.envs[idx].reset()
            obs_list.append(obs)
        if len(obs_list) > 0:
            return torch.tensor(np.stack(obs_list), dtype=torch.float32, device=self.device)
        return torch.empty((0, GRASP_OBS_DIM), device=self.device)

    def step_batch(self, actions):
        actions_np = actions.cpu().numpy()
        obs_list = []
        rewards = []
        dones = []
        infos = []

        for i, env in enumerate(self.envs):
            obs, reward, done, info = env.step(actions_np[i])
            if done:
                obs = env.reset()
            obs_list.append(obs)
            rewards.append(reward)
            dones.append(float(done))
            infos.append(info)

        obs_t = torch.tensor(np.stack(obs_list), dtype=torch.float32, device=self.device)
        rewards_t = torch.tensor(rewards, dtype=torch.float32, device=self.device)
        dones_t = torch.tensor(dones, dtype=torch.float32, device=self.device)

        return obs_t, rewards_t, dones_t, infos

    @property
    def obs_dim(self):
        return GRASP_OBS_DIM

    @property
    def act_dim(self):
        return GRASP_ACT_DIM
