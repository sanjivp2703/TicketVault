"""
Complete Transaction Management System
Handles all transaction states and automated processes
"""

import json
import datetime
from datetime import timedelta
import stripe
import insta485
import insta485.model
from insta485.email_automation import forward_ticket_email
import logging

logger = logging.getLogger(__name__)


class TransactionManager:
    """Manages all transaction states and automated processes"""

    def __init__(self):
        pass

    def create_listing(
        self, seller_email, buyer_email, price, event_details, school="michigan"
    ):
        """
        Create new listing in PENDING state until seller sends ticket

        Args:
            seller_email: Seller's email
            buyer_email: Buyer's email
            price: Ticket price
            event_details: Event information (name, location, datetime)
            school: School selection (michigan or florida)
        """
        connection = insta485.model.get_db()

        # Create event if doesn't exist
        event_id = self._get_or_create_event(event_details, connection)

        # Store original event details for verification later
        original_details = {
            "event_name": event_details.get("name", ""),
            "location": event_details.get("location", ""),
            "event_datetime": event_details.get("datetime", ""),
            "price": price,
        }

        # Create transaction in PENDING state
        now = datetime.datetime.now()
        cursor = connection.execute(
            """
            INSERT INTO transactions (
                seller_email, buyer_email, price, event_id,
                listing_created_time, original_event_details, 
                status, school
            ) VALUES (?, ?, ?, ?, ?, ?, 'pending_ticket_submission', ?)
        """,
            (
                seller_email,
                buyer_email,
                price,
                event_id,
                now.isoformat(),
                json.dumps(original_details),
                school,
            ),
        )

        transaction_id = cursor.lastrowid

        # Generate unique email for ticket submission
        # Use central email for manual operations
        ticket_email = "safetransactiontix@gmail.com"

        # Update with the ticket email
        connection.execute(
            "UPDATE transactions SET awaiting_ticket_email = ? WHERE transaction_id = ?",
            (ticket_email, transaction_id),
        )
        connection.commit()

        # No longer sending seller instructions email - automatic system

        logger.info(
            f"✅ Created PENDING listing {transaction_id} - awaiting ticket submission to {ticket_email}"
        )

        return {
            "transaction_id": transaction_id,
            "ticket_email": ticket_email,
            "status": "pending_ticket_submission",
            "message": f"Send your ticket to {ticket_email} to activate this listing",
        }

    def process_incoming_ticket(self, transaction_id, email_data):
        """
        Process ticket email sent to tx-{id}@safetransaction.com
        Activates pending listing if ticket details match original listing
        """
        connection = insta485.model.get_db()

        # Get transaction details
        transaction = self._get_transaction(transaction_id, connection)
        if not transaction:
            return {"success": False, "error": "Transaction not found"}

        # Must be in pending state
        if transaction["status"] != "pending_ticket_submission":
            return {
                "success": False,
                "error": f"Transaction in wrong state: {transaction['status']}",
            }

        # Verify sender is the seller
        if email_data["sender"] != transaction["seller_email"]:
            return {
                "success": False,
                "error": "Unauthorized sender - must be from seller email",
            }

        # Verify ticket details match original listing
        verification_result = self._verify_ticket_details_match(email_data, transaction)

        # Store ticket email data
        connection.execute(
            """
            UPDATE transactions 
            SET ticket_email_received = 1,
                ticket_received_time = CURRENT_TIMESTAMP,
                ticket_email_data = ?,
                ticket_verification_score = ?,
                ticket_details_match = ?,
                verification_notes = ?
            WHERE transaction_id = ?
        """,
            (
                json.dumps(email_data),
                verification_result["score"],
                1 if verification_result["details_match"] else 0,
                verification_result["notes"],
                transaction_id,
            ),
        )

        if verification_result["details_match"]:
            # ACTIVATE listing and set 1-hour payment window
            payment_deadline = datetime.datetime.now() + timedelta(hours=1)

            # Update status - listing is now ACTIVE
            connection.execute(
                """
                UPDATE transactions 
                SET status = 'waiting_for_payment',
                    created_time = CURRENT_TIMESTAMP,
                    payment_deadline = ?
                WHERE transaction_id = ?
            """,
                (payment_deadline.isoformat(), transaction_id),
            )

            connection.commit()

            # Send notifications to both seller and buyer
            original_details = json.loads(transaction["original_event_details"])

            # Import our new email sender
            from insta485.mailgun_sender import mailgun_sender

            # NOTE: Seller success email now sent after payment, not after verification

            # 2. Send PAYMENT notification to BUYER

            # Parse datetime if it's a string
            event_datetime = original_details.get("datetime", "TBD")
            if isinstance(event_datetime, str) and event_datetime != "TBD":
                try:
                    event_datetime = datetime.datetime.strptime(
                        event_datetime, "%Y-%m-%d %H:%M:%S"
                    )
                except:
                    pass

            # Use modern email template
            from insta485.email_automation import send_modern_buyer_notification

            # Prepare event details for email
            event_details = {
                "name": original_details["event_name"],
                "location": original_details.get("location", "TBD"),
                "datetime": original_details.get("datetime", "TBD"),
            }

            send_modern_buyer_notification(
                transaction_id=transaction_id,
                buyer_email=transaction["buyer_email"],
                seller_email=transaction["seller_email"],
                price=transaction["price"],
                event_details=event_details,
                payment_deadline=payment_deadline,
            )

            logger.info(
                f"✅ Listing {transaction_id} ACTIVATED - buyer has 1 hour to pay"
            )

            return {
                "success": True,
                "status": "listing_activated",
                "payment_deadline": payment_deadline.isoformat(),
                "verification_score": verification_result["score"],
            }
        else:
            # Ticket verification failed - notify seller and cancel listing
            original_details = json.loads(transaction["original_event_details"])

            # Import our email sender
            from insta485.mailgun_sender import mailgun_sender

            # Send FAILURE notification to SELLER
            mailgun_sender.send_seller_verification_failed(
                seller_email=transaction["seller_email"],
                transaction_id=transaction_id,
                event_name=original_details["event_name"],
                reason=verification_result["reason"],
            )

            # Update status to cancelled due to verification failure
            connection.execute(
                """
                UPDATE transactions 
                SET status = 'cancelled'
                WHERE transaction_id = ?
            """,
                (transaction_id,),
            )

            connection.commit()

            logger.error(
                f"❌ Listing {transaction_id} CANCELLED - verification failed: {verification_result['reason']}"
            )

            return {
                "success": False,
                "error": f"Ticket verification failed: {verification_result['reason']}",
                "notes": verification_result["notes"],
            }

    def _verify_ticket_details_match(self, email_data, transaction):
        """
        Advanced ticket email verification system
        Returns whether details match and verification notes
        """
        score = 0
        notes = []
        details_match = False

        # Get original listing details
        original_details = json.loads(transaction["original_event_details"])

        # Extract content from email
        email_content = (
            email_data.get("subject", "")
            + " "
            + email_data.get("body", "")
            + " "
            + email_data.get("body_text", "")
        ).lower()

        # 1. Event name verification (40 points)
        event_name = original_details["event_name"].lower()
        event_words = [word for word in event_name.split() if len(word) > 2]

        event_matches = sum(1 for word in event_words if word in email_content)
        if event_matches >= len(event_words) * 0.7:  # 70% of event words must match
            score += 40
            notes.append(f"Event name match: {event_matches}/{len(event_words)} words")
        else:
            notes.append(
                f"Event name mismatch: {event_matches}/{len(event_words)} words"
            )

        # 2. Venue/location verification (20 points)
        location = original_details.get("location", "").lower()
        if location and any(
            word in email_content for word in location.split() if len(word) > 3
        ):
            score += 20
            notes.append("Venue/location found in email")

        # 3. Ticket keywords verification (20 points)
        ticket_keywords = [
            "ticket",
            "seat",
            "section",
            "row",
            "barcode",
            "qr",
            "entry",
            "admission",
            "gate",
        ]
        keyword_matches = sum(
            1 for keyword in ticket_keywords if keyword in email_content
        )
        if keyword_matches >= 3:
            score += 20
            notes.append(f"Found {keyword_matches} ticket keywords")

        # 4. Sender domain verification (10 points)
        sender_domain = email_data.get("sender", "").split("@")[-1].lower()
        trusted_domains = [
            "ticketmaster.com",
            "stubhub.com",
            "seatgeek.com",
            "vivid-seats.com",
        ]
        if any(domain in sender_domain for domain in trusted_domains):
            score += 10
            notes.append(f"Trusted sender domain: {sender_domain}")

        # 5. Email structure verification (10 points)
        if len(email_content) > 50 and "noreply" not in email_data.get("sender", ""):
            score += 10
            notes.append("Email has substantial content")

        # Determine if verification passes
        details_match = score >= 70  # Require 70+ points for verification

        return {
            "details_match": details_match,
            "score": score,
            "notes": "; ".join(notes),
            "reason": f"Verification score: {score}/100"
            if not details_match
            else "Verification passed",
        }

    def process_payment(self, transaction_id, payment_method_id):
        """
        Process buyer payment and immediately forward tickets
        """
        connection = insta485.model.get_db()
        transaction = self._get_transaction(transaction_id, connection)
        if not transaction:
            return {"success": False, "error": "Transaction not found"}

        # Check if payment already received
        if transaction["payment_received"]:
            return {"success": False, "error": "Payment already processed"}

        # Check if past payment deadline
        payment_deadline_str = transaction["payment_deadline"]
        if isinstance(payment_deadline_str, str):
            try:
                if "T" in payment_deadline_str:
                    payment_deadline = datetime.datetime.fromisoformat(
                        payment_deadline_str.replace("Z", "+00:00")
                    )
                else:
                    payment_deadline = datetime.datetime.strptime(
                        payment_deadline_str, "%Y-%m-%d %H:%M:%S"
                    )
            except ValueError:
                return {"success": False, "error": "Invalid payment deadline format"}
        else:
            payment_deadline = payment_deadline_str

        if datetime.datetime.now() > payment_deadline:
            self._expire_transaction(transaction_id, "payment_deadline_passed")
            return {"success": False, "error": "Payment deadline has passed"}

        try:
            # Create payment intent (capture immediately for instant processing)
            payment_intent = stripe.PaymentIntent.create(
                amount=int(transaction["price"] * 100),
                currency="usd",
                payment_method=payment_method_id,
                confirmation_method="manual",
                confirm=True,
                capture_method="automatic",  # Capture immediately
                metadata={"transaction_id": transaction_id},
            )

            # Update transaction with payment info
            connection.execute(
                """
                UPDATE transactions SET 
                    payment_received = 1,
                    payment_received_time = CURRENT_TIMESTAMP,
                    payment_intent_id = ?,
                    status = 'waiting_for_payment_processing'
                WHERE transaction_id = ?
            """,
                (payment_intent.id, transaction_id),
            )

            connection.commit()

            # Immediately forward tickets to buyer
            self._forward_ticket_to_buyer(transaction_id, connection)

            # Set up automatic fund release (24 hours from now)
            release_deadline = datetime.datetime.now() + timedelta(hours=24)
            connection.execute(
                """
                UPDATE transactions SET 
                    status = 'ticket_forwarded_funds_held',
                    release_deadline = ?
                WHERE transaction_id = ?
            """,
                (release_deadline.strftime("%Y-%m-%d %H:%M:%S"), transaction_id),
            )

            connection.commit()

            logger.info(
                f"✅ Payment processed and tickets forwarded for transaction {transaction_id}"
            )

            return {
                "success": True,
                "payment_intent_id": payment_intent.id,
                "status": "tickets_forwarded",
            }

        except stripe.error.StripeError as e:
            return {"success": False, "error": f"Payment failed: {str(e)}"}

    def _advance_transaction_state(self, transaction_id):
        """
        Check transaction state and advance to next step
        """
        transaction = self._get_transaction(transaction_id)

        # Both ticket and payment received - forward ticket and hold funds
        if (
            transaction["ticket_email_received"]
            and transaction["payment_received"]
            and not transaction["ticket_forwarded"]
        ):
            self._forward_ticket_to_buyer(transaction_id)
            self._update_status(transaction_id, "ticket_forwarded_funds_held")

            # Set release deadline (24 hours from now)
            release_deadline = datetime.datetime.now() + timedelta(hours=24)
            self.connection.execute(
                """
                UPDATE transactions SET release_deadline = ?
                WHERE transaction_id = ?
            """,
                (release_deadline, transaction_id),
            )

            # Schedule automatic release
            self._schedule_payment_release(transaction_id, release_deadline)

        # Only ticket received - notify buyer to pay
        elif (
            transaction["ticket_email_received"] and not transaction["payment_received"]
        ):
            self._update_status(transaction_id, "waiting_for_payment")
            self._send_payment_reminder(transaction_id)

        self.connection.commit()

    def _forward_ticket_to_buyer(self, transaction_id, connection):
        """
        Forward ticket email to buyer immediately after payment
        """
        transaction = self._get_transaction(transaction_id, connection)
        if not transaction or not transaction["ticket_email_data"]:
            logger.error(f"❌ No ticket data found for transaction {transaction_id}")
            return False

        ticket_data = json.loads(transaction["ticket_email_data"])

        # Forward the email using the email automation system
        try:
            from insta485.email_automation import forward_ticket_email

            success = forward_ticket_email(
                to_email=transaction["buyer_email"],
                original_email_data=ticket_data,
                transaction_id=transaction_id,
            )

            if success:
                connection.execute(
                    """
                    UPDATE transactions SET 
                        ticket_forwarded = 1,
                        ticket_forwarded_time = CURRENT_TIMESTAMP
                    WHERE transaction_id = ?
                """,
                    (transaction_id,),
                )

                connection.commit()

                logger.info(
                    f"📧 Tickets forwarded to buyer: {transaction['buyer_email']}"
                )

                # Send confirmation emails to both parties
                self._notify_ticket_forwarded(transaction_id, connection)
                return True
            else:
                logger.error(
                    f"❌ Failed to forward tickets for transaction {transaction_id}"
                )
                return False

        except Exception as e:
            logger.error(f"❌ Error forwarding tickets: {e}")
            return False

    def confirm_buyer_receipt(self, transaction_id, buyer_email):
        """
        Buyer confirms they received valid tickets
        """
        transaction = self._get_transaction(transaction_id)

        if transaction["buyer_email"] != buyer_email:
            return {"success": False, "error": "Unauthorized"}

        if transaction["status"] != "ticket_forwarded_funds_held":
            return {"success": False, "error": "Invalid transaction state"}

        # Mark confirmed and release funds immediately
        self.connection.execute(
            """
            UPDATE transactions SET 
                buyer_confirmed_receipt = 1,
                buyer_confirmation_time = CURRENT_TIMESTAMP
            WHERE transaction_id = ?
        """,
            (transaction_id,),
        )

        self._release_funds_to_seller(transaction_id, "buyer_confirmed")
        return {"success": True}

    def file_complaint(self, transaction_id, buyer_email, complaint_reason):
        """
        Buyer files complaint about tickets
        """
        transaction = self._get_transaction(transaction_id)

        if transaction["buyer_email"] != buyer_email:
            return {"success": False, "error": "Unauthorized"}

        if transaction["status"] not in ["ticket_forwarded_funds_held", "completed"]:
            return {"success": False, "error": "Cannot file complaint at this stage"}

        # Update status and hold funds
        self.connection.execute(
            """
            UPDATE transactions SET 
                status = 'complaint_filed',
                complaint_reason = ?
            WHERE transaction_id = ?
        """,
            (complaint_reason, transaction_id),
        )

        # Notify admin for manual review
        self._notify_admin_complaint(transaction_id, complaint_reason)

        return {"success": True}

    def _release_funds_to_seller(self, transaction_id, reason):
        """
        Release held funds to seller
        """
        transaction = self._get_transaction(transaction_id)

        try:
            # Capture the held payment
            stripe.PaymentIntent.capture(transaction["payment_intent_id"])

            # Calculate seller amount (minus platform fee)
            platform_fee_rate = 0.05  # 5% platform fee
            seller_amount = transaction["price"] * (1 - platform_fee_rate)

            # Transfer to seller
            stripe.Transfer.create(
                amount=int(seller_amount * 100),
                currency="usd",
                destination=self._get_seller_stripe_id(transaction["seller_email"]),
                transfer_group=str(transaction_id),
            )

            # Update transaction
            self.connection.execute(
                """
                UPDATE transactions SET 
                    funds_released = 1,
                    funds_released_time = CURRENT_TIMESTAMP,
                    status = 'completed'
                WHERE transaction_id = ?
            """,
                (transaction_id,),
            )

            # Notify parties
            self._notify_funds_released(transaction_id, reason)

            logger.info(f"✅ Funds released for transaction {transaction_id}: {reason}")

        except Exception as e:
            logger.error(
                f"❌ Error releasing funds for transaction {transaction_id}: {e}"
            )

    def _expire_transaction(self, transaction_id, reason):
        """
        Handle transaction expiration
        """
        transaction = self._get_transaction(transaction_id)

        if reason == "ticket_deadline_passed":
            # No ticket received - just mark as expired
            self._update_status(transaction_id, "expired_no_ticket")
            self._notify_transaction_expired(
                transaction_id, "seller", "ticket deadline"
            )

        elif reason == "payment_deadline_passed":
            # Ticket was sent but no payment - return ticket to seller
            if transaction["ticket_email_received"]:
                self._return_ticket_to_seller(transaction_id)
                self._update_status(transaction_id, "ticket_returned")
                self._notify_transaction_expired(
                    transaction_id, "buyer", "payment deadline"
                )

    def _return_ticket_to_seller(self, transaction_id):
        """
        Return ticket email back to seller
        """
        transaction = self._get_transaction(transaction_id)
        ticket_data = json.loads(transaction["ticket_email_data"])

        # Forward ticket back to seller
        forward_ticket_email(
            to_email=transaction["seller_email"],
            original_email_data=ticket_data,
            transaction_id=transaction_id,
            return_mode=True,
        )

    def check_scheduled_deadlines(self):
        """
        Background job to check all deadlines and auto-release funds
        Called by scheduler every 5 minutes
        """
        now = datetime.datetime.now()

        # Check ticket deadlines
        expired_tickets = self.connection.execute(
            """
            SELECT transaction_id FROM transactions 
            WHERE status = 'waiting_for_ticket' 
            AND ticket_deadline < ?
        """,
            (now,),
        ).fetchall()

        for row in expired_tickets:
            self._expire_transaction(row["transaction_id"], "ticket_deadline_passed")

        # Check payment deadlines
        expired_payments = self.connection.execute(
            """
            SELECT transaction_id FROM transactions 
            WHERE status = 'waiting_for_payment' 
            AND payment_deadline < ?
        """,
            (now,),
        ).fetchall()

        for row in expired_payments:
            self._expire_transaction(row["transaction_id"], "payment_deadline_passed")

        # Check fund release deadlines
        auto_releases = self.connection.execute(
            """
            SELECT transaction_id FROM transactions 
            WHERE status = 'ticket_forwarded_funds_held' 
            AND release_deadline < ?
            AND complaint_reason IS NULL
        """,
            (now,),
        ).fetchall()

        for row in auto_releases:
            self._release_funds_to_seller(
                row["transaction_id"], "automatic_24hr_release"
            )

        self.connection.commit()

    # Helper methods
    def _get_transaction(self, transaction_id, connection):
        """Get transaction details"""
        return connection.execute(
            """
            SELECT * FROM transactions WHERE transaction_id = ?
        """,
            (transaction_id,),
        ).fetchone()

    def _update_status(self, transaction_id, new_status):
        """Update transaction status"""
        self.connection.execute(
            """
            UPDATE transactions SET status = ? WHERE transaction_id = ?
        """,
            (new_status, transaction_id),
        )

    def _verify_ticket_authenticity(self, transaction_id, email_data):
        """Verify ticket email authenticity"""
        # Implementation from previous design
        score = 0

        # Domain verification
        trusted_domains = ["ticketmaster.com", "stubhub.com", "seatgeek.com"]
        sender_domain = email_data["sender"].split("@")[-1]
        if sender_domain in trusted_domains:
            score += 40

        # Content analysis
        content = email_data["body"].lower()
        ticket_keywords = [
            "ticket",
            "event",
            "venue",
            "seat",
            "section",
            "row",
            "barcode",
        ]
        keyword_matches = sum(1 for word in ticket_keywords if word in content)
        score += min(keyword_matches * 5, 35)

        # Event matching
        transaction = self._get_transaction(transaction_id)
        event = self._get_event(transaction["event_id"])

        if event["name"].lower() in content:
            score += 15
        if event["location"].lower() in content:
            score += 10

        return {"score": score, "is_valid": score >= 70}

    def _get_event(self, event_id):
        """Get event details"""
        return self.connection.execute(
            """
            SELECT * FROM events WHERE event_id = ?
        """,
            (event_id,),
        ).fetchone()

    def _get_or_create_event(self, event_details, connection):
        """Get or create event entry"""
        existing = connection.execute(
            """
            SELECT event_id FROM events 
            WHERE name = ? AND location = ? AND event_datetime = ?
        """,
            (
                event_details["name"],
                event_details["location"],
                event_details["datetime"],
            ),
        ).fetchone()

        if existing:
            return existing["event_id"]

        cursor = connection.execute(
            """
            INSERT INTO events (name, location, event_datetime)
            VALUES (?, ?, ?)
        """,
            (
                event_details["name"],
                event_details["location"],
                event_details["datetime"],
            ),
        )

        connection.commit()
        return cursor.lastrowid

    # Notification methods (basic implementations)
    def _notify_ticket_forwarded(self, transaction_id, connection):
        """Notify both parties that ticket was forwarded"""
        try:
            from insta485.email_automation import send_email

            transaction = self._get_transaction(transaction_id, connection)
            if not transaction:
                return

            # Get event details
            original_details = json.loads(transaction["original_event_details"])
            event_name = original_details["event_name"]

            # Notify buyer
            buyer_subject = f"🎫 Your {event_name} Tickets Have Been Delivered!"
            buyer_html = f"""
            <h2>🎉 Tickets Delivered Successfully!</h2>
            <p>Great news! Your tickets for <strong>{event_name}</strong> have been delivered to your email.</p>
            <p><strong>Transaction ID:</strong> {transaction_id}</p>
            <p>If you have any issues with your tickets, please contact us within 24 hours.</p>
            <p>Enjoy the event!</p>
            """

            send_email(transaction["buyer_email"], buyer_subject, buyer_html)

            # Notify seller
            seller_subject = f"💰 Payment Confirmed - {event_name} Tickets Delivered"
            seller_html = f"""
            <h2>✅ Transaction Successful!</h2>
            <p>Your tickets for <strong>{event_name}</strong> have been successfully delivered to the buyer.</p>
            <p><strong>Transaction ID:</strong> {transaction_id}</p>
            <p><strong>Amount:</strong> ${transaction["price"]}</p>
            <p>Funds will be released to your account within 24 hours after the event.</p>
            """

            send_email(transaction["seller_email"], seller_subject, seller_html)

            logger.info(
                f"📧 Ticket forwarded notifications sent for transaction {transaction_id}"
            )

        except Exception as e:
            logger.error(f"❌ Error sending ticket forwarded notifications: {e}")

    def _notify_funds_released(self, transaction_id, reason):
        """Notify both parties that funds were released"""
        try:
            from insta485.email_automation import send_email

            connection = insta485.model.get_db()
            transaction = self._get_transaction(transaction_id, connection)
            if not transaction:
                return

            # Get event details
            original_details = json.loads(transaction["original_event_details"])
            event_name = original_details["event_name"]

            # Calculate seller amount (minus 5% platform fee)
            platform_fee_rate = 0.05
            seller_amount = transaction["price"] * (1 - platform_fee_rate)

            # Notify seller
            seller_subject = f"💰 Payment Released - {event_name}"
            seller_html = f"""
            <h2>💰 Payment Released!</h2>
            <p>Your payment for <strong>{event_name}</strong> has been released.</p>
            <p><strong>Transaction ID:</strong> {transaction_id}</p>
            <p><strong>Gross Amount:</strong> ${transaction["price"]}</p>
            <p><strong>Platform Fee (5%):</strong> ${transaction["price"] * platform_fee_rate:.2f}</p>
            <p><strong>Net Amount:</strong> ${seller_amount:.2f}</p>
            <p><strong>Reason:</strong> {reason}</p>
            <p>Funds should appear in your account within 2-3 business days.</p>
            """

            send_email(transaction["seller_email"], seller_subject, seller_html)

            logger.info(
                f"💰 Funds released notification sent for transaction {transaction_id}: {reason}"
            )

        except Exception as e:
            logger.error(f"❌ Error sending funds released notification: {e}")

    def _notify_transaction_expired(
        self, transaction_id, responsible_party, deadline_type
    ):
        """Notify about transaction expiration"""
        logger.info(f"⏰ Transaction {transaction_id} expired: {deadline_type}")

    def _notify_admin_complaint(self, transaction_id, complaint_reason):
        """Notify admin about complaint"""
        logger.info(
            f"🚨 Complaint filed for transaction {transaction_id}: {complaint_reason}"
        )

    def _send_payment_reminder(self, transaction_id):
        """Send payment reminder to buyer"""
        logger.info(f"📧 Payment reminder sent for transaction {transaction_id}")

    def _schedule_deadline_check(self, transaction_id, check_type, deadline):
        """Schedule background job for deadline checking"""
        logger.info(
            f"⏰ Scheduled {check_type} deadline check for transaction {transaction_id}"
        )

    def _schedule_payment_release(self, transaction_id, release_time):
        """Schedule automatic payment release"""
        logger.info(
            f"⏰ Scheduled payment release for transaction {transaction_id} at {release_time}"
        )

    def _get_seller_stripe_id(self, seller_email):
        """Get seller's Stripe account ID"""
        result = self.connection.execute(
            """
            SELECT stripe_id FROM users WHERE email = ?
        """,
            (seller_email,),
        ).fetchone()
        return result["stripe_id"] if result else None

    def _flag_suspicious_ticket(self, transaction_id, verification_result):
        """Flag transaction for manual review"""
        self.connection.execute(
            """
            UPDATE transactions SET 
                status = 'requires_manual_review',
                ticket_verification_score = ?
            WHERE transaction_id = ?
        """,
            (verification_result["score"], transaction_id),
        )
