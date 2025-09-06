"""
Modern email automation with ultra-sleek designs for Safe Transaction.
All emails redesigned with cutting-edge UI/UX.
"""

import insta485
from flask_mail import Message


def send_email(to_email, subject, html_content):
    """Base function to send emails with modern design"""
    msg = Message(subject=subject, recipients=[to_email], html=html_content)
    insta485.mail.send(msg)


def send_seller_instructions(transaction_id, seller_email, ticket_email, deadline, event_details):
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
                    <strong style="color: #10b981;">{event_details['name']}</strong> tickets.
                </p>
                
                <div class="deadline-critical">
                    <h3 style="margin-bottom: 8px;">⏰ MISSION DEADLINE</h3>
                    <div style="font-size: 1.5rem; font-weight: 900; margin: 8px 0;">{int(hours_remaining)} Hours Remaining</div>
                    <p style="font-size: 0.875rem; font-weight: 600;">
                        Expires: {deadline.strftime('%B %d, %Y at %I:%M %p')}
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
                <div style="font-weight: 800; color: #ef4444; font-size: 1.125rem; text-shadow: 0 0 20px rgba(239, 68, 68, 0.3);">SAFE TRANSACTION</div>
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


def send_expiration_notification(transaction_id, seller_email, buyer_email, event_name, reason):
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


def forward_ticket_email(to_email, original_email_data, transaction_id, return_mode=False):
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
                {original_email_data.get('html_content', original_email_data.get('text_content', 'Original ticket content'))}
            </div>
            
            <div class="delivery-footer">
                <div style="background: linear-gradient(135deg, #475569, #64748b); color: #f1f5f9; padding: 12px 24px; border-radius: 50px; font-family: 'JetBrains Mono', monospace; font-size: 14px; font-weight: 600; display: inline-block; margin: 16px 0; border: 1px solid rgba(255, 255, 255, 0.2);">TX-{transaction_id:06d}</div>
                <div style="color: #94a3b8; margin: 16px 0;">Secure delivery powered by Safe Transaction</div>
            </div>
        </div>
    </body>
    </html>
    """
    
    send_email(to_email, subject, html_body)


# Wrapper functions for compatibility
def send_buyer_notification(transaction_id, buyer_email, seller_email, price, event_details, payment_deadline=None):
    """Send modern, minimalistic buyer notification"""
    from datetime import datetime
    
    # Calculate payment deadline if provided
    payment_hours = None
    if payment_deadline:
        # Ensure payment_deadline is a datetime object
        if isinstance(payment_deadline, str):
            from datetime import datetime
            try:
                if 'T' in payment_deadline:
                    payment_deadline = datetime.fromisoformat(payment_deadline.replace('Z', '+00:00'))
                else:
                    payment_deadline = datetime.strptime(payment_deadline, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                payment_deadline = None
                
        if payment_deadline:
            payment_hours = max(0, (payment_deadline - datetime.now()).total_seconds() / 3600)
    
    # Format deadline text
    deadline_text = ""
    if payment_deadline:
        deadline_text = payment_deadline.strftime('%I:%M %p on %B %d')
    
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
                <div class="logo">Safe Transaction</div>
                <div class="tagline">Secure Ticket Protection</div>
            </div>
            
            <div class="content">
                <div class="section">
                    <div class="section-header">
                        <span style="font-size: 24px;">🎟️</span>
                        <h2>Ticket Verified & Available</h2>
                    </div>
                    <p class="section-text">
                        This ticket has been independently verified by Safe Transaction. It matches the event, date, and seat details listed below:
                    </p>
                </div>
                
                <div class="ticket-card">
                    <div class="ticket-header">
                        <div class="event-title">{event_details['name']}</div>
                        <div class="event-subtitle">Verified by Safe Transaction</div>
                    </div>
                    
                    <div class="ticket-details">
                        <div class="detail-grid">
                            <div class="detail-item">
                                <div class="detail-label">Location</div>
                                <div class="detail-value">{event_details['location']}</div>
                            </div>
                            <div class="detail-item">
                                <div class="detail-label">Date & Time</div>
                                <div class="detail-value">{event_details['datetime']}</div>
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
                    <a href="http://localhost:8000/pay/{transaction_id}" class="cta-button">
                        💳 Complete Secure Payment
                    </a>
                    <div class="reassurance">
                        If anything goes wrong, you'll get a full refund — guaranteed.
                    </div>
                    <a href="mailto:support@safetransaction.com?subject=Problem%20with%20Transaction%20{transaction_id}" class="problem-link">
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
                
                <!-- Why Use Safe Transaction Section -->
                <div class="section">
                    <div class="section-header">
                        <span style="font-size: 24px;">💡</span>
                        <h2>Why Use Safe Transaction?</h2>
                    </div>
                    <ul class="protection-list">
                        <li class="protection-item">
                            <div class="check-icon">
                                <span style="color: white; font-size: 12px; font-weight: bold;">✓</span>
                            </div>
                            Independent Ticket Verification
                        </li>
                        <li class="protection-item">
                            <div class="check-icon">
                                <span style="color: white; font-size: 12px; font-weight: bold;">✓</span>
                            </div>
                            Escrow Protection
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
            </div>
            
            <div class="footer-section">
                <div class="footer-text">Transaction ID: #{transaction_id}</div>
                <div class="footer-text">
                    Need help? <a href="mailto:support@safetransaction.com" class="footer-link">Contact Support</a>
                </div>
                <div class="footer-brand">Safe Transaction</div>
            </div>
        </div>
    </body>
    </html>
    """
    
    send_email(buyer_email, subject, html_body)


