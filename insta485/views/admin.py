import flask
import insta485
from insta485.views.balance import add_earnings, deduct_withdrawal

@insta485.app.route('/admin', methods=['GET'], endpoint='admin_dashboard')
def admin_dashboard():
    """Admin dashboard: show all complaints using admin.html with admin context."""
    if 'email' not in flask.session:
        return flask.abort(403)
    connection = insta485.model.get_db()
    user = connection.execute(
        'SELECT is_admin FROM users WHERE email = ?',
        (flask.session['email'],)
    ).fetchone()
    if not user or not user['is_admin']:
        return flask.abort(403)
    # Fetch all complaints (transactions with status 'complaint_filed')
    complaints = connection.execute(
        "SELECT t.*, e.name AS ticket_description, e.location, e.event_datetime FROM transactions t JOIN events e ON t.event_id = e.event_id WHERE t.status = 'complaint_filed' ORDER BY t.transaction_id DESC"
    ).fetchall()
    context = {
        'is_admin': True,
        'logemail': flask.session['email'],
        'complaints': complaints,
        'user_type': 'admin',
        'transactions': [],  # not used for admin
    }
    return flask.render_template('admin.html', **context)

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
