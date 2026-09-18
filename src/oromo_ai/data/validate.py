"""Validation helpers for processed Afaan Oromoo corpus records."""

from __future__ import annotations

from .audit import looks_like_repetition_artifact
from .schema import DocumentRecord


def validate_processed_record(record: DocumentRecord) -> tuple[bool, str]:
    """
    Validate a record after cleaning.

    Returns:
        (is_valid, reason)

    Validation is intentionally conservative. Repetition signals are
    diagnostic and do not automatically invalidate a record.
    """

    if not isinstance(record, DocumentRecord):
        raise TypeError("record must be a DocumentRecord")

    text = record.text.strip()

    # Check the post-cleaning state first so the pipeline can distinguish
    # an intentionally removed artifact-only record from other validation
    # failures.
    if not text:
        return False, "empty_after_cleaning"

    try:
        record.validate()
    except ValueError as exc:
        return False, str(exc)

    if looks_like_repetition_artifact(text):
        return True, "repetition_signal_review_only"

    return True, "valid"
