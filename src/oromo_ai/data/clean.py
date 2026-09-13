"""Conservative text cleaning for Afaan Oromoo corpora."""

from __future__ import annotations

import re
import unicodedata


# ---------------------------------------------------------------------------
# Patterns
# ---------------------------------------------------------------------------

_READ_MORE_RE = re.compile(
    r"(?i)(?<!\w)(?:\[?\s*read\s*more\s*\]?)(?!\w)"
)

_EMBED_MARKER_RE = re.compile(
    r"(?i)\[/?(?:embed|embedyt)[^\]]*\]"
)

_HTML_TAG_RE = re.compile(
    r"<\/?[A-Za-z][^>]*>"
)

_URL_RE = re.compile(
    r"(?i)\b(?:https?://|www\.)[^\s<>\[\]()]+"
)

_CMS_BOILERPLATE_RE = re.compile(
    r"(?i)(?<!\w)comments\s+off(?!\w)"
)

_WHITESPACE_RE = re.compile(r"\s+")

# Used only as a diagnostic signal. It does not reject text.
_REPEATED_TOKEN_RE = re.compile(r"\b(\S+)(?:\s+\1){7,}\b", re.IGNORECASE)


# ---------------------------------------------------------------------------
# Individual transformations
# ---------------------------------------------------------------------------


def normalize_unicode(text: str) -> str:
    """Normalize text using Unicode NFC."""
    if not isinstance(text, str):
        raise TypeError("text must be a string")

    return unicodedata.normalize("NFC", text)


def normalize_whitespace(text: str) -> str:
    """Collapse runs of whitespace while preserving punctuation and words."""
    if not isinstance(text, str):
        raise TypeError("text must be a string")

    return _WHITESPACE_RE.sub(" ", text).strip()


def remove_read_more(text: str) -> str:
    """Remove obvious Read More extraction markers."""
    if not isinstance(text, str):
        raise TypeError("text must be a string")

    cleaned = _READ_MORE_RE.sub("", text)
    return cleaned.rstrip()


def remove_embed_markers(text: str) -> str:
    """Remove obvious CMS embed markers but preserve surrounding content."""
    if not isinstance(text, str):
        raise TypeError("text must be a string")

    return _EMBED_MARKER_RE.sub("", text)


def remove_html(text: str) -> str:
    """Remove obvious HTML tags without removing normal text."""
    if not isinstance(text, str):
        raise TypeError("text must be a string")

    return _HTML_TAG_RE.sub("", text)


def remove_urls(text: str) -> str:
    """Remove URLs while preserving surrounding linguistic content."""
    if not isinstance(text, str):
        raise TypeError("text must be a string")

    return _URL_RE.sub("", text)


def remove_cms_boilerplate(text: str) -> str:
    """Remove clearly identifiable CMS boilerplate."""
    if not isinstance(text, str):
        raise TypeError("text must be a string")

    return _CMS_BOILERPLATE_RE.sub("", text)


# ---------------------------------------------------------------------------
# Diagnostics
# ---------------------------------------------------------------------------


def has_pathological_repetition(text: str) -> bool:
    """Detect obvious repeated-token corruption.

    This is diagnostic only. It does not modify or reject the text.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")

    return bool(_REPEATED_TOKEN_RE.search(text))


# ---------------------------------------------------------------------------
# Main cleaning function
# ---------------------------------------------------------------------------


def clean_text(text: str) -> str:
    """Apply the conservative Oromo AI v0.1.0 cleaning policy.

    Order:
        1. Unicode NFC
        2. Read More markers
        3. Embed markers
        4. HTML
        5. URLs
        6. CMS boilerplate
        7. Whitespace normalization

    No lowercasing, ASCII folding, punctuation removal, or linguistic
    rewriting is performed.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")

    cleaned = normalize_unicode(text)
    cleaned = remove_read_more(cleaned)
    cleaned = remove_embed_markers(cleaned)
    cleaned = remove_html(cleaned)
    cleaned = remove_urls(cleaned)
    cleaned = remove_cms_boilerplate(cleaned)
    cleaned = normalize_whitespace(cleaned)

    return cleaned
