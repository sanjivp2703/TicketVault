"""
Insta485 index (main) view.

URLs include:
/
"""
import flask
from flask import url_for, session, flash
import insta485
import pathlib
import uuid
import datetime

# Custom Jinja2 filter for datetime conversion
@insta485.app.template_filter('datetime')
def format_datetime(value, format='%A, %b %d, %Y at %-I:%M %p'):
    if value is None:
        return ""
    return value.strftime(format)

    if value.tzinfo is None:
        value = utc_tz.localize(value)
        
    local_dt = value.astimezone(eastern_tz)
    return local_dt.strftime(format)

def check_login():
    """Check if user is logged in."""
    test_login = 'email' not in flask.session
    if test_login:
        return flask.redirect(flask.url_for('show_accounts', url='login'))
    return False

@insta485.app.route('/favicon.ico')
def favicon():
    return "", 204


@insta485.app.route('/')
def show_index_orig():
    if 'email' in flask.session:
        connection = insta485.model.get_db()
        user = connection.execute(
            'SELECT is_admin FROM users WHERE email = ?',
            (flask.session['email'],)
        ).fetchone()
        if user and user['is_admin']:
            return flask.redirect(url_for('admin_dashboard'))
        else:
            return flask.redirect(url_for('show_index', user_type='buyer'))
    else:
        return flask.redirect(url_for('show_accounts', url='login'))

@insta485.app.route('/<user_type>')
def show_index(user_type):
    if check_login():
        return check_login()

    logemail = flask.session['email']
    connection = insta485.model.get_db()

    if user_type not in ['buyer', 'seller']:
        return flask.redirect(url_for('show_index', user_type='buyer'))

    # Check admin status
    user = connection.execute(
        'SELECT is_admin FROM users WHERE email = ?',
        (logemail,)
    ).fetchone()
    is_admin = user and user['is_admin']

    if user_type == "buyer":
        transactions = connection.execute(
            "SELECT t.transaction_id, e.name AS ticket_description, t.seller_email, t.price, e.location, e.event_datetime, t.status, t.expected_ticket_send_time, t.complaint_reason, t.buyer_cancel_requested, t.seller_cancel_requested "
            "FROM transactions t "
            "JOIN events e ON t.event_id = e.event_id "
            "WHERE t.buyer_email = ?",
            (logemail,)
        ).fetchall()

    else:  # seller
        transactions = connection.execute(
            "SELECT t.transaction_id, e.name AS ticket_description, t.buyer_email, t.price, e.location, e.event_datetime, t.status, t.expected_ticket_send_time, t.complaint_reason, t.buyer_cancel_requested, t.seller_cancel_requested "
            "FROM transactions t "
            "JOIN events e ON t.event_id = e.event_id "
            "WHERE t.seller_email = ?",
            (logemail,)
        ).fetchall()

    formatted_transactions = []
    now = datetime.datetime.now()

    from insta485.views.manage import send_payment_seller
    for trans in transactions:
        trans_dict = dict(trans)
        # --- AUTO-UPDATE STATUS TO 'event_occurred' IF EVENT TIME PASSED ---
        event_dt = datetime.datetime.strptime(trans['event_datetime'], '%Y-%m-%d %H:%M:%S')
        # 1. Promote to event_occurred if event time passed
        if trans['status'] in ('waiting_for_ticket_transfer', 'ticket_sent') and now >= event_dt:
            connection.execute(
                "UPDATE transactions SET status = 'event_occurred' WHERE transaction_id = ?",
                (trans['transaction_id'],)
            )
            trans_dict['status'] = 'event_occurred'
        # 2. Promote to success if 1 min after event time and status is event_occurred
        elif trans['status'] == 'event_occurred' and now > (event_dt + datetime.timedelta(minutes=1)):
            connection.execute(
                "UPDATE transactions SET status = 'success' WHERE transaction_id = ?",
                (trans['transaction_id'],)
            )
            trans_dict['status'] = 'success'
            send_payment_seller(trans['transaction_id'])
        # Convert expected_ticket_send_time to datetime if present
        if trans_dict.get('expected_ticket_send_time'):
            trans_dict['expected_ticket_send_time'] = datetime.datetime.strptime(
                trans_dict['expected_ticket_send_time'], '%Y-%m-%d %H:%M:%S'
            )
        if trans_dict.get('status') == 'waiting_for_ticket_transfer' and trans_dict.get('expected_ticket_send_time'):
            deadline = trans_dict['expected_ticket_send_time']
            trans_dict['transfer_deadline_passed'] = now > deadline
            # Pass the deadline as a formatted string
            trans_dict['transfer_deadline'] = deadline.strftime('%Y-%m-%d %I:%M %p')
        else:
            trans_dict['transfer_deadline_passed'] = False

        # Pass the event datetime as a formatted string
        event_dt = datetime.datetime.strptime(trans_dict['event_datetime'], '%Y-%m-%d %H:%M:%S')
        trans_dict['event_datetime_str'] = event_dt.strftime('%Y-%m-%d %I:%M %p')
        trans_dict['event_started'] = now >= event_dt

        # Allow problem reporting for up to 1 minute after the event
        problem_report_deadline = event_dt + datetime.timedelta(minutes=1)
        trans_dict['can_report_problem'] = now <= problem_report_deadline
        trans_dict['problem_report_deadline_str'] = problem_report_deadline.strftime('%Y-%m-%d %I:%M %p')

        formatted_transactions.append(trans_dict)

    context = {
        'user_type': user_type,
        'logemail': logemail,
        'transactions': formatted_transactions,
        'is_admin': is_admin
    }
    return flask.render_template("index.html", **context)


