from oromo_ai.data.sources.wikimedia_clean import (
    clean_wikimedia_wikitext,
)


def test_preserves_plain_oromo_prose():
    text = (
        "Afaan Oromoo afaan Kuushii keessaa "
        "isa guddaa dha."
    )

    assert clean_wikimedia_wikitext(text) == text


def test_removes_template():
    text = (
        "{{Wiktionary|Oromoo}}\n"
        "Oromoon ummata guddaadha."
    )

    assert (
        clean_wikimedia_wikitext(text)
        == "Oromoon ummata guddaadha."
    )


def test_preserves_wikilink_text():
    text = (
        "Ummanni [[Oromoo]] "
        "[[Gaanfa Afrikaa]] keessa jira."
    )

    assert clean_wikimedia_wikitext(text) == (
        "Ummanni Oromoo Gaanfa Afrikaa keessa jira."
    )


def test_preserves_piped_link_label():
    text = (
        "[[horsiisee-bulaa|horsiisee-bulaatti]] "
        "jiraata."
    )

    assert clean_wikimedia_wikitext(text) == (
        "horsiisee-bulaatti jiraata."
    )


def test_removes_file_link():
    text = (
        "[[File:Africa.svg|thumb|Kartaa Afrikaa]]\n"
        "Afrikaan ardii guddaadha."
    )

    assert clean_wikimedia_wikitext(text) == (
        "Afrikaan ardii guddaadha."
    )


def test_removes_category():
    text = (
        "Afrikaan ardii guddaadha.\n"
        "[[Category:Afrikaa]]"
    )

    assert clean_wikimedia_wikitext(text) == (
        "Afrikaan ardii guddaadha."
    )


def test_removes_gallery():
    text = (
        "Afrikaa\n"
        "<gallery>\n"
        "File:test.jpg\n"
        "</gallery>\n"
        "Ardii guddaa."
    )

    assert clean_wikimedia_wikitext(text) == (
        "Afrikaa\n\nArdii guddaa."
    )


def test_preserves_heading_text():
    text = (
        "== Seenaa ==\n"
        "Afaan Oromoo seenaa dheeraa qaba."
    )

    assert clean_wikimedia_wikitext(text) == (
        "Seenaa\n\n"
        "Afaan Oromoo seenaa dheeraa qaba."
    )


def test_removes_refs():
    text = (
        "Oromoon Afrikaa keessa jira."
        "<ref>Some citation</ref>"
    )

    assert clean_wikimedia_wikitext(text) == (
        "Oromoon Afrikaa keessa jira."
    )


def test_removes_bold_and_italic_markup():
    text = (
        "'''Afaan Oromoo''' "
        "''afaan Kuushii'' dha."
    )

    assert clean_wikimedia_wikitext(text) == (
        "Afaan Oromoo afaan Kuushii dha."
    )


def test_normalizes_inline_heading():
    text = (
        "Barnoota garii == Dhufaatii ==\n"
        "Ka'umsi Oromoo eessaa akka ta'e."
    )

    assert clean_wikimedia_wikitext(text) == (
        "Barnoota garii\n"
        "Dhufaatii\n"
        "Ka'umsi Oromoo eessaa akka ta'e."
    )


def test_repairs_single_bracket_malformed_wikilink():
    text = (
        "Magaalaan [[Oromia] keessa jirti."
    )

    assert clean_wikimedia_wikitext(text) == (
        "Magaalaan Oromia keessa jirti."
    )


def test_removes_orphan_double_wikilink_closing_marker():
    text = (
        "Urjiin kun bishaan qaba agarsiisa]] "
        "jedhame."
    )

    assert clean_wikimedia_wikitext(text) == (
        "Urjiin kun bishaan qaba agarsiisa "
        "jedhame."
    )


def test_removes_standalone_template_close():
    text = (
        "Population = 110,688\n"
        "}}\n"
        "Naqamte magaalaa Oromiyaa ti."
    )

    assert clean_wikimedia_wikitext(text) == (
        "Population = 110,688\n\n"
        "Naqamte magaalaa Oromiyaa ti."
    )


def test_preserves_tex_double_closing_braces():
    text = (
        r"c_{\mathrm{air}} = 331.3"
    )

    assert clean_wikimedia_wikitext(text) == text


def test_preserves_tex_fraction():
    text = (
        r"E = \frac{P_n}{P_{n-1}} \times 100"
    )

    assert clean_wikimedia_wikitext(text) == text


def test_removes_broken_leading_heading_marker():
    text = (
        "== Aanaan Jajuu aanaalee keessaa tokko."
    )

    assert clean_wikimedia_wikitext(text) == (
        "Aanaan Jajuu aanaalee keessaa tokko."
    )


def test_removes_broken_trailing_heading_marker():
    text = (
        "Wallee Oromoo ==="
    )

    assert clean_wikimedia_wikitext(text) == (
        "Wallee Oromoo"
    )


def test_removes_orphan_table_control_lines():
    text = (
        "|-\n"
        "Barruu Oromoo\n"
        "|}\n"
        "Keewwata itti aanu."
    )

    assert clean_wikimedia_wikitext(text) == (
        "Barruu Oromoo\n\n"
        "Keewwata itti aanu."
    )