from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from transformers import AutoTokenizer


DEFAULT_CORPUS = Path(
    "tokenizer/evaluation/samples/"
    "afriberta_oromo_v0.1.2_n10000.jsonl"
)

WORD_PATTERN = re.compile(r"\S+")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Audit tokenizer offset alignment against "
            "whitespace-delimited words."
        )
    )

    parser.add_argument(
        "--tokenizer",
        required=True,
        help="Hugging Face tokenizer identifier.",
    )

    parser.add_argument(
        "--corpus",
        type=Path,
        default=DEFAULT_CORPUS,
        help="Frozen tokenizer evaluation JSONL corpus.",
    )

    return parser.parse_args()


def load_records(path: Path) -> list[dict]:
    records: list[dict] = []

    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            line = line.strip()

            if not line:
                continue

            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"Invalid JSON at line {line_number}: {path}"
                ) from exc

            text = record.get("text")

            if isinstance(text, str) and text.strip():
                records.append(record)

    return records


def find_unaligned_words(
    text: str,
    offsets: list[tuple[int, int]],
) -> list[dict]:
    usable_offsets = [
        (start, end)
        for start, end in offsets
        if end > start
    ]

    problems: list[dict] = []

    for match in WORD_PATTERN.finditer(text):
        word_start, word_end = match.span()

        overlapping = [
            (start, end)
            for start, end in usable_offsets
            if start < word_end and end > word_start
        ]

        if not overlapping:
            problems.append(
                {
                    "word": match.group(),
                    "word_start": word_start,
                    "word_end": word_end,
                    "reason": "no_overlapping_token",
                    "offsets": [],
                }
            )
            continue

        covered_positions: set[int] = set()

        for start, end in overlapping:
            clipped_start = max(start, word_start)
            clipped_end = min(end, word_end)

            covered_positions.update(
                range(clipped_start, clipped_end)
            )

        expected_positions = set(
            range(word_start, word_end)
        )

        missing_positions = sorted(
            expected_positions - covered_positions
        )

        if missing_positions:
            problems.append(
                {
                    "word": match.group(),
                    "word_start": word_start,
                    "word_end": word_end,
                    "reason": "partial_offset_coverage",
                    "offsets": overlapping,
                    "missing_positions": missing_positions,
                    "missing_characters": [
                        text[position]
                        for position in missing_positions
                    ],
                }
            )

    return problems


def main() -> None:
    args = parse_args()

    if not args.corpus.exists():
        raise FileNotFoundError(args.corpus)

    records = load_records(args.corpus)

    tokenizer = AutoTokenizer.from_pretrained(
        args.tokenizer,
        use_fast=True,
    )

    if not tokenizer.is_fast:
        raise RuntimeError(
            "Alignment audit requires a fast tokenizer."
        )

    total_words = 0
    problem_words = 0
    problem_records = 0

    print("\n=== Tokenizer Alignment Audit ===")
    print(f"Tokenizer: {args.tokenizer}")
    print(f"Corpus: {args.corpus}")
    print(f"Records: {len(records):,}")

    for index, record in enumerate(records, start=1):
        text = record["text"]

        encoding = tokenizer(
            text,
            add_special_tokens=False,
            return_offsets_mapping=True,
            truncation=False,
        )

        offsets = encoding["offset_mapping"]

        words = list(WORD_PATTERN.finditer(text))
        total_words += len(words)

        problems = find_unaligned_words(
            text,
            offsets,
        )

        if not problems:
            continue

        problem_records += 1
        problem_words += len(problems)

        print("\n----------------------------------------")
        print(f"Sample index: {index}")
        print(f"Record ID: {record.get('record_id')}")
        print(f"Text: {text}")

        tokens = tokenizer.convert_ids_to_tokens(
            encoding["input_ids"]
        )

        print("\nTokens + offsets:")

        for token, offset in zip(tokens, offsets):
            print(
                f"  {token!r:25} {tuple(offset)}"
            )

        print("\nProblem words:")

        for problem in problems:
            print(
                json.dumps(
                    problem,
                    ensure_ascii=False,
                    indent=2,
                )
            )

    print("\n=== Alignment Summary ===")
    print(f"Total whitespace words: {total_words:,}")
    print(f"Problem records: {problem_records:,}")
    print(f"Problem words: {problem_words:,}")

    if total_words:
        print(
            "Problem-word rate: "
            f"{problem_words / total_words:.8f}"
        )


if __name__ == "__main__":
    main()