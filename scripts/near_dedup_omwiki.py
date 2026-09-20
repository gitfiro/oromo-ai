from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from oromo_ai.data.near_deduplicate import (
    jaccard_similarity,
    shingle_hashes,
)


DEFAULT_OMWIKI = Path(
    "data/interim/wikimedia-omwiki/quality/"
    "articles.accepted.exact-new.jsonl"
)

DEFAULT_BASELINE = Path(
    "data/processed/afriberta_oromo_v0.1.2/"
    "train.jsonl"
)

DEFAULT_OUTPUT_DIR = Path(
    "data/interim/wikimedia-omwiki/near_dedup"
)

SHINGLE_SIZE = 5
THRESHOLD = 0.85


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Near-deduplicate exact-new omwiki records "
            "against themselves and AfriBERTa v0.1.2."
        )
    )

    parser.add_argument(
        "--omwiki",
        type=Path,
        default=DEFAULT_OMWIKI,
    )

    parser.add_argument(
        "--baseline",
        type=Path,
        default=DEFAULT_BASELINE,
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
    )

    parser.add_argument(
        "--threshold",
        type=float,
        default=THRESHOLD,
    )

    parser.add_argument(
        "--shingle-size",
        type=int,
        default=SHINGLE_SIZE,
    )

    return parser.parse_args()


def write_jsonl(
    handle: Any,
    value: dict[str, Any],
) -> None:
    handle.write(
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
        )
        + "\n"
    )


def load_jsonl(
    path: Path,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    with path.open(
        encoding="utf-8"
    ) as handle:
        for line in handle:
            rows.append(
                json.loads(line)
            )

    return rows


def build_candidate_index(
    shingle_sets: list[set[int]],
) -> dict[int, list[int]]:
    """
    Map each shingle hash to candidate record indices.
    """

    index: dict[int, list[int]] = defaultdict(list)

    for record_index, shingles in enumerate(
        shingle_sets
    ):
        for shingle in shingles:
            index[shingle].append(
                record_index
            )

    return dict(index)


def candidate_indices(
    shingles: set[int],
    index: dict[int, list[int]],
) -> set[int]:
    """
    Return records sharing at least one shingle.
    """

    candidates: set[int] = set()

    for shingle in shingles:
        matches = index.get(shingle)

        if matches:
            candidates.update(matches)

    return candidates


def within_source_near_dedup(
    rows: list[dict[str, Any]],
    *,
    threshold: float,
    shingle_size: int,
) -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
]:
    """
    Near-deduplicate omwiki against itself.

    Deterministic policy:
    first record in source order wins.
    """

    kept_rows: list[dict[str, Any]] = []
    kept_shingles: list[set[int]] = []

    index: dict[int, list[int]] = defaultdict(list)

    duplicates: list[dict[str, Any]] = []

    for row in rows:
        text = row["text"]

        shingles = shingle_hashes(
            text,
            shingle_size=shingle_size,
        )

        candidates: set[int] = set()

        for shingle in shingles:
            candidates.update(
                index.get(shingle, [])
            )

        best_match: int | None = None
        best_similarity = 0.0

        for candidate_index in sorted(candidates):
            score = jaccard_similarity(
                shingles,
                kept_shingles[candidate_index],
            )

            if score > best_similarity:
                best_similarity = score
                best_match = candidate_index

        if (
            best_match is not None
            and best_similarity >= threshold
        ):
            matched = kept_rows[best_match]

            duplicates.append(
                {
                    "record_id": row["record_id"],
                    "title": row.get("title", ""),
                    "matched_record_id": (
                        matched["record_id"]
                    ),
                    "matched_title": matched.get(
                        "title",
                        "",
                    ),
                    "similarity": round(
                        best_similarity,
                        6,
                    ),
                    "threshold": threshold,
                    "shingle_size": shingle_size,
                    "reason": (
                        "near_duplicate_within_omwiki"
                    ),
                }
            )

            continue

        new_index = len(kept_rows)

        kept_rows.append(row)
        kept_shingles.append(shingles)

        for shingle in shingles:
            index[shingle].append(
                new_index
            )

    return kept_rows, duplicates


