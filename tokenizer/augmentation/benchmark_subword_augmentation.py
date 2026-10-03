from __future__ import annotations

import argparse
import copy
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import tokenizers
import transformers
from transformers import (
    AddedToken,
    AutoTokenizer,
)

from oromo_ai.tokenizer.metrics import (
    calculate_metrics,
    calculate_word_fragmentation,
)


DEFAULT_CANDIDATES = Path(
    "tokenizer/augmentation/candidates/"
    "oromo_subword_candidates.jsonl"
)

DEFAULT_EVAL_CORPUS = Path(
    "tokenizer/evaluation/samples/"
    "afriberta_oromo_v0.1.2_n10000.jsonl"
)

DEFAULT_RESULTS_DIR = Path(
    "tokenizer/augmentation/results_subword"
)

DEFAULT_BUDGETS = (
    2000,
    4000,
    8000,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Benchmark Phase 4B2 internal Oromo "
            "subword vocabulary augmentation."
        )
    )

    parser.add_argument(
        "--tokenizer",
        required=True,
    )

    parser.add_argument(
        "--candidates",
        type=Path,
        default=DEFAULT_CANDIDATES,
    )

    parser.add_argument(
        "--eval-corpus",
        type=Path,
        default=DEFAULT_EVAL_CORPUS,
    )

    parser.add_argument(
        "--budgets",
        type=int,
        nargs="+",
        default=list(DEFAULT_BUDGETS),
    )

    parser.add_argument(
        "--results-dir",
        type=Path,
        default=DEFAULT_RESULTS_DIR,
    )

    parser.add_argument(
        "--ranking-batch-size",
        type=int,
        default=4096,
    )

    return parser.parse_args()


def load_candidates(
    path: Path,
) -> list[dict[str, Any]]:
    values = []

    with path.open(
        "r",
        encoding="utf-8",
    ) as handle:
        for line in handle:
            if not line.strip():
                continue

            row = json.loads(line)

            values.append(
                {
                    "piece": row["piece"],
                    "frequency": int(
                        row["frequency"]
                    ),
                    "characters": int(
                        row["characters"]
                    ),
                    "reference_piece_id": (
                        row.get(
                            "reference_piece_id"
                        )
                    ),
                }
            )

    return values


def load_eval_texts(
    path: Path,
) -> list[str]:
    texts = []

    with path.open(
        "r",
        encoding="utf-8",
    ) as handle:
        for line in handle:
            if not line.strip():
                continue

            row = json.loads(line)

            text = row.get("text", "")

            if (
                isinstance(text, str)
                and text.strip()
            ):
                texts.append(text)

    return texts


def overlapping_piece_count(
    offsets: list[tuple[int, int]],
    start: int,
    end: int,
) -> int:
    return sum(
        1
        for begin, finish in offsets
        if (
            finish > start
            and begin < end
        )
    )


def rank_candidates(
    tokenizer,
    candidates: list[dict[str, Any]],
    batch_size: int,
) -> list[dict[str, Any]]:
    """
    Estimate the value of an internal subword by tokenizing it
    inside a neutral alphabetic frame.

    The frame discourages accidental word-boundary advantages:

        "x" + piece + "x"

    Ranking is training-side only. Final effectiveness is measured
    on the frozen evaluation holdout after the vocabulary is added.
    """

    ranked = []
    total = len(candidates)

    for start_idx in range(
        0,
        total,
        batch_size,
    ):
        batch = candidates[
            start_idx:start_idx + batch_size
        ]

        framed = [
            "x" + item["piece"] + "x"
            for item in batch
        ]

        encoded = tokenizer(
            framed,
            add_special_tokens=False,
            padding=False,
            truncation=False,
            return_offsets_mapping=True,
        )

        for item, offsets in zip(
            batch,
            encoded["offset_mapping"],
        ):
            piece = item["piece"]

            native_pieces = (
                overlapping_piece_count(
                    offsets,
                    1,
                    1 + len(piece),
                )
            )

            if native_pieces <= 1:
                continue

            savings = (
                native_pieces - 1
            )

            score = (
                item["frequency"]
                * savings
            )

            ranked.append(
                {
                    **item,
                    "native_pieces_in_frame":
                        native_pieces,
                    "estimated_savings_per_occurrence":
                        savings,
                    "estimated_training_savings":
                        score,
                }
            )

        processed = min(
            start_idx + batch_size,
            total,
        )

        print(
            f"Ranked {processed:,}/"
            f"{total:,} candidates...",
            flush=True,
        )

    ranked.sort(
        key=lambda item: (
            -item[
                "estimated_training_savings"
            ],
            -item["frequency"],
            -item[
                "native_pieces_in_frame"
            ],
            -item["characters"],
            item["piece"],
        )
    )

    return ranked


