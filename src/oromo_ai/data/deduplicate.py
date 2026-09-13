from __future__ import annotations

import hashlib
import re
import unicodedata

from .schema import DocumentRecord


_WHITESPACE_RE = re.compile(r"\s+")


def normalize_for_hash(text: str) -> str:
    """
    Normalize text for deterministic duplicate detection.

    This normalization is deliberately conservative:
    - Unicode normalization
    - whitespace collapsing
    - leading/trailing whitespace removal

    It does NOT lowercase or remove punctuation because those operations
    could erase meaningful distinctions in Afaan Oromoo.
    """
    text = unicodedata.normalize("NFC", text)
    text = _WHITESPACE_RE.sub(" ", text)
    return text.strip()


def text_hash(text: str) -> str:
    """Return a deterministic SHA-256 hash of normalized text."""
    normalized = normalize_for_hash(text)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def record_hash(record: DocumentRecord) -> str:
    """Return the deterministic identity hash for a document record."""
    return text_hash(record.text)


def deduplicate_records(
    records: list[DocumentRecord],
) -> tuple[list[DocumentRecord], int]:
    """
    Remove duplicate records based on normalized text.

    Returns:
        (unique_records, duplicate_count)
    """
    seen: set[str] = set()
    unique: list[DocumentRecord] = []
    duplicates = 0

    for record in records:
        digest = record_hash(record)

        if digest in seen:
            duplicates += 1
            continue

        seen.add(digest)
        unique.append(record)

    return unique, duplicates
