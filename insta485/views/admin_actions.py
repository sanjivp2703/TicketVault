"""
Admin action routes for Safe-Transaction.
"""

import flask
import insta485
import requests
from insta485.views.balance import add_earnings
import logging

logger = logging.getLogger(__name__)


def send_mailgun_email(to_email, subject, html_body, text_body=None):
    """Send email using Mailgun HTTP API (more reliable than SMTP)."""
    try:
        api_key = insta485.app.config["MAILGUN_API_KEY"]
        domain = insta485.app.config["MAILGUN_DOMAIN"]

        response = requests.post(
            f"https://api.mailgun.net/v3/{domain}/messages",
            auth=("api", api_key),
            data={
                "from": f"Safe Transaction <noreply@{domain}>",
                "to": to_email,
                "subject": subject,
                "html": html_body,
                "text": text_body or "Please view this email in HTML format.",
            },
        )

        if response.status_code == 200:
            logger.info(f"✅ Email sent successfully to {to_email}")
            return True
        else:
            logger.error(f"❌ Email failed: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        logger.error(f"❌ Email error: {e}")
        return False


@insta485.app.route("/admin/verify-ticket/<int:transaction_id>", methods=["POST"])
def admin_verify_ticket(transaction_id):
    """Admin verifies ticket and sends payment email to buyer."""
    if "email" not in flask.session:
        return flask.abort(403)

    connection = insta485.model.get_db()
    user = connection.execute(
        "SELECT is_admin FROM users WHERE email = ?", (flask.session["email"],)
    ).fetchone()
    if not user or not user["is_admin"]:
        return flask.abort(403)

    # Get transaction details
    transaction = connection.execute(
        """SELECT t.*, e.name as event_name, e.location, e.event_datetime 
           FROM transactions t 
           JOIN events e ON t.event_id = e.event_id 
           WHERE t.transaction_id = ?""",
        (transaction_id,),
    ).fetchone()

    if not transaction:
        flask.flash("Transaction not found", "error")
        return flask.redirect(flask.url_for("admin_dashboard"))

    # Update transaction status to waiting_for_payment
    connection.execute(
        "UPDATE transactions SET status = ? WHERE transaction_id = ?",
        ("waiting_for_payment", transaction_id),
    )

    # Send payment email to buyer
    try:
        subject = f"🎫 Ticket Verified - Complete Your Payment (Transaction #{transaction_id})"

        # Create direct Stripe checkout URL
        payment_url = (
            f"https://safetransaction.app/api/transactions/{transaction_id}/pay"
        )

        html_body = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #4caf50;">✅ Great News! Your Ticket is Verified</h2>
            
            <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h3>Event Details:</h3>
                <p><strong>Event:</strong> {transaction["event_name"]}</p>
                <p><strong>Location:</strong> {transaction["location"]}</p>
                <p><strong>Date:</strong> {transaction["event_datetime"]}</p>
                <p><strong>Price:</strong> ${transaction["price"]}</p>
            </div>
            
            <div style="background: #e8f5e8; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h3>✅ Ticket Status: VERIFIED</h3>
                <p>We've received and verified the ticket from the seller. The ticket matches your requested event and seating details.</p>
            </div>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{payment_url}" style="background: #4caf50; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-size: 18px; font-weight: bold;">
                    💳 Complete Payment - ${transaction["price"]}
                </a>
            </div>
            
            <div style="background: #fff3cd; padding: 15px; border-radius: 8px; margin: 20px 0;">
                <h4>What happens next:</h4>
                <ol>
                    <li>Click the payment button above</li>
                    <li>Complete your secure payment via Stripe</li>
                    <li>We'll immediately forward your ticket</li>
                    <li>You'll receive your ticket within minutes!</li>
                </ol>
            </div>
            
            <p style="color: #666; font-size: 14px;">
                Questions? Contact us at <a href="mailto:safetransactiontix@gmail.com">safetransactiontix@gmail.com</a>
            </p>
        </div>
        """

        text_body = f"""
        Great News! Your Ticket is Verified
        
        Event: {transaction["event_name"]}
        Location: {transaction["location"]}
        Date: {transaction["event_datetime"]}
        Price: ${transaction["price"]}
        
        ✅ Ticket Status: VERIFIED
        We've received and verified the ticket from the seller.
        
        Complete your payment: {payment_url}
        
        Questions? Contact us at safetransactiontix@gmail.com
        """

        # Use Mailgun HTTP API instead of SMTP
        email_sent = send_mailgun_email(
            to_email=transaction["buyer_email"],
            subject=subject,
            html_body=html_body,
            text_body=text_body,
        )

        if email_sent:
            flask.flash(
                f"✅ Ticket verified and payment email sent to {transaction['buyer_email']}",
                "success",
            )
        else:
            flask.flash(
                f"✅ Ticket verified but email failed to send to {transaction['buyer_email']}",
                "warning",
            )

    except Exception as e:
        flask.flash(f"Ticket verified but email failed: {str(e)}", "warning")

    return flask.redirect(flask.url_for("admin_dashboard"))


@insta485.app.route("/admin/accept-ticket/<int:transaction_id>", methods=["POST"])
def admin_accept_ticket(transaction_id):
    """Admin accepts ticket and sends payment email to buyer."""
    if "email" not in flask.session:
        return flask.abort(403)

    connection = insta485.model.get_db()
    user = connection.execute(
        "SELECT is_admin FROM users WHERE email = ?", (flask.session["email"],)
    ).fetchone()
    if not user or not user["is_admin"]:
        return flask.abort(403)

    # Get transaction details
    transaction = connection.execute(
        """SELECT t.*, e.name as event_name, e.location, e.event_datetime 
           FROM transactions t 
           JOIN events e ON t.event_id = e.event_id 
           WHERE t.transaction_id = ?""",
        (transaction_id,),
    ).fetchone()

    if not transaction:
        flask.flash("Transaction not found", "error")
        return flask.redirect(flask.url_for("admin_dashboard"))

    # Check if transaction is in correct status
    if transaction["status"] != "waiting_for_verification":
        flask.flash(
            f"Cannot accept ticket - transaction is in status: {transaction['status']}",
            "error",
        )
        return flask.redirect(flask.url_for("admin_dashboard"))

    # Update transaction status to waiting_for_payment
    connection.execute(
        "UPDATE transactions SET status = ? WHERE transaction_id = ?",
        ("waiting_for_payment", transaction_id),
    )
    connection.commit()

    # Send payment email to buyer
    try:
        subject = f"🎫 Ticket Verified - Complete Your Payment (Transaction #{transaction_id})"

        # Create direct Stripe checkout URL
        payment_url = (
            f"https://safetransaction.app/api/transactions/{transaction_id}/pay"
        )

        html_body = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #4caf50;">✅ Great News! Your Ticket is Verified</h2>
            
            <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h3>Event Details:</h3>
                <p><strong>Event:</strong> {transaction["event_name"]}</p>
                <p><strong>Location:</strong> {transaction["location"]}</p>
                <p><strong>Date:</strong> {transaction["event_datetime"]}</p>
                <p><strong>Price:</strong> ${transaction["price"]}</p>
            </div>
            
            <div style="background: #e8f5e8; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h3>✅ Ticket Status: VERIFIED</h3>
                <p>We've received and verified the ticket from the seller. The ticket matches your requested event and seating details.</p>
            </div>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{payment_url}" style="background: #4caf50; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-size: 18px; font-weight: bold;">
                    💳 Complete Payment - ${transaction["price"]}
                </a>
            </div>
            
            <div style="background: #fff3cd; padding: 15px; border-radius: 8px; margin: 20px 0;">
                <h4>What happens next:</h4>
                <ol>
                    <li>Click the payment button above</li>
                    <li>Complete your secure payment via Stripe</li>
                    <li>We'll immediately forward your ticket</li>
                    <li>You'll receive your ticket within minutes!</li>
                </ol>
            </div>
            
            <p style="color: #666; font-size: 14px;">
                Questions? Contact us at <a href="mailto:safetransactiontix@gmail.com">safetransactiontix@gmail.com</a>
            </p>
        </div>
        """

        text_body = f"""
        Great News! Your Ticket is Verified
        
        Event: {transaction["event_name"]}
        Location: {transaction["location"]}
        Date: {transaction["event_datetime"]}
        Price: ${transaction["price"]}
        
        ✅ Ticket Status: VERIFIED
        We've received and verified the ticket from the seller.
        
        Complete your payment: {payment_url}
        
        Questions? Contact us at safetransactiontix@gmail.com
        """

        # Use Mailgun HTTP API
        email_sent = send_mailgun_email(
            to_email=transaction["buyer_email"],
            subject=subject,
            html_body=html_body,
            text_body=text_body,
        )

        if email_sent:
            flask.flash(
                f"✅ Ticket accepted and payment email sent to {transaction['buyer_email']}",
                "success",
            )
        else:
            flask.flash(
                f"✅ Ticket accepted but email failed to send to {transaction['buyer_email']}",
                "warning",
            )

    except Exception as e:
        flask.flash(f"Ticket accepted but email failed: {str(e)}", "warning")

    return flask.redirect(flask.url_for("admin_dashboard"))


@insta485.app.route("/admin/reject-ticket/<int:transaction_id>", methods=["POST"])
def admin_reject_ticket(transaction_id):
    """Admin rejects ticket and sends reason to seller."""
    if "email" not in flask.session:
        return flask.abort(403)

    connection = insta485.model.get_db()
    user = connection.execute(
        "SELECT is_admin FROM users WHERE email = ?", (flask.session["email"],)
    ).fetchone()
    if not user or not user["is_admin"]:
        return flask.abort(403)

    # Get rejection reason from form
    rejection_reason = flask.request.form.get("rejection_reason", "No reason provided")

    # Get transaction details
    transaction = connection.execute(
        """SELECT t.*, e.name as event_name, e.location, e.event_datetime 
           FROM transactions t 
           JOIN events e ON t.event_id = e.event_id 
           WHERE t.transaction_id = ?""",
        (transaction_id,),
    ).fetchone()

    if not transaction:
        flask.flash("Transaction not found", "error")
        return flask.redirect(flask.url_for("admin_dashboard"))

    # Check if transaction is in correct status
    if transaction["status"] != "waiting_for_verification":
        flask.flash(
            f"Cannot reject ticket - transaction is in status: {transaction['status']}",
            "error",
        )
        return flask.redirect(flask.url_for("admin_dashboard"))

    # Update transaction status back to pending_ticket_submission
    connection.execute(
        "UPDATE transactions SET status = ?, ticket_email_received = 0 WHERE transaction_id = ?",
        ("pending_ticket_submission", transaction_id),
    )
    connection.commit()

    # Send rejection email to seller
    try:
        subject = (
            f"❌ Ticket Rejected - Please Resubmit (Transaction #{transaction_id})"
        )

        html_body = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #ef4444;">❌ Ticket Submission Rejected</h2>
            
            <div style="background: #fee; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #ef4444;">
                <h3>Rejection Reason:</h3>
                <p style="font-size: 16px;"><strong>{rejection_reason}</strong></p>
            </div>
            
            <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h3>Event Details:</h3>
                <p><strong>Event:</strong> {transaction["event_name"]}</p>
                <p><strong>Location:</strong> {transaction["location"]}</p>
                <p><strong>Date:</strong> {transaction["event_datetime"]}</p>
                <p><strong>Price:</strong> ${transaction["price"]}</p>
                <p><strong>Buyer:</strong> {transaction["buyer_email"]}</p>
            </div>
            
            <div style="background: #fff3cd; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h3>What To Do Next:</h3>
                <ol>
                    <li>Review the rejection reason above</li>
                    <li>Make the necessary corrections to your ticket</li>
                    <li>Click "I've Sent the Ticket" button again to resubmit</li>
                    <li>We'll review it as soon as possible</li>
                </ol>
            </div>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="https://safetransaction.app/" style="background: #3b82f6; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-size: 16px; font-weight: bold;">
                    Go to Safe Transaction
                </a>
            </div>
            
            <p style="color: #666; font-size: 14px;">
                Questions? Contact us at <a href="mailto:safetransactiontix@gmail.com">safetransactiontix@gmail.com</a>
            </p>
        </div>
        """

        text_body = f"""
        Ticket Submission Rejected
        
        Rejection Reason: {rejection_reason}
        
        Event: {transaction["event_name"]}
        Location: {transaction["location"]}
        Date: {transaction["event_datetime"]}
        Price: ${transaction["price"]}
        Buyer: {transaction["buyer_email"]}
        
        What To Do Next:
        1. Review the rejection reason above
        2. Make the necessary corrections to your ticket
        3. Click "I've Sent the Ticket" button again to resubmit
        4. We'll review it as soon as possible
        
        Go to Safe Transaction: https://safetransaction.app/
        
        Questions? Contact us at safetransactiontix@gmail.com
        """

        # Use Mailgun HTTP API
        email_sent = send_mailgun_email(
            to_email=transaction["seller_email"],
            subject=subject,
            html_body=html_body,
            text_body=text_body,
        )

        if email_sent:
            flask.flash(
                f"❌ Ticket rejected. Reason sent to seller: {rejection_reason}",
                "success",
            )
        else:
            flask.flash(
                f"❌ Ticket rejected but email failed to send to {transaction['seller_email']}",
                "warning",
            )

    except Exception as e:
        flask.flash(f"Ticket rejected but email failed: {str(e)}", "warning")

    return flask.redirect(flask.url_for("admin_dashboard"))


@insta485.app.route("/admin/release-funds/<int:transaction_id>", methods=["POST"])
def admin_release_funds(transaction_id):
    """Admin releases funds to seller after ticket is confirmed sent."""
    if "email" not in flask.session:
        return flask.abort(403)

    connection = insta485.model.get_db()
    user = connection.execute(
        "SELECT is_admin FROM users WHERE email = ?", (flask.session["email"],)
    ).fetchone()
    if not user or not user["is_admin"]:
        return flask.abort(403)

    # Get transaction details
    transaction = connection.execute(
        "SELECT * FROM transactions WHERE transaction_id = ?", (transaction_id,)
    ).fetchone()

    if not transaction:
        flask.flash("Transaction not found", "error")
        return flask.redirect(flask.url_for("admin_dashboard"))

    try:
        # Update transaction to completed and release funds
        connection.execute(
            """UPDATE transactions 
               SET status = 'completed', 
                   funds_released = 1,
                   funds_released_time = CURRENT_TIMESTAMP
               WHERE transaction_id = ?""",
            (transaction_id,),
        )

        # Add earnings to seller (you can implement this)
        # add_earnings(transaction['seller_email'], transaction['price'])

        flask.flash(
            f"✅ Funds released to seller for transaction #{transaction_id}", "success"
        )

    except Exception as e:
        flask.flash(f"Error releasing funds: {str(e)}", "error")

    return flask.redirect(flask.url_for("admin_dashboard"))


@insta485.app.route("/admin/refund-buyer/<int:transaction_id>", methods=["POST"])
def admin_refund_buyer(transaction_id):
    """Admin refunds buyer for a transaction."""
    if "email" not in flask.session:
        return flask.abort(403)

    connection = insta485.model.get_db()
    user = connection.execute(
        "SELECT is_admin FROM users WHERE email = ?", (flask.session["email"],)
    ).fetchone()
    if not user or not user["is_admin"]:
        return flask.abort(403)

    # Get transaction details
    transaction = connection.execute(
        "SELECT * FROM transactions WHERE transaction_id = ?", (transaction_id,)
    ).fetchone()

    if not transaction:
        flask.flash("Transaction not found", "error")
        return flask.redirect(flask.url_for("admin_dashboard"))

    # Update transaction status
    connection.execute(
        "UPDATE transactions SET status = 'complaint - refunded buyer' WHERE transaction_id = ?",
        (transaction_id,),
    )

    # Process refund to buyer
    # Note: In a real system, this would integrate with a payment processor
    # Here we're just updating the status and recording the transaction

    # Record the refund in monetary_transactions
    try:
        connection.execute(
            "INSERT INTO monetary_transactions "
            "(sender, recipient, transaction_id_ref, amount, transaction_type) "
            "VALUES (?, ?, ?, ?, ?)",
            (
                "sanjivp2703@gmail.com",
                transaction["buyer_email"],
                transaction_id,
                transaction["price"],
                "refund",
            ),
        )
        connection.commit()
        flask.flash(
            f"Buyer has been refunded for transaction #{transaction_id}", "success"
        )
    except Exception as e:
        connection.rollback()
        flask.flash(f"Error processing refund: {str(e)}", "error")
    return flask.redirect(flask.url_for("admin_dashboard"))


@insta485.app.route("/admin/pay-seller/<int:transaction_id>", methods=["POST"])
def admin_pay_seller(transaction_id):
    """Admin pays seller for a transaction."""
    if "email" not in flask.session:
        return flask.abort(403)

    connection = insta485.model.get_db()
    user = connection.execute(
        "SELECT is_admin FROM users WHERE email = ?", (flask.session["email"],)
    ).fetchone()
    if not user or not user["is_admin"]:
        return flask.abort(403)

    # Get transaction details
    transaction = connection.execute(
        "SELECT * FROM transactions WHERE transaction_id = ?", (transaction_id,)
    ).fetchone()

    if not transaction:
        flask.flash("Transaction not found", "error")
        return flask.redirect(flask.url_for("admin_dashboard"))

    # Update transaction status
    connection.execute(
        "UPDATE transactions SET status = 'complaint - paid seller' WHERE transaction_id = ?",
        (transaction_id,),
    )

    # Add earnings to seller's balance
    try:
        add_earnings(
            transaction["seller_email"],
            transaction["price"],
            transaction_id,
            f"Admin payment for transaction #{transaction_id}",
        )
        flask.flash(
            f"Seller has been paid for transaction #{transaction_id}", "success"
        )
    except Exception as e:
        flask.flash(f"Error processing payment: {str(e)}", "error")

    return flask.redirect(flask.url_for("admin_dashboard"))


@insta485.app.route("/admin/declare-ticket-sent/<int:transaction_id>", methods=["POST"])
def admin_declare_ticket_sent(transaction_id):
    """Admin declares that ticket was sent for a transaction."""
    if "email" not in flask.session:
        return flask.abort(403)

    connection = insta485.model.get_db()
    user = connection.execute(
        "SELECT is_admin FROM users WHERE email = ?", (flask.session["email"],)
    ).fetchone()
    if not user or not user["is_admin"]:
        return flask.abort(403)

    # Get transaction details with event information
    transaction = connection.execute(
        """SELECT t.*, e.name as event_name, e.location, e.event_datetime
           FROM transactions t 
           JOIN events e ON t.event_id = e.event_id
           WHERE t.transaction_id = ?""",
        (transaction_id,),
    ).fetchone()

    if not transaction:
        flask.flash("Transaction not found", "error")
        return flask.redirect(flask.url_for("admin_dashboard"))

    # Check if transaction is in a valid state for ticket declaration (payment must be received)
    is_payment_received = transaction.get("payment_received") == 1
    is_valid_status = transaction["status"] in ["waiting_for_payment_processing"]

    if not (is_payment_received or is_valid_status):
        flask.flash(
            f"Cannot declare ticket sent - payment not yet received for transaction #{transaction_id}",
            "error",
        )
        return flask.redirect(flask.url_for("admin_dashboard"))

    try:
        # Update transaction status to ticket_sent
        connection.execute(
            """UPDATE transactions 
               SET status = 'ticket_sent', 
                   ticket_forwarded = 1,
                   ticket_forwarded_time = CURRENT_TIMESTAMP
               WHERE transaction_id = ?""",
            (transaction_id,),
        )

        # Add earnings to seller's balance when ticket is sent
        add_earnings(
            transaction["seller_email"],
            transaction["price"],
            transaction_id,
            f"Payment for {transaction['event_name']} - Transaction #{transaction_id}",
        )

        # Send notification emails
        send_ticket_sent_notifications(transaction_id, transaction)

        connection.commit()
        flask.flash(
            f"✅ Ticket marked as sent for transaction #{transaction_id}. Seller paid ${transaction['price']:.2f}. Notification emails sent.",
            "success",
        )

    except Exception as e:
        connection.rollback()
        flask.flash(f"Error updating transaction: {str(e)}", "error")
        logger.error(f"Error in admin_declare_ticket_sent: {e}")

    return flask.redirect(flask.url_for("admin_dashboard"))


def send_ticket_sent_notifications(transaction_id, transaction):
    """Send notification emails to buyer and seller when admin declares ticket sent."""
    try:
        from flask_mail import Message

        # Email to buyer - Professional HTML template
        buyer_subject = (
            f"🎫 Your Tickets Have Been Sent! - Transaction #{transaction_id}"
        )

        # Create professional HTML email
        buyer_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #28a745, #20c997); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: white; padding: 30px; border: 1px solid #ddd; border-top: none; }}
                .success-banner {{ background: #d4edda; padding: 20px; border-radius: 8px; border-left: 4px solid #28a745; margin: 20px 0; }}
                .event-details {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; border: 1px solid #e9ecef; }}
                .detail-row {{ display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #e9ecef; }}
                .detail-row:last-child {{ border-bottom: none; }}
                .detail-label {{ font-weight: 600; color: #495057; }}
                .detail-value {{ color: #28a745; font-weight: 600; }}
                .instructions {{ background: #e7f3ff; padding: 20px; border-radius: 8px; border-left: 4px solid #007bff; margin: 20px 0; }}
                .warning {{ background: #fff3cd; padding: 20px; border-radius: 8px; border-left: 4px solid #ffc107; margin: 20px 0; }}
                .footer {{ text-align: center; padding: 20px; color: #6c757d; font-size: 14px; }}
                .btn {{ display: inline-block; background: #007bff; color: white; padding: 12px 25px; text-decoration: none; border-radius: 8px; font-weight: bold; margin: 10px 0; }}
                ul {{ padding-left: 20px; }}
                li {{ margin-bottom: 8px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🛡️ Safe Transaction</h1>
                    <p>Your Ticket Delivery Confirmation</p>
                </div>
                <div class="content">
                    <div class="success-banner">
                        <h2 style="margin: 0 0 10px 0; color: #155724;">🎉 Great News! Your Tickets Have Been Sent!</h2>
                        <p style="margin: 0; color: #155724;">Your secure ticket transfer has been initiated and should arrive in your email shortly.</p>
                    </div>
                    
                    <div class="event-details">
                        <h3 style="margin-top: 0; color: #333;">📋 Transaction Summary</h3>
                        <div class="detail-row">
                            <span class="detail-label">Transaction ID:</span>
                            <span class="detail-value">ST-{transaction_id}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Event:</span>
                            <span class="detail-value">{transaction["event_name"]}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Venue:</span>
                            <span class="detail-value">{transaction["location"]}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Amount Paid:</span>
                            <span class="detail-value">${transaction["price"]:.2f}</span>
                        </div>
                    </div>
                    
                    <div class="instructions">
                        <h3 style="margin-top: 0; color: #0056b3;">📧 Where to Check for Your Tickets</h3>
                        <p>Your tickets should arrive within the next <strong>30 minutes</strong>. Please check:</p>
                        <ul>
                            <li><strong>Your main email inbox</strong> - Look for the seller's email</li>
                            <li><strong>Spam/Junk folder</strong> - Sometimes emails get filtered</li>
                            <li><strong>All email addresses</strong> you may have provided</li>
                            <li><strong>Email from seller:</strong> {transaction["seller_email"]}</li>
                        </ul>
                    </div>
                    
                    <div class="warning">
                        <h3 style="margin-top: 0; color: #856404;">⚠️ Important Reminders</h3>
                        <ul style="margin: 0;">
                            <li><strong>Contact us immediately</strong> if you don't receive tickets within 1 hour</li>
                            <li><strong>Save this email</strong> as proof of purchase and payment</li>
                            <li><strong>24-hour protection:</strong> You have until 24 hours after the event to report any issues</li>
                            <li><strong>Enjoy your event!</strong> You're protected by Safe Transaction's guarantee</li>
                        </ul>
                    </div>
                    
                    <div style="text-align: center; margin: 25px 0;">
                        <p><strong>Need help or have questions?</strong></p>
                        <a href="mailto:safetransactiontix@gmail.com?subject=Support Request - Transaction #{transaction_id}" class="btn">
                            📞 Contact Support
                        </a>
                    </div>
                    
                    <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center;">
                        <h4 style="margin-top: 0; color: #28a745;">✅ You're Protected!</h4>
                        <p style="margin: 0; color: #6c757d;">This transaction was processed through Safe Transaction's secure platform. Your payment is protected and your tickets are guaranteed.</p>
                    </div>
                </div>
                <div class="footer">
                    <p>Thank you for choosing Safe Transaction - The secure way to buy tickets!</p>
                    <p style="margin: 5px 0;"><strong>Safe Transaction LLC</strong> | <a href="mailto:safetransactiontix@gmail.com" style="color: #007bff;">safetransactiontix@gmail.com</a></p>
                </div>
            </div>
        </body>
        </html>
        """

        # Create plain text version
        buyer_text = f"""
🎫 YOUR TICKETS HAVE BEEN SENT! - Transaction #{transaction_id}

Great news! Your secure ticket transfer has been initiated.

📋 TRANSACTION SUMMARY:
• Transaction ID: ST-{transaction_id}
• Event: {transaction["event_name"]}
• Venue: {transaction["location"]}
• Amount Paid: ${transaction["price"]:.2f}

📧 WHERE TO CHECK FOR YOUR TICKETS:
Your tickets should arrive within 30 minutes. Please check:
• Your main email inbox
• Spam/Junk folder  
• All email addresses you provided
• Email from seller: {transaction["seller_email"]}

⚠️ IMPORTANT REMINDERS:
• Contact us immediately if you don't receive tickets within 1 hour
• Save this email as proof of purchase
• 24-hour protection: You can report issues until 24 hours after the event
• Enjoy your event! You're protected by Safe Transaction's guarantee

Need help? Contact us at safetransactiontix@gmail.com

✅ YOU'RE PROTECTED!
This transaction was processed through Safe Transaction's secure platform.

Thank you for choosing Safe Transaction - The secure way to buy tickets!
Safe Transaction LLC | safetransactiontix@gmail.com
        """

        buyer_msg = Message(
            subject=buyer_subject,
            recipients=[transaction["buyer_email"]],
            html=buyer_html,
            body=buyer_text,
        )
        insta485.mail.send(buyer_msg)

        # Email to seller
        seller_subject = f"✅ Ticket Delivery Confirmed - Transaction #{transaction_id}"
        seller_body = f"""
Your ticket delivery has been confirmed by our admin team.

📋 Transaction Details:
• Transaction ID: ST-{transaction_id}
• Event: {transaction["event_name"]}
• Buyer: {transaction["buyer_email"]}
• Amount: ${transaction["price"]:.2f}

✅ Status Update:
Your tickets have been marked as successfully sent to the buyer. This transaction is now complete.

💰 Payment:
Your earnings will be processed and added to your account balance shortly.

Thank you for using Safe Transaction!

Best regards,
The Safe Transaction Team
        """

        seller_msg = Message(
            subject=seller_subject,
            recipients=[transaction["seller_email"]],
            body=seller_body,
        )
        insta485.mail.send(seller_msg)

        logger.info(
            f"📧 Sent ticket delivery notifications for transaction {transaction_id}"
        )

    except Exception as e:
        logger.error(f"❌ Failed to send ticket delivery emails: {e}")
        # Don't raise the exception since the main transaction update should still succeed
