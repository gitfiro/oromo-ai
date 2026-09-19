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
    "oromo_word_candidates.jsonl"
)

DEFAULT_EVAL_CORPUS = Path(
    "tokenizer/evaluation/samples/"
    "afriberta_oromo_v0.1.2_n10000.jsonl"
)

DEFAULT_RESULTS_DIR = Path(
    "tokenizer/augmentation/results"
)

DEFAULT_BUDGETS = (
    2000,
    4000,
    8000,
    16000,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Simulate whole-word Afaan Oromoo "
            "vocabulary augmentation for a pretrained "
            "Hugging Face tokenizer."
        )
    )

    parser.add_argument(
        "--tokenizer",
        required=True,
        help=(
            "Hugging Face tokenizer identifier."
        ),
    )

    parser.add_argument(
        "--candidates",
        type=Path,
        default=DEFAULT_CANDIDATES,
        help=(
            "Leakage-safe lexical candidate JSONL."
        ),
    )

    parser.add_argument(
        "--eval-corpus",
        type=Path,
        default=DEFAULT_EVAL_CORPUS,
        help=(
            "Frozen tokenizer evaluation JSONL."
        ),
    )

    parser.add_argument(
        "--budgets",
        type=int,
        nargs="+",
        default=list(DEFAULT_BUDGETS),
        help=(
            "Exact effective vocabulary additions "
            "to benchmark."
        ),
    )

    parser.add_argument(
        "--results-dir",
        type=Path,
        default=DEFAULT_RESULTS_DIR,
        help=(
            "Directory for augmentation experiment "
            "results."
        ),
    )

    parser.add_argument(
        "--ranking-batch-size",
        type=int,
        default=4096,
        help=(
            "Batch size used while ranking lexical "
            "candidates with the native tokenizer."
        ),
    )

    return parser.parse_args()


def load_candidate_pool(
    path: Path,
) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []

    with path.open(
        "r",
        encoding="utf-8",
    ) as handle:
        for line in handle:
            if not line.strip():
                continue

            record = json.loads(line)

            word = record["word"]
            frequency = int(
                record["frequency"]
            )

            candidates.append(
                {
                    "word": word,
                    "frequency": frequency,
                }
            )

    return candidates


def load_eval_texts(
    path: Path,
) -> list[str]:
    texts: list[str] = []

    with path.open(
        "r",
        encoding="utf-8",
    ) as handle:
        for line in handle:
            if not line.strip():
                continue

            record = json.loads(line)

            text = record.get(
                "text",
                "",
            )

            if (
                isinstance(text, str)
                and text.strip()
            ):
                texts.append(text)

    return texts


def count_word_pieces(
    offsets: list[tuple[int, int]],
    word_length: int,
) -> int:
    """
    Count native tokenizer pieces overlapping a candidate
    word in the synthetic context:

        " " + word

    The leading space approximates the dominant in-sentence
    word-boundary condition without consulting evaluation data.
    """

    word_start = 1
    word_end = 1 + word_length

    return sum(
        1
        for begin, end in offsets
        if (
            end > word_start
            and begin < word_end
        )
    )


