"""Safe-Transaction manage function for files."""
import hashlib
import pathlib
import uuid
import datetime
import os
import flask
import stripe
import insta485
import time

# This is a test key. In a real application, this should be stored securely.
stripe.api_key = "sk_test_51QrpdQC07BpFIQPX9s25iHN5nA78PYrurooQeTqtiEUhqBhzC8qcl3BHd6ZDFYCNLM6fGS1ynqwHY0uKtZ19zSDe00OalrifSw"

def send_payment_buyer(transaction_id):
    print(f"[PAYMENT] Buyer is paying Safe-Transaction for transaction {transaction_id}.")
    """Create a stripe checkout session for the buyer and store tid in session."""
    flask.session['transaction_id'] = transaction_id
    connection = insta485.model.get_db()
    transaction = connection.execute(
        "SELECT price FROM transactions WHERE transaction_id = ?",
        (transaction_id,)
    ).fetchone()

    if not transaction:
        flask.abort(404)

    amount = transaction['price'] * 100  # Convert to cents

    session = print(f"[PAYMENT] Stripe checkout session created for buyer payment on transaction {transaction_id}.")
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': f'Payment for Transaction #{transaction_id}',
                },
                'unit_amount': amount,
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=flask.url_for('payment_success', _external=True),
        cancel_url=flask.url_for('payment_cancel', _external=True),
    )
    return flask.redirect(session.url, code=303)

def hash_password(password):
    """Hash a password for storing."""
    algorithm = 'sha512'
    salt = uuid.uuid4().hex
    hash_obj = hashlib.new(algorithm)
    password_salted = salt + password
    hash_obj.update(password_salted.encode('utf-8'))
    password_hash = hash_obj.hexdigest()
    password_db_string = "$".join([algorithm, salt, password_hash])
    return password_db_string

def verify_pw(stored, provided):
    """Verify a stored password against one provided by user."""
    algorithm, salt, hash_obj = stored.split('$')
    hash_obj2 = hashlib.new(algorithm)
    password_salted = salt + provided
    hash_obj2.update(password_salted.encode('utf-8'))
    password_hash = hash_obj2.hexdigest()
    return password_hash == hash_obj

def manage_create(target, connection):
    """Create a user."""
    firstname = flask.request.form['firstname']
    lastname = flask.request.form['lastname']
    email = flask.request.form['email']
    password = flask.request.form['password']
    if not all([password, email, firstname, lastname]):
        flask.abort(400)

    # Check if user exists
    row = connection.execute(
        "SELECT * FROM users WHERE email == ?",
        (email,)
    ).fetchone()
    if row:
        flask.abort(409)

    # Insert new user
    connection.execute(
        "INSERT INTO users "
        "(firstname, lastname, email, password) "
        "VALUES (?, ?, ?, ?)",
        (firstname, lastname, email, hash_password(password))
    )
    flask.session['email'] = email
    return seller_onboarding()


def manage_login(connection, target):
    """Login a user."""
    email = flask.request.form['email']
    password = flask.request.form['password']
    if email == "" or password == "":
        return flask.abort(400)
    curr = connection.execute(
        "SELECT password FROM users WHERE email == ?",
        (email,)
    )
    row = curr.fetchone()
    valid = False
    if row:
        valid = verify_pw(row['password'], password)
    if valid:
        flask.session['email'] = email
        return flask.redirect(target)
    return flask.abort(403)

def manage_edit(connection, target):
    """Handle account editing. (Placeholder)"""
    # This feature is not yet implemented.
    return flask.abort(501) # Not Implemented


def seller_onboarding():
    """Handle seller onboarding with Stripe."""
    if 'email' not in flask.session:
        return flask.redirect(flask.url_for('manage_accounts'))

    email = flask.session['email']
    connection = insta485.model.get_db()
    user = connection.execute(
        "SELECT firstname, lastname "
        "FROM users "
        "WHERE email = ? ",
        (email, )
    ).fetchone()

    if not user:
        flask.abort(404)

    account = stripe.Account.create(
        type="express",
        country="US",
        email=email,
        business_type="individual",
        capabilities={"transfers": {"requested": True}},
        individual={
            "first_name": user['firstname'],
            "last_name": user['lastname'],
            "email": email
        },
        business_profile={
            "product_description": "Selling event tickets on Peer-to-peer platform for ticket resales."
        }
    )

    connection.execute(
        "UPDATE users "
        "SET stripe_id = ? "
        "WHERE email = ? ",
        (account.id, email, )
    )

    account_link = stripe.AccountLink.create(
        account=account.id,
        refresh_url=flask.url_for('reauth', _external=True),
        return_url=flask.url_for('onboarding_complete', _external=True),
        type="account_onboarding",
    )

    return flask.redirect(account_link.url)


