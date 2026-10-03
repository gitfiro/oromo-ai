from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from transformers import AutoTokenizer


PILOT_DIR = Path(
    "training/data/oromocorpus-cpt-pilot-v0.1"
)

EXPECTED = {
    "train": (
        "9c71050faca4be2700ccbfb94737a8e8"
        "f190f3d9a3325b70fec60745c48b1a0a"
    ),
    "validation": (
        "cd1872643749992c7d4e22dad9b7dbe3"
        "4907f0a5f96204c3040d428fc749a3d8"
    ),
}

TOKENIZERS = {
    "native": "google/gemma-3-1b-pt",
    "oromo8k": (
        "tokenizer/augmentation/artifacts/"
        "gemma-3-1b-pt-oromo-8k"
    ),
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()

    with path.open("rb") as f:
        while chunk := f.read(1024 * 1024):
            h.update(chunk)

    return h.hexdigest()


def verify_input(
    split: str,
    path: Path,
) -> None:
    digest = sha256_file(path)

    if digest != EXPECTED[split]:
        raise RuntimeError(
            f"{split} SHA-256 mismatch\n"
            f"Expected: {EXPECTED[split]}\n"
            f"Actual:   {digest}"
        )


def iter_texts(path: Path):
    with path.open(
        "r",
        encoding="utf-8",
    ) as handle:
        for line in handle:
            if not line.strip():
                continue

            row = json.loads(line)

            text = row.get("text")

            if not isinstance(text, str):
                raise RuntimeError(
                    "Pilot row missing text."
                )

            yield text


def pack_split(
    tokenizer,
    input_path: Path,
    output_path: Path,
    seq_len: int,
):
    eos = tokenizer.eos_token_id

    if eos is None:
        raise RuntimeError(
            "Tokenizer has no EOS token."
        )

    buffer: list[int] = []

    source_records = 0
    content_tokens = 0
    total_tokens = 0
    packed_sequences = 0

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output_path.open(
        "w",
        encoding="utf-8",
    ) as out:
        for text in iter_texts(
            input_path
        ):
            ids = tokenizer.encode(
                text,
                add_special_tokens=False,
            )

            source_records += 1
            content_tokens += len(ids)

            # One EOS separator per document.
            ids.append(eos)

            total_tokens += len(ids)
            buffer.extend(ids)

            while len(buffer) >= seq_len:
                block = buffer[:seq_len]
                del buffer[:seq_len]

                row = {
                    "input_ids": block,
                }

                out.write(
                    json.dumps(
                        row,
                        separators=(",", ":"),
                    )
                    + "\n"
                )

                packed_sequences += 1

        # Keep the final partial block.
        #
        # Padding will be handled by the training
        # collator. We do not silently discard text.
        remainder_tokens = len(buffer)

        if buffer:
            out.write(
                json.dumps(
                    {
                        "input_ids": buffer,
                    },
                    separators=(",", ":"),
                )
                + "\n"
            )

            packed_sequences += 1

    return {
        "source_records": (
            source_records
        ),
        "content_tokens": (
            content_tokens
        ),
        "total_tokens_with_eos": (
            total_tokens
        ),
        "sequence_length": (
            seq_len
        ),
        "packed_sequences": (
            packed_sequences
        ),
        "final_partial_tokens": (
            remainder_tokens
        ),
        "output_path": str(
            output_path
        ),
        "output_sha256": (
            sha256_file(
                output_path
            )
        ),
    }


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--variant",
        required=True,
        choices=[
            "native",
            "oromo8k",
        ],
    )

    parser.add_argument(
        "--sequence-length",
        type=int,
        default=1024,
    )

    args = parser.parse_args()

    variant = args.variant
    seq_len = args.sequence_length

    tokenizer_ref = (
        TOKENIZERS[variant]
    )

    print(
        "=== OromoLM CPT Packed Dataset Builder ==="
    )
    print()
    print(
        f"Variant:         {variant}"
    )
    print(
        f"Tokenizer:       {tokenizer_ref}"
    )
    print(
        f"Sequence length: {seq_len:,}"
    )

    tokenizer = (
        AutoTokenizer.from_pretrained(
            tokenizer_ref,
            use_fast=True,
        )
    )

    print(
        f"Tokenizer size:  {len(tokenizer):,}"
    )

    output_dir = (
        Path("training/packed")
        / "oromocorpus-cpt-pilot-v0.1"
        / variant
        / f"seq{seq_len}"
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    manifest = {
        "format_version": 1,
        "dataset": (
            "oromocorpus-cpt-pilot-v0.1"
        ),
        "variant": variant,
        "tokenizer": (
            tokenizer_ref
        ),
        "tokenizer_length": (
            len(tokenizer)
        ),
        "sequence_length": (
            seq_len
        ),
        "packing_policy": (
            "concatenate documents with "
            "one EOS separator; fixed-length "
            "blocks; retain final partial block"
        ),
        "splits": {},
    }

    for split in (
        "train",
        "validation",
    ):
        input_path = (
            PILOT_DIR
            / f"{split}.jsonl"
        )

        verify_input(
            split,
            input_path,
        )

        output_path = (
            output_dir
            / f"{split}.jsonl"
        )

        print()
        print(
            f"Packing {split}..."
        )

        stats = pack_split(
            tokenizer,
            input_path,
            output_path,
            seq_len,
        )

        manifest[
            "splits"
        ][split] = stats

        print(
            f"  records: "
            f"{stats['source_records']:,}"
        )

        print(
            f"  tokens + EOS: "
            f"{stats['total_tokens_with_eos']:,}"
        )

        print(
            f"  packed sequences: "
            f"{stats['packed_sequences']:,}"
        )

        print(
            f"  final partial: "
            f"{stats['final_partial_tokens']:,}"
        )

        print(
            f"  SHA-256: "
            f"{stats['output_sha256']}"
        )

    manifest_path = (
        output_dir
        / "manifest.json"
    )

    manifest_path.write_text(
        json.dumps(
            manifest,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    print()
    print("Manifest:")
    print(manifest_path)
    print(
        "SHA-256: "
        f"{sha256_file(manifest_path)}"
    )

    print()
    print("=" * 72)
    print("SUCCESS")
    print("=" * 72)


if __name__ == "__main__":
    main()