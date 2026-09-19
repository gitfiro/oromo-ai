from __future__ import annotations

import argparse
import json
import unicodedata
from collections import Counter
from pathlib import Path

import sentencepiece as spm


DEFAULT_SAMPLE = Path(
    "tokenizer/evaluation/samples/"
    "afriberta_oromo_v0.1.2_n10000.jsonl"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit unknown tokens from a SentencePiece tokenizer."
    )

    parser.add_argument(
        "--model",
        type=Path,
        required=True,
    )

    parser.add_argument(
        "--sample",
        type=Path,
        default=DEFAULT_SAMPLE,
    )

    return parser.parse_args()


def describe_character(char: str) -> str:
    codepoint = f"U+{ord(char):04X}"

    try:
        name = unicodedata.name(char)
    except ValueError:
        name = "UNNAMED"

    category = unicodedata.category(char)

    return (
        f"{repr(char)} "
        f"{codepoint} "
        f"{name} "
        f"[{category}]"
    )


def main() -> None:
    args = parse_args()

    if not args.model.exists():
        raise FileNotFoundError(args.model)

    if not args.sample.exists():
        raise FileNotFoundError(args.sample)

    sp = spm.SentencePieceProcessor(
        model_file=str(args.model)
    )

    unknown_id = sp.unk_id()

    total_unknown_tokens = 0
    affected_records = 0

    unknown_surfaces: Counter[str] = Counter()
    unknown_characters: Counter[str] = Counter()

    print("=== SentencePiece Unknown-Token Audit ===")
    print(f"Model: {args.model}")
    print(f"Sample: {args.sample}")
    print()

    with args.sample.open(
        "r",
        encoding="utf-8",
    ) as handle:
        for sample_index, line in enumerate(
            handle,
            start=1,
        ):
            record = json.loads(line)
            text = record["text"]

            proto = sp.encode(
                text,
                return_type="proto",
            )

            record_unknowns = []

            for piece in proto.pieces:
                if piece.id != unknown_id:
                    continue

                surface = piece.surface

                total_unknown_tokens += 1
                unknown_surfaces[surface] += 1

                for char in surface:
                    unknown_characters[char] += 1

                record_unknowns.append(
                    {
                        "surface": surface,
                        "begin": piece.begin,
                        "end": piece.end,
                    }
                )

            if not record_unknowns:
                continue

            affected_records += 1

            print("-" * 72)
            print(f"Sample index: {sample_index}")
            print(
                f"Record ID: "
                f"{record.get('record_id')}"
            )
            print(f"Text: {text}")
            print("Unknown spans:")

            for item in record_unknowns:
                print(
                    f"  {item['begin']}:"
                    f"{item['end']} "
                    f"{item['surface']!r}"
                )

                for char in item["surface"]:
                    print(
                        "    "
                        + describe_character(char)
                    )

    print()
    print("=== Unknown Summary ===")
    print(
        f"Unknown tokens: "
        f"{total_unknown_tokens:,}"
    )
    print(
        f"Affected records: "
        f"{affected_records:,}"
    )

    print()
    print("Unknown surfaces:")

    for surface, count in (
        unknown_surfaces.most_common()
    ):
        print(
            f"  {surface!r}: {count}"
        )

    print()
    print("Unknown characters:")

    for char, count in (
        unknown_characters.most_common()
    ):
        print(
            f"  {describe_character(char)}: "
            f"{count}"
        )


if __name__ == "__main__":
    main()