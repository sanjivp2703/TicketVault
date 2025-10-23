import flask
import insta485
from insta485.views.balance import add_earnings, deduct_withdrawal
from insta485.views.manage import hash_password

@insta485.app.route('/admin', methods=['GET'], endpoint='admin_dashboard')
def admin_dashboard():
    """Comprehensive admin dashboard showing all database content."""
    if 'email' not in flask.session:
        return flask.abort(403)
    connection = insta485.model.get_db()
    user = connection.execute(
        'SELECT is_admin FROM users WHERE email = ?',
        (flask.session['email'],)
    ).fetchone()
    if not user or not user['is_admin']:
        return flask.abort(403)
    
    # Get all users
    users = connection.execute(
        """SELECT email, firstname, lastname, stripe_id, is_admin, balance, created,
                  CASE WHEN phone_number IS NOT NULL THEN phone_number ELSE 'N/A' END as phone_number,
                  CASE WHEN email_verified IS NOT NULL THEN email_verified ELSE 0 END as email_verified,
                  CASE WHEN phone_verified IS NOT NULL THEN phone_verified ELSE 0 END as phone_verified,
                  CASE WHEN last_login IS NOT NULL THEN last_login ELSE 'Never' END as last_login
           FROM users ORDER BY created DESC"""
    ).fetchall()
    
    # Get transactions that need action (priority)
    action_needed = connection.execute(
        """SELECT t.*, e.name AS ticket_description, e.location, e.event_datetime,
                  u1.firstname || ' ' || u1.lastname AS buyer_name,
                  u2.firstname || ' ' || u2.lastname AS seller_name
           FROM transactions t 
           LEFT JOIN events e ON t.event_id = e.event_id
           LEFT JOIN users u1 ON t.buyer_email = u1.email
           LEFT JOIN users u2 ON t.seller_email = u2.email
           WHERE t.status IN ('pending_ticket_submission', 'waiting_for_verification', 'waiting_for_ticket', 'waiting_for_payment_processing', 'waiting_for_payment', 'ticket_forwarded_funds_held')
           ORDER BY t.created_time DESC"""
    ).fetchall()
    
    # Get all transactions
    transactions = connection.execute(
        """SELECT t.*, e.name AS ticket_description, e.location, e.event_datetime,
                  u1.firstname || ' ' || u1.lastname AS buyer_name,
                  u2.firstname || ' ' || u2.lastname AS seller_name
           FROM transactions t 
           LEFT JOIN events e ON t.event_id = e.event_id
           LEFT JOIN users u1 ON t.buyer_email = u1.email
           LEFT JOIN users u2 ON t.seller_email = u2.email
           ORDER BY t.created_time DESC LIMIT 50"""
    ).fetchall()
    
    # Get all complaints
    complaints = connection.execute(
        """SELECT t.*, e.name AS ticket_description, e.location, e.event_datetime,
                  u1.firstname || ' ' || u1.lastname AS buyer_name,
                  u2.firstname || ' ' || u2.lastname AS seller_name
           FROM transactions t 
           JOIN events e ON t.event_id = e.event_id
           LEFT JOIN users u1 ON t.buyer_email = u1.email
           LEFT JOIN users u2 ON t.seller_email = u2.email
           WHERE t.status = 'complaint_filed' 
           ORDER BY t.transaction_id DESC"""
    ).fetchall()
    
    # Get verification codes (if table exists)
    verification_codes = []
    try:
        verification_codes = connection.execute(
            """SELECT id, email, code, code_type, expires_at, used, created_at
               FROM verification_codes 
               ORDER BY created_at DESC LIMIT 20"""
        ).fetchall()
    except:
        pass  # Table might not exist yet
    
    # Get pending withdrawals
    pending_withdrawals = []
    try:
        pending_withdrawals = connection.execute(
            """SELECT wr.*, u.firstname, u.lastname
               FROM withdrawal_requests wr
               JOIN users u ON wr.user_email = u.email
               WHERE wr.status = 'pending'
               ORDER BY wr.created_at ASC"""
        ).fetchall()
    except:
        pass  # Table might not exist yet
    
    # Calculate statistics
    stats = {
        'total_users': len(users),
        'admin_users': len([u for u in users if u['is_admin']]),
        'verified_users': len([u for u in users if u['email_verified']]),
        'total_transactions': len(transactions),
        'active_complaints': len(complaints),
        'total_balance': sum(u['balance'] for u in users if u['balance']),
        'pending_withdrawals': len(pending_withdrawals),
    }
    
    context = {
        'is_admin': True,
        'logemail': flask.session['email'],
        'users': users,
        'transactions': transactions,
        'action_needed': action_needed,
        'complaints': complaints,
        'verification_codes': verification_codes,
        'pending_withdrawals': pending_withdrawals,
        'stats': stats,
        'user_type': 'admin',
    }
    return flask.render_template('admin_comprehensive.html', **context)

