"""TicketVault manage function for files."""

import hashlib
import uuid
import datetime
import flask
import stripe
import insta485
import random
import string
from insta485.logger_config import get_logger

# Initialize loggers
logger = get_logger(__name__)
payment_logger = get_logger("payment")
email_logger = get_logger("email")


def send_payment_buyer(transaction_id):
    """Create a stripe checkout session for the buyer and store tid in session."""
    payment_logger.info(f"Buyer initiating payment for transaction {transaction_id}")

    flask.session["transaction_id"] = transaction_id
    connection = insta485.model.get_db()
    transaction = connection.execute(
        "SELECT price FROM transactions WHERE transaction_id = ?", (transaction_id,)
    ).fetchone()

    if not transaction:
        payment_logger.error(f"Transaction {transaction_id} not found for payment")
        flask.abort(404)

    amount = int(transaction["price"] * 100)  # Convert to cents as integer
    payment_logger.info(
        f"Creating Stripe checkout session for transaction {transaction_id}, amount: ${transaction['price']}"
    )

    # Set expiration time to 1 hour from now (Unix timestamp)
    expires_at = int(
        (datetime.datetime.now() + datetime.timedelta(hours=1)).timestamp()
    )

    try:
        session = stripe.checkout.Session.create(
            # Enable all available payment methods including Apple Pay, Google Pay, cards
            payment_method_types=["card"],
            # Automatic payment methods will enable Apple Pay, Google Pay on compatible devices
            payment_method_options={"card": {"request_three_d_secure": "automatic"}},
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
            # Expire the payment link after 1 hour
            expires_at=expires_at,
        )
        payment_logger.info(
            f"Stripe checkout session created successfully for transaction {transaction_id}, session_id: {session.id}"
        )
        return flask.redirect(session.url, code=303)
    except stripe.error.StripeError as e:
        payment_logger.error(
            f"Stripe error creating checkout session for transaction {transaction_id}: {str(e)}"
        )
        flask.abort(500)
    except Exception as e:
        payment_logger.error(
            f"Unexpected error creating checkout session for transaction {transaction_id}: {str(e)}"
        )
        flask.abort(500)


def hash_password(password):
    """Hash a password for storing."""
    algorithm = "sha512"
    salt = uuid.uuid4().hex
    hash_obj = hashlib.new(algorithm)
    password_salted = salt + password
    hash_obj.update(password_salted.encode("utf-8"))
    password_hash = hash_obj.hexdigest()
    password_db_string = "$".join([algorithm, salt, password_hash])
    return password_db_string


def verify_pw(stored, provided):
    """Verify a stored password against one provided by user."""
    algorithm, salt, hash_obj = stored.split("$")
    hash_obj2 = hashlib.new(algorithm)
    password_salted = salt + provided
    hash_obj2.update(password_salted.encode("utf-8"))
    password_hash = hash_obj2.hexdigest()
    return password_hash == hash_obj


def generate_verification_code(length=6):
    """Generate a random verification code."""
    return "".join(random.choices(string.digits, k=length))


def send_verification_email(email, code):
    """Send verification email (placeholder implementation)."""
    # In a real application, you would use a service like SendGrid, AWS SES, etc.
    email_logger.info(f"Sending verification code to {email}")
    logger.debug(f"Verification code for {email}: {code}")
    # For development, we'll just log to console
    return True


def send_verification_sms(phone_number, code):
    """Send verification SMS using Textbelt API (free for testing)."""
    # Use Textbelt for SMS sending - it's free for testing
    try:
        # Format phone number - ensure it starts with +1 for US numbers
        if not phone_number.startswith("+"):
            if not phone_number.startswith("1"):
                phone_number = "1" + phone_number
            phone_number = "+" + phone_number

        # For development, we'll log to console instead of sending real SMS
        email_logger.info(f"Sending SMS verification code to {phone_number}")
        logger.debug(f"SMS verification code for {phone_number}: {code}")

        # Uncomment the following lines to send real SMS in production:
        # payload = {
        #     'phone': phone_number,
        #     'message': f'Your TicketVault verification code is: {code}',
        #     'key': 'textbelt'  # Use 'textbelt' for free quota
        # }
        # response = requests.post('https://textbelt.com/text', data=payload)
        # return response.json().get('success', False)

        return True  # Return True for development
    except Exception as e:
        email_logger.error(f"Failed to send SMS to {phone_number}: {str(e)}")
        return False


