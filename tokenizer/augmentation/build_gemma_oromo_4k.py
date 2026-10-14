"""Build the deterministic Gemma +4K Oromo tokenizer from the frozen +8K artifact.

The +8K experiment was cumulative: the first 4,000 lexical additions are the
exact +4K candidate selected under the same ranking. This tool reconstructs that
candidate without reranking or consulting evaluation data.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from transformers import AddedToken, AutoTokenizer

BASE_MODEL = "google/gemma-3-1b-pt"
SOURCE_8K = Path("tokenizer/augmentation/artifacts/gemma-3-1b-pt-oromo-8k")
OUTPUT = Path("tokenizer/augmentation/artifacts/gemma-3-1b-pt-oromo-4k")
BASE_LEN = 262_145
START_ID = 262_145
COUNT = 4_000
FINAL_LEN = 266_145


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
        p.error(f"Refusing to overwrite existing artifact: {args.output}")

    base = AutoTokenizer.from_pretrained(BASE_MODEL, use_fast=True)
    source = AutoTokenizer.from_pretrained(SOURCE_8K, use_fast=True)

    if len(base) != BASE_LEN:
        raise RuntimeError(f"Unexpected native tokenizer length: {len(base)}")
    if len(source) != BASE_LEN + 8_000:
        raise RuntimeError(f"Unexpected +8K tokenizer length: {len(source)}")

    added = source.get_added_vocab()
    by_id = sorted(
        ((int(token_id), token) for token, token_id in added.items()
         if START_ID <= int(token_id) < START_ID + COUNT),
        key=lambda x: x[0],
    )
    if len(by_id) != COUNT:
        raise RuntimeError(f"Expected {COUNT} first Oromo additions; found {len(by_id)}")

    for expected_id, (source_id, token) in enumerate(by_id, start=START_ID):
        if source_id != expected_id:
            raise RuntimeError(
                f"Non-contiguous +8K source IDs: expected {expected_id}, got {source_id}"
            )
        delta = base.add_tokens([
            AddedToken(
                token,
                single_word=True,
                lstrip=False,
                rstrip=False,
                normalized=True,
                special=False,
            )
        ])
        if delta != 1:
            raise RuntimeError(f"Could not add {token!r} exactly once")
        actual_id = base.get_added_vocab().get(token)
        if actual_id != expected_id:
            raise RuntimeError(
                f"ID mismatch for {token!r}: expected {expected_id}, got {actual_id}"
            )

    if len(base) != FINAL_LEN:
        raise RuntimeError(f"Unexpected final +4K length: {len(base)}")

    args.output.mkdir(parents=True)
    base.save_pretrained(args.output)

    files = {}
    for name in ("tokenizer.json", "tokenizer_config.json"):
        path = args.output / name
        if path.exists():
            files[name] = {"bytes": path.stat().st_size, "sha256": sha256_file(path)}

    manifest = {
        "format_version": 1,
        "artifact": "gemma-3-1b-pt-oromo-4k",
        "base_model": BASE_MODEL,
        "derivation": "first 4,000 Oromo lexical additions from frozen cumulative +8K artifact",
        "source_8k_artifact": str(SOURCE_8K),
        "augmentation": {
            "type": "whole_word_lexical",
            "native_tokenizer_length": BASE_LEN,
            "added_tokens": COUNT,
            "oromo_start_id": START_ID,
            "oromo_end_id": START_ID + COUNT - 1,
            "final_tokenizer_length": FINAL_LEN,
            "added_token_configuration": {
                "single_word": True,
                "lstrip": False,
                "rstrip": False,
                "normalized": True,
                "special": False,
            },
        },
        "expected_frozen_holdout_metrics": {
            "tokens_per_word": 2.3696594464573146,
            "fragmentation_rate": 0.38208431548677635,
            "single_token_word_rate": 0.6179156845132237,
            "unknown_tokens": 0,
            "tokens_per_word_reduction_vs_native": 0.14929792059836908,
        },
        "artifact_files": files,
        "status": "generated_ablation_candidate",
    }
    manifest_path = args.output / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(json.dumps(manifest, indent=2, sort_keys=True))
    print("manifest_sha256", sha256_file(manifest_path))


if __name__ == "__main__":
    main()