def count_unknown_tokens(
    tokenizer,
    input_ids,
) -> int:
    unk = tokenizer.unk_token_id

    if unk is None:
        return 0

    return sum(
        token_id == unk
        for ids in input_ids
        for token_id in ids
    )


def benchmark(
    tokenizer,
    texts: list[str],
) -> dict[str, Any]:
    encoded = tokenizer(
        texts,
        add_special_tokens=False,
        padding=False,
        truncation=False,
        return_offsets_mapping=True,
    )

    input_ids = encoded["input_ids"]
    offsets = encoded["offset_mapping"]

    token_counts = [
        len(ids)
        for ids in input_ids
    ]

    (
        fragmented_words,
        single_token_words,
        unaligned_words,
    ) = calculate_word_fragmentation(
        texts,
        offsets,
    )

    metrics = calculate_metrics(
        texts,
        token_counts,
        fragmented_words=fragmented_words,
        single_token_words=single_token_words,
        unaligned_words=unaligned_words,
        unknown_tokens=count_unknown_tokens(
            tokenizer,
            input_ids,
        ),
    )

    return {
        "effective_vocabulary_size":
            len(tokenizer),
        "reported_base_vocabulary_size":
            tokenizer.vocab_size,
        "characters": metrics.characters,
        "words": metrics.words,
        "tokens": metrics.tokens,
        "tokens_per_word":
            metrics.tokens_per_word,
        "characters_per_token":
            metrics.characters_per_token,
        "bytes": metrics.bytes,
        "bytes_per_token":
            metrics.bytes_per_token,
        "unknown_tokens":
            metrics.unknown_tokens,
        "unknown_token_rate":
            metrics.unknown_token_rate,
        "fragmented_words":
            metrics.fragmented_words,
        "single_token_words":
            metrics.single_token_words,
        "unaligned_words":
            metrics.unaligned_words,
        "word_fragmentation_rate":
            metrics.word_fragmentation_rate,
        "single_token_word_rate":
            metrics.single_token_word_rate,
        "unaligned_word_rate":
            metrics.unaligned_word_rate,
    }


def add_to_budget(
    tokenizer,
    ranked,
    selected: set[str],
    base_length: int,
    target_budget: int,
) -> list[dict[str, Any]]:
    newly_added = []

    for item in ranked:
        actual = (
            len(tokenizer)
            - base_length
        )

        if actual >= target_budget:
            break

        piece = item["piece"]

        if piece in selected:
            continue

        before = len(tokenizer)

        token = AddedToken(
            piece,
            single_word=False,
            lstrip=False,
            rstrip=False,
            normalized=True,
            special=False,
        )

        tokenizer.add_tokens([token])

        after = len(tokenizer)

        delta = after - before

        if delta == 0:
            continue

        if delta != 1:
            raise RuntimeError(
                "Unexpected vocabulary growth "
                f"for {piece!r}: "
                f"{before} -> {after}"
            )

        selected.add(piece)

        newly_added.append(
            {
                **item,
                "token_id":
                    tokenizer
                    .get_added_vocab()
                    .get(piece),
            }
        )

    actual = (
        len(tokenizer)
        - base_length
    )

    if actual != target_budget:
        raise RuntimeError(
            "Could not reach requested subword "
            f"budget {target_budget:,}; "
            f"actual={actual:,}. "
            "Increase the candidate pool or "
            "lower the requested budget."
        )

    return newly_added


