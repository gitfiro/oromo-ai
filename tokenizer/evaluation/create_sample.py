from __future__ import annotations

import argparse
import hashlib
import json
import random
from pathlib import Path


DEFAULT_CORPUS = Path(
    "data/processed/afriberta_oromo_v0.1.2/train.jsonl"
)
DEFAULT_OUTPUT = Path(
    "tokenizer/evaluation/samples/"
    "afriberta_oromo_v0.1.2_n10000.jsonl"
)

DEFAULT_SAMPLE_SIZE = 10_000
DEFAULT_SEED = 20260919


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Create a deterministic tokenizer evaluation sample "
            "from a processed Afaan Oromoo corpus."
        )
    )

    parser.add_argument(
        "--corpus",
        type=Path,
        default=DEFAULT_CORPUS,
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
    )

    parser.add_argument(
        "--sample-size",
        type=int,
        default=DEFAULT_SAMPLE_SIZE,
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=DEFAULT_SEED,
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.sample_size < 1:
        raise ValueError("--sample-size must be >= 1")

    if not args.corpus.is_file():
        raise FileNotFoundError(args.corpus)

    # First pass: count valid JSONL records.
    record_count = 0

    with args.corpus.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                record_count += 1

    if args.sample_size > record_count:
        raise ValueError(
            f"Requested {args.sample_size:,} records but corpus "
            f"contains only {record_count:,}"
        )

    # Deterministically select record positions.
    rng = random.Random(args.seed)

    selected_indices = sorted(
        rng.sample(range(record_count), args.sample_size)
    )

    selected_set = set(selected_indices)

    args.output.parent.mkdir(parents=True, exist_ok=True)

    written = 0
    logical_index = 0

    with (
        args.corpus.open("r", encoding="utf-8") as source,
        args.output.open("w", encoding="utf-8") as destination,
    ):
        for line in source:
            if not line.strip():
                continue

            if logical_index in selected_set:
                record = json.loads(line)

                sample_record = {
                    "record_id": record.get("record_id"),
                    "source_id": record.get("source_id"),
                    "source_line": record.get(
                        "metadata", {}
                    ).get("source_line"),
                    "text": record["text"],
                }

                destination.write(
                    json.dumps(
                        sample_record,
                        ensure_ascii=False,
                        sort_keys=True,
                    )
                    + "\n"
                )

                written += 1

            logical_index += 1

    if written != args.sample_size:
        raise RuntimeError(
            f"Expected {args.sample_size:,} records, wrote {written:,}"
        )

    print("=== Tokenizer Evaluation Sample ===")
    print(f"Corpus: {args.corpus}")
    print(f"Corpus records: {record_count:,}")
    print(f"Corpus SHA-256: {sha256_file(args.corpus)}")
    print(f"Sample: {args.output}")
    print(f"Sample records: {written:,}")
    print(f"Seed: {args.seed}")
    print(f"Sample SHA-256: {sha256_file(args.output)}")


if __name__ == "__main__":
    main()



