"""
API endpoints for the automated transaction system
"""

import flask
import json
import stripe
from datetime import datetime, timedelta
import insta485
from insta485.transaction_manager import TransactionManager
import logging

logger = logging.getLogger(__name__)
# Email processing functionality will be added later


@insta485.app.route("/api/transactions/create", methods=["POST"])
def create_transaction_api():
    """
    Create new transaction listing

    POST /api/transactions/create
    {
        "buyer_email": "buyer@example.com",
        "price": 150.00,
        "event_name": "Taylor Swift Concert",
        "event_location": "MetLife Stadium",
        "event_datetime": "2024-07-15 20:00:00",
        "ticket_deadline_hours": 24,
        "payment_deadline_hours": 48
    }
    """
    if "email" not in flask.session:
        return flask.jsonify({"error": "Authentication required"}), 401

    seller_email = flask.session["email"]
    data = flask.request.get_json()

    # Validate required fields
    required_fields = [
        "buyer_email",
        "price",
        "event_name",
        "event_location",
        "event_datetime",
    ]
    for field in required_fields:
        if field not in data:
            return flask.jsonify({"error": f"Missing field: {field}"}), 400

    # Validate seller isn't creating transaction with themselves
    if seller_email == data["buyer_email"]:
        return flask.jsonify({"error": "Cannot create transaction with yourself"}), 400

    try:
        # Validate and create buyer user if doesn't exist
        connection = insta485.model.get_db()
        buyer_exists = connection.execute(
            "SELECT email FROM users WHERE email = ?", (data["buyer_email"],)
        ).fetchone()

        if not buyer_exists:
            # Create placeholder user for buyer
            password_hash = "sha512$placeholder$placeholder_hash_needs_reset"
            connection.execute(
                "INSERT INTO users (email, firstname, lastname, password) VALUES (?, ?, ?, ?)",
                (data["buyer_email"], "New", "User", password_hash),
            )
            connection.commit()

        # Fix datetime format - convert from HTML5 datetime-local to SQLite format
        event_datetime_raw = data["event_datetime"]
        if "T" in event_datetime_raw:
            # Format: "2025-10-04T00:00" -> "2025-10-04 00:00:00"
            event_datetime = event_datetime_raw.replace("T", " ")
            # Add seconds if not present
            if len(event_datetime) == 16:
                event_datetime += ":00"
        else:
            event_datetime = event_datetime_raw

        transaction_manager = TransactionManager()

        event_details = {
            "name": data["event_name"],
            "location": data["event_location"],
            "datetime": event_datetime,
        }

        result = transaction_manager.create_listing(
            seller_email=seller_email,
            buyer_email=data["buyer_email"],
            price=float(data["price"]),
            event_details=event_details,
            school=data.get("school", "michigan"),
        )

        return flask.jsonify(
            {
                "success": True,
                "transaction_id": result["transaction_id"],
                "ticket_email": result["ticket_email"],
                "status": result["status"],
                "message": result["message"],
            }
        )

    except Exception as e:
        return flask.jsonify({"error": str(e)}), 500


@insta485.app.route(
    "/api/transactions/<int:transaction_id>/pay", methods=["GET", "POST"]
)
def get_payment_checkout_url(transaction_id):
    """
    Get Stripe checkout URL for buyer payment

    GET /api/transactions/123/pay - Redirects directly to Stripe (for email links)
    POST /api/transactions/123/pay - Returns JSON with checkout_url (for AJAX)
    """
    try:
        connection = insta485.model.get_db()
        transaction = connection.execute(
            "SELECT price FROM transactions WHERE transaction_id = ?", (transaction_id,)
        ).fetchone()

        if not transaction:
            return flask.jsonify(
                {"success": False, "error": "Transaction not found"}
            ), 404

        amount = int(transaction["price"] * 100)  # Convert to cents as integer

        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": f"Payment for Transaction #{transaction_id}",
                        },
                        "unit_amount": amount,
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url=flask.url_for(
                "payment_success", transaction_id=transaction_id, _external=True
            ),
            cancel_url=flask.url_for("payment_cancel", _external=True),
        )

        # Store transaction_id in session for success page
        flask.session["transaction_id"] = transaction_id

        # Handle GET requests (from email links) - redirect directly to Stripe
        if flask.request.method == "GET":
            return flask.redirect(session.url)

        # Handle POST requests (from AJAX) - return JSON
        return flask.jsonify({"success": True, "checkout_url": session.url})

    except Exception as e:
        return flask.jsonify({"success": False, "error": str(e)}), 500


