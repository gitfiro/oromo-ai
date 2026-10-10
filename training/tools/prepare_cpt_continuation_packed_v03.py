"""Pack the frozen OromoLM v0.3 fresh-continuation corpus with Gemma +8K.

Training comes from the fresh v0.3 continuation JSONL. Validation deliberately
remains the original frozen v0.1 Oromo validation split so learning-curve
measurements stay comparable to the established 1.733832395 BPB target.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from transformers import AutoTokenizer


TRAIN = Path("training/data/oromocorpus-cpt-continuation-v0.3/train.jsonl")
TRAIN_EXPECTED = "814f52575f4e4e38ff64b98b01bbe3837d17129cc2628d43cd8e571d1d2b298d"
VALIDATION = Path("training/data/oromocorpus-cpt-pilot-v0.1/validation.jsonl")
VALIDATION_EXPECTED = "cd1872643749992c7d4e22dad9b7dbe34907f0a5f96204c3040d428fc749a3d8"
TOKENIZER = Path("tokenizer/augmentation/artifacts/gemma-3-1b-pt-oromo-8k")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def verify(path: Path, expected: str) -> None:
    actual = sha256_file(path)
    if actual != expected:
        raise RuntimeError(
            f"SHA mismatch for {path}\nExpected: {expected}\nActual:   {actual}"
        )


def iter_texts(path: Path):
    with path.open(encoding="utf-8") as stream:
        for line_no, line in enumerate(stream, 1):
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

    buffer: list[int] = []
    source_records = 0
    content_tokens = 0
    total_tokens = 0
    packed_sequences = 0

    with destination.open("x", encoding="utf-8") as out:
        for text in iter_texts(source):
            ids = tokenizer.encode(text, add_special_tokens=False)
            source_records += 1
            content_tokens += len(ids)
            ids.append(eos)
            total_tokens += len(ids)
            buffer.extend(ids)

            while len(buffer) >= seq_len:
                block = buffer[:seq_len]
                del buffer[:seq_len]
                out.write(json.dumps({"input_ids": block}, separators=(",", ":")) + "\n")
                packed_sequences += 1

        final_partial = len(buffer)
        if buffer:
            out.write(json.dumps({"input_ids": buffer}, separators=(",", ":")) + "\n")
            packed_sequences += 1

    return {
        "source_records": source_records,
        "content_tokens": content_tokens,
        "total_tokens_with_eos": total_tokens,
        "sequence_length": seq_len,
        "packed_sequences": packed_sequences,
        "final_partial_tokens": final_partial,
        "output_path": str(destination),
        "output_sha256": sha256_file(destination),
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--sequence-length", type=int, default=1024)
    args = p.parse_args()

    verify(TRAIN, TRAIN_EXPECTED)
    verify(VALIDATION, VALIDATION_EXPECTED)

    tokenizer = AutoTokenizer.from_pretrained(TOKENIZER, use_fast=True)
    if len(tokenizer) != 270_145:
        raise RuntimeError(f"Unexpected +8K tokenizer length: {len(tokenizer)}")

    root = (
        Path("training/packed")
        / "oromocorpus-cpt-continuation-v0.3"
        / "oromo8k"
        / f"seq{args.sequence_length}"
    )
    manifest_path = root / "manifest.json"
    if manifest_path.exists():
        p.error(f"Manifest exists; refusing overwrite: {manifest_path}")

    print("Packing fresh v0.3 train...")
    train_stats = pack(
        tokenizer,
        TRAIN,
        root / "train.jsonl",
        args.sequence_length,
    )

    print("Packing frozen v0.1 validation with same +8K tokenizer...")
    validation_stats = pack(
        tokenizer,
        VALIDATION,
        root / "validation.jsonl",
        args.sequence_length,
    )

    manifest = {
        "format_version": 1,
        "dataset": "oromocorpus-cpt-continuation-v0.3",
        "variant": "oromo8k",
        "tokenizer": str(TOKENIZER),
        "tokenizer_length": len(tokenizer),
        "sequence_length": args.sequence_length,
        "training_policy": "fresh v0.3 continuation only",
        "validation_policy": "reuse frozen v0.1 Oromo validation text",
        "inputs": {
            "train": {"path": str(TRAIN), "sha256": TRAIN_EXPECTED},
            "validation": {
                "path": str(VALIDATION),
                "sha256": VALIDATION_EXPECTED,
            },
        },
        "packing_policy": (
            "concatenate documents with exactly one EOS separator; fixed-length "
            "blocks; retain final partial block"
        ),
        "splits": {
            "train": train_stats,
            "validation": validation_stats,
        },
    }

    root.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print(json.dumps(manifest["splits"], indent=2, sort_keys=True))
    print("Manifest:", manifest_path)
    print("Manifest SHA-256:", sha256_file(manifest_path))


if __name__ == "__main__":
    main()
