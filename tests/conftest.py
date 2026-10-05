"""Shared pytest fixtures.

Every test runs against a throwaway SQLite database built from
``sql/schema.sql`` and ``sql/data.sql`` so the suite never touches
``var/insta485.sqlite3``.
"""

import os
import pathlib
import sqlite3

import pytest

# Configuration is read at import time, so provide safe test values first.
os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ.setdefault("STRIPE_SECRET_KEY", "sk_test_placeholder")
os.environ.setdefault("MAILGUN_DOMAIN", "mail.example.test")
os.environ.setdefault("MAILGUN_API_KEY", "test-mailgun-key")

import insta485  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent

SELLER_EMAIL = "sanjivp2703@gmail.com"
ADMIN_EMAIL = "admin@gmail.com"
BUYER_EMAIL = "buyer@example.com"

# One transaction per interesting state, all owned by SELLER_EMAIL.
SEEDED_STATUSES = [
    "pending_ticket_submission",
    "waiting_for_verification",
    "waiting_for_payment",
    "ticket_forwarded_funds_held",
    "completed",
    "cancelled",
    "payment_deadline_expired",
    "complaint_filed",
]


@pytest.fixture(name="app")
def app_fixture(tmp_path, monkeypatch):
    """Return the Flask app wired to a freshly seeded temporary database."""
    db_path = tmp_path / "test.sqlite3"
    connection = sqlite3.connect(db_path)
    connection.executescript((ROOT / "sql" / "schema.sql").read_text())
    connection.executescript((ROOT / "sql" / "data.sql").read_text())
    for status in SEEDED_STATUSES:
        connection.execute(
            "INSERT INTO transactions "
            "(buyer_email, seller_email, price, event_id, status, "
            " ticket_deadline, payment_deadline, awaiting_ticket_email) "
            "VALUES (?, ?, 100, 1, ?, "
            " datetime('now', '+1 day'), datetime('now', '+1 day'), ?)",
            (BUYER_EMAIL, SELLER_EMAIL, status, "tickets@mail.example.test"),
        )
    connection.commit()
    connection.close()

    monkeypatch.setitem(insta485.app.config, "DATABASE_FILENAME", db_path)
    monkeypatch.setitem(insta485.app.config, "TESTING", True)
    monkeypatch.setitem(insta485.app.config, "MAIL_SUPPRESS_SEND", True)
    return insta485.app


@pytest.fixture(name="client")
def client_fixture(app):
    """Return an anonymous test client."""
    with app.test_client() as client:
        yield client


def _login(client, email):
    with client.session_transaction() as session:
        session["email"] = email
    return client


@pytest.fixture(name="seller_client")
def seller_client_fixture(client):
    """Return a test client logged in as a regular seller."""
    return _login(client, SELLER_EMAIL)


@pytest.fixture(name="admin_client")
def admin_client_fixture(client):
    """Return a test client logged in as an administrator."""
    return _login(client, ADMIN_EMAIL)
