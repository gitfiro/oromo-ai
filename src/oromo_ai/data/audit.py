"""Audit raw Oromo corpus quality without modifying source data."""

from __future__ import annotations

import base64
import json
import re
from pathlib import Path

from .clean import clean_text, has_pathological_repetition


# ---------------------------------------------------------------------------
# Strong diagnostic patterns
# ---------------------------------------------------------------------------

_URL_RE = re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE)

_DATA_URI_RE = re.compile(
    r"data:[^,\s]+;base64,[A-Za-z0-9+/=\s]+",
    re.IGNORECASE,
)

_BASE64_LONG_RE = re.compile(
    r"(?<![A-Za-z0-9+/=])[A-Za-z0-9+/]{200,}={0,2}(?![A-Za-z0-9+/=])"
)

_HTML_RE = re.compile(
    r"<\s*/?\s*[A-Za-z][^>]*>",
    re.IGNORECASE,
)

# Strong technical indicators only.
# Do NOT use generic words such as "chart", "github", or "code".
_GITHUB_URL_RE = re.compile(
    r"(?:https?://)?(?:www\.)?github\.com/",
    re.IGNORECASE,
)

_TECHNICAL_URL_RE = re.compile(
    r"https?://\S*(?:quickchart|mermaid|plotly|vega|raw\.githubusercontent)"
    r"\S*",
    re.IGNORECASE,
)

_IMAGE_PAYLOAD_RE = re.compile(
    r"(?:data:image/|image/png|image/jpeg|image/svg\+xml)",
    re.IGNORECASE,
)

_DNA_SEQUENCE_RE = re.compile(
    r"(?<![A-Za-z])(?:[ACGT]{40,}|[ACGTN]{40,})(?![A-Za-z])",
    re.IGNORECASE,
)

_DNA_HEAVY_RE = re.compile(
    r"^[ACGTN\s\d|:_.,;()\-/>]{50,}$",
    re.IGNORECASE,
)

_SEQUENCE_METADATA_RE = re.compile(
    r"\b(?:genomic\s+dna|genomic|pcr|primer|ssr|microsatellite|"
    r"sequence|chromosome|allele|locus|bp|base\s+pair|"
    r"nucleotide|dna|rna)\b",
    re.IGNORECASE,
)

_TABLE_NUMERIC_RE = re.compile(
    r"(?:\b\d+(?:\.\d+)?\b[\s|,\t]+){4,}"
)

_TABLE_STRUCTURAL_RE = re.compile(
    r"(?:\t|\|)"
)

_TABLE_ALIGNMENT_RE = re.compile(
    r"\b\d+\s+\d+\s+[A-Z]\s+[A-Z]\s+"
    r"(?:[A-Z<>+\-]+|\S+)\s+"
    r"(?:\d+\s+){2,}"
)

_REPEATED_SYMBOL_RE = re.compile(r"(.)\1{7,}")

_REPEATED_TOKEN_SEQUENCE_RE = re.compile(
    r"\b(\w+)(?:\s+\1){4,}\b",
    re.IGNORECASE,
)

# Strong signals of extracted source metadata/navigation.
_CMS_METADATA_RE = re.compile(
    r"(?i)(?:"
    r"(?<!\w)author\s+\w+"
    r"|(?<!\w)posted\s+on\s+[A-Z][a-z]+\s+\d{1,2},\s+\d{4}"
    r"|(?<!\w)leave\s+a\s+comment(?:\s+on)?"
    r"|(?<!\w)comments?\s+off\s+on\s+"
    r"|(?<!\w)comments?\s+off\s*/\s*continue\s+reading"
    r"|(?<!\w)subscribe(?:\s+by\s+email|\s+to)?"
    r"|(?<!\w)follow\s+me"
    r"|(?<!\w)the\s+post\b.*\bappeared\s+first\b"
    r")"
)


# ---------------------------------------------------------------------------
# Detection helpers
# ---------------------------------------------------------------------------

