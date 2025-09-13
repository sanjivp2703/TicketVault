"""Insta485 package initializer."""
import flask
from apscheduler.schedulers.background import BackgroundScheduler

# app is a single object used by all the code modules in this package
app = flask.Flask(__name__)  # pylint: disable=invalid-name

# Read settings from config module (insta485/config.py)
app.config.from_object('insta485.config')

# Overlay settings read from a Python file whose path is set in the environment
# variable INSTA485_SETTINGS. Setting this environment variable is optional.
# Docs: http://flask.pocoo.org/docs/latest/config/
#
# EXAMPLE:
# $ export INSTA485_SETTINGS=secret_key_config.py
app.config.from_envvar('INSTA485_SETTINGS', silent=True)

# Mailgun configuration for Safe Transaction
from flask_mail import Mail

# Mailgun SMTP Configuration
app.config['MAIL_SERVER'] = 'smtp.mailgun.org'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'postmaster@sandboxb9b4c56251404e08939d238b07603aff.mailgun.org'
app.config['MAIL_PASSWORD'] = 'd3fac427288306d90280459b2faddb07-1ae02a08-43aa9974'  # Your API key
app.config['MAIL_DEFAULT_SENDER'] = 'Safe Transaction <noreply@sandboxb9b4c56251404e08939d238b07603aff.mailgun.org>'

# Mailgun API Configuration
app.config['MAILGUN_DOMAIN'] = 'sandboxb9b4c56251404e08939d238b07603aff.mailgun.org'
app.config['MAILGUN_API_KEY'] = 'd3fac427288306d90280459b2faddb07-1ae02a08-43aa9974'
app.config['MAILGUN_BASE_URL'] = 'https://api.mailgun.net/v3/sandboxb9b4c56251404e08939d238b07603aff.mailgun.org'

mail = Mail(app)

# Initialize scheduler (no timezone)
scheduler = BackgroundScheduler()
scheduler.start()
app.scheduler = scheduler

# Start background jobs for automated processing
def start_automated_jobs():
    """Start automated background jobs for transaction processing"""
    try:
        from insta485.transaction_manager import TransactionManager
        from insta485.email_monitor import email_monitor
        
        transaction_manager = TransactionManager()
        
        # Schedule deadline checking every 5 minutes
        scheduler.add_job(
            func=transaction_manager.check_scheduled_deadlines,
            trigger="interval",
            minutes=5,
            id='deadline_checker',
            replace_existing=True
        )
        
        # Start email monitoring
        email_monitor.start()
        
        print("✅ Automated background jobs started successfully")
        
    except Exception as e:
        print(f"❌ Error starting background jobs: {e}")

# Start background jobs when app initializes
start_automated_jobs()

# Tell our app about views and model.  This is dangerously close to a
# circular import, which is naughty, but Flask was designed that way.
# (Reference http://flask.pocoo.org/docs/patterns/packages/)  We're
# going to tell pylint and pycodestyle to ignore this coding style violation.
import insta485.model  # noqa: E402  pylint: disable=wrong-import-position
import insta485.views  # noqa: E402  pylint: disable=wrong-import-position
import insta485.api  # noqa: E402  pylint: disable=wrong-import-position
import insta485.email_webhook  # noqa: E402  pylint: disable=wrong-import-position
import insta485.deadline_manager  # noqa: E402  pylint: disable=wrong-import-position
import insta485.email_monitor  # noqa: E402  pylint: disable=wrong-import-position

# Add custom template filter for datetime formatting
from datetime import datetime

@app.template_filter('format_datetime')
def format_datetime(value, format='%Y-%m-%d %I:%M %p'):
    """Format a datetime object to a string.
    Default format: YYYY-MM-DD HH:MM AM/PM
    """
    if value is None:
        return ""
    return value.strftime(format)
