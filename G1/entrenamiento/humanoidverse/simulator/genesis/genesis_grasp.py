import torch
import genesis as gs
from loguru import logger
from humanoidverse.simulator.genesis.genesis import Genesis


class GenesisGrasp(Genesis):
    """Genesis simulator extended with table and grasp box entities for manipulation tasks."""

    def __init__(self, config, device):
        super().__init__(config, device)

    def setup_terrain(self, mesh_type):
        """Add ground plane and table."""
        super().setup_terrain(mesh_type)

        grasp_cfg = self.cfg.grasp
        table_size = grasp_cfg.table_size
        table_pos = grasp_cfg.table_pos

        logger.info(f"[Grasp] Adding table at {table_pos} size {table_size}")
        self.table = self.scene.add_entity(
            gs.morphs.Box(
                size=tuple(table_size),
                pos=tuple(table_pos),
            ),
        )

    def load_assets(self):
        """Load robot and grasp box."""
        super().load_assets()

        grasp_cfg = self.cfg.grasp
        box_size = grasp_cfg.box_size
        box_pos = grasp_cfg.box_default_pos

        logger.info(f"[Grasp] Adding box at {box_pos} size {box_size}")
        self.grasp_box = self.scene.add_entity(
            gs.morphs.Box(
                size=tuple(box_size),
                pos=tuple(box_pos),
            ),
        )

    def prepare_sim(self):
        super().prepare_sim()
        self.box_pos = self.grasp_box.get_pos()
        self.box_quat = self.grasp_box.get_quat()
        self.box_vel = self.grasp_box.get_vel()

    def refresh_sim_tensors(self):
        """Refresh robot and box states."""
        super().refresh_sim_tensors()
        self.box_pos = self.grasp_box.get_pos()
        self.box_quat = self.grasp_box.get_quat()
        self.box_vel = self.grasp_box.get_vel()

    def reset_box(self, env_ids, box_pos):
        """Reset box position and zero velocity for specified environments."""
        self.grasp_box.set_pos(box_pos, zero_velocity=True, envs_idx=env_ids)
