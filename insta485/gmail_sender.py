#!/usr/bin/env python3
"""
Gmail SMTP sender for buyer confirmation emails
This bypasses Mailgun sandbox restrictions for buyer emails
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os


class GmailSender:
    """Send emails via Gmail SMTP for buyer notifications"""

    def __init__(self):
        # Gmail SMTP configuration
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.sender_email = "safetransactiontix@gmail.com"
        # In production, this should be an app password, not the regular password
        self.sender_password = os.environ.get("GMAIL_APP_PASSWORD", "")

    def send_email(self, to_email, subject, html_content):
        """Send email via Gmail SMTP"""
        try:
            # Create message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.sender_email
            msg["To"] = to_email

            # Add HTML content
            html_part = MIMEText(html_content, "html")
            msg.attach(html_part)

            # Connect to Gmail SMTP
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()  # Enable encryption

            # Login (requires app password for Gmail)
            if self.sender_password:
                server.login(self.sender_email, self.sender_password)

                # Send email
                server.send_message(msg)
                server.quit()

                print(f"✅ Gmail SMTP: Email sent to {to_email}: {subject}")
                return True
            else:
                print("❌ Gmail SMTP: No app password configured")
                return False

        except Exception as e:
            print(f"❌ Gmail SMTP error sending to {to_email}: {e}")
            return False


def test_gmail_sender():
    """Test Gmail SMTP sender"""
    gmail = GmailSender()

    print("🧪 Testing Gmail SMTP sender...")

    test_email = "testbuyer@example.com"
    test_subject = "Test Buyer Confirmation Email"
    test_html = """
    <html>
    <body>
        <h2>Payment Confirmation</h2>
        <p>This is a test email sent via Gmail SMTP to bypass Mailgun sandbox restrictions.</p>
        <p>Your payment was successful!</p>
    </body>
    </html>
    """

    success = gmail.send_email(test_email, test_subject, test_html)

    if success:
        print("✅ Gmail SMTP test successful!")
    else:
        print("❌ Gmail SMTP test failed")
        print("💡 To enable Gmail SMTP:")
        print("   1. Enable 2-factor authentication on safetransactiontix@gmail.com")
        print("   2. Generate an app password")
        print("   3. Set GMAIL_APP_PASSWORD environment variable")


if __name__ == "__main__":
    test_gmail_sender()