@insta485.app.route('/uploads/<filename>')
def get_image(filename):
    """Serve image from uploads folder."""
    try:
        return flask.send_from_directory(insta485.app.config['UPLOAD_FOLDER'],
                                         filename)
    except FileNotFoundError:
        return flask.abort(404)

@insta485.app.route('/accounts/<url>/', methods=['POST', 'GET'])
def show_accounts(url):
    """Display /accounts/<url> route."""
    link_dict = {
        "login": login,
        "create": create,
        "delete": delete,
        "edit": edit,
        "password": password,
    }

    if url in link_dict:
        return link_dict[url]()
    return None


@insta485.app.route('/accounts/login', methods=['GET', 'POST'])
def login():
    """Display /accounts/login route."""
    if 'email' in flask.session:
        # Check if admin
        connection = insta485.model.get_db()
        user = connection.execute(
            'SELECT is_admin FROM users WHERE email = ?',
            (flask.session['email'],)
        ).fetchone()
        if user and user['is_admin']:
            return flask.redirect(url_for('admin_dashboard'))
        else:
            return flask.redirect(url_for('show_index', user_type='buyer'))
    return flask.render_template("login.html")


def create():
    """Display /accounts/create route and handle POST requests."""
    if flask.request.method == 'POST':
        try:
            insta485.views.manage.manage_create()
        except flask.helpers.HTTPException as e:
            if e.code == 409:
                return flask.render_template("create.html", error="User with that email already exists."), 409
            return flask.render_template("create.html", error="All fields are required."), 400
        return flask.redirect(url_for('show_index_orig'))

    if 'email' in flask.session:
        return flask.redirect(url_for('show_accounts', url='edit'))
    return flask.render_template("create.html")


def delete():
    """Display /accounts/delete route."""
    if 'email' not in flask.session:
        return flask.abort(403)
    logemail_dict = {"logemail": flask.session['email']}
    return flask.render_template("delete.html", **logemail_dict)


def edit():
    """Display /accounts/edit route."""
    if 'email' not in flask.session:
        return flask.abort(403)
    connection = insta485.model.get_db()
    curr = connection.execute(
        "SELECT firstname, lastname, email "
        "FROM users "
        "WHERE email == ? ",
        (flask.session['email'], )
    )
    user = curr.fetchone()
    logemail_dict = {"logemail": flask.session['email']}
    return flask.render_template("edit.html", user=user, **logemail_dict)