@insta485.app.route("/api/transactions/<int:transaction_id>/confirm", methods=["POST"])
def confirm_receipt_api(transaction_id):
    """
    Buyer confirms receipt of valid tickets

    POST /api/transactions/123/confirm
    """
    if "email" not in flask.session:
        return flask.jsonify({"error": "Authentication required"}), 401

    buyer_email = flask.session["email"]

    try:
        transaction_manager = TransactionManager()
        result = transaction_manager.confirm_buyer_receipt(
            transaction_id=transaction_id, buyer_email=buyer_email
        )

        if result["success"]:
            return flask.jsonify(
                {
                    "success": True,
                    "message": "Receipt confirmed, funds released to seller",
                }
            )
        else:
            return flask.jsonify({"error": result["error"]}), 400

    except Exception as e:
        return flask.jsonify({"error": str(e)}), 500


@insta485.app.route(
    "/api/transactions/<int:transaction_id>/complaint", methods=["POST"]
)
def file_complaint_api(transaction_id):
    """
    File complaint about transaction

    POST /api/transactions/123/complaint
    {
        "reason": "Fake tickets received"
    }
    """
    if "email" not in flask.session:
        return flask.jsonify({"error": "Authentication required"}), 401

    buyer_email = flask.session["email"]
    data = flask.request.get_json()

    if "reason" not in data:
        return flask.jsonify({"error": "Missing complaint reason"}), 400

    try:
        from insta485.error_handler import error_handler

        result = error_handler.handle_complaint_filed(
            transaction_id=transaction_id,
            complaint_reason=data["reason"],
            buyer_email=buyer_email,
        )

        if result["success"]:
            return flask.jsonify(
                {
                    "success": True,
                    "message": "Complaint filed, funds are now held for review",
                }
            )
        else:
            return flask.jsonify({"error": result["error"]}), 400

    except Exception as e:
        return flask.jsonify({"error": str(e)}), 500


@insta485.app.route("/api/transactions/<int:transaction_id>/status", methods=["GET"])
def get_transaction_status_api(transaction_id):
    """
    Get current transaction status

    GET /api/transactions/123/status
    """
    try:
        connection = insta485.model.get_db()
        transaction = connection.execute(
            """
            SELECT t.*, e.name as event_name, e.location as event_location,
                   e.event_datetime
            FROM transactions t
            JOIN events e ON t.event_id = e.event_id
            WHERE t.transaction_id = ?
        """,
            (transaction_id,),
        ).fetchone()

        if not transaction:
            return flask.jsonify({"error": "Transaction not found"}), 404

        # Convert to dict and handle datetime serialization
        result = dict(transaction)
        for key, value in result.items():
            if isinstance(value, datetime):
                result[key] = value.isoformat()

        return flask.jsonify({"success": True, "transaction": result})

    except Exception as e:
        return flask.jsonify({"error": str(e)}), 500


@insta485.app.route("/webhook/email/ticket/<int:transaction_id>", methods=["POST"])
def receive_ticket_email(transaction_id):
    """
    Webhook endpoint for receiving ticket emails
    Called by email service when email sent to ticket-{id}@safetransaction.com
    """
    try:
        # Parse incoming email data
        email_data = {
            "sender": flask.request.form.get("sender"),
            "subject": flask.request.form.get("subject"),
            "body": flask.request.form.get("body-plain", ""),
            "html_body": flask.request.form.get("body-html", ""),
            "attachments": [],  # Handle attachments if needed
            "received_time": datetime.now(),
        }

        # Process through transaction manager
        transaction_manager = TransactionManager()
        result = transaction_manager.process_incoming_ticket(
            transaction_id=transaction_id, email_data=email_data
        )

        if result["success"]:
            return flask.jsonify(
                {
                    "success": True,
                    "message": "Ticket processed successfully",
                    "verification_score": result["verification_score"],
                }
            )
        else:
            return flask.jsonify({"error": result["error"]}), 400

    except Exception as e:
        return flask.jsonify({"error": str(e)}), 500


# REMOVED: /pay/<transaction_id> route - consolidated into /ticket/<transaction_id> route
# All payment links now use /ticket/<transaction_id> for consistency and better security


@insta485.app.route("/payment/complete/<int:transaction_id>")
def payment_complete(transaction_id):
    """
    Handle successful payment return from Stripe Checkout
    """
    try:
        # Update transaction status to indicate payment received
        connection = insta485.model.get_db()
        connection.execute(
            """
            UPDATE transactions 
            SET payment_received = 1,
                payment_received_time = CURRENT_TIMESTAMP,
                status = 'waiting_for_payment_processing'
            WHERE transaction_id = ?
        """,
            (transaction_id,),
        )
        connection.commit()

        # Redirect to ticket status page
        return flask.redirect(
            flask.url_for("show_ticket_status", transaction_id=transaction_id)
        )

    except Exception as e:
        return flask.render_template(
            "payment_error.html", error=f"Payment processing error: {str(e)}"
        )


