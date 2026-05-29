import sys
import torch
import torch.nn as nn

HIDDEN = [512, 256, 128]
DEFAULT_INPUT_DIM  = 62
DEFAULT_OUTPUT_DIM = 29


def build_mlp(input_dim, output_dim):
    layers = []
    dims = [input_dim] + HIDDEN
    for i in range(len(dims) - 1):
        layers.append(nn.Linear(dims[i], dims[i + 1]))
        layers.append(nn.ELU())
    layers.append(nn.Linear(HIDDEN[-1], output_dim))
    return nn.Sequential(*layers)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("checkpoint", help="Ruta al checkpoint .pt")
    parser.add_argument("output",     help="Ruta de salida JIT .pt")
    parser.add_argument("--input_dim",  type=int, default=DEFAULT_INPUT_DIM,
                        help=f"Dimensión de entrada (default: {DEFAULT_INPUT_DIM})")
    parser.add_argument("--output_dim", type=int, default=DEFAULT_OUTPUT_DIM,
                        help=f"Dimensión de salida (default: {DEFAULT_OUTPUT_DIM})")
    args = parser.parse_args()

    ckpt = torch.load(args.checkpoint, map_location="cpu")
    actor_sd = ckpt["actor_model_state_dict"]

    mlp_sd = {
        k.replace("actor_module.module.", ""): v
        for k, v in actor_sd.items()
        if k.startswith("actor_module.module.")
    }

    # Auto-detectar input_dim desde los pesos si es posible
    first_weight_key = next((k for k in mlp_sd if "0.weight" in k), None)
    if first_weight_key:
        detected_input = mlp_sd[first_weight_key].shape[1]
        if detected_input != args.input_dim:
            print(f"[INFO] input_dim detectado del checkpoint: {detected_input} "
                  f"(argumento: {args.input_dim}) — usando {detected_input}")
            args.input_dim = detected_input

    mlp = build_mlp(args.input_dim, args.output_dim)
    mlp.load_state_dict(mlp_sd)
    mlp.eval()

    scripted = torch.jit.script(mlp)
    scripted.save(args.output)
    print(f"Exportado JIT: {args.output}")
    print(f"Input: {args.input_dim} dims  |  Output: {args.output_dim} dims")

    dummy = torch.zeros(1, args.input_dim)
    out = scripted(dummy)
    print(f"Sanity check — output shape: {out.shape}, max: {out.abs().max():.4f}")
