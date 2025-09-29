"""Balance and withdrawal management for Safe Transaction."""
import flask
import stripe
import insta485
from flask import flash, redirect, url_for

# Set Stripe API key (same as in manage.py)
stripe.api_key = "sk_test_51QrpdQC07BpFIQPX9s25iHN5nA78PYrurooQeTqtiEUhqBhzC8qcl3BHd6ZDFYCNLM6fGS1ynqwHY0uKtZ19zSDe00OalrifSw"

def add_earnings(user_email, amount, transaction_id, description="Transaction earnings"):
    """Add earnings to seller's balance and record transaction."""
    connection = insta485.model.get_db()
    
    try:
        # Update user balance
        connection.execute(
            "UPDATE users SET balance = balance + ? WHERE email = ?",
            (amount, user_email)
        )
        
        # Record balance change
        connection.execute(
            "INSERT INTO balance_changes (user_email, amount, change_type, transaction_id_ref) "
            "VALUES (?, ?, 'earning', ?)",
            (user_email, amount, transaction_id)
        )
        
        connection.commit()
        print(f"[BALANCE] Added ${amount} to {user_email} balance (Transaction #{transaction_id})")
        return True
        
    except Exception as e:
        print(f"[BALANCE ERROR] Failed to add earnings: {e}")
        connection.rollback()
        return False

def deduct_withdrawal(user_email, amount, withdrawal_id, description="Withdrawal"):
    """Deduct withdrawal amount from seller's balance."""
    connection = insta485.model.get_db()
    
    try:
        # Check if user has sufficient balance
        user = connection.execute(
            "SELECT balance FROM users WHERE email = ?",
            (user_email,)
        ).fetchone()
        
        if not user or user['balance'] < amount:
            return False, "Insufficient balance"
        
        # Update user balance
        connection.execute(
            "UPDATE users SET balance = balance - ? WHERE email = ?",
            (amount, user_email)
        )
        
        # Record balance change
        connection.execute(
            "INSERT INTO balance_changes (user_email, amount, change_type) "
            "VALUES (?, ?, 'withdrawal')",
            (user_email, -amount)
        )
        
        # Record monetary transaction
        connection.execute(
            "INSERT INTO monetary_transactions (sender, recipient, amount, transaction_type) "
            "VALUES (?, ?, ?, 'withdrawal')",
            ('sanjivp2703@gmail.com', user_email, amount)
        )
        
        connection.commit()
        print(f"[BALANCE] Deducted ${amount} from {user_email} balance (Withdrawal #{withdrawal_id})")
        return True, "Success"
        
    except Exception as e:
        print(f"[BALANCE ERROR] Failed to deduct withdrawal: {e}")
        connection.rollback()
        return False, f"Error: {e}"

def get_user_balance(user_email):
    """Get current balance for a user."""
    connection = insta485.model.get_db()
    user = connection.execute(
        "SELECT balance FROM users WHERE email = ?",
        (user_email,)
    ).fetchone()
    # Convert from cents to dollars
    return (user['balance'] / 100) if user else 0

def get_balance_history(user_email, limit=50):
    """Get balance transaction history for a user."""
    connection = insta485.model.get_db()
    history = connection.execute(
        "SELECT * FROM balance_changes WHERE user_email = ? "
        "ORDER BY created DESC LIMIT ?",
        (user_email, limit)
    ).fetchall()
    return history


@insta485.app.route('/secure-withdrawal', methods=['GET'])
def secure_withdrawal():
    """Show the secure withdrawal page with maze verification."""
    if 'email' not in flask.session:
        return redirect(url_for('show_accounts', url='login'))
    
    logemail = flask.session['email']
    connection = insta485.model.get_db()
    
    # Get user balance
    user = connection.execute(
        "SELECT balance FROM users WHERE email = ?",
        (logemail,)
    ).fetchone()
    
    if not user:
        flask.abort(404)
    
    return flask.render_template('secure_withdrawal.html', 
                                user_balance=user['balance'],
                                logemail=logemail)