def create_verification_code(email, code_type, connection):
    """Create and store a verification code."""
    code = generate_verification_code()
    expires_at = datetime.datetime.now() + datetime.timedelta(
        minutes=10
    )  # 10 minute expiry

    connection.execute(
        "INSERT INTO verification_codes (email, code, code_type, expires_at) VALUES (?, ?, ?, ?)",
        (email, code, code_type, expires_at),
    )

    if code_type == "email_verification":
        send_verification_email(email, code)
    elif code_type == "phone_verification":
        # Get user's phone number for SMS
        try:
            user = connection.execute(
                "SELECT phone_number FROM users WHERE email = ?", (email,)
            ).fetchone()
            if user and user["phone_number"]:
                send_verification_sms(user["phone_number"], code)
        except Exception:
            logger.error(
                f"[SMS] Could not send SMS - phone number not available for {email}"
            )

    return code


def verify_code(email, provided_code, code_type, connection):
    """Verify a provided code against stored codes."""
    current_time = datetime.datetime.now()

    # Get the most recent unused code of the specified type
    code_record = connection.execute(
        """SELECT id, code FROM verification_codes 
           WHERE email = ? AND code_type = ? AND used = 0 AND expires_at > ?
           ORDER BY created_at DESC LIMIT 1""",
        (email, code_type, current_time),
    ).fetchone()

    if not code_record:
        return False

    if code_record["code"] == provided_code:
        # Mark code as used
        connection.execute(
            "UPDATE verification_codes SET used = 1 WHERE id = ?", (code_record["id"],)
        )

        # Update user verification status
        if code_type == "email_verification":
            connection.execute(
                "UPDATE users SET email_verified = 1 WHERE email = ?", (email,)
            )
        elif code_type == "phone_verification":
            connection.execute(
                "UPDATE users SET phone_verified = 1 WHERE email = ?", (email,)
            )

        return True

    return False


def manage_create(target, connection):
    """Create a user."""
    # Get form data
    firstname = flask.request.form.get("firstname", "").strip()
    email = flask.request.form.get("email", "").strip().lower()
    password = flask.request.form.get("password", "")

    logger.info(f"Signup attempt: {firstname} <{email}>")

    # Simple validation
    if not firstname or not email or not password:
        logger.warning("Signup failed: Missing required fields")
        return flask.render_template("create.html", error="All fields are required.")

    # Check if user exists
    try:
        existing_user = connection.execute(
            "SELECT email FROM users WHERE email = ?", (email,)
        ).fetchone()

        if existing_user:
            logger.warning(f"Signup failed: User already exists: {email}")
            return flask.render_template(
                "create.html", error="User with that email already exists."
            )
    except Exception as e:
        logger.error(f"Database check failed during signup: {str(e)}")
        return flask.render_template(
            "create.html", error="Database error. Please try again."
        )

    # Split name into first/last
    if " " in firstname:
        name_parts = firstname.split(" ", 1)
        actual_firstname = name_parts[0]
        actual_lastname = name_parts[1]
    else:
        actual_firstname = firstname
        actual_lastname = ""

    # Create user
    try:
        connection.execute(
            "INSERT INTO users (firstname, lastname, email, password) VALUES (?, ?, ?, ?)",
            (actual_firstname, actual_lastname, email, hash_password(password)),
        )
        connection.commit()
        logger.info(f"[SUCCESS] User created: {email}")

        # Set session
        flask.session["email"] = email
        logger.info(f"[SUCCESS] Session set for: {email}")

        # Redirect to main page
        redirect_url = flask.url_for("show_index")
        logger.info(f"[DEBUG] Redirecting to: {redirect_url}")
        return flask.redirect(redirect_url)

    except Exception as e:
        logger.error(f"[ERROR] Failed to create user: {e}")
        return flask.render_template(
            "create.html", error="Failed to create account. Please try again."
        )


def manage_login(connection, target):
    """Login a user."""
    email = flask.request.form.get("email", "").strip().lower()
    password = flask.request.form.get("password", "")

    logger.info(f"[DEBUG] Login attempt for: {email}")

    if not email or not password:
        logger.error("[ERROR] Missing email or password")
        return flask.render_template(
            "login.html", error="Email and password are required."
        )

    try:
        # Get user from database
        row = connection.execute(
            "SELECT password FROM users WHERE email = ?", (email,)
        ).fetchone()

        if not row:
            logger.error(f"[ERROR] User not found: {email}")
            return flask.render_template(
                "login.html", error="Invalid email or password."
            )

        # Verify password
        if verify_pw(row["password"], password):
            flask.session["email"] = email
            logger.info(f"[SUCCESS] Login successful for: {email}")
            return flask.redirect(target if target else flask.url_for("show_index"))
        else:
            logger.error(f"[ERROR] Invalid password for: {email}")
            return flask.render_template(
                "login.html", error="Invalid email or password."
            )

    except Exception as e:
        logger.error(f"[ERROR] Login failed: {e}")
        return flask.render_template(
            "login.html", error="Login failed. Please try again."
        )


