from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Sequence


@dataclass(frozen=True)
class TokenizationMetrics:
    characters: int
    bytes: int
    words: int
    tokens: int
    fragmented_words: int
    single_token_words: int
    unaligned_words: int
    unknown_tokens: int

    @property
    def tokens_per_word(self) -> float:
        return self.tokens / self.words if self.words else 0.0

    @property
    def characters_per_token(self) -> float:
        return self.characters / self.tokens if self.tokens else 0.0

    @property
    def bytes_per_token(self) -> float:
        return self.bytes / self.tokens if self.tokens else 0.0

    @property
    def word_fragmentation_rate(self) -> float:
        return self.fragmented_words / self.words if self.words else 0.0

    @property
    def single_token_word_rate(self) -> float:
        return self.single_token_words / self.words if self.words else 0.0

    @property
    def unaligned_word_rate(self) -> float:
        return self.unaligned_words / self.words if self.words else 0.0

    @property
    def unknown_token_rate(self) -> float:
        return self.unknown_tokens / self.tokens if self.tokens else 0.0


def calculate_metrics(
    texts: list[str],
    token_counts: list[int],
    *,
    fragmented_words: int = 0,
    single_token_words: int = 0,
    unaligned_words: int = 0,
    unknown_tokens: int = 0,
) -> TokenizationMetrics:
    """Calculate corpus-level tokenizer efficiency metrics."""

    if len(texts) != len(token_counts):
        raise ValueError("texts and token_counts must have equal length")

    if any(count < 0 for count in token_counts):
        raise ValueError("token counts must be non-negative")

    if fragmented_words < 0:
        raise ValueError("fragmented_words must be non-negative")

    if single_token_words < 0:
        raise ValueError("single_token_words must be non-negative")

    if unaligned_words < 0:
        raise ValueError("unaligned_words must be non-negative")

    if unknown_tokens < 0:
        raise ValueError("unknown_tokens must be non-negative")

    characters = sum(len(text) for text in texts)
    encoded_bytes = sum(
        len(text.encode("utf-8"))
        for text in texts
    )
    words = sum(
        len(text.split())
        for text in texts
    )
    tokens = sum(token_counts)

    if fragmented_words > words:
        raise ValueError(
            "fragmented_words cannot exceed words"
        )

    if single_token_words > words:
        raise ValueError(
            "single_token_words cannot exceed words"
        )

    if unaligned_words > words:
        raise ValueError(
            "unaligned_words cannot exceed words"
        )

    if unknown_tokens > tokens:
        raise ValueError(
            "unknown_tokens cannot exceed tokens"
        )

    classified_words = (
        fragmented_words
        + single_token_words
        + unaligned_words
    )

    if words and classified_words != words:
        raise ValueError(
            "word classification mismatch: "
            f"fragmented={fragmented_words}, "
            f"single_token={single_token_words}, "
            f"unaligned={unaligned_words}, "
            f"total={classified_words}, "
            f"expected={words}"
        )

    return TokenizationMetrics(
        characters=characters,
        bytes=encoded_bytes,
        words=words,
        tokens=tokens,
        fragmented_words=fragmented_words,
        single_token_words=single_token_words,
        unaligned_words=unaligned_words,
        unknown_tokens=unknown_tokens,
    )


def calculate_word_fragmentation(
    texts: Sequence[str],
    offset_mappings: Sequence[
        Sequence[tuple[int, int]]
    ],
) -> tuple[int, int, int]:
    """
    Classify whitespace-delimited words using tokenizer offsets.

    Returns:
        fragmented_words:
            Words represented by two or more tokenizer pieces.

        single_token_words:
            Words represented by exactly one tokenizer piece.

        unaligned_words:
            Words with no overlapping tokenizer offset.

    Zero-length offsets are ignored because they usually represent
    special tokens.

    A word with partial character coverage is still classified by
    the number of tokenizer pieces that overlap it. This allows
    tokenizers that normalize or discard Unicode formatting/control
    characters to remain measurable without silently losing the word
    from accounting.
    """

    if len(texts) != len(offset_mappings):
        raise ValueError(
            "texts and offset_mappings must have equal length"
        )

    fragmented_words = 0
    single_token_words = 0
    unaligned_words = 0

    for text, offsets in zip(
        texts,
        offset_mappings,
    ):
        words = [
            match.span()
            for match in re.finditer(r"\S+", text)
        ]

        for word_start, word_end in words:
            token_count = sum(
                token_start < word_end
                and token_end > word_start
                for token_start, token_end in offsets
                if token_end > token_start
            )

            if token_count == 0:
                unaligned_words += 1
            elif token_count == 1:
                single_token_words += 1
            else:
                fragmented_words += 1

    return (
        fragmented_words,
        single_token_words,
        unaligned_words,
    )