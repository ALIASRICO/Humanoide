# Copyright (c) 2022-2026, The Isaac Lab Project Developers.
# SPDX-License-Identifier: BSD-3-Clause
"""High-Level Policy (madre): MLP pequeño que decide commands + skill gating."""
from __future__ import annotations

import torch
import torch.nn as nn


class HighLevelPolicy(nn.Module):
    """π_M: (obs_world, goal) → (cmd_vector, skill_gating).

    Output: (vx_des, vy_des, wz_des, alpha_locomotion).
    alpha ∈ [0,1] (sigmoid) → blend entre STAND y WALK.
    """
    def __init__(self, obs_dim: int, n_skills: int = 2, hidden: tuple[int, ...] = (128, 64)):
        super().__init__()
        self.n_skills = n_skills
        layers = []
        last = obs_dim
        for h in hidden:
            layers.append(nn.Linear(last, h))
            layers.append(nn.ELU())
            last = h
        # 3 cmd dims + n_skills logits
        layers.append(nn.Linear(last, 3 + n_skills))
        self.net = nn.Sequential(*layers)

    def forward(self, obs: torch.Tensor):
        out = self.net(obs)
        cmd = torch.tanh(out[..., :3])           # (vx, vy, wz) en [-1, 1]
        logits = out[..., 3:]
        if self.n_skills == 2:
            alpha = torch.sigmoid(logits[..., :1])
            return cmd, alpha
        return cmd, torch.softmax(logits, dim=-1)


class FrozenChild:
    """Wrapper para una sub-política entrenada — frozen, solo .act(obs)."""
    def __init__(self, checkpoint_path: str, agent_cfg, env, device: str):
        from rsl_rl.runners import OnPolicyRunner
        runner = OnPolicyRunner(env, agent_cfg.to_dict(), log_dir=None, device=device)
        runner.load(checkpoint_path)
        self.policy = runner.get_inference_policy(device=device)
        try:
            params = runner.alg.get_policy().parameters()
        except AttributeError:
            params = runner.alg.policy.parameters()
        for p in params:
            p.requires_grad_(False)
        self._runner = runner

    @torch.inference_mode()
    def act(self, obs: dict) -> torch.Tensor:
        return self.policy(obs)


class FSMHighLevel:
    """Alternativa determinista (sin entrenar madre): state-machine."""
    STAND, WALK, RECOVER, STAIR = range(4)

    def __init__(self, arrival_threshold: float = 0.3):
        self.arrival = arrival_threshold

    def step(
        self,
        target_xy: torch.Tensor,
        robot_xy:  torch.Tensor,
        is_falling: torch.Tensor,
        is_on_stairs: torch.Tensor,
    ):
        d = torch.norm(target_xy - robot_xy, dim=-1)
        skill = torch.full_like(d, self.WALK, dtype=torch.long)
        skill = torch.where(is_falling,    torch.full_like(skill, self.RECOVER), skill)
        skill = torch.where(d < self.arrival, torch.full_like(skill, self.STAND), skill)
        skill = torch.where(is_on_stairs,  torch.full_like(skill, self.STAIR),   skill)
        cmd = target_xy - robot_xy
        return skill, cmd