def cross_source_near_dedup(
    omwiki_rows: list[dict[str, Any]],
    baseline_path: Path,
    *,
    threshold: float,
    shingle_size: int,
) -> tuple[
    set[int],
    dict[int, dict[str, Any]],
    int,
    int,
]:
    """
    Find omwiki near duplicates in the frozen baseline.

    The omwiki corpus is indexed because it is much smaller.
    AfriBERTa is streamed read-only.
    """

    omwiki_shingles = [
        shingle_hashes(
            row["text"],
            shingle_size=shingle_size,
        )
        for row in omwiki_rows
    ]

    index = build_candidate_index(
        omwiki_shingles
    )

    duplicate_indices: set[int] = set()

    best_matches: dict[
        int,
        dict[str, Any],
    ] = {}

    baseline_records = 0
    candidate_comparisons = 0

    with baseline_path.open(
        encoding="utf-8"
    ) as handle:
        for baseline_line, line in enumerate(
            handle,
            start=1,
        ):
            baseline_row = json.loads(line)
            baseline_text = baseline_row["text"]

            baseline_records += 1

            baseline_shingles = shingle_hashes(
                baseline_text,
                shingle_size=shingle_size,
            )

            candidates = candidate_indices(
                baseline_shingles,
                index,
            )

            for omwiki_index in candidates:
                candidate_comparisons += 1

                score = jaccard_similarity(
                    baseline_shingles,
                    omwiki_shingles[
                        omwiki_index
                    ],
                )

                if score < threshold:
                    continue

                current = best_matches.get(
                    omwiki_index
                )

                if (
                    current is None
                    or score
                    > current["similarity"]
                ):
                    best_matches[
                        omwiki_index
                    ] = {
                        "similarity": score,
                        "baseline_line": (
                            baseline_line
                        ),
                        "baseline_record_id": (
                            baseline_row.get(
                                "record_id",
                                "",
                            )
                        ),
                        "baseline_title": (
                            baseline_row.get(
                                "title",
                                "",
                            )
                        ),
                    }

                duplicate_indices.add(
                    omwiki_index
                )

    return (
        duplicate_indices,
        best_matches,
        baseline_records,
        candidate_comparisons,
    )


