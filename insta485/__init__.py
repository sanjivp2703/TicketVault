"""Safe Transaction application package.

The package keeps its historical name (``insta485``) because the production
service, CLI scripts and database paths all reference it.
"""

import logging

import flask
from apscheduler.schedulers.background import BackgroundScheduler
from flask_mail import Mail

# app is a single object used by all the code modules in this package
app = flask.Flask(__name__)  # pylint: disable=invalid-name

# Read settings from config module (insta485/config.py)
app.config.from_object("insta485.config")

# Overlay settings read from a Python file whose path is set in the environment
# variable INSTA485_SETTINGS. Setting this environment variable is optional.
app.config.from_envvar("INSTA485_SETTINGS", silent=True)

for _setting in ("STRIPE_SECRET_KEY", "MAILGUN_API_KEY", "MAILGUN_DOMAIN"):
    if not app.config.get(_setting):
        logging.getLogger(__name__).warning(
            "%s is not configured; the features that depend on it will fail.",
            _setting,
        )

mail = Mail(app)

# Background scheduler used by the (currently disabled) automated workflow.
scheduler = BackgroundScheduler()
scheduler.start()
app.scheduler = scheduler


def start_automated_jobs():
    """Start the automated deadline checker and inbound email monitor.

    The platform currently runs in manual-operations mode, so this is not
    called at startup. Call it (and re-enable the ``deadline_manager`` and
    ``email_monitor`` imports below) to turn automation back on.
    """
    try:
        from insta485.email_monitor import email_monitor
        from insta485.transaction_manager import TransactionManager

        transaction_manager = TransactionManager()

        # Schedule deadline checking every 5 minutes
        scheduler.add_job(
            func=transaction_manager.check_scheduled_deadlines,
            trigger="interval",
            minutes=5,
            id="deadline_checker",
            replace_existing=True,
        )

        # Start email monitoring
        email_monitor.start()

        print("✅ Automated background jobs started successfully")

    except Exception as e:
        print(f"❌ Error starting background jobs: {e}")


@app.template_filter("format_datetime")
def format_datetime(value, format="%Y-%m-%d %I:%M %p"):
    """Format a datetime object as a string (default: YYYY-MM-DD HH:MM AM/PM)."""
    if value is None:
        return ""
    return value.strftime(format)


# Tell our app about views and model.  This is dangerously close to a
# circular import, which is naughty, but Flask was designed that way.
# (Reference http://flask.pocoo.org/docs/patterns/packages/)
import insta485.model  # noqa: E402  pylint: disable=wrong-import-position
import insta485.views  # noqa: E402  pylint: disable=wrong-import-position
import insta485.api  # noqa: E402  pylint: disable=wrong-import-position
import insta485.email_webhook  # noqa: E402  pylint: disable=wrong-import-position

# Disabled while the platform runs in manual-operations mode:
# import insta485.deadline_manager
# import insta485.email_monitor
