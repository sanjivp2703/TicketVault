"""
Email Monitoring System
Continuously monitors for incoming ticket emails and processes them automatically
"""

import time
import re
import json
import threading
from datetime import datetime
import insta485
import insta485.model
from insta485.transaction_manager import TransactionManager


class EmailMonitor:
    """Monitors incoming emails for ticket submissions"""

    def __init__(self):
        self.running = False
        self.thread = None

    def start(self):
        """Start email monitoring in background thread"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._monitor_emails, daemon=True)
            self.thread.start()
            print("📧 Email Monitor started - checking for incoming tickets")

    def stop(self):
        """Stop email monitoring"""
        self.running = False
        if self.thread:
            self.thread.join()
        print("📧 Email Monitor stopped")

    def _monitor_emails(self):
        """Main monitoring loop - checks for emails every 10 seconds"""
        while self.running:
            try:
                with insta485.app.app_context():
                    self._check_incoming_emails()
                time.sleep(10)  # Check every 10 seconds
            except Exception as e:
                print(f"Error in email monitoring: {e}")
                time.sleep(30)  # Wait longer on error

    def _check_incoming_emails(self):
        """
        Check for new emails sent to tx-{id}@safetransaction.com

        NOTE: This is a simplified implementation
        In production, you would integrate with:
        - Mailgun webhooks
        - SendGrid Inbound Parse
        - Direct IMAP connection
        - Email service API
        """
        connection = insta485.model.get_db()

        # Get all pending transactions awaiting tickets
        pending_transactions = connection.execute("""
            SELECT transaction_id, seller_email, awaiting_ticket_email, 
                   listing_created_time, original_event_details
            FROM transactions 
            WHERE status = 'pending_ticket_submission'
            ORDER BY listing_created_time ASC
        """).fetchall()

        if pending_transactions:
            print(
                f"📧 Monitoring {len(pending_transactions)} pending listings for ticket emails..."
            )

        # In production, this would be replaced with actual email checking
        # For now, we'll simulate checking for test emails
        for transaction in pending_transactions:
            # This is where you'd check your email service for new emails
            # sent to transaction['awaiting_ticket_email']
            self._check_transaction_emails(transaction)

    def _check_transaction_emails(self, transaction):
        """
        Check for emails sent to a specific transaction's email address

        In production, this would:
        1. Connect to email service API
        2. Check for emails sent to tx-{id}@safetransaction.com
        3. Process any new emails found
        """
        transaction_id = transaction["transaction_id"]
        ticket_email = transaction["awaiting_ticket_email"]

        # For testing, we'll check if there's a test file
        test_email_file = f"test_emails/tx-{transaction_id:06d}.json"

        try:
            # This simulates receiving an email
            # In production, replace with actual email service integration
            with open(test_email_file, "r") as f:
                email_data = json.load(f)

            print(f"📧 Found test email for transaction {transaction_id}")

            # Process the email
            transaction_manager = TransactionManager()
            result = transaction_manager.process_incoming_ticket(
                transaction_id, email_data
            )

            if result["success"]:
                print(f"✅ Successfully activated listing {transaction_id}")
                # Remove test file after processing
                import os

                os.remove(test_email_file)
            else:
                print(
                    f"❌ Failed to activate listing {transaction_id}: {result['error']}"
                )

        except FileNotFoundError:
            # No email found - this is normal
            pass
        except Exception as e:
            print(f"Error processing email for transaction {transaction_id}: {e}")


# Production Email Integration Classes
class MailgunEmailMonitor(EmailMonitor):
    """Email monitor using Mailgun API"""

    def __init__(self, api_key, domain):
        super().__init__()
        self.api_key = api_key
        self.domain = domain

    def _check_incoming_emails(self):
        """Check Mailgun for new emails"""
        import requests

        # Get events from Mailgun
        response = requests.get(
            f"https://api.mailgun.net/v3/{self.domain}/events",
            auth=("api", self.api_key),
            params={"event": "stored", "limit": 100},
        )

        if response.status_code == 200:
            events = response.json().get("items", [])
            for event in events:
                if "tx-" in event.get("recipient", ""):
                    self._process_mailgun_event(event)

    def _process_mailgun_event(self, event):
        """Process a Mailgun stored message event"""
        # Extract transaction ID from recipient
        recipient = event.get("recipient", "")
        match = re.search(r"tx-(\d+)@", recipient)

        if match:
            transaction_id = int(match.group(1))

            # Get the stored message
            message_url = event.get("storage", {}).get("url")
            if message_url:
                # Download and process the message
                # Implementation depends on Mailgun's stored message format
                pass


class SendGridEmailMonitor(EmailMonitor):
    """Email monitor using SendGrid Inbound Parse"""

    def __init__(self, api_key):
        super().__init__()
        self.api_key = api_key

    def _check_incoming_emails(self):
        """
        SendGrid typically uses webhooks, so this would be different
        You'd set up a webhook endpoint instead of polling
        """
        pass


def create_test_email(transaction_id, seller_email, event_name, location):
    """
    Create a test email file for testing the email monitoring system
    """
    import os

    # Create test_emails directory if it doesn't exist
    os.makedirs("test_emails", exist_ok=True)

    # Create a realistic test email
    test_email = {
        "sender": seller_email,
        "recipient": f"tx-{transaction_id:06d}@safetransaction.com",
        "subject": f"Your {event_name} Tickets - Order Confirmation",
        "body": f"""
Thank you for your ticket purchase!

Event: {event_name}
Venue: {location}
Order Number: TM-123456789
Seat: Section 101, Row A, Seats 5-6

Your tickets are attached as PDF files.

Please arrive 30 minutes early.

Best regards,
Ticketmaster Support
        """,
        "attachments": ["tickets.pdf"],
        "timestamp": datetime.now().isoformat(),
    }

    # Save to test file
    with open(f"test_emails/tx-{transaction_id:06d}.json", "w") as f:
        json.dump(test_email, f, indent=2)

    print(f"📧 Created test email file for transaction {transaction_id}")


# Global email monitor instance
email_monitor = EmailMonitor()
