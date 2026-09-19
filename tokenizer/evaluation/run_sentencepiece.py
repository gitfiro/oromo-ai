from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

import sentencepiece as spm


DEFAULT_SAMPLE = Path(
    "tokenizer/evaluation/samples/"
    "afriberta_oromo_v0.1.2_n10000.jsonl"
)

DEFAULT_RESULTS_DIR = Path(
    "tokenizer/evaluation/results"
)

WORD_PATTERN = re.compile(r"\S+")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Benchmark a native SentencePiece tokenizer "
            "on the frozen Afaan Oromoo evaluation sample."
        )
    )

    parser.add_argument(
        "--model",
        type=Path,
        required=True,
        help="Path to the SentencePiece .model file.",
    )

    parser.add_argument(
        "--name",
        required=True,
        help="Stable candidate name used in benchmark output.",
    )

    parser.add_argument(
        "--sample",
        type=Path,
        default=DEFAULT_SAMPLE,
        help="Frozen tokenizer evaluation JSONL sample.",
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional JSON output path.",
    )

    return parser.parse_args()


def load_sample(path: Path) -> list[dict]:
    records: list[dict] = []

    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            line = line.strip()

            if not line:
                continue

            record = json.loads(line)

            text = record.get("text")

            if not isinstance(text, str) or not text.strip():
                raise ValueError(
                    f"Invalid text in evaluation sample "
                    f"at line {line_number}"
                )

            records.append(record)

    if not records:
        raise RuntimeError(
            f"No usable evaluation records found in {path}"
        )

    return records


def whitespace_spans(text: str) -> list[tuple[int, int]]:
    return [
        match.span()
        for match in WORD_PATTERN.finditer(text)
    ]


