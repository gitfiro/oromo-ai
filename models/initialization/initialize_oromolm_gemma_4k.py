"""Initialize Gemma 3 1B with the frozen +4K Oromo tokenizer.

Each appended Oromo embedding is the centroid of its native-tokenization pieces,
scaled to the native embedding table's mean L2 norm. Native rows are preserved.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

BASE_MODEL = "google/gemma-3-1b-pt"
TOKENIZER = Path("tokenizer/augmentation/artifacts/gemma-3-1b-pt-oromo-4k")
OUTPUT = Path("models/initialization/oromolm-gemma-3-1b-pt-4k-v0.1")
NATIVE_ROWS = 262_144
IMAGE_SOFT_TOKEN_ID = 262_144
OROMO_START_ID = 262_145
FINAL_ROWS = 266_145


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", type=Path, default=OUTPUT)
    args = p.parse_args()
    if args.output.exists():
        p.error(f"Refusing to overwrite existing output: {args.output}")

    native_tok = AutoTokenizer.from_pretrained(BASE_MODEL, use_fast=True)
    tok = AutoTokenizer.from_pretrained(TOKENIZER, use_fast=True)
    if len(tok) != FINAL_ROWS:
        raise RuntimeError(f"Unexpected +4K tokenizer length: {len(tok)}")

    model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        torch_dtype=torch.float32,
        low_cpu_mem_usage=True,
    )
    emb = model.get_input_embeddings()
    if emb.num_embeddings != NATIVE_ROWS:
        raise RuntimeError(f"Unexpected native embedding rows: {emb.num_embeddings}")

    native_weight = emb.weight.detach().clone()
    native_mean_norm = native_weight.norm(dim=1).mean()
    model.resize_token_embeddings(FINAL_ROWS, mean_resizing=False)
    resized = model.get_input_embeddings().weight

    added_vocab = tok.get_added_vocab()
    pieces_counts = []
    with torch.no_grad():
        for token_id in range(OROMO_START_ID, FINAL_ROWS):
            token = next((t for t, i in added_vocab.items() if int(i) == token_id), None)
            if token is None:
                raise RuntimeError(f"Missing added token for ID {token_id}")
            piece_ids = native_tok.encode(token, add_special_tokens=False)
            if not piece_ids:
                raise RuntimeError(f"No native pieces for {token!r}")
            if any(i >= NATIVE_ROWS for i in piece_ids):
                raise RuntimeError(f"Non-native piece while initializing {token!r}: {piece_ids}")
            vector = native_weight[piece_ids].mean(dim=0)
            norm = vector.norm()
            if norm == 0:
                raise RuntimeError(f"Zero centroid norm for {token!r}")
            resized[token_id].copy_(vector * (native_mean_norm / norm))
            pieces_counts.append(len(piece_ids))

        # Preserve every original model row exactly.
        resized[:NATIVE_ROWS].copy_(native_weight)

    if model.config.vocab_size != FINAL_ROWS:
        raise RuntimeError(f"Unexpected config vocab_size: {model.config.vocab_size}")

    args.output.mkdir(parents=True)
    model.save_pretrained(args.output, safe_serialization=True)
    tok.save_pretrained(args.output)

    installed = resized[OROMO_START_ID:FINAL_ROWS].detach()
    manifest = {
        "format_version": 1,
        "artifact": "OromoLM Gemma-3-1B +4K initialization",
        "base_model": BASE_MODEL,
        "tokenizer": str(TOKENIZER),
        "status": "initialized_not_trained",
        "vocabulary": {
            "native_model_rows": NATIVE_ROWS,
            "image_soft_token_id": IMAGE_SOFT_TOKEN_ID,
            "oromo_start_id": OROMO_START_ID,
            "oromo_end_id": FINAL_ROWS - 1,
            "oromo_additions": FINAL_ROWS - OROMO_START_ID,
            "final_rows": FINAL_ROWS,
        },
        "initialization": {
            "method": "native_subtoken_centroid_scaled_to_native_mean_l2_norm",
            "native_mean_l2_norm": float(native_mean_norm),
            "installed_mean_l2_norm": float(installed.norm(dim=1).mean()),
            "installed_std_l2_norm": float(installed.norm(dim=1).std()),
            "mean_native_pieces_per_word": sum(pieces_counts) / len(pieces_counts),
        },
        "artifact_files": {},
    }
    for name in ("config.json", "generation_config.json", "model.safetensors",
                 "tokenizer.json", "tokenizer_config.json"):
        path = args.output / name
        if path.exists():
            manifest["artifact_files"][name] = {
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }

    mp = args.output / "initialization_manifest.json"
    mp.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(json.dumps(manifest, indent=2, sort_keys=True))
    print("manifest_sha256", sha256_file(mp))


if __name__ == "__main__":
    main()