def main() -> int:
    args = parse_args()

    if not 0.0 <= args.threshold <= 1.0:
        raise ValueError(
            "threshold must be between 0 and 1"
        )

    if args.shingle_size < 1:
        raise ValueError(
            "shingle-size must be >= 1"
        )

    if not args.omwiki.is_file():
        raise FileNotFoundError(
            args.omwiki
        )

    if not args.baseline.is_file():
        raise FileNotFoundError(
            args.baseline
        )

    args.output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    final_path = (
        args.output_dir
        / "articles.near-dedup-new.jsonl"
    )

    within_path = (
        args.output_dir
        / "articles.near-duplicates-within.jsonl"
    )

    cross_path = (
        args.output_dir
        / "articles.near-duplicates-cross.jsonl"
    )

    # --------------------------------------------------------------
    # Load exact-net-new omwiki candidates.
    # --------------------------------------------------------------

    original_rows = load_jsonl(
        args.omwiki
    )

    original_chars = sum(
        len(row["text"])
        for row in original_rows
    )

    # --------------------------------------------------------------
    # Within-source near dedup.
    # --------------------------------------------------------------

    (
        within_unique,
        within_duplicates,
    ) = within_source_near_dedup(
        original_rows,
        threshold=args.threshold,
        shingle_size=args.shingle_size,
    )

    with within_path.open(
        "w",
        encoding="utf-8",
        newline="\n",
    ) as handle:
        for item in within_duplicates:
            write_jsonl(
                handle,
                item,
            )

    # --------------------------------------------------------------
    # Cross-source near dedup.
    # --------------------------------------------------------------

    (
        cross_duplicate_indices,
        best_matches,
        baseline_records,
        candidate_comparisons,
    ) = cross_source_near_dedup(
        within_unique,
        args.baseline,
        threshold=args.threshold,
        shingle_size=args.shingle_size,
    )

    with cross_path.open(
        "w",
        encoding="utf-8",
        newline="\n",
    ) as handle:
        for record_index in sorted(
            cross_duplicate_indices
        ):
            row = within_unique[
                record_index
            ]

            match = best_matches[
                record_index
            ]

            write_jsonl(
                handle,
                {
                    "record_id": row["record_id"],
                    "title": row.get(
                        "title",
                        "",
                    ),
                    "matched_corpus": (
                        "afriberta_oromo_v0.1.2"
                    ),
                    "matched_record_id": (
                        match[
                            "baseline_record_id"
                        ]
                    ),
                    "matched_title": (
                        match["baseline_title"]
                    ),
                    "matched_baseline_line": (
                        match["baseline_line"]
                    ),
                    "similarity": round(
                        match["similarity"],
                        6,
                    ),
                    "threshold": (
                        args.threshold
                    ),
                    "shingle_size": (
                        args.shingle_size
                    ),
                    "reason": (
                        "near_duplicate_cross_source"
                    ),
                },
            )

    # --------------------------------------------------------------
    # Write final net-new omwiki.
    # --------------------------------------------------------------

    final_records = 0
    final_chars = 0

    with final_path.open(
        "w",
        encoding="utf-8",
        newline="\n",
    ) as handle:
        for record_index, row in enumerate(
            within_unique
        ):
            if (
                record_index
                in cross_duplicate_indices
            ):
                continue

            metadata = dict(
                row.get(
                    "metadata",
                    {}
                )
            )

            metadata.update(
                {
                    "near_dedup_method": (
                        "word_shingle_jaccard"
                    ),
                    "near_dedup_threshold": (
                        args.threshold
                    ),
                    "near_dedup_shingle_size": (
                        args.shingle_size
                    ),
                    "near_dedup_baseline": (
                        "afriberta_oromo_v0.1.2"
                    ),
                    "near_duplicate": False,
                }
            )

            output_row = dict(row)
            output_row["metadata"] = metadata

            write_jsonl(
                handle,
                output_row,
            )

            final_records += 1
            final_chars += len(
                row["text"]
            )

    # --------------------------------------------------------------
    # Report.
    # --------------------------------------------------------------

    print(
        "=== omwiki Near-Dedup Report ==="
    )

    print(
        "threshold:",
        args.threshold,
    )

    print(
        "shingle_size:",
        args.shingle_size,
    )

    print()
    print(
        "input_exact_new_records:",
        len(original_rows),
    )

    print(
        "input_exact_new_chars:",
        original_chars,
    )

    print()
    print(
        "within_source_near_duplicates:",
        len(within_duplicates),
    )

    print(
        "after_within_source:",
        len(within_unique),
    )

    print()
    print(
        "baseline_records_scanned:",
        baseline_records,
    )

    print(
        "candidate_comparisons:",
        candidate_comparisons,
    )

    print(
        "cross_source_near_duplicates:",
        len(cross_duplicate_indices),
    )

    print()
    print(
        "final_net_new_records:",
        final_records,
    )

    print(
        "final_net_new_chars:",
        final_chars,
    )

    retention = (
        final_records
        / len(original_rows)
        * 100
        if original_rows
        else 0
    )

    print(
        "near_dedup_record_retention_percent:",
        round(
            retention,
            2,
        ),
    )

    print()
    print(
        "final_output:",
        final_path,
    )

    print(
        "within_duplicate_ledger:",
        within_path,
    )

    print(
        "cross_duplicate_ledger:",
        cross_path,
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
