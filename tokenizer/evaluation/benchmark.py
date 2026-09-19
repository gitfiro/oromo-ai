from __future__ import annotations

import json
from pathlib import Path
from typing import Iterator

CORPUS_PATH = Path("data/processed/afriberta_oromo_v0.1.2/train.jsonl")


def iter_corpus(limit: int | None = None) -> Iterator[str]:
    """Yield non-empty text records from the validated production corpus."""
    count = 0

    with CORPUS_PATH.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            record = json.loads(line)
            text = record.get("text", "")

            if not isinstance(text, str) or not text.strip():
                continue

            yield text

            count += 1
            if limit is not None and count >= limit:
                break


def corpus_sample(limit: int = 1000) -> list[str]:
    """Return a deterministic prefix sample from the production corpus."""
    if limit < 1:
        raise ValueError("limit must be >= 1")

    return list(iter_corpus(limit))


if __name__ == "__main__":
    sample = corpus_sample(10)

    print(f"Corpus: {CORPUS_PATH}")
    print(f"Sample size: {len(sample)}")

    for index, text in enumerate(sample, start=1):
        print(f"{index:02d}: {text}")
