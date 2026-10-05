"""Application configuration.

All secrets and deployment-specific values are read from the environment.
For local development, copy ``.env.example`` to ``.env`` at the repository
root; it is loaded automatically at import time. Real environment variables
always take precedence over values in ``.env``.
"""

import os
import pathlib

import stripe
from dotenv import load_dotenv

# Repository root (the directory that contains the ``insta485`` package).
INSTA485_ROOT = pathlib.Path(__file__).resolve().parent.parent

load_dotenv(INSTA485_ROOT / ".env")


def _env_bool(name, default):
    """Read a boolean environment variable."""
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


# --------------------------------------------------------------------------
# Flask
# --------------------------------------------------------------------------

# Root of this application, useful if it doesn't occupy an entire domain.
APPLICATION_ROOT = "/"

# Key used to sign session cookies. Generate one with:
#   python -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError(
        "SECRET_KEY is not set. Copy .env.example to .env and fill it in, "
        "or export SECRET_KEY in the environment."
    )

SESSION_COOKIE_NAME = "login"

# Exposes /dev/skip-login/<user_type> and the shortcut buttons on the sign-in
# page. Development only: it signs anyone in as a seeded seller or admin.
ENABLE_DEV_LOGIN = _env_bool("ENABLE_DEV_LOGIN", False)

# --------------------------------------------------------------------------
# Storage
# --------------------------------------------------------------------------

UPLOAD_FOLDER = INSTA485_ROOT / "var" / "uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024

DATABASE_FILENAME = INSTA485_ROOT / "var" / "insta485.sqlite3"

# --------------------------------------------------------------------------
# Stripe
# --------------------------------------------------------------------------

STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY")
stripe.api_key = STRIPE_SECRET_KEY

# --------------------------------------------------------------------------
# Email (Mailgun HTTP API and SMTP relay, Gmail SMTP for buyer emails)
# --------------------------------------------------------------------------

MAILGUN_DOMAIN = os.environ.get("MAILGUN_DOMAIN", "")
MAILGUN_API_KEY = os.environ.get("MAILGUN_API_KEY", "")
MAILGUN_BASE_URL = os.environ.get(
    "MAILGUN_BASE_URL", f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}"
)

MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.mailgun.org")
MAIL_PORT = int(os.environ.get("MAIL_PORT", "587"))
MAIL_USE_TLS = _env_bool("MAIL_USE_TLS", True)
MAIL_USERNAME = os.environ.get("MAIL_USERNAME", f"postmaster@{MAILGUN_DOMAIN}")
MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", MAILGUN_API_KEY)
MAIL_DEFAULT_SENDER = os.environ.get(
    "MAIL_DEFAULT_SENDER", f"Safe Transaction <noreply@{MAILGUN_DOMAIN}>"
)

GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "")
