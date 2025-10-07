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
from werkzeug.exceptions import HTTPException

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
            return flask.redirect(url_for('show_index'))
    else:
        return flask.redirect(url_for('show_accounts', url='login'))

@insta485.app.route('/seller')
@insta485.app.route('/index')
def show_index():
    if check_login():
        return check_login()

    logemail = flask.session['email']
    connection = insta485.model.get_db()

    # Get filter parameter (active, history, all)
    view_filter = flask.request.args.get('filter', 'active')

    # Check admin status
    user = connection.execute(
        'SELECT is_admin FROM users WHERE email = ?',
        (logemail,)
    ).fetchone()
    is_admin = user and user['is_admin']

    # Get seller transactions (including pending ones)
    transactions = connection.execute(
        """SELECT t.transaction_id, e.name AS ticket_description, t.buyer_email, t.price, 
                  e.location, e.event_datetime, e.is_tbd, t.status, t.ticket_deadline,
                  t.awaiting_ticket_email, t.listing_created_time, t.payment_deadline
           FROM transactions t 
           JOIN events e ON t.event_id = e.event_id 
           WHERE t.seller_email = ?
           ORDER BY 
               CASE t.status 
                   WHEN 'pending_ticket_submission' THEN 1
                   WHEN 'waiting_for_payment' THEN 2
                   ELSE 3
               END,
               COALESCE(t.listing_created_time, t.created_time) DESC""",
        (logemail,)
    ).fetchall()
    

    


    formatted_transactions = []
    now = datetime.datetime.now()


    for trans in transactions:
        trans_dict = dict(trans)
        
        # --- AUTO-UPDATE STATUS TO 'payment_deadline_expired' IF PAYMENT DEADLINE PASSED ---
        if trans['payment_deadline'] and trans['status'] == 'waiting_for_payment':
            try:
                payment_deadline = datetime.datetime.strptime(trans['payment_deadline'], '%Y-%m-%d %H:%M:%S')
                if now > payment_deadline:
                    connection.execute(
                        "UPDATE transactions SET status = 'payment_deadline_expired' WHERE transaction_id = ?",
                        (trans['transaction_id'],)
                    )
                    trans_dict['status'] = 'payment_deadline_expired'
            except ValueError:
                pass  # Invalid datetime format, continue normally
        
        # --- AUTO-UPDATE STATUS TO 'completed' IF EVENT TIME PASSED ---
        if trans['event_datetime'] and trans['event_datetime'].strip():
            event_dt = datetime.datetime.strptime(trans['event_datetime'], '%Y-%m-%d %H:%M:%S')
            # 1. Promote to completed if event time passed and tickets were sent
            if trans['status'] in ('waiting_for_ticket', 'ticket_forwarded_funds_held') and now >= event_dt:
                connection.execute(
                    "UPDATE transactions SET status = 'completed' WHERE transaction_id = ?",
                    (trans['transaction_id'],)
                )
                trans_dict['status'] = 'completed'
                send_payment_seller(trans['transaction_id'])
        # Convert ticket_deadline to datetime if present
        if trans_dict.get('ticket_deadline'):
            trans_dict['ticket_deadline'] = datetime.datetime.strptime(
                trans_dict['ticket_deadline'], '%Y-%m-%d %H:%M:%S'
            )
        
        # Convert payment_deadline to datetime if present
        if trans_dict.get('payment_deadline'):
            # Handle both ISO format (from API) and SQLite format
            payment_deadline_str = trans_dict['payment_deadline']
            try:
                # Try ISO format first (from API)
                if 'T' in payment_deadline_str:
                    trans_dict['payment_deadline'] = datetime.datetime.fromisoformat(
                        payment_deadline_str.replace('Z', '+00:00')
                    )
                else:
                    # SQLite format
                    trans_dict['payment_deadline'] = datetime.datetime.strptime(
                        payment_deadline_str, '%Y-%m-%d %H:%M:%S'
                    )
            except ValueError:
                # If parsing fails, set to None
                trans_dict['payment_deadline'] = None
        
        # Add ticket_email for template compatibility
        trans_dict['ticket_email'] = 'system@safe-transaction.com'

        # Pass the event datetime as a formatted string, handling TBD times
        try:
            event_dt = datetime.datetime.strptime(trans_dict['event_datetime'], '%Y-%m-%d %H:%M:%S')
        except (ValueError, TypeError):
            # Handle empty or invalid datetime - use a default
            event_dt = datetime.datetime(2024, 12, 1, 12, 0, 0)
        if trans_dict.get('is_tbd', 0):
            # For TBD times, show only the date
            trans_dict['event_datetime_str'] = event_dt.strftime('%Y-%m-%d') + ' TBD'
        else:
            # For specific times, show date and time
            trans_dict['event_datetime_str'] = event_dt.strftime('%Y-%m-%d %I:%M %p')
        trans_dict['event_started'] = now >= event_dt

        # Allow problem reporting for up to 1 minute after the event
        problem_report_deadline = event_dt + datetime.timedelta(minutes=1)
        trans_dict['can_report_problem'] = now <= problem_report_deadline
        trans_dict['problem_report_deadline_str'] = problem_report_deadline.strftime('%Y-%m-%d %I:%M %p')

        # Add status category for filtering
        if trans_dict['status'] in ['pending_ticket_submission', 'waiting_for_ticket', 'waiting_for_payment', 'both_received_processing', 'ticket_forwarded_funds_held', 'complaint_filed']:
            trans_dict['status_category'] = 'active'
        elif trans_dict['status'] in ['payment_deadline_expired', 'cancelled_by_seller']:
            trans_dict['status_category'] = 'cancelled'
        else:
            trans_dict['status_category'] = 'completed'

        formatted_transactions.append(trans_dict)

    # Commit all status updates
    connection.commit()

    # Filter transactions based on view_filter
    if view_filter == 'active':
        filtered_transactions = [t for t in formatted_transactions if t['status_category'] == 'active']
    elif view_filter == 'history':
        filtered_transactions = [t for t in formatted_transactions if t['status_category'] in ['completed', 'cancelled']]
    else:  # 'all'
        filtered_transactions = formatted_transactions
    


    # Count transactions for tabs
    active_count = len([t for t in formatted_transactions if t['status_category'] == 'active'])
    history_count = len([t for t in formatted_transactions if t['status_category'] == 'completed'])

    # Get user balance (all users are sellers now)
    from insta485.views.balance import get_user_balance
    user_balance = get_user_balance(logemail)

    # Calculate real platform statistics
    stats = calculate_platform_stats(connection)

    # Get finished (completed and cancelled) transactions for the separate finished listings section
    # Fetch completed and cancelled transactions with proper event data using a fresh query
    finished_transactions_raw = connection.execute("""
        SELECT t.*, e.name, e.location, e.event_datetime 
        FROM transactions t 
        JOIN events e ON t.event_id = e.event_id 
        WHERE t.seller_email = ? AND t.status IN ('completed', 'cancelled_by_seller', 'payment_deadline_expired')
        ORDER BY t.created_time DESC
    """, (logemail,)).fetchall()
    
    finished_transactions = []
    for trans in finished_transactions_raw:
        trans_dict = dict(trans)
        
        # Format event datetime for display
        if trans_dict.get('event_datetime'):
            try:
                event_dt = datetime.datetime.strptime(trans_dict['event_datetime'], '%Y-%m-%d %H:%M:%S')
                trans_dict['event_datetime_formatted'] = event_dt.strftime('%A, %B %d, %Y at %I:%M %p')
            except ValueError:
                trans_dict['event_datetime_formatted'] = 'Date TBD'
        else:
            trans_dict['event_datetime_formatted'] = 'Date TBD'
        
        # Format completion time (use created_time as basis)
        if trans_dict.get('created_time'):
            try:
                created_dt = datetime.datetime.strptime(trans_dict['created_time'], '%Y-%m-%d %H:%M:%S')
                time_diff = now - created_dt
                if time_diff.days < 0:
                    trans_dict['completed_time_formatted'] = 'Recently'
                elif time_diff.days == 0:
                    trans_dict['completed_time_formatted'] = 'Today'
                elif time_diff.days == 1:
                    trans_dict['completed_time_formatted'] = 'Yesterday'
                elif time_diff.days < 7:
                    trans_dict['completed_time_formatted'] = f'{time_diff.days} days ago'
                else:
                    trans_dict['completed_time_formatted'] = created_dt.strftime('%b %d, %Y')
            except ValueError:
                trans_dict['completed_time_formatted'] = 'Recently'
        else:
            trans_dict['completed_time_formatted'] = 'Recently'
        
        # Set event location
        trans_dict['event_location'] = trans_dict.get('location', 'Location TBD')
        
        # Create ticket description using event name
        trans_dict['ticket_description'] = trans_dict.get('name', f"Event #{trans_dict.get('event_id', 'Unknown')}")
        
        finished_transactions.append(trans_dict)

    context = {
        'logemail': logemail,
        'transactions': filtered_transactions,
        'finished_transactions': finished_transactions,
        'is_admin': is_admin,
        'view_filter': view_filter,
        'active_count': active_count,
        'history_count': history_count,
        'total_count': len(formatted_transactions),
        'user_balance': user_balance,
        'stats': stats
    }
    

    
    return flask.render_template("index.html", **context)


