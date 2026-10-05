"""
TicketVault How it Works view.

URLs include:
/how-it-works/
"""

import flask
import insta485


@insta485.app.route("/how-it-works/")
def show_how_it_works():
    """Display the comprehensive How it Works page."""
    return flask.render_template("how_it_works.html")
