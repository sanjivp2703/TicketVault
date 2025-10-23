
"""
Mailgun Email Sender for Safe Transaction
Handles all email sending with proper routing and templates
"""

import requests
import json
from datetime import datetime, timedelta
import insta485

class MailgunSender:
    """Handles email sending via Mailgun with proper routing"""
    
    def __init__(self):
        # Use Flask app configuration
        self.base_url = insta485.app.config['MAILGUN_BASE_URL']
        self.api_key = insta485.app.config['MAILGUN_API_KEY']
        self.domain = insta485.app.config['MAILGUN_DOMAIN']
    
    def send_email(self, to_email, subject, html_content, from_name="Safe Transaction"):
        """Send email via Mailgun with professional sender"""
        url = f"{self.base_url}/messages"
        
        # Use professional sender email that looks legitimate
        data = {
            'from': f'{from_name} <hello@{self.domain}>',  # Changed from noreply to hello - more friendly and trustworthy
            'to': to_email,
            'subject': subject,
            'html': html_content,
            # Headers to help prevent spam filtering
            'h:Reply-To': f'support@{self.domain}',  # Allow replies to go to support
            'h:X-Mailgun-Track-Clicks': 'yes',
            'h:X-Mailgun-Track-Opens': 'yes'
        }
        
        try:
            response = requests.post(
                url,
                auth=('api', self.api_key),
                data=data,
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"✅ Email sent to {to_email}: {subject}")
                return True
            else:
                print(f"❌ Email failed to {to_email}: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Email error to {to_email}: {e}")
            return False
    
    def send_seller_verification_success(self, seller_email, transaction_id, event_name, buyer_email, payment_deadline):
        """Send modern sale completion email to seller based on buyer payment design"""
        import insta485
        
        # Get transaction price from database
        connection = insta485.model.get_db()
        transaction = connection.execute(
            "SELECT price FROM transactions WHERE transaction_id = ?",
            (transaction_id,)
        ).fetchone()
        
        if not transaction:
            print(f"❌ Transaction {transaction_id} not found")
            return False
            
        ticket_price = float(transaction['price'])
        bonus_amount = ticket_price * 0.10  # 10% bonus
        total_amount = ticket_price + bonus_amount
        
        subject = f"🎉 Your sale is complete! - {event_name}"
        
        html_content = f"""
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
                
                .hero-card {{
                    background: #ffffff;
                    border-radius: 16px;
                    margin: 32px 0;
                    padding: 32px;
                    border: 1px solid #e5e7eb;
                    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
                    text-align: center;
                }}
                
                .hero-title {{
                    font-size: 20px;
                    font-weight: 700;
                    color: #222222;
                    margin-bottom: 8px;
                    line-height: 1.3;
                }}
                
                .hero-subtitle {{
                    font-size: 14px;
                    color: #717171;
                    font-weight: 400;
                    margin-bottom: 24px;
                }}
               
                .amount-card {{
                    background: #ffffff;
                    border-radius: 16px;
                    margin: 32px 0;
                    padding: 32px;
                    border: 1px solid #e5e7eb;
                    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
                }}
               
                .amount-header {{
                    padding: 0 0 24px 0;
                    border-bottom: 1px solid #f1f3f4;
                    margin-bottom: 32px;
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
                
                .bonus-highlight {{
                    background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
                    color: white;
                    padding: 4px 12px;
                    border-radius: 8px;
                    font-size: 12px;
                    font-weight: 700;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                    display: inline-block;
                    margin-left: 8px;
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
                   
                    .hero-card {{
                        margin: 32px 0;
                    }}
                   
                    .amount-card {{
                        margin: 32px 0;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="email-container">
                <div class="header">
                    <div class="logo">Safe Transaction</div>
                    <div class="tagline">Your sale is complete!</div>
                </div>
                
                <div class="content">
                    <!-- Section 1: Congratulations -->
                    <div class="section">
                        <div class="section-header">
                            <span style="font-size: 24px; margin-right: 12px;">🎉</span>
                            <h2 style="font-size: 24px; font-weight: 800; color: #059669; margin: 0;">Congratulations, your ticket has sold!</h2>
                    </div>
                        <p style="color: #222222; margin-bottom: 32px; line-height: 1.6; font-size: 18px; font-weight: 500;">
                            The buyer's payment is secured in your balance on SafeTransaction. We'll send your ticket to them shortly.
                        </p>
                       
                        <div class="amount-card">
                            <div class="detail-grid">
                                <div class="detail-item">
                                    <div class="detail-label">Ticket Price</div>
                                    <div class="detail-value">${ticket_price:.2f}</div>
                                </div>
                                <div class="detail-item">
                                    <div class="detail-label">Our 10% Bonus <span class="bonus-highlight">On Us!</span></div>
                                    <div class="detail-value">${bonus_amount:.2f}</div>
                                </div>
                                <div class="detail-item">
                                    <div class="detail-label">Total Earned</div>
                                    <div class="detail-value price">${total_amount:.2f}</div>
                                </div>
                                <div class="detail-item">
                                    <div class="detail-label">Status</div>
                                    <div class="detail-value">Available for Withdrawal</div>
                                </div>
                            </div>
                    </div>
                    
                        <!-- Payment Button Container -->
                        <div class="payment-container">
                            <p style="color: #059669; font-size: 18px; font-weight: 700; margin: 0 0 16px 0; text-align: center;">
                                ✨ Withdraw Your Balance Now
                            </p>
                            <div class="cta-section">
                                <a href="http://localhost:8000/withdraw" class="cta-button">
                                    💰 Withdraw Your Balance Now
                                </a>
                        </div>
                        </div>
                        </div>
                   
                    <!-- Section 2: What happens next -->
                    <div class="section">
                        <div class="section-header">
                            <span style="font-size: 24px; margin-right: 12px;">📋</span>
                            <h2 style="font-size: 22px; font-weight: 700; color: #222222; margin: 0;">Here's what happens next:</h2>
                        </div>
                        <div class="protection-section">
                            <ul class="protection-list">
                                <li class="protection-item">
                                    <div class="check-icon">
                                        <span style="color: white; font-size: 12px; font-weight: bold;">✓</span>
                                    </div>
                                    Your Balance - Withdraw Your Balance Now
                                </li>
                                <li class="protection-item">
                                    <div class="check-icon">
                                        <span style="color: white; font-size: 12px; font-weight: bold;">✓</span>
                                    </div>
                                    Ticket Transfer - We'll forward your ticket to the buyer within the hour.
                                </li>
                                <li class="protection-item">
                                    <div class="check-icon">
                                        <span style="color: white; font-size: 12px; font-weight: bold;">✓</span>
                                    </div>
                                    Your Bonus - We've added a +10% bonus on us — thanks for selling with Safe Transaction!
                                </li>
                            </ul>
                        </div>
                    </div>
                    
                    <!-- Section 3: Extra Reassurance -->
                    <div class="section">
                        <div class="section-header">
                            <span style="font-size: 20px; margin-right: 8px;">🛡️</span>
                            <h2 style="font-size: 20px; font-weight: 700; color: #222222; margin: 0;">Extra Reassurance</h2>
                        </div>
                        <ul class="protection-list">
                            <li class="protection-item">
                                <div class="check-icon">
                                    <span style="color: white; font-size: 12px; font-weight: bold;">✓</span>
                                </div>
                                Funds are securely held and protected from chargebacks
                            </li>
                            <li class="protection-item">
                                <div class="check-icon">
                                    <span style="color: white; font-size: 12px; font-weight: bold;">✓</span>
                                </div>
                                Withdraw anytime to your bank account
                            </li>
                            <li class="protection-item">
                                <div class="check-icon">
                                    <span style="color: white; font-size: 12px; font-weight: bold;">✓</span>
                                </div>
                                Full customer protection and support
                            </li>
                        </ul>
                    </div>
                   
                    <!-- Section 4: Support Information -->
                    <div style="text-align: center; margin: 32px 0;">
                        <div class="help-text">
                            Questions? We're here to help! If something goes wrong, let us know and we'll attempt to make it right.
                        </div>
                        <a href="mailto:support@safetransaction.app" class="help-link">
                            💬 Contact our support team 24/7
                        </a>
                    </div>
                </div>
                
                <div class="footer-section">
                    <div class="footer-text">Transaction ID: #{transaction_id:06d}</div>
                    <div class="footer-text">
                        Need help? <a href="mailto:support@safetransaction.app" class="footer-link">Contact Support</a>
                    </div>
                    <div class="footer-brand">Safe Transaction</div>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(seller_email, subject, html_content)
    
    def send_seller_verification_failed(self, seller_email, transaction_id, event_name, reason):
        """Send verification failure email to seller"""
        subject = f"❌ Ticket Verification Failed - TX-{transaction_id:06d} | {event_name}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f8fafc; margin: 0; padding: 20px; }}
                .container {{ background: white; max-width: 600px; margin: 0 auto; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }}
                .header {{ background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); color: white; padding: 30px; text-align: center; }}
                .content {{ padding: 30px; }}
                .error-badge {{ background: #fef2f2; border: 2px solid #ef4444; color: #dc2626; padding: 15px; border-radius: 8px; text-align: center; margin: 20px 0; }}
                .info-box {{ background: #fff7ed; border-left: 4px solid #f97316; padding: 20px; margin: 20px 0; }}
                .action-box {{ background: #f0f9ff; border: 2px solid #0ea5e9; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .footer {{ background: #f8fafc; padding: 20px; text-align: center; color: #6b7280; }}
                .button {{ background: #3b82f6; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block; margin: 10px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>⚠️ Ticket Verification Failed</h1>
                    <p>Transaction #{transaction_id:06d}</p>
                </div>
                
                <div class="content">
                    <div class="error-badge">
                        <strong>❌ VERIFICATION FAILED</strong><br>
                        Your ticket could not be verified automatically
                    </div>
                    
                    <div class="info-box">
                        <h3>📋 Issue Details</h3>
                        <p><strong>Event:</strong> {event_name}</p>
                        <p><strong>Reason:</strong> {reason}</p>
                        <p><strong>Status:</strong> Ticket returned - listing cancelled</p>
                    </div>
                    
                    <div class="action-box">
                        <h3>🔧 What You Can Do</h3>
                        <ul>
                            <li><strong>Check ticket details:</strong> Ensure event name, date, and venue match exactly</li>
                            <li><strong>Verify ticket format:</strong> Make sure it's a valid ticket (PDF, image, or email)</li>
                            <li><strong>Create new listing:</strong> Try again with corrected information</li>
                            <li><strong>Contact support:</strong> If you believe this is an error</li>
                        </ul>
                    </div>
                    
                    <div class="info-box">
                        <h3>🛡️ Security Notice</h3>
                        <p>Our automated system protects buyers from invalid or fraudulent tickets. This verification failure helps maintain platform trust and security.</p>
                    </div>
                </div>
                
                <div class="footer">
                    <p>🎯 Safe Transaction - Automated Ticket Platform</p>
                    <p>Transaction ID: {transaction_id:06d} | Secure & Automated</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(seller_email, subject, html_content)
    
    # REMOVED: send_buyer_payment_notification - now using send_modern_buyer_notification from email_automation.py
    def send_buyer_payment_notification(self, buyer_email, transaction_id, event_name, event_location, event_datetime, price, payment_deadline, payment_url):
        """Send payment notification to buyer"""
        subject = f"🎫 Secure Payment Required - {event_name} | TX-{transaction_id:06d}"
        
        deadline_str = payment_deadline.strftime('%B %d, %Y at %I:%M %p') if payment_deadline else "24 hours"
        event_date_str = event_datetime.strftime('%B %d, %Y at %I:%M %p') if isinstance(event_datetime, datetime) else str(event_datetime)
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f8fafc; margin: 0; padding: 20px; }}
                .container {{ background: white; max-width: 600px; margin: 0 auto; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }}
                .header {{ background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%); color: white; padding: 30px; text-align: center; }}
                .content {{ padding: 30px; }}
                .ticket-info {{ background: #f0f9ff; border: 2px solid #3b82f6; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .price-box {{ background: #10b981; color: white; padding: 20px; border-radius: 8px; text-align: center; margin: 20px 0; }}
                .security-box {{ background: #ecfdf5; border-left: 4px solid #10b981; padding: 20px; margin: 20px 0; }}
                .warning-box {{ background: #fef3c7; border-left: 4px solid #f59e0b; padding: 20px; margin: 20px 0; }}
                .footer {{ background: #f8fafc; padding: 20px; text-align: center; color: #6b7280; }}
                .pay-button {{ background: #10b981; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; display: inline-block; margin: 20px 0; font-weight: bold; font-size: 16px; }}
                .pay-button:hover {{ background: #059669; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎫 Verified Ticket Available!</h1>
                    <p>Secure Payment Required</p>
                </div>
                
                <div class="content">
                    <div class="ticket-info">
                        <h3>🎪 Event Details</h3>
                        <p><strong>Event:</strong> {event_name}</p>
                        <p><strong>Location:</strong> {event_location}</p>
                        <p><strong>Date & Time:</strong> {event_date_str}</p>
                        <p><strong>Transaction ID:</strong> #{transaction_id:06d}</p>
                    </div>
                    
                    <div class="price-box">
                        <h2>💰 Total: ${price:.2f}</h2>
                        <p>Secure payment via Stripe</p>
                    </div>
                    
                    <!-- Payment Button - Multiple formats for compatibility -->
                    <div style="text-align: center; margin: 30px 0;">
                        <!-- Primary Button -->
                        <table cellpadding="0" cellspacing="0" border="0" style="margin: 0 auto;">
                            <tr>
                                <td style="background: #10b981; border-radius: 8px; padding: 0;">
                                    <a href="{payment_url}" style="background: #10b981; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; display: block; font-weight: bold; font-size: 16px; border: none; font-family: Arial, sans-serif;">
                                        🔒 Pay Securely Now
                                    </a>
                                </td>
                            </tr>
                        </table>
                        
                        <!-- Fallback Text Link -->
                        <p style="margin-top: 20px; font-size: 14px; color: #6b7280;">
                            Button not working? Copy and paste this link into your browser:<br>
                            <a href="{payment_url}" style="color: #3b82f6; text-decoration: underline; word-break: break-all;">
                                {payment_url}
                            </a>
                        </p>
                    </div>
                    
                    <div class="security-box">
                        <h3>🛡️ Your Protection</h3>
                        <ul>
                            <li><strong>Verified Ticket:</strong> Automatically verified against original listing</li>
                            <li><strong>Secure Payment:</strong> Protected by Stripe encryption</li>
                            <li><strong>Instant Delivery:</strong> Ticket delivered immediately after payment</li>
                            <li><strong>Full Refund:</strong> If ticket is invalid or event cancelled</li>
                        </ul>
                    </div>
                    
                    <div class="warning-box">
                        <h3>⏰ Payment Deadline</h3>
                        <p><strong>You must complete payment by: {deadline_str}</strong></p>
                        <p>After this deadline, the ticket will be returned to the seller and this offer will expire.</p>
                    </div>
                    
                    <div class="security-box">
                        <h3>📋 What Happens After Payment</h3>
                        <ol>
                            <li>Payment processed securely via Stripe</li>
                            <li>Ticket delivered to your email immediately</li>
                            <li>Funds held in escrow until event completion</li>
                            <li>Seller paid after successful event attendance</li>
                        </ol>
                    </div>
                </div>
                
                <div class="footer">
                    <p>🎯 Safe Transaction - Automated Ticket Platform</p>
                    <p>Transaction ID: {transaction_id:06d} | Secure & Automated</p>
                    <p><em>This is a secure, verified ticket offer</em></p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(buyer_email, subject, html_content)
    
    def send_ticket_to_buyer(self, buyer_email, transaction_id, event_name, seller_email):
        """Send ticket to buyer after payment"""
        subject = f"🎫 Your Tickets - {event_name} | TX-{transaction_id:06d}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f8fafc; margin: 0; padding: 20px; }}
                .container {{ background: white; max-width: 600px; margin: 0 auto; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }}
                .header {{ background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; padding: 30px; text-align: center; }}
                .content {{ padding: 30px; }}
                .ticket-box {{ background: #ecfdf5; border: 2px solid #10b981; padding: 20px; border-radius: 8px; margin: 20px 0; text-align: center; }}
                .success-box {{ background: #d1fae5; border-left: 4px solid #10b981; padding: 20px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 Payment Complete!</h1>
                    <p>Your tickets have been delivered</p>
                </div>
                
                <div class="content">
                    <div class="success-box">
                        <h3>✅ Transaction Complete</h3>
                        <p><strong>Event:</strong> {event_name}</p>
                        <p><strong>Transaction ID:</strong> #{transaction_id:06d}</p>
                        <p><strong>Seller:</strong> {seller_email}</p>
                    </div>
                    
                    <div class="ticket-box">
                        <h2>🎫 Your Tickets</h2>
                        <p><strong>The seller's original ticket email has been automatically forwarded to you.</strong></p>
                        <p>Check your inbox for the ticket details and entry instructions.</p>
                    </div>
                    
                    <div class="success-box">
                        <h3>🛡️ You're Protected</h3>
                        <ul>
                            <li>✅ Ticket verified before purchase</li>
                            <li>✅ Secure payment processed</li>
                            <li>✅ Original ticket forwarded</li>
                            <li>✅ Full support available</li>
                        </ul>
                    </div>
                    
                    <p style="text-align: center; color: #6b7280; margin-top: 30px;">
                        Enjoy the event! 🎉<br>
                        - Safe Transaction Team
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(buyer_email, subject, html_content)
    
    def send_seller_payment_received(self, seller_email, transaction_id, event_name, amount, buyer_email):
        """Send payment notification to seller"""
        subject = f"💰 Payment Received - {event_name} | TX-{transaction_id:06d}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f8fafc; margin: 0; padding: 20px; }}
                .container {{ background: white; max-width: 600px; margin: 0 auto; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }}
                .header {{ background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; padding: 30px; text-align: center; }}
                .content {{ padding: 30px; }}
                .money-box {{ background: #10b981; color: white; padding: 20px; border-radius: 8px; text-align: center; margin: 20px 0; }}
                .success-box {{ background: #d1fae5; border-left: 4px solid #10b981; padding: 20px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>💰 Payment Received!</h1>
                    <p>Your ticket sale is complete</p>
                </div>
                
                <div class="content">
                    <div class="money-box">
                        <h2>💵 ${amount:.2f} Added to Balance</h2>
                        <p>Available for withdrawal</p>
                    </div>
                    
                    <div class="success-box">
                        <h3>✅ Sale Complete</h3>
                        <p><strong>Event:</strong> {event_name}</p>
                        <p><strong>Buyer:</strong> {buyer_email}</p>
                        <p><strong>Transaction ID:</strong> #{transaction_id:06d}</p>
                    </div>
                    
                    <div class="success-box">
                        <h3>🎯 What Happened</h3>
                        <ul>
                            <li>✅ Buyer completed secure payment</li>
                            <li>✅ Your ticket was automatically forwarded</li>
                            <li>✅ Funds added to your account balance</li>
                            <li>✅ Ready for withdrawal anytime</li>
                        </ul>
                    </div>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="http://localhost:8000/balance" style="background: #10b981; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; display: inline-block; font-weight: bold; font-size: 16px;">
                            💰 View Balance & Withdraw
                        </a>
                    </div>
                    
                    <p style="text-align: center; color: #6b7280; margin-top: 30px;">
                        Thanks for using Safe Transaction! 🎉<br>
                        - Safe Transaction Team
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(seller_email, subject, html_content)
    
    def send_seller_instructions(self, seller_email, transaction_id, ticket_email, event_name, deadline):
        """Send ticket submission instructions to seller"""
        subject = f"📧 Send Your Ticket - TX-{transaction_id:06d} | {event_name}"
        
        deadline_str = deadline.strftime('%B %d, %Y at %I:%M %p') if deadline else "24 hours"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f8fafc; margin: 0; padding: 20px; }}
                .container {{ background: white; max-width: 600px; margin: 0 auto; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }}
                .header {{ background: linear-gradient(135deg, #7c3aed 0%, #5b21b6 100%); color: white; padding: 30px; text-align: center; }}
                .content {{ padding: 30px; }}
                .instruction-box {{ background: #f0f9ff; border: 2px solid #3b82f6; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .email-box {{ background: #1f2937; color: #f9fafb; padding: 20px; border-radius: 8px; text-align: center; margin: 20px 0; font-family: monospace; }}
                .warning-box {{ background: #fef3c7; border-left: 4px solid #f59e0b; padding: 20px; margin: 20px 0; }}
                .footer {{ background: #f8fafc; padding: 20px; text-align: center; color: #6b7280; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📧 Send Your Ticket Now</h1>
                    <p>Transaction #{transaction_id:06d}</p>
                </div>
                
                <div class="content">
                    <div class="instruction-box">
                        <h3>🎯 Next Step: Forward Your Ticket</h3>
                        <p><strong>Event:</strong> {event_name}</p>
                        <p><strong>Deadline:</strong> {deadline_str}</p>
                    </div>
                    
                    <div class="email-box">
                        <h3>📧 Send Your Ticket To:</h3>
                        <div style="font-size: 18px; font-weight: bold; margin: 10px 0;">
                            {ticket_email}
                        </div>
                        <p style="font-size: 12px; opacity: 0.8;">Copy this email address exactly</p>
                    </div>
                    
                    <div class="instruction-box">
                        <h3>📋 How to Send Your Ticket</h3>
                        <ol>
                            <li><strong>Forward your original ticket email</strong> to the address above</li>
                            <li><strong>Or attach ticket files</strong> (PDF, images, screenshots)</li>
                            <li><strong>Include any confirmation numbers</strong> or booking references</li>
                            <li><strong>Send from the same email</strong> you used to create this listing</li>
                        </ol>
                    </div>
                    
                    <div class="warning-box">
                        <h3>⚠️ Important Requirements</h3>
                        <ul>
                            <li>Ticket details must match your listing exactly</li>
                            <li>Must be sent before {deadline_str}</li>
                            <li>Only valid, transferable tickets accepted</li>
                            <li>Verification is automatic - you'll get confirmation within minutes</li>
                        </ul>
                    </div>
                    
                    <div class="instruction-box">
                        <h3>🚀 What Happens Next</h3>
                        <ol>
                            <li>Our system automatically verifies your ticket</li>
                            <li>If verified, buyer gets payment notification immediately</li>
                            <li>Once buyer pays, funds are held securely until event completion</li>
                            <li>You get paid after the event (or buyer confirmation)</li>
                        </ol>
                    </div>
                </div>
                
                <div class="footer">
                    <p>🎯 Safe Transaction - Automated Ticket Platform</p>
                    <p>Transaction ID: {transaction_id:06d} | Secure & Automated</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(seller_email, subject, html_content)
    
    def send_ticket_transfer_congratulations(self, buyer_email, transaction_id, event_name, seller_email, event_datetime_str):
        """Send congratulations email to buyer when Safe Transaction transfers their ticket to them"""
        subject = f"🎫 Your {event_name} tickets have arrived!"
        
        html_content = f"""
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
                
                .hero-card {{
                    background: #ffffff;
                    border-radius: 16px;
                    margin: 32px 0;
                    padding: 32px;
                    border: 1px solid #e5e7eb;
                    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
                    text-align: center;
                }}
                
                .celebration-icon {{
                    font-size: 64px;
                    margin-bottom: 16px;
                }}
                
                .hero-title {{
                    font-size: 24px;
                    font-weight: 700;
                    color: #059669;
                    margin-bottom: 12px;
                    line-height: 1.3;
                }}
                
                .hero-subtitle {{
                    font-size: 16px;
                    color: #222222;
                    font-weight: 500;
                    margin-bottom: 24px;
                    line-height: 1.5;
                }}
               
                .transaction-card {{
                    background: #ffffff;
                    border-radius: 16px;
                    margin: 32px 0;
                    padding: 32px;
                    border: 1px solid #e5e7eb;
                    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
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
               
                .status-success {{
                    color: #059669;
                    background: rgba(16, 185, 129, 0.1);
                    padding: 8px 16px;
                    border-radius: 8px;
                    font-size: 14px;
                    font-weight: 700;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }}
               
                .protection-section {{
                    background: #f9fafb;
                    border-radius: 12px;
                    padding: 24px;
                    margin: 32px 0;
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
                   
                    .footer-section {{
                        padding: 32px 20px;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="email-container">
                <div class="header">
                    <div class="logo">Safe Transaction</div>
                    <div class="tagline">Your Tickets Have Arrived!</div>
                </div>
               
                <div class="content">
                    <!-- Section 1: Congratulations -->
                    <div class="section">
                        <div class="hero-card">
                            <div class="celebration-icon">🎫</div>
                            <div class="hero-title">Great news! Your tickets have arrived</div>
                            <div class="hero-subtitle">
                                Your {event_name} tickets have been successfully delivered to you. 
                                You now have everything you need to enjoy the event!
                            </div>
                        </div>
                       
                        <div class="transaction-card">
                            <div class="detail-grid">
                                <div class="detail-item">
                                    <div class="detail-label">Event</div>
                                    <div class="detail-value">{event_name}</div>
                                </div>
                                <div class="detail-item">
                                    <div class="detail-label">Seller</div>
                                    <div class="detail-value">{seller_email}</div>
                                </div>
                                <div class="detail-item">
                                    <div class="detail-label">Event Date</div>
                                    <div class="detail-value">{event_datetime_str}</div>
                                </div>
                                <div class="detail-item">
                                    <div class="detail-label">Delivery Status</div>
                                    <div class="detail-value">
                                        <span class="status-success">✓ Delivered</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                   
                    <!-- Section 2: What happens next -->
                    <div class="section">
                        <div class="section-header">
                            <span style="font-size: 24px; margin-right: 12px;">📋</span>
                            <h2 style="font-size: 22px; font-weight: 700; color: #222222; margin: 0;">What happens next:</h2>
                        </div>
                        <div class="protection-section">
                            <ul class="protection-list">
                                <li class="protection-item">
                                    <div class="check-icon">
                                        <span style="color: white; font-size: 12px; font-weight: bold;">✓</span>
                                    </div>
                                    You now have your tickets and can attend the event
                                </li>
                                <li class="protection-item">
                                    <div class="check-icon">
                                        <span style="color: white; font-size: 12px; font-weight: bold;">✓</span>
                                    </div>
                                    Check your email for the actual ticket files or confirmation
                                </li>
                                <li class="protection-item">
                                    <div class="check-icon">
                                        <span style="color: white; font-size: 12px; font-weight: bold;">✓</span>
                                    </div>
                                    Show up to the event and enjoy - you're all set!
                                </li>
                            </ul>
                        </div>
                    </div>
                   
                    <!-- Section 3: Thank you message -->
                    <div style="text-align: center; margin: 32px 0;">
                        <div style="font-size: 16px; color: #222222; margin-bottom: 16px; font-weight: 500;">
                            🎉 Thank you for choosing Safe Transaction! Hope we've made your ticket purchase seamless and secure.
                        </div>
                        <div style="font-size: 14px; color: #717171;">
                            Questions? <a href="mailto:support@safetransaction.app" style="color: #3b82f6; text-decoration: none;">Contact our support team</a>
                        </div>
                    </div>
                </div>
               
                <div class="footer-section">
                    <div class="footer-text">Transaction ID: #{transaction_id:06d}</div>
                    <div class="footer-text">
                        Need help? <a href="mailto:support@safetransaction.app" class="footer-link">Contact Support</a>
                    </div>
                    <div class="footer-brand">Safe Transaction</div>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(buyer_email, subject, html_content)

# Create global instance
mailgun_sender = MailgunSender()
