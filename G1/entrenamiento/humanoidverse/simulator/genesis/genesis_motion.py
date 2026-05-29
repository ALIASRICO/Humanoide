import torch
from humanoidverse.simulator.genesis.genesis import Genesis


class GenesisMotion(Genesis):
    """Genesis simulator for motion tasks — reuses base Genesis without modifications."""

    def __init__(self, config, device):
        super().__init__(config, device)
