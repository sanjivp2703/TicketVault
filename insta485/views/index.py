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
from insta485.email_utils import send_accept_confirmation_email, send_reject_confirmation_email

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

        cursor = connection.execute(
            "INSERT INTO transactions (seller_email, buyer_email, price, event_id) "
            "VALUES (?, ?, ?, ?)",
            (logemail, buyer_email, price, event_id)
        )
        transaction_id = cursor.lastrowid
        # Send email notification to buyer with Accept/Reject buttons
        from insta485.email_utils import send_email
        subject = f"You have a new ticket offer for {event_name}!"
        body = f"Hello,\n\nYou have received a new ticket offer for '{event_name}'.\nPrice: ${price}\nSeller: {logemail}\n\nPlease log in to Safe-Transaction to view and accept or reject the offer.\n\nBest,\nSafe-Transaction Team"
        # Build Accept/Reject URLs
        accept_url = flask.url_for('email_accept', transaction_id=transaction_id, _external=True)
        reject_url = flask.url_for('update_transaction_status', transaction_id=transaction_id, _external=True)
        html = f'''
            <p>Hello,</p>
            <p>You have received a new ticket offer for <b>{event_name}</b>.<br>
            Price: <b>${price}</b><br>
            Seller: <b>{logemail}</b></p>
            <a href="{accept_url}" style="background:#28a745;color:white;padding:10px 18px;text-decoration:none;border-radius:4px;font-weight:bold;display:inline-block;">Accept</a>
            <form action="{reject_url}" method="post" style="display:inline;margin-left:10px;">
                <input type="hidden" name="status" value="rejected">
                <button style="background:#dc3545;color:white;padding:8px 16px;border:none;border-radius:4px;cursor:pointer;">Reject</button>
            </form>
            <p style="margin-top:24px;">Best,<br>Safe-Transaction Team</p>
        '''
        send_email(buyer_email, subject, body, html=html)

    return flask.redirect(url_for('show_index', user_type=user_type))

@insta485.app.route('/update_transaction_status/<int:transaction_id>', methods=['POST'])
def update_transaction_status(transaction_id):
    """Update the status of a transaction. No login or buyer check (email or dashboard)."""
    new_status = flask.request.form.get('status')
    connection = insta485.model.get_db()
    row = connection.execute(
        "SELECT status, buyer_email, seller_email, event_id FROM transactions WHERE transaction_id = ?",
        (transaction_id,)
    ).fetchone()
    if not row:
        return "<html><body><h2>Transaction not found.</h2></body></html>"
    # Get event name for email
    event_name = None
    if row['event_id']:
        event_row = connection.execute(
            "SELECT name FROM events WHERE event_id = ?",
            (row['event_id'],)
        ).fetchone()
        if event_row:
            event_name = event_row['name']
    # Allow Reject if status is waiting_for_payment_processing (payment not completed)
    if new_status == 'rejected':
        if row['status'] == 'rejected':
            return "<html><body><h2>You have already rejected this offer.</h2></body></html>"
        elif row['status'] in ('waiting_for_ticket_transfer', 'success', 'complete'):
            return "<html><body><h2>You have already accepted this offer. You may close this tab.</h2></body></html>"
        # Allow rejection if still waiting for payment
        connection.execute(
            "UPDATE transactions SET status = 'rejected' WHERE transaction_id = ?",
            (transaction_id,)
        )
        # Send rejection confirmation email
        if row['buyer_email'] and event_name and row['seller_email']:
            send_reject_confirmation_email(row['buyer_email'], event_name, row['seller_email'])
        return "<html><body><h2>The offer has been rejected. You may now close this tab and return to your email.</h2></body></html>"
    # Accept logic
    if row['status'] in ('waiting_for_payment_processing', 'waiting_for_ticket_transfer', 'success', 'complete'):
        return "<html><body><h2>You have already accepted this offer. You may close this tab and return to your email.</h2></body></html>"
    elif row['status'] == 'rejected':
        return "<html><body><h2>You have already rejected this offer.</h2></body></html>"
    if new_status == 'waiting_for_payment_processing':
        connection.execute(
            "UPDATE transactions SET status = 'waiting_for_payment_processing' WHERE transaction_id = ?",
            (transaction_id,)
        )
        return insta485.views.manage.send_payment_buyer(transaction_id)
    return "<html><body><h2>Action completed.</h2></body></html>"