# REMOVED: Duplicate /ticket/<int:transaction_id> route - now handled by ticket_status_check route
# This was conflicting with the main route in views/index.py


# Background job endpoint (for cron/scheduler)
@insta485.app.route("/api/background/check-deadlines", methods=["POST"])
def run_deadline_check():
    """
    Manually trigger deadline check (for cron jobs)
    """
    try:
        transaction_manager = TransactionManager()
        transaction_manager.check_scheduled_deadlines()

        return flask.jsonify({"success": True, "message": "Deadline check completed"})

    except Exception as e:
        return flask.jsonify({"error": str(e)}), 500


# Testing endpoint for simulation
@insta485.app.route(
    "/api/transactions/<int:transaction_id>/simulate-verification", methods=["POST"]
)
def simulate_verification(transaction_id):
    """
    Testing endpoint: Simulate ticket email verification process
    This bypasses the email monitoring and directly processes a fake ticket email
    """
    try:
        email_data = flask.request.get_json()

        if not email_data:
            return flask.jsonify({"success": False, "error": "No email data provided"})

        # Use TransactionManager to process the simulated ticket
        transaction_manager = TransactionManager()
        result = transaction_manager.process_incoming_ticket(transaction_id, email_data)

        if result["success"]:
            logger.info(
                f"🧪 SIMULATION: Transaction {transaction_id} activated successfully"
            )
            logger.info("📧 SIMULATION: Buyer notification would be sent")
            logger.info(
                f"⏰ SIMULATION: Payment deadline set to {result.get('payment_deadline', 'N/A')}"
            )
            logger.info(
                f"🔍 SIMULATION: Verification score: {result.get('verification_score', 'N/A')}"
            )

            return flask.jsonify(
                {
                    "success": True,
                    "status": result.get("status", "listing_activated"),
                    "payment_deadline": result.get("payment_deadline"),
                    "verification_score": result.get("verification_score"),
                }
            )
        else:
            return flask.jsonify(
                {"success": False, "error": result.get("error", "Unknown error")}
            )

    except Exception as e:
        logger.error(f"❌ SIMULATION ERROR: {e}")
        return flask.jsonify({"success": False, "error": str(e)})


# Testing endpoint for direct verification
@insta485.app.route(
    "/api/transactions/<int:transaction_id>/mark-verified", methods=["POST"]
)
def mark_as_verified(transaction_id):
    """
    Testing endpoint: Directly mark transaction as verified and activate listing
    This bypasses both email sending and verification, directly setting status to waiting_for_payment
    """
    try:
        connection = insta485.model.get_db()

        # Get transaction details
        transaction = connection.execute(
            "SELECT * FROM transactions WHERE transaction_id = ?", (transaction_id,)
        ).fetchone()

        if not transaction:
            return flask.jsonify({"success": False, "error": "Transaction not found"})

        # Must be in pending state
        if transaction["status"] != "pending_ticket_submission":
            return flask.jsonify(
                {
                    "success": False,
                    "error": f"Transaction in wrong state: {transaction['status']}",
                }
            )

        # Set 1-hour payment deadline
        payment_deadline = datetime.now() + timedelta(hours=1)

        # Format payment deadline for SQLite (no microseconds, space instead of T)
        payment_deadline_str = payment_deadline.strftime("%Y-%m-%d %H:%M:%S")

        # Mark as verified and activate listing
        connection.execute(
            """
            UPDATE transactions 
            SET status = 'waiting_for_payment',
                ticket_email_received = 1,
                ticket_received_time = CURRENT_TIMESTAMP,
                ticket_verification_score = 100,
                ticket_details_match = 1,
                verification_notes = 'TEST: Manually marked as verified',
                created_time = CURRENT_TIMESTAMP,
                payment_deadline = ?
            WHERE transaction_id = ?
        """,
            (payment_deadline_str, transaction_id),
        )

        connection.commit()

        # Send buyer notification (same as in verification flow)
        try:
            from insta485.email_automation import send_modern_buyer_notification

            original_details = json.loads(transaction["original_event_details"])

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
                f"📧 TEST: Buyer notification sent to {transaction['buyer_email']}"
            )
        except Exception as e:
            logger.error(f"📧 TEST: Failed to send buyer notification: {e}")
            import traceback

            traceback.print_exc()

        logger.info(
            f"✅ TEST: Transaction {transaction_id} manually marked as verified and activated"
        )
        logger.info(f"⏰ TEST: Payment deadline set to {payment_deadline}")

        return flask.jsonify(
            {
                "success": True,
                "status": "waiting_for_payment",
                "payment_deadline": payment_deadline_str,
                "verification_score": 100,
                "message": "Listing manually verified and activated",
            }
        )

    except Exception as e:
        logger.error(f"❌ TEST ERROR: {e}")
        return flask.jsonify({"success": False, "error": str(e)})


