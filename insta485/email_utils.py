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
    subject = f"🎉 Payment confirmed for {event_name}!"
    body = (
        f"Hello,\n\nYour payment for '{event_name}' was successful. "
        f"Price: ${price}\nSeller: {seller_email}\n\n"
        "We're now processing your ticket.\n\nBest,\nSafe-Transaction Team"
    )
    
    # Generate action URLs
    DOMAIN = "http://localhost:8000"
    ticket_status_url = f"{DOMAIN}/ticket/{transaction_id}" if transaction_id else "#"
    
    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
            
            body {{
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: #f8fafb;
                margin: 0;
                padding: 40px 20px;
                color: #1f2937;
                line-height: 1.6;
            }}
            
            .email-container {{
                max-width: 600px;
                margin: 0 auto;
                background: #ffffff;
                border-radius: 20px;
                overflow: hidden;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
                border: 1px solid #e5e7eb;
            }}
            
            .header {{
                background: linear-gradient(135deg, #3b82f6 0%, #059669 100%);
                padding: 48px 40px;
                text-align: center;
                color: white;
            }}
            
            .logo {{
                font-size: 32px;
                font-weight: 700;
                color: white;
                margin-bottom: 8px;
            }}
            
            .tagline {{
                font-size: 16px;
                color: white;
                margin: 16px 0 0 0;
                opacity: 0.9;
            }}
            
            .content {{
                padding: 48px 40px;
            }}
            
            .success-message {{
                text-align: center;
                margin-bottom: 40px;
            }}
            
            .success-icon {{
                font-size: 48px;
                margin-bottom: 20px;
            }}
            
            .success-title {{
                font-size: 24px;
                font-weight: 700;
                color: #059669;
                margin-bottom: 12px;
            }}
            
            .success-subtitle {{
                font-size: 18px;
                color: #6b7280;
                font-weight: 500;
            }}
            
            .transaction-card {{
                background: #f8fafb;
                border-radius: 16px;
                padding: 32px;
                margin: 32px 0;
                border: 1px solid #e5e7eb;
            }}
            
            .transaction-details {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 24px;
                margin-bottom: 0;
            }}
            
            .detail-item {{
                background: #ffffff;
                border-radius: 12px;
                padding: 20px;
                border: 1px solid #f1f3f4;
            }}
            
            .detail-label {{
                font-size: 11px;
                color: #9ca3af;
                text-transform: uppercase;
                letter-spacing: 0.8px;
                font-weight: 600;
                margin-bottom: 8px;
                display: block;
            }}
            
            .detail-value {{
                font-size: 16px;
                color: #1f2937;
                font-weight: 700;
                line-height: 1.4;
                margin: 0;
            }}
            
            .detail-value.price {{
                font-size: 20px;
                color: #059669;
                font-weight: 800;
            }}
            
            .next-steps {{
                background: #dcfce7;
                border-radius: 16px;
                padding: 32px;
                margin: 32px 0;
            }}
            
            .next-steps-title {{
                font-size: 18px;
                font-weight: 700;
                color: #059669;
                margin-bottom: 20px;
                display: flex;
                align-items: center;
            }}
            
            .step {{
                display: flex;
                align-items: flex-start;
                margin-bottom: 16px;
            }}
            
            .step:last-child {{
                margin-bottom: 0;
            }}
            
            .step-icon {{
                color: #059669;
                margin-right: 12px;
                margin-top: 2px;
                font-size: 16px;
            }}
            
            .step-text {{
                color: #065f46;
                font-size: 15px;
                line-height: 1.5;
                font-weight: 500;
            }}
            
            .cta-section {{
                text-align: center;
                margin: 40px 0;
            }}
            
            .cta-button {{
                display: inline-block;
                background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
                color: #ffffff !important;
                padding: 16px 32px;
                text-decoration: none;
                border-radius: 12px;
                font-weight: 700;
                font-size: 16px;
                transition: all 0.3s ease;
                box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
            }}
            
            .footer {{
                background: #f8fafb;
                padding: 32px 40px;
                text-align: center;
                border-top: 1px solid #e5e7eb;
            }}
            
            .footer-text {{
                color: #6b7280;
                font-size: 14px;
                margin-bottom: 8px;
            }}
            
            .footer-link {{
                color: #3b82f6;
                text-decoration: none;
                font-weight: 500;
            }}
            
            @media (max-width: 640px) {{
                .email-container {{
                    margin: 0;
                    border-radius: 0;
                }}
                
                .header, .content, .footer {{
                    padding: 32px 24px;
                }}
                
                .transaction-details {{
                    grid-template-columns: 1fr;
                    gap: 16px;
                }}
                
                .detail-item {{
                    padding: 16px;
                }}
                
                .next-steps {{
                    padding: 24px;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <div class="header">
                <div class="logo">Safe Transaction</div>
                <div class="tagline">Secure Ticket Protection</div>
            </div>
            
            <div class="content">
                <div class="success-message">
                    <div class="success-icon">🎉</div>
                    <h2 class="success-title">Payment confirmed!</h2>
                    <p class="success-subtitle">Thanks! We've received your payment and are now processing your secure transaction.</p>
                </div>
                
                <div class="transaction-card">
                    <div class="transaction-details">
                        <div class="detail-item">
                            <div class="detail-label">Event</div>
                            <div class="detail-value">{event_name}</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">Price</div>
                            <div class="detail-value price">${price}</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">Order ID</div>
                            <div class="detail-value">#ST-{transaction_id or "PENDING"}</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">Seller</div>
                            <div class="detail-value">{seller_email}</div>
                        </div>
                    </div>
                </div>
                
                <div class="next-steps">
                    <h3 class="next-steps-title">
                        <span style="margin-right: 8px;">⚡</span>
                        What happens next:
                    </h3>
                    <div class="step">
                        <span class="step-icon">🔒</span>
                        <span class="step-text">Your funds are securely held in escrow until ticket delivery</span>
                    </div>
                    <div class="step">
                        <span class="step-icon">🎫</span>
                        <span class="step-text">The seller will transfer your verified ticket shortly</span>
                    </div>
                    <div class="step">
                        <span class="step-icon">📧</span>
                        <span class="step-text">You'll receive an email with your ticket once it's ready</span>
                    </div>
                    <div class="step">
                        <span class="step-icon">🛡️</span>
                        <span class="step-text">Full protection guarantee - if anything goes wrong, you're covered</span>
                    </div>
                </div>
                
                <div class="cta-section">
                    <a href="{ticket_status_url}" class="cta-button">
                        📋 Track Your Order
                    </a>
                </div>
            </div>
            
            <div class="footer">
                <div class="footer-text">Questions? We're here to help!</div>
                <div class="footer-text">
                    <a href="mailto:support@safetransaction.app" class="footer-link">support@safetransaction.app</a>
                </div>
                <div class="footer-text" style="margin-top: 16px; font-size: 12px; color: #9ca3af;">
                    Safe Transaction - Secure Ticket Protection
                </div>
            </div>
        </div>
    </body>
    </html>
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

def send_ticket_sent_email(buyer_email, event_name, price, seller_email, event_datetime, transaction_id, validation_deadline):
    """Send Email 2: Ticket sent notification to buyer with validation options."""
    subject = f"🎫 Your {event_name} ticket has been sent!"
    
    DOMAIN = "http://localhost:8000"  # CHANGE THIS to your deployed domain!
    validate_url = f"{DOMAIN}/validate-ticket/{transaction_id}"
    complaint_url = f"{DOMAIN}/ticket/{transaction_id}#complaint"
    
    body = (
        f"Great news! Your ticket for '{event_name}' has been sent by the seller.\n\n"
        f"Event: {event_name}\n"
        f"Price: ${price}\n"
        f"Seller: {seller_email}\n"
        f"Event Date: {event_datetime}\n\n"
        f"IMPORTANT: Please check your ticket and validate it within 2 minutes.\n"
        f"If you don't validate or report a problem, the transaction will automatically complete.\n\n"
        f"Validation deadline: {validation_deadline}\n\n"
        f"To validate: {validate_url}\n"
        f"To report problem: {complaint_url}\n\n"
        "Best,\nSafe-Transaction Team"
    )
    
    validate_btn = f'<a href="{validate_url}" style="background:#28a745;color:white;padding:12px 24px;border:none;border-radius:5px;text-decoration:none;display:inline-block;font-family:sans-serif;font-size:16px;font-weight:bold;margin-right:10px;">✅ Validate Ticket</a>'
    problem_btn = f'<a href="{complaint_url}" style="background:#dc3545;color:white;padding:12px 24px;border:none;border-radius:5px;text-decoration:none;display:inline-block;font-family:sans-serif;font-size:16px;font-weight:bold;">⚠️ Report Problem</a>'
    
    html = f'''
        <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #28a745;">🎫 Your ticket has been sent!</h2>
            
            <div style="background: #f8f9fa; border-left: 4px solid #28a745; padding: 15px; margin: 20px 0;">
                <h3 style="margin-top: 0; color: #333;">Event Details</h3>
                <p><strong>Event:</strong> {event_name}</p>
                <p><strong>Price:</strong> ${price}</p>
                <p><strong>Seller:</strong> {seller_email}</p>
                <p><strong>Event Date:</strong> {event_datetime}</p>
            </div>
            
            <div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0;">
                <h3 style="margin-top: 0; color: #856404;">⏰ Action Required</h3>
                <p>Please check your ticket and validate it within <strong>2 minutes</strong>.</p>
                <p>If you don't take action, the transaction will automatically complete at:</p>
                <p style="font-weight: bold; color: #dc3545;">{validation_deadline}</p>
            </div>
            
            <div style="text-align: center; margin: 30px 0;">
                {validate_btn}
                {problem_btn}
            </div>
            
            <div style="background: #e9ecef; padding: 15px; border-radius: 5px; margin-top: 20px;">
                <p style="margin: 0; font-size: 14px; color: #6c757d;">
                    <strong>Security Note:</strong> Only validate if you've received the correct ticket. 
                    If there are any issues, report them immediately.
                </p>
            </div>
            
            <p style="margin-top: 30px;">Best,<br>Safe-Transaction Team</p>
        </div>
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
