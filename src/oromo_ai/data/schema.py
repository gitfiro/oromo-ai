from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class DocumentRecord:
    """
    Canonical representation of a single Oromo text record.

    This schema is intentionally provenance-first. Every training example
    must remain traceable to its original source.
    """

    text: str

    language: str = "orm"
    source: str = ""
    source_url: str = ""
    license: str = ""
    author: str = ""
    title: str = ""

    domain: str = ""
    dialect: str = ""
    country: str = "ET"

    source_id: str = ""
    record_id: str = ""

    collected_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    quality_score: float | None = None

    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        """Validate required fields and basic constraints."""

        if not self.text.strip():
            raise ValueError("text cannot be empty")

        if self.language != "orm":
            raise ValueError(
                f"Expected Afaan Oromoo ISO 639-3 code 'orm', "
                f"got '{self.language}'"
            )

        if not self.source:
            raise ValueError("source is required")

        if not self.license:
            raise ValueError("license is required")

        if self.quality_score is not None:
            if not 0 <= self.quality_score <= 1:
                raise ValueError("quality_score must be between 0 and 1")

    def to_dict(self) -> dict[str, Any]:
        """Convert the record to a serializable dictionary."""

        return {
            "text": self.text,
            "language": self.language,
            "source": self.source,
            "source_url": self.source_url,
            "license": self.license,
            "author": self.author,
            "title": self.title,
            "domain": self.domain,
            "dialect": self.dialect,
            "country": self.country,
            "source_id": self.source_id,
            "record_id": self.record_id,
            "collected_at": self.collected_at,
            "quality_score": self.quality_score,
            "metadata": self.metadata,
        }


@dataclass
class DatasetManifest:
    """
    Dataset-level provenance and processing manifest.
    """

    name: str
    version: str
    description: str = ""

    language: str = "orm"

    license: str = ""
    source: str = ""
    source_url: str = ""

    record_count: int = 0
    total_characters: int = 0
    total_tokens: int | None = None

    processing_version: str = "0.1.0"

    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        """Validate the dataset manifest."""

        if not self.name.strip():
            raise ValueError("dataset name is required")

        if not self.version.strip():
            raise ValueError("dataset version is required")

        if self.language != "orm":
            raise ValueError(
                f"Expected Afaan Oromoo ISO 639-3 code 'orm', "
                f"got '{self.language}'"
            )

        if self.record_count < 0:
            raise ValueError("record_count cannot be negative")

        if self.total_characters < 0:
            raise ValueError("total_characters cannot be negative")

    def to_dict(self) -> dict[str, Any]:
        """Convert the manifest to a serializable dictionary."""

        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "language": self.language,
            "license": self.license,
            "source": self.source,
            "source_url": self.source_url,
            "record_count": self.record_count,
            "total_characters": self.total_characters,
            "total_tokens": self.total_tokens,
            "processing_version": self.processing_version,
            "created_at": self.created_at,
            "metadata": self.metadata,
        }