# New Test Verify API endpoint
@insta485.app.route("/api/test-verify", methods=["POST"])
def test_verify_transaction():
    """
    ⚡ TEST: Mark as Verified - Testing endpoint
    Instantly marks a transaction as verified and sends buyer notification,
    bypassing the normal email verification flow.

    POST /api/test-verify
    {
        "transaction_id": 123,
        "test_mode": true
    }
    """
    try:
        data = flask.request.get_json()

        if not data or "transaction_id" not in data:
            return flask.jsonify({"success": False, "error": "Missing transaction_id"})

        transaction_id = data["transaction_id"]
        connection = insta485.model.get_db()

        # Get transaction details
        transaction = connection.execute(
            "SELECT * FROM transactions WHERE transaction_id = ?", (transaction_id,)
        ).fetchone()

        if not transaction:
            return flask.jsonify({"success": False, "error": "Transaction not found"})

        # Must be in pending_ticket_submission state
        if transaction["status"] != "pending_ticket_submission":
            return flask.jsonify(
                {
                    "success": False,
                    "error": f"Transaction must be in pending_ticket_submission state. Current: {transaction['status']}",
                }
            )

        # Set 1-hour payment deadline from now
        payment_deadline = datetime.now() + timedelta(hours=1)
        payment_deadline_str = payment_deadline.strftime("%Y-%m-%d %H:%M:%S")

        # Update transaction: instant verification (100%) and move to waiting_for_payment
        connection.execute(
            """
            UPDATE transactions 
            SET status = 'waiting_for_payment',
                ticket_email_received = 1,
                ticket_received_time = CURRENT_TIMESTAMP,
                ticket_verification_score = 100,
                ticket_details_match = 1,
                verification_notes = '⚡ TEST: Instant verification via Test Verify button',
                payment_deadline = ?
            WHERE transaction_id = ?
        """,
            (payment_deadline_str, transaction_id),
        )

        connection.commit()

        # Send notifications using new Mailgun system
        try:
            original_details = json.loads(transaction["original_event_details"])

            # NOTE: Seller success email now sent after payment, not after verification

            # 2. Send PAYMENT notification to BUYER

            # Parse datetime if it's a string
            event_datetime = original_details.get("datetime", "TBD")
            if isinstance(event_datetime, str) and event_datetime != "TBD":
                try:
                    event_datetime = datetime.strptime(
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
                f"📧 TEST VERIFY: Notifications sent to seller ({transaction['seller_email']}) and buyer ({transaction['buyer_email']})"
            )
            email_sent = True

        except Exception as e:
            logger.error(f"📧 TEST VERIFY: Failed to send buyer notification: {e}")
            import traceback

            traceback.print_exc()
            email_sent = False

        # Log the test verification
        logger.info(f"⚡ TEST VERIFY: Transaction {transaction_id} instantly verified")
        logger.info("📈 TEST VERIFY: Verification score set to 100%")
        logger.info(f"⏰ TEST VERIFY: Payment deadline set to {payment_deadline}")
        logger.info(
            "🔄 TEST VERIFY: Status: pending_ticket_submission → waiting_for_payment"
        )

        return flask.jsonify(
            {
                "success": True,
                "message": "⚡ TEST VERIFICATION COMPLETE",
                "details": {
                    "verification_score": 100,
                    "status_change": "pending_ticket_submission → waiting_for_payment",
                    "payment_deadline": payment_deadline_str,
                    "buyer_notification_sent": email_sent,
                    "test_metadata": {
                        "verification_method": "test_verify_button",
                        "instant_verification": True,
                        "bypass_email_flow": True,
                    },
                },
            }
        )

    except Exception as e:
        logger.error(f"❌ TEST VERIFY ERROR: {e}")
        import traceback

        traceback.print_exc()
        return flask.jsonify({"success": False, "error": str(e)})


# API endpoint to get transaction status
@insta485.app.route("/api/transactions/<int:transaction_id>/status", methods=["GET"])
def get_transaction_status(transaction_id):
    """
    Get current transaction status and details
    """
    try:
        connection = insta485.model.get_db()

        # Get transaction details with event info
        transaction = connection.execute(
            """
            SELECT t.*, e.name as event_name, e.location as event_location
            FROM transactions t
            LEFT JOIN events e ON t.event_id = e.event_id
            WHERE t.transaction_id = ?
            """,
            (transaction_id,),
        ).fetchone()

        if not transaction:
            return flask.jsonify({"success": False, "error": "Transaction not found"})

        # Convert row to dict for JSON serialization
        transaction_dict = dict(transaction)

        return flask.jsonify({"success": True, "transaction": transaction_dict})

    except Exception as e:
        logger.error(f"❌ STATUS API ERROR: {e}")
        return flask.jsonify({"success": False, "error": str(e)})


