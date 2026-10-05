"""Balance and withdrawal management for TicketVault."""

import flask
import stripe
import insta485
from flask import flash, redirect, url_for
import logging

logger = logging.getLogger(__name__)


def add_earnings(
    user_email, amount, transaction_id, description="Transaction earnings"
):
    """Add earnings to seller's balance and record transaction."""
    connection = insta485.model.get_db()

    try:
        # Update user balance
        connection.execute(
            "UPDATE users SET balance = balance + ? WHERE email = ?",
            (amount, user_email),
        )

        # Record balance change
        connection.execute(
            "INSERT INTO balance_changes (user_email, amount, change_type, transaction_id_ref) "
            "VALUES (?, ?, 'earning', ?)",
            (user_email, amount, transaction_id),
        )

        connection.commit()
        logger.info(
            f"[BALANCE] Added ${amount} to {user_email} balance (Transaction #{transaction_id})"
        )

        # Send payment received notification email
        try:
            # Get transaction details for email
            trans_details = connection.execute(
                "SELECT buyer_email, price, name as event_name FROM transactions WHERE transaction_id = ?",
                (transaction_id,),
            ).fetchone()

            if trans_details:
                from insta485.email_automation import send_payment_received_notification

                # Calculate 10% bonus (amount should already include it, but let's compute for display)
                price = trans_details["price"] / 100  # Convert cents to dollars
                bonus_amount = price * 0.10

                send_payment_received_notification(
                    transaction_id=transaction_id,
                    seller_email=user_email,
                    buyer_email=trans_details["buyer_email"],
                    price=price,
                    event_name=trans_details["event_name"],
                    bonus_amount=bonus_amount,
                )
                logger.info(
                    f"[PAYMENT EMAIL] Sent payment received notification to {user_email}"
                )
        except Exception as email_error:
            logger.error(
                f"[PAYMENT EMAIL ERROR] Failed to send payment notification: {email_error}"
            )
            # Don't raise - email failure shouldn't stop the payment

        return True

    except Exception as e:
        logger.error(f"[BALANCE ERROR] Failed to add earnings: {e}")
        connection.rollback()
        return False


def deduct_withdrawal(user_email, amount, withdrawal_id, description="Withdrawal"):
    """Deduct withdrawal amount from seller's balance."""
    connection = insta485.model.get_db()

    try:
        # Check if user has sufficient balance
        user = connection.execute(
            "SELECT balance FROM users WHERE email = ?", (user_email,)
        ).fetchone()

        if not user or user["balance"] < amount:
            return False, "Insufficient balance"

        # Update user balance
        connection.execute(
            "UPDATE users SET balance = balance - ? WHERE email = ?",
            (amount, user_email),
        )

        # Record balance change
        connection.execute(
            "INSERT INTO balance_changes (user_email, amount, change_type) "
            "VALUES (?, ?, 'withdrawal')",
            (user_email, -amount),
        )

        # Record monetary transaction
        connection.execute(
            "INSERT INTO monetary_transactions (sender, recipient, amount, transaction_type) "
            "VALUES (?, ?, ?, 'withdrawal')",
            ("sanjivp2703@gmail.com", user_email, amount),
        )

        connection.commit()
        logger.info(
            f"[BALANCE] Deducted ${amount} from {user_email} balance (Withdrawal #{withdrawal_id})"
        )
        return True, "Success"

    except Exception as e:
        logger.error(f"[BALANCE ERROR] Failed to deduct withdrawal: {e}")
        connection.rollback()
        return False, f"Error: {e}"


def get_user_balance(user_email):
    """Get current balance for a user."""
    connection = insta485.model.get_db()
    user = connection.execute(
        "SELECT balance FROM users WHERE email = ?", (user_email,)
    ).fetchone()
    # Convert from cents to dollars
    return (user["balance"] / 100) if user else 0


def get_balance_history(user_email, limit=50):
    """Get balance transaction history for a user."""
    connection = insta485.model.get_db()
    history = connection.execute(
        "SELECT * FROM balance_changes WHERE user_email = ? "
        "ORDER BY created DESC LIMIT ?",
        (user_email, limit),
    ).fetchall()
    return history


