"""
Export the HumanoidVerse G1 actor as a TorchScript JIT model.
Architecture: 48 → 512 → ELU → 256 → ELU → 128 → ELU → 12
Run from ~/HumanoidVerse:
    python export_jit_actor.py <checkpoint.pt> <output.pt>
"""
import sys
import torch
import torch.nn as nn

HIDDEN = [512, 256, 128]
INPUT_DIM = 48
OUTPUT_DIM = 12


def build_mlp():
    layers = []
    dims = [INPUT_DIM] + HIDDEN
    for i in range(len(dims) - 1):
        layers.append(nn.Linear(dims[i], dims[i + 1]))
        layers.append(nn.ELU())
    layers.append(nn.Linear(HIDDEN[-1], OUTPUT_DIM))
    return nn.Sequential(*layers)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python export_jit_actor.py <checkpoint.pt> <output.pt>")
        sys.exit(1)

    ckpt_path, out_path = sys.argv[1], sys.argv[2]
    ckpt = torch.load(ckpt_path, map_location="cpu")
    actor_sd = ckpt["actor_model_state_dict"]

    # Extract only actor_module.module.* keys → remap to module.*
    mlp_sd = {
        k.replace("actor_module.module.", ""): v
        for k, v in actor_sd.items()
        if k.startswith("actor_module.module.")
    }

    mlp = build_mlp()
    mlp.load_state_dict(mlp_sd)
    mlp.eval()

    scripted = torch.jit.script(mlp)
    scripted.save(out_path)
    print(f"Exported JIT actor to: {out_path}")
    print(f"Input: {INPUT_DIM} dims  |  Output: {OUTPUT_DIM} dims")

    # Quick sanity check
    dummy = torch.zeros(1, INPUT_DIM)
    out = scripted(dummy)
    print(f"Sanity check — output shape: {out.shape}, max: {out.abs().max():.4f}")
