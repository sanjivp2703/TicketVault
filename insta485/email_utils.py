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

def send_accept_confirmation_email(buyer_email, event_name, price, seller_email):
    subject = f"Your payment for {event_name} was successful!"
    body = (
        f"Hello,\n\nYour payment for '{event_name}' was successful. "
        f"Price: ${price}\nSeller: {seller_email}\n\n"
        "The seller will transfer your ticket soon.\n\nBest,\nSafe-Transaction Team"
    )
    html = f'''
        <p>Hello,</p>
        <p>Your payment for <b>{event_name}</b> was successful.<br>
        Price: <b>${price}</b><br>
        Seller: <b>{seller_email}</b></p>
        <p>The seller will transfer your ticket soon.</p>
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