@insta485.app.route("/secure-withdrawal", methods=["GET"])
def secure_withdrawal():
    """Show the secure withdrawal page with maze verification."""
    if "email" not in flask.session:
        return redirect(url_for("show_accounts", url="login"))

    logemail = flask.session["email"]
    connection = insta485.model.get_db()

    # Get user balance
    user = connection.execute(
        "SELECT balance FROM users WHERE email = ?", (logemail,)
    ).fetchone()

    if not user:
        flask.abort(404)

    return flask.render_template(
        "secure_withdrawal.html", user_balance=user["balance"], logemail=logemail
    )


@insta485.app.route("/withdraw", methods=["GET"])
def withdraw_funds():
    """Show modern withdrawal page with multiple payment options."""
    if "email" not in flask.session:
        return redirect(url_for("show_accounts", url="login"))

    logemail = flask.session["email"]
    connection = insta485.model.get_db()

    # Get user balance and Stripe connection status
    user = connection.execute(
        "SELECT balance, stripe_id FROM users WHERE email = ?", (logemail,)
    ).fetchone()

    if not user:
        flask.abort(404)

    # Check if user has Stripe Connect set up and get bank info
    has_stripe_connected = bool(user["stripe_id"])
    stripe_bank_info = None

    if has_stripe_connected:
        try:
            # Get Stripe account details
            account = stripe.Account.retrieve(user["stripe_id"])

            # Get external accounts (bank accounts)
            if account.external_accounts and account.external_accounts.data:
                bank_account = account.external_accounts.data[0]
                stripe_bank_info = {
                    "bank_name": bank_account.bank_name
                    if hasattr(bank_account, "bank_name")
                    else "Bank Account",
                    "last4": bank_account.last4
                    if hasattr(bank_account, "last4")
                    else "****",
                    "status": bank_account.status
                    if hasattr(bank_account, "status")
                    else "active",
                }
        except Exception as e:
            logger.error(f"[STRIPE INFO ERROR] Could not retrieve bank info: {e}")
            # Continue without bank info

    return flask.render_template(
        "withdraw_modern.html",
        balance=user["balance"],
        has_stripe_connected=has_stripe_connected,
        stripe_bank_info=stripe_bank_info,
        logemail=logemail,
    )