def password():
    """Display /accounts/password route."""
    if 'email' not in flask.session:
        return flask.abort(403)
    logemail_dict = {"logemail": flask.session['email']}
    return flask.render_template("password.html", **logemail_dict)


@insta485.app.route('/accounts/logout/')
def logout():
    """Log out user."""
    flask.session.clear()
    return flask.redirect(url_for('show_accounts', url='login'))


@insta485.app.route('/api/events', methods=['GET'])
def get_events():
    """Return a list of events for autocomplete."""
    query = flask.request.args.get('q', '')
    connection = insta485.model.get_db()
    events = connection.execute(
        "SELECT name, location, event_datetime FROM events WHERE name LIKE ? OR location LIKE ? LIMIT 10",
        (f"%{query}%", f"%{query}%")
    ).fetchall()
    results = []
    for row in events:
        event_dt = datetime.datetime.strptime(row['event_datetime'], '%Y-%m-%d %H:%M:%S')
        results.append({
            'name': row['name'],
            'location': row['location'],
            'datetime': event_dt.strftime('%A, %b %d, %Y at %-I:%M %p')
        })
    return flask.jsonify(results)

@insta485.app.route('/transactions/', methods=['POST'])
def initiate_transaction():
    """Initiate a new transaction."""
    if 'email' not in flask.session:
        return flask.redirect(url_for('show_accounts', url='login'))

    logemail = flask.session['email']
    user_type = flask.request.form.get('user_type', 'buyer')
    connection = insta485.model.get_db()

    if user_type == 'buyer':
        # This logic is outdated due to schema changes and will likely fail.
        seller_email = flask.request.form.get('seller_email')
        if logemail == seller_email:
            flask.abort(400, "You cannot create a transaction with yourself.")
        price = flask.request.form.get('price')
        ticket_description = flask.request.form.get('ticket_description')
        connection.execute(
            "INSERT INTO transactions (buyer_email, seller_email, price, ticket_description) "
            "VALUES (?, ?, ?, ?)",
            (logemail, seller_email, price, ticket_description)
        )
        flask.flash('Thank you for your purchase! The seller will transfer your ticket within 2 days of acceptance.', 'success')
    elif user_type == 'seller':
        # Logic for seller initiating a transaction
        buyer_email = flask.request.form.get('buyer')
        if logemail == buyer_email:
            flask.abort(400, "You cannot create a transaction with yourself.")
        price = flask.request.form.get('price')
        event_name = flask.request.form.get('ticket_description')

        event_row = connection.execute(
            "SELECT event_id FROM events WHERE name = ?",
            (event_name,)
        ).fetchone()

        if not event_row:
            flask.abort(404, "Event not found")

        event_id = event_row['event_id']

        connection.execute(
            "INSERT INTO transactions (seller_email, buyer_email, price, event_id) "
            "VALUES (?, ?, ?, ?)",
            (logemail, buyer_email, price, event_id)
        )

    return flask.redirect(url_for('show_index', user_type=user_type))

@insta485.app.route('/update_transaction_status/<int:transaction_id>', methods=['POST'])
def update_transaction_status(transaction_id):
    """Update the status of a transaction."""
    if 'email' not in flask.session:
        return flask.redirect(url_for('show_accounts', url='login'))

    logemail = flask.session['email']
    connection = insta485.model.get_db()

    transaction = connection.execute(
        "SELECT buyer_email FROM transactions WHERE transaction_id = ?",
        (transaction_id,)
    ).fetchone()

    if not transaction or transaction['buyer_email'] != logemail:
        flask.abort(403)

    new_status = flask.request.form.get('status')
    if new_status == 'waiting_for_payment_processing':
        connection.execute(
            "UPDATE transactions SET status = 'waiting_for_payment_processing' WHERE transaction_id = ?",
            (transaction_id,)
        )
        return insta485.views.manage.send_payment_buyer(transaction_id)
    elif new_status == 'rejected':
        connection.execute(
            "UPDATE transactions SET status = 'rejected' WHERE transaction_id = ?",
            (transaction_id,)
        )

    return flask.redirect(url_for('show_index', user_type='buyer'))


