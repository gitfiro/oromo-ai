from __future__ import annotations

import json
from pathlib import Path

import pytest

from oromo_ai.data.source_registry import (
    SourceRegistryEntry,
    find_source,
    load_registry,
    register_source,
    sha256_file,
    update_source,
    write_registry,
)


def make_entry(
    source_id: str = "example-source",
) -> SourceRegistryEntry:
    return SourceRegistryEntry(
        source_id=source_id,
        source_name="Example Oromo Source",
        owner_or_publisher="Example Publisher",
        source_url=(
            "https://example.org/oromo"
        ),
        acquisition_method="direct_download",
        license="CC-BY-4.0",
        training_permission="yes",
        redistribution_permission="yes",
        attribution_requirements=(
            "Attribution required"
        ),
        domain="general",
        dialect_or_region_if_known="",
        language_risk="low",
        pii_or_sensitive_data_risk="low",
        raw_artifact_hash=(
            "a" * 64
        ),
        review_status="approved",
    )


def test_valid_source_entry() -> None:
    entry = make_entry()

    entry.validate()

    assert (
        entry.source_id
        == "example-source"
    )


def test_approved_requires_training_permission() -> None:
    entry = make_entry()

    entry.training_permission = "no"

    with pytest.raises(
        ValueError,
        match="training_permission",
    ):
        entry.validate()


def test_approved_requires_license() -> None:
    entry = make_entry()

    entry.license = ""

    with pytest.raises(
        ValueError,
        match="documented license",
    ):
        entry.validate()


def test_invalid_review_status() -> None:
    entry = make_entry()

    entry.review_status = "maybe"

    with pytest.raises(
        ValueError,
        match="review_status",
    ):
        entry.validate()


def test_write_and_load_registry(
    tmp_path: Path,
) -> None:
    path = (
        tmp_path
        / "registry.jsonl"
    )

    entries = [
        make_entry("source-b"),
        make_entry("source-a"),
    ]

    write_registry(
        path,
        entries,
    )

    loaded = load_registry(
        path
    )

    assert [
        entry.source_id
        for entry in loaded
    ] == [
        "source-a",
        "source-b",
    ]


def test_duplicate_source_id_rejected(
    tmp_path: Path,
) -> None:
    path = (
        tmp_path
        / "registry.jsonl"
    )

    with pytest.raises(
        ValueError,
        match="Duplicate source_id",
    ):
        write_registry(
            path,
            [
                make_entry(
                    "duplicate"
                ),
                make_entry(
                    "duplicate"
                ),
            ],
        )


def test_register_source(
    tmp_path: Path,
) -> None:
    path = (
        tmp_path
        / "registry.jsonl"
    )

    register_source(
        path,
        make_entry(
            "source-a"
        ),
    )

    loaded = load_registry(
        path
    )

    assert len(loaded) == 1

    assert (
        loaded[0].source_id
        == "source-a"
    )


def test_register_duplicate_rejected(
    tmp_path: Path,
) -> None:
    path = (
        tmp_path
        / "registry.jsonl"
    )

    entry = make_entry(
        "source-a"
    )

    register_source(
        path,
        entry,
    )

    with pytest.raises(
        ValueError,
        match="already registered",
    ):
        register_source(
            path,
            entry,
        )


def test_update_source(
    tmp_path: Path,
) -> None:
    path = (
        tmp_path
        / "registry.jsonl"
    )

    original = make_entry(
        "source-a"
    )

    register_source(
        path,
        original,
    )

    updated = make_entry(
        "source-a"
    )

    updated.domain = "education"

    update_source(
        path,
        updated,
    )

    loaded = load_registry(
        path
    )

    assert (
        loaded[0].domain
        == "education"
    )


def test_find_source() -> None:
    entries = [
        make_entry(
            "source-a"
        ),
        make_entry(
            "source-b"
        ),
    ]

    result = find_source(
        entries,
        "source-b",
    )

    assert result is not None

    assert (
        result.source_id
        == "source-b"
    )


def test_sha256_file(
    tmp_path: Path,
) -> None:
    path = (
        tmp_path
        / "sample.txt"
    )

    path.write_text(
        "Oromo AI",
        encoding="utf-8",
    )

    digest = sha256_file(
        path
    )

    assert len(digest) == 64


def test_load_invalid_json(
    tmp_path: Path,
) -> None:
    path = (
        tmp_path
        / "registry.jsonl"
    )

    path.write_text(
        "{invalid json}\n",
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="Invalid JSON",
    ):
        load_registry(
            path
        )


def test_registry_json_is_valid(
    tmp_path: Path,
) -> None:
    path = (
        tmp_path
        / "registry.jsonl"
    )

    write_registry(
        path,
        [
            make_entry(
                "source-a"
            )
        ],
    )

    line = (
        path.read_text(
            encoding="utf-8"
        )
        .strip()
    )

    parsed = json.loads(
        line
    )

    assert (
        parsed["source_id"]
        == "source-a"
    )