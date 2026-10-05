"""
Email Webhook System for Safe Transaction
Receives and processes incoming ticket emails from sellers
"""

import json
from datetime import datetime, timedelta
import re
import insta485


class EmailWebhookHandler:
    """Handles incoming email webhooks for ticket processing"""

    def __init__(self):
        pass

    def process_incoming_email(self, webhook_data):
        """
        Process incoming email from webhook
        Expected webhook format from email service (like Mailgun, SendGrid, etc.)
        """
        try:
            connection = insta485.model.get_db()

            # Extract email data from webhook
            email_data = self._parse_webhook_data(webhook_data)

            # Extract transaction ID from recipient email
            transaction_id = self._extract_transaction_id(email_data["to"])

            if not transaction_id:
                return {"error": "Invalid recipient email format"}

            # Get transaction details
            transaction = self._get_transaction(transaction_id, connection)
            if not transaction:
                return {"error": "Transaction not found"}

            # Verify transaction is in correct state
            if transaction["status"] != "pending_ticket_submission":
                return {"error": f"Transaction in wrong state: {transaction['status']}"}

            # Verify sender is the seller
            if email_data["from"] != transaction["seller_email"]:
                from insta485.error_handler import error_handler

                return error_handler.handle_invalid_sender(
                    transaction_id, email_data["from"], transaction["seller_email"]
                )

            # Check for duplicate emails
            from insta485.error_handler import error_handler

            duplicate_check = error_handler.handle_duplicate_email(
                transaction_id, email_data
            )
            if (
                "error" in duplicate_check
                and "already processed" in duplicate_check["error"]
            ):
                return duplicate_check

            # Process and verify the ticket email
            verification_result = self._verify_ticket_email(email_data, transaction)

            # Store email data and update transaction
            self._store_ticket_email(
                transaction_id, email_data, verification_result, connection
            )

            # Update transaction status and trigger payment window
            if verification_result["is_valid"]:
                self._activate_payment_window(transaction_id, transaction, connection)
                return {
                    "success": True,
                    "message": "Ticket verified and payment window activated",
                }
            else:
                # Handle verification failure through error handler
                from insta485.error_handler import error_handler

                error_handler.handle_verification_failure(
                    transaction_id, verification_result, email_data
                )
                return {
                    "error": f"Ticket verification failed: {verification_result['reason']}"
                }

        except Exception as e:
            print(f"Error processing email webhook: {e}")
            return {"error": "Internal processing error"}

    def _parse_webhook_data(self, webhook_data):
        """Parse webhook data from email service"""
        # This will vary based on your email service (Mailgun, SendGrid, etc.)
        # For now, assuming a standard format
        return {
            "from": webhook_data.get("sender", ""),
            "to": webhook_data.get("recipient", ""),
            "subject": webhook_data.get("subject", ""),
            "body_text": webhook_data.get("body-plain", ""),
            "body_html": webhook_data.get("body-html", ""),
            "attachments": webhook_data.get("attachments", []),
            "timestamp": datetime.now().isoformat(),
        }

    def _extract_transaction_id(self, recipient_email):
        """Extract transaction ID from tx-123456@safetransaction.com format"""
        match = re.match(r"tx-(\d+)@", recipient_email.lower())
        return int(match.group(1)) if match else None

    def _get_transaction(self, transaction_id, connection):
        """Get transaction details from database"""
        return connection.execute(
            """
            SELECT t.*, e.name as event_name, e.location, e.event_datetime
            FROM transactions t
            JOIN events e ON t.event_id = e.event_id
            WHERE t.transaction_id = ?
            """,
            (transaction_id,),
        ).fetchone()

    def _verify_ticket_email(self, email_data, transaction):
        """Verify the ticket email is authentic and matches the transaction"""
        verification_score = 0
        reasons = []

        # 1. Check sender domain (basic verification)
        sender_domain = email_data["from"].split("@")[-1].lower()
        trusted_domains = [
            "ticketmaster.com",
            "stubhub.com",
            "seatgeek.com",
            "vivid-seats.com",
            "tickpick.com",
            "gametime.co",
        ]

        if any(domain in sender_domain for domain in trusted_domains):
            verification_score += 30
            reasons.append("Trusted sender domain")
        else:
            reasons.append(f"Unknown sender domain: {sender_domain}")

        # 2. Check for ticket-related keywords
        content = (email_data["body_text"] + " " + email_data["subject"]).lower()
        ticket_keywords = [
            "ticket",
            "seat",
            "section",
            "row",
            "event",
            "venue",
            "admission",
        ]

        keyword_matches = sum(1 for keyword in ticket_keywords if keyword in content)
        if keyword_matches >= 3:
            verification_score += 25
            reasons.append(f"Contains {keyword_matches} ticket keywords")

        # 3. Check for event name match
        event_name = transaction["event_name"].lower()
        if any(word in content for word in event_name.split() if len(word) > 3):
            verification_score += 20
            reasons.append("Event name matches")

        # 4. Check for attachments (PDFs, images)
        if email_data["attachments"]:
            verification_score += 15
            reasons.append(f"Has {len(email_data['attachments'])} attachments")

        # 5. Check email structure (not automated reply)
        if (
            "noreply" not in email_data["from"].lower()
            and "donotreply" not in email_data["from"].lower()
        ):
            verification_score += 10
            reasons.append("Not an automated reply")

        return {
            "is_valid": verification_score >= 60,  # Require 60+ points for approval
            "score": verification_score,
            "reasons": reasons,
            "max_score": 100,
        }

    def _store_ticket_email(
        self, transaction_id, email_data, verification_result, connection
    ):
        """Store the ticket email data in the database"""
        connection.execute(
            """
            UPDATE transactions 
            SET ticket_email_received = 1,
                ticket_received_time = CURRENT_TIMESTAMP,
                ticket_email_data = ?,
                ticket_verification_score = ?
            WHERE transaction_id = ?
            """,
            (json.dumps(email_data), verification_result["score"], transaction_id),
        )
        connection.commit()

    def _activate_payment_window(self, transaction_id, transaction, connection):
        """Activate the 1-hour payment window for the buyer"""
        # Set payment deadline to 1 hour from now
        payment_deadline = datetime.now() + timedelta(hours=1)

        # Update transaction status
        connection.execute(
            """
            UPDATE transactions 
            SET status = 'waiting_for_payment',
                payment_deadline = ?,
                ticket_details_match = 1,
                verification_notes = ?
            WHERE transaction_id = ?
            """,
            (
                payment_deadline.strftime("%Y-%m-%d %H:%M:%S"),
                "Automatically verified via email webhook",
                transaction_id,
            ),
        )
        connection.commit()

        # Send notifications
        from insta485.email_automation import (
            send_buyer_notification,
        )

        # Notify buyer that tickets are ready and payment is required
        event_details = {
            "name": transaction["event_name"],
            "location": transaction["location"],
            "datetime": transaction["event_datetime"],
        }

        send_buyer_notification(
            transaction_id=transaction_id,
            buyer_email=transaction["buyer_email"],
            seller_email=transaction["seller_email"],
            price=transaction["price"],
            event_details=event_details,
            payment_deadline=payment_deadline,
        )

        # Notify seller that tickets were verified
        print(f"✅ Tickets verified for transaction {transaction_id}")
        print(f"📧 Payment window activated for buyer: {transaction['buyer_email']}")


