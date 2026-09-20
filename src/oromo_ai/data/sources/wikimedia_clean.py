from __future__ import annotations

import html
import re


# ---------------------------------------------------------------------------
# Structural MediaWiki blocks
# ---------------------------------------------------------------------------

_TABLE_RE = re.compile(
    r"\{\|.*?\|\}",
    flags=re.DOTALL,
)

_GALLERY_RE = re.compile(
    r"<gallery\b[^>]*>.*?</gallery>",
    flags=re.DOTALL | re.IGNORECASE,
)

_REF_BLOCK_RE = re.compile(
    r"<ref\b[^>]*>.*?</ref>",
    flags=re.DOTALL | re.IGNORECASE,
)

_REF_SELF_RE = re.compile(
    r"<ref\b[^>]*/\s*>",
    flags=re.IGNORECASE,
)

_COMMENT_RE = re.compile(
    r"<!--.*?-->",
    flags=re.DOTALL,
)


# ---------------------------------------------------------------------------
# Links / categories / files
# ---------------------------------------------------------------------------

_FILE_LINK_RE = re.compile(
    r"\[\[(?:File|Image):.*?\]\]",
    flags=re.DOTALL | re.IGNORECASE,
)

_CATEGORY_RE = re.compile(
    r"\[\[Category:[^\]]*\]\]",
    flags=re.IGNORECASE,
)

# Some source pages contain malformed one-bracket category links:
#
# [[Category:Seerluga]
#
# These are metadata, not training prose.
_MALFORMED_CATEGORY_RE = re.compile(
    r"\[\[Category:[^\]\n]*(?:\]\]|\])?",
    flags=re.IGNORECASE,
)

# Same defensive handling for malformed File/Image links.
_MALFORMED_FILE_RE = re.compile(
    r"\[\[(?:File|Image):[^\]\n]*(?:\]\]|\])?",
    flags=re.IGNORECASE,
)

# Malformed internal link:
#
# [[Oromia]
#
# Limit the span so this cannot consume a large section of a damaged page.
_MALFORMED_WIKILINK_RE = re.compile(
    r"\[\[([^\[\]\n]{1,300})\]"
)


# ---------------------------------------------------------------------------
# Headings
# ---------------------------------------------------------------------------

# Standard heading occupying a whole line:
#
# == Seenaa ==
_HEADING_RE = re.compile(
    r"(?m)^\s*={2,}\s*(.*?)\s*={2,}\s*$"
)

# Inline heading:
#
# Barnoota garii == Dhufaatii ==
#
# IMPORTANT: require at least TWO "=" characters.
_INLINE_HEADING_RE = re.compile(
    r"\s*={2,}\s*([^=\n]+?)\s*={2,}\s*"
)

# Broken one-sided headings:
#
# == Aanaan Jajuu ...
# ====@
# romoo ===
#
# Only strip markers at line boundaries so mathematical "=" occurring
# inside normal text is preserved.
_LEADING_HEADING_MARKER_RE = re.compile(
    r"(?m)^\s*={2,}\s*"
)

_TRAILING_HEADING_MARKER_RE = re.compile(
    r"(?m)\s*={2,}\s*$"
)


# ---------------------------------------------------------------------------
# Residual structural markers
# ---------------------------------------------------------------------------

# Remove malformed template closing braces ONLY when the complete line
# consists of the template marker. Do not globally remove "}}" because
# TeX/math expressions legitimately contain adjacent closing braces.
_STANDALONE_TEMPLATE_CLOSE_RE = re.compile(
    r"(?m)^\s*\}\}\s*$"
)

# Residual table-control lines. Complete tables are removed by _TABLE_RE,
# but malformed source pages can contain orphan table starts/ends.
_TABLE_OPEN_LINE_RE = re.compile(
    r"(?m)^\s*\{\|[^\n]*$"
)

_TABLE_CLOSE_LINE_RE = re.compile(
    r"(?m)^\s*\|\}\s*$"
)

