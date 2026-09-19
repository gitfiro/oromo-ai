from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


DEFAULT_INPUT = Path(
    "tokenizer/training/"
    "afriberta_oromo_v0.1.2_tokenizer_train.txt"
)

DEFAULT_OUTPUT = Path(
    "tokenizer/augmentation/candidates/"
    "oromo_word_candidates.jsonl"
)

DEFAULT_MANIFEST = Path(
    "tokenizer/augmentation/candidates/"
    "oromo_word_candidates.manifest.json"
)

# Standard modern Afaan Oromoo uses Latin/Qubee characters.
#
# This feasibility experiment intentionally excludes:
# - digits
# - CJK
# - Lao
# - Hangul
# - emoji
# - URLs
# - arbitrary symbols
#
# Apostrophe variants and internal hyphens are preserved.
LEXICAL_PATTERN = re.compile(
    r"[A-Za-z]+(?:['’ʼ-][A-Za-z]+)*"
)

EDGE_STRIP_CHARS = (
    " \t\r\n"
    ".,;:!?()[]{}<>"
    "\"“”„«»"
    "/\\|"
    "*+=~`"
    "…"
)

APOSTROPHES = {
    "'",
    "’",
    "ʼ",
}


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
            "Build a leakage-safe lexical candidate pool "
            "for Afaan Oromoo tokenizer augmentation."
        )
    )

    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help=(
            "Leakage-safe tokenizer training corpus."
        ),
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Candidate JSONL output path.",
    )

    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_MANIFEST,
        help="Candidate-pool manifest output path.",
    )

    parser.add_argument(
        "--min-frequency",
        type=int,
        default=2,
        help=(
            "Minimum exact-form frequency required "
            "for a lexical candidate."
        ),
    )

    parser.add_argument(
        "--min-length",
        type=int,
        default=2,
        help="Minimum candidate character length.",
    )

    parser.add_argument(
        "--max-length",
        type=int,
        default=64,
        help="Maximum candidate character length.",
    )

    return parser.parse_args()


def normalize_surface_token(
    raw_token: str,
) -> str | None:
    """
    Convert one whitespace-delimited corpus token into
    a conservative lexical candidate.

    This does NOT lowercase, stem, lemmatize, or otherwise
    rewrite the word.
    """

    if not raw_token:
        return None

    # Avoid turning hashtags, handles, and URLs into candidates.
    if raw_token.startswith(("#", "@")):
        return None

    lowered = raw_token.lower()

    if (
        "http://" in lowered
        or "https://" in lowered
        or "www." in lowered
    ):
        return None

    token = raw_token.strip(
        EDGE_STRIP_CHARS
    )

    if not token:
        return None

    if not LEXICAL_PATTERN.fullmatch(
        token
    ):
        return None

    return token


def main() -> None:
    args = parse_args()

    if not args.input.exists():
        raise FileNotFoundError(
            args.input
        )

    if args.min_frequency < 1:
        raise ValueError(
            "--min-frequency must be >= 1"
        )

    if args.min_length < 1:
        raise ValueError(
            "--min-length must be >= 1"
        )

    if args.max_length < args.min_length:
        raise ValueError(
            "--max-length must be >= "
            "--min-length"
        )

    counts: Counter[str] = Counter()

    line_count = 0
    whitespace_token_count = 0
    accepted_occurrences = 0

    with args.input.open(
        "r",
        encoding="utf-8",
    ) as handle:
        for line in handle:
            line_count += 1

            for raw_token in line.split():
                whitespace_token_count += 1

                token = normalize_surface_token(
                    raw_token
                )

                if token is None:
                    continue

                if not (
                    args.min_length
                    <= len(token)
                    <= args.max_length
                ):
                    continue

                counts[token] += 1
                accepted_occurrences += 1

    candidates = [
        (word, frequency)
        for word, frequency in counts.items()
        if frequency >= args.min_frequency
    ]

    candidates.sort(
        key=lambda item: (
            -item[1],
            item[0],
        )
    )

    args.output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with args.output.open(
        "w",
        encoding="utf-8",
    ) as handle:
        for rank, (
            word,
            frequency,
        ) in enumerate(
            candidates,
            start=1,
        ):
            record = {
                "rank_by_frequency": rank,
                "word": word,
                "frequency": frequency,
                "characters": len(word),
            }

            handle.write(
                json.dumps(
                    record,
                    ensure_ascii=False,
                    sort_keys=True,
                )
                + "\n"
            )

    input_sha256 = sha256_file(
        args.input
    )

    output_sha256 = sha256_file(
        args.output
    )

    manifest = {
        "format_version": 1,
        "created_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "purpose": (
            "Leakage-safe lexical candidate pool "
            "for tokenizer augmentation research."
        ),
        "input": {
            "path": str(args.input),
            "sha256": input_sha256,
            "lines": line_count,
        },
        "filters": {
            "min_frequency": (
                args.min_frequency
            ),
            "min_length": (
                args.min_length
            ),
            "max_length": (
                args.max_length
            ),
            "latin_ascii_letters_only": True,
            "internal_apostrophes": sorted(
                APOSTROPHES
            ),
            "internal_hyphen": True,
            "lowercased": False,
            "lemmatized": False,
        },
        "statistics": {
            "whitespace_tokens_seen": (
                whitespace_token_count
            ),
            "accepted_lexical_occurrences": (
                accepted_occurrences
            ),
            "unique_lexical_forms": (
                len(counts)
            ),
            "candidate_forms": (
                len(candidates)
            ),
        },
        "output": {
            "path": str(args.output),
            "sha256": output_sha256,
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

    print(
        "=== Oromo Augmentation Candidate Pool ==="
    )
    print(
        f"Training corpus: {args.input}"
    )
    print(
        f"Training SHA-256: "
        f"{input_sha256}"
    )
    print(
        f"Training lines: "
        f"{line_count:,}"
    )
    print(
        f"Whitespace tokens seen: "
        f"{whitespace_token_count:,}"
    )
    print(
        f"Accepted lexical occurrences: "
        f"{accepted_occurrences:,}"
    )
    print(
        f"Unique lexical forms: "
        f"{len(counts):,}"
    )
    print(
        f"Candidates (freq >= "
        f"{args.min_frequency}): "
        f"{len(candidates):,}"
    )
    print(
        f"Candidate file: {args.output}"
    )
    print(
        f"Candidate SHA-256: "
        f"{output_sha256}"
    )
    print(
        f"Manifest: {args.manifest}"
    )

    print()
    print("Top 30 candidates:")

    for rank, (
        word,
        frequency,
    ) in enumerate(
        candidates[:30],
        start=1,
    ):
        print(
            f"{rank:>4} "
            f"{frequency:>8,} "
            f"{word}"
        )


if __name__ == "__main__":
    main()