"""
Insta485 index (main) view.

URLs include:
/
"""
import flask
from flask import url_for, session, flash
from flask_mail import Message
import insta485
import pathlib
import uuid
import datetime
from insta485.email_utils import send_accept_confirmation_email, send_reject_confirmation_email
from insta485.payment_utils import send_payment_seller

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

    # Get filter parameter (active, history, all)
    view_filter = flask.request.args.get('filter', 'active')

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

        # Add status category for filtering
        if trans_dict['status'] in ['pending', 'waiting_for_payment_processing', 'waiting_for_ticket_transfer', 'ticket_sent', 'event_occurred', 'complaint_filed']:
            trans_dict['status_category'] = 'active'
        else:
            trans_dict['status_category'] = 'completed'

        formatted_transactions.append(trans_dict)

    # Filter transactions based on view_filter
    if view_filter == 'active':
        filtered_transactions = [t for t in formatted_transactions if t['status_category'] == 'active']
    elif view_filter == 'history':
        filtered_transactions = [t for t in formatted_transactions if t['status_category'] == 'completed']
    else:  # 'all'
        filtered_transactions = formatted_transactions

    # Count transactions for tabs
    active_count = len([t for t in formatted_transactions if t['status_category'] == 'active'])
    history_count = len([t for t in formatted_transactions if t['status_category'] == 'completed'])

    # Get user balance for sellers
    user_balance = 0
    if user_type == 'seller':
        from insta485.views.balance import get_user_balance
        user_balance = get_user_balance(logemail)

    context = {
        'user_type': user_type,
        'logemail': logemail,
        'transactions': filtered_transactions,
        'is_admin': is_admin,
        'view_filter': view_filter,
        'active_count': active_count,
        'history_count': history_count,
        'total_count': len(formatted_transactions),
        'user_balance': user_balance
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


@insta485.app.route('/dev/skip-login/<user_type>')
def skip_login(user_type):
    """TEMPORARY: Skip login for development/testing purposes."""
    # This is a temporary route for testing - remove in production!
    connection = insta485.model.get_db()
    
    if user_type == 'admin':
        # Log in as admin
        flask.session['email'] = 'admin@gmail.com'
        return flask.redirect(url_for('admin_dashboard'))
    elif user_type == 'buyer':
        # Log in as regular user
        flask.session['email'] = 'user1@gmail.com'
        return flask.redirect(url_for('show_index', user_type='buyer'))
    elif user_type == 'seller':
        # Log in as another user for seller functionality
        flask.session['email'] = 'user2@gmail.com'
        return flask.redirect(url_for('show_index', user_type='seller'))
    else:
        flask.flash('Invalid user type for skip login')
        return flask.redirect(url_for('show_accounts', url='login'))


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
        try:
            # Try parsing as standard SQLite datetime first
            event_dt = datetime.datetime.strptime(row['event_datetime'], '%Y-%m-%d %H:%M:%S')
        except ValueError:
            try:
                # Try parsing HTML5 datetime-local format
                event_dt = datetime.datetime.strptime(row['event_datetime'], '%Y-%m-%dT%H:%M')
            except ValueError:
                # If all else fails, use a default format
                event_dt = datetime.datetime.now()
        
        results.append({
            'name': row['name'],
            'location': row['location'],
            'datetime': event_dt.strftime('%A, %b %d, %Y at %I:%M %p'),
            'raw_datetime': row['event_datetime']
        })
    return flask.jsonify(results)


@insta485.app.route('/create-listing', methods=['GET'])
def create_listing():
    """Display create listing page for sellers."""
    if check_login():
        return check_login()
    
    return flask.render_template("create_listing.html", 
                               logemail=flask.session['email'])


@insta485.app.route('/create-transaction', methods=['POST'])
def create_transaction():
    """Create a new transaction and send email to buyer."""
    if check_login():
        return check_login()
    
    seller_email = flask.session['email']
    buyer_email = flask.request.form['buyer_email']
    price = int(flask.request.form['price'])
    event_name = flask.request.form['event_name']
    event_location = flask.request.form['event_location']
    event_datetime_raw = flask.request.form['event_datetime']
    ticket_details = flask.request.form.get('ticket_details', '')
    
    # Fix datetime format - convert from HTML5 datetime-local to SQLite format
    if 'T' in event_datetime_raw and len(event_datetime_raw) == 16:
        # Format: "2026-07-05T12:32" -> "2026-07-05 12:32:00"
        event_datetime = event_datetime_raw.replace('T', ' ') + ':00'
    else:
        event_datetime = event_datetime_raw
    
    # Validate that seller isn't creating transaction with themselves
    if seller_email == buyer_email:
        flask.flash('You cannot create a transaction with yourself.', 'error')
        return flask.redirect(url_for('create_listing'))
    
    connection = insta485.model.get_db()
    
    # Check if buyer exists in users table, if not create a placeholder
    buyer_exists = connection.execute(
        "SELECT email FROM users WHERE email = ?",
        (buyer_email,)
    ).fetchone()
    
    if not buyer_exists:
        # Create placeholder user for buyer
        import hashlib
        # Generate a random password hash (they'll need to reset it later)
        password_hash = 'sha512$placeholder$placeholder_hash_needs_reset'
        connection.execute(
            "INSERT INTO users (email, firstname, lastname, password) VALUES (?, ?, ?, ?)",
            (buyer_email, 'New', 'User', password_hash)
        )
    
    # Check if event exists, if not create it
    event = connection.execute(
        "SELECT event_id FROM events WHERE name = ? AND location = ? AND event_datetime = ?",
        (event_name, event_location, event_datetime)
    ).fetchone()
    
    if event:
        event_id = event['event_id']
    else:
        # Create new event
        cursor = connection.execute(
            "INSERT INTO events (name, location, event_datetime) VALUES (?, ?, ?)",
            (event_name, event_location, event_datetime)
        )
        event_id = cursor.lastrowid
    
    # Create transaction
    try:
        cursor = connection.execute(
            """INSERT INTO transactions 
               (buyer_email, seller_email, price, event_id, status) 
               VALUES (?, ?, ?, ?, 'pending')""",
            (buyer_email, seller_email, price, event_id)
        )
        transaction_id = cursor.lastrowid
        
        # Send email to buyer
        send_buyer_email_1(transaction_id, buyer_email, event_name, price, seller_email)
        
        flask.flash(f'Listing created successfully! Email sent to {buyer_email}', 'success')
        return flask.redirect(url_for('show_index', user_type='seller'))
        
    except Exception as e:
        print(f"Error creating transaction: {e}")
        flask.flash(f'Error creating listing: {str(e)}', 'error')
        return flask.redirect(url_for('create_listing'))


def send_buyer_email_1(transaction_id, buyer_email, event_name, price, seller_email):
    """Send Email 1 to buyer with secure payment link."""
    subject = f"🎫 Secure Ticket Offer - {event_name}"
    
    # Create HTML email content
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #007bff, #0056b3); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: white; padding: 30px; border: 1px solid #ddd; }}
            .event-details {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; }}
            .price {{ font-size: 24px; font-weight: bold; color: #007bff; text-align: center; margin: 20px 0; }}
            .cta-button {{ display: inline-block; background: #28a745; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: bold; margin: 20px 0; }}
            .security {{ background: #d4edda; padding: 15px; border-radius: 8px; border-left: 4px solid #28a745; margin: 20px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🛡️ Safe Transaction</h1>
                <p>Your Secure Ticket Purchase</p>
            </div>
            <div class="content">
                <h2>Hi there! 👋</h2>
                <p>Thanks for using <strong>Safe Transaction</strong>, our scam-free ticket platform!</p>
                <p>You have a secure ticket offer from <strong>{seller_email}</strong>:</p>
                
                <div class="event-details">
                    <h3>🎫 {event_name}</h3>
                    <div class="price">💰 ${price}</div>
                </div>
                
                <div style="text-align: center;">
                    <a href="http://localhost:8000/ticket/{transaction_id}" class="cta-button">
                        🔒 View Offer & Pay Securely
                    </a>
                </div>
                
                <div class="security">
                    <strong>🛡️ 100% Secure:</strong> Your payment is protected until you receive the ticket. No scams, guaranteed!
                </div>
                
                <p>Click the link above to view full details and pay securely.</p>
                <p>Best regards,<br>The Safe Transaction Team</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Create plain text version
    text_body = f"""
    Hi there!

    Thanks for using Safe Transaction, our scam-free ticket platform!
    You have a ticket offer from {seller_email}:

    🎫 Event: {event_name}
    💰 Price: ${price}
    🔗 Secure Payment Link: http://localhost:8000/ticket/{transaction_id}

    Click the link above to view details and pay securely.
    Your payment is protected until you receive the ticket!

    Safe Transaction Team
    """
    
    try:
        # Create and send email
        msg = Message(
            subject=subject,
            recipients=[buyer_email],
            html=html_body,
            body=text_body
        )
        insta485.mail.send(msg)
        
        # Also log to console for debugging
        print(f"\n✅ EMAIL 1 SENT SUCCESSFULLY!")
        print(f"📧 TO: {buyer_email}")
        print(f"📋 SUBJECT: {subject}")
        print(f"🔗 Payment Link: http://localhost:8000/ticket/{transaction_id}")
        print(f"{'='*50}\n")
        
    except Exception as e:
        print(f"\n❌ EMAIL SEND FAILED!")
        print(f"Error: {e}")
        print(f"TO: {buyer_email}")
        print(f"SUBJECT: {subject}")
        print(f"{'='*50}\n")
        # Still continue with the transaction creation


@insta485.app.route('/ticket/<int:transaction_id>')
def buyer_ticket_card(transaction_id):
    """Display ticket card for buyer from email link."""
    connection = insta485.model.get_db()
    
    # Get transaction and event details
    transaction = connection.execute(
        """SELECT t.*, e.name, e.location, e.event_datetime 
           FROM transactions t 
           JOIN events e ON t.event_id = e.event_id 
           WHERE t.transaction_id = ?""",
        (transaction_id,)
    ).fetchone()
    
    if not transaction:
        flask.abort(404)
    
    # Format event datetime
    event_dt = datetime.datetime.strptime(transaction['event_datetime'], '%Y-%m-%d %H:%M:%S')
    formatted_datetime = event_dt.strftime('%A, %B %d, %Y at %I:%M %p')
    
    context = {
        'transaction': transaction,
        'event_name': transaction['name'],
        'event_location': transaction['location'],
        'event_datetime': formatted_datetime,
        'is_buyer_logged_in': ('email' in flask.session and 
                               flask.session['email'] == transaction['buyer_email'])
    }
    
    return flask.render_template("buyer_ticket_card.html", **context)


@insta485.app.route('/simulate-payment/<int:transaction_id>', methods=['POST'])
def simulate_payment(transaction_id):
    """Simulate payment processing for the transaction."""
    connection = insta485.model.get_db()
    
    # Get transaction details
    transaction = connection.execute(
        "SELECT buyer_email, seller_email, price FROM transactions WHERE transaction_id = ?",
        (transaction_id,)
    ).fetchone()
    
    # Update transaction status to payment processing
    connection.execute(
        "UPDATE transactions SET status = 'waiting_for_payment_processing', payment_processed_time = CURRENT_TIMESTAMP WHERE transaction_id = ?",
        (transaction_id,)
    )
    
    # Add record to monetary_transactions table
    connection.execute(
        "INSERT INTO monetary_transactions (sender, recipient, transaction_id_ref, amount, transaction_type) VALUES (?, ?, ?, ?, ?)",
        (transaction['buyer_email'], 'sanjivp2703@gmail.com', transaction_id, transaction['price'], "purchase")
    )
    
    # Simulate processing time (in real app, this would be async)
    import time
    time.sleep(1)
    
    # Update to waiting for ticket transfer
    connection.execute(
        "UPDATE transactions SET status = 'waiting_for_ticket_transfer' WHERE transaction_id = ?",
        (transaction_id,)
    )
    
    # Simulate sending notification to seller
    send_seller_notification(transaction_id, transaction['seller_email'])
    
    flask.flash('Payment successful! The seller has been notified.', 'success')
    return flask.redirect(url_for('buyer_ticket_card', transaction_id=transaction_id))


@insta485.app.route('/validate-ticket/<int:transaction_id>', methods=['GET', 'POST'])
def validate_ticket(transaction_id):
    """Mark ticket as validated by buyer."""
    connection = insta485.model.get_db()
    
    # Check if transaction exists and is in correct status
    transaction = connection.execute(
        "SELECT status, buyer_email, seller_email FROM transactions WHERE transaction_id = ?",
        (transaction_id,)
    ).fetchone()
    
    if not transaction:
        return "<html><body><h2>❌ Transaction not found.</h2></body></html>"
    
    if transaction['status'] != 'ticket_sent':
        return f"<html><body><h2>❌ Invalid action. Transaction status is: {transaction['status']}</h2></body></html>"
    
    # Update transaction status to success
    connection.execute(
        "UPDATE transactions SET status = 'success' WHERE transaction_id = ?",
        (transaction_id,)
    )
    connection.commit()
    
    # Cancel any scheduled auto-validation
    try:
        insta485.app.scheduler.remove_job(f'auto_validate_{transaction_id}')
        print(f"[SCHEDULER] Cancelled auto-validation for transaction {transaction_id}")
    except Exception as e:
        print(f"[SCHEDULER] No auto-validation job to cancel for transaction {transaction_id}: {e}")
    
    # Get full transaction details for success email
    trans_details = connection.execute(
        "SELECT t.buyer_email, t.seller_email, t.price, e.name, e.event_datetime "
        "FROM transactions t JOIN events e ON t.event_id = e.event_id "
        "WHERE t.transaction_id = ?",
        (transaction_id,)
    ).fetchone()
    
    if trans_details:
        # Add earnings to seller balance
        from insta485.views.balance import add_earnings
        add_earnings(trans_details['seller_email'], trans_details['price'], transaction_id, 
                   f"Payment for {trans_details['name']}")
        
        send_buyer_email_3(transaction_id, trans_details['buyer_email'])
        print(f"[EMAIL] Sent success email to {trans_details['buyer_email']}")
    
    # Get event details for confirmation page
    event_details = connection.execute(
        "SELECT e.name, e.location, e.event_datetime "
        "FROM events e JOIN transactions t ON e.event_id = t.event_id "
        "WHERE t.transaction_id = ?",
        (transaction_id,)
    ).fetchone()
    
    # Generate a ticket code
    ticket_code = f"SAFE-{transaction_id}-{hash(transaction['seller_email']) % 10000:04d}"
    
    # Format date for display
    from datetime import datetime
    event_datetime = event_details['event_datetime']
    try:
        dt = datetime.strptime(event_datetime, '%Y-%m-%d %H:%M:%S')
        event_datetime = dt.strftime('%A, %b %d, %Y at %I:%M %p')
    except ValueError:
        # Already in pretty format
        pass
    
    # Prepare context for success page
    context = {
        "transaction_id": transaction_id,
        "event_name": event_details['name'],
        "event_location": event_details['location'],
        "event_datetime": event_datetime,
        "price": trans_details['price'],
        "seller_email": transaction['seller_email'],
        "ticket_code": ticket_code
    }
    
    # Render the success template
    return flask.render_template('validate_ticket_success.html', **context)


def send_seller_notification(transaction_id, seller_email):
    """Send notification to seller about payment received."""
    subject = f"💰 Payment Received - Transfer Ticket Now (Transaction #{transaction_id})"
    
    # Create HTML email content
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #28a745, #1e7e34); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: white; padding: 30px; border: 1px solid #ddd; }}
            .highlight {{ background: #d4edda; padding: 20px; border-radius: 8px; border-left: 4px solid #28a745; margin: 20px 0; }}
            .cta-button {{ display: inline-block; background: #007bff; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: bold; margin: 20px 0; }}
            .steps {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎉 Great News!</h1>
                <p>Payment Received - Transfer Ticket Now</p>
            </div>
            <div class="content">
                <div class="highlight">
                    <h2>💰 Your buyer has paid for Transaction #{transaction_id}!</h2>
                </div>
                
                <h3>📋 Next Steps:</h3>
                <div class="steps">
                    <ol>
                        <li><strong>Transfer the ticket</strong> to the buyer via your ticket platform (Ticketmaster, StubHub, etc.)</li>
                        <li><strong>Log into Safe Transaction</strong> and mark the ticket as "sent"</li>
                        <li><strong>Get paid</strong> once the buyer confirms receipt (or automatically after 48 hours)</li>
                    </ol>
                </div>
                
                <div style="text-align: center;">
                    <a href="http://localhost:8000/seller" class="cta-button">
                        📱 Go to Seller Dashboard
                    </a>
                </div>
                
                <p><strong>Important:</strong> Please transfer the ticket promptly to maintain a good seller rating.</p>
                <p>Best regards,<br>The Safe Transaction Team</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Create plain text version
    text_body = f"""
    Great news! Your buyer has paid for Transaction #{transaction_id}.

    Next Steps:
    1. Transfer the ticket to the buyer via your ticket platform
    2. Log into Safe Transaction and mark the ticket as 'sent'
    3. Get paid once the buyer confirms receipt

    Dashboard: http://localhost:8000/seller

    Safe Transaction Team
    """
    
    try:
        # Create and send email
        msg = Message(
            subject=subject,
            recipients=[seller_email],
            html=html_body,
            body=text_body
        )
        insta485.mail.send(msg)
        
        # Also log to console for debugging
        print(f"\n✅ SELLER NOTIFICATION SENT!")
        print(f"📧 TO: {seller_email}")
        print(f"📋 Transaction: #{transaction_id}")
        print(f"{'='*40}\n")
        
    except Exception as e:
        print(f"\n❌ SELLER EMAIL SEND FAILED!")
        print(f"Error: {e}")
        print(f"TO: {seller_email}")
        print(f"{'='*40}\n")


def send_buyer_email_3(transaction_id, buyer_email):
    """Send Email 3 (success) to buyer."""
    subject = f"🎉 Transaction Complete - No Scams Here! (#{transaction_id})"
    
    # Create HTML email content
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #28a745, #20c997); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: white; padding: 30px; border: 1px solid #ddd; }}
            .success {{ background: #d4edda; padding: 20px; border-radius: 8px; border-left: 4px solid #28a745; margin: 20px 0; text-align: center; }}
            .highlight {{ background: #fff3cd; padding: 15px; border-radius: 8px; margin: 20px 0; }}
            .cta-button {{ display: inline-block; background: #ffc107; color: #212529; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: bold; margin: 20px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎉 Congratulations!</h1>
                <p>Transaction Complete - No Scams Here!</p>
            </div>
            <div class="content">
                <div class="success">
                    <h2>✅ Your ticket purchase was completed successfully!</h2>
                    <p><strong>You didn't get scammed and used our secure service!</strong></p>
                </div>
                
                <p>Transaction <strong>#{transaction_id}</strong> is now complete.</p>
                
                <div class="highlight">
                    <p><strong>🛡️ Safe Transaction protected your purchase:</strong></p>
                    <ul>
                        <li>✅ Verified seller</li>
                        <li>✅ Secure payment processing</li>
                        <li>✅ Ticket delivery confirmed</li>
                        <li>✅ Zero scam risk</li>
                    </ul>
                </div>
                
                <p><strong>Enjoy your event!</strong> Thanks for using Safe Transaction to avoid scams.</p>
                
                <div style="text-align: center;">
                    <a href="http://localhost:8000/buyer" class="cta-button">
                        ⭐ Rate Your Experience
                    </a>
                </div>
                
                <p>Help us prevent scams by sharing Safe Transaction with friends!</p>
                <p>Best regards,<br>The Safe Transaction Team</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Create plain text version
    text_body = f"""
    🎉 Congratulations! Your ticket purchase was completed successfully!

    You didn't get scammed and used our secure service!

    Transaction #{transaction_id} is now complete.
    Enjoy your event and thanks for using Safe Transaction!

    ⭐ Rate your experience: http://localhost:8000/buyer

    Help us prevent scams by sharing Safe Transaction with friends!

    Safe Transaction Team
    """
    
    try:
        # Create and send email
        msg = Message(
            subject=subject,
            recipients=[buyer_email],
            html=html_body,
            body=text_body
        )
        insta485.mail.send(msg)
        
        # Also log to console for debugging
        print(f"\n✅ SUCCESS EMAIL SENT!")
        print(f"📧 TO: {buyer_email}")
        print(f"🎉 Transaction #{transaction_id} completed!")
        print(f"{'='*40}\n")
        
    except Exception as e:
        print(f"\n❌ SUCCESS EMAIL SEND FAILED!")
        print(f"Error: {e}")
        print(f"TO: {buyer_email}")
        print(f"{'='*40}\n")


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
        "SELECT seller_email, buyer_email, status FROM transactions WHERE transaction_id = ?",
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
        # Only allow if status is waiting_for_ticket_transfer
        if transaction['status'] != 'waiting_for_ticket_transfer':
            return "<html><body><h2>Invalid action for current transaction status.</h2></body></html>"
        
        # Update status to ticket_sent
        connection.execute(
            "UPDATE transactions SET status = 'ticket_sent' WHERE transaction_id = ?",
            (transaction_id,)
        )
        connection.commit()
        
        # Send Email 2 to buyer
        try:
            # Get transaction details for email
            trans_details = connection.execute(
                "SELECT t.buyer_email, t.price, t.seller_email, e.name, e.event_datetime "
                "FROM transactions t JOIN events e ON t.event_id = e.event_id "
                "WHERE t.transaction_id = ?",
                (transaction_id,)
            ).fetchone()
            
            if trans_details:
                import datetime
                # 2-minute timer for testing
                validation_deadline = (datetime.datetime.now() + datetime.timedelta(minutes=2)).strftime('%Y-%m-%d %I:%M %p')
                
                from insta485.email_utils import send_ticket_sent_email
                send_ticket_sent_email(
                    trans_details['buyer_email'],
                    trans_details['name'],
                    trans_details['price'],
                    trans_details['seller_email'],
                    trans_details['event_datetime'],
                    transaction_id,
                    validation_deadline
                )
                print(f"[EMAIL] Sent ticket notification to {trans_details['buyer_email']}")
            
        except Exception as e:
            print(f"[EMAIL ERROR] Failed to send ticket sent email: {e}")
        
        # Schedule auto-validation after 2 minutes
        schedule_auto_validation(transaction_id)
        
        if logemail:
            flask.flash("✅ Ticket marked as sent! The buyer has been notified.", "success")
            return flask.redirect(flask.url_for('show_index', user_type='seller'))
        else:
            return "<html><body><h2>✅ Thank you! The buyer has been notified that the ticket was sent. You may now close this tab.</h2></body></html>"
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

@insta485.app.route('/report_problem/<int:transaction_id>', methods=['GET', 'POST'])
def report_problem(transaction_id):
    """Handle problem reports from the buyer."""
    connection = insta485.model.get_db()

    # Get transaction details
    transaction = connection.execute(
        "SELECT buyer_email, seller_email, status FROM transactions WHERE transaction_id = ?",
        (transaction_id,)
    ).fetchone()

    if not transaction:
        return "<html><body><h2>❌ Transaction not found.</h2></body></html>"
    
    # Allow access if user is logged in as buyer OR if accessing via email link (no login required)
    logemail = flask.session.get('email')
    print(f"[DEBUG] Complaint access - Logged in as: {logemail}, Transaction buyer: {transaction['buyer_email']}")
    
    # Only restrict access if user is logged in as a DIFFERENT user than the buyer
    # If not logged in at all, allow access (email link)
    if logemail and logemail != transaction['buyer_email']:
        print(f"[DEBUG] Access denied - wrong user logged in")
        return "<html><body><h2>❌ Access denied. You must be the buyer for this transaction to file a complaint.</h2></body></html>"
    
    if flask.request.method == 'GET':
        # Show complaint form page for email link access
        return flask.render_template('complaint_form.html', 
                                   transaction_id=transaction_id,
                                   buyer_email=transaction['buyer_email'])
    
    # POST - Handle complaint submission
    print(f"[DEBUG] Form data: {dict(flask.request.form)}")
    reason = flask.request.form.get('reason')
    print(f"[DEBUG] Reason: {reason}")
    
    if reason == 'Other':
        complaint_reason = flask.request.form.get('other_reason', 'Other issue reported by buyer.')
    else:
        complaint_reason = reason

    print(f"[DEBUG] Final complaint reason: {complaint_reason}")

    # Update transaction status to complaint_filed
    connection.execute(
        "UPDATE transactions SET status = 'complaint_filed', complaint_reason = ? WHERE transaction_id = ?",
        (complaint_reason, transaction_id)
    )
    connection.commit()
    
    # Send notification to seller requesting proof
    try:
        send_seller_proof_request(transaction_id, transaction['seller_email'], transaction['buyer_email'], complaint_reason)
        print(f"[EMAIL] Sent proof request to seller: {transaction['seller_email']}")
        
        # Schedule reminder email after 12 hours
        schedule_seller_reminder(transaction_id, transaction['seller_email'], transaction['buyer_email'], complaint_reason)
        
        # Schedule auto-refund after 24 hours if no response
        schedule_auto_refund(transaction_id)
        
    except Exception as e:
        print(f"[EMAIL ERROR] Failed to send proof request: {e}")
    
    if logemail:
        flash("✅ Your complaint has been filed. The seller has been notified to provide proof.", "success")
        return flask.redirect(flask.url_for('show_index', user_type='buyer'))
    else:
        return "<html><body><h2>✅ Your complaint has been filed. The seller has been notified to provide proof. You may close this tab.</h2></body></html>"

def send_seller_proof_request(transaction_id, seller_email, buyer_email, complaint_reason):
    """Send email to seller requesting proof of ticket transfer when buyer complains."""
    subject = f"🚨 URGENT: Proof Required - Buyer Complaint Filed (Transaction #{transaction_id})"
    
    # Create HTML email content
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 650px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #dc3545, #c82333); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: white; padding: 30px; border: 1px solid #ddd; border-radius: 0 0 10px 10px; }}
            .alert {{ background: #f8d7da; border-left: 4px solid #dc3545; padding: 20px; margin: 20px 0; border-radius: 8px; }}
            .warning {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 20px; margin: 20px 0; border-radius: 8px; }}
            .cta-button {{ display: inline-block; background: #dc3545; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: bold; margin: 20px 0; }}
            .deadline {{ background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 20px 0; text-align: center; }}
            .steps {{ background: #e9ecef; padding: 20px; border-radius: 8px; margin: 20px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚨 URGENT ACTION REQUIRED</h1>
                <p>Buyer Complaint Filed - Proof Needed</p>
            </div>
            <div class="content">
                <div class="alert">
                    <h2>⚠️ A buyer has filed a complaint about Transaction #{transaction_id}</h2>
                    <p><strong>Buyer:</strong> {buyer_email}</p>
                    <p><strong>Complaint:</strong> {complaint_reason}</p>
                </div>
                
                <div class="warning">
                    <h3>🕐 You have 24 HOURS to provide proof</h3>
                    <p>If you don't respond with proof within 24 hours, the buyer will automatically receive a full refund and you will not be paid.</p>
                </div>
                
                <h3>📋 Required Actions:</h3>
                <div class="steps">
                    <ol>
                        <li><strong>Forward your ticket transfer confirmation email</strong> to <a href="mailto:safetransaction@gmail.com">safetransaction@gmail.com</a></li>
                        <li><strong>Include screenshots</strong> of the ticket transfer from your platform (Ticketmaster, StubHub, etc.)</li>
                        <li><strong>Provide tracking/confirmation numbers</strong> if available</li>
                        <li><strong>Include Transaction #{transaction_id}</strong> in your email subject line</li>
                    </ol>
                </div>
                
                <h3>✅ What Counts as Valid Proof:</h3>
                <div class="steps">
                    <ul style="margin: 10px 0; padding-left: 20px;">
                        <li>Email confirmation from ticket platform showing successful transfer</li>
                        <li>Screenshots of "Transfer Complete" page from Ticketmaster/StubHub/etc.</li>
                        <li>Mobile app notifications showing ticket sent</li>
                        <li>SMS confirmations with transfer details</li>
                        <li>Platform transaction history showing completed transfer</li>
                    </ul>
                </div>
                
                <h3>❌ What Does NOT Count:</h3>
                <div class="steps">
                    <ul style="margin: 10px 0; padding-left: 20px; color: #dc3545;">
                        <li>Screenshots of tickets before transfer</li>
                        <li>Purchase confirmations (doesn't prove transfer)</li>
                        <li>Text messages to/from buyer (can be faked)</li>
                        <li>Social media screenshots</li>
                    </ul>
                </div>
                
                <div class="deadline">
                    <h3 style="color: #dc3545; margin: 0;">⏰ DEADLINE: 24 Hours from Now</h3>
                    <p style="margin: 8px 0 0 0;">No response = Automatic buyer refund</p>
                </div>
                
                <div style="text-align: center;">
                    <a href="mailto:safetransaction@gmail.com?subject=Proof for Transaction #{transaction_id}&body=Hi,%0D%0A%0D%0AAttached is proof that I transferred the ticket for Transaction #{transaction_id}.%0D%0A%0D%0AComplaint: {complaint_reason}%0D%0A%0D%0AProof attached:%0D%0A- [Attach your ticket transfer confirmation]%0D%0A- [Attach screenshots]%0D%0A%0D%0AThank you" class="cta-button">
                        📧 Send Proof Email Now
                    </a>
                </div>
                
                <div style="background: #e3f2fd; padding: 15px; border-radius: 8px; margin-top: 20px;">
                    <p style="margin: 0; font-size: 14px; color: #0d47a1;">
                        <strong>💡 Pro Tip:</strong> Always save confirmation emails and screenshots when transferring tickets. This protects both you and the buyer.
                    </p>
                </div>
                
                <p><strong>Questions?</strong> Contact us at <a href="mailto:safetransaction@gmail.com">safetransaction@gmail.com</a></p>
                <p>Safe Transaction Team</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Plain text version
    plain_body = f"""
🚨 URGENT ACTION REQUIRED - Transaction #{transaction_id}

A buyer has filed a complaint:
- Buyer: {buyer_email}
- Complaint: {complaint_reason}

⏰ You have 24 HOURS to provide proof or you will not be paid.

REQUIRED ACTIONS:
1. Forward your ticket transfer confirmation email to safetransaction@gmail.com
2. Include screenshots of the ticket transfer 
3. Include Transaction #{transaction_id} in your subject line

DEADLINE: 24 Hours from Now
No response = Automatic buyer refund

Send proof to: safetransaction@gmail.com
Subject: Proof for Transaction #{transaction_id}

Safe Transaction Team
    """
    
    # Send email using Flask-Mail
    from flask_mail import Message
    from insta485 import mail
    
    try:
        msg = Message(subject, recipients=[seller_email], body=plain_body)
        msg.html = html_body
        mail.send(msg)
        print(f"✅ Seller proof request sent to {seller_email}")
        return True
    except Exception as e:
        print(f"❌ Failed to send seller proof request: {e}")
        return False

def schedule_auto_validation(transaction_id):
    """Schedule automatic validation after 2 minutes (for testing)."""
    import datetime
    
    def auto_validate_transaction():
        """Auto-validate transaction after timeout."""
        try:
            connection = insta485.model.get_db()
            
            # Check if transaction is still in ticket_sent status
            transaction = connection.execute(
                "SELECT status, buyer_email, seller_email FROM transactions WHERE transaction_id = ?",
                (transaction_id,)
            ).fetchone()
            
            if transaction and transaction['status'] == 'ticket_sent':
                # Auto-complete the transaction
                connection.execute(
                    "UPDATE transactions SET status = 'success' WHERE transaction_id = ?",
                    (transaction_id,)
                )
                connection.commit()
                print(f"[AUTO-VALIDATION] Transaction {transaction_id} auto-validated after 2 minutes")
                
                # Send success email to both parties
                try:
                    trans_details = connection.execute(
                        "SELECT t.buyer_email, t.seller_email, t.price, e.name, e.event_datetime "
                        "FROM transactions t JOIN events e ON t.event_id = e.event_id "
                        "WHERE t.transaction_id = ?",
                        (transaction_id,)
                    ).fetchone()
                    
                    if trans_details:
                        # Add earnings to seller balance
                        from insta485.views.balance import add_earnings
                        add_earnings(trans_details['seller_email'], trans_details['price'], transaction_id, 
                                   f"Payment for {trans_details['name']}")
                        
                        # Send Email 3 (success) to buyer
                        send_buyer_email_3(transaction_id, trans_details['buyer_email'])
                        print(f"[EMAIL] Sent success email to buyer: {trans_details['buyer_email']}")
                        
                except Exception as e:
                    print(f"[EMAIL ERROR] Failed to send success email: {e}")
            else:
                print(f"[AUTO-VALIDATION] Transaction {transaction_id} status is {transaction.get('status') if transaction else 'not found'}, skipping auto-validation")
                
        except Exception as e:
            print(f"[AUTO-VALIDATION ERROR] Failed to auto-validate transaction {transaction_id}: {e}")
    
    # Schedule the job 2 minutes from now
    run_time = datetime.datetime.now() + datetime.timedelta(minutes=2)
    insta485.app.scheduler.add_job(
        func=auto_validate_transaction,
        trigger='date',
        run_date=run_time,
        id=f'auto_validate_{transaction_id}',
        replace_existing=True
    )
    print(f"[SCHEDULER] Scheduled auto-validation for transaction {transaction_id} at {run_time}")

def schedule_seller_reminder(transaction_id, seller_email, buyer_email, complaint_reason):
    """Schedule a reminder email to seller after 12 hours if complaint still unresolved."""
    import datetime
    
    def send_reminder():
        """Send reminder email to seller."""
        try:
            connection = insta485.model.get_db()
            
            # Check if complaint is still active
            transaction = connection.execute(
                "SELECT status FROM transactions WHERE transaction_id = ?",
                (transaction_id,)
            ).fetchone()
            
            if transaction and transaction['status'] == 'complaint_filed':
                # Send reminder email
                subject = f"⚠️ FINAL REMINDER: 12 Hours Left - Proof Required (Transaction #{transaction_id})"
                
                html_body = f"""
                <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background: #fff3cd; border: 2px solid #ffc107; border-radius: 10px;">
                    <h2 style="color: #856404; text-align: center;">⚠️ FINAL REMINDER - 12 HOURS LEFT</h2>
                    
                    <div style="background: #dc3545; color: white; padding: 15px; border-radius: 8px; text-align: center; margin: 20px 0;">
                        <h3 style="margin: 0;">You have ONLY 12 HOURS LEFT to provide proof</h3>
                        <p style="margin: 10px 0 0 0;">Transaction #{transaction_id} will be automatically refunded to the buyer if you don't respond</p>
                    </div>
                    
                    <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <h4>Buyer's Complaint:</h4>
                        <p style="font-style: italic; color: #666;">"{complaint_reason}"</p>
                    </div>
                    
                    <div style="text-align: center; margin: 20px 0;">
                        <a href="mailto:safetransaction@gmail.com?subject=URGENT Proof for Transaction #{transaction_id}" 
                           style="background: #dc3545; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: bold; display: inline-block;">
                            📧 Send Proof NOW - 12 Hours Left
                        </a>
                    </div>
                    
                    <p style="text-align: center; color: #856404; font-weight: bold;">
                        No response = Automatic buyer refund + No payment to you
                    </p>
                </div>
                """
                
                from flask_mail import Message
                from insta485 import mail
                
                msg = Message(subject, recipients=[seller_email], html=html_body)
                mail.send(msg)
                print(f"[REMINDER] Sent 12-hour reminder to seller: {seller_email}")
            else:
                print(f"[REMINDER] Complaint {transaction_id} already resolved, no reminder needed")
                
        except Exception as e:
            print(f"[REMINDER ERROR] Failed to send reminder for transaction {transaction_id}: {e}")
    
    # Schedule for 12 hours from now (720 minutes)
    run_time = datetime.datetime.now() + datetime.timedelta(hours=12)
    insta485.app.scheduler.add_job(
        func=send_reminder,
        trigger='date',
        run_date=run_time,
        id=f'reminder_{transaction_id}',
        replace_existing=True
    )
    print(f"[SCHEDULER] Scheduled seller reminder for transaction {transaction_id} at {run_time}")

def schedule_auto_refund(transaction_id):
    """Schedule automatic buyer refund after 24 hours if seller doesn't provide proof."""
    import datetime
    
    def auto_refund():
        """Automatically refund buyer if seller hasn't provided proof."""
        try:
            connection = insta485.model.get_db()
            
            # Check if complaint is still unresolved
            transaction = connection.execute(
                "SELECT status, buyer_email, seller_email FROM transactions WHERE transaction_id = ?",
                (transaction_id,)
            ).fetchone()
            
            if transaction and transaction['status'] == 'complaint_filed':
                # Auto-refund buyer
                connection.execute(
                    "UPDATE transactions SET status = 'complaint - refunded buyer' WHERE transaction_id = ?",
                    (transaction_id,)
                )
                connection.commit()
                print(f"[AUTO-REFUND] Transaction {transaction_id} auto-refunded - seller didn't respond in 24 hours")
                
                # Send notification emails
                try:
                    from insta485.views.admin import send_complaint_resolution_email
                    send_complaint_resolution_email(transaction_id, 'refund_buyer', 'Seller failed to provide proof within 24 hours. Automatic refund issued.')
                    print(f"[EMAIL] Sent auto-refund notification emails for transaction {transaction_id}")
                except Exception as e:
                    print(f"[EMAIL ERROR] Failed to send auto-refund emails: {e}")
                    
            else:
                print(f"[AUTO-REFUND] Complaint {transaction_id} already resolved, no auto-refund needed")
                
        except Exception as e:
            print(f"[AUTO-REFUND ERROR] Failed to auto-refund transaction {transaction_id}: {e}")
    
    # Schedule for 24 hours from now
    run_time = datetime.datetime.now() + datetime.timedelta(hours=24)
    insta485.app.scheduler.add_job(
        func=auto_refund,
        trigger='date',
        run_date=run_time,
        id=f'auto_refund_{transaction_id}',
        replace_existing=True
    )
    print(f"[SCHEDULER] Scheduled auto-refund for transaction {transaction_id} at {run_time}")