@insta485.app.route('/admin/complete-withdrawal/<int:withdrawal_id>', methods=['POST'])
def complete_withdrawal(withdrawal_id):
    """Mark a withdrawal as completed."""
    if 'email' not in flask.session:
        return flask.abort(403)
    connection = insta485.model.get_db()
    user = connection.execute(
        'SELECT is_admin FROM users WHERE email = ?',
        (flask.session['email'],)
    ).fetchone()
    if not user or not user['is_admin']:
        return flask.abort(403)
    
    # Update withdrawal status
    connection.execute(
        "UPDATE withdrawal_requests SET status = 'completed', completed_at = datetime('now') WHERE id = ?",
        (withdrawal_id,)
    )
    connection.commit()
    
    flask.flash(f"✅ Withdrawal #{withdrawal_id} marked as completed!", "success")
    return flask.redirect(flask.url_for('admin_dashboard'))

@insta485.app.route('/admin/create-admin', methods=['POST'])
def create_admin_user():
    """Create an admin user (for development/testing)."""
    if 'email' not in flask.session:
        return flask.abort(403)
    connection = insta485.model.get_db()
    user = connection.execute(
        'SELECT is_admin FROM users WHERE email = ?',
        (flask.session['email'],)
    ).fetchone()
    if not user or not user['is_admin']:
        return flask.abort(403)
    
    email = flask.request.form.get('email')
    password = flask.request.form.get('password', 'admin123')
    firstname = flask.request.form.get('firstname', 'Admin')
    lastname = flask.request.form.get('lastname', 'User')
    
    if not email:
        return flask.abort(400)
    
    # Check if user already exists
    existing = connection.execute(
        "SELECT email FROM users WHERE email = ?", (email,)
    ).fetchone()
    
    if existing:
        return flask.redirect(flask.url_for('admin_dashboard'))
    
    # Create admin user
    try:
        connection.execute(
            "INSERT INTO users (firstname, lastname, email, password, is_admin) VALUES (?, ?, ?, ?, ?)",
            (firstname, lastname, email, hash_password(password), 1)
        )
        connection.commit()
        print(f"[ADMIN] Created admin user: {email}")
    except Exception as e:
        print(f"[ERROR] Failed to create admin user: {e}")
    
    return flask.redirect(flask.url_for('admin_dashboard'))

@insta485.app.route('/admin/resolve-complaint/<int:transaction_id>', methods=['POST'])
def resolve_complaint(transaction_id):
    """Admin resolves a complaint - either refund buyer or pay seller."""
    if 'email' not in flask.session:
        return flask.abort(403)
    
    connection = insta485.model.get_db()
    user = connection.execute(
        'SELECT is_admin FROM users WHERE email = ?',
        (flask.session['email'],)
    ).fetchone()
    if not user or not user['is_admin']:
        return flask.abort(403)
    
    resolution = flask.request.form.get('resolution')  # 'refund_buyer' or 'pay_seller'
    admin_notes = flask.request.form.get('admin_notes', '')
    
    if resolution == 'refund_buyer':
        new_status = 'complaint - refunded buyer'
        # Send refund email to buyer
        try:
            send_complaint_resolution_email(transaction_id, resolution, admin_notes)
        except Exception as e:
            print(f"[EMAIL ERROR] Failed to send resolution email: {e}")
            
    elif resolution == 'pay_seller':
        new_status = 'complaint - paid seller'
        # Send payment confirmation to seller
        try:
            send_complaint_resolution_email(transaction_id, resolution, admin_notes)
        except Exception as e:
            print(f"[EMAIL ERROR] Failed to send resolution email: {e}")
    else:
        flask.flash("Invalid resolution option.", "error")
        return flask.redirect(flask.url_for('admin_dashboard'))
    
    # Update transaction status
    connection.execute(
        "UPDATE transactions SET status = ? WHERE transaction_id = ?",
        (new_status, transaction_id)
    )
    connection.commit()
    
    flask.flash(f"✅ Complaint resolved: {resolution.replace('_', ' ').title()}", "success")
    return flask.redirect(flask.url_for('admin_dashboard'))

