from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import sentencepiece as spm


DEFAULT_INPUT = Path(
    "tokenizer/training/"
    "afriberta_oromo_v0.1.2_tokenizer_train.txt"
)

DEFAULT_MODEL = Path(
    "tokenizer/training/candidates/"
    "oromo_unigram_48k_byte/tokenizer.model"
)

DEFAULT_OUTPUT = Path(
    "tokenizer/augmentation/candidates/"
    "oromo_subword_candidates.jsonl"
)

DEFAULT_MANIFEST = Path(
    "tokenizer/augmentation/candidates/"
    "oromo_subword_candidates.manifest.json"
)

# Phase 4B2 intentionally tests internal Oromo subword augmentation.
# SentencePiece word-boundary pieces (those beginning with ▁) are excluded
# because Hugging Face AddedToken cannot reproduce SentencePiece boundary
# semantics portably across unrelated tokenizer families.
LATIN_SUBWORD = re.compile(
    r"[A-Za-z]+(?:['’ʼ-][A-Za-z]+)*"
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(
            lambda: handle.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build leakage-safe internal Afaan Oromoo "
            "subword candidates from the trained Oromo "
            "SentencePiece reference tokenizer."
        )
    )

    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
    )

    parser.add_argument(
        "--sentencepiece-model",
        type=Path,
        default=DEFAULT_MODEL,
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
    )

    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_MANIFEST,
    )

    parser.add_argument(
        "--min-frequency",
        type=int,
        default=20,
    )

    parser.add_argument(
        "--min-length",
        type=int,
        default=2,
    )

    parser.add_argument(
        "--max-length",
        type=int,
        default=16,
    )

    return parser.parse_args()


def is_candidate(
    piece: str,
    *,
    min_length: int,
    max_length: int,
) -> bool:
    if not piece:
        return False

    # Exclude SentencePiece word-boundary/prefix pieces. Phase 4B1 already
    # measured whole-word additions; 4B2 isolates reusable internal pieces.
    if piece.startswith("▁"):
        return False

    # Exclude byte-fallback pieces such as <0xAB>, specials and controls.
    if piece.startswith("<") and piece.endswith(">"):
        return False

    if not (
        min_length
        <= len(piece)
        <= max_length
    ):
        return False

    return (
        LATIN_SUBWORD.fullmatch(piece)
        is not None
    )


def main() -> None:
    args = parse_args()

    if not args.input.is_file():
        raise FileNotFoundError(args.input)

    if not args.sentencepiece_model.is_file():
        raise FileNotFoundError(
            args.sentencepiece_model
        )

    if args.min_frequency < 1:
        raise ValueError(
            "--min-frequency must be >= 1"
        )

    if args.min_length < 2:
        raise ValueError(
            "--min-length must be >= 2"
        )

    if args.max_length < args.min_length:
        raise ValueError(
            "--max-length must be >= --min-length"
        )

    sp = spm.SentencePieceProcessor(
        model_file=str(
            args.sentencepiece_model
        )
    )

    eligible_ids: dict[int, str] = {}

    for piece_id in range(
        sp.get_piece_size()
    ):
        piece = sp.id_to_piece(piece_id)

        if is_candidate(
            piece,
            min_length=args.min_length,
            max_length=args.max_length,
        ):
            eligible_ids[piece_id] = piece

    counts: Counter[int] = Counter()

    lines = 0
    reference_pieces = 0
    eligible_occurrences = 0

    with args.input.open(
        "r",
        encoding="utf-8",
    ) as handle:
        for line in handle:
            lines += 1

            text = line.strip()

            if not text:
                continue

            piece_ids = sp.encode(
                text,
                out_type=int,
            )

            reference_pieces += len(
                piece_ids
            )

            for piece_id in piece_ids:
                if piece_id not in eligible_ids:
                    continue

                counts[piece_id] += 1
                eligible_occurrences += 1

            if lines % 50_000 == 0:
                print(
                    f"Processed {lines:,} "
                    "training records...",
                    flush=True,
                )

    candidates = []

    for piece_id, frequency in (
        counts.items()
    ):
        if frequency < args.min_frequency:
            continue

        piece = eligible_ids[piece_id]

        candidates.append(
            {
                "piece": piece,
                "reference_piece_id": (
                    piece_id
                ),
                "frequency": frequency,
                "characters": len(piece),
                "candidate_type": (
                    "internal_subword"
                ),
            }
        )

    candidates.sort(
        key=lambda item: (
            -item["frequency"],
            -item["characters"],
            item["piece"],
        )
    )

    args.output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with args.output.open(
        "w",
        encoding="utf-8",
        newline="\n",
    ) as handle:
        for rank, item in enumerate(
            candidates,
            start=1,
        ):
            record = {
                "rank_by_frequency": rank,
                **item,
            }

            handle.write(
                json.dumps(
                    record,
                    ensure_ascii=False,
                    sort_keys=True,
                )
                + "\n"
            )

    manifest = {
        "format_version": 1,
        "created_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "phase": "4B2",
        "purpose": (
            "Leakage-safe internal Oromo "
            "subword augmentation candidate pool."
        ),
        "input": {
            "path": str(args.input),
            "sha256": sha256_file(
                args.input
            ),
            "records": lines,
        },
        "reference_tokenizer": {
            "path": str(
                args.sentencepiece_model
            ),
            "sha256": sha256_file(
                args.sentencepiece_model
            ),
            "piece_count": (
                sp.get_piece_size()
            ),
        },
        "policy": {
            "candidate_type":
                "internal_subword",
            "sentencepiece_boundary_pieces_excluded":
                True,
            "byte_fallback_pieces_excluded":
                True,
            "special_control_pieces_excluded":
                True,
            "latin_qubee_like_only":
                True,
            "min_frequency":
                args.min_frequency,
            "min_length":
                args.min_length,
            "max_length":
                args.max_length,
            "evaluation_data_used":
                False,
        },
        "statistics": {
            "reference_pieces_seen":
                reference_pieces,
            "eligible_piece_types":
                len(eligible_ids),
            "eligible_piece_occurrences":
                eligible_occurrences,
            "candidate_types_after_frequency_filter":
                len(candidates),
        },
        "output": {
            "path": str(args.output),
            "sha256": sha256_file(
                args.output
            ),
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
    print(
        "=== Oromo Phase 4B2 Subword Candidate Pool ==="
    )
    print(
        "Training records:",
        f"{lines:,}",
    )
    print(
        "Reference pieces seen:",
        f"{reference_pieces:,}",
    )
    print(
        "Eligible internal piece types:",
        f"{len(eligible_ids):,}",
    )
    print(
        "Candidate types:",
        f"{len(candidates):,}",
    )
    print(
        "Candidate SHA-256:",
        sha256_file(args.output),
    )
    print(
        "Manifest:",
        args.manifest,
    )

    print()
    print("Top 40 internal subwords:")

    for item in candidates[:40]:
        print(
            f"{item['rank_by_frequency']:>4} "
            f"{item['frequency']:>9,} "
            f"{item['characters']:>2} "
            f"{item['piece']}"
        )


if __name__ == "__main__":
    main()
