"""
Modern email automation with ultra-sleek designs for TicketVault.
All emails redesigned with cutting-edge UI/UX.
"""

import insta485
from flask_mail import Message
import logging

logger = logging.getLogger(__name__)


def send_email(to_email, subject, html_content):
    """Base function to send emails with modern design"""
    msg = Message(subject=subject, recipients=[to_email], html=html_content)
    insta485.mail.send(msg)


def send_seller_instructions(
    transaction_id, seller_email, ticket_email, deadline, event_details
):
    """Send ultra-modern seller instructions with sleek design"""
    from datetime import datetime

    hours_remaining = max(0, (deadline - datetime.now()).total_seconds() / 3600)

    subject = f"🚀 MISSION BRIEFING: Deploy Tickets Now - TX-{transaction_id:06d}"

    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
            @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&display=swap');
            
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
                color: #f1f5f9;
                min-height: 100vh;
                line-height: 1.6;
            }}
            
            .mission-container {{
                max-width: 650px;
                margin: 40px auto;
                background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
                border-radius: 24px;
                overflow: hidden;
                box-shadow: 
                    0 25px 50px rgba(0, 0, 0, 0.4),
                    0 0 0 1px rgba(255, 255, 255, 0.05),
                    inset 0 1px 0 rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(20px);
                border: 1px solid rgba(239, 68, 68, 0.3);
            }}
            
            .mission-header {{
                background: linear-gradient(135deg, #ef4444 0%, #dc2626 50%, #b91c1c 100%);
                padding: 40px;
                text-align: center;
                position: relative;
                overflow: hidden;
            }}
            
            .mission-header::before {{
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: 
                    radial-gradient(circle at 20% 80%, rgba(255, 255, 255, 0.1) 0%, transparent 50%),
                    radial-gradient(circle at 80% 20%, rgba(255, 255, 255, 0.1) 0%, transparent 50%);
                animation: missionPulse 3s ease-in-out infinite;
            }}
            
            @keyframes missionPulse {{
                0%, 100% {{ opacity: 0.8; }}
                50% {{ opacity: 1; }}
            }}
            
            .mission-title {{
                font-size: 2.25rem;
                font-weight: 900;
                margin-bottom: 8px;
                position: relative;
                z-index: 1;
                text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
            }}
            
            .urgent-alert {{
                background: linear-gradient(135deg, #f59e0b, #d97706);
                color: white;
                padding: 20px;
                text-align: center;
                font-weight: 800;
                font-size: 1.125rem;
                animation: urgentFlash 2s ease-in-out infinite;
            }}
            
            @keyframes urgentFlash {{
                0%, 100% {{ transform: scale(1); }}
                50% {{ transform: scale(1.02); }}
            }}
            
            .mission-content {{
                padding: 40px;
            }}
            
            .status-chip {{
                display: inline-block;
                background: linear-gradient(135deg, #10b981, #059669);
                color: white;
                padding: 8px 16px;
                border-radius: 20px;
                font-size: 0.875rem;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                margin-bottom: 24px;
            }}
            
            .deadline-critical {{
                background: linear-gradient(135deg, #fee2e2, #fecaca);
                border: 2px solid #ef4444;
                color: #7f1d1d;
                padding: 24px;
                border-radius: 16px;
                margin: 24px 0;
                text-align: center;
                position: relative;
                overflow: hidden;
            }}
            
            .deadline-critical::before {{
                content: '';
                position: absolute;
                top: 0;
                left: -100%;
                width: 100%;
                height: 100%;
                background: linear-gradient(90deg, transparent, rgba(239, 68, 68, 0.1), transparent);
                animation: deadlineSlide 2s ease-in-out infinite;
            }}
            
            @keyframes deadlineSlide {{
                0% {{ left: -100%; }}
                100% {{ left: 100%; }}
            }}
            
            .portal-section {{
                background: linear-gradient(135deg, #fef3c7, #fed7aa);
                border: 3px solid #f59e0b;
                border-radius: 20px;
                padding: 32px;
                margin: 32px 0;
                text-align: center;
                position: relative;
                overflow: hidden;
            }}
            
            .portal-email {{
                font-family: 'JetBrains Mono', monospace;
                font-size: 1.25rem;
                font-weight: 700;
                color: #92400e;
                background: rgba(255, 255, 255, 0.8);
                padding: 16px;
                border-radius: 12px;
                word-break: break-all;
                position: relative;
                z-index: 1;
                border: 2px solid #d97706;
            }}
            
            .instruction-card {{
                background: rgba(59, 130, 246, 0.1);
                border: 1px solid rgba(59, 130, 246, 0.2);
                border-radius: 16px;
                padding: 24px;
                border-left: 4px solid #3b82f6;
                margin: 20px 0;
            }}
            
            .mission-footer {{
                background: rgba(15, 23, 42, 0.8);
                padding: 32px;
                text-align: center;
                border-top: 1px solid rgba(255, 255, 255, 0.1);
            }}
            
            .transaction-id {{
                background: linear-gradient(135deg, #475569, #64748b);
                color: #f1f5f9;
                padding: 12px 24px;
                border-radius: 50px;
                font-family: 'JetBrains Mono', monospace;
                font-size: 14px;
                font-weight: 600;
                display: inline-block;
                margin: 16px 0;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }}
        </style>
    </head>
    <body>
        <div class="mission-container">
            <div class="mission-header">
                <h1 class="mission-title">🚀 MISSION CONTROL</h1>
                <p>Ultra-Secure Ticket Deployment Protocol</p>
            </div>
            
            <div class="urgent-alert">
                ⚡ CRITICAL: BUYER STANDING BY - DEPLOY TICKETS IMMEDIATELY
            </div>
            
            <div class="mission-content">
                <div class="status-chip">🎯 MISSION ACTIVE</div>
                
                <h2 style="color: #f1f5f9; margin-bottom: 16px;">Agent Briefing</h2>
                <p style="color: #cbd5e1; margin-bottom: 24px;">
                    Mission confirmed! Buyer has been notified and is cleared for payment processing of your 
                    <strong style="color: #10b981;">{event_details["name"]}</strong> tickets.
                </p>
                
                <div class="deadline-critical">
                    <h3 style="margin-bottom: 8px;">⏰ MISSION DEADLINE</h3>
                    <div style="font-size: 1.5rem; font-weight: 900; margin: 8px 0;">{int(hours_remaining)} Hours Remaining</div>
                    <p style="font-size: 0.875rem; font-weight: 600;">
                        Expires: {deadline.strftime("%B %d, %Y at %I:%M %p")}
                    </p>
                </div>
                
                <div class="portal-section">
                    <div style="color: #92400e; font-size: 1.5rem; font-weight: 800; margin-bottom: 16px;">🎯 SECURE UPLOAD PORTAL</div>
                    <div class="portal-email">{ticket_email}</div>
                    <p style="font-size: 0.875rem; margin-top: 16px; color: #92400e; font-weight: 600;">
                        CLASSIFIED: Use this encrypted endpoint only
                    </p>
                </div>
                
                <div class="instruction-card">
                    <h4 style="color: #f1f5f9; margin-bottom: 16px;">🔄 DEPLOYMENT INSTRUCTIONS</h4>
                    <ol style="color: #cbd5e1; padding-left: 20px;">
                        <li style="margin-bottom: 12px;"><strong>Forward Original Email</strong> - Send the complete email from Ticketmaster, StubHub, or your ticket provider</li>
                        <li style="margin-bottom: 12px;"><strong>Include All Attachments</strong> - Ensure all PDFs, images, and digital tickets are attached</li>
                        <li style="margin-bottom: 12px;"><strong>Verify Target Address</strong> - Copy the email address exactly: <code style="color: #3b82f6;">{ticket_email}</code></li>
                        <li style="margin-bottom: 12px;"><strong>Execute Deployment</strong> - Send immediately - Our AI will verify tickets in real-time</li>
                    </ol>
                </div>
                
                <div style="background: linear-gradient(135deg, #6366f1, #4f46e5); color: white; padding: 32px; border-radius: 20px; margin: 32px 0;">
                    <h4 style="font-size: 1.25rem; font-weight: 800; margin-bottom: 16px;">🚫 MISSION-CRITICAL PROTOCOL</h4>
                    <p style="font-weight: 500; line-height: 1.6;">
                        <strong>NEVER</strong> send tickets directly to the buyer! Our secure system protects both parties 
                        through verified escrow processing. All tickets must pass through our authentication pipeline.
                    </p>
                </div>
            </div>
            
            <div class="mission-footer">
                <div class="transaction-id">TX-{transaction_id:06d}</div>
                <div style="color: #94a3b8; margin: 16px 0; font-weight: 500;">Mission support available 24/7 - Reply for immediate assistance</div>
                <div style="font-weight: 800; color: #ef4444; font-size: 1.125rem; text-shadow: 0 0 20px rgba(239, 68, 68, 0.3);">TICKETVAULT</div>
            </div>
        </div>
    </body>
    </html>
    """

    send_email(seller_email, subject, html_body)


def send_reminder_emails(transaction_id, email, email_type, hours_remaining, details):
    """Send ultra-modern reminder emails"""
    if email_type == "ticket_deadline":
        subject = f"🚨 URGENT: {int(hours_remaining)}H LEFT - Deploy Tickets TX-{transaction_id:06d}"
        icon = "🎫"
        action = "SEND TICKETS NOW"
        color_scheme = "#ef4444"
    else:  # payment_deadline
        subject = f"⏰ PAYMENT WINDOW CLOSING: {int(hours_remaining)}H LEFT - TX-{transaction_id:06d}"
        icon = "💳"
        action = "COMPLETE PAYMENT NOW"
        color_scheme = "#f59e0b"

    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
            
            body {{
                font-family: 'Inter', sans-serif;
                background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
                color: #f1f5f9;
                margin: 0;
                padding: 40px 20px;
            }}
            
            .alert-container {{
                max-width: 600px;
                margin: 0 auto;
                background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
                border-radius: 24px;
                overflow: hidden;
                box-shadow: 0 25px 50px rgba(0, 0, 0, 0.4);
                border: 2px solid {color_scheme};
                animation: alertPulse 2s ease-in-out infinite;
            }}
            
            @keyframes alertPulse {{
                0%, 100% {{ transform: scale(1); box-shadow: 0 25px 50px rgba(0, 0, 0, 0.4), 0 0 0 0 {color_scheme}40; }}
                50% {{ transform: scale(1.02); box-shadow: 0 30px 60px rgba(0, 0, 0, 0.5), 0 0 0 20px {color_scheme}00; }}
            }}
            
            .alert-header {{
                background: linear-gradient(135deg, {color_scheme}, {color_scheme}dd);
                padding: 40px;
                text-align: center;
                color: white;
            }}
            
            .alert-content {{
                padding: 40px;
                text-align: center;
            }}
            
            .countdown-display {{
                background: linear-gradient(135deg, #fee2e2, #fecaca);
                color: #7f1d1d;
                padding: 32px;
                border-radius: 20px;
                margin: 24px 0;
                font-size: 2rem;
                font-weight: 900;
                border: 3px solid #ef4444;
            }}
            
            .action-button {{
                display: inline-block;
                background: linear-gradient(135deg, {color_scheme}, {color_scheme}dd);
                color: white;
                padding: 20px 40px;
                text-decoration: none;
                border-radius: 50px;
                font-weight: 800;
                font-size: 1.25rem;
                margin: 32px 0;
                box-shadow: 0 15px 35px {color_scheme}40;
            }}
        </style>
    </head>
    <body>
        <div class="alert-container">
            <div class="alert-header">
                <h1 style="font-size: 2.5rem; margin-bottom: 16px;">{icon} URGENT REMINDER</h1>
                <p style="font-size: 1.25rem;">Time-sensitive action required</p>
            </div>
            
            <div class="alert-content">
                <div class="countdown-display">
                    {int(hours_remaining)} HOURS LEFT
                </div>
                
                <h2 style="color: #f1f5f9; margin-bottom: 24px;">Action Required</h2>
                <p style="color: #cbd5e1; font-size: 1.125rem; margin-bottom: 32px;">
                    Your transaction window is closing soon. Please take immediate action to avoid automatic expiration.
                </p>
                
                <a href="http://localhost:8000/ticket/{transaction_id}" class="action-button">
                    {action}
                </a>
                
                <div style="background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 16px; padding: 24px; margin: 32px 0;">
                    <h3 style="color: #ef4444; margin-bottom: 12px;">⚠️ What happens if time expires?</h3>
                    <p style="color: #cbd5e1; font-size: 0.875rem;">
                        Transaction will be automatically cancelled and tickets/funds will be returned to their original owners.
                    </p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

    send_email(email, subject, html_body)


def send_expiration_notification(
    transaction_id, seller_email, buyer_email, event_name, reason
):
    """Send ultra-modern expiration notification"""
    subject = f"🔄 Transaction Expired - TX-{transaction_id:06d} | Automatic Resolution"

    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
            
            body {{
                font-family: 'Inter', sans-serif;
                background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
                color: #f1f5f9;
                margin: 0;
                padding: 40px 20px;
            }}
            
            .notification-container {{
                max-width: 600px;
                margin: 0 auto;
                background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
                border-radius: 24px;
                overflow: hidden;
                box-shadow: 0 25px 50px rgba(0, 0, 0, 0.4);
                border: 1px solid rgba(245, 158, 11, 0.3);
            }}
            
            .notification-header {{
                background: linear-gradient(135deg, #f59e0b, #d97706);
                padding: 40px;
                text-align: center;
                color: white;
            }}
            
            .notification-content {{
                padding: 40px;
            }}
            
            .status-badge {{
                display: inline-block;
                background: linear-gradient(135deg, #6b7280, #4b5563);
                color: white;
                padding: 12px 24px;
                border-radius: 50px;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                margin-bottom: 24px;
            }}
            
            .resolution-box {{
                background: linear-gradient(135deg, #dcfce7, #bbf7d0);
                border: 2px solid #10b981;
                color: #065f46;
                padding: 32px;
                border-radius: 20px;
                margin: 32px 0;
                text-align: center;
            }}
        </style>
    </head>
    <body>
        <div class="notification-container">
            <div class="notification-header">
                <h1 style="font-size: 2.25rem; margin-bottom: 16px;">🔄 AUTOMATIC RESOLUTION</h1>
                <p style="font-size: 1.125rem;">Transaction processed by our secure system</p>
            </div>
            
            <div class="notification-content">
                <div class="status-badge">⏰ EXPIRED</div>
                
                <h2 style="color: #f1f5f9; margin-bottom: 16px;">Transaction Update</h2>
                <p style="color: #cbd5e1; margin-bottom: 24px;">
                    Your transaction for <strong style="color: #10b981;">{event_name}</strong> has expired due to: <em>{reason}</em>
                </p>
                
                <div class="resolution-box">
                    <h3 style="font-size: 1.25rem; font-weight: 800; margin-bottom: 16px;">✅ AUTOMATIC RESOLUTION COMPLETE</h3>
                    <p style="font-weight: 500; line-height: 1.6;">
                        Our secure system has automatically processed the return of tickets/funds to their original owners. 
                        No further action is required from either party.
                    </p>
                </div>
                
                <div style="text-align: center; margin: 32px 0;">
                    <p style="color: #cbd5e1; margin-bottom: 16px;">Want to create a new listing?</p>
                    <a href="http://localhost:8000/seller" style="display: inline-block; background: linear-gradient(135deg, #3b82f6, #1e40af); color: white; padding: 16px 32px; text-decoration: none; border-radius: 50px; font-weight: 700;">
                        🚀 Create New Listing
                    </a>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

    send_email(seller_email, subject, html_body)
    send_email(buyer_email, subject, html_body)


def forward_ticket_email(
    to_email, original_email_data, transaction_id, return_mode=False
):
    """Forward ticket email with modern design wrapper"""
    action = "returned to seller" if return_mode else "delivered to buyer"
    subject = f"🎫 Tickets {action.title()} - TX-{transaction_id:06d}"

    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
            
            body {{
                font-family: 'Inter', sans-serif;
                background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
                color: #f1f5f9;
                margin: 0;
                padding: 20px;
            }}
            
            .delivery-wrapper {{
                max-width: 650px;
                margin: 0 auto;
                background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
                border-radius: 24px;
                overflow: hidden;
                box-shadow: 0 25px 50px rgba(0, 0, 0, 0.4);
                border: 1px solid rgba(16, 185, 129, 0.3);
            }}
            
            .delivery-header {{
                background: linear-gradient(135deg, #10b981, #059669);
                padding: 32px;
                text-align: center;
                color: white;
            }}
            
            .original-email {{
                background: white;
                color: #1f2937;
                padding: 32px;
                font-family: inherit;
            }}
            
            .delivery-footer {{
                background: rgba(15, 23, 42, 0.8);
                padding: 24px;
                text-align: center;
                border-top: 1px solid rgba(255, 255, 255, 0.1);
            }}
        </style>
    </head>
    <body>
        <div class="delivery-wrapper">
            <div class="delivery-header">
                <h1 style="font-size: 2rem; margin-bottom: 12px;">🎫 SECURE TICKET DELIVERY</h1>
                <p style="font-size: 1.125rem;">Your tickets have been {action} securely</p>
            </div>
            
            <div class="original-email">
                {original_email_data.get("html_content", original_email_data.get("text_content", "Original ticket content"))}
            </div>
            
            <div class="delivery-footer">
                <div style="background: linear-gradient(135deg, #475569, #64748b); color: #f1f5f9; padding: 12px 24px; border-radius: 50px; font-family: 'JetBrains Mono', monospace; font-size: 14px; font-weight: 600; display: inline-block; margin: 16px 0; border: 1px solid rgba(255, 255, 255, 0.2);">TX-{transaction_id:06d}</div>
                <div style="color: #94a3b8; margin: 16px 0;">Secure delivery powered by TicketVault</div>
            </div>
        </div>
    </body>
    </html>
    """

    send_email(to_email, subject, html_body)


# Wrapper functions for compatibility
def send_buyer_notification(
    transaction_id,
    buyer_email,
    seller_email,
    price,
    event_details,
    payment_deadline=None,
):
    """Send modern, minimalistic buyer notification"""
    from datetime import datetime

    # Calculate payment deadline if provided
    payment_hours = None
    if payment_deadline:
        # Ensure payment_deadline is a datetime object
        if isinstance(payment_deadline, str):
            from datetime import datetime

            try:
                if "T" in payment_deadline:
                    payment_deadline = datetime.fromisoformat(
                        payment_deadline.replace("Z", "+00:00")
                    )
                else:
                    payment_deadline = datetime.strptime(
                        payment_deadline, "%Y-%m-%d %H:%M:%S"
                    )
            except ValueError:
                payment_deadline = None

        if payment_deadline:
            payment_hours = max(
                0, (payment_deadline - datetime.now()).total_seconds() / 3600
            )

    # Format deadline text
    deadline_text = ""
    if payment_deadline:
        deadline_text = payment_deadline.strftime("%I:%M %p on %B %d")

    # Smart status check route that handles cancellation and routes to payment
    payment_url = f"http://localhost:8000/ticket_status_check/{transaction_id}"

    subject = f"✅ Your {event_details['name']} Tickets Are Ready"

    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Circular:wght@400;500;700&display=swap');
            
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Circular', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background-color: #f7f7f7;
                color: #222222;
                line-height: 1.43;
                margin: 0;
                padding: 0;
            }}
            
            .email-container {{
                max-width: 680px;
                margin: 0 auto;
                background: #ffffff;
            }}
            
            .header {{
                padding: 32px 24px 0 24px;
                text-align: left;
            }}
            
            .logo {{
                color: #3b82f6;
                font-size: 28px;
                font-weight: 700;
                text-decoration: none;
                letter-spacing: -0.5px;
            }}
            
            .tagline {{
                color: #717171;
                font-size: 14px;
                font-weight: 400;
                margin-top: 4px;
            }}
            
            .content {{
                padding: 32px 24px;
            }}
            
            .section {{
                margin-bottom: 32px;
            }}
            
            .section-header {{
                display: flex;
                align-items: center;
                margin-bottom: 16px;
            }}
            
            .section-header h2 {{
                font-size: 20px;
                font-weight: 700;
                color: #222222;
                margin-left: 8px;
            }}
            
            .section-text {{
                color: #484848;
                margin-bottom: 16px;
                line-height: 1.5;
                font-size: 16px;
            }}
            
            
            .ticket-card {{
                border: 1px solid #DDDDDD;
                border-radius: 12px;
                overflow: hidden;
                margin: 32px 0;
                background: #ffffff;
            }}
            
            .ticket-header {{
                padding: 24px;
                border-bottom: 1px solid #EBEBEB;
            }}
            
            .event-title {{
                font-size: 20px;
                font-weight: 700;
                color: #222222;
                margin-bottom: 8px;
                line-height: 1.3;
            }}
            
            .event-subtitle {{
                font-size: 14px;
                color: #717171;
                font-weight: 400;
            }}
            
            .ticket-details {{
                padding: 24px;
            }}
            
            .detail-grid {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 24px;
                margin-bottom: 24px;
            }}
            
            .detail-item {{
                
            }}
            
            .detail-label {{
                font-size: 12px;
                color: #717171;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                margin-bottom: 4px;
                font-weight: 500;
            }}
            
            .detail-value {{
                font-size: 16px;
                color: #222222;
                font-weight: 500;
                line-height: 1.3;
            }}
            
            .price-section {{
                border-top: 1px solid #EBEBEB;
                padding-top: 24px;
                text-align: center;
            }}
            
            .price-label {{
                font-size: 14px;
                color: #717171;
                margin-bottom: 8px;
            }}
            
            .price-value {{
                font-size: 32px;
                font-weight: 700;
                color: #059669;
                line-height: 1;
            }}
            
            .cta-section {{
                text-align: center;
                margin: 40px 0;
            }}
            
            .cta-button {{
                display: inline-block;
                background: #059669;
                color: #ffffff;
                padding: 16px 32px;
                text-decoration: none;
                border-radius: 8px;
                font-weight: 700;
                font-size: 16px;
                border: none;
                cursor: pointer;
                transition: background 0.2s ease;
                margin-bottom: 16px;
            }}
            
            .cta-button:hover {{
                background: #047857;
            }}
            
            .reassurance {{
                color: #717171;
                font-size: 14px;
                margin-bottom: 8px;
            }}
            
            .problem-link {{
                color: #3b82f6;
                text-decoration: none;
                font-size: 14px;
                display: inline-block;
            }}
            
            
            .protection-list {{
                list-style: none;
                padding: 0;
                margin: 0;
            }}
            
            .protection-item {{
                display: flex;
                align-items: center;
                margin-bottom: 12px;
                font-size: 14px;
                color: #484848;
            }}
            
            .check-icon {{
                width: 20px;
                height: 20px;
                background: #059669;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                margin-right: 12px;
                flex-shrink: 0;
            }}
            
            .footer-section {{
                background: #f7f7f7;
                padding: 32px 24px;
                text-align: center;
                border-top: 1px solid #EBEBEB;
            }}
            
            .footer-text {{
                font-size: 12px;
                color: #717171;
                line-height: 1.4;
                margin-bottom: 8px;
            }}
            
            .footer-link {{
                color: #3b82f6;
                text-decoration: none;
            }}
            
            .footer-brand {{
                font-size: 14px;
                font-weight: 700;
                color: #3b82f6;
                margin-top: 16px;
            }}
            
            
            @media (max-width: 600px) {{
                .email-container {{
                    margin: 0;
                }}
                
                .content {{
                    padding: 24px 16px;
                }}
                
                .header {{
                    padding: 24px 16px 0 16px;
                }}
                
                .detail-grid {{
                    grid-template-columns: 1fr;
                    gap: 16px;
                }}
                
                .footer-section {{
                    padding: 24px 16px;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <div class="header">
                <div class="logo">TicketVault</div>
                <div class="tagline">Secure Ticket Protection</div>
            </div>
            
            <div class="content">
                <div class="section">
                    <div class="section-header">
                        <span style="font-size: 24px;">🎟️</span>
                        <h2>Ticket Verified & Available</h2>
                    </div>
                    <p class="section-text">
                        This ticket has been independently verified by TicketVault. It matches the event, date, and seat details listed below:
                    </p>
                </div>
                
                <div class="ticket-card">
                    <div class="ticket-header">
                        <div class="event-title">{event_details["name"]}</div>
                        <div class="event-subtitle">Verified by TicketVault</div>
                    </div>
                    
                    <div class="ticket-details">
                        <div class="detail-grid">
                            <div class="detail-item">
                                <div class="detail-label">Location</div>
                                <div class="detail-value">{event_details["location"]}</div>
                            </div>
                            <div class="detail-item">
                                <div class="detail-label">Date & Time</div>
                                <div class="detail-value">{event_details["datetime"]}</div>
                            </div>
                        </div>
                        
                        <div class="price-section">
                            <div class="price-label">Total price</div>
                            <div class="price-value">${price}</div>
                        </div>
                    </div>
                </div>
                
                <!-- Payment Deadline Section -->
                {"<div class='section'><div class='section-header'><span style='font-size: 24px;'>⏳</span><h2>Payment Deadline</h2></div><p class='section-text'>Please complete payment by " + deadline_text + " to secure your ticket.</p></div>" if payment_hours else ""}
                
                <!-- Payment Button Section -->
                <div class="cta-section">
                    <a href="{payment_url}" class="cta-button">
                        💳 Complete Secure Payment
                    </a>
                    <div class="reassurance">
                        If anything goes wrong, you'll get a full refund — guaranteed.
                    </div>
                    <a href="mailto:safetransactiontix@gmail.com?subject=Problem%20with%20Transaction%20{transaction_id}" class="problem-link">
                        📢 Report a Problem
                    </a>
                </div>
                
                <!-- Purchase Protection Section -->
                <div class="section">
                    <div class="section-header">
                        <span style="font-size: 24px;">✅</span>
                        <h2>Your Purchase is Protected</h2>
                    </div>
                    <p class="section-text">
                        You have 24 hours after the event to let us know if anything went wrong — if so, we'll refund you in full.
                    </p>
                </div>
            </div>
            
            <div class="footer-section">
                <div class="footer-text">Transaction ID: #{transaction_id}</div>
                <div class="footer-text">
                    Need help? <a href="mailto:safetransactiontix@gmail.com" class="footer-link">Contact Support</a>
                </div>
                <div class="footer-brand">TicketVault</div>
            </div>
        </div>
    </body>
    </html>
    """

    send_email(buyer_email, subject, html_body)


def send_modern_buyer_notification(
    transaction_id,
    buyer_email,
    seller_email,
    price,
    event_details,
    payment_deadline=None,
):
    """Send simple, accurate buyer notification"""
    from datetime import datetime

    # Calculate payment deadline if provided
    if payment_deadline:
        # Ensure payment_deadline is a datetime object
        if isinstance(payment_deadline, str):
            from datetime import datetime

            payment_deadline = datetime.fromisoformat(
                payment_deadline.replace("Z", "+00:00")
            )

    # Use smart status check route that handles cancellation and routes to payment
    payment_url = f"http://localhost:8000/ticket_status_check/{transaction_id}"

    subject = f"🎫 Verified Ticket Available - {event_details['name']}"

    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Circular:wght@400;500;700&display=swap');
            
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Circular', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background-color: #f7f7f7;
                color: #222222;
                line-height: 1.43;
                margin: 0;
                padding: 0;
            }}
            
            .email-container {{
                max-width: 680px;
                margin: 0 auto;
                background: #ffffff;
            }}
            
            .header {{
                background: linear-gradient(135deg, #3b82f6 0%, #059669 100%);
                padding: 48px 40px;
                text-align: center;
                color: white;
            }}
            
            .logo {{
                color: white;
                font-size: 32px;
                font-weight: 700;
                text-decoration: none;
                letter-spacing: -0.5px;
                margin-bottom: 8px;
            }}
            
            .tagline {{
                color: white;
                font-size: 16px;
                margin: 16px 0 0 0;
                opacity: 0.9;
                font-weight: 500;
            }}
            
            .content {{
                padding: 40px 32px;
            }}
            
            .section {{
                margin-bottom: 48px;
            }}
            
            .section-header {{
                display: flex;
                align-items: center;
                margin-bottom: 24px;
            }}
            
            .ticket-card {{
                background: #ffffff;
                border-radius: 16px;
                margin: 32px 0;
                padding: 32px;
                border: 1px solid #e5e7eb;
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            }}
            
            .ticket-header {{
                padding: 0 0 24px 0;
                border-bottom: 1px solid #f1f3f4;
                margin-bottom: 32px;
            }}
            
            .event-title {{
                font-size: 20px;
                font-weight: 700;
                color: #222222;
                margin-bottom: 8px;
                line-height: 1.3;
            }}
            
            .event-subtitle {{
                font-size: 14px;
                color: #717171;
                font-weight: 400;
            }}
            
            .ticket-details {{
                padding: 0;
            }}
            
            .detail-grid {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 32px;
                margin-bottom: 0;
            }}
            
            .detail-item {{
                background: #ffffff;
                border-radius: 12px;
                padding: 24px;
                box-shadow: none;
                border: 1px solid #f1f3f4;
                transition: all 0.2s ease;
            }}
            
            .detail-item:hover {{
                border-color: #d1d5db;
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
                font-size: 18px;
                color: #1f2937;
                font-weight: 700;
                line-height: 1.4;
                margin: 0;
            }}
            
            .detail-value.price {{
                font-size: 24px;
                color: #059669;
                font-weight: 800;
            }}
            
            
            .cta-section {{
                text-align: center;
                margin: 32px 0 0 0;
            }}
            
            .cta-button {{
                display: inline-block;
                background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
                color: #ffffff !important;
                padding: 18px 36px;
                text-decoration: none;
                border-radius: 12px;
                font-weight: 700;
                font-size: 16px;
                border: none;
                cursor: pointer;
                transition: all 0.3s ease;
                width: 100%;
                max-width: 320px;
                box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
                text-align: center;
            }}
            
            .cta-button:hover {{
                background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
                color: #ffffff !important;
                box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
                transform: translateY(-2px);
            }}
            
            .payment-container {{
                background: #ffffff;
                border-radius: 16px;
                margin: 24px 0 0 0;
                padding: 24px;
                border: 1px solid #e5e7eb;
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            }}
            
            .deadline-banner {{
                background: #fff3cd;
                border: 1px solid #ffeaa7;
                border-radius: 8px;
                padding: 16px 20px;
                margin: 24px 0;
                text-align: center;
            }}
            
            .deadline-text {{
                color: #856404;
                font-size: 14px;
                font-weight: 500;
                margin: 0;
            }}
            
            .protection-section {{
                background: #f9fafb;
                border-radius: 12px;
                padding: 24px;
                margin: 32px 0;
            }}
            
            .protection-title {{
                font-size: 18px;
                font-weight: 700;
                color: #222222;
                margin-bottom: 16px;
            }}
            
            .protection-list {{
                list-style: none;
                padding: 0;
                margin: 0;
            }}
            
            .protection-item {{
                display: flex;
                align-items: center;
                margin-bottom: 12px;
                font-size: 14px;
                color: #484848;
            }}
            
            .check-icon {{
                width: 20px;
                height: 20px;
                background: #059669;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                margin-right: 12px;
                flex-shrink: 0;
            }}
            
            .footer-section {{
                background: #f7f7f7;
                padding: 32px 24px;
                text-align: center;
                border-top: 1px solid #EBEBEB;
            }}
            
            .footer-text {{
                font-size: 12px;
                color: #717171;
                line-height: 1.4;
                margin-bottom: 8px;
            }}
            
            .footer-link {{
                color: #3b82f6;
                text-decoration: none;
            }}
            
            .footer-brand {{
                font-size: 14px;
                font-weight: 700;
                color: #3b82f6;
                margin-top: 16px;
            }}
            
            .divider {{
                height: 1px;
                background: #EBEBEB;
                margin: 32px 0;
            }}
            
            .help-section {{
                text-align: center;
                margin: 24px 0;
            }}
            
            .help-text {{
                font-size: 14px;
                color: #717171;
                margin-bottom: 8px;
            }}
            
            .help-link {{
                color: #3b82f6;
                text-decoration: none;
                font-size: 14px;
                font-weight: 500;
            }}
            
            @media (max-width: 600px) {{
                .email-container {{
                    margin: 0;
                }}
                
                .content {{
                    padding: 32px 20px;
                }}
                
                .header {{
                    padding: 32px 20px;
                }}
                
                .logo {{
                    font-size: 28px;
                }}
                
                .detail-grid {{
                    grid-template-columns: 1fr;
                    gap: 20px;
                }}
                
                .detail-item {{
                    padding: 20px;
                }}
                
                .detail-label {{
                    font-size: 10px;
                    margin-bottom: 6px;
                }}
                
                .detail-value {{
                    font-size: 16px;
                }}
                
                .detail-value.price {{
                    font-size: 20px;
                }}
                
                .cta-button {{
                    width: 100%;
                    max-width: none;
                }}
                
                .payment-container {{
                    margin: 16px 0 0 0;
                    padding: 20px;
                }}
                
                .section-header {{
                    flex-direction: column;
                    align-items: flex-start;
                    text-align: left;
                }}
                
                .section-header span {{
                    margin-bottom: 12px;
                    margin-right: 0 !important;
                }}
                
                .footer-section {{
                    padding: 32px 20px;
                }}
                
                .ticket-details {{
                    padding: 24px;
                }}
                
                .ticket-card {{
                    margin: 32px 0;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <div class="header">
                <div class="logo">TicketVault</div>
                <div class="tagline">Secure Ticket Protection</div>
            </div>
            
            <div class="content">
                <!-- Section 1: Ticket Verified & Available -->
                <div class="section">
                    <div class="section-header">
                        <span style="font-size: 24px; margin-right: 12px;">🎉</span>
                        <h2 style="font-size: 24px; font-weight: 800; color: #059669; margin: 0;">Your ticket is ready!</h2>
                    </div>
                    <p style="color: #222222; margin-bottom: 32px; line-height: 1.6; font-size: 18px; font-weight: 500;">
                        Exciting news! We've carefully verified every detail of your ticket — it's 100% authentic and matches the event perfectly. Here's what you're getting:
                    </p>
                    
                    <div class="ticket-card">
                        <div class="ticket-details">
                            <div class="detail-grid">
                                <div class="detail-item">
                                    <div class="detail-label">Event</div>
                                    <div class="detail-value">{event_details["name"]}</div>
                                </div>
                                <div class="detail-item">
                                    <div class="detail-label">Location</div>
                                    <div class="detail-value">{event_details["location"]}</div>
                                </div>
                                <div class="detail-item">
                                    <div class="detail-label">Date & Time</div>
                                    <div class="detail-value">{event_details["datetime"]}</div>
                                </div>
                                <div class="detail-item">
                                    <div class="detail-label">Price</div>
                                    <div class="detail-value price">${price}</div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Payment Button Container -->
                    <div class="payment-container">
                        <p style="color: #059669; font-size: 18px; font-weight: 700; margin: 0 0 16px 0; text-align: center;">
                            ✨ Just one click to make this ticket yours!
                        </p>
                        <div class="cta-section">
                            <a href="{payment_url}" class="cta-button">
                                🎫 Complete Your Payment
                            </a>
                        </div>
                    </div>
                </div>
                
                <!-- Section 2: Your Purchase is Protected -->
                <div class="section">
                    <div class="section-header">
                        <span style="font-size: 24px; margin-right: 12px;">🛡️</span>
                        <h2 style="font-size: 22px; font-weight: 700; color: #3b82f6; margin: 0;">We've got your back</h2>
                    </div>
                    <p style="color: #222222; margin-bottom: 32px; line-height: 1.6; font-size: 18px; font-weight: 500;">
                        Relax and enjoy the event! If anything doesn't go as planned, just let us know within 24 hours and we'll make it right with a full refund. No questions asked.
                    </p>
                </div>
                
                <!-- Section 3: Why Use TicketVault -->
                <div class="section">
                    <div class="section-header">
                        <span style="font-size: 20px; margin-right: 8px;">💡</span>
                        <h2 style="font-size: 20px; font-weight: 700; color: #222222; margin: 0;">Why Use TicketVault?</h2>
                </div>
                    <ul class="protection-list">
                        <li class="protection-item">
                            <div class="check-icon">
                                <span style="color: white; font-size: 12px; font-weight: bold;">✓</span>
                            </div>
                            Ticket Verification
                        </li>
                        <li class="protection-item">
                            <div class="check-icon">
                                <span style="color: white; font-size: 12px; font-weight: bold;">✓</span>
                            </div>
                            Secure transfer system
                        </li>
                        <li class="protection-item">
                            <div class="check-icon">
                                <span style="color: white; font-size: 12px; font-weight: bold;">✓</span>
                            </div>
                            Full Refund Guarantee
                        </li>
                        <li class="protection-item">
                            <div class="check-icon">
                                <span style="color: white; font-size: 12px; font-weight: bold;">✓</span>
                            </div>
                            24/7 Support
                        </li>
                    </ul>
                </div>
                
                <!-- Section 4: Payment Deadline -->
                <div class="section">
                    <div class="section-header">
                        <span style="font-size: 20px; margin-right: 8px;">⏳</span>
                        <h2 style="font-size: 20px; font-weight: 700; color: #222222; margin: 0;">Payment Deadline</h2>
                    </div>
                    <p style="color: #484848; margin-bottom: 24px; line-height: 1.6; font-size: 18px; font-weight: 500;">
                        Please complete payment within 1 hour to secure your ticket.
                    </p>
                </div>
                
                <!-- Section 5: Support Information -->
                <div style="text-align: center; margin: 32px 0;">
                    <div class="reassurance" style="color: #717171; font-size: 14px; margin-bottom: 16px;">
                        Questions? We're here to help! If something goes wrong, let us know and we'll attempt to refund you.
                    </div>
                    <a href="mailto:safetransactiontix@gmail.com?subject=Problem%20with%20Transaction%20{transaction_id}" class="help-link" style="color: #3b82f6; text-decoration: none; font-size: 14px; font-weight: 500;">
                        💬 Get Help or Report an Issue
                    </a>
                </div>
            </div>
            
            <div class="footer-section">
                <div class="footer-text">Transaction ID: #{transaction_id}</div>
                <div class="footer-text">
                    Need help? <a href="mailto:safetransactiontix@gmail.com" class="footer-link">Contact Support</a>
                </div>
                <div class="footer-brand">TicketVault</div>
            </div>
        </div>
    </body>
    </html>
    """

    # Use Mailgun sender instead of Flask-Mail to avoid context issues
    from insta485.mailgun_sender import mailgun_sender

    mailgun_sender.send_email(buyer_email, subject, html_body)


def send_buyer_waiting_notification(
    transaction_id, buyer_email, seller_email, price, event_details, ticket_deadline
):
    """Send notification to buyer that seller is preparing tickets"""
    from datetime import datetime

    # Calculate time remaining for seller
    if isinstance(ticket_deadline, str):
        ticket_deadline = datetime.fromisoformat(ticket_deadline.replace("Z", "+00:00"))

    minutes_remaining = max(0, (ticket_deadline - datetime.now()).total_seconds() / 60)

    subject = f"🎫 Tickets Being Prepared - {event_details['name']}"

    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
            
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
                color: #f1f5f9;
                min-height: 100vh;
                line-height: 1.6;
            }}
            
            .email-container {{
                max-width: 650px;
                margin: 40px auto;
                background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
                border-radius: 24px;
                overflow: hidden;
                box-shadow: 0 25px 50px rgba(0, 0, 0, 0.4);
                border: 1px solid rgba(59, 130, 246, 0.2);
            }}
            
            .header {{
                background: linear-gradient(135deg, #f59e0b, #d97706);
                padding: 40px;
                text-align: center;
                color: white;
            }}
            
            .content {{
                padding: 40px;
            }}
            
            .status-card {{
                background: rgba(245, 158, 11, 0.1);
                border: 1px solid rgba(245, 158, 11, 0.2);
                border-radius: 16px;
                padding: 32px;
                margin: 24px 0;
                text-align: center;
            }}
            
            .countdown-display {{
                background: linear-gradient(135deg, #f59e0b, #d97706);
                color: white;
                padding: 24px;
                border-radius: 16px;
                font-size: 1.5rem;
                font-weight: 800;
                margin: 24px 0;
            }}
            
            .footer {{
                background: rgba(15, 23, 42, 0.8);
                padding: 32px;
                text-align: center;
                border-top: 1px solid rgba(255, 255, 255, 0.1);
            }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <div class="header">
                <h1>🛡️ TicketVault</h1>
                <p>Secure Ticket Protection</p>
            </div>
            
            <div class="content">
                <h2 style="color: #f1f5f9; margin-bottom: 16px;">🎫 Tickets Being Prepared</h2>
                <p style="color: #cbd5e1; margin-bottom: 24px;">
                    Great news! <strong style="color: #f59e0b;">{seller_email}</strong> is preparing your tickets.
                </p>
                
                <div class="status-card">
                    <h3 style="color: #f1f5f9; margin-bottom: 16px;">📋 {event_details["name"]}</h3>
                    <p style="color: #cbd5e1; margin-bottom: 8px;"><strong>📍 Location:</strong> {event_details["location"]}</p>
                    <p style="color: #cbd5e1; margin-bottom: 16px;"><strong>📅 Date:</strong> {event_details["datetime"]}</p>
                    <div class="countdown-display">${price}</div>
                </div>
                
                <div style="background: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59, 130, 246, 0.2); border-radius: 16px; padding: 24px; margin: 24px 0; text-align: center;">
                    <h3 style="color: #3b82f6; margin-bottom: 12px;">⏰ Seller Has</h3>
                    <p style="font-size: 1.25rem; font-weight: 700; color: #f1f5f9;">{int(minutes_remaining)} minutes remaining</p>
                    <p style="color: #cbd5e1; font-size: 0.875rem; margin-top: 8px;">to send tickets to our secure system</p>
                </div>
                
                <div style="background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.2); border-radius: 16px; padding: 24px; margin: 32px 0;">
                    <h3 style="color: #10b981; margin-bottom: 16px;">📬 What Happens Next</h3>
                    <ul style="color: #cbd5e1; text-align: left; padding-left: 20px;">
                        <li>Seller sends tickets to our secure system</li>
                        <li>We verify tickets are authentic</li>
                        <li>You'll get a payment link (5 minutes to pay)</li>
                        <li>Tickets delivered instantly after payment</li>
                    </ul>
                </div>
            </div>
            
            <div class="footer">
                <p style="color: #94a3b8;">Transaction #{transaction_id}</p>
                <p style="color: #94a3b8; margin-top: 8px;">We'll notify you when tickets are ready!</p>
                <p style="font-weight: 700; color: #3b82f6; margin-top: 16px;">TicketVault</p>
            </div>
        </div>
    </body>
    </html>
    """

    # Use Mailgun sender instead of Flask-Mail to avoid context issues
    from insta485.mailgun_sender import mailgun_sender

    mailgun_sender.send_email(buyer_email, subject, html_body)


def send_ticket_deadline_reminder(
    transaction_id, seller_email, hours_remaining, ticket_email, event_name
):
    """Modern ticket deadline reminder"""
    details = {"ticket_email": ticket_email, "event_name": event_name}
    send_reminder_emails(
        transaction_id, seller_email, "ticket_deadline", hours_remaining, details
    )


def send_payment_deadline_reminder(
    transaction_id, buyer_email, hours_remaining, event_name, price
):
    """Modern payment deadline reminder"""
    details = {"event_name": event_name, "price": price}
    send_reminder_emails(
        transaction_id, buyer_email, "payment_deadline", hours_remaining, details
    )


def send_listing_expired_notification(
    transaction_id, seller_email, buyer_email, event_name, reason
):
    """Modern listing expiration notification"""
    send_expiration_notification(
        transaction_id, seller_email, buyer_email, event_name, reason
    )


def send_ticket_returned_notification(
    transaction_id, seller_email, buyer_email, event_name
):
    """Modern ticket return notification"""
    send_expiration_notification(
        transaction_id,
        seller_email,
        buyer_email,
        event_name,
        "buyer payment deadline exceeded",
    )


def send_payment_deadline_expired_emails(
    transaction_id, seller_email, buyer_email, event_name, price
):
    """Send notifications to both parties when payment deadline expires"""

    # Email to SELLER
    seller_subject = f"🔄 Payment Deadline Expired - Transaction #{transaction_id} | Ticket Will Be Returned"

    seller_html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
            
            body {{
                font-family: 'Inter', sans-serif;
                background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
                color: #f1f5f9;
                margin: 0;
                padding: 40px 20px;
            }}
            
            .notification-container {{
                max-width: 600px;
                margin: 0 auto;
                background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
                border-radius: 24px;
                overflow: hidden;
                box-shadow: 0 25px 50px rgba(0, 0, 0, 0.4);
                border: 1px solid rgba(239, 68, 68, 0.3);
            }}
            
            .notification-header {{
                background: linear-gradient(135deg, #ef4444, #dc2626);
                padding: 40px;
                text-align: center;
                color: white;
            }}
            
            .notification-content {{
                padding: 40px;
            }}
            
            .info-box {{
                background: rgba(59, 130, 246, 0.1);
                border-left: 4px solid #3b82f6;
                padding: 20px;
                margin: 20px 0;
                border-radius: 8px;
            }}
            
            .warning-box {{
                background: rgba(245, 158, 11, 0.1);
                border-left: 4px solid #f59e0b;
                padding: 20px;
                margin: 20px 0;
                border-radius: 8px;
            }}
            
            .action-button {{
                display: inline-block;
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: white;
                padding: 16px 32px;
                border-radius: 12px;
                text-decoration: none;
                font-weight: 700;
                margin: 20px 0;
            }}
        </style>
    </head>
    <body>
        <div class="notification-container">
            <div class="notification-header">
                <h1 style="margin: 0; font-size: 28px; font-weight: 800;">⏰ Payment Deadline Expired</h1>
                <p style="margin: 10px 0 0 0; font-size: 16px; opacity: 0.9;">Transaction #{transaction_id:06d}</p>
            </div>
            
            <div class="notification-content">
                <h2 style="color: #f59e0b; margin-top: 0;">Transaction Automatically Cancelled</h2>
                
                <p style="font-size: 16px; line-height: 1.6;">
                    The buyer did not complete payment within the 1-hour deadline for your ticket listing:
                </p>
                
                <div class="info-box">
                    <strong style="color: #3b82f6;">📋 Transaction Details:</strong><br>
                    <strong>Event:</strong> {event_name}<br>
                    <strong>Price:</strong> ${price}<br>
                    <strong>Buyer:</strong> {buyer_email}<br>
                    <strong>Status:</strong> <span style="color: #ef4444;">Payment Deadline Expired</span>
                </div>
                
                <div class="warning-box">
                    <strong style="color: #f59e0b;">🎫 What Happens Next:</strong><br><br>
                    <strong>TicketVault will automatically transfer your ticket back to you.</strong><br><br>
                    You should receive the ticket back at your Michigan Athletics account within the next few hours.<br><br>
                    Once you receive it back, you can:
                    <ul style="margin: 10px 0;">
                        <li>Create a new listing if the buyer is still interested</li>
                        <li>List it for a different buyer</li>
                        <li>Keep the ticket for yourself</li>
                    </ul>
                </div>
                
                <p style="font-size: 14px; color: #94a3b8; margin-top: 30px;">
                    <strong>Why did this happen?</strong><br>
                    The buyer didn't complete payment within our 1-hour payment window. This protects sellers by ensuring tickets aren't held indefinitely.
                </p>
                
                <p style="font-size: 14px; color: #94a3b8; margin-top: 20px;">
                    If you have any questions, please contact our support team.
                </p>
                
                <div style="text-align: center; margin-top: 40px;">
                    <a href="https://safetransaction.app/seller" class="action-button">View Dashboard</a>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

    # Email to BUYER
    buyer_subject = (
        f"⏰ Payment Deadline Expired - Transaction #{transaction_id} Cancelled"
    )

    buyer_html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
            
            body {{
                font-family: 'Inter', sans-serif;
                background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
                color: #f1f5f9;
                margin: 0;
                padding: 40px 20px;
            }}
            
            .notification-container {{
                max-width: 600px;
                margin: 0 auto;
                background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
                border-radius: 24px;
                overflow: hidden;
                box-shadow: 0 25px 50px rgba(0, 0, 0, 0.4);
                border: 1px solid rgba(239, 68, 68, 0.3);
            }}
            
            .notification-header {{
                background: linear-gradient(135deg, #ef4444, #dc2626);
                padding: 40px;
                text-align: center;
                color: white;
            }}
            
            .notification-content {{
                padding: 40px;
            }}
            
            .info-box {{
                background: rgba(59, 130, 246, 0.1);
                border-left: 4px solid #3b82f6;
                padding: 20px;
                margin: 20px 0;
                border-radius: 8px;
            }}
            
            .warning-box {{
                background: rgba(245, 158, 11, 0.1);
                border-left: 4px solid #f59e0b;
                padding: 20px;
                margin: 20px 0;
                border-radius: 8px;
            }}
        </style>
    </head>
    <body>
        <div class="notification-container">
            <div class="notification-header">
                <h1 style="margin: 0; font-size: 28px; font-weight: 800;">⏰ Payment Deadline Expired</h1>
                <p style="margin: 10px 0 0 0; font-size: 16px; opacity: 0.9;">Transaction #{transaction_id:06d}</p>
            </div>
            
            <div class="notification-content">
                <h2 style="color: #f59e0b; margin-top: 0;">Transaction Cancelled - Payment Window Closed</h2>
                
                <p style="font-size: 16px; line-height: 1.6;">
                    The payment deadline for this ticket transaction has expired:
                </p>
                
                <div class="info-box">
                    <strong style="color: #3b82f6;">📋 Transaction Details:</strong><br>
                    <strong>Event:</strong> {event_name}<br>
                    <strong>Price:</strong> ${price}<br>
                    <strong>Seller:</strong> {seller_email}<br>
                    <strong>Status:</strong> <span style="color: #ef4444;">Cancelled - Payment Not Received</span>
                </div>
                
                <div class="warning-box">
                    <strong style="color: #f59e0b;">❌ What This Means:</strong><br><br>
                    • The transaction has been automatically cancelled<br>
                    • The payment link is no longer valid<br>
                    • The ticket is being returned to the seller<br>
                    • No charges will be made to your account
                </div>
                
                <p style="font-size: 14px; color: #94a3b8; margin-top: 30px;">
                    <strong>Still interested in this ticket?</strong><br>
                    Contact the seller directly to arrange a new transaction. TicketVault protects sellers by limiting the payment window to 1 hour after ticket verification.
                </p>
                
                <p style="font-size: 14px; color: #94a3b8; margin-top: 20px;">
                    If you have any questions or if this was an error, please contact our support team.
                </p>
            </div>
        </div>
    </body>
    </html>
    """

    # Send emails using mailgun
    try:
        from insta485.mailgun_sender import send_email_mailgun

        # Send to seller
        send_email_mailgun(
            to_email=seller_email,
            subject=seller_subject,
            html_body=seller_html_body,
            text_body=f"Payment Deadline Expired - Transaction #{transaction_id}\n\nThe buyer did not complete payment within the deadline. The ticket will be automatically returned to your Michigan Athletics account.\n\nEvent: {event_name}\nPrice: ${price}\n\nYou can create a new listing once you receive the ticket back.",
        )
        logger.info(f"[PAYMENT-EXPIRED] Sent seller notification to {seller_email}")

        # Send to buyer
        send_email_mailgun(
            to_email=buyer_email,
            subject=buyer_subject,
            html_body=buyer_html_body,
            text_body=f"Payment Deadline Expired - Transaction #{transaction_id}\n\nThe payment deadline has expired and the transaction has been cancelled.\n\nEvent: {event_name}\nPrice: ${price}\n\nContact the seller if you're still interested in purchasing this ticket.",
        )
        logger.info(f"[PAYMENT-EXPIRED] Sent buyer notification to {buyer_email}")

    except Exception as e:
        logger.error(f"[PAYMENT-EXPIRED ERROR] Failed to send emails: {e}")
        raise


def send_payment_received_notification(
    transaction_id, seller_email, buyer_email, price, event_name, bonus_amount
):
    """Send notification to seller when they receive payment for a ticket sale"""

    subject = f"💰 Payment Received - ${price:.2f} + ${bonus_amount:.2f} Bonus! | Transaction #{transaction_id}"

    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
            
            body {{
                font-family: 'Inter', sans-serif;
                background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
                color: #f1f5f9;
                margin: 0;
                padding: 40px 20px;
            }}
            
            .notification-container {{
                max-width: 600px;
                margin: 0 auto;
                background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
                border-radius: 24px;
                overflow: hidden;
                box-shadow: 0 25px 50px rgba(0, 0, 0, 0.4);
                border: 1px solid rgba(16, 185, 129, 0.3);
            }}
            
            .notification-header {{
                background: linear-gradient(135deg, #10b981, #059669);
                padding: 40px;
                text-align: center;
                color: white;
            }}
            
            .notification-content {{
                padding: 40px;
            }}
            
            .success-box {{
                background: rgba(16, 185, 129, 0.1);
                border-left: 4px solid #10b981;
                padding: 20px;
                margin: 20px 0;
                border-radius: 8px;
            }}
            
            .amount-display {{
                text-align: center;
                padding: 30px;
                background: rgba(16, 185, 129, 0.15);
                border-radius: 16px;
                margin: 20px 0;
            }}
            
            .action-button {{
                display: inline-block;
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: white;
                padding: 16px 32px;
                border-radius: 12px;
                text-decoration: none;
                font-weight: 700;
                margin: 20px 0;
            }}
        </style>
    </head>
    <body>
        <div class="notification-container">
            <div class="notification-header">
                <h1 style="margin: 0; font-size: 32px; font-weight: 800;">🎉 Payment Received!</h1>
                <p style="margin: 10px 0 0 0; font-size: 18px; opacity: 0.95;">Transaction #{transaction_id:06d}</p>
            </div>
            
            <div class="notification-content">
                <h2 style="color: #10b981; margin-top: 0;">Funds Added to Your Balance</h2>
                
                <p style="font-size: 16px; line-height: 1.6;">
                    Great news! The buyer has completed payment for your ticket listing. Your funds have been added to your TicketVault balance.
                </p>
                
                <div class="amount-display">
                    <div style="font-size: 14px; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px;">Total Earnings</div>
                    <div style="font-size: 48px; font-weight: 900; color: #10b981; margin: 10px 0;">${(price + bonus_amount):.2f}</div>
                    <div style="font-size: 16px; color: #cbd5e1; margin-top: 10px;">
                        ${price:.2f} ticket price + <span style="color: #fbbf24; font-weight: 700;">${bonus_amount:.2f} bonus</span>
                    </div>
                </div>
                
                <div class="success-box">
                    <strong style="color: #10b981;">📋 Transaction Details:</strong><br>
                    <strong>Event:</strong> {event_name}<br>
                    <strong>Buyer:</strong> {buyer_email}<br>
                    <strong>Ticket Price:</strong> ${price:.2f}<br>
                    <strong>10% Bonus:</strong> <span style="color: #fbbf24;">+${bonus_amount:.2f}</span><br>
                    <strong>Total Credited:</strong> <span style="color: #10b981; font-weight: 700;">${(price + bonus_amount):.2f}</span>
                </div>
                
                <div style="background: rgba(59, 130, 246, 0.1); border-left: 4px solid #3b82f6; padding: 20px; margin: 20px 0; border-radius: 8px;">
                    <strong style="color: #3b82f6;">🎫 Next Steps:</strong><br><br>
                    • Ticket will be automatically transferred to buyer within 1 hour<br>
                    • Funds are now in your TicketVault balance<br>
                    • You can withdraw funds anytime from your dashboard<br>
                    • Want to sell more tickets? Create another listing!
                </div>
                
                <div style="text-align: center; margin-top: 30px;">
                    <a href="https://safetransaction.app/" class="action-button">
                        View Dashboard & Withdraw Funds
                    </a>
                </div>
                
                <p style="font-size: 14px; color: #94a3b8; margin-top: 30px; text-align: center;">
                    Thank you for using TicketVault!<br>
                    <a href="mailto:support@safetransaction.app" style="color: #3b82f6;">support@safetransaction.app</a>
                </p>
            </div>
        </div>
    </body>
    </html>
    """

    try:
        from insta485.mailgun_sender import send_email_mailgun

        send_email_mailgun(
            to_email=seller_email,
            subject=subject,
            html_body=html_body,
            text_body=f"Payment Received - Transaction #{transaction_id}\n\nGreat news! The buyer has completed payment.\n\nTotal Earnings: ${(price + bonus_amount):.2f}\n- Ticket Price: ${price:.2f}\n- 10% Bonus: +${bonus_amount:.2f}\n\nEvent: {event_name}\nBuyer: {buyer_email}\n\nFunds have been added to your balance. You can withdraw them anytime from your dashboard.",
        )
        logger.info(
            f"[PAYMENT-RECEIVED] Sent notification to {seller_email} for ${(price + bonus_amount):.2f}"
        )

    except Exception as e:
        logger.error(f"[PAYMENT-RECEIVED ERROR] Failed to send email: {e}")
        raise


def send_withdrawal_confirmation(
    user_email,
    amount,
    fee_amount,
    transfer_amount,
    transfer_id=None,
    payment_method=None,
    destination=None,
):
    """Send confirmation email when user withdraws funds"""

    # Determine method name for display
    if payment_method == "venmo":
        method_display = "Venmo"
    elif payment_method == "cashapp":
        method_display = "Cash App"
    elif payment_method == "stripe":
        method_display = "Bank Account"
    else:
        method_display = "Payment Method"

    subject = f"✅ Withdrawal Request Received - ${transfer_amount:.2f} to {destination if destination else method_display}"

    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
            
            body {{
                font-family: 'Inter', sans-serif;
                background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
                color: #f1f5f9;
                margin: 0;
                padding: 40px 20px;
            }}
            
            .notification-container {{
                max-width: 600px;
                margin: 0 auto;
                background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
                border-radius: 24px;
                overflow: hidden;
                box-shadow: 0 25px 50px rgba(0, 0, 0, 0.4);
                border: 1px solid rgba(59, 130, 246, 0.3);
            }}
            
            .notification-header {{
                background: linear-gradient(135deg, #3b82f6, #2563eb);
                padding: 40px;
                text-align: center;
                color: white;
            }}
            
            .notification-content {{
                padding: 40px;
            }}
            
            .info-box {{
                background: rgba(59, 130, 246, 0.1);
                border-left: 4px solid #3b82f6;
                padding: 20px;
                margin: 20px 0;
                border-radius: 8px;
            }}
            
            .amount-display {{
                text-align: center;
                padding: 30px;
                background: rgba(59, 130, 246, 0.15);
                border-radius: 16px;
                margin: 20px 0;
            }}
            
            .breakdown-row {{
                display: flex;
                justify-content: space-between;
                padding: 12px 0;
                border-bottom: 1px solid rgba(148, 163, 184, 0.2);
            }}
            
            .breakdown-total {{
                display: flex;
                justify-content: space-between;
                padding: 16px 0;
                font-weight: 700;
                font-size: 18px;
                color: #3b82f6;
                margin-top: 8px;
            }}
        </style>
    </head>
    <body>
        <div class="notification-container">
            <div class="notification-header">
                <h1 style="margin: 0; font-size: 32px; font-weight: 800;">💸 Withdrawal Confirmed</h1>
                <p style="margin: 10px 0 0 0; font-size: 16px; opacity: 0.95;">Funds are on their way!</p>
            </div>
            
            <div class="notification-content">
                <h2 style="color: #3b82f6; margin-top: 0;">Withdrawal Request Received</h2>
                
                <p style="font-size: 16px; line-height: 1.6;">
                    Your withdrawal request has been received and will be processed. The funds will be sent to:
                </p>
                
                {f'<div style="background: rgba(59, 130, 246, 0.1); border-left: 4px solid #3b82f6; padding: 16px; border-radius: 8px; margin: 20px 0;"><strong style="color: #3b82f6; font-size: 18px;">{method_display}: {destination}</strong></div>' if destination else ""}
                
                <div class="amount-display">
                    <div style="font-size: 14px; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px;">Amount You'll Receive</div>
                    <div style="font-size: 48px; font-weight: 900; color: #3b82f6; margin: 10px 0;">${transfer_amount:.2f}</div>
                </div>
                
                <div style="background: rgba(148, 163, 184, 0.1); padding: 24px; border-radius: 12px; margin: 20px 0;">
                    <strong style="color: #cbd5e1; font-size: 16px; margin-bottom: 16px; display: block;">Transaction Breakdown</strong>
                    
                    <div class="breakdown-row">
                        <span style="color: #94a3b8;">Withdrawal Amount</span>
                        <span style="color: #f1f5f9; font-weight: 600;">${amount:.2f}</span>
                    </div>
                    
                    <div class="breakdown-row">
                        <span style="color: #94a3b8;">TicketVault Fee (5%)</span>
                        <span style="color: #f59e0b; font-weight: 600;">-${fee_amount:.2f}</span>
                    </div>
                    
                    <div class="breakdown-total">
                        <span>Total Transferred</span>
                        <span style="color: #3b82f6;">${transfer_amount:.2f}</span>
                    </div>
                </div>
                
                <div style="background: rgba(239, 68, 68, 0.1); border-left: 4px solid #ef4444; padding: 20px; margin: 20px 0; border-radius: 8px;">
                    <strong style="color: #ef4444;">⚠️ CRITICAL - Made a Mistake?</strong><br><br>
                    <span style="color: #dc2626;">If you entered the wrong {method_display if method_display != "Bank Account" else "bank account"} and realize it IMMEDIATELY, email us at <strong><a href="mailto:support@safetransaction.app" style="color: #dc2626;">support@safetransaction.app</a></strong> right away!</span><br><br>
                    <span style="color: #991b1b; font-weight: 600;">⚠️ WARNING: If we already sent the money to the wrong account, there is NOTHING we can do to recover it. Contact us ASAP if you made an error!</span>
                </div>
                
                <div class="info-box">
                    <strong style="color: #3b82f6;">⏱️ What to Expect:</strong><br><br>
                    • Funds typically arrive within one business day<br>
                    • You'll receive an email when processed<br>
                    {f'• Request ID: <code style="background: rgba(255,255,255,0.1); padding: 2px 6px; border-radius: 4px;">{transfer_id}</code><br>' if transfer_id else ""}
                    • Check your {method_display if destination else "payment method"}
                </div>
                
                <div style="background: rgba(16, 185, 129, 0.1); border-left: 4px solid #10b981; padding: 20px; margin: 20px 0; border-radius: 8px;">
                    <strong style="color: #10b981;">💡 Pro Tip:</strong><br><br>
                    Keep selling tickets to earn more! Every completed sale includes a 10% bonus from TicketVault. The more you sell, the more you earn!
                </div>
                
                <p style="font-size: 14px; color: #94a3b8; margin-top: 30px; text-align: center;">
                    Questions about your withdrawal?<br>
                    Contact us at <a href="mailto:support@safetransaction.app" style="color: #3b82f6;">support@safetransaction.app</a>
                </p>
            </div>
        </div>
    </body>
    </html>
    """

    try:
        from insta485.mailgun_sender import send_email_mailgun

        send_email_mailgun(
            to_email=user_email,
            subject=subject,
            html_body=html_body,
            text_body=f"Withdrawal Request Received\n\nYour withdrawal request has been received.\n\nWithdrawal Amount: ${amount:.2f}\nTicketVault Fee (5%): -${fee_amount:.2f}\nTotal You'll Receive: ${transfer_amount:.2f}\n\n{f'Sending to {method_display}: {destination}' if destination else ''}\n\n⚠️ CRITICAL: If you entered the wrong {method_display if method_display != 'Bank Account' else 'bank account'}, email support@safetransaction.app IMMEDIATELY!\n\n⚠️ WARNING: If we already sent the money, there is NOTHING we can do to recover it.\n\nFunds typically arrive within one business day.{f' Request ID: {transfer_id}' if transfer_id else ''}\n\nThank you for using TicketVault!",
        )
        logger.info(
            f"[WITHDRAWAL-CONFIRMED] Sent notification to {user_email} for ${transfer_amount:.2f}"
        )

    except Exception as e:
        logger.error(f"[WITHDRAWAL-CONFIRMED ERROR] Failed to send email: {e}")
        raise


def send_withdrawal_completed_email(
    user_email,
    amount,
    fee_amount,
    transfer_amount,
    payment_method=None,
    destination=None,
):
    """Send email when withdrawal is completed/sent by admin"""

    # Determine method name for display
    if payment_method == "venmo":
        method_display = "Venmo"
    elif payment_method == "cashapp":
        method_display = "Cash App"
    elif payment_method == "stripe":
        method_display = "Bank Account (Stripe)"
    else:
        method_display = "Payment Method"

    subject = f"✅ Withdrawal Complete - ${transfer_amount:.2f} Sent to Your {method_display}!"

    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
            
            body {{
                font-family: 'Inter', sans-serif;
                background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
                color: #f1f5f9;
                margin: 0;
                padding: 40px 20px;
            }}
            
            .notification-container {{
                max-width: 600px;
                margin: 0 auto;
                background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
                border-radius: 24px;
                overflow: hidden;
                box-shadow: 0 25px 50px rgba(0, 0, 0, 0.4);
                border: 1px solid rgba(16, 185, 129, 0.3);
            }}
            
            .notification-header {{
                background: linear-gradient(135deg, #10b981, #059669);
                padding: 40px;
                text-align: center;
                color: white;
            }}
            
            .notification-content {{
                padding: 40px;
            }}
            
            .info-box {{
                background: rgba(16, 185, 129, 0.1);
                border-left: 4px solid #10b981;
                padding: 20px;
                margin: 20px 0;
                border-radius: 8px;
            }}
            
            .amount-display {{
                text-align: center;
                padding: 30px;
                background: rgba(16, 185, 129, 0.15);
                border-radius: 16px;
                margin: 20px 0;
            }}
            
            .breakdown-row {{
                display: flex;
                justify-content: space-between;
                padding: 12px 0;
                border-bottom: 1px solid rgba(148, 163, 184, 0.2);
            }}
            
            .breakdown-total {{
                display: flex;
                justify-content: space-between;
                padding: 16px 0;
                font-weight: 700;
                font-size: 18px;
                color: #10b981;
                margin-top: 8px;
            }}
        </style>
    </head>
    <body>
        <div class="notification-container">
            <div class="notification-header">
                <h1 style="margin: 0; font-size: 32px; font-weight: 800;">🎉 Money Sent!</h1>
                <p style="margin: 10px 0 0 0; font-size: 16px; opacity: 0.95;">Your withdrawal has been completed</p>
            </div>
            
            <div class="notification-content">
                <h2 style="color: #10b981; margin-top: 0;">✅ Withdrawal Completed Successfully</h2>
                
                <p style="font-size: 16px; line-height: 1.6;">
                    Great news! Your withdrawal has been processed and sent. The funds are on their way to:
                </p>
                
                {f'<div style="background: rgba(16, 185, 129, 0.1); border-left: 4px solid #10b981; padding: 16px; border-radius: 8px; margin: 20px 0;"><strong style="color: #10b981; font-size: 18px;">{method_display}: {destination}</strong></div>' if destination else ""}
                
                <div class="amount-display">
                    <div style="font-size: 14px; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px;">Amount Sent</div>
                    <div style="font-size: 48px; font-weight: 900; color: #10b981; margin: 10px 0;">${transfer_amount:.2f}</div>
                </div>
                
                <div style="background: rgba(148, 163, 184, 0.1); padding: 24px; border-radius: 12px; margin: 20px 0;">
                    <strong style="color: #cbd5e1; font-size: 16px; margin-bottom: 16px; display: block;">Transaction Summary</strong>
                    
                    <div class="breakdown-row">
                        <span style="color: #94a3b8;">Withdrawal Amount</span>
                        <span style="color: #f1f5f9; font-weight: 600;">${amount:.2f}</span>
                    </div>
                    
                    <div class="breakdown-row">
                        <span style="color: #94a3b8;">TicketVault Fee (5%)</span>
                        <span style="color: #f59e0b; font-weight: 600;">-${fee_amount:.2f}</span>
                    </div>
                    
                    <div class="breakdown-total">
                        <span>Total Sent to You</span>
                        <span style="color: #10b981;">${transfer_amount:.2f}</span>
                    </div>
                </div>
                
                <div class="info-box">
                    <strong style="color: #10b981;">💰 What to Expect Next:</strong><br><br>
                    {"• Check your Venmo app for the incoming payment<br>" if payment_method == "venmo" else ""}
                    {"• Check your Cash App for the incoming payment<br>" if payment_method == "cashapp" else ""}
                    {"• Check your bank account in 1-3 business days<br>" if payment_method == "stripe" else ""}
                    • The payment should appear {"instantly or within minutes" if payment_method in ["venmo", "cashapp"] else "within 1-3 business days"}<br>
                    • If you don't see it, check your spam/pending transactions<br>
                    • Contact us if you have any issues
                </div>
                
                <div style="background: rgba(59, 130, 246, 0.1); border-left: 4px solid #3b82f6; padding: 20px; margin: 20px 0; border-radius: 8px;">
                    <strong style="color: #3b82f6;">💡 Keep Earning!</strong><br><br>
                    Keep selling tickets to earn more! Remember: every completed sale includes a 10% bonus from TicketVault. The more you sell, the more you earn!
                </div>
                
                <p style="font-size: 14px; color: #94a3b8; margin-top: 30px; text-align: center;">
                    Questions about your withdrawal?<br>
                    Contact us at <a href="mailto:support@safetransaction.app" style="color: #3b82f6;">support@safetransaction.app</a>
                </p>
            </div>
        </div>
    </body>
    </html>
    """

    try:
        from insta485.mailgun_sender import send_email_mailgun

        send_email_mailgun(
            to_email=user_email,
            subject=subject,
            html_body=html_body,
            text_body=f"Withdrawal Completed!\n\nYour withdrawal has been processed and sent.\n\nWithdrawal Amount: ${amount:.2f}\nTicketVault Fee (5%): -${fee_amount:.2f}\nTotal Sent to You: ${transfer_amount:.2f}\n\n{f'Sent to {method_display}: {destination}' if destination else ''}\n\nThe payment should appear {'instantly or within minutes' if payment_method in ['venmo', 'cashapp'] else 'within 1-3 business days'}.\n\nThank you for using TicketVault!",
        )
        logger.info(
            f"[WITHDRAWAL-COMPLETED] Sent notification to {user_email} for ${transfer_amount:.2f}"
        )

    except Exception as e:
        logger.error(f"[WITHDRAWAL-COMPLETED ERROR] Failed to send email: {e}")
        raise