def create_webhook_routes():
    """Create Flask routes for email webhooks"""
    import flask

    @insta485.app.route("/webhook/mailgun", methods=["POST"])
    def handle_mailgun_webhook():
        """Handle Mailgun webhook for incoming emails"""
        try:
            # Mailgun sends form data
            webhook_data = {
                "sender": flask.request.form.get("sender", ""),
                "recipient": flask.request.form.get("recipient", ""),
                "subject": flask.request.form.get("subject", ""),
                "body-plain": flask.request.form.get("body-plain", ""),
                "body-html": flask.request.form.get("body-html", ""),
                "timestamp": flask.request.form.get("timestamp", ""),
            }

            print(
                f"📧 MAILGUN: Received email from {webhook_data['sender']} to {webhook_data['recipient']}"
            )

            # Process the email
            handler = EmailWebhookHandler()
            result = handler.process_incoming_email(webhook_data)

            if "error" in result:
                print(f"❌ MAILGUN: {result['error']}")
                return flask.jsonify(result), 400
            else:
                print("✅ MAILGUN: Email processed successfully")
                return flask.jsonify(result), 200

        except Exception as e:
            print(f"❌ MAILGUN ERROR: {e}")
            return flask.jsonify({"error": "Webhook processing failed"}), 500

    @insta485.app.route("/webhook/sendgrid", methods=["POST"])
    def handle_sendgrid_webhook():
        """Handle SendGrid Inbound Parse webhook"""
        try:
            # SendGrid sends form data
            webhook_data = {
                "sender": flask.request.form.get("from", ""),
                "recipient": flask.request.form.get("to", ""),
                "subject": flask.request.form.get("subject", ""),
                "body-plain": flask.request.form.get("text", ""),
                "body-html": flask.request.form.get("html", ""),
                "timestamp": "",
            }

            print(
                f"📧 SENDGRID: Received email from {webhook_data['sender']} to {webhook_data['recipient']}"
            )

            # Process the email
            handler = EmailWebhookHandler()
            result = handler.process_incoming_email(webhook_data)

            return flask.jsonify(
                {"status": "processed" if "error" not in result else "failed"}
            ), 200

        except Exception as e:
            print(f"❌ SENDGRID ERROR: {e}")
            return flask.jsonify({"error": "Webhook processing failed"}), 500

    @insta485.app.route("/api/simulate-ticket-email", methods=["POST"])
    def simulate_ticket_email():
        """Development endpoint to simulate receiving a ticket email"""
        try:
            data = flask.request.get_json()

            if not data or "transaction_id" not in data:
                return flask.jsonify(
                    {"success": False, "error": "Missing transaction_id"}
                ), 400

            transaction_id = data["transaction_id"]

            # Get transaction details to use seller email
            connection = insta485.model.get_db()
            transaction = connection.execute(
                "SELECT seller_email FROM transactions WHERE transaction_id = ?",
                (transaction_id,),
            ).fetchone()

            if not transaction:
                return flask.jsonify(
                    {"success": False, "error": "Transaction not found"}
                ), 400

            # Create realistic email data
            webhook_data = {
                "sender": transaction["seller_email"],
                "recipient": f"tx-{transaction_id:06d}@safetransaction.com",
                "subject": data.get(
                    "subject", "Your Event Tickets - Order Confirmation"
                ),
                "body-plain": data.get("body", "Your tickets are attached."),
                "body-html": data.get("html_content", ""),
                "timestamp": datetime.now().isoformat(),
            }

            print(
                f"🧪 SIMULATION: Processing ticket email for transaction {transaction_id}"
            )

            # Process through webhook handler
            handler = EmailWebhookHandler()
            result = handler.process_incoming_email(webhook_data)

            if "error" in result:
                return flask.jsonify({"success": False, "error": result["error"]}), 400
            else:
                return flask.jsonify(
                    {"success": True, "message": result["message"]}
                ), 200

        except Exception as e:
            print(f"❌ EMAIL SIMULATION ERROR: {e}")
            return flask.jsonify({"success": False, "error": str(e)}), 500


# Initialize the webhook routes
create_webhook_routes()
