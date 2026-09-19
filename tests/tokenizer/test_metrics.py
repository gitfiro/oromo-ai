from oromo_ai.tokenizer.metrics import (
    calculate_metrics,
    calculate_word_fragmentation,
)


def test_calculate_metrics():
    texts = [
        "Ani Oromoo",
        "Afaan Oromoo",
    ]

    metrics = calculate_metrics(
        texts,
        [2, 3],
        fragmented_words=2,
        single_token_words=2,
        unaligned_words=0,
        unknown_tokens=1,
    )

    assert metrics.characters == 22
    assert metrics.bytes == 22
    assert metrics.words == 4
    assert metrics.tokens == 5

    assert metrics.tokens_per_word == 1.25
    assert metrics.characters_per_token == 4.4
    assert metrics.bytes_per_token == 4.4

    assert metrics.fragmented_words == 2
    assert metrics.single_token_words == 2
    assert metrics.unaligned_words == 0
    assert metrics.unknown_tokens == 1

    assert metrics.word_fragmentation_rate == 0.5
    assert metrics.single_token_word_rate == 0.5
    assert metrics.unaligned_word_rate == 0.0
    assert metrics.unknown_token_rate == 0.2


def test_empty_metrics():
    metrics = calculate_metrics([], [])

    assert metrics.characters == 0
    assert metrics.bytes == 0
    assert metrics.words == 0
    assert metrics.tokens == 0

    assert metrics.tokens_per_word == 0.0
    assert metrics.characters_per_token == 0.0
    assert metrics.bytes_per_token == 0.0

    assert metrics.fragmented_words == 0
    assert metrics.single_token_words == 0
    assert metrics.unaligned_words == 0
    assert metrics.unknown_tokens == 0

    assert metrics.word_fragmentation_rate == 0.0
    assert metrics.single_token_word_rate == 0.0
    assert metrics.unaligned_word_rate == 0.0
    assert metrics.unknown_token_rate == 0.0


def test_mismatched_lengths():
    try:
        calculate_metrics(["Ani"], [1, 2])
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError")


def test_invalid_token_count():
    try:
        calculate_metrics(["Ani"], [-1])
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError")


def test_invalid_metric_counts():
    try:
        calculate_metrics(["Ani"], [1], fragmented_words=2)
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError")

    try:
        calculate_metrics(["Ani"], [1], unknown_tokens=2)
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError")


def test_word_fragmentation_classification():
    texts = [
        "Ani Mootummaan Oromoo",
    ]

    # Ani         -> one token
    # Mootummaan  -> three tokens
    # Oromoo      -> one token
    offsets = [
        [
            (0, 3),
            (4, 7),
            (7, 10),
            (10, 14),
            (15, 21),
        ]
    ]

    fragmented, single, unaligned = calculate_word_fragmentation(
        texts,
        offsets,
    )

    assert fragmented == 1
    assert single == 2
    assert unaligned == 0

    assert fragmented + single + unaligned == 3


def test_unaligned_word():
    texts = [
        "Ani \u200b Oromoo",
    ]

    # The zero-width-space word occupies position 4 but the tokenizer
    # provides no offset for it.
    offsets = [
        [
            (0, 3),
            (6, 12),
        ]
    ]

    fragmented, single, unaligned = calculate_word_fragmentation(
        texts,
        offsets,
    )

    assert fragmented == 0
    assert single == 2
    assert unaligned == 1

    assert fragmented + single + unaligned == 3


def test_partial_offset_coverage_still_classified():
    texts = [
        "\u200eOromoo",
    ]

    # Position 0 is an invisible formatting character that the
    # tokenizer dropped. The visible Oromo text is still represented
    # by one token.
    offsets = [
        [
            (1, 7),
        ]
    ]

    fragmented, single, unaligned = calculate_word_fragmentation(
        texts,
        offsets,
    )

    assert fragmented == 0
    assert single == 1
    assert unaligned == 0


def test_fragmentation_input_length_mismatch():
    try:
        calculate_word_fragmentation(
            ["Ani"],
            [],
        )
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError")


def test_word_classification_invariant():
    texts = [
        "Ani Oromoo",
    ]

    try:
        calculate_metrics(
            texts,
            [2],
            fragmented_words=1,
            single_token_words=0,
            unaligned_words=0,
        )
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError")