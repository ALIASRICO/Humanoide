#!/bin/bash
source /home/udc/miniconda3/etc/profile.d/conda.sh
conda activate hgen
cd /home/udc/Humanoide/G1/entrenamiento
python humanoidverse/eval_agent.py \
    +simulator=genesis \
    +exp=motion \
    +domain_rand=NO_domain_rand \
    +rewards=motion/agacharse_rewards_v5 \
    +robot=g1/g1_29dof \
    +terrain=terrain_base \
    +obs=motion/agacharse_obs \
    +num_envs=1 \
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
    "checkpoint='logs/G1_Agacharse/20260522_143409-G1_Agacharse_V10-motion-g1_29dof/model_6000.pt'" \
    "+device=cuda:0"
