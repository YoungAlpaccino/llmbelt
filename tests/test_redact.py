from llmbelt import find_pii, redact


def test_redacts_email():
    assert redact("contact me at jane.doe@example.com please") == (
        "contact me at [EMAIL] please"
    )


def test_redacts_phone():
    out = redact("call 555-123-4567 now")
    assert "[PHONE]" in out
    assert "555" not in out


def test_redacts_credit_card():
    out = redact("card 4111 1111 1111 1111 on file")
    assert "[CREDIT_CARD]" in out
    assert "4111" not in out


def test_redacts_ssn():
    assert "[SSN]" in redact("ssn 123-45-6789")


def test_redacts_ip():
    assert redact("server at 192.168.1.1") == "server at [IP]"


def test_redacts_api_key():
    out = redact("key sk-ABCD1234abcd5678efgh used")
    assert "[API_KEY]" in out
    assert "sk-ABCD1234" not in out


def test_redacts_aws_key():
    assert "[AWS_KEY]" in redact("AKIAIOSFODNN7EXAMPLE")


def test_no_pii_unchanged():
    text = "just a normal sentence with no secrets"
    assert redact(text) == text


def test_empty():
    assert redact("") == ""


def test_custom_mask_callable():
    out = redact("a@b.com", mask=lambda label: f"<{label}>")
    assert out == "<EMAIL>"


def test_mask_is_literal_no_backref_error():
    # A mask containing regex-replacement syntax must not raise or be interpreted.
    out = redact("a@b.com", mask=r"[\1{label}]")
    assert out == r"[\1EMAIL]"


def test_find_pii_lists_matches():
    found = find_pii("mail a@b.com and ip 10.0.0.1")
    labels = {label for label, _ in found}
    assert "EMAIL" in labels
    assert "IP" in labels
    assert ("EMAIL", "a@b.com") in found