def _contains_data_uri(text: str) -> bool:
    return bool(_DATA_URI_RE.search(text))


def _contains_long_base64(text: str) -> bool:
    match = _BASE64_LONG_RE.search(text)

    if not match:
        return False

    try:
        base64.b64decode(match.group(0), validate=True)
        return True
    except Exception:
        return False


def _contains_genomic_sequence(text: str) -> bool:
    """Detect strong genomic/biological sequence evidence."""
    if _DNA_SEQUENCE_RE.search(text):
        return True

    if _SEQUENCE_METADATA_RE.search(text):
        compact = re.sub(r"\s+", "", text)

        # Scientific metadata + substantial sequence-like content.
        if len(compact) >= 40:
            sequence_chars = sum(
                char.upper() in "ACGTN"
                for char in compact
            )

            if sequence_chars / len(compact) >= 0.70:
                return True

    compact = re.sub(r"\s+", "", text)

    return (
        len(compact) >= 80
        and bool(_DNA_HEAVY_RE.fullmatch(text))
    )


def _looks_like_table_or_alignment(text: str) -> bool:
    """Detect structural table/alignment extraction."""
    if _TABLE_ALIGNMENT_RE.search(text):
        return True

    if _TABLE_NUMERIC_RE.search(text):
        return True

    # Multiple pipe/tab separators are stronger evidence than spaces alone.
    if text.count("|") >= 3:
        return True

    if text.count("\t") >= 2:
        return True

    return False


def _looks_like_technical_payload(text: str) -> bool:
    """Detect strong technical/web payload evidence."""
    if _GITHUB_URL_RE.search(text):
        return True

    if _TECHNICAL_URL_RE.search(text):
        return True

    if _IMAGE_PAYLOAD_RE.search(text):
        return True

    # Obvious source-code structure.
    code_signals = (
        "```",
        "<?xml",
        "<svg",
        "BEGIN DATA",
        "application/json",
        "application/javascript",
    )

    return any(signal in text for signal in code_signals)


def looks_like_repetition_artifact(text: str) -> bool:
    """Detect repetition only when the pattern is structurally suspicious."""
    if _REPEATED_TOKEN_SEQUENCE_RE.search(text):
        return True

    # Repeated symbols alone are not sufficient: Oromo uses expressive
    # repetition legitimately.
    if _REPEATED_SYMBOL_RE.search(text):
        repeated_chars = re.findall(r"(.)\1{7,}", text)

        for char in repeated_chars:
            if char not in "_-=|":
                continue

            return True

    return has_pathological_repetition(text)


def classify_record(text: str) -> list[str]:
    """Return overlapping diagnostic categories.

    Classification is diagnostic only and never implies rejection.
    """

    categories: list[str] = []

    if _contains_data_uri(text) or _contains_long_base64(text):
        categories.append("base64_or_data_uri")

    if _contains_genomic_sequence(text):
        categories.append("genomic_or_biological_sequence")

    if _looks_like_technical_payload(text):
        categories.append("technical_or_code_payload")
    elif _URL_RE.search(text):
        categories.append("url_or_web_payload")

    if _HTML_RE.search(text):
        categories.append("html_or_markup")

    if _looks_like_table_or_alignment(text):
        categories.append("table_or_numeric_extraction")

    if _CMS_METADATA_RE.search(text):
        categories.append("cms_or_social_metadata")

    if looks_like_repetition_artifact(text):
        categories.append("repetition_artifact")

    if not categories:
        categories.append("no_suspicion_detected")

    return categories


# ---------------------------------------------------------------------------
# Audit
# ---------------------------------------------------------------------------

