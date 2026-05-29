import torch
import numpy as np
import sys
import os

sys.path.insert(0, '/home/udc/Humanoide/G1/entrenamiento')

from humanoidverse.utils.config_utils import *
import hydra
from hydra.utils import instantiate

def validate_motion_policy(motion_id, motion_name, checkpoint_path, num_episodes=20):
    """Validate a trained motion policy on multiple episodes."""
    
    with hydra.initialize_config_dir(
        config_dir='/home/udc/Humanoide/G1/entrenamiento/humanoidverse/config',
        version_base=None
    ):
        cfg = hydra.compose(
            config_name='base',
            overrides=[
                '+simulator=genesis',
                '+exp=motion',
                '+domain_rand=NO_domain_rand',
                '+rewards=motion/motion_rewards',
                '+robot=g1/g1_29dof',
                '+terrain=terrain_locomotion_plane',
                '+obs=motion/motion_obs',
                'num_envs=1',
                'headless=True',
                'env.config.motion.motion_id=' + str(motion_id),
            ]
        )
        
        env = instantiate(cfg.env, device='cuda:0')
        
        # Compute algo_obs_dim_dict (required by PPO)
        obs_dim_dict = {}
        _obs_key_list = cfg.obs.obs_dict
        _aux_obs_key_list = cfg.obs.obs_auxiliary
        
        auxiliary_obs_dims = {}
        for aux_obs_key, aux_config in _aux_obs_key_list.items():
            auxiliary_obs_dims[aux_obs_key] = 0
            for _key, _num in aux_config.items():
                auxiliary_obs_dims[aux_obs_key] += cfg.obs.obs_dims[_key] * _num
        
        for obs_key, obs_config in _obs_key_list.items():
            obs_dim_dict[obs_key] = 0
            for key in obs_config:
                if key.endswith("_raw"): key = key[:-4]
                if key in cfg.obs.obs_dims.keys():
                    obs_dim_dict[obs_key] += cfg.obs.obs_dims[key]
                else:
                    obs_dim_dict[obs_key] += auxiliary_obs_dims[key]
        
        cfg.robot.algo_obs_dim_dict = obs_dim_dict
        env.config.robot.algo_obs_dim_dict = obs_dim_dict
        
        # Load policy
        checkpoint = torch.load(checkpoint_path, map_location='cuda:0')
        
        # Create actor network
        from humanoidverse.agents.ppo.ppo import PPO
        ppo = instantiate(cfg.algo, env=env, device='cuda:0')
        ppo.setup()
        
        # Load weights
        ppo.actor.load_state_dict(checkpoint['actor_model_state_dict'])
        ppo.actor.eval()
        
        results = []
        
        for ep in range(num_episodes):
            obs_dict = env.reset_all()
            done = False
            episode_data = {
                'right_shoulder_pitch_min': float('inf'),
                'wrist_pitch_range': [float('inf'), float('-inf')],
                'pelvis_z_min': float('inf'),
                'pelvis_z_start': env.simulator.robot_root_states[0, 2].item(),
                'left_knee_max': float('-inf'),
                'right_knee_max': float('-inf'),
                'left_shoulder_pitch_min': float('inf'),
                'right_shoulder_pitch_min': float('inf'),
                'left_wrist_roll_range': [float('inf'), float('-inf')],
                'right_wrist_roll_range': [float('inf'), float('-inf')],
                'robot_stood': True,
                'steps': 0,
            }
            
            while not done:
                with torch.no_grad():
                    action = ppo.actor.act_inference(obs_dict['actor_obs'])
                
                actor_state = {"actions": action}
                obs_dict, reward, done, info = env.step(actor_state)
                done = done[0].item()
                
                # Collect metrics
                dof_pos = env.simulator.dof_pos[0]
                pelvis_z = env.simulator.robot_root_states[0, 2].item()
                
                episode_data['pelvis_z_min'] = min(episode_data['pelvis_z_min'], pelvis_z)
                episode_data['steps'] += 1
                
                if pelvis_z < 0.5:
                    episode_data['robot_stood'] = False
                
                # Motion-specific metrics
                if motion_id == 0:  # Saludar
                    r_shoulder_pitch = dof_pos[22].item()
                    r_wrist_pitch = dof_pos[27].item()
                    episode_data['right_shoulder_pitch_min'] = min(
                        episode_data['right_shoulder_pitch_min'], r_shoulder_pitch)
                    episode_data['wrist_pitch_range'][0] = min(
                        episode_data['wrist_pitch_range'][0], r_wrist_pitch)
                    episode_data['wrist_pitch_range'][1] = max(
                        episode_data['wrist_pitch_range'][1], r_wrist_pitch)
                
                elif motion_id == 1:  # Agacharse
                    l_knee = dof_pos[3].item()
                    r_knee = dof_pos[9].item()
                    episode_data['left_knee_max'] = max(episode_data['left_knee_max'], l_knee)
                    episode_data['right_knee_max'] = max(episode_data['right_knee_max'], r_knee)
                
                elif motion_id == 2:  # Estirar
                    l_shoulder_pitch = dof_pos[15].item()
                    r_shoulder_pitch = dof_pos[22].item()
                    episode_data['left_shoulder_pitch_min'] = min(
                        episode_data['left_shoulder_pitch_min'], l_shoulder_pitch)
                    episode_data['right_shoulder_pitch_min'] = min(
                        episode_data['right_shoulder_pitch_min'], r_shoulder_pitch)
                
                elif motion_id == 3:  # Munecas
                    l_wrist_roll = dof_pos[19].item()
                    r_wrist_roll = dof_pos[26].item()
                    episode_data['left_wrist_roll_range'][0] = min(
                        episode_data['left_wrist_roll_range'][0], l_wrist_roll)
                    episode_data['left_wrist_roll_range'][1] = max(
                        episode_data['left_wrist_roll_range'][1], l_wrist_roll)
                    episode_data['right_wrist_roll_range'][0] = min(
                        episode_data['right_wrist_roll_range'][0], r_wrist_roll)
                    episode_data['right_wrist_roll_range'][1] = max(
                        episode_data['right_wrist_roll_range'][1], r_wrist_roll)
                
                if done:
                    break
            
            results.append(episode_data)
        
        return results


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--motion_id', type=int, required=True)
    parser.add_argument('--motion_name', type=str, required=True)
    parser.add_argument('--checkpoint', type=str, required=True)
    parser.add_argument('--num_episodes', type=int, default=20)
    args = parser.parse_args()
    
    results = validate_motion_policy(
        args.motion_id, args.motion_name, args.checkpoint, args.num_episodes)
    
    print(f"\n=== Validation Results: {args.motion_name} ===")
    print(f"{'Ep':>3} | {'Result':>6} | Details")
    print("-" * 60)
    
    passes = 0
    for i, r in enumerate(results):
        if args.motion_id == 0:  # Saludar
            wrist_range = r['wrist_pitch_range'][1] - r['wrist_pitch_range'][0]
            passed = (r['right_shoulder_pitch_min'] < -0.8) and (wrist_range > 0.3)
            detail = f"r_shoulder_pitch_min={r['right_shoulder_pitch_min']:.3f}, wrist_range={wrist_range:.3f}"
        
        elif args.motion_id == 1:  # Agacharse
            knee_delta = r['left_knee_max'] - 0.3  # default is 0.3
            pelvis_drop = r['pelvis_z_start'] - r['pelvis_z_min']
            passed = (knee_delta > 0.05) and (pelvis_drop > 0.01) and r['robot_stood']
            detail = f"knee_delta={knee_delta:.3f}, pelvis_drop={pelvis_drop:.3f}, stood={r['robot_stood']}"
        
        elif args.motion_id == 2:  # Estirar
            passed = (r['left_shoulder_pitch_min'] < -1.0) and (r['right_shoulder_pitch_min'] < -1.0)
            detail = f"l_shoulder={r['left_shoulder_pitch_min']:.3f}, r_shoulder={r['right_shoulder_pitch_min']:.3f}"
        
        elif args.motion_id == 3:  # Munecas
            l_wrist_range = r['left_wrist_roll_range'][1] - r['left_wrist_roll_range'][0]
            r_wrist_range = r['right_wrist_roll_range'][1] - r['right_wrist_roll_range'][0]
            passed = (l_wrist_range > 0.7) and (r_wrist_range > 0.7)
            detail = f"l_wrist_range={l_wrist_range:.3f}, r_wrist_range={r_wrist_range:.3f}"
        
        status = "PASS" if passed else "FAIL"
        if passed:
            passes += 1
        
        print(f"{i+1:>3} | {status:>6} | {detail}")
    
    print("-" * 60)
    print(f"Total: {passes}/{len(results)} PASS ({100*passes/len(results):.1f}%)")
    
    if passes >= 16:
        print("APPROVED")
    else:
        print("NOT APPROVED")
