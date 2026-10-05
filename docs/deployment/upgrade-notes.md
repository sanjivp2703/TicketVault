# Upgrade notes: environment-based configuration

This release removes every credential from source control, stops tracking
runtime data in git, and replaces the per-page inline styles with a shared
design system. Application behaviour is unchanged, but a server that was
deployed from an earlier revision needs the one-time steps below **before**
pulling.

## 1. Back up runtime data

Earlier revisions tracked the SQLite database, uploads, and `.env` in git.
They are now ignored. Because git removes files that stop being tracked, copy
them aside first:

```bash
cd /var/www/safetransaction
cp var/insta485.sqlite3 ~/insta485.sqlite3.backup
cp -r var/uploads ~/uploads.backup 2>/dev/null || true
cp .env ~/env.backup 2>/dev/null || true
```

## 2. Pull, then restore

```bash
sudo git pull origin main
mkdir -p var/uploads
[ -f var/insta485.sqlite3 ] || cp ~/insta485.sqlite3.backup var/insta485.sqlite3
[ -d ~/uploads.backup ] && cp -rn ~/uploads.backup/. var/uploads/
[ -f .env ] || cp ~/env.backup .env 2>/dev/null || cp .env.example .env
```

If `git pull` stops because of local changes to `var/insta485.sqlite3`, move
the file aside (`mv var/insta485.sqlite3 ~/`), run `git checkout -- var/`,
pull, and then copy the backup into place as shown above.

## 3. Provide the configuration

The application no longer contains fallback keys and refuses to start without
`SECRET_KEY`. Set these in `.env` beside the code or in the service
environment:

```ini
SECRET_KEY=<python -c "import secrets; print(secrets.token_hex(32))">
STRIPE_SECRET_KEY=<Stripe secret key>
MAILGUN_DOMAIN=<Mailgun sending domain>
MAILGUN_API_KEY=<Mailgun private API key>
```

Notes:

- Changing `SECRET_KEY` signs every user out once.
- Admin notification emails and automated emails now use the same
  `MAILGUN_DOMAIN`. Previously the admin emails defaulted to
  `safetransaction.app` while the automated ones used the sandbox domain.
- Leave `ENABLE_DEV_LOGIN` unset. The password-less "sign in as seller/admin"
  shortcut is now off unless that flag is set.

## 4. Rotate the credentials that were in git history

The following were committed in earlier revisions and must be treated as
compromised. Rotate them in the respective dashboards and put the new values
in `.env`:

- Mailgun API key
- Stripe test secret key
- The GitHub personal access token that appeared in the deployment notes
- The Flask session key (replaced by `SECRET_KEY` above)
- The private key file `insta485key.pem`

## 5. Install dependencies and restart

```bash
source env/bin/activate        # or venv/bin/activate, whichever the server uses
pip install -r requirements.txt
sudo systemctl restart safetransaction   # or: sudo supervisorctl restart safetransaction
```

Node.js is no longer required; the unused webpack toolchain was removed.

## 6. Verify

- `https://safetransaction.app/accounts/login` loads with the new sign-in page
  and no "development shortcuts" panel.
- `https://safetransaction.app/dev/skip-login/admin` returns 404.
- Create a test listing and confirm the notification email arrives.
