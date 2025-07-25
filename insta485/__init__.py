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

# Flask-Mail configuration for Gmail SMTP
from flask_mail import Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'sanjivp2703@gmail.com'
app.config['MAIL_PASSWORD'] = 'slfa lcwa owan psxe'
app.config['MAIL_DEFAULT_SENDER'] = 'sanjivp2703@gmail.com'
mail = Mail(app)

# Initialize scheduler (no timezone)
scheduler = BackgroundScheduler()
scheduler.start()
app.scheduler = scheduler

# Tell our app about views and model.  This is dangerously close to a
# circular import, which is naughty, but Flask was designed that way.
# (Reference http://flask.pocoo.org/docs/patterns/packages/)  We're
# going to tell pylint and pycodestyle to ignore this coding style violation.
import insta485.model  # noqa: E402  pylint: disable=wrong-import-position
import insta485.views  # noqa: E402  pylint: disable=wrong-import-position
import insta485.api  # noqa: E402  pylint: disable=wrong-import-position

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
