from __future__ import annotations

import bz2
import hashlib
import json
import xml.etree.ElementTree as ET

from dataclasses import dataclass
from pathlib import Path
from typing import Iterator
from urllib.parse import quote

from oromo_ai.data.schema import DocumentRecord


SOURCE_ID = "wikimedia-omwiki"
SOURCE_NAME = "Afaan Oromoo Wikipedia"
LICENSE = "CC-BY-SA-4.0"
BASE_URL = "https://om.wikipedia.org/wiki/"
REVISION_BASE_URL = "https://om.wikipedia.org/w/index.php?oldid="


@dataclass
class WikimediaExtractionStats:
    pages_seen: int = 0
    namespace_zero_pages: int = 0
    redirects_skipped: int = 0
    empty_text_skipped: int = 0
    records_emitted: int = 0

    def to_dict(self) -> dict[str, int]:
        return {
            "pages_seen": self.pages_seen,
            "namespace_zero_pages": self.namespace_zero_pages,
            "redirects_skipped": self.redirects_skipped,
            "empty_text_skipped": self.empty_text_skipped,
            "records_emitted": self.records_emitted,
        }


def _local_name(tag: str) -> str:
    """Return an XML tag without its namespace prefix."""
    if "}" in tag:
        return tag.rsplit("}", 1)[1]
    return tag


def _child_text(
    element: ET.Element,
    child_name: str,
) -> str:
    """Return direct-child text by local XML tag name."""
    for child in element:
        if _local_name(child.tag) == child_name:
            return child.text or ""
    return ""


def _child(
    element: ET.Element,
    child_name: str,
) -> ET.Element | None:
    """Return a direct child by local XML tag name."""
    for child in element:
        if _local_name(child.tag) == child_name:
            return child
    return None


def _article_url(title: str) -> str:
    normalized = title.replace(" ", "_")
    return BASE_URL + quote(normalized, safe="()/:")


def _record_id(
    page_id: str,
    revision_id: str,
) -> str:
    raw = f"{SOURCE_ID}:{page_id}:{revision_id}"
    digest = hashlib.sha256(
        raw.encode("utf-8")
    ).hexdigest()

    return f"omwiki-{digest[:24]}"


def iter_wikimedia_records(
    dump_path: Path,
    *,
    include_redirects: bool = False,
    stats: WikimediaExtractionStats | None = None,
) -> Iterator[DocumentRecord]:
    """
    Stream namespace-0 articles from an Oromo Wikipedia XML dump.

    This is an extraction stage, not a cleaning stage. Article text is
    emitted as raw MediaWiki wikitext so later processing remains
    reproducible and auditable.
    """

    if stats is None:
        stats = WikimediaExtractionStats()

    with bz2.open(dump_path, "rb") as stream:
        context = ET.iterparse(
            stream,
            events=("end",),
        )

        for _, elem in context:
            if _local_name(elem.tag) != "page":
                continue

            stats.pages_seen += 1

            title = _child_text(elem, "title")
            namespace = _child_text(elem, "ns")
            page_id = _child_text(elem, "id")

            if namespace != "0":
                elem.clear()
                continue

            stats.namespace_zero_pages += 1

            redirect = _child(elem, "redirect")

            if redirect is not None and not include_redirects:
                stats.redirects_skipped += 1
                elem.clear()
                continue

            revision = _child(elem, "revision")

            if revision is None:
                stats.empty_text_skipped += 1
                elem.clear()
                continue

            revision_id = _child_text(
                revision,
                "id",
            )

            revision_timestamp = _child_text(
                revision,
                "timestamp",
            )

            text = _child_text(
                revision,
                "text",
            )

            if not text.strip():
                stats.empty_text_skipped += 1
                elem.clear()
                continue

            redirect_target = ""

            if redirect is not None:
                redirect_target = (
                    redirect.attrib.get("title", "")
                )

            page_url = _article_url(title)

            revision_url = ""
            if revision_id:
                revision_url = (
                    REVISION_BASE_URL
                    + quote(revision_id, safe="")
                )

            record = DocumentRecord(
                text=text,
                language="orm",
                source=SOURCE_NAME,
                source_url=page_url,
                license=LICENSE,
                title=title,
                domain="encyclopedia_reference",
                country="ET",
                source_id=SOURCE_ID,
                record_id=_record_id(
                    page_id,
                    revision_id,
                ),
                metadata={
                    "page_id": page_id,
                    "revision_id": revision_id,
                    "revision_timestamp": (
                        revision_timestamp
                    ),
                    "revision_url": revision_url,
                    "namespace": 0,
                    "redirect": redirect is not None,
                    "redirect_target": redirect_target,
                    "wiki_code": "omwiki",
                    "wikimedia_language_code": "om",
                    "text_format": "mediawiki_wikitext",
                },
            )

            record.validate()

            stats.records_emitted += 1
            yield record

            elem.clear()


def extract_wikimedia_dump(
    dump_path: Path,
    output_path: Path,
    *,
    include_redirects: bool = False,
) -> WikimediaExtractionStats:
    """
    Extract an Oromo Wikipedia dump into provenance-preserving JSONL.
    """

    stats = WikimediaExtractionStats()

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output_path.open(
        "w",
        encoding="utf-8",
        newline="\n",
    ) as out:
        for record in iter_wikimedia_records(
            dump_path,
            include_redirects=include_redirects,
            stats=stats,
        ):
            out.write(
                json.dumps(
                    record.to_dict(),
                    ensure_ascii=False,
                    sort_keys=True,
                )
            )
            out.write("\n")

    return stats