def calculate_platform_stats(connection):
    """Calculate real platform statistics from database."""
    # Total transaction count
    total_transactions = connection.execute(
        "SELECT COUNT(*) as count FROM transactions"
    ).fetchone()['count']
    
    # Total value protected (sum of all transaction prices)
    total_value = connection.execute(
        "SELECT COALESCE(SUM(price), 0) as total FROM transactions"
    ).fetchone()['total']
    
    # Success rate calculation
    total_completed = connection.execute(
        "SELECT COUNT(*) as count FROM transactions WHERE status IN ('completed')"
    ).fetchone()['count']
    
    success_rate = 100.0 if total_transactions == 0 else (total_completed / total_transactions) * 100
    
    # Format total value
    if total_value >= 1000000:
        formatted_value = f"${total_value / 1000000:.1f}M+"
    elif total_value >= 1000:
        formatted_value = f"${total_value / 1000:.0f}K+"
    else:
        formatted_value = f"${total_value}"
    
    # Format transaction count
    if total_transactions >= 1000:
        formatted_transactions = f"{total_transactions / 1000:.0f}K+"
    else:
        formatted_transactions = str(total_transactions)
    
    return {
        'total_value': formatted_value,
        'total_transactions': formatted_transactions,
        'success_rate': f"{success_rate:.1f}%"
    }

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
    if flask.request.method == 'POST':
        connection = insta485.model.get_db()
        target = flask.request.args.get('target', flask.url_for('show_index'))
        return insta485.views.manage.manage_login(connection, target)
    
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
            return flask.redirect(url_for('show_index'))
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
    elif user_type in ['seller', 'user']:
        # Log in as seller (all users are sellers now)
        flask.session['email'] = 'sanjivp2703@gmail.com'
        return flask.redirect(url_for('show_index'))
    else:
        flask.flash('Invalid user type for skip login')
        return flask.redirect(url_for('show_accounts', url='login'))


@insta485.app.route('/accounts/create', methods=['GET', 'POST'])
def create():
    """Display /accounts/create route and handle POST requests."""
    if flask.request.method == 'POST':
        connection = insta485.model.get_db()
        target = flask.request.args.get('target', '/')
        return insta485.views.manage.manage_create(target, connection)

    if 'email' in flask.session:
        return flask.redirect(url_for('show_index'))
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


@insta485.app.route('/accounts/verify/', methods=['GET', 'POST'])
def verify_code():
    """Display and handle email/phone verification."""
    if 'email' not in flask.session:
        return flask.redirect(url_for('show_accounts', url='login'))
    
    if flask.request.method == 'POST':
        # Combine the 4 individual code inputs
        code_parts = [
            flask.request.form.get('code1', ''),
            flask.request.form.get('code2', ''),
            flask.request.form.get('code3', ''),
            flask.request.form.get('code4', '')
        ]
        provided_code = ''.join(code_parts)
        
        if len(provided_code) != 4:
            return flask.render_template("verify.html", error="Please enter a complete 4-digit code.")
        
        email = flask.session['email']
        connection = insta485.model.get_db()
        
        # Try to verify the code
        from insta485.views.manage import verify_code as verify_user_code
        if verify_user_code(email, provided_code, 'email_verification', connection):
            # Verification successful, now redirect to Stripe onboarding
            from insta485.views.manage import seller_onboarding
            return seller_onboarding()
        else:
            return flask.render_template("verify.html", error="Invalid or expired verification code.")
    
    return flask.render_template("verify.html")


