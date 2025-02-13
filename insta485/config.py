"""Insta485 development configuration."""

import pathlib
import stripe
import os

# Root of this application, useful if it doesn't occupy an entire domain
APPLICATION_ROOT = '/'

# Secret key for encrypting cookies
SECRET_KEY = b'|V\x9f\xad\xa8\xd2\x1e\xcd\xfa-\x84\x12\xb6;\xfa#\x9f\x1a\
              x0e\x10\xbd\x00|\x1b'
SESSION_COOKIE_NAME = 'login'

# File Upload to var/uploads/
INSTA485_ROOT = pathlib.Path(__file__).resolve().parent.parent
UPLOAD_FOLDER = INSTA485_ROOT/'var'/'uploads'
ASSET_FOLDER = INSTA485_ROOT/'assets'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
MAX_CONTENT_LENGTH = 16 * 1024 * 1024

# Database file is var/insta485.sqlite3
DATABASE_FILENAME = INSTA485_ROOT/'var'/'insta485.sqlite3'

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")  # Load secret key from environment variables
MIDDLEMAN_STRIPE_ACCOUNT = "acct_xxxxxxxxxxxxxx"  # Replace with your Stripe business account ID

