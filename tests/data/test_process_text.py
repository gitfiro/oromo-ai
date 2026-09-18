from __future__ import annotations

import hashlib
import json
from pathlib import Path

from oromo_ai.data.process_text import process_text_corpus


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_process_text_corpus_is_non_destructive(tmp_path: Path) -> None:
    source = tmp_path / "train.txt"
    output = tmp_path / "processed.jsonl"
    rejected = tmp_path / "rejected.jsonl"
    manifest = tmp_path / "manifest.json"

    source.write_text(
        "Afaan Oromoo barachuun bareeda.\n"
        "[Read More]\n"
        "DNA probe PCR sequencing chromosome nucleotide.\n"
        "Barreeffama Afaan Oromoo qulqulluu.\n",
        encoding="utf-8",
    )

    before_hash = _sha256(source)

    result = process_text_corpus(
        source,
        output,
        rejected,
        manifest,
        source="AfriBERTa Corpus",
        source_id="afriberta_oromo",
        license="Apache-2.0",
        source_url="https://huggingface.co/datasets/castorini/afriberta-corpus",
    )

    after_hash = _sha256(source)

    assert before_hash == after_hash
    assert result["input_records"] == 4
    assert result["output_records"] >= 1
    assert result["rejected_records"] >= 1


def test_cleaned_record_preserves_provenance(tmp_path: Path) -> None:
    source = tmp_path / "train.txt"
    output = tmp_path / "processed.jsonl"
    rejected = tmp_path / "rejected.jsonl"
    manifest = tmp_path / "manifest.json"

    source.write_text(
        "Afaan Oromoo barachuun bareeda. https://example.com\n",
        encoding="utf-8",
    )

    process_text_corpus(
        source,
        output,
        rejected,
        manifest,
        source="AfriBERTa Corpus",
        source_id="afriberta_oromo",
        license="Apache-2.0",
        source_url="https://huggingface.co/datasets/castorini/afriberta-corpus",
    )

    records = [
        json.loads(line)
        for line in output.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    assert len(records) == 1

    record = records[0]

    assert record["language"] == "orm"
    assert record["source"] == "AfriBERTa Corpus"
    assert record["license"] == "Apache-2.0"
    assert record["source_id"] == "afriberta_oromo"
    assert record["metadata"]["source_line"] == 1
    assert record["metadata"]["decision"] == "CLEAN"
    assert "https://example.com" not in record["text"]


def test_rejected_records_are_not_written_to_training_corpus(
    tmp_path: Path,
) -> None:
    source = tmp_path / "train.txt"
    output = tmp_path / "processed.jsonl"
    rejected = tmp_path / "rejected.jsonl"
    manifest = tmp_path / "manifest.json"

    source.write_text(
        "Afaan Oromoo barachuun bareeda.\n"
        "DNA probe PCR sequencing chromosome nucleotide.\n",
        encoding="utf-8",
    )

    process_text_corpus(
        source,
        output,
        rejected,
        manifest,
        source="AfriBERTa Corpus",
        source_id="afriberta_oromo",
        license="Apache-2.0",
    )

    output_text = output.read_text(encoding="utf-8")

    assert "Afaan Oromoo barachuun bareeda." in output_text
    assert "DNA probe PCR sequencing chromosome nucleotide." not in output_text

    rejected_records = [
        json.loads(line)
        for line in rejected.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    assert len(rejected_records) == 1
    assert rejected_records[0]["source_line"] == 2
    assert rejected_records[0]["decision"] == "REJECT"


def test_deduplication_happens_after_cleaning(tmp_path: Path) -> None:
    source = tmp_path / "train.txt"
    output = tmp_path / "processed.jsonl"
    rejected = tmp_path / "rejected.jsonl"
    manifest = tmp_path / "manifest.json"

    source.write_text(
        "Afaan Oromoo barachuun bareeda. https://example.com\n"
        "Afaan Oromoo barachuun bareeda.\n",
        encoding="utf-8",
    )

    result = process_text_corpus(
        source,
        output,
        rejected,
        manifest,
        source="AfriBERTa Corpus",
        source_id="afriberta_oromo",
        license="Apache-2.0",
    )

    records = [
        json.loads(line)
        for line in output.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    assert len(records) == 1
    assert result["duplicates_removed"] == 1
    assert records[0]["metadata"]["source_line"] == 1


def test_empty_after_cleaning_is_rejected(tmp_path: Path) -> None:
    source = tmp_path / "train.txt"
    output = tmp_path / "processed.jsonl"
    rejected = tmp_path / "rejected.jsonl"
    manifest = tmp_path / "manifest.json"

    source.write_text(
        "[Read More] https://example.com\n"
        "Afaan Oromoo barachuun bareeda.\n",
        encoding="utf-8",
    )

    result = process_text_corpus(
        source,
        output,
        rejected,
        manifest,
        source="AfriBERTa Corpus",
        source_id="afriberta_oromo",
        license="Apache-2.0",
    )

    assert result["empty_after_cleaning"] == 1
    assert result["output_records"] == 1
    assert result["rejected_records"] == 1


def test_manifest_contains_processing_statistics(tmp_path: Path) -> None:
    source = tmp_path / "train.txt"
    output = tmp_path / "processed.jsonl"
    rejected = tmp_path / "rejected.jsonl"
    manifest = tmp_path / "manifest.json"

    source.write_text(
        "Afaan Oromoo barachuun bareeda.\n"
        "Afaan Oromoo barachuun bareeda.\n",
        encoding="utf-8",
    )

    result = process_text_corpus(
        source,
        output,
        rejected,
        manifest,
        source="AfriBERTa Corpus",
        source_id="afriberta_oromo",
        license="Apache-2.0",
    )

    data = json.loads(manifest.read_text(encoding="utf-8"))

    assert data["record_count"] == 1
    assert data["metadata"]["input_record_count"] == 2
    assert data["metadata"]["output_record_count"] == 1
    assert data["metadata"]["duplicates_removed"] == 1
    assert result["duplicates_removed"] == 1
