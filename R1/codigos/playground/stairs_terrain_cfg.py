# Copyright (c) 2022-2026, The Isaac Lab Project Developers.
# SPDX-License-Identifier: BSD-3-Clause
"""Playground completo: rough + slope + gaps + obstáculos + escaleras."""
from __future__ import annotations

import isaaclab.sim as sim_utils
from isaaclab.terrains import TerrainGeneratorCfg, TerrainImporterCfg
from isaaclab.terrains.config.rough import (
    HfDiscreteObstaclesTerrainCfg,
    HfInvertedPyramidStairsTerrainCfg,
    HfPyramidSlopedTerrainCfg,
    HfPyramidStairsTerrainCfg,
    HfRandomUniformTerrainCfg,
    MeshGapTerrainCfg,
)


PYRAMID_STAIRS_CFG = HfPyramidStairsTerrainCfg(
    proportion=0.4,
    border_width=1.0,
    horizontal_scale=0.1,
    vertical_scale=0.005,
    slope_threshold=0.75,
    step_height_range=(0.05, 0.20),
    step_width=0.30,
    platform_width=2.0,
    holes=False,
)

INVERTED_PYRAMID_STAIRS_CFG = HfInvertedPyramidStairsTerrainCfg(
    proportion=0.2,
    border_width=1.0,
    horizontal_scale=0.1,
    vertical_scale=0.005,
    slope_threshold=0.75,
    step_height_range=(0.05, 0.20),
    step_width=0.30,
    platform_width=2.0,
    holes=False,
)

ROUGH_TERRAIN_CFG = HfRandomUniformTerrainCfg(
    proportion=0.2,
    horizontal_scale=0.1,
    vertical_scale=0.005,
    border_width=0.25,
    noise_range=(0.02, 0.10),
    noise_step=0.02,
)

SLOPE_CFG = HfPyramidSlopedTerrainCfg(
    proportion=0.1,
    horizontal_scale=0.1,
    vertical_scale=0.005,
    slope_range=(0.0, 0.4),
    border_width=0.25,
    platform_width=2.0,
)

GAP_CFG = MeshGapTerrainCfg(
    proportion=0.05,
    gap_width_range=(0.05, 0.30),
    platform_width=2.0,
)

OBSTACLES_CFG = HfDiscreteObstaclesTerrainCfg(
    proportion=0.05,
    horizontal_scale=0.1,
    vertical_scale=0.005,
    obstacle_height_range=(0.05, 0.20),
    obstacle_width_range=(0.10, 0.30),
    num_obstacles=10,
    border_width=0.25,
    platform_width=2.0,
)

TERRAIN_GENERATOR_CFG = TerrainGeneratorCfg(
    seed=0,
    size=(8.0, 8.0),
    border_width=20.0,
    num_rows=10,
    num_cols=20,
    horizontal_scale=0.1,
    vertical_scale=0.005,
    slope_threshold=0.75,
    use_cache=False,
    sub_terrains={
        "pyramid_stairs":          PYRAMID_STAIRS_CFG,
        "inverted_pyramid_stairs": INVERTED_PYRAMID_STAIRS_CFG,
        "rough":                   ROUGH_TERRAIN_CFG,
        "slope":                   SLOPE_CFG,
        "gap":                     GAP_CFG,
        "obstacles":               OBSTACLES_CFG,
    },
    curriculum=True,
)

PLAYGROUND_TERRAIN_CFG = TerrainImporterCfg(
    prim_path="/World/ground",
    terrain_type="generator",
    terrain_generator=TERRAIN_GENERATOR_CFG,
    max_init_terrain_level=5,
    collision_group=-1,
    physics_material=sim_utils.RigidBodyMaterialCfg(
        friction_combine_mode="multiply",
        restitution_combine_mode="multiply",
        static_friction=1.0,
        dynamic_friction=1.0,
    ),
    debug_vis=False,
)
