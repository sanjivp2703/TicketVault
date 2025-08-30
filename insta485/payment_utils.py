"""Payment processing utilities for Safe Transaction."""
import insta485
import insta485.model


def send_payment_seller(transaction_id):
    """Send payment to seller via Stripe after a 1-minute delay."""
    print(f"Scheduler: Processing payment for transaction {transaction_id}")
    import stripe
    import flask
    # Always use a fresh DB connection to avoid sqlite locked errors
    with insta485.app.app_context():
        connection = insta485.model.get_db()
        # Get transaction details
        transaction = connection.execute(
            """
            SELECT t.seller_email, t.price, t.status, t.payment_processed_time,
                   e.event_datetime
            FROM transactions t
            JOIN events e ON t.event_id = e.event_id
            WHERE t.transaction_id = ?
            """,
            (transaction_id,)
        ).fetchone()
        
        if not transaction:
            print(f"[ERROR] Transaction {transaction_id} not found")
            return
        
        if transaction['status'] != 'waiting_for_payment':
            print(f"[ERROR] Transaction {transaction_id} not in correct status: {transaction['status']}")
            return
        
        try:
            # Update transaction status to indicate payment processing started
            connection.execute(
                "UPDATE transactions SET status = 'waiting_for_ticket', payment_processed_time = CURRENT_TIMESTAMP WHERE transaction_id = ?",
                (transaction_id,)
            )
            connection.commit()
            print(f"[PAYMENT] Updated transaction {transaction_id} to waiting_for_ticket")
            
            # Send email to seller notifying them to send the ticket
            from insta485.email_utils import send_seller_notification
            send_seller_notification(transaction_id, transaction['seller_email'])
            
        except Exception as e:
            print(f"[PAYMENT ERROR] Error processing payment for transaction {transaction_id}: {e}")
            connection.rollback() 