@insta485.app.route('/reauth')
def reauth():
    """Handle Stripe re-authentication."""
    return seller_onboarding()


@insta485.app.route('/onboarding_complete')
def onboarding_complete():
    """Handle completion of Stripe onboarding."""
    return flask.redirect(flask.url_for('show_index', user_type='seller'))

def send_payment_seller(transaction_id):
    """Send payment to seller via Stripe after a 1-minute delay."""
    print(f"Scheduler: Processing payment for transaction {transaction_id}")
    import insta485.model
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
            print(f"Scheduler: Transaction {transaction_id} not found.")
            return
        seller_email = transaction['seller_email']
        price = transaction['price']
        status = transaction['status']
        payment_processed_time = transaction['payment_processed_time']
        event_datetime = transaction['event_datetime']
        # Get seller's Stripe ID
        seller = connection.execute(
            "SELECT stripe_id FROM users WHERE email = ?",
            (seller_email,)
        ).fetchone()
        if not seller or not seller['stripe_id']:
            print(f"Scheduler: Seller {seller_email} does not have a Stripe account.")
            return
        stripe_id = seller['stripe_id']
        # Send payment via Stripe
        try:
            print(f"Scheduler: Sending payment of ${price:.2f} to {seller_email} (Stripe ID: {stripe_id})")
            stripe.Transfer.create(
                amount=int(price * 100),  # Amount in cents
                currency="usd",
                destination=stripe_id,
                transfer_group=str(transaction_id),
            )
            try:
                # Use a fresh connection for the status update
                import insta485.model
                connection2 = insta485.model.get_db()
                connection2.execute(
                    "UPDATE transactions SET status = 'completed' WHERE transaction_id = ?",
                    (transaction_id,)
                )
                connection2.commit()
                print(f"Scheduler: Status updated to 'success' for transaction {transaction_id}.")
                print(f"[PAYMENT] Safe-Transaction paid seller for transaction {transaction_id}.")
            except Exception as db_err:
                print(f"[ERROR] Failed to update status to 'success' for transaction {transaction_id}: {db_err}")
            print(f"Scheduler: Successfully transferred ${price} for transaction {transaction_id}.")
        except stripe.error.StripeError as e:
            print(f"Scheduler: Stripe Error for transaction {transaction_id}: {e}")

@insta485.app.route('/accounts/', methods=["POST", "GET"])
def manage_accounts():
    """Manage accounts."""
    connection = insta485.model.get_db()
    target = flask.request.args.get('target')
    operation = flask.request.form['operation']
    if target is None or target == "":
        target = "/"
    if operation == "login":
        return manage_login(connection, target)
    if operation == "edit_account":
        return manage_edit(connection, target)
    if operation == "create":
        return manage_create(target, connection)
    if operation == "delete":
        pfp_file = connection.execute(
            "SELECT filename "
            "FROM users "
            "WHERE email == ? ",
            (flask.session['email'], )
        ).fetchone()
        os.remove(insta485.app.config['UPLOAD_FOLDER']/pfp_file['filename'])
        connection.execute(
            "DELETE FROM users "
            "WHERE email = ? ",
            (flask.session['email'], )
        )
        flask.session.clear()
    if operation == "update_password":
        old_pw = flask.request.form['password']
        new_pw1 = flask.request.form['new_password1']
        new_pw2 = flask.request.form['new_password2']
        status = -1
        if not old_pw or not new_pw1 or not new_pw2:
            status = 400
        elif new_pw1 != new_pw2:
            status = 401
        if status != -1:
            return flask.abort(status)
        row = connection.execute(
            "SELECT password FROM users WHERE email == ?",
            (flask.session['email'], )).fetchone()
        if not verify_pw(row['password'], old_pw):
            return flask.abort(403)
        connection.execute(
            "UPDATE users "
            "SET password = ? "
            "WHERE email == ? ",
            (hash_password(new_pw1), flask.session['email'])
        )
    return flask.redirect(target)