@insta485.app.route('/accounts/resend/')
def resend_code():
    """Resend verification code."""
    if 'email' not in flask.session:
        return flask.redirect(url_for('show_accounts', url='login'))
    
    email = flask.session['email']
    connection = insta485.model.get_db()
    
    from insta485.views.manage import create_verification_code
    create_verification_code(email, 'email_verification', connection)
    
    flask.flash('Verification code sent!')
    return flask.redirect(url_for('verify_code'))


@insta485.app.route('/api/events', methods=['GET'])
def get_events():
    """Return a list of events for autocomplete."""
    query = flask.request.args.get('q', '')
    school = flask.request.args.get('school', '')
    connection = insta485.model.get_db()
    
    # Filter events based on school
    if school == 'michigan':
        events = connection.execute(
            "SELECT name, location, event_datetime, is_tbd, max_ticket_price FROM events WHERE (name LIKE ? OR location LIKE ?) AND (name LIKE '%Michigan%' OR name LIKE '%michigan%') LIMIT 10",
            (f"%{query}%", f"%{query}%")
        ).fetchall()
    elif school == 'florida':
        events = connection.execute(
            "SELECT name, location, event_datetime, is_tbd, max_ticket_price FROM events WHERE (name LIKE ? OR location LIKE ?) AND (name LIKE '%Florida%' OR name LIKE '%florida%') LIMIT 10",
            (f"%{query}%", f"%{query}%")
        ).fetchall()
    else:
        # Default behavior - show all events
        events = connection.execute(
            "SELECT name, location, event_datetime, is_tbd, max_ticket_price FROM events WHERE name LIKE ? OR location LIKE ? LIMIT 10",
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
        
        # Handle TBD times
        if row.get('is_tbd', 0):
            formatted_datetime = event_dt.strftime('%A, %b %d, %Y') + ' at TBD'
        else:
            formatted_datetime = event_dt.strftime('%A, %b %d, %Y at %I:%M %p')
        
        results.append({
            'name': row['name'],
            'location': row['location'],
            'datetime': formatted_datetime,
            'raw_datetime': row['event_datetime'],
            'is_tbd': row.get('is_tbd', 0),
            'max_ticket_price': row.get('max_ticket_price', 20000)
        })
    return flask.jsonify(results)

@insta485.app.route('/api/test-verify', methods=['POST'])
def test_verify():
    """Test endpoint to instantly verify a listing for development purposes"""
    try:
        data = flask.request.get_json()
        transaction_id = data.get('transaction_id')

        if not transaction_id:
            return flask.jsonify({'success': False, 'error': 'Missing transaction_id'}), 400

        connection = insta485.model.get_db()

        # Get transaction details
        transaction = connection.execute("""
            SELECT t.*, e.name as event_name, e.location, e.event_datetime
            FROM transactions t
            JOIN events e ON t.event_id = e.event_id
            WHERE t.transaction_id = ?
        """, (transaction_id,)).fetchone()

        if not transaction:
            return flask.jsonify({'success': False, 'error': 'Transaction not found'}), 400

        if transaction['status'] != 'pending_ticket_submission':
            return flask.jsonify({'success': False, 'error': f'Transaction in wrong state: {transaction["status"]}'}), 400

        # Create fake email data for testing
        fake_email_data = {
            'sender': transaction['seller_email'],
            'recipient': transaction['awaiting_ticket_email'],
            'subject': f'Your {transaction["event_name"]} Tickets - Order Confirmation',
            'body': f"""
Thank you for your ticket purchase!
Event: {transaction['event_name']}
Venue: {transaction['location']}
Order Number: TM-123456789
Section: 101, Row A, Seats 5-6
Your tickets are attached as PDF files.
Please arrive 30 minutes early.
Best regards,
Ticketmaster Support
            """,
            'body_text': f'Your tickets for {transaction["event_name"]} at {transaction["location"]}. Section 101, Row A, Seats 5-6.',
            'attachments': ['tickets.pdf'],
            'timestamp': datetime.datetime.now().isoformat()
        }

        # Process through transaction manager
        from insta485.transaction_manager import TransactionManager
        transaction_manager = TransactionManager()

        result = transaction_manager.process_incoming_ticket(transaction_id, fake_email_data)

        if result['success']:
            return flask.jsonify({
                'success': True,
                'message': 'Test verification completed successfully',
                'status': result['status'],
                'payment_deadline': result.get('payment_deadline')
            })
        else:
            return flask.jsonify({
                'success': False,
                'error': result['error']
            }), 400

    except Exception as e:
        print(f"Error in test verification: {e}")
        return flask.jsonify({'success': False, 'error': str(e)}), 500


@insta485.app.route('/pay/<int:transaction_id>/process', methods=['POST'])
def process_buyer_payment(transaction_id):
    """Process buyer payment through Stripe"""
    try:
        import stripe
        connection = insta485.model.get_db()

        # Get transaction details
        transaction = connection.execute("""
            SELECT t.*, e.name as event_name
            FROM transactions t
            JOIN events e ON t.event_id = e.event_id
            WHERE t.transaction_id = ?
        """, (transaction_id,)).fetchone()

        if not transaction:
            return flask.jsonify({'success': False, 'error': 'Transaction not found'}), 404

        if transaction['status'] != 'waiting_for_payment':
            return flask.jsonify({'success': False, 'error': 'Transaction not available for payment'}), 400

        # Create Stripe checkout session
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': f'Tickets for {transaction["event_name"]}',
                        'description': f'Transaction #{transaction_id}'
                    },
                    'unit_amount': int(transaction['price'] * 100),  # Convert to cents
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=f'https://safetransaction.app/payment-success/{transaction_id}',
            cancel_url=f'https://safetransaction.app/ticket/{transaction_id}',
            metadata={'transaction_id': transaction_id}
        )

        return flask.jsonify({'checkout_url': session.url})

    except Exception as e:
        print(f"Error creating payment session: {e}")
        return flask.jsonify({'success': False, 'error': str(e)}), 500