@insta485.app.route(
    "/api/transactions/<int:transaction_id>/simulate-ticket-sent", methods=["POST"]
)
def simulate_ticket_sent(transaction_id):
    """
    Simulate TicketVault transferring ticket to buyer and send congratulations email to seller
    """
    try:
        connection = insta485.model.get_db()

        # Get transaction details
        transaction = connection.execute(
            """
            SELECT t.*, e.name as event_name, e.location, e.event_datetime
            FROM transactions t
            LEFT JOIN events e ON t.event_id = e.event_id
            WHERE t.transaction_id = ?
            """,
            (transaction_id,),
        ).fetchone()

        if not transaction:
            return flask.jsonify({"success": False, "error": "Transaction not found"})

        # Check if transaction is in a valid state for ticket simulation
        valid_statuses = [
            "waiting_for_ticket",
            "waiting_for_payment",
            "waiting_for_payment_processing",
        ]
        if transaction["status"] not in valid_statuses:
            return flask.jsonify(
                {
                    "success": False,
                    "error": f"Cannot simulate ticket transfer for status: {transaction['status']}",
                }
            )

        # Update transaction status to simulate ticket transfer completion
        connection.execute(
            """
            UPDATE transactions 
            SET status = 'ticket_forwarded_funds_held'
            WHERE transaction_id = ?
            """,
            (transaction_id,),
        )
        connection.commit()

        # Send congratulations email to seller
        try:
            from insta485.mailgun_sender import mailgun_sender

            # Format event datetime
            from datetime import datetime

            try:
                event_dt = datetime.strptime(
                    transaction["event_datetime"], "%Y-%m-%d %H:%M:%S"
                )
                event_datetime_str = event_dt.strftime("%A, %b %d, %Y at %I:%M %p")
            except (ValueError, TypeError):
                event_datetime_str = (
                    str(transaction["event_datetime"])
                    if transaction["event_datetime"]
                    else "TBD"
                )

            # Send ticket received email to buyer
            mailgun_sender.send_ticket_transfer_congratulations(
                buyer_email=transaction["buyer_email"],
                transaction_id=transaction_id,
                event_name=transaction["event_name"],
                seller_email=transaction["seller_email"],
                event_datetime_str=event_datetime_str,
            )

            logger.info(
                f"📧 Sent ticket received email to buyer {transaction['buyer_email']}"
            )

        except Exception as e:
            logger.error(f"❌ Failed to send congratulations email: {e}")
            # Don't fail the whole operation if email fails

        return flask.jsonify(
            {
                "success": True,
                "message": "Ticket transfer simulated successfully",
                "new_status": "ticket_forwarded_funds_held",
            }
        )

    except Exception as e:
        logger.error(f"❌ SIMULATE TICKET SENT API ERROR: {e}")
        return flask.jsonify({"success": False, "error": str(e)})


@insta485.app.route("/api/ticket-verification", methods=["POST"])
def ticket_verification():
    """Handle ticket verification from seller dashboard."""
    try:
        data = flask.request.get_json()
        if not data or "transaction_id" not in data or "action" not in data:
            return flask.jsonify(
                {"success": False, "error": "Missing required data"}
            ), 400

        transaction_id = data["transaction_id"]
        action = data["action"]  # 'correct' or 'incorrect'

        connection = insta485.model.get_db()

        # Get transaction details
        transaction = connection.execute(
            """SELECT t.*, e.name as event_name, e.location, e.event_datetime
               FROM transactions t 
               JOIN events e ON t.event_id = e.event_id
               WHERE t.transaction_id = ?""",
            (transaction_id,),
        ).fetchone()

        if not transaction:
            return flask.jsonify(
                {"success": False, "error": "Transaction not found"}
            ), 404

        if transaction["status"] != "waiting_for_ticket":
            return flask.jsonify(
                {"success": False, "error": f"Invalid status: {transaction['status']}"}
            ), 400

        if action == "incorrect":
            # Mark ticket as incorrect and cancel transaction
            connection.execute(
                "UPDATE transactions SET status = 'cancelled_by_seller', verification_notes = ? WHERE transaction_id = ?",
                ("Seller marked ticket as incorrect", transaction_id),
            )
            connection.commit()

            return flask.jsonify(
                {
                    "success": True,
                    "message": "Transaction cancelled due to incorrect ticket",
                }
            )

        elif action == "correct":
            # Mark ticket as verified and set payment deadline (1 hour from now)
            from datetime import datetime, timedelta

            payment_deadline = datetime.now() + timedelta(hours=1)
            payment_deadline_str = payment_deadline.strftime("%Y-%m-%d %H:%M:%S")

            connection.execute(
                """UPDATE transactions 
                   SET status = 'waiting_for_payment',
                       ticket_verification_score = 100,
                       ticket_details_match = 1,
                       verification_notes = 'Seller confirmed ticket is correct',
                       payment_deadline = ?
                   WHERE transaction_id = ?""",
                (payment_deadline_str, transaction_id),
            )
            connection.commit()

            # Send payment email to buyer
            from insta485.views.index import send_buyer_email_1

            send_buyer_email_1(
                transaction_id=transaction_id,
                buyer_email=transaction["buyer_email"],
                event_name=transaction["event_name"],
                price=transaction["price"],
                seller_email=transaction["seller_email"],
                payment_deadline=payment_deadline,
            )

            # Seller will see deadline on their dashboard - no email needed

            return flask.jsonify(
                {
                    "success": True,
                    "message": "Ticket verified! Buyer notified and payment deadline set.",
                    "payment_deadline": payment_deadline_str,
                }
            )

        else:
            return flask.jsonify({"success": False, "error": "Invalid action"}), 400

    except Exception as e:
        logger.error(f"❌ TICKET VERIFICATION ERROR: {e}")
        return flask.jsonify({"success": False, "error": str(e)}), 500


