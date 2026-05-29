# Copyright (c) 2022-2026, The Isaac Lab Project Developers.
# SPDX-License-Identifier: BSD-3-Clause
"""Playground sin escaleras (etapa intermedia del curriculum)."""
from __future__ import annotations

import isaaclab.sim as sim_utils
from isaaclab.terrains import TerrainGeneratorCfg, TerrainImporterCfg
from isaaclab.terrains.config.rough import (
    HfPyramidSlopedTerrainCfg,
    HfRandomUniformTerrainCfg,
)


ROUGH_CFG = HfRandomUniformTerrainCfg(
    proportion=0.6,
    horizontal_scale=0.1,
    vertical_scale=0.005,
    border_width=0.25,
    noise_range=(0.01, 0.06),
    noise_step=0.01,
)

SLOPE_CFG = HfPyramidSlopedTerrainCfg(
    proportion=0.4,
    horizontal_scale=0.1,
    vertical_scale=0.005,
    slope_range=(0.0, 0.25),
    border_width=0.25,
    platform_width=2.0,
)

ROUGH_PLAYGROUND_GENERATOR_CFG = TerrainGeneratorCfg(
    seed=0,
    size=(8.0, 8.0),
    border_width=20.0,
    num_rows=8,
    num_cols=20,
    horizontal_scale=0.1,
    vertical_scale=0.005,
    slope_threshold=0.75,
    use_cache=False,
    sub_terrains={
        "rough": ROUGH_CFG,
        "slope": SLOPE_CFG,
    },
    curriculum=True,
)

ROUGH_PLAYGROUND_TERRAIN_CFG = TerrainImporterCfg(
    prim_path="/World/ground",
    terrain_type="generator",
    terrain_generator=ROUGH_PLAYGROUND_GENERATOR_CFG,
    max_init_terrain_level=4,
    collision_group=-1,
    physics_material=sim_utils.RigidBodyMaterialCfg(
        friction_combine_mode="multiply",
        restitution_combine_mode="multiply",
        static_friction=1.0,
        dynamic_friction=1.0,
    ),
    debug_vis=False,
)
