from flask_mail import Message
from flask import current_app

def send_email(to_email, subject, body, html=None):
    """
    Send an email using Flask-Mail with Gmail SMTP.
    Uses app config for credentials.
    Supports plain text and optional HTML body.
    Returns True if successful, False otherwise.
    """
    from insta485 import mail  # Adjust import if mail is created elsewhere
    try:
        msg = Message(subject, recipients=[to_email], body=body)
        if html:
            msg.html = html
        mail.send(msg)
        return True
    except Exception as e:
        current_app.logger.error(f"Failed to send email: {e}")
        return False

def send_accept_confirmation_email(buyer_email, event_name, price, seller_email, transaction_id=None):
    subject = f"Your payment for {event_name} was successful!"
    body = (
        f"Hello,\n\nYour payment for '{event_name}' was successful. "
        f"Price: ${price}\nSeller: {seller_email}\n\n"
        "The seller will transfer your ticket soon.\n\nBest,\nSafe-Transaction Team"
    )
    # Add a confirm and cancel button if transaction_id is provided
    confirm_btn = cancel_btn = ""
    if transaction_id:
        # Use url_for to generate absolute URLs if possible, else set YOUR_DOMAIN to your deployed domain
        DOMAIN = "http://localhost:8000"  # CHANGE THIS to your deployed domain!
        confirm_url = f"{DOMAIN}/ticket_status/{transaction_id}?action=confirm"
        cancel_url = f"{DOMAIN}/cancel?transaction_id={transaction_id}&user_type=buyer"
        confirm_btn = f'<a href="{confirm_url}" style="background:#28a745;color:white;padding:10px 18px;border:none;border-radius:4px;text-decoration:none;display:inline-block;font-family:sans-serif;font-size:16px;font-weight:bold;">I Received My Ticket</a>'
        cancel_btn = f'<a href="{cancel_url}" style="background:#dc3545;color:white;padding:10px 18px;border:none;border-radius:4px;text-decoration:none;margin-left:10px;display:inline-block;font-family:sans-serif;font-size:16px;font-weight:bold;">Cancel Transaction</a>'
    html = f'''
        <p>Hello,</p>
        <p>Your payment for <b>{event_name}</b> was successful.<br>
        Price: <b>${price}</b><br>
        Seller: <b>{seller_email}</b></p>
        <p>The seller will transfer your ticket soon.</p>
        <div style="margin-top:28px;">{confirm_btn} {cancel_btn}</div>
        <p style="margin-top:24px;">Best,<br>Safe-Transaction Team</p>
    '''
    return send_email(buyer_email, subject, body, html=html)

def send_reject_confirmation_email(buyer_email, event_name, seller_email):
    subject = f"You have rejected the offer for {event_name}"
    body = (
        f"Hello,\n\nYou have rejected the ticket offer for '{event_name}'. "
        f"Seller: {seller_email}\n\nIf this was a mistake, please contact the seller directly.\n\nBest,\nSafe-Transaction Team"
    )
    html = f'''
        <p>Hello,</p>
        <p>You have rejected the ticket offer for <b>{event_name}</b>.<br>
        Seller: <b>{seller_email}</b></p>
        <p>If this was a mistake, please contact the seller directly.</p>
        <p style="margin-top:24px;">Best,<br>Safe-Transaction Team</p>
    '''
    return send_email(buyer_email, subject, body, html=html)

def send_ticket_received_email(buyer_email, event_name, price, seller_email, event_datetime, complaint_deadline):
    subject = f"Enjoy {event_name}! Your ticket is ready."
    body = (
        f"Hello,\n\nYou have confirmed receipt of your ticket for '{event_name}'. "
        f"Price: ${price}\nSeller: {seller_email}\n\n"
        f"Enjoy the event! If you have any issues, you have until {complaint_deadline} to file a complaint.\n\nBest,\nSafe-Transaction Team"
    )
    html = f'''
        <p>Hello,</p>
        <p>You have confirmed receipt of your ticket for <b>{event_name}</b>.<br>
        Price: <b>${price}</b><br>
        Seller: <b>{seller_email}</b></p>
        <p><b>Enjoy the event!</b></p>
        <p style="margin-top:18px;">If you have any issues, you have until <b>{complaint_deadline}</b> to file a complaint.</p>
        <p style="margin-top:24px;">Best,<br>Safe-Transaction Team</p>
    '''
    return send_email(buyer_email, subject, body, html=html)
