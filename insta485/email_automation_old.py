"""
Email automation for the transaction system
"""
import json
from flask_mail import Message
import insta485


def send_seller_instructions(transaction_id, seller_email, ticket_email, deadline, event_details):
    """Send comprehensive seller instructions with all timing details"""
    # Calculate hours remaining
    from datetime import datetime
    hours_remaining = max(0, (deadline - datetime.now()).total_seconds() / 3600)
    
    subject = f"🎫 Action Required: Send Your Tickets - {event_details['name']}"
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #28a745, #20c997); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: white; padding: 30px; border: 1px solid #ddd; border-radius: 0 0 10px 10px; }}
            .urgent-box {{ background: #fff3cd; border: 2px solid #ffc107; padding: 20px; border-radius: 8px; margin: 20px 0; }}
            .instruction-box {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #007bff; }}
            .email-highlight {{ background: #e7f3ff; padding: 15px; border-radius: 8px; font-family: monospace; font-size: 18px; text-align: center; border: 2px solid #007bff; }}
            .timeline-box {{ background: #d1ecf1; padding: 20px; border-radius: 8px; border-left: 4px solid #0dcaf0; }}
            .warning-box {{ background: #f8d7da; padding: 15px; border-radius: 8px; border-left: 4px solid #dc3545; margin: 20px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎫 Safe Transaction</h1>
                <p>Listing Created Successfully!</p>
            </div>
            <div class="content">
                <h2>Hi {seller_email}! 👋</h2>
                <p>Your listing for <strong>{event_details['name']}</strong> has been created and the buyer has been notified!</p>
                
                <div class="urgent-box">
                    <h3>⏰ TIME SENSITIVE ACTION REQUIRED</h3>
                    <p><strong>You have {int(hours_remaining)} hours and {int((hours_remaining % 1) * 60)} minutes</strong> to send your tickets</p>
                    <p><strong>Deadline:</strong> {deadline.strftime('%A, %B %d, %Y at %I:%M %p')}</p>
                </div>
                
                <div style="background: linear-gradient(135deg, #dc3545, #c82333); color: white; padding: 25px; border-radius: 8px; margin: 20px 0; text-align: center;">
                    <h3>🚨 CRITICAL: DO NOT SEND TICKETS DIRECTLY TO BUYER!</h3>
                    <p style="font-size: 16px;">Send to our secure system instead ↓</p>
                </div>
                
                <div class="instruction-box" style="border: 3px solid #dc3545;">
                    <h3>📧 STEP 1: Forward Your Ticket Email to Our System</h3>
                    <p><strong>⚠️ NEVER send tickets directly to the buyer!</strong> Forward your original ticket email (from Ticketmaster, StubHub, etc.) to our secure address:</p>
                    <div class="email-highlight" style="border: 3px solid #dc3545; background: #ffe6e6;">
                        {ticket_email}
                    </div>
                    <div style="background: #fff3cd; padding: 15px; border-radius: 8px; margin: 15px 0; border: 2px solid #ffc107;">
                        <h4>⚠️ CRITICAL REMINDERS:</h4>
                        <ul style="text-align: left; margin: 10px 0;">
                            <li><strong>Copy this email exactly:</strong> {ticket_email}</li>
                            <li><strong>Forward the ENTIRE email</strong> with all attachments</li>
                            <li><strong>Double-check the address</strong> before sending</li>
                            <li><strong>NEVER send directly to buyer</strong> - payment isn't guaranteed until our system processes it</li>
                        </ul>
                    </div>
                </div>
                
                <div class="timeline-box">
                    <h3>📋 What Happens Next</h3>
                    <ol>
                        <li><strong>You forward ticket email</strong> → We verify authenticity (instant)</li>
                        <li><strong>Buyer gets payment notification</strong> → They have time to pay</li>
                        <li><strong>Buyer pays</strong> → Funds held securely in escrow</li>
                        <li><strong>Tickets auto-forwarded to buyer</strong> → Instant delivery</li>
                        <li><strong>You get paid</strong> → Funds released after 24 hours (or buyer confirmation)</li>
                    </ol>
                </div>
                
                <div class="warning-box">
                    <h3>⚠️ Important: If Deadline is Missed</h3>
                    <p>If you don't send your tickets by the deadline:</p>
                    <ul>
                        <li>Your listing will automatically cancel</li>
                        <li>The buyer will be notified it's no longer available</li>
                        <li>No money changes hands - completely clean closure</li>
                        <li>You can create a new listing anytime</li>
                    </ul>
                </div>
                
                <div style="background: #d4edda; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3>🛡️ Your Payment is 100% Guaranteed!</h3>
                    <p>Once the buyer pays, your money is secured in escrow. We guarantee you'll receive payment - no risk of chargebacks or scams!</p>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <p><strong>Transaction ID:</strong> #{transaction_id}</p>
                    <p>Questions? Reply to this email for instant support!</p>
                </div>
                
                <p>Best regards,<br>The Safe Transaction Team</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    msg = Message(subject=subject, recipients=[seller_email], html=html_body)
    insta485.mail.send(msg)


def send_buyer_notification(transaction_id, buyer_email, seller_email, price, event_details, payment_deadline=None):
    """Send ultra-modern, sleek buyer notification"""
    from datetime import datetime
    
    # Calculate payment deadline if provided
    payment_hours = None
    if payment_deadline:
        payment_hours = max(0, (payment_deadline - datetime.now()).total_seconds() / 3600)
    
    subject = f"⚡ Exclusive Ticket Drop - {event_details['name']} | Limited Access"
    
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
                line-height: 1.6;
                color: #f1f5f9;
                background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
                min-height: 100vh;
            }}
            
            .email-container {{
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
                border: 1px solid rgba(59, 130, 246, 0.2);
            }}
            
            .hero-header {{
                background: linear-gradient(135deg, #3b82f6 0%, #1e40af 50%, #6366f1 100%);
                padding: 50px 40px;
                text-align: center;
                position: relative;
                overflow: hidden;
            }}
            
            .hero-header::before {{
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: 
                    radial-gradient(circle at 20% 80%, rgba(255, 255, 255, 0.1) 0%, transparent 50%),
                    radial-gradient(circle at 80% 20%, rgba(255, 255, 255, 0.1) 0%, transparent 50%),
                    linear-gradient(45deg, transparent 40%, rgba(255, 255, 255, 0.05) 50%, transparent 60%);
                animation: shimmer 3s ease-in-out infinite;
            }}
            
            @keyframes shimmer {{
                0%, 100% {{ opacity: 0.8; }}
                50% {{ opacity: 1; }}
            }}
            
            .hero-header h1 {{
                font-size: 2.5rem;
                font-weight: 900;
                margin-bottom: 12px;
                position: relative;
                z-index: 1;
                text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
                letter-spacing: -0.02em;
            }}
            
            .hero-header p {{
                font-size: 1.25rem;
                opacity: 0.95;
                position: relative;
                z-index: 1;
                font-weight: 500;
            }}
            
            .content {{
                padding: 50px 40px;
            }}
            
            .greeting {{
                font-size: 1.75rem;
                font-weight: 800;
                color: #f1f5f9;
                margin-bottom: 20px;
                background: linear-gradient(135deg, #3b82f6, #10b981);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }}
            
            .seller-badge {{
                background: linear-gradient(135deg, #475569, #64748b);
                padding: 24px;
                border-radius: 20px;
                margin: 30px 0;
                border: 1px solid rgba(255, 255, 255, 0.1);
                position: relative;
                overflow: hidden;
            }}
            
            .seller-badge::before {{
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: linear-gradient(45deg, transparent, rgba(59, 130, 246, 0.1), transparent);
                transform: translateX(-100%);
                animation: slide 2s ease-in-out infinite;
            }}
            
            @keyframes slide {{
                0% {{ transform: translateX(-100%); }}
                100% {{ transform: translateX(100%); }}
            }}
            
            .seller-badge p {{
                position: relative;
                z-index: 1;
                color: #cbd5e1;
                margin-bottom: 8px;
                font-weight: 500;
            }}
            
            .seller-name {{
                position: relative;
                z-index: 1;
                font-size: 1.25rem;
                font-weight: 700;
                color: #3b82f6;
                text-shadow: 0 0 20px rgba(59, 130, 246, 0.3);
            }}
            
            .event-showcase {{
                background: linear-gradient(135deg, #475569 0%, #64748b 100%);
                padding: 40px;
                border-radius: 24px;
                margin: 40px 0;
                border: 1px solid rgba(255, 255, 255, 0.1);
                position: relative;
                overflow: hidden;
            }}
            
            .event-showcase::before {{
                content: '';
                position: absolute;
                top: -50%;
                left: -50%;
                width: 200%;
                height: 200%;
                background: radial-gradient(circle, rgba(59, 130, 246, 0.1) 0%, transparent 70%);
                animation: rotate 20s linear infinite;
            }}
            
            @keyframes rotate {{
                0% {{ transform: rotate(0deg); }}
                100% {{ transform: rotate(360deg); }}
            }}
            
            .event-title {{
                position: relative;
                z-index: 1;
                font-size: 2rem;
                font-weight: 900;
                color: #f1f5f9;
                margin-bottom: 24px;
                text-align: center;
                text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
            }}
            
            .event-meta {{
                position: relative;
                z-index: 1;
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
                margin: 30px 0;
            }}
            
            .meta-item {{
                background: rgba(15, 23, 42, 0.6);
                padding: 20px;
                border-radius: 16px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                text-align: center;
            }}
            
            .meta-label {{
                color: #94a3b8;
                font-size: 0.875rem;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                margin-bottom: 8px;
            }}
            
            .meta-value {{
                color: #f1f5f9;
                font-size: 1.125rem;
                font-weight: 700;
            }}
            
            .price-spotlight {{
                position: relative;
                z-index: 1;
                background: linear-gradient(135deg, #10b981, #059669);
                padding: 30px;
                border-radius: 20px;
                text-align: center;
                margin: 30px 0;
                box-shadow: 
                    0 20px 40px rgba(16, 185, 129, 0.3),
                    inset 0 1px 0 rgba(255, 255, 255, 0.2);
                position: relative;
                overflow: hidden;
            }}
            
            .price-spotlight::before {{
                content: '';
                position: absolute;
                top: -2px;
                left: -2px;
                right: -2px;
                bottom: -2px;
                background: linear-gradient(45deg, #10b981, #3b82f6, #10b981);
                border-radius: 20px;
                z-index: -1;
                animation: borderPulse 2s ease-in-out infinite;
            }}
            
            @keyframes borderPulse {{
                0%, 100% {{ opacity: 0.6; }}
                50% {{ opacity: 1; }}
            }}
            
            .price-amount {{
                font-size: 3rem;
                font-weight: 900;
                color: white;
                text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
                letter-spacing: -0.02em;
            }}
            
            {"" if not payment_deadline else f'''
            .countdown-alert {{
                background: linear-gradient(135deg, #ef4444, #dc2626);
                padding: 25px;
                border-radius: 16px;
                margin: 30px 0;
                text-align: center;
                border: 1px solid rgba(255, 255, 255, 0.1);
                animation: pulse 2s ease-in-out infinite;
            }}
            
            @keyframes pulse {{
                0%, 100% {{ transform: scale(1); }}
                50% {{ transform: scale(1.02); }}
            }}
            
            .countdown-title {{
                font-size: 1.25rem;
                font-weight: 800;
                color: white;
                margin-bottom: 12px;
                text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
            }}
            
            .countdown-time {{
                font-size: 1.5rem;
                font-weight: 900;
                color: white;
                text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
            }}
            
            .countdown-warning {{
                font-size: 0.875rem;
                color: rgba(255, 255, 255, 0.9);
                margin-top: 8px;
                font-weight: 500;
            }}
            '''}
            
            .cta-zone {{
                text-align: center;
                margin: 50px 0;
            }}
            
            .cta-button {{
                display: inline-block;
                background: linear-gradient(135deg, #10b981 0%, #059669 50%, #3b82f6 100%);
                color: white;
                padding: 20px 50px;
                text-decoration: none;
                border-radius: 50px;
                font-weight: 800;
                font-size: 1.25rem;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                transition: all 0.3s ease;
                box-shadow: 
                    0 15px 35px rgba(16, 185, 129, 0.4),
                    inset 0 1px 0 rgba(255, 255, 255, 0.2);
                position: relative;
                overflow: hidden;
            }}
            
            .cta-button::before {{
                content: '';
                position: absolute;
                top: 0;
                left: -100%;
                width: 100%;
                height: 100%;
                background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
                transition: all 0.6s ease;
            }}
            
            .cta-button:hover::before {{
                left: 100%;
            }}
            
            .security-fortress {{
                background: linear-gradient(135deg, #064e3b, #065f46);
                padding: 40px;
                border-radius: 20px;
                margin: 40px 0;
                border: 1px solid rgba(16, 185, 129, 0.3);
                position: relative;
            }}
            
            .security-title {{
                font-size: 1.5rem;
                font-weight: 800;
                color: #10b981;
                margin-bottom: 24px;
                text-align: center;
                text-shadow: 0 0 20px rgba(16, 185, 129, 0.5);
            }}
            
            .security-grid {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
            }}
            
            .security-item {{
                background: rgba(16, 185, 129, 0.1);
                padding: 20px;
                border-radius: 12px;
                border: 1px solid rgba(16, 185, 129, 0.2);
            }}
            
            .security-icon {{
                width: 40px;
                height: 40px;
                background: linear-gradient(135deg, #10b981, #059669);
                border-radius: 10px;
                display: flex;
                align-items: center;
                justify-content: center;
                margin-bottom: 12px;
                font-size: 18px;
            }}
            
            .security-label {{
                font-weight: 700;
                color: #10b981;
                margin-bottom: 4px;
                font-size: 0.875rem;
            }}
            
            .security-desc {{
                color: #a7f3d0;
                font-size: 0.875rem;
                line-height: 1.4;
            }}
            
            .process-flow {{
                background: linear-gradient(135deg, #1e40af, #3730a3);
                padding: 40px;
                border-radius: 20px;
                margin: 40px 0;
                border: 1px solid rgba(59, 130, 246, 0.3);
            }}
            
            .process-title {{
                font-size: 1.5rem;
                font-weight: 800;
                color: #60a5fa;
                margin-bottom: 30px;
                text-align: center;
                text-shadow: 0 0 20px rgba(96, 165, 250, 0.5);
            }}
            
            .process-steps {{
                display: grid;
                gap: 20px;
            }}
            
            .process-step {{
                background: rgba(59, 130, 246, 0.1);
                padding: 20px;
                border-radius: 16px;
                border: 1px solid rgba(59, 130, 246, 0.2);
                position: relative;
                padding-left: 60px;
            }}
            
            .step-number {{
                position: absolute;
                left: 20px;
                top: 50%;
                transform: translateY(-50%);
                width: 30px;
                height: 30px;
                background: linear-gradient(135deg, #3b82f6, #1e40af);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: 800;
                color: white;
                font-size: 14px;
            }}
            
            .step-content {{
                color: #bfdbfe;
                font-weight: 500;
                line-height: 1.5;
            }}
            
            .urgency-pulse {{
                background: linear-gradient(135deg, #f59e0b, #d97706);
                padding: 30px;
                border-radius: 16px;
                margin: 40px 0;
                text-align: center;
                border: 1px solid rgba(245, 158, 11, 0.3);
                animation: urgencyPulse 1.5s ease-in-out infinite;
            }}
            
            @keyframes urgencyPulse {{
                0%, 100% {{ box-shadow: 0 0 0 0 rgba(245, 158, 11, 0.4); }}
                50% {{ box-shadow: 0 0 0 20px rgba(245, 158, 11, 0); }}
            }}
            
            .urgency-title {{
                font-size: 1.25rem;
                font-weight: 800;
                color: white;
                margin-bottom: 12px;
            }}
            
            .urgency-text {{
                color: rgba(255, 255, 255, 0.9);
                font-weight: 600;
            }}
            
            .footer-zone {{
                background: rgba(15, 23, 42, 0.8);
                padding: 40px;
                text-align: center;
                border-top: 1px solid rgba(255, 255, 255, 0.1);
            }}
            
            .transaction-chip {{
                background: linear-gradient(135deg, #475569, #64748b);
                color: #f1f5f9;
                padding: 12px 24px;
                border-radius: 50px;
                font-family: 'JetBrains Mono', monospace;
                font-size: 14px;
                font-weight: 600;
                display: inline-block;
                margin: 20px 0;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }}
            
            .support-text {{
                color: #94a3b8;
                margin: 20px 0;
                font-weight: 500;
            }}
            
            .brand-signature {{
                font-weight: 800;
                color: #3b82f6;
                font-size: 1.125rem;
                margin-top: 16px;
                text-shadow: 0 0 20px rgba(59, 130, 246, 0.3);
            }}
            
            .trust-badge {{
                color: #64748b;
                font-size: 0.875rem;
                margin-top: 8px;
                font-weight: 500;
            }}
            
            @media (max-width: 600px) {{
                .email-container {{
                    margin: 20px;
                    border-radius: 16px;
                }}
                
                .hero-header, .content {{
                    padding: 30px 20px;
                }}
                
                .event-meta, .security-grid {{
                    grid-template-columns: 1fr;
                }}
                
                .price-amount {{
                    font-size: 2.5rem;
                }}
                
                .cta-button {{
                    padding: 16px 32px;
                    font-size: 1.125rem;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <div class="hero-header">
                <h1>🚀 SAFE TRANSACTION</h1>
                <p>Ultra-Secure Ticket Ecosystem</p>
            </div>
            
            <div class="content">
                <div class="greeting">Exclusive Access Granted 🎯</div>
                
                <div class="seller-badge">
                    <p><strong>Premium ticket offer secured from verified seller:</strong></p>
                    <div class="seller-name">{seller_email}</div>
                </div>
                
                <div class="event-showcase">
                    <div class="event-title">🎫 {event_details['name']}</div>
                    <div class="event-meta">
                        <div class="meta-item">
                            <div class="meta-label">📍 Venue</div>
                            <div class="meta-value">{event_details['location']}</div>
                        </div>
                        <div class="meta-item">
                            <div class="meta-label">📅 Event Date</div>
                            <div class="meta-value">{event_details['datetime']}</div>
                        </div>
                    </div>
                    <div class="price-spotlight">
                        <div class="price-amount">${price}</div>
                    </div>
                </div>
                
                {"" if not payment_deadline else f'''
                <div class="countdown-alert">
                    <div class="countdown-title">⏰ LIMITED TIME WINDOW</div>
                    <div class="countdown-time">{int(payment_hours)}h {int((payment_hours % 1) * 60)}m remaining</div>
                    <div class="countdown-warning">Secure your tickets before time expires</div>
                </div>
                '''}
                
                <div class="cta-zone">
                    <a href="http://localhost:8000/ticket/{transaction_id}" class="cta-button">
                        🔒 SECURE ACCESS NOW
                    </a>
                </div>
                
                <div class="security-fortress">
                    <div class="security-title">🛡️ MILITARY-GRADE PROTECTION</div>
                    <div class="security-grid">
                        <div class="security-item">
                            <div class="security-icon">🔐</div>
                            <div class="security-label">Escrow Shield</div>
                            <div class="security-desc">Funds secured until delivery confirmed</div>
                        </div>
                        <div class="security-item">
                            <div class="security-icon">⚡</div>
                            <div class="security-label">Instant Transfer</div>
                            <div class="security-desc">Tickets delivered within seconds</div>
                        </div>
                        <div class="security-item">
                            <div class="security-icon">🕰️</div>
                            <div class="security-label">24h Safety Net</div>
                            <div class="security-desc">Full verification window guaranteed</div>
                        </div>
                        <div class="security-item">
                            <div class="security-icon">💯</div>
                            <div class="security-label">Zero Risk</div>
                            <div class="security-desc">Complete refund if issues arise</div>
                        </div>
                    </div>
                </div>
                
                <div class="process-flow">
                    <div class="process-title">⚡ LIGHTNING-FAST PROCESS</div>
                    <div class="process-steps">
                        <div class="process-step">
                            <div class="step-number">1</div>
                            <div class="step-content"><strong>AI Verification</strong> → Tickets authenticated by advanced algorithms</div>
                        </div>
                        <div class="process-step">
                            <div class="step-number">2</div>
                            <div class="step-content"><strong>Secure Payment</strong> → Funds locked in bank-grade escrow vault</div>
                        </div>
                        <div class="process-step">
                            <div class="step-number">3</div>
                            <div class="step-content"><strong>Instant Delivery</strong> → Tickets transmitted to your inbox immediately</div>
                        </div>
                        <div class="process-step">
                            <div class="step-number">4</div>
                            <div class="step-content"><strong>Seller Payout</strong> → Automatic release after 24h or your approval</div>
                        </div>
                    </div>
                </div>
                
                <div class="urgency-pulse">
                    <div class="urgency-title">⚡ EXCLUSIVE LIMITED ACCESS</div>
                    <div class="urgency-text">This premium offer expires when the seller's allocation runs out</div>
                </div>
            </div>
            
            <div class="footer-zone">
                <div class="transaction-chip">TX-{transaction_id:06d}</div>
                <div class="support-text">Need assistance? Reply for instant VIP support</div>
                <div class="brand-signature">SAFE TRANSACTION</div>
                <div class="trust-badge">Trusted by 10,000+ users worldwide</div>
            </div>
        </div>
    </body>
    </html>
    """
    
    msg = Message(subject=subject, recipients=[buyer_email], html=html_body)
    insta485.mail.send(msg)


def forward_ticket_email(to_email, original_email_data, transaction_id, return_mode=False):
    """Forward ticket email to buyer or return to seller"""
    try:
        if return_mode:
            subject = f"🔄 TICKET RETURNED - {original_email_data['subject']}"
            header = """
            <div style="background: #f8d7da; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #dc3545;">
                <h3>🔄 TICKET RETURNED BY SAFE TRANSACTION</h3>
                <p><strong>Reason:</strong> Payment deadline expired - buyer did not complete payment</p>
                <p>Your ticket has been safely returned to you. You can create a new listing anytime!</p>
                <p><strong>Transaction ID:</strong> #{transaction_id}</p>
            </div>
            """
        else:
            subject = f"🎫 TICKETS DELIVERED - {original_email_data['subject']}"
            header = """
            <div style="background: #d4edda; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #28a745;">
                <h3>✅ TICKETS DELIVERED VIA SAFE TRANSACTION</h3>
                <p><strong>Your payment is protected!</strong> You have 24 hours to verify these tickets.</p>
                <p>If there are any issues, contact us immediately for a full refund.</p>
                <p><strong>Transaction ID:</strong> #{transaction_id}</p>
            </div>
            """
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                {header}
                <hr style="margin: 30px 0; border: 1px solid #ddd;">
                <h3>Original Ticket Email:</h3>
                {original_email_data.get('html_body', original_email_data['body'])}
            </div>
        </body>
        </html>
        """
        
        msg = Message(subject=subject, recipients=[to_email], html=html_body)
        insta485.mail.send(msg)
        return True
        
    except Exception as e:
        print(f"Error forwarding email: {e}")
        return False


def send_ticket_deadline_reminder(transaction_id, seller_email, hours_remaining, ticket_email, event_name):
    """Send reminder to seller about approaching ticket deadline"""
    urgency = "URGENT" if hours_remaining <= 2 else "REMINDER"
    subject = f"⏰ {urgency}: Send Your Tickets - {hours_remaining} Hours Left!"
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .urgent-header {{ background: linear-gradient(135deg, #dc3545, #c82333); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: white; padding: 30px; border: 1px solid #ddd; border-radius: 0 0 10px 10px; }}
            .countdown-box {{ background: #fff3cd; border: 2px solid #ffc107; padding: 20px; border-radius: 8px; margin: 20px 0; text-align: center; }}
            .action-box {{ background: #e7f3ff; padding: 20px; border-radius: 8px; border-left: 4px solid #007bff; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="urgent-header">
                <h1>⏰ TIME RUNNING OUT!</h1>
                <p>Action Required for Your Ticket Listing</p>
            </div>
            <div class="content">
                <h2>Hi {seller_email}!</h2>
                
                <div class="countdown-box">
                    <h3>🚨 ONLY {int(hours_remaining)} HOURS LEFT!</h3>
                    <p>Your ticket deadline for <strong>{event_name}</strong> is approaching fast!</p>
                </div>
                
                <div class="action-box">
                    <h3>📧 ACTION REQUIRED: Forward Your Tickets NOW</h3>
                    <p>Send your ticket email to:</p>
                    <div style="background: #fff; padding: 15px; border-radius: 8px; font-family: monospace; font-size: 18px; text-align: center; border: 2px solid #007bff; margin: 10px 0;">
                        {ticket_email}
                    </div>
                </div>
                
                <div style="background: #f8d7da; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <h3>⚠️ What Happens If You Miss the Deadline:</h3>
                    <ul>
                        <li>Your listing will automatically cancel</li>
                        <li>The buyer will be notified it's no longer available</li>
                        <li>You'll need to create a new listing</li>
                    </ul>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <p><strong>Transaction ID:</strong> #{transaction_id}</p>
                </div>
                
                <p>Best regards,<br>The Safe Transaction Team</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    msg = Message(subject=subject, recipients=[seller_email], html=html_body)
    insta485.mail.send(msg)


def send_payment_deadline_reminder(transaction_id, buyer_email, hours_remaining, event_name, price):
    """Send reminder to buyer about approaching payment deadline"""
    urgency = "URGENT" if hours_remaining <= 4 else "REMINDER"
    subject = f"⏰ {urgency}: Complete Payment - {event_name} ({int(hours_remaining)} Hours Left)"
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .urgent-header {{ background: linear-gradient(135deg, #ffc107, #e0a800); color: #333; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: white; padding: 30px; border: 1px solid #ddd; border-radius: 0 0 10px 10px; }}
            .countdown-box {{ background: #fff3cd; border: 2px solid #ffc107; padding: 20px; border-radius: 8px; margin: 20px 0; text-align: center; }}
            .cta-button {{ display: inline-block; background: #28a745; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="urgent-header">
                <h1>⏰ Payment Deadline Approaching!</h1>
                <p>Don't Miss Out on Your Tickets</p>
            </div>
            <div class="content">
                <h2>Hi there!</h2>
                
                <div class="countdown-box">
                    <h3>🚨 ONLY {int(hours_remaining)} HOURS LEFT!</h3>
                    <p>Complete your payment for <strong>{event_name}</strong> before it's too late!</p>
                    <p><strong>Price: ${price}</strong></p>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="http://localhost:8000/ticket/{transaction_id}" class="cta-button">
                        💳 Complete Payment Now
                    </a>
                </div>
                
                <div style="background: #f8d7da; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <h3>⚠️ What Happens If You Miss the Deadline:</h3>
                    <ul>
                        <li>The tickets will be returned to the seller</li>
                        <li>You'll lose the opportunity to purchase</li>
                        <li>The seller can relist to other buyers</li>
                    </ul>
                </div>
                
                <div style="background: #d4edda; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <h3>🛡️ Your Payment is Protected</h3>
                    <p>Remember: Your money is held in escrow and protected until you receive valid tickets!</p>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <p><strong>Transaction ID:</strong> #{transaction_id}</p>
                </div>
                
                <p>Best regards,<br>The Safe Transaction Team</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    msg = Message(subject=subject, recipients=[buyer_email], html=html_body)
    insta485.mail.send(msg)


def send_listing_expired_notification(transaction_id, seller_email, buyer_email, event_name, reason):
    """Send notifications when listing expires"""
    
    # Email to seller
    seller_subject = f"❌ Listing Expired - {event_name}"
    seller_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: #6c757d; color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: white; padding: 30px; border: 1px solid #ddd; border-radius: 0 0 10px 10px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📋 Listing Status Update</h1>
                <p>Transaction Expired</p>
            </div>
            <div class="content">
                <h2>Hi {seller_email}!</h2>
                
                <div style="background: #f8d7da; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3>❌ Your listing for {event_name} has expired</h3>
                    <p><strong>Reason:</strong> Ticket deadline passed without receiving your tickets</p>
                </div>
                
                <div style="background: #e2e3e5; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <h3>What This Means:</h3>
                    <ul>
                        <li>Your listing has been automatically cancelled</li>
                        <li>The buyer has been notified it's no longer available</li>
                        <li>No money was involved - clean closure</li>
                    </ul>
                </div>
                
                <div style="background: #d1ecf1; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <h3>🎯 Want to Try Again?</h3>
                    <p>You can create a new listing anytime! Just make sure to send your tickets within the deadline next time.</p>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <p><strong>Transaction ID:</strong> #{transaction_id}</p>
                </div>
                
                <p>Best regards,<br>The Safe Transaction Team</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Email to buyer
    buyer_subject = f"📋 Listing No Longer Available - {event_name}"
    buyer_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: #6c757d; color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: white; padding: 30px; border: 1px solid #ddd; border-radius: 0 0 10px 10px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📋 Listing Update</h1>
                <p>Offer No Longer Available</p>
            </div>
            <div class="content">
                <h2>Hi there!</h2>
                
                <div style="background: #fff3cd; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3>📋 The listing for {event_name} is no longer available</h3>
                    <p><strong>Reason:</strong> The seller did not send their tickets within the deadline</p>
                </div>
                
                <div style="background: #e2e3e5; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <h3>What This Means:</h3>
                    <ul>
                        <li>This specific offer has been cancelled</li>
                        <li>No payment was processed</li>
                        <li>You can look for other listings</li>
                    </ul>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <p><strong>Transaction ID:</strong> #{transaction_id}</p>
                </div>
                
                <p>Best regards,<br>The Safe Transaction Team</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Send both emails
    msg_seller = Message(subject=seller_subject, recipients=[seller_email], html=seller_html)
    msg_buyer = Message(subject=buyer_subject, recipients=[buyer_email], html=buyer_html)
    
    insta485.mail.send(msg_seller)
    insta485.mail.send(msg_buyer)


def send_ticket_returned_notification(transaction_id, seller_email, buyer_email, event_name):
    """Send notifications when tickets are returned due to payment deadline"""
    
    # Email to seller
    seller_subject = f"🔄 Tickets Returned - {event_name}"
    seller_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #6c757d, #5a6268); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: white; padding: 30px; border: 1px solid #ddd; border-radius: 0 0 10px 10px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔄 Tickets Returned</h1>
                <p>Payment Deadline Expired</p>
            </div>
            <div class="content">
                <h2>Hi {seller_email}!</h2>
                
                <div style="background: #fff3cd; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3>🔄 Your tickets for {event_name} have been returned</h3>
                    <p><strong>Reason:</strong> The buyer did not complete payment within the deadline</p>
                </div>
                
                <div style="background: #d4edda; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <h3>✅ Good News:</h3>
                    <ul>
                        <li>Your tickets have been safely returned to you</li>
                        <li>You can create a new listing anytime</li>
                        <li>Look for the returned ticket email in your inbox</li>
                    </ul>
                </div>
                
                <div style="background: #d1ecf1; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <h3>🎯 Next Steps:</h3>
                    <p>You can create a new listing with different timing settings or find another buyer!</p>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <p><strong>Transaction ID:</strong> #{transaction_id}</p>
                </div>
                
                <p>Best regards,<br>The Safe Transaction Team</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Email to buyer
    buyer_subject = f"⏰ Payment Deadline Missed - {event_name}"
    buyer_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: #dc3545; color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: white; padding: 30px; border: 1px solid #ddd; border-radius: 0 0 10px 10px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>⏰ Payment Deadline Missed</h1>
                <p>Opportunity Expired</p>
            </div>
            <div class="content">
                <h2>Hi there!</h2>
                
                <div style="background: #f8d7da; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3>⏰ You missed the payment deadline for {event_name}</h3>
                    <p>The tickets have been returned to the seller and are no longer available to you.</p>
                </div>
                
                <div style="background: #e2e3e5; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <h3>What Happened:</h3>
                    <ul>
                        <li>The payment deadline expired</li>
                        <li>The tickets were automatically returned to the seller</li>
                        <li>The seller can now relist them</li>
                    </ul>
                </div>
                
                <div style="background: #d1ecf1; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <h3>💡 For Future Purchases:</h3>
                    <p>Make sure to complete payment within the deadline to secure your tickets!</p>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <p><strong>Transaction ID:</strong> #{transaction_id}</p>
                </div>
                
                <p>Best regards,<br>The Safe Transaction Team</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Send both emails
    msg_seller = Message(subject=seller_subject, recipients=[seller_email], html=seller_html)
    msg_buyer = Message(subject=buyer_subject, recipients=[buyer_email], html=buyer_html)
    
    insta485.mail.send(msg_seller)
    insta485.mail.send(msg_buyer)