@insta485.app.route('/success')
def payment_success():
    """Handle successful payment by updating status and expected_ticket_send_time."""
    if 'transaction_id' not in flask.session:
        return flask.redirect(url_for('show_index', user_type='buyer'))

    transaction_id = flask.session.pop('transaction_id', None)
    connection = insta485.model.get_db()

    # Get event time for this transaction
    row = connection.execute(
        """
        SELECT e.event_datetime, t.payment_processed_time 
        FROM transactions t 
        JOIN events e ON t.event_id = e.event_id 
        WHERE t.transaction_id = ?
        """,
        (transaction_id,)
    ).fetchone()
    
    if row:
        # Get current time as payment processed time if not already set
        if not row['payment_processed_time']:
            # Store payment_processed_time as naive local time (no timezone info)
            payment_processed_time = datetime.datetime.now().replace(second=0, microsecond=0)
            # Update the payment_processed_time in the database (naive string)
            connection.execute(
                "UPDATE transactions SET payment_processed_time = ? WHERE transaction_id = ?",
                (payment_processed_time.strftime('%Y-%m-%d %H:%M:%S'), transaction_id)
            )
        else:
            # Convert string to datetime if it's a string
            if isinstance(row['payment_processed_time'], str):
                # Always interpret as naive local time
                payment_processed_time = datetime.datetime.strptime(
                    row['payment_processed_time'], 
                    '%Y-%m-%d %H:%M:%S'
                )
            else:
                payment_processed_time = row['payment_processed_time']
        
        # Parse event time
        event_time = datetime.datetime.strptime(row['event_datetime'], '%Y-%m-%d %H:%M:%S')
        # Ensure both are naive (no tzinfo)

        time_to_event = (event_time - payment_processed_time).total_seconds() / 3600.0
        
        print(f"[DEBUG] payment_processed_time: {payment_processed_time}")
        print(f"[DEBUG] event_time: {event_time}")
        print(f"[DEBUG] time_to_event (hours): {time_to_event}")
        
        if time_to_event > 2:
            # If event is more than 2 hours away, give seller 2 hours from payment processing
            expected_send = (payment_processed_time + datetime.timedelta(hours=2)).replace(second=0, microsecond=0)
        elif 1 < time_to_event <= 2:
            # If event is 1-2 hours away, set deadline to 30 minutes before event
            expected_send = (event_time - datetime.timedelta(minutes=30)).replace(second=0, microsecond=0)
        else:  # Event is less than 1 hour away
            # Give seller 1 minute to send the ticket from the time of payment processing
            expected_send = (payment_processed_time + datetime.timedelta(minutes=1)).replace(second=0, microsecond=0)
        
        print(f"[DEBUG] expected_ticket_send_time: {expected_send}")
        
        connection.execute(
            """
            UPDATE transactions 
            SET status = 'waiting_for_ticket_transfer', 
                expected_ticket_send_time = ? 
            WHERE transaction_id = ?
            """,
            (expected_send.strftime('%Y-%m-%d %H:%M:%S'), transaction_id)
        )
    else:
        connection.execute(
            "UPDATE transactions SET status = 'waiting_for_ticket_transfer' WHERE transaction_id = ?",
            (transaction_id,)
        )
    return flask.redirect(url_for('show_index', user_type='buyer'))