@insta485.app.route('/payment-success/<int:transaction_id>')
def payment_success(transaction_id):
    """Handle successful payment"""
    connection = insta485.model.get_db()

    # Get transaction details
    transaction = connection.execute("""
        SELECT t.*, e.name as event_name
        FROM transactions t
        JOIN events e ON t.event_id = e.event_id
        WHERE t.transaction_id = ?
    """, (transaction_id,)).fetchone()

    if not transaction:
        flask.abort(404)

    # Process payment through transaction manager
    from insta485.transaction_manager import TransactionManager
    transaction_manager = TransactionManager()

    # For now, we'll simulate successful payment processing
    # In production, you'd verify the payment with Stripe webhooks
    try:
        # Update transaction status to indicate payment received
        connection.execute("""
            UPDATE transactions 
            SET payment_received = 1,
                payment_received_time = CURRENT_TIMESTAMP,
                status = 'both_received_processing'
            WHERE transaction_id = ?
        """, (transaction_id,))
        connection.commit()

        # Forward tickets to buyer
        transaction_manager._forward_ticket_to_buyer(transaction_id, connection)

        # Add funds to seller balance (price * 1.1, converted to cents)
        seller_amount_dollars = float(transaction['price']) * 1.1
        seller_amount_cents = int(seller_amount_dollars * 100)
        
        # Add funds to seller balance (using users.balance column, stored in cents)
        connection.execute("""
            UPDATE users 
            SET balance = balance + ?
            WHERE email = ?
        """, (seller_amount_cents, transaction['seller_email']))
        
        print(f"💰 Added ${seller_amount_dollars:.2f} ({seller_amount_cents} cents) to seller {transaction['seller_email']} balance")

        # Send "Your sale is complete" email to seller after successful payment
        try:
            from insta485.mailgun_sender import mailgun_sender
            from datetime import datetime
            
            # Create a payment deadline (not used in this context but required by function)
            payment_deadline = datetime.now()
            
            mailgun_sender.send_seller_verification_success(
                seller_email=transaction['seller_email'],
                transaction_id=transaction_id,
                event_name=transaction['event_name'],
                buyer_email=transaction['buyer_email'],
                payment_deadline=payment_deadline
            )
            
            print(f"📧 Sent 'sale complete' email to seller {transaction['seller_email']}")
        except Exception as e:
            print(f"❌ Failed to send seller success email: {e}")

        flask.flash('Payment successful! Your tickets have been sent to your email.')

    except Exception as e:
        print(f"Error processing payment success: {e}")
        flask.flash('Payment was successful but there was an error processing your order. Please contact support.')

    return flask.render_template('payment_success.html', 
                               transaction=transaction,
                               transaction_id=transaction_id,
                               buyer_email=transaction['buyer_email'],
                               price=transaction['price'],
                               payment_time="Just now",
                               event_name=transaction['event_name'],
                               email_sent=True)

@insta485.app.route('/receipt/<int:transaction_id>')
def download_receipt(transaction_id):
    """Generate and serve a downloadable PDF receipt for a transaction."""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Frame, PageTemplate
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.pdfgen import canvas
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    from io import BytesIO
    from datetime import datetime
    
    connection = insta485.model.get_db()
    
    # Get transaction details with event information
    transaction = connection.execute("""
        SELECT t.*, e.name as event_name, e.location, e.event_datetime
        FROM transactions t
        JOIN events e ON t.event_id = e.event_id
        WHERE t.transaction_id = ?
    """, (transaction_id,)).fetchone()
    
    if not transaction:
        flask.abort(404)
    
    # Create a BytesIO buffer to hold the PDF
    buffer = BytesIO()
    
    # Create the PDF document
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch, 
                           leftMargin=0.75*inch, rightMargin=0.75*inch)
    
    # Define styles matching the email aesthetics
    styles = getSampleStyleSheet()
    
    # Custom styles inspired by the email templates
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#667eea'),
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#475569'),
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName='Helvetica'
    )
    
    section_header_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#0f172a'),
        spaceAfter=8,
        spaceBefore=16,
        fontName='Helvetica-Bold',
        backColor=colors.HexColor('#f8fafc'),
        borderPadding=8
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#475569'),
        spaceAfter=4,
        fontName='Helvetica'
    )
    
    highlight_style = ParagraphStyle(
        'Highlight',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#0f172a'),
        fontName='Helvetica-Bold'
    )
    
    # Format dates
    current_time = datetime.now().strftime('%B %d, %Y at %I:%M %p')
    try:
        event_dt = datetime.strptime(transaction['event_datetime'], '%Y-%m-%d %H:%M:%S')
        formatted_event_time = event_dt.strftime('%A, %B %d, %Y at %I:%M %p')
    except:
        formatted_event_time = transaction['event_datetime']
    
    # Build the story (content)
    story = []
    
    # Header with gradient-like styling
    story.append(Paragraph("🛡️ SAFE TRANSACTION", title_style))
    story.append(Paragraph("Official Receipt", subtitle_style))
    story.append(Spacer(1, 12))
    
    # Receipt metadata in a styled table
    receipt_info = [
        ['Receipt Generated:', current_time],
        ['Transaction ID:', f'ST-{transaction_id}'],
    ]
    
    receipt_table = Table(receipt_info, colWidths=[2*inch, 3*inch])
    receipt_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f1f5f9')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#475569')),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#0f172a')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
    ]))
    
    story.append(receipt_table)
    story.append(Spacer(1, 20))
    
    # Event Information Section
    story.append(Paragraph("🎫 TICKET INFORMATION", section_header_style))
    
    event_info = [
        ['Event:', transaction['event_name']],
        ['Venue:', transaction['location']],
        ['Date & Time:', formatted_event_time],
    ]
    
    event_table = Table(event_info, colWidths=[1.5*inch, 4*inch])
    event_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0fff4')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#059669')),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#0f172a')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bbf7d0')),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
    ]))
    
    story.append(event_table)
    story.append(Spacer(1, 16))
    
    # Purchase Details Section
    story.append(Paragraph("💳 PURCHASE DETAILS", section_header_style))
    
    purchase_info = [
        ['Buyer Email:', transaction['buyer_email']],
        ['Seller Email:', transaction['seller_email']],
        ['Amount Paid:', f"${transaction['price']:.2f}"],
        ['Status:', transaction['status'].replace('_', ' ').title()],
    ]
    
    purchase_table = Table(purchase_info, colWidths=[1.5*inch, 4*inch])
    purchase_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f4ff')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#667eea')),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#0f172a')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#c3d1ff')),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
    ]))
    
    story.append(purchase_table)
    story.append(Spacer(1, 16))
    
    # Timeline Section
    story.append(Paragraph("⏱️ TRANSACTION TIMELINE", section_header_style))
    
    timeline_info = [
        ['Transaction Created:', transaction['created_time'] or 'N/A'],
        ['Payment Processed:', transaction.get('payment_received_time', 'N/A')],
    ]
    
    timeline_table = Table(timeline_info, colWidths=[2*inch, 3.5*inch])
    timeline_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#fffbeb')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#d97706')),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#0f172a')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#fde68a')),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
    ]))
    
    story.append(timeline_table)
    story.append(Spacer(1, 20))
    
    # Important Notes Section
    story.append(Paragraph("📋 IMPORTANT INFORMATION", section_header_style))
    
    notes = [
        "• This receipt serves as proof of purchase",
        "• Keep this receipt for your records",
        "• Contact support at safetransactiontix@gmail.com for any issues",
        "• You have 24 hours after the event to file any complaints",
        "• All transactions are protected by Safe Transaction's guarantee"
    ]
    
    for note in notes:
        story.append(Paragraph(note, normal_style))
    
    story.append(Spacer(1, 24))
    
    # Footer
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#94a3b8'),
        alignment=TA_CENTER,
        fontName='Helvetica',
        spaceAfter=4
    )
    
    story.append(Paragraph("Thank you for using Safe Transaction!", highlight_style))
    story.append(Spacer(1, 8))
    story.append(Paragraph("Safe Transaction LLC • Secure Ticket Marketplace", footer_style))
    story.append(Paragraph("Visit us at safetransaction.com", footer_style))
    
    # Build the PDF
    doc.build(story)
    
    # Get the PDF content from the buffer
    pdf_content = buffer.getvalue()
    buffer.close()
    
    # Create response with PDF content
    response = flask.make_response(pdf_content)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename="receipt_ST-{transaction_id}.pdf"'
    
    return response

