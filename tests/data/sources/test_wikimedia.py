from __future__ import annotations

import bz2
from pathlib import Path

from oromo_ai.data.sources.wikimedia import (
    WikimediaExtractionStats,
    extract_wikimedia_dump,
    iter_wikimedia_records,
)


SAMPLE_XML = """<?xml version="1.0" encoding="UTF-8"?>
<mediawiki
    xmlns="http://www.mediawiki.org/xml/export-0.11/"
    version="0.11"
    xml:lang="om">
  <page>
    <title>Afaan Oromoo</title>
    <ns>0</ns>
    <id>10</id>
    <revision>
      <id>100</id>
      <timestamp>2026-09-01T00:00:00Z</timestamp>
      <text xml:space="preserve">Afaan Oromoo afaan uummata Oromoo ti.</text>
    </revision>
  </page>

  <page>
    <title>Talk:Afaan Oromoo</title>
    <ns>1</ns>
    <id>11</id>
    <revision>
      <id>101</id>
      <timestamp>2026-09-01T00:00:00Z</timestamp>
      <text xml:space="preserve">Talk content</text>
    </revision>
  </page>

  <page>
    <title>Oromiffa</title>
    <ns>0</ns>
    <id>12</id>
    <redirect title="Afaan Oromoo" />
    <revision>
      <id>102</id>
      <timestamp>2026-09-01T00:00:00Z</timestamp>
      <text xml:space="preserve">#REDIRECT [[Afaan Oromoo]]</text>
    </revision>
  </page>

  <page>
    <title>Qubee Afaan Oromoo</title>
    <ns>0</ns>
    <id>13</id>
    <revision>
      <id>103</id>
      <timestamp>2026-09-02T00:00:00Z</timestamp>
      <text xml:space="preserve">Qubeen Afaan Oromoo qubee Laatiin fayyadama.</text>
    </revision>
  </page>
</mediawiki>
"""


def write_sample_dump(
    path: Path,
) -> None:
    with bz2.open(path, "wt", encoding="utf-8") as f:
        f.write(SAMPLE_XML)


def test_iter_wikimedia_records(
    tmp_path: Path,
) -> None:
    dump = tmp_path / "sample.xml.bz2"
    write_sample_dump(dump)

    stats = WikimediaExtractionStats()

    records = list(
        iter_wikimedia_records(
            dump,
            stats=stats,
        )
    )

    assert len(records) == 2

    assert records[0].title == "Afaan Oromoo"
    assert records[0].language == "orm"
    assert records[0].source_id == "wikimedia-omwiki"

    assert (
        records[0].metadata["page_id"]
        == "10"
    )

    assert (
        records[0].metadata["revision_id"]
        == "100"
    )

    assert (
        records[0].metadata["namespace"]
        == 0
    )

    assert stats.pages_seen == 4
    assert stats.namespace_zero_pages == 3
    assert stats.redirects_skipped == 1
    assert stats.records_emitted == 2


def test_redirects_can_be_included(
    tmp_path: Path,
) -> None:
    dump = tmp_path / "sample.xml.bz2"
    write_sample_dump(dump)

    records = list(
        iter_wikimedia_records(
            dump,
            include_redirects=True,
        )
    )

    assert len(records) == 3

    redirect = next(
        record
        for record in records
        if record.title == "Oromiffa"
    )

    assert redirect.metadata["redirect"] is True

    assert (
        redirect.metadata["redirect_target"]
        == "Afaan Oromoo"
    )


def test_record_ids_are_deterministic(
    tmp_path: Path,
) -> None:
    dump = tmp_path / "sample.xml.bz2"
    write_sample_dump(dump)

    first = list(
        iter_wikimedia_records(dump)
    )

    second = list(
        iter_wikimedia_records(dump)
    )

    assert [
        record.record_id
        for record in first
    ] == [
        record.record_id
        for record in second
    ]


def test_article_urls_are_preserved(
    tmp_path: Path,
) -> None:
    dump = tmp_path / "sample.xml.bz2"
    write_sample_dump(dump)

    records = list(
        iter_wikimedia_records(dump)
    )

    record = records[0]

    assert record.source_url.startswith(
        "https://om.wikipedia.org/wiki/"
    )

    assert (
        record.metadata["revision_url"]
        == "https://om.wikipedia.org/"
        "w/index.php?oldid=100"
    )


def test_extract_wikimedia_dump(
    tmp_path: Path,
) -> None:
    dump = tmp_path / "sample.xml.bz2"
    output = tmp_path / "output.jsonl"

    write_sample_dump(dump)

    stats = extract_wikimedia_dump(
        dump,
        output,
    )

    assert output.exists()

    lines = output.read_text(
        encoding="utf-8"
    ).splitlines()

    assert len(lines) == 2
    assert stats.records_emitted == 2