def rank_candidates(
    tokenizer,
    candidates: list[dict[str, Any]],
    batch_size: int,
) -> list[dict[str, Any]]:
    """
    Rank training-derived candidates by estimated native
    token savings:

        frequency * (native_pieces - 1)

    Candidates already represented as one native piece are
    excluded because they provide no sequence-length benefit.
    """

    ranked: list[dict[str, Any]] = []

    total = len(candidates)

    for start in range(
        0,
        total,
        batch_size,
    ):
        batch = candidates[
            start:start + batch_size
        ]

        texts = [
            " " + item["word"]
            for item in batch
        ]

        encoded = tokenizer(
            texts,
            add_special_tokens=False,
            padding=False,
            truncation=False,
            return_offsets_mapping=True,
        )

        for item, offsets in zip(
            batch,
            encoded["offset_mapping"],
        ):
            word = item["word"]
            frequency = item["frequency"]

            native_pieces = (
                count_word_pieces(
                    offsets,
                    len(word),
                )
            )

            if native_pieces <= 1:
                continue

            savings_per_occurrence = (
                native_pieces - 1
            )

            estimated_training_savings = (
                frequency
                * savings_per_occurrence
            )

            ranked.append(
                {
                    "word": word,
                    "frequency": frequency,
                    "native_pieces": (
                        native_pieces
                    ),
                    "savings_per_occurrence": (
                        savings_per_occurrence
                    ),
                    "estimated_training_savings": (
                        estimated_training_savings
                    ),
                }
            )

        processed = min(
            start + batch_size,
            total,
        )

        print(
            f"Ranked "
            f"{processed:,}/{total:,} "
            f"candidate forms..."
        )

    ranked.sort(
        key=lambda item: (
            -item[
                "estimated_training_savings"
            ],
            -item["frequency"],
            -item["native_pieces"],
            item["word"],
        )
    )

    return ranked


def count_unknown_tokens(
    tokenizer,
    input_ids: list[list[int]],
) -> int:
    unknown_token_id = (
        tokenizer.unk_token_id
    )

    if unknown_token_id is None:
        return 0

    return sum(
        token_id == unknown_token_id
        for ids in input_ids
        for token_id in ids
    )


