#!/bin/bash
# V10: kp/kd oficiales Unitree en Genesis (igual que MuJoCo sim)
# hip=40/2.6, knee=100/6.3, ankle=28/1.8
# Objetivo: cerrar brecha sim-to-sim — política aprende con los mismos kp que se usan en MuJoCo
# Desde cero (V9 entrenó con kp=100/200 — no es útil como checkpoint aquí)
source /home/udc/miniconda3/etc/profile.d/conda.sh
conda activate hgen
cd /home/udc/Humanoide/G1/entrenamiento
python humanoidverse/train_agent.py \
    +simulator=genesis \
    +exp=motion \
    +domain_rand=domain_rand_g1_sim2real \
    +rewards=motion/agacharse_rewards_v5 \
    +robot=g1/g1_29dof \
    +terrain=terrain_base \
    +obs=motion/agacharse_obs \
    num_envs=4096 \
    project_name=G1_Agacharse \
    experiment_name=G1_Agacharse_V10 \
    "env.config.motion.motion_id=1" \
    "robot.control.action_scale=0.25" \
    "robot.control.action_clip_value=3.0" \
    "robot.control.stiffness.hip_pitch=40" \
    "robot.control.stiffness.hip_roll=40" \
    "robot.control.stiffness.hip_yaw=40" \
    "robot.control.stiffness.knee=100" \
    "robot.control.stiffness.ankle_pitch=28" \
    "robot.control.stiffness.ankle_roll=28" \
    "robot.control.damping.hip_pitch=2.6" \
    "robot.control.damping.hip_roll=2.6" \
    "robot.control.damping.hip_yaw=2.6" \
    "robot.control.damping.knee=6.3" \
    "robot.control.damping.ankle_pitch=1.8" \
    "robot.control.damping.ankle_roll=1.8" \
    "algo.config.init_at_random_ep_len=False" \
    "algo.config.init_noise_std=0.25" \
    "+device=cuda:0"
