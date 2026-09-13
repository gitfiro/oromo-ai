from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from .schema import DocumentRecord


def read_jsonl(path: str | Path) -> Iterable[dict]:
    """Read JSON Lines records from a UTF-8 file."""
    path = Path(path)

    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            line = line.strip()

            if not line:
                continue

            try:
                yield json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"Invalid JSON on line {line_number} of {path}"
                ) from exc


def records_from_jsonl(
    path: str | Path,
    *,
    source: str,
    license: str,
    source_url: str = "",
) -> Iterable[DocumentRecord]:
    """
    Convert a JSONL source into canonical DocumentRecord objects.

    The input must contain a 'text' field. Existing provenance metadata
    is preserved where available.
    """
    for raw in read_jsonl(path):
        text = raw.get("text")

        if not isinstance(text, str):
            raise ValueError("Every JSONL record must contain a string 'text' field")

        record = DocumentRecord(
            text=text,
            language=raw.get("language", "orm"),
            source=raw.get("source", source),
            source_url=raw.get("source_url", source_url),
            license=raw.get("license", license),
            author=raw.get("author", ""),
            title=raw.get("title", ""),
            domain=raw.get("domain", ""),
            dialect=raw.get("dialect", ""),
            country=raw.get("country", "ET"),
            source_id=raw.get("source_id", ""),
            record_id=raw.get("record_id", ""),
            quality_score=raw.get("quality_score"),
            metadata=raw.get("metadata", {}),
        )

        record.validate()
        yield record


def write_jsonl(
    records: Iterable[DocumentRecord],
    path: str | Path,
) -> int:
    """Write canonical DocumentRecord objects to JSONL."""

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    count = 0

    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            record.validate()
            handle.write(
                json.dumps(
                    record.to_dict(),
                    ensure_ascii=False,
                )
                + "\n"
            )
            count += 1

    return count
