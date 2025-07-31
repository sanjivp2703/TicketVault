"""Balance and withdrawal management for Safe Transaction."""
import flask
import insta485
from flask import flash, redirect, url_for

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
    return user['balance'] if user else 0

def get_balance_history(user_email, limit=50):
    """Get balance transaction history for a user."""
    connection = insta485.model.get_db()
    history = connection.execute(
        "SELECT * FROM balance_changes WHERE user_email = ? "
        "ORDER BY created DESC LIMIT ?",
        (user_email, limit)
    ).fetchall()
    return history

@insta485.app.route('/balance')
def show_balance():
    """Show seller's balance and earnings dashboard."""
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
    
    # Get balance history
    balance_history = connection.execute(
        "SELECT bc.*, t.transaction_id as ref_transaction_id "
        "FROM balance_changes bc "
        "LEFT JOIN transactions t ON bc.transaction_id_ref = t.transaction_id "
        "WHERE bc.user_email = ? "
        "ORDER BY bc.created DESC LIMIT 20",
        (logemail,)
    ).fetchall()
    
    # Get recent successful transactions (earnings)
    recent_earnings = connection.execute(
        "SELECT t.transaction_id, t.price, e.name as event_name, t.status, "
        "bc.created as earning_date "
        "FROM transactions t "
        "JOIN events e ON t.event_id = e.event_id "
        "LEFT JOIN balance_changes bc ON t.transaction_id = bc.transaction_id_ref AND bc.change_type = 'earning' "
        "WHERE t.seller_email = ? AND t.status IN ('success', 'complaint - paid seller') "
        "ORDER BY COALESCE(bc.created, t.payment_processed_time) DESC LIMIT 10",
        (logemail,)
    ).fetchall()
    
    # Get withdrawal history
    withdrawals = connection.execute(
        "SELECT change_id, user_email, amount, created, change_type "
        "FROM balance_changes "
        "WHERE user_email = ? AND change_type = 'withdrawal' "
        "ORDER BY created DESC LIMIT 10",
        (logemail,)
    ).fetchall()
    
    context = {
        'logemail': logemail,
        'balance': user['balance'],
        'balance_history': balance_history,
        'recent_earnings': recent_earnings,
        'withdrawals': withdrawals,
        'user_type': 'seller'  # Always seller for balance page
    }
    
    return flask.render_template('balance.html', **context)

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
    amount = flask.request.form.get('amount', type=int)
    bank_name = flask.request.form.get('bank_name', '').strip()
    routing_number = flask.request.form.get('routing_number', '').strip()
    account_number = flask.request.form.get('account_number', '').strip()
    
    # Validation
    if not amount or amount <= 0:
        flash("Please enter a valid withdrawal amount.", "error")
        return redirect(url_for('withdraw_funds'))
    
    if amount < 10:  # Minimum withdrawal amount
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
        # Update user balance
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
        
        flash(f"✅ Withdrawal request for ${amount} submitted successfully! We'll process it within 3-5 business days.", "success")
        return redirect(url_for('show_balance'))
        
    except Exception as e:
        print(f"[WITHDRAWAL ERROR] Failed to create withdrawal request: {e}")
        flash("Failed to submit withdrawal request. Please try again.", "error")
        return redirect(url_for('withdraw_funds'))


@insta485.app.route('/simulate-withdrawal', methods=['POST'])
def simulate_withdrawal():
    """Simulate a withdrawal for testing purposes."""
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
    
    # Default withdrawal amount (for testing)
    amount = min(user['balance'], 50)  # Take either full balance or $50, whichever is smaller
    
    if amount <= 0:
        flash("No funds available for withdrawal.", "error")
        return redirect(url_for('show_balance'))
    
    try:
        # Update user balance
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
        
        flash(f"✅ Simulated withdrawal of ${amount} completed successfully!", "success")
    except Exception as e:
        print(f"[WITHDRAWAL ERROR] Failed to simulate withdrawal: {e}")
        connection.rollback()
        flash("Failed to simulate withdrawal. Please try again.", "error")
    
    return redirect(url_for('show_balance')) 