_TABLE_ROW_SEPARATOR_RE = re.compile(
    r"(?m)^\s*\|-[^\n]*$"
)

_TABLE_CAPTION_RE = re.compile(
    r"(?m)^\s*\|\+[^\n]*$"
)


# ---------------------------------------------------------------------------
# Other markup
# ---------------------------------------------------------------------------

_EXTERNAL_LINK_RE = re.compile(
    r"\[(https?://\S+)(?:\s+([^\]]+))?\]"
)

_HTML_TAG_RE = re.compile(
    r"</?[A-Za-z][^>]*>"
)

_MULTIPLE_BLANKS_RE = re.compile(
    r"\n{3,}"
)

_MULTIPLE_SPACES_RE = re.compile(
    r"[ \t]{2,}"
)


def _remove_templates(text: str) -> str:
    """
    Remove balanced MediaWiki {{...}} template blocks.

    A small state machine is used rather than a broad regular expression
    so nested templates are handled without deleting unrelated prose.

    Unmatched closing braces are intentionally left alone here because
    TeX/math notation may legitimately contain adjacent closing braces.
    """

    output: list[str] = []
    depth = 0
    i = 0

    while i < len(text):
        if text.startswith("{{", i):
            depth += 1
            i += 2
            continue

        if text.startswith("}}", i) and depth:
            depth -= 1
            i += 2
            continue

        if depth == 0:
            output.append(text[i])

        i += 1

    return "".join(output)


def _replace_wikilinks(text: str) -> str:
    """
    Preserve human-visible text from normal MediaWiki links.

    Examples:

        [[Oromoo]]
            -> Oromoo

        [[Afaan Oromoo|Afaanicha]]
            -> Afaanicha

        [[horsiisee-bulaa|horsiisee-bulaatti]]
            -> horsiisee-bulaatti
    """

    pattern = re.compile(
        r"\[\[([^\[\]]+)\]\]"
    )

    def replace(match: re.Match[str]) -> str:
        content = match.group(1)

        if "|" in content:
            return content.rsplit("|", 1)[1].strip()

        return content.strip()

    previous = None

    while previous != text:
        previous = text
        text = pattern.sub(replace, text)

    return text


def _replace_malformed_wikilinks(text: str) -> str:
    """
    Preserve visible text from simple malformed links.

    Example:

        [[Oromia]
            -> Oromia

    This is intentionally conservative and limited to one line and
    300 characters.
    """

    def replace(match: re.Match[str]) -> str:
        content = match.group(1).strip()

        if "|" in content:
            return content.rsplit("|", 1)[1].strip()

        return content

    return _MALFORMED_WIKILINK_RE.sub(
        replace,
        text,
    )