def main() -> None:
    args = parse_args()

    if not args.model.exists():
        raise FileNotFoundError(args.model)

    if not args.sample.exists():
        raise FileNotFoundError(args.sample)

    records = load_sample(args.sample)
    texts = [record["text"] for record in records]

    sp = spm.SentencePieceProcessor(
        model_file=str(args.model)
    )

    vocabulary_size = sp.get_piece_size()

    total_characters = 0
    total_bytes = 0
    total_words = 0
    total_tokens = 0

    fragmented_words = 0
    single_token_words = 0
    unaligned_words = 0
    unknown_tokens = 0

    sample_tokenizations: list[dict] = []

    for record_index, text in enumerate(texts):
        total_characters += len(text)
        total_bytes += len(text.encode("utf-8"))

        words = text.split()
        total_words += len(words)

        ids = sp.encode(
            text,
            out_type=int,
            add_bos=False,
            add_eos=False,
        )

        pieces = sp.encode(
            text,
            out_type=str,
            add_bos=False,
            add_eos=False,
        )

        total_tokens += len(ids)

        unknown_tokens += sum(
            token_id == sp.unk_id()
            for token_id in ids
        )

        if record_index < 10:
            sample_tokenizations.append(
                {
                    "text": text,
                    "tokens": pieces,
                }
            )

        # SentencePiece exposes immutable proto pieces containing
        # begin/end offsets into the original input.
        proto = sp.encode(
    text,
    return_type="proto",
)

        token_spans = [
            (piece.begin, piece.end)
            for piece in proto.pieces
            if piece.end > piece.begin
        ]

        for word_start, word_end in whitespace_spans(text):
            overlapping = [
                (token_start, token_end)
                for token_start, token_end in token_spans
                if token_start < word_end
                and token_end > word_start
            ]

            if not overlapping:
                unaligned_words += 1
                continue

            # Count unique tokenizer pieces that overlap this
            # whitespace-delimited word.
            piece_count = len(overlapping)

            if piece_count == 1:
                single_token_words += 1
            else:
                fragmented_words += 1

    accounted_words = (
        fragmented_words
        + single_token_words
        + unaligned_words
    )

    if accounted_words != total_words:
        raise RuntimeError(
            "Word accounting invariant failed: "
            f"{fragmented_words:,} fragmented + "
            f"{single_token_words:,} single + "
            f"{unaligned_words:,} unaligned != "
            f"{total_words:,} total"
        )

    tokens_per_word = (
        total_tokens / total_words
        if total_words
        else 0.0
    )

    characters_per_token = (
        total_characters / total_tokens
        if total_tokens
        else 0.0
    )

    bytes_per_token = (
        total_bytes / total_tokens
        if total_tokens
        else 0.0
    )

    unknown_token_rate = (
        unknown_tokens / total_tokens
        if total_tokens
        else 0.0
    )

    word_fragmentation_rate = (
        fragmented_words / total_words
        if total_words
        else 0.0
    )

    single_token_word_rate = (
        single_token_words / total_words
        if total_words
        else 0.0
    )

    unaligned_word_rate = (
        unaligned_words / total_words
        if total_words
        else 0.0
    )

    result = {
        "benchmark": {
            "tokenizer": args.name,
            "tokenizer_type": "sentencepiece_unigram",
            "model": str(args.model),
            "model_sha256": sha256_file(args.model),
            "corpus": str(args.sample),
            "corpus_sha256": sha256_file(args.sample),
            "sample_size": len(records),
            "timestamp_utc": datetime.now(
                timezone.utc
            ).isoformat(),
        },
        "versions": {
            "sentencepiece": spm.__version__,
        },
        "metrics": {
            "vocabulary_size": vocabulary_size,
            "characters": total_characters,
            "words": total_words,
            "tokens": total_tokens,
            "tokens_per_word": tokens_per_word,
            "characters_per_token": characters_per_token,
            "unknown_tokens": unknown_tokens,
            "unknown_token_rate": unknown_token_rate,
            "fragmented_words": fragmented_words,
            "single_token_words": single_token_words,
            "unaligned_words": unaligned_words,
            "word_fragmentation_rate": (
                word_fragmentation_rate
            ),
            "single_token_word_rate": (
                single_token_word_rate
            ),
            "unaligned_word_rate": (
                unaligned_word_rate
            ),
            "bytes": total_bytes,
            "bytes_per_token": bytes_per_token,
        },
        "sample_tokenizations": sample_tokenizations,
    }

    DEFAULT_RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = (
        args.output
        if args.output is not None
        else DEFAULT_RESULTS_DIR
        / f"{args.name}__n{len(records)}.json"
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
        )
        + "\n",
        encoding="utf-8",
    )

    print()
    print("=== Afaan Oromoo SentencePiece Benchmark ===")
    print(f"Tokenizer: {args.name}")
    print(f"Model: {args.model}")
    print(f"Corpus: {args.sample}")
    print(f"Sample size: {len(records):,}")
    print(f"Vocabulary size: {vocabulary_size:,}")
    print(f"Characters: {total_characters:,}")
    print(f"Words: {total_words:,}")
    print(f"Tokens: {total_tokens:,}")
    print(f"Tokens/word: {tokens_per_word:.4f}")
    print(
        f"Characters/token: "
        f"{characters_per_token:.4f}"
    )
    print(f"Unknown tokens: {unknown_tokens:,}")
    print(
        f"Unknown token rate: "
        f"{unknown_token_rate:.6f}"
    )
    print(
        f"Fragmented words: "
        f"{fragmented_words:,}"
    )
    print(
        f"Single-token words: "
        f"{single_token_words:,}"
    )
    print(
        f"Unaligned words: "
        f"{unaligned_words:,}"
    )
    print(
        f"Word fragmentation rate: "
        f"{word_fragmentation_rate:.6f}"
    )
    print(
        f"Single-token word rate: "
        f"{single_token_word_rate:.6f}"
    )
    print(
        f"Unaligned word rate: "
        f"{unaligned_word_rate:.8f}"
    )
    print(f"Bytes: {total_bytes:,}")
    print(
        f"Bytes/token: "
        f"{bytes_per_token:.4f}"
    )
    print(
        f"SentencePiece version: "
        f"{spm.__version__}"
    )
    print(f"JSON result: {output_path}")

    print()
    print("Sample tokenizations:")

    for sample in sample_tokenizations:
        print()
        print(f"TEXT: {sample['text']}")
        print(
            "TOKENS: "
            + " | ".join(sample["tokens"])
        )


if __name__ == "__main__":
    main()