def main() -> None:
    args = parse_args()

    if not args.candidates.is_file():
        raise FileNotFoundError(
            args.candidates
        )

    if not args.eval_corpus.is_file():
        raise FileNotFoundError(
            args.eval_corpus
        )

    budgets = sorted(
        set(args.budgets)
    )

    if not budgets or budgets[0] < 1:
        raise ValueError(
            "Budgets must contain positive integers."
        )

    candidates = load_candidates(
        args.candidates
    )

    texts = load_eval_texts(
        args.eval_corpus
    )

    print(
        "=== Oromo Phase 4B2 "
        "Subword Augmentation ==="
    )
    print("Tokenizer:", args.tokenizer)
    print(
        "Candidate types:",
        f"{len(candidates):,}",
    )
    print(
        "Evaluation records:",
        f"{len(texts):,}",
    )
    print(
        "Budgets:",
        ", ".join(
            f"+{x:,}"
            for x in budgets
        ),
    )

    tokenizer = (
        AutoTokenizer.from_pretrained(
            args.tokenizer,
            use_fast=True,
        )
    )

    if not tokenizer.is_fast:
        raise RuntimeError(
            "Fast tokenizer required."
        )

    print()
    print(
        "Ranking training-derived "
        "internal subwords..."
    )

    ranked = rank_candidates(
        tokenizer,
        candidates,
        args.ranking_batch_size,
    )

    if len(ranked) < max(budgets):
        raise RuntimeError(
            "Not enough fragmented subword "
            "candidates for largest budget. "
            f"Need {max(budgets):,}; "
            f"ranked {len(ranked):,}."
        )

    print(
        "Ranked fragmented candidates:",
        f"{len(ranked):,}",
    )

    print()
    print("Top 30:")

    for i, item in enumerate(
        ranked[:30],
        start=1,
    ):
        print(
            f"{i:>4} "
            f"score="
            f"{item['estimated_training_savings']:>10,} "
            f"freq={item['frequency']:>8,} "
            f"pieces="
            f"{item['native_pieces_in_frame']:>2} "
            f"{item['piece']}"
        )

    print()
    print("Benchmarking native tokenizer...")

    native = benchmark(
        tokenizer,
        texts,
    )

    working = copy.deepcopy(
        tokenizer
    )

    base_length = len(working)

    selected: set[str] = set()
    selected_records = []

    results = [
        {
            "budget": 0,
            "added_tokens": 0,
            "metrics": native,
        }
    ]

    for budget in budgets:
        print()
        print("=" * 72)
        print(
            f"Subword budget +{budget:,}"
        )
        print("=" * 72)

        new = add_to_budget(
            working,
            ranked,
            selected,
            base_length,
            budget,
        )

        selected_records.extend(new)

        metrics = benchmark(
            working,
            texts,
        )

        reduction = (
            (
                native["tokens_per_word"]
                - metrics["tokens_per_word"]
            )
            / native["tokens_per_word"]
        )

        results.append(
            {
                "budget": budget,
                "added_tokens": (
                    len(working)
                    - base_length
                ),
                "selected_subwords":
                    len(selected),
                "tokens_per_word_reduction_vs_native":
                    reduction,
                "metrics": metrics,
            }
        )

        print(
            "Tokens/word:",
            f"{metrics['tokens_per_word']:.4f}",
        )
        print(
            "Reduction vs native:",
            f"{reduction * 100:.2f}%",
        )
        print(
            "Fragmentation:",
            f"{metrics['word_fragmentation_rate'] * 100:.2f}%",
        )
        print(
            "Single-token words:",
            f"{metrics['single_token_word_rate'] * 100:.2f}%",
        )
        print(
            "UNK:",
            f"{metrics['unknown_tokens']:,}",
        )

    args.results_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    safe = (
        args.tokenizer
        .replace("/", "__")
        .replace(":", "_")
    )

    result_path = (
        args.results_dir
        / f"{safe}__subword_augmentation.json"
    )

    selected_path = (
        args.results_dir
        / f"{safe}__selected_subwords.jsonl"
    )

    payload = {
        "experiment": {
            "phase": "4B2",
            "type":
                "internal_subword_tokenizer_augmentation",
            "base_tokenizer":
                args.tokenizer,
            "candidate_pool":
                str(args.candidates),
            "evaluation_corpus":
                str(args.eval_corpus),
            "budgets": budgets,
            "candidate_boundary_policy":
                (
                    "SentencePiece boundary pieces "
                    "excluded; internal pieces only"
                ),
            "added_token_policy": {
                "single_word": False,
                "lstrip": False,
                "rstrip": False,
                "normalized": True,
            },
            "created_utc": datetime.now(
                timezone.utc
            ).isoformat(),
            "transformers_version":
                transformers.__version__,
            "tokenizers_version":
                tokenizers.__version__,
        },
        "ranked_candidate_count":
            len(ranked),
        "results": results,
    }

    result_path.write_text(
        json.dumps(
            payload,
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    with selected_path.open(
        "w",
        encoding="utf-8",
        newline="\n",
    ) as handle:
        for rank, item in enumerate(
            selected_records,
            start=1,
        ):
            handle.write(
                json.dumps(
                    {
                        "selection_rank":
                            rank,
                        **item,
                    },
                    ensure_ascii=False,
                    sort_keys=True,
                )
                + "\n"
            )

    print()
    print("Result:", result_path)
    print(
        "Selected subwords:",
        selected_path,
    )


if __name__ == "__main__":
    main()
