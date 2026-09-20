from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


ALLOWED_REVIEW_STATUSES = {
    "candidate",
    "reviewing",
    "approved",
    "rejected",
    "hold",
}

ALLOWED_PERMISSION_VALUES = {
    "yes",
    "no",
    "unclear",
    "not_applicable",
}

ALLOWED_RISK_LEVELS = {
    "low",
    "medium",
    "high",
    "unknown",
}


@dataclass
class SourceRegistryEntry:
    """
    Canonical provenance and licensing record for a candidate
    OromoCorpus source.

    A source must be registered before ingestion into a future
    production OromoCorpus release.
    """

    source_id: str
    source_name: str

    owner_or_publisher: str
    source_url: str
    acquisition_method: str

    acquired_at: str = field(
        default_factory=lambda: datetime.now(
            timezone.utc
        ).isoformat()
    )

    license: str = ""

    training_permission: str = "unclear"
    redistribution_permission: str = "unclear"

    attribution_requirements: str = ""

    domain: str = ""
    dialect_or_region_if_known: str = ""

    language_risk: str = "unknown"
    pii_or_sensitive_data_risk: str = "unknown"

    raw_artifact_hash: str = ""

    review_status: str = "candidate"

    notes: str = ""

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def validate(self) -> None:
        """
        Validate registry invariants.

        Validation is intentionally strict for provenance fields
        and conservative for uncertain legal/licensing fields.
        """

        if not self.source_id.strip():
            raise ValueError(
                "source_id is required"
            )

        if not self.source_name.strip():
            raise ValueError(
                "source_name is required"
            )

        if not self.owner_or_publisher.strip():
            raise ValueError(
                "owner_or_publisher is required"
            )

        if not self.source_url.strip():
            raise ValueError(
                "source_url is required"
            )

        if not self.acquisition_method.strip():
            raise ValueError(
                "acquisition_method is required"
            )

        if self.training_permission not in (
            ALLOWED_PERMISSION_VALUES
        ):
            raise ValueError(
                "training_permission must be one of: "
                + ", ".join(
                    sorted(
                        ALLOWED_PERMISSION_VALUES
                    )
                )
            )

        if self.redistribution_permission not in (
            ALLOWED_PERMISSION_VALUES
        ):
            raise ValueError(
                "redistribution_permission must be one of: "
                + ", ".join(
                    sorted(
                        ALLOWED_PERMISSION_VALUES
                    )
                )
            )

        if self.language_risk not in (
            ALLOWED_RISK_LEVELS
        ):
            raise ValueError(
                "language_risk must be one of: "
                + ", ".join(
                    sorted(
                        ALLOWED_RISK_LEVELS
                    )
                )
            )

        if self.pii_or_sensitive_data_risk not in (
            ALLOWED_RISK_LEVELS
        ):
            raise ValueError(
                "pii_or_sensitive_data_risk must be one of: "
                + ", ".join(
                    sorted(
                        ALLOWED_RISK_LEVELS
                    )
                )
            )

        if self.review_status not in (
            ALLOWED_REVIEW_STATUSES
        ):
            raise ValueError(
                "review_status must be one of: "
                + ", ".join(
                    sorted(
                        ALLOWED_REVIEW_STATUSES
                    )
                )
            )

        if (
            self.review_status == "approved"
            and self.training_permission != "yes"
        ):
            raise ValueError(
                "approved sources must have "
                "training_permission='yes'"
            )

        if (
            self.review_status == "approved"
            and not self.license.strip()
        ):
            raise ValueError(
                "approved sources must have a "
                "documented license"
            )

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return asdict(self)

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> SourceRegistryEntry:
        entry = cls(**data)
        entry.validate()
        return entry


def sha256_file(
    path: Path,
) -> str:
    """
    Compute SHA-256 for a local raw source artifact.
    """

    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(
            lambda: handle.read(
                1024 * 1024
            ),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def load_registry(
    path: Path,
) -> list[SourceRegistryEntry]:
    """
    Load and validate a JSONL source registry.
    """

    entries: list[
        SourceRegistryEntry
    ] = []

    if not path.exists():
        return entries

    seen_source_ids: set[str] = set()

    with path.open(
        "r",
        encoding="utf-8",
    ) as handle:
        for line_number, line in enumerate(
            handle,
            start=1,
        ):
            if not line.strip():
                continue

            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"Invalid JSON on registry "
                    f"line {line_number}"
                ) from exc

            entry = (
                SourceRegistryEntry.from_dict(
                    record
                )
            )

            if entry.source_id in seen_source_ids:
                raise ValueError(
                    "Duplicate source_id in registry: "
                    f"{entry.source_id}"
                )

            seen_source_ids.add(
                entry.source_id
            )

            entries.append(entry)

    return entries


def write_registry(
    path: Path,
    entries: Iterable[
        SourceRegistryEntry
    ],
) -> None:
    """
    Write a deterministic JSONL registry.

    Entries are sorted by source_id for stable diffs and
    reproducibility.
    """

    validated_entries = list(
        entries
    )

    seen_source_ids: set[str] = set()

    for entry in validated_entries:
        entry.validate()

        if entry.source_id in seen_source_ids:
            raise ValueError(
                "Duplicate source_id: "
                f"{entry.source_id}"
            )

        seen_source_ids.add(
            entry.source_id
        )

    validated_entries.sort(
        key=lambda item: item.source_id
    )

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with path.open(
        "w",
        encoding="utf-8",
    ) as handle:
        for entry in validated_entries:
            handle.write(
                json.dumps(
                    entry.to_dict(),
                    ensure_ascii=False,
                    sort_keys=True,
                )
                + "\n"
            )


def find_source(
    entries: Iterable[
        SourceRegistryEntry
    ],
    source_id: str,
) -> SourceRegistryEntry | None:
    """
    Find one source by stable source_id.
    """

    for entry in entries:
        if entry.source_id == source_id:
            return entry

    return None


def register_source(
    path: Path,
    entry: SourceRegistryEntry,
) -> None:
    """
    Append a new logical source to the registry while
    preventing source_id collisions.

    The registry is rewritten deterministically.
    """

    entry.validate()

    entries = load_registry(
        path
    )

    existing = find_source(
        entries,
        entry.source_id,
    )

    if existing is not None:
        raise ValueError(
            "source_id already registered: "
            f"{entry.source_id}"
        )

    entries.append(entry)

    write_registry(
        path,
        entries,
    )


def update_source(
    path: Path,
    entry: SourceRegistryEntry,
) -> None:
    """
    Replace an existing source registry entry by source_id.
    """

    entry.validate()

    entries = load_registry(
        path
    )

    replaced = False

    updated_entries: list[
        SourceRegistryEntry
    ] = []

    for existing in entries:
        if (
            existing.source_id
            == entry.source_id
        ):
            updated_entries.append(
                entry
            )
            replaced = True
        else:
            updated_entries.append(
                existing
            )

    if not replaced:
        raise ValueError(
            "Cannot update unregistered source_id: "
            f"{entry.source_id}"
        )

    write_registry(
        path,
        updated_entries,
    )