def send_complaint_resolution_email(transaction_id, resolution, admin_notes):
    """Send email to both parties about complaint resolution."""
    connection = insta485.model.get_db()
    
    # Get transaction details
    trans_details = connection.execute(
        "SELECT t.buyer_email, t.seller_email, t.price, t.complaint_reason, e.name "
        "FROM transactions t JOIN events e ON t.event_id = e.event_id "
        "WHERE t.transaction_id = ?",
        (transaction_id,)
    ).fetchone()
    
    if not trans_details:
        return
    
    from flask_mail import Message
    from insta485 import mail
    
    if resolution == 'refund_buyer':
        # Email to buyer
        subject = f"✅ Complaint Resolved - Refund Issued (Transaction #{transaction_id})"
        buyer_body = f"""
Your complaint for Transaction #{transaction_id} has been resolved in your favor.

Event: {trans_details['name']}
Original Complaint: {trans_details['complaint_reason']}
Resolution: Full refund issued

Your refund of ${trans_details['price']} will be processed within 3-5 business days.

{admin_notes if admin_notes else ''}

Thank you for using Safe Transaction.
Safe Transaction Team
        """
        
        buyer_msg = Message(subject, recipients=[trans_details['buyer_email']], body=buyer_body)
        mail.send(buyer_msg)
        
        # Email to seller
        seller_subject = f"❌ Complaint Resolved - Buyer Refunded (Transaction #{transaction_id})"
        seller_body = f"""
The complaint for Transaction #{transaction_id} has been resolved in favor of the buyer.

Event: {trans_details['name']}
Complaint: {trans_details['complaint_reason']}
Resolution: Buyer has been refunded ${trans_details['price']}

No payment will be issued to you for this transaction.

{admin_notes if admin_notes else ''}

Safe Transaction Team
        """
        
        seller_msg = Message(seller_subject, recipients=[trans_details['seller_email']], body=seller_body)
        mail.send(seller_msg)
        
    elif resolution == 'pay_seller':
        # Email to seller
        subject = f"✅ Complaint Resolved - Payment Issued (Transaction #{transaction_id})"
        seller_body = f"""
The complaint for Transaction #{transaction_id} has been resolved in your favor.

Event: {trans_details['name']}
Original Complaint: {trans_details['complaint_reason']}
Resolution: Your proof was sufficient

Payment of ${trans_details['price']} will be processed within 3-5 business days.

{admin_notes if admin_notes else ''}

Thank you for using Safe Transaction.
Safe Transaction Team
        """
        
        seller_msg = Message(subject, recipients=[trans_details['seller_email']], body=seller_body)
        mail.send(seller_msg)
        
        # Email to buyer
        buyer_subject = f"❌ Complaint Resolved - Seller Verified (Transaction #{transaction_id})"
        buyer_body = f"""
Your complaint for Transaction #{transaction_id} has been reviewed and resolved in favor of the seller.

Event: {trans_details['name']}
Your Complaint: {trans_details['complaint_reason']}
Resolution: Seller provided sufficient proof of ticket transfer

No refund will be issued for this transaction.

{admin_notes if admin_notes else ''}

Safe Transaction Team
        """
        
        buyer_msg = Message(buyer_subject, recipients=[trans_details['buyer_email']], body=buyer_body)
        mail.send(buyer_msg)
    
    print(f"[EMAIL] Sent complaint resolution emails for transaction {transaction_id}")
