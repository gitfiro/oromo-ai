from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


DEFAULT_SOURCE = Path(
    "data/processed/afriberta_oromo_v0.1.2/train.jsonl"
)

DEFAULT_EVAL_SAMPLE = Path(
    "tokenizer/evaluation/samples/"
    "afriberta_oromo_v0.1.2_n10000.jsonl"
)

DEFAULT_OUTPUT = Path(
    "tokenizer/training/"
    "afriberta_oromo_v0.1.2_tokenizer_train.txt"
)

DEFAULT_MANIFEST = Path(
    "tokenizer/training/"
    "afriberta_oromo_v0.1.2_tokenizer_train.manifest.json"
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


def load_eval_record_ids(path: Path) -> set[str]:
    record_ids: set[str] = set()

    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            line = line.strip()

            if not line:
                continue

            record = json.loads(line)

            record_id = record.get("record_id")

            if not isinstance(record_id, str) or not record_id:
                raise ValueError(
                    f"Missing/invalid record_id in evaluation sample "
                    f"at line {line_number}"
                )

            if record_id in record_ids:
                raise ValueError(
                    f"Duplicate evaluation record_id: {record_id}"
                )

            record_ids.add(record_id)

    return record_ids


def source_record_id(
    record: dict[str, Any],
    line_number: int,
) -> str | None:
    """
    Resolve the stable record ID used by the frozen evaluation sample.

    Prefer an explicit record_id if the processed source contains one.
    Otherwise reconstruct it from source_id/source_line, matching the
    evaluation sample format.
    """

    explicit = record.get("record_id")

    if isinstance(explicit, str) and explicit:
        return explicit

    source_id = record.get("source_id")
    source_line = record.get("source_line")

    if (
        isinstance(source_id, str)
        and source_id
        and isinstance(source_line, int)
    ):
        return f"{source_id}:line:{source_line}"

    # The current AfriBERTa Oromo dataset may rely on physical source
    # line numbering. Keep this fallback explicit and deterministic.
    if isinstance(source_id, str) and source_id:
        return f"{source_id}:line:{line_number}"

    return None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Prepare a leakage-safe Afaan Oromoo tokenizer training corpus."
        )
    )

    parser.add_argument(
        "--source",
        type=Path,
        default=DEFAULT_SOURCE,
        help="Processed JSONL corpus.",
    )

    parser.add_argument(
        "--eval-sample",
        type=Path,
        default=DEFAULT_EVAL_SAMPLE,
        help="Frozen tokenizer evaluation sample.",
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Output plain-text tokenizer training corpus.",
    )

    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_MANIFEST,
        help="Output reproducibility manifest.",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if not args.source.exists():
        raise FileNotFoundError(args.source)

    if not args.eval_sample.exists():
        raise FileNotFoundError(args.eval_sample)

    eval_record_ids = load_eval_record_ids(args.eval_sample)

    print("=== Preparing Afaan Oromoo Tokenizer Training Corpus ===")
    print(f"Source: {args.source}")
    print(f"Evaluation sample: {args.eval_sample}")
    print(f"Frozen evaluation records: {len(eval_record_ids):,}")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.parent.mkdir(parents=True, exist_ok=True)

    source_records = 0
    usable_records = 0
    excluded_eval_records = 0
    empty_records = 0
    unresolved_record_ids = 0

    training_record_ids: set[str] = set()

    with (
        args.source.open("r", encoding="utf-8") as source_handle,
        args.output.open("w", encoding="utf-8", newline="\n") as output_handle,
    ):
        for line_number, line in enumerate(source_handle, start=1):
            line = line.strip()

            if not line:
                continue

            source_records += 1

            record = json.loads(line)

            text = record.get("text", "")

            if not isinstance(text, str) or not text.strip():
                empty_records += 1
                continue

            record_id = source_record_id(record, line_number)

            if record_id is None:
                unresolved_record_ids += 1
                raise RuntimeError(
                    "Could not resolve stable record_id for "
                    f"source line {line_number}. Refusing to continue "
                    "because evaluation leakage cannot be ruled out."
                )

            if record_id in eval_record_ids:
                excluded_eval_records += 1
                continue

            if record_id in training_record_ids:
                raise RuntimeError(
                    f"Duplicate training record_id encountered: {record_id}"
                )

            training_record_ids.add(record_id)

            # Preserve the processed text exactly except for outer
            # whitespace and the newline required by the training file.
            output_handle.write(text.strip())
            output_handle.write("\n")

            usable_records += 1

    leaked_ids = training_record_ids.intersection(eval_record_ids)

    if leaked_ids:
        examples = sorted(leaked_ids)[:10]
        raise RuntimeError(
            "Evaluation leakage detected. Example record IDs: "
            + ", ".join(examples)
        )

    if excluded_eval_records != len(eval_record_ids):
        missing_count = len(eval_record_ids) - excluded_eval_records

        raise RuntimeError(
            "Not every frozen evaluation record was found and excluded. "
            f"Expected {len(eval_record_ids):,}; "
            f"excluded {excluded_eval_records:,}; "
            f"missing {missing_count:,}. "
            "Refusing to produce a trusted training corpus."
        )

    output_sha256 = sha256_file(args.output)
    source_sha256 = sha256_file(args.source)
    eval_sha256 = sha256_file(args.eval_sample)

    manifest = {
        "format_version": 1,
        "purpose": "Afaan Oromoo tokenizer training corpus",
        "source": {
            "path": str(args.source),
            "sha256": source_sha256,
            "records": source_records,
        },
        "evaluation_holdout": {
            "path": str(args.eval_sample),
            "sha256": eval_sha256,
            "records": len(eval_record_ids),
            "excluded_records": excluded_eval_records,
        },
        "training_corpus": {
            "path": str(args.output),
            "sha256": output_sha256,
            "records": usable_records,
        },
        "filtering": {
            "empty_records": empty_records,
            "unresolved_record_ids": unresolved_record_ids,
            "evaluation_leakage_records": len(leaked_ids),
        },
    }

    args.manifest.write_text(
        json.dumps(
            manifest,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    print()
    print("=== Tokenizer Training Corpus ===")
    print(f"Source records: {source_records:,}")
    print(f"Training records: {usable_records:,}")
    print(f"Evaluation records excluded: {excluded_eval_records:,}")
    print(f"Empty records skipped: {empty_records:,}")
    print(f"Unresolved record IDs: {unresolved_record_ids:,}")
    print(f"Evaluation leakage: {len(leaked_ids):,}")
    print()
    print(f"Training corpus: {args.output}")
    print(f"Training SHA-256: {output_sha256}")
    print(f"Manifest: {args.manifest}")
    print()
    print("PASS: leakage-safe tokenizer training corpus prepared.")


if __name__ == "__main__":
    main()