from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from .deduplicate import record_hash
from .schema import DatasetManifest, DocumentRecord


def build_manifest(
    records: Iterable[DocumentRecord],
    *,
    name: str,
    version: str,
    description: str = "",
    license: str = "",
    source: str = "",
    source_url: str = "",
) -> DatasetManifest:
    """Build a dataset manifest from canonical records."""

    record_list = list(records)

    for record in record_list:
        record.validate()

    manifest = DatasetManifest(
        name=name,
        version=version,
        description=description,
        license=license,
        source=source,
        source_url=source_url,
        record_count=len(record_list),
        total_characters=sum(len(record.text) for record in record_list),
        metadata={
            "unique_record_hashes": len(
                {record_hash(record) for record in record_list}
            ),
        },
    )

    manifest.validate()
    return manifest


def write_manifest(
    manifest: DatasetManifest,
    path: str | Path,
) -> None:
    """Write a dataset manifest as UTF-8 JSON."""

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    manifest.validate()

    path.write_text(
        json.dumps(
            manifest.to_dict(),
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