@insta485.app.route("/withdraw/process", methods=["POST"])
def process_withdrawal():
    """Process withdrawal request with modern payment methods."""
    if "email" not in flask.session:
        return redirect(url_for("show_accounts", url="login"))

    logemail = flask.session["email"]
    connection = insta485.model.get_db()

    # Get payment method and details
    payment_method = flask.request.form.get("payment_method", "").strip()
    amount_str = flask.request.form.get("amount", "").strip()

    # Get method-specific details
    venmo_handle = flask.request.form.get("venmo_handle", "").strip()
    cashapp_tag = flask.request.form.get("cashapp_tag", "").strip()

    # Validate payment method
    if payment_method not in ["venmo", "cashapp", "stripe"]:
        flash("Please select a valid payment method.", "error")
        return redirect(url_for("withdraw_funds"))

    # Validate payment details for non-Stripe methods
    if payment_method == "venmo" and not venmo_handle:
        flash("Please enter your Venmo username or PayPal email.", "error")
        return redirect(url_for("withdraw_funds"))

    if payment_method == "cashapp" and not cashapp_tag:
        flash("Please enter your Cash App $Cashtag.", "error")
        return redirect(url_for("withdraw_funds"))

    # For Stripe, check if account is connected
    if payment_method == "stripe":
        user_check = connection.execute(
            "SELECT stripe_id FROM users WHERE email = ?", (logemail,)
        ).fetchone()

        if not user_check or not user_check["stripe_id"]:
            flash("Please connect your Stripe account first.", "error")
            return redirect(url_for("withdraw_funds"))

    # Convert amount (already in cents from form)
    try:
        amount = int(amount_str)
    except (ValueError, TypeError):
        flash("Invalid withdrawal amount.", "error")
        return redirect(url_for("withdraw_funds"))

    # Validation
    if amount < 1000:  # Minimum $10
        flash("Minimum withdrawal amount is $10.", "error")
        return redirect(url_for("withdraw_funds"))

    # Calculate 5% TicketVault fee
    platform_fee = int(amount * 0.05)
    total_deduction = amount
    amount_to_transfer = amount - platform_fee

    # Check user balance
    user = connection.execute(
        "SELECT balance FROM users WHERE email = ?", (logemail,)
    ).fetchone()

    if not user or user["balance"] < total_deduction:
        flash("Insufficient balance for withdrawal.", "error")
        return redirect(url_for("withdraw_funds"))

    # Determine payment destination
    if payment_method == "stripe":
        payment_destination = "Connected Bank Account"
    else:
        payment_destination = venmo_handle if payment_method == "venmo" else cashapp_tag

    try:
        # Update database (deduct full amount)
        connection.execute(
            "UPDATE users SET balance = balance - ? WHERE email = ?",
            (total_deduction, logemail),
        )

        # Record withdrawal in balance_changes
        connection.execute(
            "INSERT INTO balance_changes (user_email, amount, change_type) "
            "VALUES (?, ?, 'withdrawal')",
            (logemail, -total_deduction),
        )

        # Record 5% fee (as part of withdrawal)
        connection.execute(
            "INSERT INTO balance_changes (user_email, amount, change_type) "
            "VALUES (?, ?, 'withdrawal')",
            (logemail, -platform_fee),
        )

        # Record monetary transaction
        connection.execute(
            "INSERT INTO monetary_transactions (sender, recipient, amount, transaction_type) "
            "VALUES (?, ?, ?, 'withdrawal')",
            ("sanjivp2703@gmail.com", logemail, amount_to_transfer),
        )

        # Store withdrawal request with modern payment info
        connection.execute(
            """INSERT INTO withdrawal_requests 
               (user_email, amount, fee_amount, transfer_amount, 
                bank_name, routing_number, account_number_last4, 
                status, created_at, notes)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), ?)""",
            (
                logemail,
                amount,
                platform_fee,
                amount_to_transfer,
                payment_method.upper(),
                "",
                payment_destination,
                "pending",
                f"{payment_method.upper()} withdrawal to {payment_destination}",
            ),
        )

        withdrawal_id = connection.execute("SELECT last_insert_rowid()").fetchone()[0]
        connection.commit()

        fee_dollars = platform_fee / 100
        transfer_dollars = amount_to_transfer / 100

        logger.info(
            f"[WITHDRAWAL] {payment_method.upper()} withdrawal: ${transfer_dollars:.2f} to {payment_destination} for {logemail}"
        )

        # Handle Stripe automatic transfer
        stripe_transfer_id = None
        if payment_method == "stripe":
            try:
                # Get Stripe account ID
                user_stripe = connection.execute(
                    "SELECT stripe_id FROM users WHERE email = ?", (logemail,)
                ).fetchone()

                if user_stripe and user_stripe["stripe_id"]:
                    # Automatic Stripe transfer
                    transfer = stripe.Transfer.create(
                        amount=amount_to_transfer,
                        currency="usd",
                        destination=user_stripe["stripe_id"],
                        transfer_group=f"withdrawal_{logemail}_{withdrawal_id}",
                        description=f"Withdrawal #{withdrawal_id} - ${transfer_dollars:.2f} (after 5% fee)",
                    )

                    stripe_transfer_id = transfer.id

                    # Update withdrawal status to completed
                    connection.execute(
                        "UPDATE withdrawal_requests SET status = 'completed', stripe_transfer_id = ?, completed_at = datetime('now') WHERE rowid = ?",
                        (transfer.id, withdrawal_id),
                    )
                    connection.commit()

                    logger.info(
                        f"[STRIPE SUCCESS] Transfer {transfer.id} created for {logemail}"
                    )

            except stripe.error.StripeError as stripe_error:
                logger.error(
                    f"[STRIPE ERROR] Automatic transfer failed: {stripe_error}"
                )
                # Don't rollback - withdrawal request is valid, just needs manual processing
                # Stripe error will be handled in the flash message below

        # Send withdrawal confirmation email
        try:
            from insta485.email_automation import send_withdrawal_confirmation

            send_withdrawal_confirmation(
                user_email=logemail,
                amount=amount / 100,
                fee_amount=platform_fee / 100,
                transfer_amount=amount_to_transfer / 100,
                transfer_id=stripe_transfer_id
                if stripe_transfer_id
                else f"{payment_method.upper()}-{withdrawal_id}",
                payment_method=payment_method,
                destination=payment_destination,
            )
            logger.info(
                f"[WITHDRAWAL EMAIL] Sent confirmation to {logemail} for {payment_method} to {payment_destination}"
            )
        except Exception as email_error:
            logger.error(f"[WITHDRAWAL EMAIL ERROR] {email_error}")

        # Success message
        if payment_method == "stripe" and stripe_transfer_id:
            flash(
                f"✅ Withdrawal successful! ${transfer_dollars:.2f} sent to your bank account. (5% fee: ${fee_dollars:.2f}) Arrives in 1-3 business days.",
                "success",
            )
        elif payment_method == "stripe":
            flash(
                f"✅ Withdrawal request received! ${transfer_dollars:.2f} will be sent to your bank account within one business day. (5% fee: ${fee_dollars:.2f})",
                "success",
            )
        else:
            method_name = "Venmo" if payment_method == "venmo" else "Cash App"
            flash(
                f"✅ Withdrawal request received! ${transfer_dollars:.2f} will be sent to your {method_name} ({payment_destination}) within one business day. (5% fee: ${fee_dollars:.2f})",
                "success",
            )

        return redirect(url_for("show_index"))

    except Exception as e:
        logger.error(f"[WITHDRAWAL ERROR] {e}")
        import traceback

        traceback.print_exc()
        connection.rollback()
        flash(
            f"Failed to process withdrawal: {str(e)}. Please try again or contact support.",
            "error",
        )
        return redirect(url_for("withdraw_funds"))


