"""Background tasks for the application."""

import stripe
import insta485


def send_payment_seller(transaction_id):
    """Send payment to seller via Stripe."""
    with insta485.app.app_context():
        connection = insta485.model.get_db()
        transaction = connection.execute(
            "SELECT seller_email, price FROM transactions WHERE transaction_id = ?",
            (transaction_id,),
        ).fetchone()

        if not transaction:
            return

        seller_email = transaction["seller_email"]
        price = transaction["price"]

        user = connection.execute(
            "SELECT stripe_id FROM users WHERE email = ?", (seller_email,)
        ).fetchone()

        if not user or not user["stripe_id"]:
            return

        stripe_id = user["stripe_id"]

        try:
            stripe.Transfer.create(
                amount=int(price * 100),  # Amount in cents
                currency="usd",
                destination=stripe_id,
                transfer_group=str(transaction_id),
            )
            connection.execute(
                "UPDATE transactions SET status = 'completed' WHERE transaction_id = ?",
                (transaction_id,),
            )
        except stripe.error.StripeError as e:
            print(f"Stripe Error: {e}")
