"""Corpus quality decisions for the v0.1 Oromo training pipeline."""

from __future__ import annotations

import re

from .audit import classify_record


_SCIENTIFIC_METADATA_RE = re.compile(
    r"\b(?:genomic\s+dna|dna\s+probe|pcr\s*[-–]?\s*ssr|"
    r"microsatellite|chromosome|nucleotide|cDNA|"
    r"polymerase\s+chain\s+reaction|sequencing|"
    r"primer|amplicon|genotype|genotyping)\b",
    re.IGNORECASE,
)

_SEQUENCE_TOKEN_RE = re.compile(
    r"^[ACGTN]{40,}$",
    re.IGNORECASE,
)

_SEQUENCE_FRAGMENT_RE = re.compile(
    r"\b[ACGTN]{60,}\b",
    re.IGNORECASE,
)

_SEQUENCE_TABLE_ENTRY_RE = re.compile(
    r"\b\d+\s+[ACGTN]{18,}\s+\d+\b",
    re.IGNORECASE,
)

_SOCIAL_SPAM_RE = re.compile(
    r"(?:#\w+\s+){5,}|"
    r"(?:@\w+\s+){3,}",
    re.IGNORECASE,
)

_SHORT_PLACEHOLDER_RE = re.compile(r"[■□�]")


def _is_scientific_payload(text: str) -> bool:
    """Reject obvious scientific/sequence contamination.

    This deliberately requires structural evidence. Natural Oromo prose
    contains many A/C/G/T/N characters, so alphabet-overlap alone is not
    sufficient evidence of a biological sequence.
    """

    if _SCIENTIFIC_METADATA_RE.search(text):
        return True

    tokens = text.split()

    # A long uninterrupted DNA-like token is strong evidence.
    if any(_SEQUENCE_TOKEN_RE.fullmatch(token.strip(".,;:()[]{}")) for token in tokens):
        return True

    # A very long DNA-like fragment embedded in otherwise short metadata
    # is also strong evidence.
    if _SEQUENCE_FRAGMENT_RE.search(text):
        return True

    sequence_table_entries = _SEQUENCE_TABLE_ENTRY_RE.findall(text)

    if len(sequence_table_entries) >= 5:
    	return True

    # Sequence/alignment records frequently consist of many short sequence
    # tokens rather than natural-language words. Require several independent
    # signals before rejecting.
    if len(tokens) >= 8:
        sequence_tokens = 0

        for token in tokens:
            cleaned = re.sub(r"[^A-Za-z]", "", token)

            if 6 <= len(cleaned) <= 80 and re.fullmatch(
                r"[ACGTN]+", cleaned, re.IGNORECASE
            ):
                sequence_tokens += 1

        sequence_ratio = sequence_tokens / len(tokens)

        if sequence_tokens >= 6 and sequence_ratio >= 0.60:
            return True

    return False


def _is_social_spam(text: str) -> bool:
    """Detect records dominated by social-media noise."""

    if len(text) > 800:
        return False

    hashtags = len(re.findall(r"#\w+", text))
    handles = len(re.findall(r"@\w+", text))

    if hashtags >= 8:
        return True

    if handles >= 4:
        return True

    tokens = re.findall(r"\b\w+\b", text.lower())

    if len(tokens) >= 12:
        unique_ratio = len(set(tokens)) / len(tokens)

        if unique_ratio < 0.30:
            return True

    return False


def _is_obvious_garbage(text: str) -> bool:
    """Reject clearly non-linguistic extraction noise."""

    if not text.strip():
        return True

    alphanumeric = sum(char.isalnum() for char in text)

    if len(text) >= 20 and alphanumeric / len(text) < 0.25:
        return True

    # Extremely short records made almost entirely from punctuation/symbols.
    if len(text) >= 20 and alphanumeric == 0:
        return True

    # Known binary/terminal-like garbage pattern.
    if "``" in text and alphanumeric < 20:
        return True

    return False


def _is_short_extraction_artifact(text: str) -> bool:
    """Reject short OCR/extraction fragments with placeholder glyphs.

    This rule is intentionally narrow. Short text and spaced single-character
    tokens alone are not sufficient evidence of corruption. The combination
    of short length, high single-character ratio, and replacement/placeholder
    glyphs is required.
    """

    if len(text) >= 20:
        return False

    tokens = text.split()

    if len(tokens) < 3:
        return False

    if not _SHORT_PLACEHOLDER_RE.search(text):
        return False

    single_character_tokens = sum(
        1
        for token in tokens
        if len(token.strip(".,!?;:()[]{}\"'’ʼ")) == 1
    )

    single_character_ratio = single_character_tokens / len(tokens)

    return single_character_ratio >= 0.75


def decide_record(text: str) -> tuple[str, list[str]]:
    """Return KEEP, CLEAN, or REJECT plus reasons.

    Decisions are conservative and deterministic.
    """

    categories = classify_record(text)

    # ---------------------------------------------------------------
    # REJECT
    # ---------------------------------------------------------------

    if "base64_or_data_uri" in categories:
        return "REJECT", ["base64_or_data_uri"]

    if _is_scientific_payload(text):
        return "REJECT", ["scientific_or_genomic_payload"]

    if _is_social_spam(text):
        return "REJECT", ["social_media_spam"]

    if _is_obvious_garbage(text):
        return "REJECT", ["obvious_extraction_garbage"]

    if _is_short_extraction_artifact(text):
        return "REJECT", ["short_extraction_artifact"]

    if "technical_or_code_payload" in categories:
        return "REJECT", ["technical_or_code_payload"]

    # ---------------------------------------------------------------
    # CLEAN
    # ---------------------------------------------------------------

    clean_categories = {
        "url_or_web_payload",
        "html_or_markup",
        "cms_or_social_metadata",
    }

    matched_clean_categories = clean_categories.intersection(categories)

    if matched_clean_categories:
        return "CLEAN", sorted(matched_clean_categories)

    # ---------------------------------------------------------------
    # KEEP
    # ---------------------------------------------------------------

    # Repetition is NOT automatically a rejection.
    if "repetition_artifact" in categories:
        return "KEEP", ["repetition_reviewed_preserve_by_default"]

    # Numeric/table detection is diagnostic only.
    # Oromo documents legitimately contain dates, laws, lists, currency,
    # measurements, statistics, scores, citations and numbered sections.
    if "table_or_numeric_extraction" in categories:
        return "KEEP", ["numeric_or_table_signal_not_sufficient_for_rejection"]

    return "KEEP", ["no_rejection_signal"]


def decision_counts(records: list[str]) -> dict[str, int]:
    """Summarize decisions for a collection of records."""

    counts = {
        "KEEP": 0,
        "CLEAN": 0,
        "REJECT": 0,
    }

    for text in records:
        decision, _ = decide_record(text)
        counts[decision] += 1

    return counts
