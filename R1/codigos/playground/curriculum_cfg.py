# Copyright (c) 2022-2026, The Isaac Lab Project Developers.
# SPDX-License-Identifier: BSD-3-Clause
"""Curriculum por etapas — push-recovery + difficulty scaling."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class CurriculumStage:
    iters_until: int
    push_force_min: float
    push_force_max: float
    push_interval_s: float
    enable_com_reward: float
    max_terrain_level: int
    note: str


# === Standing curriculum (4 etapas) ===
STANDING_CURRICULUM = [
    CurriculumStage(2000,  0.0,  0.0,  1e9, 0.0, 0, "Etapa 1 — Postura estática (pushes OFF)"),
    CurriculumStage(4000,  0.0,  0.0,  1e9, 1.0, 0, "Etapa 2 — Postura activa con CoM"),
    CurriculumStage(10000, 5.0, 10.0,  1.0, 1.0, 0, "Etapa 3 — Push recovery 5–10 N"),
    CurriculumStage(15000, 15.0, 25.0, 0.8, 1.0, 0, "Etapa 4 — Stepping 15–25 N"),
]

# === Locomotion curriculum (3 etapas) ===
LOCOMOTION_CURRICULUM = [
    CurriculumStage(3000,  0.0, 0.0, 1e9, 1.0, 0, "Etapa A — Plano"),
    CurriculumStage(8000,  0.0, 0.0, 1e9, 1.0, 4, "Etapa B — Rough + Slope"),
    CurriculumStage(15000, 0.0, 0.0, 1e9, 1.0, 9, "Etapa C — Stairs full"),
]


def get_stage_for_iter(curriculum: list[CurriculumStage], it: int) -> CurriculumStage:
    """Devuelve la stage activa para una iteración dada."""
    for s in curriculum:
        if it < s.iters_until:
            return s
    return curriculum[-1]
