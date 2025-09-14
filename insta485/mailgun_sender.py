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
        """Send email via Mailgun"""
        url = f"{self.base_url}/messages"
        
        data = {
            'from': f'{from_name} <noreply@{self.domain}>',
            'to': to_email,
            'subject': subject,
            'html': html_content
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
        """Send verification success email to seller"""
        subject = f"✅ Ticket Verified - TX-{transaction_id:06d} | {event_name}"
        
        deadline_str = payment_deadline.strftime('%B %d, %Y at %I:%M %p') if payment_deadline else "24 hours"
        
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
                .success-badge {{ background: #dcfce7; border: 2px solid #16a34a; color: #15803d; padding: 15px; border-radius: 8px; text-align: center; margin: 20px 0; }}
                .info-box {{ background: #f0f9ff; border-left: 4px solid #0ea5e9; padding: 20px; margin: 20px 0; }}
                .timeline {{ background: #f9fafb; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .timeline-item {{ display: flex; align-items: center; margin: 10px 0; }}
                .timeline-icon {{ width: 24px; height: 24px; background: #10b981; color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 15px; font-size: 12px; }}
                .footer {{ background: #f8fafc; padding: 20px; text-align: center; color: #6b7280; }}
                .button {{ background: #3b82f6; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block; margin: 10px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 Ticket Verified Successfully!</h1>
                    <p>Transaction #{transaction_id:06d}</p>
                </div>
                
                <div class="content">
                    <div class="success-badge">
                        <strong>✅ VERIFICATION COMPLETE</strong><br>
                        Your ticket has been verified and sent to the buyer for payment
                    </div>
                    
                    <div class="info-box">
                        <h3>📋 Transaction Details</h3>
                        <p><strong>Event:</strong> {event_name}</p>
                        <p><strong>Buyer:</strong> {buyer_email}</p>
                        <p><strong>Payment Deadline:</strong> {deadline_str}</p>
                        <p><strong>Status:</strong> Waiting for buyer payment</p>
                    </div>
                    
                    <div class="timeline">
                        <h3>🚀 What Happens Next</h3>
                        <div class="timeline-item">
                            <div class="timeline-icon">✓</div>
                            <div>Ticket verified and forwarded to buyer</div>
                        </div>
                        <div class="timeline-item">
                            <div class="timeline-icon">2</div>
                            <div>Buyer has until {deadline_str} to pay</div>
                        </div>
                        <div class="timeline-item">
                            <div class="timeline-icon">3</div>
                            <div>Once paid, funds are held securely until event completion</div>
                        </div>
                        <div class="timeline-item">
                            <div class="timeline-icon">💰</div>
                            <div>Funds released to you after event (or buyer confirmation)</div>
                        </div>
                    </div>
                    
                    <div class="info-box">
                        <h3>⚠️ Important Notes</h3>
                        <ul>
                            <li>If buyer doesn't pay by deadline, ticket will be returned to you</li>
                            <li>You'll receive updates on payment status automatically</li>
                            <li>Funds are protected by our secure escrow system</li>
                        </ul>
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

# Create global instance
mailgun_sender = MailgunSender()
