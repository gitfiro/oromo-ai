"""Streaming production processor for line-oriented Afaan Oromoo corpora."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .clean import clean_text
from .decide import decide_record
from .deduplicate import text_hash
from .manifest import write_manifest
from .schema import DatasetManifest, DocumentRecord
from .validate import validate_processed_record


PROCESSING_VERSION = "0.1.0"


def _sha256_file(path: Path) -> str:
    """Return the SHA-256 checksum of a file."""
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


def _record_id(source_id: str, line_number: int) -> str:
    """Create a deterministic source-record identifier."""
    return f"{source_id}:line:{line_number}"


def _write_jsonl_record(handle: Any, record: dict[str, Any]) -> None:
    """Write one UTF-8 JSONL record."""
    handle.write(
        json.dumps(
            record,
            ensure_ascii=False,
            sort_keys=True,
        )
        + "\n"
    )


def process_text_corpus(
    input_path: str | Path,
    output_path: str | Path,
    rejected_path: str | Path,
    manifest_path: str | Path,
    *,
    source: str,
    source_id: str,
    license: str,
    source_url: str = "",
    description: str = "",
) -> dict[str, int]:
    """
    Process a line-oriented Afaan Oromoo corpus.

    Pipeline:

        raw line
          -> decision
          -> clean if required
          -> validate
          -> deduplicate cleaned text
          -> processed JSONL

    Rejected records are written separately and never enter the training
    corpus. The input file is opened read-only and is never modified.
    """

    input_path = Path(input_path)
    output_path = Path(output_path)
    rejected_path = Path(rejected_path)
    manifest_path = Path(manifest_path)

    if not input_path.is_file():
        raise FileNotFoundError(f"Input corpus not found: {input_path}")

    if not source.strip():
        raise ValueError("source is required")

    if not source_id.strip():
        raise ValueError("source_id is required")

    if not license.strip():
        raise ValueError("license is required")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    rejected_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)

    source_sha256 = _sha256_file(input_path)

    input_records = 0
    output_records = 0
    rejected_records = 0
    clean_decisions = 0
    changed_records = 0
    empty_after_cleaning = 0
    duplicates_removed = 0

    input_characters = 0
    output_characters = 0

    decision_counts = {
        "KEEP": 0,
        "CLEAN": 0,
        "REJECT": 0,
    }

    rejection_reasons: dict[str, int] = {}

    seen_hashes: set[str] = set()

    with (
        input_path.open("r", encoding="utf-8", newline="") as source_handle,
        output_path.open("w", encoding="utf-8") as output_handle,
        rejected_path.open("w", encoding="utf-8") as rejected_handle,
    ):
        for line_number, raw_line in enumerate(source_handle, start=1):
            if raw_line.endswith("\n"):
                original = raw_line[:-1]

                if original.endswith("\r"):
                    original = original[:-1]
            else:
                original = raw_line

            input_records += 1
            input_characters += len(original)

            decision, reasons = decide_record(original)
            decision_counts[decision] += 1

            if decision == "REJECT":
                rejected_records += 1

                for reason in reasons:
                    rejection_reasons[reason] = (
                        rejection_reasons.get(reason, 0) + 1
                    )

                _write_jsonl_record(
                    rejected_handle,
                    {
                        "source": source,
                        "source_id": source_id,
                        "source_line": line_number,
                        "record_id": _record_id(source_id, line_number),
                        "decision": "REJECT",
                        "reasons": reasons,
                        "text_hash": text_hash(original),
                    },
                )

                continue

            if decision == "CLEAN":
                clean_decisions += 1
                cleaned = clean_text(original)

                if cleaned != original:
                    changed_records += 1
            else:
                cleaned = original

            validation_record = DocumentRecord(
                text=cleaned,
                language="orm",
                source=source,
                source_url=source_url,
                license=license,
                country="ET",
                source_id=source_id,
                record_id=_record_id(source_id, line_number),
                metadata={
                    "source_line": line_number,
                    "decision": decision,
                },
            )

            is_valid, validation_reason = validate_processed_record(
                validation_record
            )

            if not is_valid:
                rejected_records += 1

                if validation_reason == "empty_after_cleaning":
                    empty_after_cleaning += 1

                rejection_reasons[validation_reason] = (
                    rejection_reasons.get(validation_reason, 0) + 1
                )

                _write_jsonl_record(
                    rejected_handle,
                    {
                        "source": source,
                        "source_id": source_id,
                        "source_line": line_number,
                        "record_id": _record_id(source_id, line_number),
                        "decision": "REJECT",
                        "reasons": [validation_reason],
                        "original_decision": decision,
                        "text_hash": text_hash(original),
                    },
                )

                continue

            cleaned_hash = text_hash(cleaned)

            if cleaned_hash in seen_hashes:
                duplicates_removed += 1

                _write_jsonl_record(
                    rejected_handle,
                    {
                        "source": source,
                        "source_id": source_id,
                        "source_line": line_number,
                        "record_id": _record_id(source_id, line_number),
                        "decision": "REJECT",
                        "reasons": ["duplicate_after_cleaning"],
                        "original_decision": decision,
                        "text_hash": text_hash(original),
                        "cleaned_text_hash": cleaned_hash,
                    },
                )

                continue

            seen_hashes.add(cleaned_hash)

            record = DocumentRecord(
                text=cleaned,
                language="orm",
                source=source,
                source_url=source_url,
                license=license,
                country="ET",
                source_id=source_id,
                record_id=_record_id(source_id, line_number),
                metadata={
                    "source_line": line_number,
                    "decision": decision,
                    "original_text_hash": text_hash(original),
                    "cleaned_text_hash": cleaned_hash,
                    "processing_version": PROCESSING_VERSION,
                },
            )

            record.validate()

            _write_jsonl_record(
                output_handle,
                record.to_dict(),
            )

            output_records += 1
            output_characters += len(cleaned)

    manifest = DatasetManifest(
        name="afriberta_oromo_processed",
        version=PROCESSING_VERSION,
        description=description,
        language="orm",
        license=license,
        source=source,
        source_url=source_url,
        record_count=output_records,
        total_characters=output_characters,
        processing_version=PROCESSING_VERSION,
        metadata={
            "input_record_count": input_records,
            "output_record_count": output_records,
            "rejected_record_count": rejected_records,
            "clean_decisions": clean_decisions,
            "changed_records": changed_records,
            "empty_after_cleaning": empty_after_cleaning,
            "duplicates_removed": duplicates_removed,
            "input_characters": input_characters,
            "output_characters": output_characters,
            "source_path": str(input_path),
            "source_sha256": source_sha256,
            "source_id": source_id,
            "processing_version": PROCESSING_VERSION,
            "decision_counts": decision_counts,
            "rejection_reasons": rejection_reasons,
            "raw_source_modified": False,
            "unique_cleaned_text_hashes": len(seen_hashes),
        },
    )

    manifest.validate()
    write_manifest(manifest, manifest_path)

    return {
        "input_records": input_records,
        "output_records": output_records,
        "rejected_records": rejected_records,
        "clean_decisions": clean_decisions,
        "changed_records": changed_records,
        "empty_after_cleaning": empty_after_cleaning,
        "duplicates_removed": duplicates_removed,
    }
