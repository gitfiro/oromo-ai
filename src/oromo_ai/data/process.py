from __future__ import annotations

from pathlib import Path

from .deduplicate import deduplicate_records
from .ingest import records_from_jsonl, write_jsonl
from .manifest import build_manifest, write_manifest


def process_jsonl_dataset(
    input_path: str | Path,
    output_path: str | Path,
    manifest_path: str | Path,
    *,
    name: str,
    version: str,
    source: str,
    license: str,
    source_url: str = "",
    description: str = "",
) -> dict[str, int]:
    """
    Process a JSONL dataset through the canonical Oromo data pipeline.

    Pipeline:
        source JSONL
          -> canonical records
          -> validation
          -> deduplication
          -> processed JSONL
          -> provenance manifest
    """

    records = list(
        records_from_jsonl(
            input_path,
            source=source,
            license=license,
            source_url=source_url,
        )
    )

    input_count = len(records)

    unique_records, duplicate_count = deduplicate_records(records)

    output_count = write_jsonl(
        unique_records,
        output_path,
    )

    manifest = build_manifest(
        unique_records,
        name=name,
        version=version,
        description=description,
        license=license,
        source=source,
        source_url=source_url,
    )

    manifest.metadata["input_record_count"] = input_count
    manifest.metadata["output_record_count"] = output_count
    manifest.metadata["duplicates_removed"] = duplicate_count

    write_manifest(manifest, manifest_path)

    return {
        "input_records": input_count,
        "output_records": output_count,
        "duplicates_removed": duplicate_count,
    }
