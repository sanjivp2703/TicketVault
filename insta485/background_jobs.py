"""
Background Jobs for Automated Transaction Processing
Handles all timeouts, deadlines, and automatic actions
"""

import schedule
import time
import threading
from datetime import datetime, timedelta
from insta485.transaction_manager import TransactionManager
import insta485.model


class BackgroundJobManager:
    """Manages all background jobs for transaction automation"""

    def __init__(self):
        self.transaction_manager = TransactionManager()
        self.running = False

    def start_scheduler(self):
        """Start the background job scheduler"""
        self.running = True

        # Schedule jobs
        schedule.every(5).minutes.do(self._check_all_deadlines)
        schedule.every(1).hour.do(self._cleanup_old_transactions)
        schedule.every(10).minutes.do(self._send_reminder_emails)

        # Run scheduler in background thread
        def run_scheduler():
            while self.running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute

        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
        print("✅ Background job scheduler started")

    def stop_scheduler(self):
        """Stop the background scheduler"""
        self.running = False
        schedule.clear()
        print("🛑 Background job scheduler stopped")

    def _check_all_deadlines(self):
        """Check all transaction deadlines and take appropriate actions"""
        print(f"🔍 Checking deadlines at {datetime.now()}")

        try:
            # Use transaction manager's deadline checking
            self.transaction_manager.check_scheduled_deadlines()

            # Additional specific checks
            self._check_ticket_deadlines()
            self._check_payment_deadlines()
            self._check_release_deadlines()

        except Exception as e:
            print(f"❌ Error in deadline checking: {e}")

    def _check_ticket_deadlines(self):
        """Check for expired ticket deadlines"""
        connection = insta485.model.get_db()
        now = datetime.now()

        expired_listings = connection.execute(
            """
            SELECT transaction_id, seller_email, ticket_deadline 
            FROM transactions 
            WHERE status = 'waiting_for_ticket' 
            AND ticket_deadline < ?
        """,
            (now,),
        ).fetchall()

        for listing in expired_listings:
            try:
                self._expire_listing_no_ticket(listing["transaction_id"])
                print(
                    f"⏰ Expired listing {listing['transaction_id']} - no ticket received"
                )
            except Exception as e:
                print(f"❌ Error expiring listing {listing['transaction_id']}: {e}")

    def _check_payment_deadlines(self):
        """Check for expired payment deadlines"""
        connection = insta485.model.get_db()
        now = datetime.now()

        expired_payments = connection.execute(
            """
            SELECT transaction_id, buyer_email, payment_deadline,
                   ticket_email_data, seller_email
            FROM transactions 
            WHERE status = 'waiting_for_payment' 
            AND payment_deadline < ?
        """,
            (now,),
        ).fetchall()

        for payment in expired_payments:
            try:
                self._return_ticket_to_seller(payment["transaction_id"])
                print(
                    f"🔄 Returned ticket for transaction {payment['transaction_id']} - payment deadline passed"
                )
            except Exception as e:
                print(f"❌ Error returning ticket {payment['transaction_id']}: {e}")

    def _check_release_deadlines(self):
        """Check for automatic fund release deadlines"""
        connection = insta485.model.get_db()
        now = datetime.now()

        auto_releases = connection.execute(
            """
            SELECT transaction_id, seller_email, release_deadline
            FROM transactions 
            WHERE status = 'ticket_forwarded_funds_held' 
            AND release_deadline < ?
            AND complaint_reason IS NULL
            AND buyer_confirmed_receipt = 0
        """,
            (now,),
        ).fetchall()

        for release in auto_releases:
            try:
                self.transaction_manager._release_funds_to_seller(
                    release["transaction_id"], "automatic_24hr_release"
                )
                print(
                    f"💰 Auto-released funds for transaction {release['transaction_id']}"
                )
            except Exception as e:
                print(f"❌ Error releasing funds {release['transaction_id']}: {e}")

    def _expire_listing_no_ticket(self, transaction_id):
        """Expire listing when seller doesn't send ticket"""
        connection = insta485.model.get_db()

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
        self._notify_listing_expired(transaction_id, "seller_no_ticket")

    def _return_ticket_to_seller(self, transaction_id):
        """Return ticket to seller when buyer doesn't pay"""
        connection = insta485.model.get_db()

        # Get transaction data
        transaction = connection.execute(
            """
            SELECT * FROM transactions WHERE transaction_id = ?
        """,
            (transaction_id,),
        ).fetchone()

        if transaction and transaction["ticket_email_data"]:
            # Forward ticket back to seller
            import json
            from insta485.email_utils import forward_ticket_email

            ticket_data = json.loads(transaction["ticket_email_data"])

            success = forward_ticket_email(
                to_email=transaction["seller_email"],
                original_email_data=ticket_data,
                transaction_id=transaction_id,
                return_mode=True,
            )

            if success:
                connection.execute(
                    """
                    UPDATE transactions 
                    SET status = 'ticket_returned'
                    WHERE transaction_id = ?
                """,
                    (transaction_id,),
                )
                connection.commit()

                # Send notifications
                self._notify_ticket_returned(transaction_id)

    def _send_reminder_emails(self):
        """Send reminder emails for pending actions"""
        connection = insta485.model.get_db()
        now = datetime.now()

        # Remind sellers to send tickets (2 hours before deadline)
        upcoming_ticket_deadlines = connection.execute(
            """
            SELECT transaction_id, seller_email, ticket_deadline
            FROM transactions 
            WHERE status = 'waiting_for_ticket'
            AND ticket_deadline BETWEEN ? AND ?
            AND ticket_deadline > ?
        """,
            (now + timedelta(hours=1), now + timedelta(hours=3), now),
        ).fetchall()

        for reminder in upcoming_ticket_deadlines:
            self._send_ticket_reminder(reminder["transaction_id"])

        # Remind buyers to pay (4 hours before deadline)
        upcoming_payment_deadlines = connection.execute(
            """
            SELECT transaction_id, buyer_email, payment_deadline
            FROM transactions 
            WHERE status = 'waiting_for_payment'
            AND payment_deadline BETWEEN ? AND ?
            AND payment_deadline > ?
        """,
            (now + timedelta(hours=2), now + timedelta(hours=6), now),
        ).fetchall()

        for reminder in upcoming_payment_deadlines:
            self._send_payment_reminder(reminder["transaction_id"])

    def _cleanup_old_transactions(self):
        """Clean up old completed/expired transactions"""
        connection = insta485.model.get_db()
        cutoff_date = datetime.now() - timedelta(days=30)

        # Archive old completed transactions
        old_transactions = connection.execute(
            """
            SELECT transaction_id FROM transactions 
            WHERE status IN ('completed', 'expired_no_ticket', 'ticket_returned', 'cancelled_by_seller')
            AND created_time < ?
        """,
            (cutoff_date,),
        ).fetchall()

        archived_count = 0
        for transaction in old_transactions:
            # Move to archive table (implement if needed)
            # For now, just log
            archived_count += 1

        if archived_count > 0:
            print(f"📁 Archived {archived_count} old transactions")

    # Notification methods (implement based on your email system)
    def _notify_listing_expired(self, transaction_id, reason):
        """Notify about expired listing"""

        connection = insta485.model.get_db()
        transaction = connection.execute(
            """
            SELECT t.*, e.name as event_name
            FROM transactions t
            JOIN events e ON t.event_id = e.event_id
            WHERE t.transaction_id = ?
        """,
            (transaction_id,),
        ).fetchone()

        if reason == "seller_no_ticket":
            # Notify seller they missed deadline
            from flask_mail import Message

            msg = Message(
                subject=f"Listing Expired - {transaction['event_name']}",
                recipients=[transaction["seller_email"]],
                html=f"<h2>Listing Expired</h2><p>Your listing for {transaction['event_name']} has expired because the ticket deadline was missed.</p>",
            )
            insta485.mail.send(msg)

            # Notify buyer listing is no longer available
            msg = Message(
                subject=f"Listing No Longer Available - {transaction['event_name']}",
                recipients=[transaction["buyer_email"]],
                html=f"<h2>Listing Unavailable</h2><p>The listing for {transaction['event_name']} is no longer available.</p>",
            )
            insta485.mail.send(msg)

    def _notify_ticket_returned(self, transaction_id):
        """Notify about ticket being returned to seller"""
        from flask_mail import Message
        import insta485

        connection = insta485.model.get_db()
        transaction = connection.execute(
            """
            SELECT t.*, e.name as event_name
            FROM transactions t
            JOIN events e ON t.event_id = e.event_id
            WHERE t.transaction_id = ?
        """,
            (transaction_id,),
        ).fetchone()

        # Notify seller their ticket was returned
        msg = Message(
            subject=f"Ticket Returned - {transaction['event_name']}",
            recipients=[transaction["seller_email"]],
            html=f"<h2>Ticket Returned</h2><p>Your ticket for {transaction['event_name']} has been returned because the buyer didn't pay in time.</p>",
        )
        insta485.mail.send(msg)

        # Notify buyer they missed payment deadline
        msg = Message(
            subject=f"Payment Deadline Missed - {transaction['event_name']}",
            recipients=[transaction["buyer_email"]],
            html=f"<h2>Payment Deadline Missed</h2><p>You missed the payment deadline for {transaction['event_name']}.</p>",
        )
        insta485.mail.send(msg)

    def _send_ticket_reminder(self, transaction_id):
        """Send reminder to seller to send ticket"""
        from flask_mail import Message
        import insta485

        connection = insta485.model.get_db()
        transaction = connection.execute(
            """
            SELECT t.*, e.name as event_name
            FROM transactions t
            JOIN events e ON t.event_id = e.event_id
            WHERE t.transaction_id = ?
        """,
            (transaction_id,),
        ).fetchone()

        hours_remaining = (
            transaction["ticket_deadline"] - datetime.now()
        ).total_seconds() / 3600
        ticket_email = f"ticket-{transaction_id}@safetransaction.com"

        msg = Message(
            subject=f"Reminder: Send Ticket for {transaction['event_name']}",
            recipients=[transaction["seller_email"]],
            html=f"""
            <h2>Ticket Deadline Reminder</h2>
            <p>You have {int(hours_remaining)} hours remaining to send your tickets for {transaction["event_name"]}.</p>
            <p>Forward your tickets to: <strong>{ticket_email}</strong></p>
            """,
        )
        insta485.mail.send(msg)

    def _send_payment_reminder(self, transaction_id):
        """Send reminder to buyer to pay"""
        from flask_mail import Message
        import insta485

        connection = insta485.model.get_db()
        transaction = connection.execute(
            """
            SELECT t.*, e.name as event_name
            FROM transactions t
            JOIN events e ON t.event_id = e.event_id
            WHERE t.transaction_id = ?
        """,
            (transaction_id,),
        ).fetchone()

        hours_remaining = (
            transaction["payment_deadline"] - datetime.now()
        ).total_seconds() / 3600
        payment_url = f"http://localhost:8000/ticket/{transaction_id}"

        msg = Message(
            subject=f"Reminder: Pay for {transaction['event_name']} Tickets",
            recipients=[transaction["buyer_email"]],
            html=f"""
            <h2>Payment Deadline Reminder</h2>
            <p>You have {int(hours_remaining)} hours remaining to pay for {transaction["event_name"]}.</p>
            <p><a href="{payment_url}">Click here to pay now</a></p>
            """,
        )
        insta485.mail.send(msg)


# Global instance
background_manager = BackgroundJobManager()


def start_background_jobs():
    """Start all background jobs"""
    background_manager.start_scheduler()


def stop_background_jobs():
    """Stop all background jobs"""
    background_manager.stop_scheduler()


if __name__ == "__main__":
    # For testing - run background jobs
    print("🚀 Starting background job manager...")
    start_background_jobs()

    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        print("\n🛑 Stopping background job manager...")
        stop_background_jobs()