@insta485.app.route('/withdraw', methods=['GET', 'POST'])
def withdraw_funds():
    """Handle withdrawal requests."""
    if 'email' not in flask.session:
        return redirect(url_for('show_accounts', url='login'))
    
    logemail = flask.session['email']
    connection = insta485.model.get_db()
    
    if flask.request.method == 'GET':
        # Show withdrawal form
        user = connection.execute(
            "SELECT balance FROM users WHERE email = ?",
            (logemail,)
        ).fetchone()
        
        if not user:
            flask.abort(404)
        
        return flask.render_template('withdraw.html', 
                                   balance=user['balance'],
                                   logemail=logemail)
    
    # POST - Process withdrawal request
    amount_str = flask.request.form.get('amount', '').strip()
    bank_name = flask.request.form.get('bank_name', '').strip()
    routing_number = flask.request.form.get('routing_number', '').strip()
    account_number = flask.request.form.get('account_number', '').strip()
    
    # Convert amount (comes as decimal string from form)
    try:
        amount = int(float(amount_str) * 100)  # Convert dollars to cents
    except (ValueError, TypeError):
        flash("Invalid withdrawal amount.", "error")
        return redirect(url_for('withdraw_funds'))
    
    # Validation
    if amount <= 0:
        flash("Withdrawal amount must be greater than $0.", "error")
        return redirect(url_for('withdraw_funds'))
    
    if amount < 1000:  # Minimum withdrawal amount (10 dollars = 1000 cents)
        flash("Minimum withdrawal amount is $10.", "error")
        return redirect(url_for('withdraw_funds'))
    
    if not all([bank_name, routing_number, account_number]):
        flash("Please fill in all bank account details.", "error")
        return redirect(url_for('withdraw_funds'))
    
    # Check user balance
    user = connection.execute(
        "SELECT balance FROM users WHERE email = ?",
        (logemail,)
    ).fetchone()
    
    if not user or user['balance'] < amount:
        flash("Insufficient balance for withdrawal.", "error")
        return redirect(url_for('withdraw_funds'))
    
    try:
        # Get user's Stripe account ID for payout
        user_stripe = connection.execute(
            "SELECT stripe_id FROM users WHERE email = ?",
            (logemail,)
        ).fetchone()
        
        if not user_stripe or not user_stripe['stripe_id']:
            flash("❌ Stripe account not set up. Please complete seller onboarding first.", "error")
            return redirect(url_for('withdraw_funds'))
        
        stripe_account_id = user_stripe['stripe_id']
        
        # First, update database
        connection.execute(
            "UPDATE users SET balance = balance - ? WHERE email = ?",
            (amount, logemail)
        )
        
        # Record withdrawal in balance_changes
        connection.execute(
            "INSERT INTO balance_changes (user_email, amount, change_type) "
            "VALUES (?, ?, 'withdrawal')",
            (logemail, -amount)
        )
        
        # Record monetary transaction
        connection.execute(
            "INSERT INTO monetary_transactions (sender, recipient, amount, transaction_type) "
            "VALUES (?, ?, ?, 'withdrawal')",
            ('sanjivp2703@gmail.com', logemail, amount)
        )
        
        connection.commit()
        print(f"[WITHDRAWAL] Database updated for ${amount/100:.2f} withdrawal for {logemail}")
        
        # Now send real money via Stripe Transfer (same pattern as seller payments)
        try:
            amount_dollars = amount / 100  # Convert cents back to dollars for display
            print(f"[STRIPE] Initiating transfer of ${amount_dollars} to Stripe account {stripe_account_id}")
            
            transfer = stripe.Transfer.create(
                amount=amount,  # Already in cents
                currency="usd",
                destination=stripe_account_id,
                transfer_group=f"withdrawal_{logemail}_{amount_dollars}",
                description=f"Withdrawal for {logemail} - ${amount_dollars}"
            )
            
            print(f"[STRIPE SUCCESS] Transfer created: {transfer.id}")
            flash(f"✅ Withdrawal of ${amount_dollars:.2f} sent successfully! Transfer ID: {transfer.id[:20]}...", "success")
            
        except stripe.error.StripeError as stripe_error:
            # Rollback database changes if Stripe fails
            print(f"[STRIPE ERROR] Failed to create transfer: {stripe_error}")
            connection.execute(
                "UPDATE users SET balance = balance + ? WHERE email = ?",
                (amount, logemail)
            )
            connection.execute(
                "DELETE FROM balance_changes WHERE user_email = ? AND amount = ? AND change_type = 'withdrawal' ORDER BY created_time DESC LIMIT 1",
                (logemail, -amount)
            )
            connection.execute(
                "DELETE FROM monetary_transactions WHERE sender = ? AND recipient = ? AND amount = ? AND transaction_type = 'withdrawal' ORDER BY id DESC LIMIT 1",
                ('sanjivp2703@gmail.com', logemail, amount)
            )
            connection.commit()
            
            flash(f"❌ Stripe transfer failed: {str(stripe_error)}. Your balance of ${amount_dollars:.2f} has been restored.", "error")
            return redirect(url_for('withdraw_funds'))
        
        return redirect(url_for('show_index'))
        
    except Exception as e:
        print(f"[WITHDRAWAL ERROR] Failed to process withdrawal request: {e}")
        connection.rollback()
        flash("Failed to process withdrawal request. Please try again.", "error")
        return redirect(url_for('withdraw_funds'))


# REMOVED: simulate_withdrawal route - test functionality no longer needed 
