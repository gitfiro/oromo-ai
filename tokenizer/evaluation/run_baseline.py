from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import tokenizers
import transformers
from transformers import AutoTokenizer

from oromo_ai.tokenizer.metrics import (
    calculate_metrics,
    calculate_word_fragmentation,
)

DEFAULT_CORPUS_PATH = Path(
    "tokenizer/evaluation/samples/"
    "afriberta_oromo_v0.1.2_n10000.jsonl"
)
RESULTS_DIR = Path("tokenizer/evaluation/results")


def load_sample(
    corpus_path: Path,
    limit: int | None = None,
) -> list[str]:
    texts: list[str] = []

    with corpus_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue

            record = json.loads(line)
            text = record.get("text", "")

            if isinstance(text, str) and text.strip():
                texts.append(text)

            if limit is not None and len(texts) >= limit:
                break

    return texts


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Benchmark a pretrained tokenizer on the frozen "
            "Afaan Oromoo evaluation sample."
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
        default=DEFAULT_CORPUS_PATH,
        help="JSONL evaluation corpus.",
    )

    parser.add_argument(
        "--sample-size",
        type=int,
        default=None,
        help=(
            "Optional maximum number of records to evaluate. "
            "By default, evaluate the entire frozen sample."
        ),
    )

    parser.add_argument(
        "--output",
        default=None,
        help="Optional path for the JSON benchmark result.",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.sample_size is not None and args.sample_size < 1:
        raise ValueError("--sample-size must be >= 1")

    if not args.corpus.exists():
        raise FileNotFoundError(
            f"Evaluation corpus does not exist: {args.corpus}"
        )

    texts = load_sample(
        args.corpus,
        args.sample_size,
    )

    if not texts:
        raise RuntimeError(
            f"No usable text records found in {args.corpus}"
        )

    tokenizer = AutoTokenizer.from_pretrained(
        args.tokenizer,
        use_fast=True,
    )

    if not tokenizer.is_fast:
        raise RuntimeError(
            f"{args.tokenizer} did not load as a fast tokenizer. "
            "Offset mappings are required for fragmentation metrics."
        )

    encoded = tokenizer(
        texts,
        add_special_tokens=False,
        padding=False,
        truncation=False,
        return_offsets_mapping=True,
    )

    input_ids = encoded["input_ids"]
    offset_mappings = encoded["offset_mapping"]

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
        offset_mappings,
    )

    unknown_token_id = tokenizer.unk_token_id
    unknown_count = 0

    if unknown_token_id is not None:
        unknown_count = sum(
            token_id == unknown_token_id
            for ids in input_ids
            for token_id in ids
        )

    metrics = calculate_metrics(
        texts,
        token_counts,
        fragmented_words=fragmented_words,
        single_token_words=single_token_words,
        unaligned_words=unaligned_words,
        unknown_tokens=unknown_count,
    )

    result = {
        "benchmark": {
            "tokenizer": args.tokenizer,
            "corpus": str(args.corpus),
            "sample_size": len(texts),
            "timestamp_utc": datetime.now(
                timezone.utc
            ).isoformat(),
        },
        "versions": {
            "transformers": transformers.__version__,
            "tokenizers": tokenizers.__version__,
        },
        "metrics": {
            "vocabulary_size": tokenizer.vocab_size,
            "characters": metrics.characters,
            "words": metrics.words,
            "tokens": metrics.tokens,
            "tokens_per_word": metrics.tokens_per_word,
            "characters_per_token": (
                metrics.characters_per_token
            ),
            "unknown_tokens": metrics.unknown_tokens,
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
            "bytes": metrics.bytes,
            "bytes_per_token": (
                metrics.bytes_per_token
            ),
        },
        "sample_tokenizations": [
            {
                "text": text,
                "tokens": tokenizer.convert_ids_to_tokens(ids),
            }
            for text, ids in zip(
                texts[:10],
                input_ids[:10],
            )
        ],
    }

    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = (
        Path(args.output)
        if args.output
        else RESULTS_DIR
        / (
            args.tokenizer.replace("/", "__")
            + f"__n{len(texts)}.json"
        )
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path.write_text(
        json.dumps(
            result,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(
        "\n=== Afaan Oromoo Tokenizer Benchmark ==="
    )
    print(f"Tokenizer: {args.tokenizer}")
    print(f"Corpus: {args.corpus}")
    print(f"Sample size: {len(texts):,}")
    print(
        f"Vocabulary size: "
        f"{tokenizer.vocab_size:,}"
    )
    print(
        f"Characters: {metrics.characters:,}"
    )
    print(f"Words: {metrics.words:,}")
    print(f"Tokens: {metrics.tokens:,}")
    print(
        f"Tokens/word: "
        f"{metrics.tokens_per_word:.4f}"
    )
    print(
        f"Characters/token: "
        f"{metrics.characters_per_token:.4f}"
    )
    print(
        f"Unknown tokens: "
        f"{metrics.unknown_tokens:,}"
    )
    print(
        f"Unknown token rate: "
        f"{metrics.unknown_token_rate:.6f}"
    )
    print(
        f"Fragmented words: "
        f"{metrics.fragmented_words:,}"
    )
    print(
        f"Single-token words: "
        f"{metrics.single_token_words:,}"
    )
    print(
        f"Unaligned words: "
        f"{metrics.unaligned_words:,}"
    )
    print(
        f"Word fragmentation rate: "
        f"{metrics.word_fragmentation_rate:.6f}"
    )
    print(
        f"Single-token word rate: "
        f"{metrics.single_token_word_rate:.6f}"
    )
    print(
        f"Unaligned word rate: "
        f"{metrics.unaligned_word_rate:.8f}"
    )
    print(f"Bytes: {metrics.bytes:,}")
    print(
        f"Bytes/token: "
        f"{metrics.bytes_per_token:.4f}"
    )
    print(
        f"Transformers version: "
        f"{transformers.__version__}"
    )
    print(
        f"Tokenizers version: "
        f"{tokenizers.__version__}"
    )
    print(f"JSON result: {output_path}")

    print("\nSample tokenizations:")

    for text, ids in zip(
        texts[:10],
        input_ids[:10],
    ):
        tokens = tokenizer.convert_ids_to_tokens(
            ids
        )

        print(f"\nTEXT: {text}")
        print(
            f"TOKENS: {' | '.join(tokens)}"
        )


if __name__ == "__main__":
    main()