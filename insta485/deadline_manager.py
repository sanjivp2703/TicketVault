"""
Deadline Management System for TicketVault
Handles all automated deadline checking and actions
"""

import time
import threading
from datetime import datetime, timedelta
import insta485
from insta485.email_automation import (
    send_ticket_deadline_reminder,
    send_payment_deadline_reminder,
    send_listing_expired_notification,
    send_ticket_returned_notification,
)
import logging

logger = logging.getLogger(__name__)


class DeadlineManager:
    """Manages all transaction deadlines and automated actions"""

    def __init__(self):
        self.running = False
        self.thread = None

    def start(self):
        """Start the deadline monitoring background thread"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._monitor_deadlines, daemon=True)
            self.thread.start()
            logger.info("🕒 Deadline Manager started")

    def stop(self):
        """Stop the deadline monitoring"""
        self.running = False
        if self.thread:
            self.thread.join()
        logger.info("🕒 Deadline Manager stopped")

    def _monitor_deadlines(self):
        """Main monitoring loop - runs every 30 seconds"""
        while self.running:
            try:
                with insta485.app.app_context():
                    connection = insta485.model.get_db()
                    self._check_ticket_deadlines(connection)
                    self._check_payment_deadlines(connection)
                    self._send_deadline_reminders(connection)
                time.sleep(30)  # Check every 30 seconds
            except Exception as e:
                logger.error(f"Error in deadline monitoring: {e}")
                time.sleep(60)  # Wait longer on error

    def _check_ticket_deadlines(self, connection):
        """Check for expired ticket deadlines"""
        now = datetime.now()

        # Find transactions where ticket deadline has passed
        expired_tickets = connection.execute(
            """
            SELECT transaction_id, seller_email, buyer_email, ticket_deadline
            FROM transactions 
            WHERE status = 'waiting_for_ticket' 
            AND ticket_deadline < ?
            """,
            (now.isoformat(),),
        ).fetchall()

        for transaction in expired_tickets:
            from insta485.error_handler import error_handler

            error_handler.handle_ticket_timeout(transaction["transaction_id"])
            logger.info(
                f"⏰ Expired listing {transaction['transaction_id']} - no tickets received"
            )

    def _check_payment_deadlines(self, connection):
        """Check for expired payment deadlines"""
        now = datetime.now()

        # Find transactions where payment deadline has passed
        expired_payments = connection.execute(
            """
            SELECT transaction_id, seller_email, buyer_email, payment_deadline
            FROM transactions 
            WHERE status = 'waiting_for_payment' 
            AND payment_deadline < ?
            """,
            (now.isoformat(),),
        ).fetchall()

        for transaction in expired_payments:
            from insta485.error_handler import error_handler

            error_handler.handle_payment_timeout(transaction["transaction_id"])
            logger.info(
                f"⏰ Returned tickets for transaction {transaction['transaction_id']} - no payment received"
            )

    def _send_deadline_reminders(self, connection):
        """Send reminder emails before deadlines"""
        now = datetime.now()

        # Ticket deadline reminders (2 minutes before)
        ticket_reminders = connection.execute(
            """
            SELECT t.transaction_id, t.seller_email, t.ticket_deadline, e.name as event_name
            FROM transactions t
            JOIN events e ON t.event_id = e.event_id
            WHERE t.status = 'waiting_for_ticket' 
            AND t.ticket_deadline > ?
            AND t.ticket_deadline <= ?
            AND t.ticket_reminder_sent_2h = 0
            """,
            (now.isoformat(), (now + timedelta(minutes=2)).isoformat()),
        ).fetchall()

        for reminder in ticket_reminders:
            minutes_left = (
                datetime.fromisoformat(reminder["ticket_deadline"]) - now
            ).total_seconds() / 60
            ticket_email = f"tx-{reminder['transaction_id']:06d}@safetransaction.com"

            send_ticket_deadline_reminder(
                reminder["transaction_id"],
                reminder["seller_email"],
                minutes_left / 60,  # Convert to hours for compatibility
                ticket_email,
                reminder["event_name"],
            )

            # Mark reminder as sent
            connection.execute(
                "UPDATE transactions SET ticket_reminder_sent_2h = 1 WHERE transaction_id = ?",
                (reminder["transaction_id"],),
            )
            connection.commit()

        # Payment deadline reminders (1 minute before)
        payment_reminders = connection.execute(
            """
            SELECT t.transaction_id, t.buyer_email, t.payment_deadline, e.name as event_name
            FROM transactions t
            JOIN events e ON t.event_id = e.event_id
            WHERE t.status = 'waiting_for_payment' 
            AND t.payment_deadline > ?
            AND t.payment_deadline <= ?
            AND t.payment_reminder_sent_1h = 0
            """,
            (now.isoformat(), (now + timedelta(minutes=1)).isoformat()),
        ).fetchall()

        for reminder in payment_reminders:
            minutes_left = (
                datetime.fromisoformat(reminder["payment_deadline"]) - now
            ).total_seconds() / 60

            send_payment_deadline_reminder(
                reminder["transaction_id"],
                reminder["buyer_email"],
                minutes_left / 60,  # Convert to hours for compatibility
                f"http://localhost:8000/ticket/{reminder['transaction_id']}",
                reminder["event_name"],
            )

            # Mark reminder as sent
            connection.execute(
                "UPDATE transactions SET payment_reminder_sent_1h = 1 WHERE transaction_id = ?",
                (reminder["transaction_id"],),
            )
            connection.commit()

    def _expire_listing_no_tickets(self, transaction_id, connection):
        """Expire listing when seller doesn't send tickets in time"""
        # Get transaction details
        transaction = connection.execute(
            """
            SELECT t.*, e.name as event_name
            FROM transactions t
            JOIN events e ON t.event_id = e.event_id
            WHERE t.transaction_id = ?
            """,
            (transaction_id,),
        ).fetchone()

        if not transaction:
            return

        # Update status
        connection.execute(
            """
            UPDATE transactions 
            SET status = 'expired_no_ticket'
            WHERE transaction_id = ?
            """,
            (transaction_id,),
        )
        connection.commit()

        # Send notifications
        send_listing_expired_notification(
            transaction_id,
            transaction["seller_email"],
            "ticket_deadline",
            transaction["event_name"],
        )

        send_listing_expired_notification(
            transaction_id,
            transaction["buyer_email"],
            "ticket_deadline",
            transaction["event_name"],
        )

    def _return_tickets_to_seller(self, transaction_id, connection):
        """Return tickets to seller when buyer doesn't pay in time"""
        # Get transaction details
        transaction = connection.execute(
            """
            SELECT t.*, e.name as event_name
            FROM transactions t
            JOIN events e ON t.event_id = e.event_id
            WHERE t.transaction_id = ?
            """,
            (transaction_id,),
        ).fetchone()

        if not transaction:
            return

        # Update status
        connection.execute(
            """
            UPDATE transactions 
            SET status = 'expired_no_payment'
            WHERE transaction_id = ?
            """,
            (transaction_id,),
        )
        connection.commit()

        # Send notifications
        send_ticket_returned_notification(
            transaction_id,
            transaction["seller_email"],
            "payment_deadline",
            transaction["event_name"],
        )

        send_listing_expired_notification(
            transaction_id,
            transaction["buyer_email"],
            "payment_deadline",
            transaction["event_name"],
        )

        # TODO: Forward original ticket email back to seller
        # This would require storing the original email and forwarding it
        logger.info(
            f"📧 Need to return original ticket email to {transaction['seller_email']}"
        )


# Global deadline manager instance
deadline_manager = DeadlineManager()


def start_deadline_monitoring():
    """Start the global deadline monitoring"""
    deadline_manager.start()


def stop_deadline_monitoring():
    """Stop the global deadline monitoring"""
    deadline_manager.stop()


# Auto-start when module is imported in production
import os

if os.environ.get("FLASK_ENV") != "development":
    start_deadline_monitoring()