@insta485.app.route('/email_accept/<int:transaction_id>', methods=['GET'])
def email_accept(transaction_id):
    """Handle Accept button from email: set status and redirect to Stripe, then show thank you after payment."""
    connection = insta485.model.get_db()
    row = connection.execute(
        "SELECT status FROM transactions WHERE transaction_id = ?",
        (transaction_id,)
    ).fetchone()
    if not row:
        return "<html><body><h2>Transaction not found.</h2></body></html>"
    if row['status'] in ('waiting_for_payment_processing', 'waiting_for_ticket_transfer', 'success', 'complete'):
        return "<html><body><h2>You have already accepted this offer. You may close this tab and return to your email.</h2></body></html>"
    elif row['status'] == 'rejected':
        return "<html><body><h2>You have already rejected this offer.</h2></body></html>"
    connection.execute(
        "UPDATE transactions SET status = 'waiting_for_payment_processing' WHERE transaction_id = ?",
        (transaction_id,)
    )
    return insta485.views.manage.send_payment_buyer(transaction_id)

@insta485.app.route('/success')
def payment_success():
    """Handle successful payment by updating status and expected_ticket_send_time."""
    if 'transaction_id' not in flask.session:
        return "<html><body><h2>Thank you! Your payment was successful. You may now close this tab and return to your email.</h2></body></html>"
    transaction_id = flask.session.pop('transaction_id', None)
    connection = insta485.model.get_db()
    # Get event time and transaction info for confirmation email
    row = connection.execute(
        """
        SELECT t.buyer_email, t.seller_email, t.price, e.name as event_name, e.event_datetime, t.payment_processed_time 
        FROM transactions t 
        JOIN events e ON t.event_id = e.event_id 
        WHERE t.transaction_id = ?
        """,
        (transaction_id,)
    ).fetchone()
    # Calculate expected_send as 1 minute after payment_processed_time (or now if not available)
    import datetime
    payment_time = row['payment_processed_time']
    if payment_time:
        payment_dt = datetime.datetime.strptime(payment_time, '%Y-%m-%d %H:%M:%S')
    else:
        payment_dt = datetime.datetime.now()
    expected_send = payment_dt + datetime.timedelta(minutes=1)
    connection.execute(
        """
        UPDATE transactions 
        SET status = 'waiting_for_ticket_transfer', 
            expected_ticket_send_time = ? 
        WHERE transaction_id = ?
        """,
        (expected_send.strftime('%Y-%m-%d %H:%M:%S'), transaction_id)
    )
    # Send acceptance confirmation email
    if row['buyer_email'] and row['event_name'] and row['price'] and row['seller_email']:
        send_accept_confirmation_email(row['buyer_email'], row['event_name'], row['price'], row['seller_email'], transaction_id=transaction_id)
    else:
        connection.execute(
            "UPDATE transactions SET status = 'waiting_for_ticket_transfer' WHERE transaction_id = ?",
            (transaction_id,)
        )
    return "<html><body><h2>Thank you! Your payment was successful. You may now close this tab and return to your email.</h2></body></html>"

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
            # Send cancellation email to buyer
            transaction_info = connection.execute(
                "SELECT buyer_email, event_id, price, seller_email FROM transactions WHERE transaction_id = ?",
                (transaction_id,)
            ).fetchone()
            event_name = None
            if transaction_info and transaction_info['event_id']:
                event_row = connection.execute(
                    "SELECT name FROM events WHERE event_id = ?",
                    (transaction_info['event_id'],)
                ).fetchone()
                if event_row:
                    event_name = event_row['name']
            if transaction_info and transaction_info['buyer_email'] and event_name:
                try:
                    from insta485.send_cancelled_email import send_cancelled_email
                    send_cancelled_email(
                        transaction_info['buyer_email'],
                        event_name,
                        price=transaction_info['price'],
                        seller_email=transaction_info['seller_email']
                    )
                except Exception as e:
                    print(f"[EMAIL ERROR] Failed to send cancellation email: {e}")
            print(f"[PAYMENT] Safe-Transaction refunded buyer for transaction {transaction_id} (double cancellation).")
        connection.commit()
        flask.flash('Cancellation request submitted.')
        return flask.redirect(url_for('show_index', user_type=user_type))
    # GET fallback
    return flask.redirect(url_for('show_index', user_type='buyer'))

