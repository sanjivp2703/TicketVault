"""Configuration is sourced from the environment, never from source code."""

import pathlib
import re

import insta485

ROOT = pathlib.Path(__file__).resolve().parent.parent

SECRET_PATTERNS = [
    re.compile(r"sk_(live|test)_[A-Za-z0-9]{16,}"),  # Stripe secret keys
    re.compile(r"[0-9a-f]{32}-[0-9a-f]{8}-[0-9a-f]{8}"),  # Mailgun API keys
    re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}"),  # GitHub tokens
]


def test_secrets_come_from_the_environment():
    assert insta485.app.config["SECRET_KEY"]
    assert insta485.app.config["SESSION_COOKIE_NAME"] == "login"
    assert insta485.app.config["ENABLE_DEV_LOGIN"] in (True, False)


def test_no_credentials_are_committed_in_source():
    offenders = []
    for path in list((ROOT / "insta485").rglob("*.py")) + list(
        (ROOT / "bin").glob("*")
    ):
        if not path.is_file():
            continue
        text = path.read_text(errors="ignore")
        if any(pattern.search(text) for pattern in SECRET_PATTERNS):
            offenders.append(str(path.relative_to(ROOT)))
    assert offenders == []
