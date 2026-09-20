from oromo_ai.data.near_deduplicate import (
    bottom_k_signature,
    is_near_duplicate,
    jaccard_similarity,
    near_duplicate_similarity,
    normalize_for_similarity,
    shingle_hashes,
    signature_overlap,
    text_signature,
)


def test_normalization_is_deterministic():
    text = "Afaan   OROMOO\nAfaan guddaa dha."

    assert normalize_for_similarity(text) == (
        "afaan oromoo afaan guddaa dha"
    )


def test_punctuation_does_not_control_similarity():
    left = "Afaan Oromoo afaan guddaa dha."
    right = "Afaan Oromoo, afaan guddaa dha!"

    assert (
        normalize_for_similarity(left)
        == normalize_for_similarity(right)
    )


def test_shingle_hashes_are_deterministic():
    text = (
        "Afaan Oromoo uummata Oromoo "
        "biratti balinaan dubbatama"
    )

    first = shingle_hashes(text)
    second = shingle_hashes(text)

    assert first == second
    assert first


def test_bottom_k_signature_has_requested_size():
    values = set(range(100))

    signature = bottom_k_signature(
        values,
        size=16,
    )

    assert len(signature) == 16
    assert signature == tuple(range(16))


def test_identical_text_has_similarity_one():
    text = (
        "Oromoon Gaanfa Afrikaa keessa "
        "waggoota dheeraaf jiraataa ture."
    )

    assert near_duplicate_similarity(
        text,
        text,
    ) == 1.0


def test_minor_change_remains_similar():
    left = (
        "Afaan Oromoo afaan Kuushii keessaa "
        "isa guddaa fi Afrikaa keessatti balinaan "
        "dubbatamu keessaa isa tokko dha."
    )

    right = (
        "Afaan Oromoo afaan Kuushii keessaa "
        "isa guddaa fi Afrikaa keessatti balinaan "
        "dubbatamu keessaa isa tokko dha. "
        "Afaan kun Oromiyaa keessatti beekama."
    )

    assert near_duplicate_similarity(
        left,
        right,
    ) > 0.50


def test_unrelated_text_is_not_near_duplicate():
    left = (
        "Afaan Oromoo afaan Kuushii keessaa "
        "isa tokko dha."
    )

    right = (
        "Bunni Itoophiyaa keessatti oomisha "
        "qonnaa barbaachisaa dha."
    )

    assert not is_near_duplicate(
        left,
        right,
        threshold=0.85,
    )


def test_signature_overlap():
    assert signature_overlap(
        (1, 2, 3, 4),
        (3, 4, 5, 6),
    ) == 2


def test_jaccard_similarity():
    assert jaccard_similarity(
        {1, 2, 3},
        {2, 3, 4},
    ) == 0.5


def test_text_signature_is_stable():
    text = (
        "Qubee Afaan Oromoo sirna "
        "barreeffamaa Afaan Oromoo ti."
    )

    assert text_signature(text) == text_signature(text)