@insta485.app.route('/ticket_status/<int:transaction_id>', methods=['GET', 'POST'])
def update_ticket_status(transaction_id):
    from insta485.views.manage import send_payment_seller
    """Update the status of the ticket transfer."""
    connection = insta485.model.get_db()
    # Allow GET for email button actions
    if flask.request.method == 'POST':
        action = flask.request.form.get('action')
    else:
        action = flask.request.args.get('action')

    # If not logged in, allow GET from email with no session
    logemail = flask.session.get('email')
    transaction = connection.execute(
        "SELECT seller_email, buyer_email FROM transactions WHERE transaction_id = ?",
        (transaction_id,)
    ).fetchone()
    if not transaction:
        return "<html><body><h2>Transaction not found.</h2></body></html>"
    # Only require login for POST; for GET allow if buyer or seller email matches
    user_type = None
    if logemail:
        if logemail == transaction['seller_email']:
            user_type = 'seller'
        elif logemail == transaction['buyer_email']:
            user_type = 'buyer'
        else:
            flask.abort(403)
    else:
        # For GET, infer user_type from action
        if action == 'sent':
            user_type = 'seller'
        elif action in ['confirm', 'received']:
            user_type = 'buyer'
    # Seller confirms ticket sent
    if action == 'sent' and user_type == 'seller':
        connection.execute(
            "UPDATE transactions SET status = 'ticket_sent' WHERE transaction_id = ?",
            (transaction_id,)
        )
        return "<html><body><h2>Thank you! The buyer has been notified that the ticket was sent. You may now close this tab and return to your email.</h2></body></html>"
    # Buyer or anyone with the link confirms ticket received
    elif action in ['confirm', 'received']:
        # Only check transaction_id, update status
        connection.execute(
            "UPDATE transactions SET status = 'ticket_sent' WHERE transaction_id = ?",
            (transaction_id,)
        )
        # Fetch transaction details for email
        info = connection.execute(
            "SELECT buyer_email, event_id, price, seller_email FROM transactions WHERE transaction_id = ?",
            (transaction_id,)
        ).fetchone()
        event_name = None
        event_datetime = None
        if info and info['event_id']:
            event_row = connection.execute(
                "SELECT name, event_datetime FROM events WHERE event_id = ?",
                (info['event_id'],)
            ).fetchone()
            if event_row:
                event_name = event_row['name']
                event_datetime = event_row['event_datetime']
        # Calculate 48-hour complaint deadline from now
        import datetime
        now = datetime.datetime.now()
        complaint_deadline = (now + datetime.timedelta(hours=48)).strftime('%Y-%m-%d %I:%M %p')
        if info and info['buyer_email'] and event_name and event_datetime:
            try:
                from insta485.email_utils import send_ticket_received_email
                send_ticket_received_email(
                    info['buyer_email'],
                    event_name,
                    price=info['price'],
                    seller_email=info['seller_email'],
                    event_datetime=event_datetime,
                    complaint_deadline=complaint_deadline
                )
            except Exception as e:
                print(f"[EMAIL ERROR] Failed to send ticket received email: {e}")
        return "<html><body><h2>You have confirmed the ticket is sent. Please return to your email.</h2></body></html>"
    # Default: show not found if no valid action
    return "<html><body><h2>Invalid or missing action for this transaction.</h2></body></html>"

@insta485.app.route('/cancel/<int:transaction_id>', methods=['GET', 'POST'])
def simple_cancel(transaction_id):
    """Buyer requests to cancel: set buyer_cancel_requested=1 and show confirmation."""
    connection = insta485.model.get_db()
    connection.execute(
        "UPDATE transactions SET buyer_cancel_requested = 1 WHERE transaction_id = ?",
        (transaction_id,)
    )
    connection.commit()
    return "<html><body><h2>You have requested to cancel.</h2></body></html>"

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