def clean_wikimedia_wikitext(
    text: str,
) -> str:
    """
    Convert raw MediaWiki wikitext to conservative plain text.

    The function removes demonstrable structural wiki markup while
    preserving human-readable source text.

    It intentionally does NOT:

    - correct Oromo spelling
    - rewrite grammar
    - normalize dialect
    - remove multilingual text automatically
    - repair factual claims
    - rewrite malformed sentences
    - normalize mathematical notation
    """

    if not text:
        return ""

    # ------------------------------------------------------------------
    # HTML entities
    # ------------------------------------------------------------------

    text = html.unescape(text)

    # ------------------------------------------------------------------
    # Large structural blocks
    # ------------------------------------------------------------------

    text = _COMMENT_RE.sub(
        " ",
        text,
    )

    text = _GALLERY_RE.sub(
        " ",
        text,
    )

    text = _TABLE_RE.sub(
        " ",
        text,
    )

    # ------------------------------------------------------------------
    # References
    # ------------------------------------------------------------------

    text = _REF_BLOCK_RE.sub(
        " ",
        text,
    )

    text = _REF_SELF_RE.sub(
        " ",
        text,
    )

    # ------------------------------------------------------------------
    # Files / categories
    # ------------------------------------------------------------------

    text = _FILE_LINK_RE.sub(
        " ",
        text,
    )

    text = _CATEGORY_RE.sub(
        " ",
        text,
    )

    text = _MALFORMED_FILE_RE.sub(
        " ",
        text,
    )

    text = _MALFORMED_CATEGORY_RE.sub(
        " ",
        text,
    )

    # ------------------------------------------------------------------
    # Templates
    # ------------------------------------------------------------------

    text = _remove_templates(text)

    # Remove ONLY standalone orphan template-closing lines.
    #
    # Do not use:
    #
    #     text.replace("}}", "")
    #
    # because this would damage TeX/math.
    text = _STANDALONE_TEMPLATE_CLOSE_RE.sub(
        " ",
        text,
    )

    # ------------------------------------------------------------------
    # Headings
    # ------------------------------------------------------------------

    text = _HEADING_RE.sub(
        lambda match: (
            f"\n{match.group(1).strip()}\n"
        ),
        text,
    )

    text = _INLINE_HEADING_RE.sub(
        lambda match: (
            f"\n{match.group(1).strip()}\n"
        ),
        text,
    )

    # Clean one-sided/malformed heading markers only at line boundaries.
    text = _LEADING_HEADING_MARKER_RE.sub(
        "",
        text,
    )

    text = _TRAILING_HEADING_MARKER_RE.sub(
        "",
        text,
    )

    # ------------------------------------------------------------------
    # Internal Wiki links
    # ------------------------------------------------------------------

    text = _replace_wikilinks(text)

    text = _replace_malformed_wikilinks(
        text,
    )

    # At this point complete and simple malformed wiki links have already
    # been processed. Remaining double brackets are orphan MediaWiki
    # delimiters, so remove only the delimiters and preserve their text.
    text = text.replace(
        "[[",
        "",
    )

    text = text.replace(
        "]]",
        "",
    )

    # ------------------------------------------------------------------
    # External links
    # ------------------------------------------------------------------

    def replace_external(
        match: re.Match[str],
    ) -> str:
        label = match.group(2)

        if label:
            return label.strip()

        return " "

    text = _EXTERNAL_LINK_RE.sub(
        replace_external,
        text,
    )

    # ------------------------------------------------------------------
    # Residual malformed table-control lines
    # ------------------------------------------------------------------

    text = _TABLE_OPEN_LINE_RE.sub(
        " ",
        text,
    )

    text = _TABLE_CLOSE_LINE_RE.sub(
        " ",
        text,
    )

    text = _TABLE_ROW_SEPARATOR_RE.sub(
        " ",
        text,
    )

    text = _TABLE_CAPTION_RE.sub(
        " ",
        text,
    )

    # ------------------------------------------------------------------
    # Bold / italic markup
    # ------------------------------------------------------------------

    text = text.replace(
        "'''",
        "",
    )

    text = text.replace(
        "''",
        "",
    )

    # ------------------------------------------------------------------
    # HTML tags
    # ------------------------------------------------------------------

    text = _HTML_TAG_RE.sub(
        " ",
        text,
    )

    # ------------------------------------------------------------------
    # List markers
    # ------------------------------------------------------------------

    text = re.sub(
        r"(?m)^\s*[*#:;]+\s*",
        "",
        text,
    )

    # ------------------------------------------------------------------
    # Horizontal whitespace
    # ------------------------------------------------------------------

    text = _MULTIPLE_SPACES_RE.sub(
        " ",
        text,
    )

    # Strip each line without flattening document structure.
    lines = [
        line.strip()
        for line in text.splitlines()
    ]

    text = "\n".join(lines)

    # Preserve logical paragraph boundaries but never more than one
    # consecutive blank line.
    text = _MULTIPLE_BLANKS_RE.sub(
        "\n\n",
        text,
    )

    return text.strip()