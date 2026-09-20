from __future__ import annotations

import hashlib
import unicodedata

import regex


WORD_RE = regex.compile(
    r"[\p{L}\p{M}\p{N}]+(?:['’ʼ-][\p{L}\p{M}\p{N}]+)*",
    flags=regex.VERSION1,
)


def normalize_for_similarity(text: str) -> str:
    if not isinstance(text, str):
        raise TypeError("text must be a string")

    text = unicodedata.normalize("NFC", text)

    return " ".join(
        token.lower()
        for token in WORD_RE.findall(text)
    )


def similarity_tokens(text: str) -> list[str]:
    normalized = normalize_for_similarity(text)

    if not normalized:
        return []

    return normalized.split()


def _hash_text(value: str) -> int:
    digest = hashlib.blake2b(
        value.encode("utf-8"),
        digest_size=8,
    ).digest()

    return int.from_bytes(
        digest,
        byteorder="big",
        signed=False,
    )


def shingle_hashes(
    text: str,
    *,
    shingle_size: int = 5,
) -> set[int]:
    if shingle_size < 1:
        raise ValueError("shingle_size must be >= 1")

    tokens = similarity_tokens(text)

    if not tokens:
        return set()

    if len(tokens) < shingle_size:
        return {
            _hash_text(" ".join(tokens))
        }

    return {
        _hash_text(
            "\x1f".join(
                tokens[index:index + shingle_size]
            )
        )
        for index in range(
            len(tokens) - shingle_size + 1
        )
    }


def bottom_k_signature(
    hashes: set[int],
    *,
    size: int = 32,
) -> tuple[int, ...]:
    if size < 1:
        raise ValueError("size must be >= 1")

    if not hashes:
        return tuple()

    return tuple(
        sorted(hashes)[:size]
    )


def text_signature(
    text: str,
    *,
    shingle_size: int = 5,
    signature_size: int = 32,
) -> tuple[int, ...]:
    return bottom_k_signature(
        shingle_hashes(
            text,
            shingle_size=shingle_size,
        ),
        size=signature_size,
    )


def signature_overlap(
    left: tuple[int, ...],
    right: tuple[int, ...],
) -> int:
    return len(
        set(left).intersection(right)
    )


def jaccard_similarity(
    left: set[int],
    right: set[int],
) -> float:
    if not left and not right:
        return 1.0

    if not left or not right:
        return 0.0

    intersection = len(
        left.intersection(right)
    )

    union = len(
        left.union(right)
    )

    return intersection / union


def near_duplicate_similarity(
    left_text: str,
    right_text: str,
    *,
    shingle_size: int = 5,
) -> float:
    left = shingle_hashes(
        left_text,
        shingle_size=shingle_size,
    )

    right = shingle_hashes(
        right_text,
        shingle_size=shingle_size,
    )

    return jaccard_similarity(
        left,
        right,
    )


def is_near_duplicate(
    left_text: str,
    right_text: str,
    *,
    threshold: float = 0.85,
    shingle_size: int = 5,
) -> bool:
    if not 0.0 <= threshold <= 1.0:
        raise ValueError(
            "threshold must be between 0 and 1"
        )

    return (
        near_duplicate_similarity(
            left_text,
            right_text,
            shingle_size=shingle_size,
        )
        >= threshold
    )