def benchmark_tokenizer(
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

    input_ids = encoded[
        "input_ids"
    ]

    offsets = encoded[
        "offset_mapping"
    ]

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

    unknown_count = (
        count_unknown_tokens(
            tokenizer,
            input_ids,
        )
    )

    metrics = calculate_metrics(
        texts,
        token_counts,
        fragmented_words=(
            fragmented_words
        ),
        single_token_words=(
            single_token_words
        ),
        unaligned_words=(
            unaligned_words
        ),
        unknown_tokens=(
            unknown_count
        ),
    )

    return {
        "effective_vocabulary_size": (
            len(tokenizer)
        ),
        "reported_base_vocabulary_size": (
            tokenizer.vocab_size
        ),
        "characters": (
            metrics.characters
        ),
        "words": (
            metrics.words
        ),
        "tokens": (
            metrics.tokens
        ),
        "tokens_per_word": (
            metrics.tokens_per_word
        ),
        "characters_per_token": (
            metrics.characters_per_token
        ),
        "unknown_tokens": (
            metrics.unknown_tokens
        ),
        "unknown_token_rate": (
            metrics.unknown_token_rate
        ),
        "fragmented_words": (
            metrics.fragmented_words
        ),
        "single_token_words": (
            metrics.single_token_words
        ),
        "unaligned_words": (
            metrics.unaligned_words
        ),
        "word_fragmentation_rate": (
            metrics.word_fragmentation_rate
        ),
        "single_token_word_rate": (
            metrics.single_token_word_rate
        ),
        "unaligned_word_rate": (
            metrics.unaligned_word_rate
        ),
        "bytes": (
            metrics.bytes
        ),
        "bytes_per_token": (
            metrics.bytes_per_token
        ),
    }


def resolve_added_token_id(
    tokenizer,
    word: str,
) -> int | None:
    """
    Return the exact vocabulary ID assigned to an added token.

    Added-vocabulary lookup is preferred over a normal
    tokenize/convert round-trip because AddedToken behavior
    may involve normalization or boundary handling.
    """

    added_vocab = (
        tokenizer.get_added_vocab()
    )

    token_id = added_vocab.get(word)

    if token_id is not None:
        return int(token_id)

    return None


def add_until_budget(
    tokenizer,
    ranked_candidates: list[
        dict[str, Any]
    ],
    selected_words: set[str],
    base_tokenizer_length: int,
    target_budget: int,
) -> list[dict[str, Any]]:
    """
    Add candidate words until the tokenizer has gained exactly
    target_budget effective vocabulary entries.

    The authoritative augmentation count is:

        len(tokenizer) - base_tokenizer_length

    rather than the return value from add_tokens().
    """

    added_records: list[
        dict[str, Any]
    ] = []

    actual_added = (
        len(tokenizer)
        - base_tokenizer_length
    )

    if actual_added > target_budget:
        raise RuntimeError(
            "Tokenizer already exceeds requested "
            "augmentation budget. "
            f"Target={target_budget:,}, "
            f"actual={actual_added:,}"
        )

    if actual_added == target_budget:
        return added_records

    for item in ranked_candidates:
        actual_added = (
            len(tokenizer)
            - base_tokenizer_length
        )

        if actual_added >= target_budget:
            break

        word = item["word"]

        if word in selected_words:
            continue

        before_length = len(tokenizer)

        token = AddedToken(
            word,
            single_word=True,
            lstrip=False,
            rstrip=False,
            normalized=True,
            special=False,
        )

        tokenizer.add_tokens(
            [token]
        )

        after_length = len(tokenizer)

        actual_delta = (
            after_length - before_length
        )

        # A candidate can collide with an existing native or
        # added vocabulary entry after tokenizer normalization.
        # Such a candidate does not count toward our budget.
        if actual_delta == 0:
            continue

        if actual_delta != 1:
            raise RuntimeError(
                "Unexpected tokenizer vocabulary growth "
                f"for {word!r}: "
                f"{before_length:,} -> "
                f"{after_length:,}"
            )

        selected_words.add(word)

        token_id = resolve_added_token_id(
            tokenizer,
            word,
        )

        added_records.append(
            {
                **item,
                "token_id": token_id,
            }
        )

    actual_added = (
        len(tokenizer)
        - base_tokenizer_length
    )

    if actual_added != target_budget:
        raise RuntimeError(
            "Could not reach requested effective "
            "augmentation budget. "
            f"Target={target_budget:,}, "
            f"actual={actual_added:,}. "
            "The candidate pool may not contain "
            "enough genuinely new tokens."
        )

    return added_records


def percentage_reduction(
    baseline: float,
    value: float,
) -> float:
    if baseline == 0:
        return 0.0

    return (
        (baseline - value)
        / baseline
    )


def main() -> None:
    args = parse_args()

    if not args.candidates.exists():
        raise FileNotFoundError(
            args.candidates
        )

    if not args.eval_corpus.exists():
        raise FileNotFoundError(
            args.eval_corpus
        )

    if args.ranking_batch_size < 1:
        raise ValueError(
            "--ranking-batch-size must be >= 1"
        )

    budgets = sorted(
        set(args.budgets)
    )

    if not budgets:
        raise ValueError(
            "At least one augmentation budget "
            "is required."
        )

    if budgets[0] < 1:
        raise ValueError(
            "Budgets must all be >= 1."
        )

    print(
        "=== Oromo Tokenizer "
        "Augmentation Simulation ==="
    )

    print(
        f"Base tokenizer: "
        f"{args.tokenizer}"
    )

    print(
        f"Candidate pool: "
        f"{args.candidates}"
    )

    print(
        f"Evaluation corpus: "
        f"{args.eval_corpus}"
    )

    print(
        "Budgets: "
        + ", ".join(
            f"{budget:,}"
            for budget in budgets
        )
    )

    candidates = load_candidate_pool(
        args.candidates
    )

    eval_texts = load_eval_texts(
        args.eval_corpus
    )

    if not candidates:
        raise RuntimeError(
            "Candidate pool is empty."
        )

    if not eval_texts:
        raise RuntimeError(
            "Evaluation corpus is empty."
        )

    print(
        f"Candidate forms: "
        f"{len(candidates):,}"
    )

    print(
        f"Evaluation records: "
        f"{len(eval_texts):,}"
    )

    print()
    print(
        "Loading base tokenizer..."
    )

    base_tokenizer = (
        AutoTokenizer.from_pretrained(
            args.tokenizer,
            use_fast=True,
        )
    )

    if not base_tokenizer.is_fast:
        raise RuntimeError(
            "A fast tokenizer is required "
            "for offset mappings."
        )

    reported_native_vocab = (
        base_tokenizer.vocab_size
    )

    effective_native_vocab = len(
        base_tokenizer
    )

    print(
        f"Reported native vocabulary: "
        f"{reported_native_vocab:,}"
    )

    print(
        f"Effective tokenizer length: "
        f"{effective_native_vocab:,}"
    )

    print()
    print(
        "Ranking training-side candidates "
        "by estimated token savings..."
    )

    ranked_candidates = rank_candidates(
        base_tokenizer,
        candidates,
        args.ranking_batch_size,
    )

    if (
        len(ranked_candidates)
        < max(budgets)
    ):
        raise RuntimeError(
            "Not enough fragmented lexical "
            "candidates to satisfy the largest "
            "augmentation budget. "
            f"Need {max(budgets):,}, "
            f"have {len(ranked_candidates):,}."
        )

    print()
    print(
        f"Fragmented candidates ranked: "
        f"{len(ranked_candidates):,}"
    )

    print()
    print(
        "Top 30 ranked additions:"
    )

    for index, item in enumerate(
        ranked_candidates[:30],
        start=1,
    ):
        print(
            f"{index:>4} "
            f"score="
            f"{item['estimated_training_savings']:>9,} "
            f"freq="
            f"{item['frequency']:>7,} "
            f"pieces="
            f"{item['native_pieces']:>2} "
            f"{item['word']}"
        )

    print()
    print(
        "Benchmarking native tokenizer..."
    )

    native_metrics = (
        benchmark_tokenizer(
            base_tokenizer,
            eval_texts,
        )
    )

    working_tokenizer = (
        copy.deepcopy(
            base_tokenizer
        )
    )

    base_tokenizer_length = len(
        working_tokenizer
    )

    selected_words: set[str] = set()

    all_selected_records: list[
        dict[str, Any]
    ] = []

    results: list[
        dict[str, Any]
    ] = []

    results.append(
        {
            "budget": 0,
            "added_tokens": 0,
            "selected_word_count": 0,
            "metrics": native_metrics,
        }
    )

    for budget in budgets:
        print()
        print(
            "=" * 72
        )

        print(
            f"Augmentation budget: "
            f"+{budget:,}"
        )

        print(
            "=" * 72
        )

        newly_added = add_until_budget(
            working_tokenizer,
            ranked_candidates,
            selected_words,
            base_tokenizer_length,
            budget,
        )

        all_selected_records.extend(
            newly_added
        )

        actual_added_tokens = (
            len(working_tokenizer)
            - base_tokenizer_length
        )

        print(
            f"Actual added tokens: "
            f"{actual_added_tokens:,}"
        )

        print(
            f"Selected lexical forms: "
            f"{len(selected_words):,}"
        )

        print(
            f"Effective vocabulary: "
            f"{len(working_tokenizer):,}"
        )

        if actual_added_tokens != budget:
            raise RuntimeError(
                "Internal augmentation accounting "
                "mismatch. "
                f"Budget={budget:,}, "
                f"actual={actual_added_tokens:,}"
            )

        metrics = benchmark_tokenizer(
            working_tokenizer,
            eval_texts,
        )

        reduction = (
            percentage_reduction(
                native_metrics[
                    "tokens_per_word"
                ],
                metrics[
                    "tokens_per_word"
                ],
            )
        )

        results.append(
            {
                "budget": budget,
                "added_tokens": (
                    actual_added_tokens
                ),
                "selected_word_count": (
                    len(selected_words)
                ),
                "tokens_per_word_reduction_vs_native": (
                    reduction
                ),
                "metrics": metrics,
            }
        )

        print(
            f"Tokens/word: "
            f"{metrics['tokens_per_word']:.4f}"
        )

        print(
            f"Tokens/word reduction vs native: "
            f"{reduction * 100:.2f}%"
        )

        print(
            f"Fragmentation: "
            f"{metrics['word_fragmentation_rate'] * 100:.2f}%"
        )

        print(
            f"Single-token words: "
            f"{metrics['single_token_word_rate'] * 100:.2f}%"
        )

        print(
            f"Unknown tokens: "
            f"{metrics['unknown_tokens']:,}"
        )

    args.results_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    safe_name = (
        args.tokenizer
        .replace("/", "__")
        .replace(":", "_")
    )

    result_path = (
        args.results_dir
        / (
            f"{safe_name}"
            "__augmentation.json"
        )
    )

    selected_path = (
        args.results_dir
        / (
            f"{safe_name}"
            "__selected_tokens.jsonl"
        )
    )

    payload = {
        "experiment": {
            "type": (
                "whole_word_tokenizer_augmentation"
            ),
            "base_tokenizer": (
                args.tokenizer
            ),
            "candidate_pool": (
                str(args.candidates)
            ),
            "evaluation_corpus": (
                str(args.eval_corpus)
            ),
            "budgets": budgets,
            "ranking": (
                "frequency * "
                "(native_pieces - 1)"
            ),
            "ranking_data_source": (
                "candidate frequencies derived "
                "only from tokenizer training split"
            ),
            "augmentation_budget_definition": (
                "exact increase in len(tokenizer) "
                "relative to the original loaded "
                "tokenizer"
            ),
            "timestamp_utc": (
                datetime.now(
                    timezone.utc
                ).isoformat()
            ),
        },
        "base_tokenizer": {
            "reported_vocab_size": (
                reported_native_vocab
            ),
            "effective_tokenizer_length": (
                effective_native_vocab
            ),
            "preexisting_added_or_special_entries": (
                effective_native_vocab
                - reported_native_vocab
            ),
        },
        "versions": {
            "transformers": (
                transformers.__version__
            ),
            "tokenizers": (
                tokenizers.__version__
            ),
        },
        "candidate_count": (
            len(candidates)
        ),
        "ranked_fragmented_candidate_count": (
            len(ranked_candidates)
        ),
        "evaluation_record_count": (
            len(eval_texts)
        ),
        "results": results,
    }

    result_path.write_text(
        json.dumps(
            payload,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    with selected_path.open(
        "w",
        encoding="utf-8",
    ) as handle:
        for index, item in enumerate(
            all_selected_records,
            start=1,
        ):
            record = {
                "augmentation_rank": (
                    index
                ),
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

    print()
    print(
        "=== Augmentation Summary ==="
    )

    print(
        f"{'Budget':>8} "
        f"{'Vocab':>10} "
        f"{'Tok/Word':>10} "
        f"{'Δ Tok %':>9} "
        f"{'Frag %':>9} "
        f"{'Single %':>10} "
        f"{'UNK':>8}"
    )

    print(
        "-" * 75
    )

    native_tokens_per_word = (
        native_metrics[
            "tokens_per_word"
        ]
    )

    for result in results:
        metrics = result[
            "metrics"
        ]

        reduction = (
            percentage_reduction(
                native_tokens_per_word,
                metrics[
                    "tokens_per_word"
                ],
            )
        )

        print(
            f"{result['budget']:>8,} "
            f"{metrics['effective_vocabulary_size']:>10,} "
            f"{metrics['tokens_per_word']:>10.4f} "
            f"{reduction * 100:>8.2f}% "
            f"{metrics['word_fragmentation_rate'] * 100:>8.2f}% "
            f"{metrics['single_token_word_rate'] * 100:>9.2f}% "
            f"{metrics['unknown_tokens']:>8,}"
        )

    print()
    print(
        f"Result JSON: "
        f"{result_path}"
    )

    print(
        f"Selected-token ledger: "
        f"{selected_path}"
    )


if __name__ == "__main__":
    main()