# Removed separate create_listing route - listing creation is now done directly on home page


@insta485.app.route('/create-transaction', methods=['POST'])
def create_transaction():
    """Create a new transaction using the automated system."""
    if check_login():
        return check_login()
    
    seller_email = flask.session['email']
    buyer_email = flask.request.form['buyer_email']
    price = float(flask.request.form['ticket_price'])  # Changed to float for new system
    event_name = flask.request.form['event_name']
    event_location = flask.request.form['event_location']
    event_datetime_raw = flask.request.form['event_datetime']
    school = flask.request.form.get('school', 'michigan')  # Get school from form, default to michigan
    
    # Use default deadlines
    ticket_deadline_hours = 24  # 24 hours to send tickets
    payment_deadline_hours = 48  # 48 hours for buyer to pay
    
    # Fix datetime format - convert from HTML5 datetime-local to SQLite format
    if 'T' in event_datetime_raw and len(event_datetime_raw) == 16:
        # Format: "2026-07-05T12:32" -> "2026-07-05 12:32:00"
        event_datetime = event_datetime_raw.replace('T', ' ') + ':00'
    else:
        event_datetime = event_datetime_raw
    
    # Validate that seller isn't creating transaction with themselves
    if seller_email == buyer_email:
        flask.flash('You cannot create a transaction with yourself.', 'error')
        return flask.redirect(url_for('show_index'))
    
    # Validate ticket price against event maximum
    connection = insta485.model.get_db()
    event = connection.execute(
        "SELECT max_ticket_price FROM events WHERE name = ? AND location = ?",
        (event_name, event_location)
    ).fetchone()
    
    if event:
        max_price_dollars = event['max_ticket_price'] / 100.0
        if price > max_price_dollars:
            flask.flash(f'Maximum ticket price for this event is ${max_price_dollars:.0f}', 'error')
            return flask.redirect(url_for('show_index'))
    
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
    
    # Use new automated transaction system
    try:
        from insta485.transaction_manager import TransactionManager
        
        transaction_manager = TransactionManager()
        
        event_details = {
            'name': event_name,
            'location': event_location,
            'datetime': event_datetime
        }
        
        result = transaction_manager.create_listing(
            seller_email=seller_email,
            buyer_email=buyer_email,
            price=price,
            event_details=event_details,
            school=school
        )
        
        # Return success response for AJAX request to show popup
        return flask.jsonify({
            'success': True,
            'transaction_id': result['transaction_id'],
            'ticket_email': result['ticket_email'],
            'status': result['status'],
            'message': result['message']
        })
        
    except Exception as e:
        print(f"Error creating transaction: {e}")
        return flask.jsonify({
            'success': False,
            'error': str(e)
        })


def send_buyer_email_1(transaction_id, buyer_email, event_name, price, seller_email, payment_deadline=None):
    """Send Email 1 to buyer with secure payment link and deadline."""
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
                
                {"" if not payment_deadline else f'''
                <div style="background: #fff3cd; padding: 20px; border-radius: 8px; border-left: 4px solid #ffc107; margin: 20px 0;">
                    <h3 style="color: #856404; margin: 0 0 10px 0;">⏰ Payment Deadline</h3>
                    <p style="margin: 0; color: #856404;"><strong>You must complete payment by: {payment_deadline.strftime("%B %d, %Y at %I:%M %p")}</strong></p>
                    <p style="margin: 5px 0 0 0; color: #856404; font-size: 14px;">This offer expires in 1 hour. After that, the payment link will be disabled.</p>
                </div>
                '''}
                
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

    {"" if not payment_deadline else f'''
    ⏰ PAYMENT DEADLINE: {payment_deadline.strftime("%B %d, %Y at %I:%M %p")}
    This offer expires in 1 hour. After that, the payment link will be disabled.
    '''}

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
    
    # Check if payment deadline has passed and format it
    payment_deadline_passed = False
    payment_deadline_formatted = None
    
    # If already expired, show the expired page
    if transaction['status'] == 'payment_deadline_expired':
        # Format datetime for display
        event_dt = datetime.datetime.strptime(transaction['event_datetime'], '%Y-%m-%d %H:%M:%S')
        formatted_datetime = event_dt.strftime('%A, %B %d, %Y at %I:%M %p')
        
        return flask.render_template("payment_expired.html",
                                   transaction_id=transaction_id,
                                   event_name=transaction['name'],
                                   event_location=transaction['location'],
                                   event_datetime=formatted_datetime,
                                   price=transaction['price'],
                                   seller_email=transaction['seller_email'])
    
    # If transaction is cancelled, show the cancelled page (only sellers can cancel)
    if transaction['status'] == 'cancelled_by_seller':
        # Format datetime for display
        event_dt = datetime.datetime.strptime(transaction['event_datetime'], '%Y-%m-%d %H:%M:%S')
        formatted_datetime = event_dt.strftime('%A, %B %d, %Y at %I:%M %p')
        
        return flask.render_template("transaction_cancelled.html",
                                   transaction_id=transaction_id,
                                   event_name=transaction['name'],
                                   event_location=transaction['location'],
                                   event_datetime=formatted_datetime,
                                   price=transaction['price'],
                                   seller_email=transaction['seller_email'])
    
    if transaction['payment_deadline'] and transaction['status'] == 'waiting_for_payment':
        try:
            deadline = datetime.datetime.strptime(transaction['payment_deadline'], '%Y-%m-%d %H:%M:%S')
            payment_deadline_formatted = deadline.strftime('%B %d, %Y at %I:%M %p')
            if datetime.datetime.now() > deadline:
                payment_deadline_passed = True
                # Update transaction status to expired
                connection.execute(
                    "UPDATE transactions SET status = 'payment_deadline_expired' WHERE transaction_id = ?",
                    (transaction_id,)
                )
                connection.commit()
                # Redirect to expired page
                event_dt = datetime.datetime.strptime(transaction['event_datetime'], '%Y-%m-%d %H:%M:%S')
                formatted_datetime = event_dt.strftime('%A, %B %d, %Y at %I:%M %p')
                
                return flask.render_template("payment_expired.html",
                                           transaction_id=transaction_id,
                                           event_name=transaction['name'],
                                           event_location=transaction['location'],
                                           event_datetime=formatted_datetime,
                                           price=transaction['price'],
                                           seller_email=transaction['seller_email'])
        except ValueError:
            pass  # Invalid datetime format, continue normally
    
    # Format event datetime
    event_dt = datetime.datetime.strptime(transaction['event_datetime'], '%Y-%m-%d %H:%M:%S')
    formatted_datetime = event_dt.strftime('%A, %B %d, %Y at %I:%M %p')
    
    context = {
        'transaction': transaction,
        'event_name': transaction['name'],
        'event_location': transaction['location'],
        'event_datetime': formatted_datetime,
        'payment_deadline_passed': payment_deadline_passed,
        'payment_deadline_formatted': payment_deadline_formatted,
        'is_buyer_logged_in': ('email' in flask.session and 
                               flask.session['email'] == transaction['buyer_email'])
    }
    
    return flask.render_template("buyer_ticket_card.html", **context)