@insta485.app.route('/cancel', methods=['GET', 'POST'])
def payment_cancel():
    """Handle cancelled payment: mark cancel requested, cancel if both agree."""
    connection = insta485.model.get_db()
    if flask.request.method == 'POST':
        transaction_id = flask.request.form.get('transaction_id')
        user_type = flask.request.form.get('user_type')
        if not transaction_id or not user_type:
            flask.flash('Missing transaction or user info')
            return flask.redirect(url_for('show_index', user_type='buyer'))
        # Fetch transaction
        transaction = connection.execute(
            "SELECT buyer_cancel_requested, seller_cancel_requested FROM transactions WHERE transaction_id = ?",
            (transaction_id,)
        ).fetchone()
        if not transaction:
            flask.flash('Transaction not found')
            return flask.redirect(url_for('show_index', user_type='buyer'))
        # Mark cancel requested
        if user_type == 'buyer':
            connection.execute(
                "UPDATE transactions SET buyer_cancel_requested = 1 WHERE transaction_id = ?",
                (transaction_id,)
            )
        elif user_type == 'seller':
            connection.execute(
                "UPDATE transactions SET seller_cancel_requested = 1 WHERE transaction_id = ?",
                (transaction_id,)
            )
        # Check if both requested
        transaction = connection.execute(
            "SELECT buyer_cancel_requested, seller_cancel_requested FROM transactions WHERE transaction_id = ?",
            (transaction_id,)
        ).fetchone()
        if transaction['buyer_cancel_requested'] and transaction['seller_cancel_requested']:
            connection.execute(
                "UPDATE transactions SET status = 'cancelled' WHERE transaction_id = ?",
                (transaction_id,)
            )
            print(f"[PAYMENT] Safe-Transaction refunded buyer for transaction {transaction_id} (double cancellation).")
        connection.commit()
        flask.flash('Cancellation request submitted.')
        return flask.redirect(url_for('show_index', user_type=user_type))
    # GET fallback
    return flask.redirect(url_for('show_index', user_type='buyer'))

@insta485.app.route('/ticket_status/<int:transaction_id>', methods=['POST'])
def update_ticket_status(transaction_id):
    from insta485.views.manage import send_payment_seller
    """Update the status of the ticket transfer."""
    if 'email' not in flask.session:
        return flask.redirect(url_for('show_accounts', url='login'))

    logemail = flask.session['email']
    connection = insta485.model.get_db()
    action = flask.request.form.get('action')

    # Verify user is part of the transaction
    transaction = connection.execute(
        "SELECT seller_email, buyer_email FROM transactions WHERE transaction_id = ?",
        (transaction_id,)
    ).fetchone()

    if not transaction or (logemail != transaction['seller_email'] and logemail != transaction['buyer_email']):
        flask.abort(403)

    user_type = 'seller' if logemail == transaction['seller_email'] else 'buyer'

    if action == 'sent' and user_type == 'seller':
        connection.execute(
            "UPDATE transactions SET status = 'ticket_sent' WHERE transaction_id = ?",
            (transaction_id,)
        )
        flask.flash("You've confirmed sending the ticket. The buyer will be notified.")
    elif action == 'received' and user_type == 'buyer':
        # Buyer confirms ticket worked: mark as success, send payment
        connection.execute(
            "UPDATE transactions SET status = 'success' WHERE transaction_id = ?",
            (transaction_id,)
        )
        send_payment_seller(transaction_id)
        payment = connection.execute(
            "SELECT price FROM transactions WHERE transaction_id = ?",
            (transaction_id,)
        ).fetchone()['price']
        # After marking success, redirect to dashboard so the card updates in-place
        return flask.redirect(url_for('show_index', user_type=user_type))


    return flask.redirect(url_for('show_index', user_type=user_type))


@insta485.app.route('/report_problem/<int:transaction_id>', methods=['POST'])
def report_problem(transaction_id):
    """Handle problem reports from the buyer."""
    if 'email' not in flask.session:
        return flask.redirect(url_for('show_accounts', url='login'))

    logemail = flask.session['email']
    connection = insta485.model.get_db()

    # Verify user is the buyer for this transaction
    transaction = connection.execute(
        "SELECT buyer_email FROM transactions WHERE transaction_id = ?",
        (transaction_id,)
    ).fetchone()

    if not transaction or logemail != transaction['buyer_email']:
        flask.abort(403)

    reason = flask.request.form.get('reason')
    if reason == 'Other':
        complaint_reason = flask.request.form.get('other_reason', 'Other issue reported by buyer.')
    else:
        complaint_reason = reason

    connection.execute(
        "UPDATE transactions SET status = 'complaint_filed', complaint_reason = ? WHERE transaction_id = ?",
        (complaint_reason, transaction_id)
    )
    flash("Your complaint has been filed. We will review the issue.")

    return flask.redirect(url_for('show_index', user_type='buyer'))

    return flask.redirect(url_for('show_index', user_type=user_type))