@insta485.app.route("/api/transactions/<int:transaction_id>/cancel", methods=["POST"])
def cancel_transaction_api(transaction_id):
    """Cancel a transaction via API."""
    try:
        if "email" not in flask.session:
            return flask.jsonify({"success": False, "error": "Not logged in"}), 401

        connection = insta485.model.get_db()

        # Get transaction details and verify ownership
        transaction = connection.execute(
            """SELECT seller_email, buyer_email, status 
               FROM transactions 
               WHERE transaction_id = ?""",
            (transaction_id,),
        ).fetchone()

        if not transaction:
            return flask.jsonify(
                {"success": False, "error": "Transaction not found"}
            ), 404

        user_email = flask.session["email"]

        # Only sellers can cancel transactions
        if user_email != transaction["seller_email"]:
            return flask.jsonify(
                {"success": False, "error": "Only sellers can cancel transactions"}
            ), 403

        # Check if transaction can be cancelled
        cancellable_statuses = [
            "waiting_for_ticket",
            "waiting_for_payment",
            "pending_ticket_submission",
        ]
        if transaction["status"] not in cancellable_statuses:
            return flask.jsonify(
                {
                    "success": False,
                    "error": f"Cannot cancel transaction with status: {transaction['status']}",
                }
            ), 400

        # Set status as cancelled by seller
        new_status = "cancelled_by_seller"
        cancel_reason = "Seller cancelled the transaction"

        # Update transaction status
        connection.execute(
            """UPDATE transactions 
               SET status = ?, verification_notes = ? 
               WHERE transaction_id = ?""",
            (new_status, cancel_reason, transaction_id),
        )
        connection.commit()

        # Get transaction details for email
        transaction_details = connection.execute(
            """SELECT t.*, e.name as event_name, e.location, e.event_datetime
               FROM transactions t 
               JOIN events e ON t.event_id = e.event_id
               WHERE t.transaction_id = ?""",
            (transaction_id,),
        ).fetchone()

        # Send cancellation emails (only seller can cancel)
        if transaction_details:
            send_cancellation_emails(
                transaction_id=transaction_id,
                seller_email=transaction_details["seller_email"],
                buyer_email=transaction_details["buyer_email"],
                event_name=transaction_details["event_name"],
                event_location=transaction_details["location"],
                event_datetime=transaction_details["event_datetime"],
                price=transaction_details["price"],
                cancelled_by=transaction_details[
                    "seller_email"
                ],  # Always seller since only sellers can cancel
            )

        logger.info(
            f"[CANCEL] Transaction {transaction_id} cancelled by {user_email}: {new_status}"
        )

        return flask.jsonify(
            {
                "success": True,
                "message": "Transaction cancelled successfully",
                "new_status": new_status,
            }
        )

    except Exception as e:
        logger.error(f"❌ CANCEL TRANSACTION ERROR: {e}")
        return flask.jsonify({"success": False, "error": str(e)}), 500