@insta485.app.route('/ticket_status_check/<int:transaction_id>')
def ticket_status_check(transaction_id):
    """Smart router: Check transaction status and route to cancellation page or Stripe payment."""
    connection = insta485.model.get_db()
    
    # Get transaction and event details (same logic as buyer_ticket_card)
    transaction = connection.execute(
        """SELECT t.*, e.name, e.location, e.event_datetime 
           FROM transactions t 
           JOIN events e ON t.event_id = e.event_id 
           WHERE t.transaction_id = ?""",
        (transaction_id,)
    ).fetchone()
    
    if not transaction:
        flask.abort(404)
    
    # Check if transaction is cancelled (only sellers can cancel)
    if transaction['status'] == 'cancelled_by_seller':
        # Redirect to dedicated cancellation page
        return flask.redirect(flask.url_for('show_cancellation_page', transaction_id=transaction_id))
    
    # Check if payment deadline has passed
    if transaction['payment_deadline'] and transaction['status'] == 'waiting_for_payment':
        try:
            deadline = datetime.datetime.strptime(transaction['payment_deadline'], '%Y-%m-%d %H:%M:%S')
            if datetime.datetime.now() > deadline:
                # Update transaction status to expired
                connection.execute(
                    "UPDATE transactions SET status = 'payment_deadline_expired' WHERE transaction_id = ?",
                    (transaction_id,)
                )
                connection.commit()
                # Redirect to cancellation page (expired is also a form of cancellation)
                return flask.redirect(flask.url_for('show_cancellation_page', transaction_id=transaction_id))
        except ValueError:
            pass  # Invalid datetime format, continue to payment
    
    # Transaction is active - redirect to Stripe payment
    from insta485.views.manage import send_payment_buyer
    return send_payment_buyer(transaction_id)


@insta485.app.route('/cancelled/<int:transaction_id>')
def show_cancellation_page(transaction_id):
    """Display dedicated cancellation page with proper messaging."""
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
    
    # Format datetime for display
    event_dt = datetime.datetime.strptime(transaction['event_datetime'], '%Y-%m-%d %H:%M:%S')
    formatted_datetime = event_dt.strftime('%A, %B %d, %Y at %I:%M %p')
    
    # Determine cancellation reason
    if transaction['status'] == 'cancelled_by_seller':
        cancellation_reason = 'seller_cancelled'
    elif transaction['status'] == 'payment_deadline_expired':
        cancellation_reason = 'payment_expired'
    else:
        cancellation_reason = 'unknown'
    
    return flask.render_template("transaction_cancelled.html",
                               transaction_id=transaction_id,
                               event_name=transaction['name'],
                               event_location=transaction['location'],
                               event_datetime=formatted_datetime,
                               price=transaction['price'],
                               seller_email=transaction['seller_email'],
                               cancellation_reason=cancellation_reason)