def send_modern_buyer_notification(transaction_id, buyer_email, seller_email, price, event_details, payment_deadline=None):
    """Send clean, modern buyer notification email"""
    from datetime import datetime
    
    # Calculate payment deadline if provided
    payment_hours = None
    if payment_deadline:
        # Ensure payment_deadline is a datetime object
        if isinstance(payment_deadline, str):
            try:
                if 'T' in payment_deadline:
                    payment_deadline = datetime.fromisoformat(payment_deadline.replace('Z', '+00:00'))
                else:
                    payment_deadline = datetime.strptime(payment_deadline, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                payment_deadline = None
                
        if payment_deadline:
            payment_hours = max(0, (payment_deadline - datetime.now()).total_seconds() / 3600)
    
    # Format deadline text
    deadline_text = ""
    if payment_deadline:
        deadline_text = payment_deadline.strftime('%I:%M %p on %B %d')
    
    subject = f"✅ Your {event_details['name']} Tickets Are Ready"
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background-color: #f8fafc;
                color: #1f2937;
                line-height: 1.5;
            }}
            
            .container {{
                max-width: 600px;
                margin: 0 auto;
                background: white;
                border-radius: 12px;
                overflow: hidden;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
            }}
            
            .header {{
                background: linear-gradient(135deg, #3b82f6, #1e40af);
                color: white;
                padding: 32px 24px;
                text-align: center;
            }}
            
            .header h1 {{
                font-size: 24px;
                font-weight: 700;
                margin-bottom: 8px;
            }}
            
            .header p {{
                opacity: 0.9;
                font-size: 16px;
            }}
            
            .content {{
                padding: 32px 24px;
            }}
            
            .event-card {{
                background: #f8fafc;
                border-radius: 8px;
                padding: 20px;
                margin: 24px 0;
                border-left: 4px solid #3b82f6;
            }}
            
            .event-name {{
                font-size: 20px;
                font-weight: 700;
                color: #1f2937;
                margin-bottom: 8px;
            }}
            
            .event-details {{
                color: #6b7280;
                font-size: 14px;
                line-height: 1.4;
            }}
            
            .price {{
                font-size: 32px;
                font-weight: 800;
                color: #059669;
                text-align: center;
                margin: 24px 0;
            }}
            
            {"" if not payment_deadline else f'''
            .countdown-box {{
                background: linear-gradient(135deg, #dc2626, #991b1b);
                color: white;
                padding: 20px;
                border-radius: 8px;
                text-align: center;
                margin: 24px 0;
            }}
            
            .countdown-label {{
                font-size: 14px;
                opacity: 0.9;
                margin-bottom: 8px;
                text-transform: uppercase;
                letter-spacing: 1px;
            }}
            
            .countdown-time {{
                font-size: 28px;
                font-weight: 700;
                font-family: 'Courier New', monospace;
                margin-bottom: 4px;
            }}
            
            .countdown-text {{
                font-size: 12px;
                opacity: 0.8;
            }}
            '''}
            
            .pay-button {{
                display: block;
                background: linear-gradient(135deg, #059669, #047857);
                color: white;
                text-decoration: none;
                padding: 16px 32px;
                border-radius: 8px;
                text-align: center;
                font-weight: 700;
                font-size: 18px;
                margin: 32px 0;
                transition: transform 0.2s ease;
            }}
            
            .pay-button:hover {{
                transform: translateY(-2px);
            }}
            
            .security-note {{
                background: #f0f9ff;
                border: 1px solid #bfdbfe;
                border-radius: 8px;
                padding: 16px;
                margin: 24px 0;
                font-size: 14px;
                color: #1e40af;
            }}
            
            .footer {{
                background: #f8fafc;
                padding: 24px;
                text-align: center;
                border-top: 1px solid #e5e7eb;
                font-size: 12px;
                color: #6b7280;
            }}
            
            @media (max-width: 600px) {{
                .container {{
                    margin: 16px;
                    border-radius: 8px;
                }}
                
                .header, .content, .footer {{
                    padding-left: 16px;
                    padding-right: 16px;
                }}
                
                .countdown-time {{
                    font-size: 24px;
                }}
                
                .pay-button {{
                    font-size: 16px;
                    padding: 14px 24px;
                }}
            }}
        </style>
        {"" if not payment_deadline else f'''
        <script>
            function startCountdown() {{
                const hoursRemaining = {payment_hours or 0};
                const totalSeconds = Math.max(0, hoursRemaining * 3600);
                const countdownElement = document.getElementById('countdown');
                
                if (!countdownElement || totalSeconds <= 0) return;
                
                let secondsLeft = totalSeconds;
                
                function updateDisplay() {{
                    const hours = Math.floor(secondsLeft / 3600);
                    const minutes = Math.floor((secondsLeft % 3600) / 60);
                    const seconds = secondsLeft % 60;
                    
                    countdownElement.innerHTML = 
                        String(hours).padStart(2, '0') + ':' +
                        String(minutes).padStart(2, '0') + ':' +
                        String(seconds).padStart(2, '0');
                    
                    if (secondsLeft <= 0) {{
                        countdownElement.innerHTML = 'EXPIRED';
                        return;
                    }}
                    
                    secondsLeft--;
                    setTimeout(updateDisplay, 1000);
                }}
                
                updateDisplay();
            }}
            
            window.onload = startCountdown;
        </script>
        '''}
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>✅ Tickets Verified</h1>
                <p>Your {event_details['name']} tickets are ready for purchase</p>
            </div>
            
            <div class="content">
                <div class="event-card">
                    <div class="event-name">{event_details['name']}</div>
                    <div class="event-details">
                        📍 {event_details.get('location', 'Venue TBD')}<br>
                        📅 {event_details.get('datetime', 'Date TBD')}<br>
                        ✅ Tickets verified and secured in escrow
                    </div>
                </div>
                
                <div class="price">${price}</div>
                
                {"" if not payment_deadline else f'''
                <div class="countdown-box">
                    <div class="countdown-label">Payment Window Closes In</div>
                    <div class="countdown-time" id="countdown">--:--:--</div>
                    <div class="countdown-text">Complete payment before {deadline_text}</div>
                </div>
                '''}
                
                <a href="http://localhost:8000/pay/{transaction_id}" class="pay-button">
                    💳 Pay Now - ${price}
                </a>
                
                <div class="security-note">
                    🛡️ <strong>Protected Transaction:</strong> Your payment is held securely until tickets are delivered. 
                    Full refund guaranteed if tickets are not as described.
                </div>
            </div>
            
            <div class="footer">
                Transaction #{transaction_id} • <a href="mailto:support@safetransaction.com">Support</a><br>
                Safe Transaction - Secure Ticket Marketplace
            </div>
        </div>
    </body>
    </html>
    """
    
    send_email(buyer_email, subject, html_body)


def send_buyer_waiting_notification(transaction_id, buyer_email, seller_email, price, event_details, ticket_deadline):
    """Send notification to buyer that seller is preparing tickets"""
    from datetime import datetime
    
    # Calculate time remaining for seller
    if isinstance(ticket_deadline, str):
        ticket_deadline = datetime.fromisoformat(ticket_deadline.replace('Z', '+00:00'))
    
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
                <h1>🛡️ Safe Transaction</h1>
                <p>Secure Ticket Protection</p>
            </div>
            
            <div class="content">
                <h2 style="color: #f1f5f9; margin-bottom: 16px;">🎫 Tickets Being Prepared</h2>
                <p style="color: #cbd5e1; margin-bottom: 24px;">
                    Great news! <strong style="color: #f59e0b;">{seller_email}</strong> is preparing your tickets.
                </p>
                
                <div class="status-card">
                    <h3 style="color: #f1f5f9; margin-bottom: 16px;">📋 {event_details['name']}</h3>
                    <p style="color: #cbd5e1; margin-bottom: 8px;"><strong>📍 Location:</strong> {event_details['location']}</p>
                    <p style="color: #cbd5e1; margin-bottom: 16px;"><strong>📅 Date:</strong> {event_details['datetime']}</p>
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
                <p style="font-weight: 700; color: #3b82f6; margin-top: 16px;">Safe Transaction</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    send_email(buyer_email, subject, html_body)


def send_ticket_deadline_reminder(transaction_id, seller_email, hours_remaining, ticket_email, event_name):
    """Modern ticket deadline reminder"""
    details = {"ticket_email": ticket_email, "event_name": event_name}
    send_reminder_emails(transaction_id, seller_email, "ticket_deadline", hours_remaining, details)


def send_payment_deadline_reminder(transaction_id, buyer_email, hours_remaining, event_name, price):
    """Modern payment deadline reminder"""
    details = {"event_name": event_name, "price": price}
    send_reminder_emails(transaction_id, buyer_email, "payment_deadline", hours_remaining, details)


def send_listing_expired_notification(transaction_id, seller_email, buyer_email, event_name, reason):
    """Modern listing expiration notification"""
    send_expiration_notification(transaction_id, seller_email, buyer_email, event_name, reason)


def send_ticket_returned_notification(transaction_id, seller_email, buyer_email, event_name):
    """Modern ticket return notification"""
    send_expiration_notification(transaction_id, seller_email, buyer_email, event_name, "buyer payment deadline exceeded")