def audit_jsonl_like_text(
    input_path: str | Path,
    output_path: str | Path,
    *,
    sample_limit: int = 100,
) -> dict:
    """Audit a line-oriented corpus without modifying raw records."""

    input_path = Path(input_path)
    output_path = Path(output_path)

    if not input_path.exists():
        raise FileNotFoundError(input_path)

    category_counts = {
        "no_suspicion_detected": 0,
        "base64_or_data_uri": 0,
        "genomic_or_biological_sequence": 0,
        "technical_or_code_payload": 0,
        "url_or_web_payload": 0,
        "html_or_markup": 0,
        "table_or_numeric_extraction": 0,
        "cms_or_social_metadata": 0,
        "repetition_artifact": 0,
    }

    category_examples = {
        category: []
        for category in category_counts
        if category != "no_suspicion_detected"
    }

    stats = {
        "input_records": 0,
        "changed_records": 0,
        "unchanged_records": 0,
        "empty_after_cleaning": 0,
        "pathological_repetition": 0,
        "input_characters": 0,
        "cleaned_characters": 0,
        "characters_removed": 0,
        "changed_examples": [],
        "category_counts": category_counts,
        "category_examples": category_examples,
    }

    with input_path.open("r", encoding="utf-8") as source:
        for line_number, line in enumerate(source, start=1):
            text = line.rstrip("\n\r")

            if not text:
                continue

            stats["input_records"] += 1
            stats["input_characters"] += len(text)

            cleaned = clean_text(text)
            stats["cleaned_characters"] += len(cleaned)

            removed = len(text) - len(cleaned)
            stats["characters_removed"] += removed

            if cleaned != text:
                stats["changed_records"] += 1

                if len(stats["changed_examples"]) < sample_limit:
                    stats["changed_examples"].append(
                        {
                            "line_number": line_number,
                            "before": text,
                            "after": cleaned,
                            "characters_removed": removed,
                        }
                    )
            else:
                stats["unchanged_records"] += 1

            if not cleaned:
                stats["empty_after_cleaning"] += 1

            if has_pathological_repetition(text):
                stats["pathological_repetition"] += 1

            categories = classify_record(text)

            for category in categories:
                category_counts[category] += 1

                if category == "no_suspicion_detected":
                    continue

                examples = category_examples[category]

                if len(examples) < sample_limit:
                    examples.append(
                        {
                            "line_number": line_number,
                            "text": text,
                        }
                    )

    stats["change_rate"] = (
        stats["changed_records"] / stats["input_records"]
        if stats["input_records"]
        else 0.0
    )

    stats["character_reduction_rate"] = (
        stats["characters_removed"] / stats["input_characters"]
        if stats["input_characters"]
        else 0.0
    )

    stats["suspicious_records"] = (
        stats["input_records"]
        - stats["category_counts"]["no_suspicion_detected"]
    )

    stats["suspicious_record_rate"] = (
        stats["suspicious_records"] / stats["input_records"]
        if stats["input_records"]
        else 0.0
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as report:
        json.dump(stats, report, ensure_ascii=False, indent=2)

    return stats


if __name__ == "__main__":
    input_path = Path("data/raw/afriberta_oromo/train/train.txt")
    output_path = Path("data/manifests/afriberta_oromo_audit.json")

    print(f"Auditing: {input_path}")
    print(f"Report:   {output_path}")

    stats = audit_jsonl_like_text(
        input_path,
        output_path,
        sample_limit=100,
    )

    print()
    print("=== CORPUS AUDIT ===")
    print(f"Input records:       {stats['input_records']:,}")
    print(f"Changed records:     {stats['changed_records']:,}")
    print(f"Unchanged records:   {stats['unchanged_records']:,}")
    print(f"Empty after cleaning:{stats['empty_after_cleaning']:,}")
    print(f"Suspicious records:  {stats['suspicious_records']:,}")
    print(f"Suspicious rate:     {stats['suspicious_record_rate']:.4%}")
    print()
    print("=== CONTAMINATION CATEGORY COUNTS ===")

    for category, count in stats["category_counts"].items():
        print(f"{category:35} {count:,}")

    print()
    print(f"Audit report written to: {output_path}")


# Backward-compatible private alias. New code should use the public helper.
_looks_like_repetition_artifact = looks_like_repetition_artifact
