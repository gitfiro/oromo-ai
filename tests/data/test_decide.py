from oromo_ai.data.decide import decide_record


def test_base64_is_rejected():
    text = (
        "REFTEST IMAGE data:image/png;base64,"
        + "A" * 300
    )

    decision, reasons = decide_record(text)

    assert decision == "REJECT"
    assert "base64_or_data_uri" in reasons


def test_genomic_record_is_rejected():
    text = (
        "30 p-mmpP2C11 genomic DNA mmp21 "
        + "AABBABAAA-" * 20
    )

    decision, _ = decide_record(text)

    assert decision == "REJECT"


def test_oromo_prose_with_url_is_cleaned():
    text = (
        "Haalli Yuniversitii Jimmaa keessa jiru "
        "daran yaadessadha – https://example.com"
    )

    decision, reasons = decide_record(text)

    assert decision == "CLEAN"
    assert "url_or_web_payload" in reasons


def test_html_with_oromo_prose_is_cleaned():
    text = (
        "<blockquote>Yaa haadha too yaa Tarrafuu<br>"
        "Tokko du’ee lamat hafuu</blockquote>"
    )

    decision, _ = decide_record(text)

    assert decision == "CLEAN"


def test_legitimate_numeric_oromo_is_kept():
    text = (
        "Bara mootiichaa jalqabee nootiin birrii "
        "1, 5, 10, 50 fi 100 hojiirra oolaa turan."
    )

    decision, _ = decide_record(text)

    assert decision == "KEEP"


def test_legitimate_repetition_is_kept():
    text = "Filannoon osoo hin jalqabamiin xumurameeee!"

    decision, _ = decide_record(text)

    assert decision == "KEEP"


def test_underscore_formatting_is_kept():
    text = "___________guyyaa har’aa, Caffee kana duratti ykn Koree"

    decision, _ = decide_record(text)

    assert decision == "KEEP"


def test_social_media_spam_is_rejected():
    text = (
        "#follow #model #photography #instagram "
        "#trending #fashion #viral #like #follow #cute"
    )

    decision, _ = decide_record(text)

    assert decision == "REJECT"

def test_wordpress_post_wrapper_is_cleaned():
    text = (
        "WBO Jecha [Read More] "
        "The post Walaloo Ajaa ibaa Waraana Bilisummaa Oromootiif "
        "Lataa Qana ii Aagaatiin Must watch appeared first on ."
    )

    decision, reasons = decide_record(text)

    assert decision == "CLEAN"
    assert "cms_or_social_metadata" in reasons


def test_legitimate_the_post_text_is_kept():
    text = (
        "The post explains how Afaan Oromoo speakers use "
        "different regional expressions."
    )

    decision, _ = decide_record(text)

    assert decision == "KEEP"


def test_cleaning_does_not_create_empty_record():
    text = "[Read More] https://example.com"

    decision, _ = decide_record(text)

    assert decision == "CLEAN"


def test_legitimate_oromo_with_comments_wording_is_kept():
    text = (
        "Namoonni waa'ee Comments Off jedhu irratti mari'atan."
    )

    decision, _ = decide_record(text)

    assert decision == "KEEP"