def send_cancellation_emails(
    transaction_id,
    seller_email,
    buyer_email,
    event_name,
    event_location,
    event_datetime,
    price,
    cancelled_by,
):
    """Send cancellation notification emails to both buyer and seller."""
    try:
        from flask_mail import Message
        import insta485
        import datetime

        # Format event datetime nicely
        try:
            event_dt = datetime.datetime.strptime(event_datetime, "%Y-%m-%d %H:%M:%S")
            formatted_datetime = event_dt.strftime("%A, %B %d, %Y at %I:%M %p")
        except:
            formatted_datetime = event_datetime

        # Only sellers can cancel, so this is always a seller cancellation
        cancellation_message = (
            "<p><strong>The seller has cancelled this transaction.</strong></p>"
        )
        next_steps_section = '<div class="next-steps"><h3>🚀 What You Can Do Next:</h3><ul><li>Contact the seller to see if they can create a new listing</li><li>Look for other tickets to the same event on TicketVault</li><li>All new listings come with our full security guarantee</li></ul></div>'

        # Email to Buyer
        buyer_subject = f"🚫 Transaction Cancelled - {event_name}"

        buyer_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #ef4444, #dc2626); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: white; padding: 30px; border: 1px solid #ddd; border-top: none; }}
                .event-details {{ background: #f8fafc; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .cancellation-notice {{ background: #fef2f2; padding: 20px; border-radius: 8px; border-left: 4px solid #ef4444; margin: 20px 0; }}
                .apology-section {{ background: #fff7ed; padding: 20px; border-radius: 8px; border-left: 4px solid #f59e0b; margin: 20px 0; }}
                .next-steps {{ background: #ecfdf5; padding: 20px; border-radius: 8px; border-left: 4px solid #10b981; margin: 20px 0; }}
                .footer {{ text-align: center; padding: 20px; color: #666; font-size: 14px; }}
                ul {{ list-style-type: none; padding: 0; }}
                li {{ margin: 8px 0; }}
                li:before {{ content: "✓ "; color: #10b981; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🛡️ TicketVault</h1>
                    <p>Transaction Cancellation Notice</p>
                </div>
                <div class="content">
                    <div class="cancellation-notice">
                        <h2>🚫 Transaction Cancelled</h2>
                        {cancellation_message}
                    </div>
                    
                    <h3>📋 Transaction Details:</h3>
                    <div class="event-details">
                        <ul>
                            <li><strong>Event:</strong> {event_name}</li>
                            <li><strong>Location:</strong> {event_location}</li>
                            <li><strong>Date:</strong> {formatted_datetime}</li>
                            <li><strong>Price:</strong> ${price}</li>
                            <li><strong>Transaction ID:</strong> ST-{transaction_id}</li>
                        </ul>
                    </div>
                    
                    <div class="apology-section">
                        <h3>💝 We're Sorry This Didn't Work Out</h3>
                        <p>We understand how disappointing this can be, especially when you're looking forward to an event.</p>
                        <p>Sometimes plans change, and we appreciate your understanding during this process.</p>
                    </div>
                    
                    {next_steps_section}
                </div>
                <div class="footer">
                    <p>TicketVault - Secure Ticket Marketplace</p>
                    <p>Questions? Contact us anytime for support.</p>
                </div>
            </div>
        </body>
        </html>
        """

        # Prepare text email content
        # Only sellers can cancel
        text_intro = "🚫 The seller has cancelled your transaction for:"
        text_next_steps = """🚀 What You Can Do Next:
• Contact the seller for a potential new listing
• Look for other tickets on TicketVault
• All new listings come with our security guarantee"""

        buyer_text = f"""
        🛡️ TICKETVAULT - Transaction Cancelled
        
        {text_intro}
        
        📋 Event Details:
        • Event: {event_name}
        • Location: {event_location}
        • Date: {formatted_datetime}
        • Price: ${price}
        • Transaction ID: ST-{transaction_id}
        
        💝 We're Sorry This Didn't Work Out
        We understand how disappointing this can be, especially when you're looking forward to an event.
        
        {text_next_steps}
        
        TicketVault Team
        """

        # Email to Seller
        seller_subject = f"✅ Transaction Cancelled - {event_name}"

        seller_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: white; padding: 30px; border: 1px solid #ddd; border-top: none; }}
                .event-details {{ background: #f8fafc; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .confirmation-notice {{ background: #ecfdf5; padding: 20px; border-radius: 8px; border-left: 4px solid #10b981; margin: 20px 0; }}
                .next-steps {{ background: #fff7ed; padding: 20px; border-radius: 8px; border-left: 4px solid #f59e0b; margin: 20px 0; }}
                .footer {{ text-align: center; padding: 20px; color: #666; font-size: 14px; }}
                ul {{ list-style-type: none; padding: 0; }}
                li {{ margin: 8px 0; }}
                li:before {{ content: "✓ "; color: #10b981; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🛡️ TicketVault</h1>
                    <p>Cancellation Confirmation</p>
                </div>
                <div class="content">
                    <div class="confirmation-notice">
                        <h2>✅ Transaction Cancelled Successfully</h2>
                        <p><strong>You have cancelled the transaction and your ticket is now available again.</strong></p>
                    </div>
                    
                    <h3>📋 Cancelled Transaction Details:</h3>
                    <div class="event-details">
                        <ul>
                            <li><strong>Event:</strong> {event_name}</li>
                            <li><strong>Location:</strong> {event_location}</li>
                            <li><strong>Date:</strong> {formatted_datetime}</li>
                            <li><strong>Price:</strong> ${price}</li>
                            <li><strong>Buyer:</strong> {buyer_email}</li>
                            <li><strong>Transaction ID:</strong> ST-{transaction_id}</li>
                        </ul>
                    </div>
                    
                    <div class="next-steps">
                        <h3>🚀 What Happens Next:</h3>
                        <ul>
                            <li>Your ticket is now available for a new listing</li>
                            <li>The buyer has been notified of the cancellation</li>
                            <li>You can create a new listing anytime on TicketVault</li>
                            <li>If the buyer is still interested, they may contact you directly</li>
                        </ul>
                    </div>
                    
                    <p style="text-align: center; margin: 30px 0;">
                        We're sorry this transaction didn't work out as planned.<br>
                        Thank you for using TicketVault's secure platform.
                    </p>
                </div>
                <div class="footer">
                    <p>TicketVault - Secure Ticket Marketplace</p>
                    <p>Questions? Contact us anytime for support.</p>
                </div>
            </div>
        </body>
        </html>
        """

        seller_text = f"""
        🛡️ TICKETVAULT - Cancellation Confirmation
        
        ✅ You have successfully cancelled your transaction for:
        
        📋 Cancelled Transaction Details:
        • Event: {event_name}
        • Location: {event_location}
        • Date: {formatted_datetime}
        • Price: ${price}
        • Buyer: {buyer_email}
        • Transaction ID: ST-{transaction_id}
        
        🚀 What Happens Next:
        • Your ticket is now available for a new listing
        • The buyer has been notified of the cancellation
        • You can create a new listing anytime on TicketVault
        • If the buyer is still interested, they may contact you directly
        
        We're sorry this transaction didn't work out as planned.
        Thank you for using TicketVault's secure platform.
        
        TicketVault Team
        """

        # Send buyer email
        buyer_msg = Message(
            subject=buyer_subject,
            recipients=[buyer_email],
            html=buyer_html,
            body=buyer_text,
        )
        insta485.mail.send(buyer_msg)

        # Send seller email
        seller_msg = Message(
            subject=seller_subject,
            recipients=[seller_email],
            html=seller_html,
            body=seller_text,
        )
        insta485.mail.send(seller_msg)

        logger.info(f"📧 Sent cancellation emails for transaction {transaction_id}")
        logger.info(f"   - Buyer email sent to: {buyer_email}")
        logger.info(f"   - Seller email sent to: {seller_email}")

    except Exception as e:
        logger.error(
            f"❌ Failed to send cancellation emails for transaction {transaction_id}: {e}"
        )


@insta485.app.route("/api/test-ticket-sent", methods=["POST"])
def test_ticket_sent():
    """Test endpoint to simulate seller marking ticket as sent."""
    if "email" not in flask.session:
        return flask.jsonify({"success": False, "error": "Not logged in"}), 401

    data = flask.request.get_json()
    transaction_id = data.get("transaction_id")

    if not transaction_id:
        return flask.jsonify(
            {"success": False, "error": "Transaction ID required"}
        ), 400

    try:
        connection = insta485.model.get_db()

        # Get transaction details
        transaction = connection.execute(
            """
            SELECT t.*, e.name as event_name, e.location, e.event_datetime
            FROM transactions t 
            JOIN events e ON t.event_id = e.event_id
            WHERE t.transaction_id = ? AND t.seller_email = ?
        """,
            (transaction_id, flask.session["email"]),
        ).fetchone()

        if not transaction:
            return flask.jsonify(
                {"success": False, "error": "Transaction not found or access denied"}
            ), 404

        # Check if transaction is in correct status
        if transaction["status"] != "pending_ticket_submission":
            return flask.jsonify(
                {
                    "success": False,
                    "error": f"Transaction is in status: {transaction['status']}. Expected: pending_ticket_submission",
                }
            ), 400

        # Update status to waiting_for_verification (seller confirms they sent ticket to TicketVault)
        # Also set ticket_email_received to 1 to mark that we received the ticket
        connection.execute(
            "UPDATE transactions SET status = 'waiting_for_verification', ticket_email_received = 1, ticket_received_time = CURRENT_TIMESTAMP WHERE transaction_id = ?",
            (transaction_id,),
        )
        connection.commit()

        return flask.jsonify(
            {
                "success": True,
                "message": "Ticket marked as sent successfully",
                "new_status": "waiting_for_verification",
            }
        )

    except Exception as e:
        logger.error(f"Error in test-ticket-sent: {e}")
        return flask.jsonify({"success": False, "error": str(e)}), 500