@insta485.app.route("/stripe/connect/onboard")
def stripe_connect_onboard():
    """Initiate Stripe Connect onboarding for direct bank transfers."""
    if "email" not in flask.session:
        return redirect(url_for("show_accounts", url="login"))

    logemail = flask.session["email"]
    connection = insta485.model.get_db()

    try:
        # Check if user already has a Stripe account
        user = connection.execute(
            "SELECT stripe_id FROM users WHERE email = ?", (logemail,)
        ).fetchone()

        if user and user["stripe_id"]:
            # Already has account, redirect to dashboard or create login link
            flash("✅ Your Stripe account is already connected!", "success")
            return redirect(url_for("show_index"))

        # Create a Stripe Connect Express account
        account = stripe.Account.create(
            type="express",
            country="US",
            email=logemail,
            capabilities={
                "card_payments": {"requested": True},
                "transfers": {"requested": True},
            },
        )

        # Store Stripe account ID
        connection.execute(
            "UPDATE users SET stripe_id = ? WHERE email = ?", (account.id, logemail)
        )
        connection.commit()

        # Create account link for onboarding
        account_link = stripe.AccountLink.create(
            account=account.id,
            refresh_url=flask.url_for("stripe_connect_onboard", _external=True),
            return_url=flask.url_for("stripe_connect_return", _external=True),
            type="account_onboarding",
        )

        logger.info(f"[STRIPE CONNECT] Created account {account.id} for {logemail}")

        # Redirect to Stripe onboarding
        return redirect(account_link.url)

    except Exception as e:
        logger.error(f"[STRIPE CONNECT ERROR] {e}")
        import traceback

        traceback.print_exc()
        flash("Failed to start Stripe Connect onboarding. Please try again.", "error")
        return redirect(url_for("withdraw_funds"))


@insta485.app.route("/stripe/connect/return")
def stripe_connect_return():
    """Handle return from Stripe Connect onboarding."""
    if "email" not in flask.session:
        return redirect(url_for("show_accounts", url="login"))

    flash(
        "✅ Stripe Connect setup complete! You can now withdraw funds directly to your bank.",
        "success",
    )
    return redirect(url_for("show_index"))


