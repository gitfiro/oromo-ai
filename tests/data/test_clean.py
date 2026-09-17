from oromo_ai.data.clean import (
    clean_text,
    normalize_unicode,
    normalize_whitespace,
    remove_read_more,
    remove_embed_markers,
    remove_html,
    remove_urls,
    remove_cms_boilerplate,
)


def test_unicode_nfc():
    text = "Afaan Oromoo"
    assert normalize_unicode(text) == text


def test_whitespace_normalization():
    text = "Afaan   Oromoo\tni\nbareeda."
    assert normalize_whitespace(text) == "Afaan Oromoo ni bareeda."


def test_read_more_removed():
    text = "Afaan Oromoo ni baranna. Read More"
    assert remove_read_more(text) == "Afaan Oromoo ni baranna."


def test_read_more_bracketed_removed():
    text = "Afaan Oromoo ni baranna. [Read More]"
    assert remove_read_more(text) == "Afaan Oromoo ni baranna."


def test_embed_marker_removed():
    text = "Kun barruu Afaan Oromoo ti. [embedyt] https://example.com"
    result = remove_embed_markers(text)
    assert "[embedyt]" not in result
    assert "Kun barruu Afaan Oromoo ti." in result


def test_html_removed():
    text = "<p>Afaan Oromoo ni baranna.</p>"
    assert remove_html(text) == "Afaan Oromoo ni baranna."


def test_url_removed():
    text = "Odeeffannoo dabalataa https://example.com argadhu."
    result = remove_urls(text)
    assert "https://example.com" not in result
    assert "Odeeffannoo dabalataa" in result
    assert "argadhu." in result


def test_cms_boilerplate_removed():
    text = "Afaan Oromoo ni baranna. Comments Off"
    result = remove_cms_boilerplate(text)
    assert "Comments Off" not in result
    assert "Afaan Oromoo ni baranna." in result


def test_oromo_characters_preserved():
    text = "Qorannoo Afaan Oromoo keessatti qajeelfama."
    result = clean_text(text)

    assert "Q" in result
    assert "q" in result
    assert "Oromoo" in result
    assert "qajeelfama" in result


def test_apostrophe_characters_preserved():
    text = "Afaan Oromoo ’ fi ' fi ʼ"
    result = clean_text(text)

    assert "’" in result
    assert "'" in result
    assert "ʼ" in result


def test_legitimate_english_word_preserved():
    text = "BBC Afaan Oromoo irratti odeeffannoo kenne."
    result = clean_text(text)

    assert "BBC" in result
    assert "Afaan Oromoo" in result


def test_legitimate_political_content_preserved():
    text = (
        "Seenaa fi siyaasaa Oromiyaa irratti qorannoon "
        "bal'aan gaggeeffame."
    )
    result = clean_text(text)

    assert "siyaasaa" in result
    assert "Oromiyaa" in result
    assert "qorannoon" in result


def test_mixed_artifacts_and_real_text():
    text = (
        "<p>Afaan Oromoo afaan dhalootaa ti.</p> "
        "Read More https://example.com"
    )

    result = clean_text(text)

    assert "Afaan Oromoo afaan dhalootaa ti." in result
    assert "<p>" not in result
    assert "Read More" not in result
    assert "https://example.com" not in result


def test_clean_text_does_not_lowercase():
    text = "Afaan Oromoo"
    result = clean_text(text)

    assert result == "Afaan Oromoo"


def test_clean_text_does_not_remove_punctuation():
    text = "Akkam jirtu? Ani nagaan jira!"
    result = clean_text(text)

    assert "?" in result
    assert "!" in result


def test_empty_after_cleaning():
    text = "[Read More] https://example.com"
    result = clean_text(text)

    assert result == ""


def test_legitimate_read_more_about_is_preserved():
    text = (
        "Read more about Mitikkuu Maddaa fi Alamaayyoo "
        "Xilaahuniin."
    )

    result = clean_text(text)

    assert result == text


def test_bracketed_read_more_before_content_is_removed():
    text = "WBO Jecha [Read More] The post barruu kanaa."

    result = clean_text(text)

    assert "[Read More]" not in result
    assert "WBO Jecha" in result
    assert "The post barruu kanaa." in result


def test_read_more_at_end_is_removed():
    text = "Afaan Oromoo ni baranna. Read More"

    result = clean_text(text)

    assert result == "Afaan Oromoo ni baranna."


def test_read_more_symbol_at_end_is_removed():
    text = "Afaan Oromoo ni baranna. Read More »"

    result = clean_text(text)

    assert result == "Afaan Oromoo ni baranna."


def test_readmore_at_end_is_removed():
    text = "Afaan Oromoo ni baranna. ReadMore"

    result = clean_text(text)

    assert result == "Afaan Oromoo ni baranna."

def test_wordpress_post_wrapper_removed():
    text = (
        "WBO Jecha [Read More] "
        "The post Walaloo Ajaa ibaa Waraana Bilisummaa Oromootiif "
        "Lataa Qana ii Aagaatiin Must watch appeared first on ."
    )

    result = clean_text(text)

    assert "WBO Jecha" in result
    assert "Walaloo Ajaa ibaa" in result
    assert "The post" not in result
    assert "appeared first on" not in result