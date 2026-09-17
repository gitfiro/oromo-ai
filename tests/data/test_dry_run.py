from __future__ import annotations

import hashlib
import json
from pathlib import Path

from oromo_ai.data.dry_run import (
    dry_run_text_corpus,
    write_dry_run_report,
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_dry_run_is_non_destructive(tmp_path: Path) -> None:
    source = tmp_path / "source.txt"

    source.write_text(
        "Afaan Oromoo barachuun barbaachisaa dha.\n"
        "[Read More]\n"
        "DNA probe PCR sequencing chromosome nucleotide.\n"
        "Barreeffama Afaan Oromoo qulqulluu.\n",
        encoding="utf-8",
    )

    before_hash = _sha256(source)

    report = dry_run_text_corpus(
        source,
        max_examples_per_category=5,
    )

    after_hash = _sha256(source)

    assert before_hash == after_hash
    assert report["non_destructive"] is True
    assert report["source_modified"] is False
    assert report["output_corpus_written"] is False
    assert report["input_records"] == 4


def test_dry_run_reports_decisions_and_cleaning_impact(tmp_path: Path) -> None:
    source = tmp_path / "source.txt"

    source.write_text(
        "Afaan Oromoo barachuun bareeda.\n"
        "[Read More]\n"
        "https://example.com\n"
        "DNA probe PCR sequencing chromosome nucleotide.\n",
        encoding="utf-8",
    )

    report = dry_run_text_corpus(
        source,
        max_examples_per_category=5,
    )

    assert sum(report["decision_counts"].values()) == 4
    assert report["decision_counts"]["KEEP"] >= 1
    assert report["decision_counts"]["REJECT"] >= 1
    assert report["changed_records"] >= 1
    assert report["empty_after_cleaning"] >= 1


def test_dry_run_report_round_trip(tmp_path: Path) -> None:
    source = tmp_path / "source.txt"
    report_path = tmp_path / "report.json"

    source.write_text(
        "Afaan Oromoo jechuun afaan saba Oromoo ti.\n"
        "[Read More]\n",
        encoding="utf-8",
    )

    report = dry_run_text_corpus(source)
    write_dry_run_report(report, report_path)

    loaded = json.loads(report_path.read_text(encoding="utf-8"))

    assert loaded["dry_run_version"] == report["dry_run_version"]
    assert loaded["input_records"] == report["input_records"]
    assert loaded["decision_counts"] == report["decision_counts"]
    assert loaded["changed_records"] == report["changed_records"]
    assert loaded["non_destructive"] is True


def test_dry_run_detects_empty_after_cleaning(tmp_path: Path) -> None:
    source = tmp_path / "source.txt"

    source.write_text(
        "[Read More]\n"
        "[embedyt]\n"
        "https://example.com\n",
        encoding="utf-8",
    )

    report = dry_run_text_corpus(source)

    assert report["input_records"] == 3
    assert report["empty_after_cleaning"] >= 1
