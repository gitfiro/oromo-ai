"""CPU preflight for the OromoLM +4K two-stage ablation."""
from __future__ import annotations

import json
import math
from pathlib import Path

from transformers import AutoTokenizer

TOKENIZER = Path("tokenizer/augmentation/artifacts/gemma-3-1b-pt-oromo-4k")
INIT = Path("models/initialization/oromolm-gemma-3-1b-pt-4k-v0.1")
PACKED = Path("training/packed")
EXPECTED_LEN = 266_145
GRAD_ACCUM = 16

DATASETS = (
    ("pilot", PACKED / "oromocorpus-cpt-pilot-v0.1/oromo4k/seq1024/manifest.json"),
    ("continuation", PACKED / "oromocorpus-cpt-continuation-v0.3/oromo4k/seq1024/manifest.json"),
)


def load_json(path: Path):
    if not path.exists():
        raise FileNotFoundError(path)
    return json.loads(path.read_text())


def main() -> None:
    tok = AutoTokenizer.from_pretrained(TOKENIZER, use_fast=True)
    if len(tok) != EXPECTED_LEN:
        raise RuntimeError(f"Tokenizer length {len(tok)} != {EXPECTED_LEN}")

    init_cfg = load_json(INIT / "config.json")
    if int(init_cfg["vocab_size"]) != EXPECTED_LEN:
        raise RuntimeError(f"Initialized model vocab_size != {EXPECTED_LEN}")
    if not (INIT / "model.safetensors").exists():
        raise FileNotFoundError(INIT / "model.safetensors")

    print("=== OromoLM +4K ablation preflight ===")
    print(f"tokenizer length: {len(tok):,}")
    print(f"maximum token ID: {len(tok)-1:,}")

    total_training_tokens = 0
    total_updates = 0

    for label, manifest_path in DATASETS:
        m = load_json(manifest_path)
        if m["variant"] != "oromo4k":
            raise RuntimeError(f"Wrong variant in {manifest_path}")
        if int(m["tokenizer_length"]) != EXPECTED_LEN:
            raise RuntimeError(f"Wrong tokenizer length in {manifest_path}")

        tr = m["splits"]["train"]
        va = m["splits"]["validation"]
        train_sequences = int(tr["packed_sequences"])
        train_tokens = int(tr["total_tokens_with_eos"])
        updates = math.ceil(train_sequences / GRAD_ACCUM)
        total_training_tokens += train_tokens
        total_updates += updates

        print()
        print(label)
        print(f"  train sequences: {train_sequences:,}")
        print(f"  train tokens: {train_tokens:,}")
        print(f"  validation sequences: {int(va['packed_sequences']):,}")
        print(f"  validation tokens: {int(va['total_tokens_with_eos']):,}")
        print(f"  optimizer updates (1 epoch): {updates:,}")
        print(f"  train SHA-256: {tr['output_sha256']}")
        print(f"  validation SHA-256: {va['output_sha256']}")

    print()
    print(f"two-stage training tokens: {total_training_tokens:,}")
    print(f"two-stage optimizer updates: {total_updates:,}")
    print("effective sequences/update: 16")
    print("PREFLIGHT SUCCESS")


if __name__ == "__main__":
    main()
