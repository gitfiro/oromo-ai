"""Compute reproducible composition statistics for an Oromo text corpus."""

from __future__ import annotations

import hashlib
import json
import math
import re
import statistics
from collections import Counter
from pathlib import Path


INPUT = Path("data/processed/afriberta_oromo_v0.1.1/train.jsonl")
OUTPUT = Path("reports/afriberta_oromo_v0.1.1/corpus_statistics.json")

TOKEN_RE = re.compile(r"\S+")

OROMO_CHARS = set(
    "QqXxCcGg"
)

OROMO_APOSTROPHES = set(
    "'’ʼ"
)

ENGLISH_SIGNAL = {
    "the", "and", "of", "to", "in", "for", "on", "with",
    "is", "are", "was", "were", "this", "that", "from",
    "news", "read", "more", "about", "current", "affairs",
}

DIGIT_RE = re.compile(r"\d")
LATIN_RE = re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿ]")
URL_RE = re.compile(r"(?i)\b(?:https?://|www\.)")
HTML_RE = re.compile(r"</?[A-Za-z][^>]*>")
REPEATED_SPACE_RE = re.compile(r"\s{2,}")


def percentile(values: list[int], p: float) -> float:
    """Compute a linear-interpolated percentile."""
    if not values:
        return 0.0

    values = sorted(values)

    position = (len(values) - 1) * p
    lower = math.floor(position)
    upper = math.ceil(position)

    if lower == upper:
        return float(values[lower])

    weight = position - lower
    return values[lower] + (values[upper] - values[lower]) * weight


def sha256(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


def main() -> None:
    if not INPUT.is_file():
        raise FileNotFoundError(INPUT)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    record_lengths: list[int] = []
    token_counts: list[int] = []

    vocabulary: Counter[str] = Counter()
    characters: Counter[str] = Counter()

    source_counts: Counter[str] = Counter()
    domain_counts: Counter[str] = Counter()
    dialect_counts: Counter[str] = Counter()

    english_signal_records = 0
    english_signal_hits = 0

    short_records = 0
    long_records = 0
    empty_records = 0

    url_records = 0
    html_records = 0
    whitespace_records = 0

    total_characters = 0
    total_tokens = 0
    total_records = 0

    with INPUT.open("r", encoding="utf-8") as handle:
        for line in handle:
            record = json.loads(line)
            text = record["text"]

            total_records += 1

            char_count = len(text)
            tokens = TOKEN_RE.findall(text)
            token_count = len(tokens)

            record_lengths.append(char_count)
            token_counts.append(token_count)

            total_characters += char_count
            total_tokens += token_count

            vocabulary.update(token.lower() for token in tokens)
            characters.update(text)

            metadata = record.get("metadata", {})

            source_counts[record.get("source", "")] += 1
            domain_counts[record.get("domain", "")] += 1
            dialect_counts[record.get("dialect", "")] += 1

            if not text.strip():
                empty_records += 1

            if char_count < 20:
                short_records += 1

            if char_count > 10000:
                long_records += 1

            if URL_RE.search(text):
                url_records += 1

            if HTML_RE.search(text):
                html_records += 1

            if REPEATED_SPACE_RE.search(text):
                whitespace_records += 1

            lower_tokens = {token.lower().strip(".,!?;:()[]{}\"'") for token in tokens}

            hits = len(lower_tokens & ENGLISH_SIGNAL)

            if hits:
                english_signal_records += 1
                english_signal_hits += hits

    unique_tokens = len(vocabulary)

    stats = {
        "dataset": {
            "input": str(INPUT),
            "sha256": sha256(INPUT),
            "records": total_records,
            "characters": total_characters,
            "tokens_whitespace_estimate": total_tokens,
        },
        "lengths_characters": {
            "min": min(record_lengths),
            "max": max(record_lengths),
            "mean": statistics.mean(record_lengths),
            "median": statistics.median(record_lengths),
            "p50": percentile(record_lengths, 0.50),
            "p90": percentile(record_lengths, 0.90),
            "p95": percentile(record_lengths, 0.95),
            "p99": percentile(record_lengths, 0.99),
        },
        "lengths_tokens": {
            "min": min(token_counts),
            "max": max(token_counts),
            "mean": statistics.mean(token_counts),
            "median": statistics.median(token_counts),
            "p90": percentile(token_counts, 0.90),
            "p95": percentile(token_counts, 0.95),
            "p99": percentile(token_counts, 0.99),
        },
        "vocabulary": {
            "unique_whitespace_tokens": unique_tokens,
            "total_whitespace_tokens": total_tokens,
            "type_token_ratio": (
                unique_tokens / total_tokens
                if total_tokens
                else 0.0
            ),
        },
        "character_profile": {
            "unique_characters": len(characters),
            "top_characters": characters.most_common(50),
            "oromo_specific_character_counts": {
                char: characters[char]
                for char in sorted(OROMO_CHARS)
            },
            "apostrophe_counts": {
                char: characters[char]
                for char in sorted(OROMO_APOSTROPHES)
            },
            "digit_characters": sum(
                count
                for char, count in characters.items()
                if char.isdigit()
            ),
        },
        "english_signal": {
            "records_with_common_english_words": english_signal_records,
            "english_signal_record_rate": (
                english_signal_records / total_records
                if total_records
                else 0.0
            ),
            "total_signal_hits": english_signal_hits,
        },
        "artifact_signals": {
            "records_with_urls": url_records,
            "records_with_html": html_records,
            "records_with_repeated_whitespace": whitespace_records,
        },
        "length_flags": {
            "records_under_20_characters": short_records,
            "records_over_10000_characters": long_records,
            "empty_records": empty_records,
        },
        "metadata": {
            "sources": source_counts.most_common(50),
            "domains": domain_counts.most_common(50),
            "dialects": dialect_counts.most_common(50),
        },
    }

    OUTPUT.write_text(
        json.dumps(
            stats,
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    print("=== CORPUS STATISTICS ===")
    print(f"records: {total_records}")
    print(f"characters: {total_characters:,}")
    print(f"whitespace_tokens: {total_tokens:,}")
    print(f"unique_tokens: {unique_tokens:,}")
    print(f"type_token_ratio: {stats['vocabulary']['type_token_ratio']:.6f}")
    print()
    print("character lengths:")
    print(f"  min: {stats['lengths_characters']['min']}")
    print(f"  median: {stats['lengths_characters']['median']:.1f}")
    print(f"  mean: {stats['lengths_characters']['mean']:.1f}")
    print(f"  p95: {stats['lengths_characters']['p95']:.1f}")
    print(f"  p99: {stats['lengths_characters']['p99']:.1f}")
    print(f"  max: {stats['lengths_characters']['max']}")
    print()
    print("token lengths:")
    print(f"  median: {stats['lengths_tokens']['median']:.1f}")
    print(f"  mean: {stats['lengths_tokens']['mean']:.1f}")
    print(f"  p95: {stats['lengths_tokens']['p95']:.1f}")
    print(f"  p99: {stats['lengths_tokens']['p99']:.1f}")
    print(f"  max: {stats['lengths_tokens']['max']}")
    print()
    print(f"english-signal records: {english_signal_records:,}")
    print(f"records with URLs: {url_records:,}")
    print(f"records with HTML: {html_records:,}")
    print(f"records under 20 chars: {short_records:,}")
    print(f"records over 10,000 chars: {long_records:,}")
    print()
    print(f"report: {OUTPUT}")


if __name__ == "__main__":
    main()
