"""Pack OromoLM CPT data with the deterministic Gemma +4K tokenizer.

Builds both the original v0.1 pilot workload and the fresh v0.3 continuation
workload so the +4K ablation can replay the same two-stage exposure trajectory
used by the +8K reference.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from transformers import AutoTokenizer

TOKENIZER = Path("tokenizer/augmentation/artifacts/gemma-3-1b-pt-oromo-4k")
EXPECTED_TOKENIZER_LEN = 266_145

PILOT = {
    "train": (
        Path("training/data/oromocorpus-cpt-pilot-v0.1/train.jsonl"),
        "9c71050faca4be2700ccbfb94737a8e8f190f3d9a3325b70fec60745c48b1a0a",
    ),
    "validation": (
        Path("training/data/oromocorpus-cpt-pilot-v0.1/validation.jsonl"),
        "cd1872643749992c7d4e22dad9b7dbe34907f0a5f96204c3040d428fc749a3d8",
    ),
}
CONTINUATION = {
    "train": (
        Path("training/data/oromocorpus-cpt-continuation-v0.3/train.jsonl"),
        "814f52575f4e4e38ff64b98b01bbe3837d17129cc2628d43cd8e571d1d2b298d",
    ),
    "validation": PILOT["validation"],
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def verify(path: Path, expected: str) -> None:
    actual = sha256_file(path)
    if actual != expected:
        raise RuntimeError(f"SHA mismatch for {path}\nExpected: {expected}\nActual:   {actual}")


def iter_texts(path: Path):
    with path.open(encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            row = json.loads(line)
            text = row.get("text")
            if not isinstance(text, str) or not text.strip():
                raise ValueError(f"Invalid text at {path}:{line_no}")
            yield text


def pack(tokenizer, source: Path, destination: Path, seq_len: int) -> dict:
    eos = tokenizer.eos_token_id
    if eos is None:
        raise RuntimeError("Tokenizer has no EOS token")
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        raise FileExistsError(f"Refusing to overwrite {destination}")

    buf: list[int] = []
    records = content_tokens = total_tokens = sequences = 0
    with destination.open("x", encoding="utf-8") as out:
        for text in iter_texts(source):
            ids = tokenizer.encode(text, add_special_tokens=False)
            records += 1
            content_tokens += len(ids)
            ids.append(eos)
            total_tokens += len(ids)
            buf.extend(ids)
            while len(buf) >= seq_len:
                block = buf[:seq_len]
                del buf[:seq_len]
                out.write(json.dumps({"input_ids": block}, separators=(",", ":")) + "\n")
                sequences += 1
        final_partial = len(buf)
        if buf:
            out.write(json.dumps({"input_ids": buf}, separators=(",", ":")) + "\n")
            sequences += 1

    return {
        "source_records": records,
        "content_tokens": content_tokens,
        "total_tokens_with_eos": total_tokens,
        "sequence_length": seq_len,
        "packed_sequences": sequences,
        "final_partial_tokens": final_partial,
        "output_path": str(destination),
        "output_sha256": sha256_file(destination),
    }


def build(dataset_name: str, inputs: dict, seq_len: int, tokenizer) -> None:
    root = Path("training/packed") / dataset_name / "oromo4k" / f"seq{seq_len}"
    manifest_path = root / "manifest.json"
    if manifest_path.exists():
        raise FileExistsError(f"Refusing to overwrite {manifest_path}")

    splits = {}
    for split, (source, expected) in inputs.items():
        verify(source, expected)
        splits[split] = pack(tokenizer, source, root / f"{split}.jsonl", seq_len)

    manifest = {
        "format_version": 1,
        "dataset": dataset_name,
        "variant": "oromo4k",
        "tokenizer": str(TOKENIZER),
        "tokenizer_length": len(tokenizer),
        "sequence_length": seq_len,
        "packing_policy": (
            "concatenate documents with exactly one EOS separator; "
            "fixed-length blocks; retain final partial block"
        ),
        "inputs": {
            k: {"path": str(v[0]), "sha256": v[1]}
            for k, v in inputs.items()
        },
        "splits": splits,
    }
    root.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"dataset": dataset_name, "splits": splits}, indent=2))
    print("manifest", manifest_path)
    print("manifest_sha256", sha256_file(manifest_path))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--dataset", choices=("pilot", "continuation", "all"), default="all")
    p.add_argument("--sequence-length", type=int, default=1024)
    args = p.parse_args()

    tokenizer = AutoTokenizer.from_pretrained(TOKENIZER, use_fast=True)
    if len(tokenizer) != EXPECTED_TOKENIZER_LEN:
        raise RuntimeError(f"Unexpected +4K tokenizer length: {len(tokenizer)}")

    if args.dataset in ("pilot", "all"):
        build("oromocorpus-cpt-pilot-v0.1", PILOT, args.sequence_length, tokenizer)
    if args.dataset in ("continuation", "all"):
        build("oromocorpus-cpt-continuation-v0.3", CONTINUATION, args.sequence_length, tokenizer)


if __name__ == "__main__":
    main()