@insta485.app.route('/simulate-payment/<int:transaction_id>', methods=['POST'])
def simulate_payment(transaction_id):
    """Simulate payment processing for the transaction."""
    connection = insta485.model.get_db()
    
    # Get transaction details including status and deadline
    transaction = connection.execute(
        "SELECT buyer_email, seller_email, price, status, payment_deadline FROM transactions WHERE transaction_id = ?",
        (transaction_id,)
    ).fetchone()
    
    if not transaction:
        flask.abort(404)
    
    # Check if payment deadline has passed
    if transaction['payment_deadline'] and transaction['status'] == 'waiting_for_payment':
        try:
            deadline = datetime.datetime.strptime(transaction['payment_deadline'], '%Y-%m-%d %H:%M:%S')
            if datetime.datetime.now() > deadline:
                # Update status and redirect to expired page
                connection.execute(
                    "UPDATE transactions SET status = 'payment_deadline_expired' WHERE transaction_id = ?",
                    (transaction_id,)
                )
                connection.commit()
                flask.flash('Payment deadline has expired. Please contact the seller for a new listing.', 'error')
                return flask.redirect(flask.url_for('buyer_ticket_card', transaction_id=transaction_id))
        except ValueError:
            pass
    
    # Check if transaction is cancelled (only sellers can cancel)
    if transaction['status'] == 'cancelled_by_seller':
        flask.flash('This transaction has been cancelled.', 'error')
        return flask.redirect(flask.url_for('buyer_ticket_card', transaction_id=transaction_id))
    
    # Check if transaction is not in payable status
    if transaction['status'] not in ['waiting_for_payment', 'pending']:
        flask.flash('This transaction cannot be paid at this time.', 'error')
        return flask.redirect(flask.url_for('buyer_ticket_card', transaction_id=transaction_id))
    
    # Update transaction status to payment processing
    connection.execute(
        "UPDATE transactions SET status = 'waiting_for_payment', payment_received_time = CURRENT_TIMESTAMP WHERE transaction_id = ?",
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
    
    # Update to waiting for ticket
    connection.execute(
        "UPDATE transactions SET status = 'waiting_for_ticket' WHERE transaction_id = ?",
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
    
    if transaction['status'] != 'ticket_forwarded_funds_held':
        return f"<html><body><h2>❌ Invalid action. Transaction status is: {transaction['status']}</h2></body></html>"
    
    # Update transaction status to completed
    connection.execute(
        "UPDATE transactions SET status = 'completed' WHERE transaction_id = ?",
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
    """Send notification to seller about payment received using the modern template."""
    import flask
    
    # Get transaction and event details for the template
    connection = insta485.model.get_db()
    transaction_details = connection.execute(
        """
        SELECT t.transaction_id, t.buyer_email, t.price, t.status,
               e.name as event_name, e.location, e.event_datetime
        FROM transactions t
        JOIN events e ON t.event_id = e.event_id
        WHERE t.transaction_id = ?
        """,
        (transaction_id,)
    ).fetchone()
    
    if not transaction_details:
        print(f"❌ Transaction {transaction_id} not found")
        return
    
    # Format event datetime for display
    import datetime
    try:
        event_dt = datetime.datetime.strptime(transaction_details['event_datetime'], '%Y-%m-%d %H:%M:%S')
        event_datetime_str = event_dt.strftime('%A, %b %d, %Y at %I:%M %p')
    except ValueError:
        event_datetime_str = transaction_details['event_datetime']
    
    # Prepare template context
    template_context = {
        'transaction_id': transaction_id,
        'transaction': {
            'transaction_id': transaction_id,
            'buyer_email': transaction_details['buyer_email'],
            'price': transaction_details['price'],
            'event_name': transaction_details['event_name'],
            'location': transaction_details['location'],
            'event_datetime': transaction_details['event_datetime'],
            'event_datetime_str': event_datetime_str
        },
        'dashboard_url': 'http://localhost:8000/seller'  # TODO: Make this configurable
    }
    
    subject = f"💰 Payment Received - Transfer Ticket Now (Transaction #{transaction_id})"
    
    try:
        # Render the beautiful template
        html_body = flask.render_template('seller_payment_received.html', **template_context)
    except Exception as e:
        # Fallback if template rendering fails
        html_body = f"<p>Payment received for Transaction #{transaction_id}. Please check your dashboard.</p>"
    
    # Create plain text version
    text_body = f"""
    Great news! Your buyer has paid for Transaction #{transaction_id}.

        Event: {transaction_details['event_name']}
        Location: {transaction_details['location']}
        Date: {event_datetime_str}
        Amount: ${transaction_details['price']}
        Buyer: {transaction_details['buyer_email']}

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
        print(f"🎫 Event: {transaction_details['event_name']}")
        print(f"💰 Amount: ${transaction_details['price']}")
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


# Legacy route - redirects to main index since we only support sellers now
@insta485.app.route('/transactions/', methods=['POST'])
def initiate_transaction():
    """Legacy route - redirect to main page."""
    if 'email' not in flask.session:
        return flask.redirect(url_for('show_accounts', url='login'))

    flask.flash('Please use the new listing creation form on the main page.', 'info')
    return flask.redirect(url_for('show_index'))

@insta485.app.route('/send-ticket-sent-email/<int:transaction_id>', methods=['POST'])
def send_ticket_sent_email_route(transaction_id):
    """Send ticket sent notification email to buyer from active listings."""
    if 'email' not in flask.session:
        return flask.jsonify({'success': False, 'error': 'Not logged in'}), 401
    
    connection = insta485.model.get_db()
    
    # Get transaction details with event information and verify seller ownership
    transaction = connection.execute("""
        SELECT t.*, e.name as event_name, e.location, e.event_datetime
        FROM transactions t 
        JOIN events e ON t.event_id = e.event_id
        WHERE t.transaction_id = ? AND t.seller_email = ?
    """, (transaction_id, flask.session['email'])).fetchone()
    
    if not transaction:
        return flask.jsonify({'success': False, 'error': 'Transaction not found or access denied'}), 404
    
    try:
        # Import the email function from admin_actions
        from insta485.views.admin_actions import send_ticket_sent_notifications
        
        # Send the notification emails
        send_ticket_sent_notifications(transaction_id, transaction)
        
        return flask.jsonify({
            'success': True, 
            'message': f'Ticket sent notification email sent successfully for transaction #{transaction_id}'
        })
        
    except Exception as e:
        print(f"Error sending ticket sent email: {e}")
        return flask.jsonify({
            'success': False, 
            'error': f'Failed to send email: {str(e)}'
        }), 500

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
        elif row['status'] in ('waiting_for_ticket', 'completed'):
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
    if row['status'] in ('waiting_for_payment', 'waiting_for_ticket', 'completed'):
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
    if row['status'] in ('waiting_for_payment', 'waiting_for_ticket', 'completed'):
        return "<html><body><h2>You have already accepted this offer. You may close this tab and return to your email.</h2></body></html>"
    elif row['status'] == 'rejected':
        return "<html><body><h2>You have already rejected this offer.</h2></body></html>"
    connection.execute(
        "UPDATE transactions SET status = 'waiting_for_payment_processing' WHERE transaction_id = ?",
        (transaction_id,)
    )
    return insta485.views.manage.send_payment_buyer(transaction_id)

@insta485.app.route('/success')
def payment_success_generic():
    """Handle successful payment by updating status and showing success page."""
    # Get transaction_id from query parameter (since buyer doesn't have a session)
    transaction_id = flask.request.args.get('transaction_id')
    
    if not transaction_id:
        # Also check session as fallback for backwards compatibility
        transaction_id = flask.session.pop('transaction_id', None) if 'transaction_id' in flask.session else None
    
    if not transaction_id:
        return flask.render_template('payment_success.html', 
                                   transaction_id="UNKNOWN",
                                   buyer_email="UNKNOWN",
                                   price=0.00,
                                   payment_time="Unknown")
    
    # Convert to int if it's a string
    try:
        transaction_id = int(transaction_id)
    except (ValueError, TypeError):
        return flask.render_template('payment_success.html', 
                                   transaction_id="INVALID",
                                   buyer_email="UNKNOWN",
                                   price=0.00,
                                   payment_time="Unknown")
    connection = insta485.model.get_db()
    
    # Get event time and transaction info for confirmation email
    row = connection.execute(
        """
        SELECT t.buyer_email, t.seller_email, t.price, e.name as event_name, e.event_datetime, t.payment_received_time 
        FROM transactions t 
        JOIN events e ON t.event_id = e.event_id 
        WHERE t.transaction_id = ?
        """,
        (transaction_id,)
    ).fetchone()
    
    if not row:
        return flask.render_template('payment_success.html', 
                                   transaction_id=transaction_id,
                                   buyer_email="UNKNOWN",
                                   price=0.00,
                                   payment_time="Unknown")
    
    # Calculate expected_send as 1 minute after payment_received_time (or now if not available)
    import datetime
    payment_time = row['payment_received_time']
    if payment_time:
        payment_dt = datetime.datetime.strptime(payment_time, '%Y-%m-%d %H:%M:%S')
    else:
        payment_dt = datetime.datetime.now()
    
    # Format payment time for display
    payment_time_display = payment_dt.strftime('%a, %b %d, %I:%M %p')
    
    # Payment received - AUTOMATICALLY complete the transaction
    connection.execute(
        """
        UPDATE transactions 
        SET status = 'completed', 
            payment_received = 1,
            payment_received_time = CURRENT_TIMESTAMP
        WHERE transaction_id = ?
        """,
        (transaction_id,)
    )
    
    # AUTOMATIC TICKET TRANSFER - Send ticket to buyer
    try:
        from insta485.mailgun_sender import mailgun_sender
        
        # Get original ticket details from database
        ticket_data = connection.execute(
            "SELECT ticket_email_data, original_event_details FROM transactions WHERE transaction_id = ?",
            (transaction_id,)
        ).fetchone()
        
        # Send ticket to buyer
        mailgun_sender.send_ticket_to_buyer(
            buyer_email=row['buyer_email'],
            transaction_id=transaction_id,
            event_name=row['event_name'],
            seller_email=row['seller_email']
        )
        
        print(f"🎫 AUTO-TRANSFER: Ticket sent to buyer {row['buyer_email']}")
        
    except Exception as e:
        print(f"❌ AUTO-TRANSFER ERROR: {e}")
    
    # AUTOMATIC FUND RELEASE - Add funds to seller balance
    try:
        # Calculate seller amount (price * 1.1 as requested, converted to cents)
        seller_amount_dollars = float(row['price']) * 1.1
        seller_amount_cents = int(seller_amount_dollars * 100)
        
        # Add to seller balance (using users.balance column, stored in cents)
        connection.execute("""
            UPDATE users 
            SET balance = balance + ?
            WHERE email = ?
        """, (seller_amount_cents, row['seller_email']))
        
        # Send fund notification to seller
        mailgun_sender.send_seller_payment_received(
            seller_email=row['seller_email'],
            transaction_id=transaction_id,
            event_name=row['event_name'],
            amount=seller_amount_dollars,
            buyer_email=row['buyer_email']
        )
        
        print(f"💰 AUTO-RELEASE: ${seller_amount_dollars:.2f} ({seller_amount_cents} cents) added to seller {row['seller_email']} balance")
        
    except Exception as e:
        print(f"❌ AUTO-RELEASE ERROR: {e}")
    
    # Send confirmation emails to both parties
    email_sent = False
    if row['buyer_email'] and row['event_name'] and row['price'] and row['seller_email']:
        try:
            email_sent = send_accept_confirmation_email(row['buyer_email'], row['event_name'], row['price'], row['seller_email'], transaction_id=transaction_id)
            if email_sent:
                print(f"✅ Confirmation email sent to {row['buyer_email']}")
            else:
                print(f"❌ Confirmation email failed for {row['buyer_email']} - likely not authorized in Mailgun sandbox")
        except Exception as e:
            print(f"❌ Confirmation email error for {row['buyer_email']}: {e}")
            email_sent = False
    
    # Render the new success page
    context = {
        'transaction_id': transaction_id,
        'buyer_email': row['buyer_email'],
        'price': row['price'],
        'payment_time': payment_time_display,
        'event_name': row['event_name'],
        'email_sent': email_sent
    }
    
    return flask.render_template('payment_success.html', **context)

@insta485.app.route('/cancel', methods=['GET', 'POST'])
def payment_cancel():
    """Handle cancelled payment: mark cancel requested, cancel if both agree."""
    connection = insta485.model.get_db()
    if flask.request.method == 'POST':
        transaction_id = flask.request.form.get('transaction_id')
        if not transaction_id:
            flask.flash('Missing transaction info')
            return flask.redirect(url_for('show_index'))
        # Fetch transaction
        transaction = connection.execute(
            "SELECT buyer_cancel_requested, seller_cancel_requested FROM transactions WHERE transaction_id = ?",
            (transaction_id,)
        ).fetchone()
        if not transaction:
            flask.flash('Transaction not found')
            return flask.redirect(url_for('show_index'))
        
        # Since platform is seller-only now, assume user is seller for cancellation
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
        return flask.redirect(url_for('show_index'))
    # GET fallback
    return flask.redirect(url_for('show_index'))

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
        # Only allow if status is waiting_for_ticket
        if transaction['status'] != 'waiting_for_ticket':
            return "<html><body><h2>Invalid action for current transaction status.</h2></body></html>"
        
        # Update status to ticket_forwarded_funds_held
        connection.execute(
            "UPDATE transactions SET status = 'ticket_forwarded_funds_held' WHERE transaction_id = ?",
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
            return flask.redirect(flask.url_for('show_index'))
        else:
            return "<html><body><h2>✅ Thank you! The buyer has been notified that the ticket was sent. You may now close this tab.</h2></body></html>"
    # Buyer or anyone with the link confirms ticket received
    elif action in ['confirm', 'received']:
        # Only check transaction_id, update status
        connection.execute(
            "UPDATE transactions SET status = 'ticket_forwarded_funds_held' WHERE transaction_id = ?",
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
        return flask.redirect(flask.url_for('show_index'))
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
            
            # Check if transaction is still in ticket_forwarded_funds_held status
            transaction = connection.execute(
                "SELECT status, buyer_email, seller_email FROM transactions WHERE transaction_id = ?",
                (transaction_id,)
            ).fetchone()
            
            if transaction and transaction['status'] == 'ticket_forwarded_funds_held':
                # Auto-complete the transaction
                connection.execute(
                    "UPDATE transactions SET status = 'completed' WHERE transaction_id = ?",
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