@insta485.app.route("/stripe/connect/update")
def stripe_connect_update():
    """Allow user to update their Stripe Connect bank account."""
    if "email" not in flask.session:
        return redirect(url_for("show_accounts", url="login"))

    logemail = flask.session["email"]
    connection = insta485.model.get_db()

    try:
        # Get user's Stripe account ID
        user = connection.execute(
            "SELECT stripe_id FROM users WHERE email = ?", (logemail,)
        ).fetchone()

        if not user or not user["stripe_id"]:
            flash(
                "❌ No Stripe account found. Please click 'Connect Bank Account' to set up Stripe Connect first.",
                "error",
            )
            return redirect(url_for("withdraw_funds"))

        # Check if account is fully onboarded
        try:
            account = stripe.Account.retrieve(user["stripe_id"])
            charges_enabled = account.get("charges_enabled", False)
            details_submitted = account.get("details_submitted", False)

            # If account isn't fully set up, use onboarding instead
            if not charges_enabled or not details_submitted:
                logger.info(
                    "[STRIPE UPDATE] Account not fully onboarded, using onboarding flow instead"
                )
                account_link = stripe.AccountLink.create(
                    account=user["stripe_id"],
                    refresh_url=flask.url_for("stripe_connect_update", _external=True),
                    return_url=flask.url_for("stripe_connect_return", _external=True),
                    type="account_onboarding",
                )
            else:
                # Account is fully set up, use update flow
                account_link = stripe.AccountLink.create(
                    account=user["stripe_id"],
                    refresh_url=flask.url_for("stripe_connect_update", _external=True),
                    return_url=flask.url_for("stripe_connect_return", _external=True),
                    type="account_update",
                )
        except stripe.error.StripeError as stripe_err:
            logger.error(f"[STRIPE UPDATE ERROR] Stripe API error: {stripe_err}")
            # If there's an error retrieving account, try onboarding
            account_link = stripe.AccountLink.create(
                account=user["stripe_id"],
                refresh_url=flask.url_for("stripe_connect_update", _external=True),
                return_url=flask.url_for("stripe_connect_return", _external=True),
                type="account_onboarding",
            )

        logger.info(f"[STRIPE UPDATE] Created account link for {logemail}")

        # Redirect to Stripe page
        return redirect(account_link.url)

    except Exception as e:
        logger.error(f"[STRIPE UPDATE ERROR] {e}")
        import traceback

        traceback.print_exc()
        flash(
            f"Failed to create Stripe link: {str(e)}. Please try again or contact support.",
            "error",
        )
        return redirect(url_for("withdraw_funds"))


@insta485.app.route("/admin/withdrawal/complete/<int:withdrawal_id>", methods=["POST"])
def mark_withdrawal_complete(withdrawal_id):
    """Mark a withdrawal as complete and send completion email."""
    if "email" not in flask.session:
        return flask.jsonify({"error": "Unauthorized"}), 401

    logemail = flask.session["email"]
    connection = insta485.model.get_db()

    try:
        # Verify admin
        admin = connection.execute(
            "SELECT is_admin FROM users WHERE email = ?", (logemail,)
        ).fetchone()

        if not admin or not admin["is_admin"]:
            return flask.jsonify({"error": "Unauthorized - Admin only"}), 403

        # Get withdrawal details
        withdrawal = connection.execute(
            """
            SELECT 
                wr.id,
                wr.user_email,
                wr.amount,
                wr.fee_amount,
                wr.transfer_amount,
                wr.bank_name,
                wr.account_number_last4,
                wr.status
            FROM withdrawal_requests wr
            WHERE wr.id = ?
        """,
            (withdrawal_id,),
        ).fetchone()

        if not withdrawal:
            return flask.jsonify({"error": "Withdrawal not found"}), 404

        if withdrawal["status"] != "pending":
            return flask.jsonify({"error": "Withdrawal already processed"}), 400

        # Update withdrawal status
        connection.execute(
            "UPDATE withdrawal_requests SET status = 'completed' WHERE id = ?",
            (withdrawal_id,),
        )
        connection.commit()

        # Send completion email
        try:
            from insta485.email_automation import send_withdrawal_completed_email

            # Map bank_name to payment_method
            payment_method = (
                withdrawal["bank_name"].lower()
                if withdrawal["bank_name"]
                else "unknown"
            )
            if payment_method not in ["venmo", "cashapp", "stripe"]:
                payment_method = (
                    "venmo" if "venmo" in payment_method.lower() else "stripe"
                )

            send_withdrawal_completed_email(
                user_email=withdrawal["user_email"],
                amount=withdrawal["amount"] / 100,
                fee_amount=withdrawal["fee_amount"] / 100,
                transfer_amount=withdrawal["transfer_amount"] / 100,
                payment_method=payment_method,
                destination=withdrawal["account_number_last4"],
            )
            logger.info(
                f"[WITHDRAWAL COMPLETE] Sent email to {withdrawal['user_email']} for ${withdrawal['transfer_amount'] / 100:.2f}"
            )
        except Exception as email_error:
            logger.error(f"[WITHDRAWAL COMPLETE EMAIL ERROR] {email_error}")
            # Don't fail the request if email fails

        return flask.jsonify(
            {
                "success": True,
                "message": f"Withdrawal marked as complete! Email sent to {withdrawal['user_email']}",
            }
        ), 200

    except Exception as e:
        logger.error(f"[MARK WITHDRAWAL COMPLETE ERROR] {e}")
        import traceback

        traceback.print_exc()
        connection.rollback()
        return flask.jsonify({"error": str(e)}), 500