def manage_edit(connection, target):
    """Handle account editing. (Placeholder)"""
    # This feature is not yet implemented.
    return flask.abort(501)  # Not Implemented


def seller_onboarding():
    """Handle seller onboarding with Stripe."""
    try:
        if "email" not in flask.session:
            logger.info("[DEBUG] No email in session, redirecting to login")
            return flask.redirect(flask.url_for("show_accounts", url="login"))

        email = flask.session["email"]
        logger.info(f"[DEBUG] Starting seller onboarding for: {email}")

        connection = insta485.model.get_db()
        user = connection.execute(
            "SELECT firstname, lastname FROM users WHERE email = ?", (email,)
        ).fetchone()

        if not user:
            logger.error(f"[ERROR] User not found in database: {email}")
            flask.abort(404)

        logger.info(f"[DEBUG] Found user: {user['firstname']} {user['lastname']}")

    except Exception as e:
        logger.error(f"[ERROR] Error in seller_onboarding: {e}")
        return flask.redirect(flask.url_for("show_index"))

    account = stripe.Account.create(
        type="express",
        country="US",
        email=email,
        business_type="individual",
        capabilities={"transfers": {"requested": True}},
        individual={
            "first_name": user["firstname"],
            "last_name": user["lastname"],
            "email": email,
        },
        business_profile={
            "product_description": "Selling event tickets on Peer-to-peer platform for ticket resales."
        },
    )

    connection.execute(
        "UPDATE users SET stripe_id = ? WHERE email = ? ",
        (
            account.id,
            email,
        ),
    )

    account_link = stripe.AccountLink.create(
        account=account.id,
        refresh_url=flask.url_for("reauth", _external=True),
        return_url=flask.url_for("onboarding_complete", _external=True),
        type="account_onboarding",
    )

    return flask.redirect(account_link.url)


@insta485.app.route("/reauth")
def reauth():
    """Handle Stripe re-authentication."""
    return seller_onboarding()


@insta485.app.route("/onboarding_complete")
def onboarding_complete():
    """Handle completion of Stripe onboarding."""
    return flask.redirect(flask.url_for("show_index", user_type="seller"))


def send_payment_seller(transaction_id):
    """Send payment to seller via Stripe after a 1-minute delay."""
    logger.info(f"Scheduler: Processing payment for transaction {transaction_id}")
    import insta485.model
    import stripe

    # Always use a fresh DB connection to avoid sqlite locked errors
    with insta485.app.app_context():
        connection = insta485.model.get_db()
        # Get transaction details
        transaction = connection.execute(
            """
            SELECT t.seller_email, t.price, t.status, t.payment_received_time,
                   e.event_datetime
            FROM transactions t
            JOIN events e ON t.event_id = e.event_id
            WHERE t.transaction_id = ?
            """,
            (transaction_id,),
        ).fetchone()
        if not transaction:
            logger.info(f"Scheduler: Transaction {transaction_id} not found.")
            return
        seller_email = transaction["seller_email"]
        price = transaction["price"]
        # Get seller's Stripe ID
        seller = connection.execute(
            "SELECT stripe_id FROM users WHERE email = ?", (seller_email,)
        ).fetchone()
        if not seller or not seller["stripe_id"]:
            logger.info(
                f"Scheduler: Seller {seller_email} does not have a Stripe account."
            )
            return
        stripe_id = seller["stripe_id"]
        # Send payment via Stripe
        try:
            logger.info(
                f"Scheduler: Sending payment of ${price:.2f} to {seller_email} (Stripe ID: {stripe_id})"
            )
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
                    (transaction_id,),
                )
                connection2.commit()
                logger.info(
                    f"Scheduler: Status updated to 'success' for transaction {transaction_id}."
                )
                logger.info(
                    f"[PAYMENT] TicketVault paid seller for transaction {transaction_id}."
                )
            except Exception as db_err:
                logger.error(
                    f"[ERROR] Failed to update status to 'success' for transaction {transaction_id}: {db_err}"
                )
            logger.info(
                f"Scheduler: Successfully transferred ${price} for transaction {transaction_id}."
            )
        except stripe.error.StripeError as e:
            logger.error(
                f"Scheduler: Stripe Error for transaction {transaction_id}: {e}"
            )


# Removed the complex manage_accounts route - using simplified individual routes instead
