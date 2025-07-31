"""
Admin action routes for Safe-Transaction.
"""
import flask
import insta485
from insta485.views.balance import add_earnings, deduct_withdrawal

@insta485.app.route('/admin/refund-buyer/<int:transaction_id>', methods=['POST'])
def admin_refund_buyer(transaction_id):
    """Admin refunds buyer for a transaction."""
    if 'email' not in flask.session:
        return flask.abort(403)
    
    connection = insta485.model.get_db()
    user = connection.execute(
        'SELECT is_admin FROM users WHERE email = ?',
        (flask.session['email'],)
    ).fetchone()
    if not user or not user['is_admin']:
        return flask.abort(403)
    
    # Get transaction details
    transaction = connection.execute(
        'SELECT * FROM transactions WHERE transaction_id = ?',
        (transaction_id,)
    ).fetchone()
    
    if not transaction:
        flask.flash('Transaction not found', 'error')
        return flask.redirect(flask.url_for('admin_dashboard'))
    
    # Update transaction status
    connection.execute(
        "UPDATE transactions SET status = 'complaint - refunded buyer' WHERE transaction_id = ?",
        (transaction_id,)
    )
    
    # Process refund to buyer
    # Note: In a real system, this would integrate with a payment processor
    # Here we're just updating the status and recording the transaction
    
    # Record the refund in monetary_transactions
    try:
        connection.execute(
            "INSERT INTO monetary_transactions "
            "(sender, recipient, transaction_id_ref, amount, transaction_type) "
            "VALUES (?, ?, ?, ?, ?)",
            ('sanjivp2703@gmail.com', transaction['buyer_email'], transaction_id, transaction['price'], 'refund')
        )
        connection.commit()
        flask.flash(f'Buyer has been refunded for transaction #{transaction_id}', 'success')
    except Exception as e:
        connection.rollback()
        flask.flash(f'Error processing refund: {str(e)}', 'error')
    return flask.redirect(flask.url_for('admin_dashboard'))

@insta485.app.route('/admin/pay-seller/<int:transaction_id>', methods=['POST'])
def admin_pay_seller(transaction_id):
    """Admin pays seller for a transaction."""
    if 'email' not in flask.session:
        return flask.abort(403)
    
    connection = insta485.model.get_db()
    user = connection.execute(
        'SELECT is_admin FROM users WHERE email = ?',
        (flask.session['email'],)
    ).fetchone()
    if not user or not user['is_admin']:
        return flask.abort(403)
    
    # Get transaction details
    transaction = connection.execute(
        'SELECT * FROM transactions WHERE transaction_id = ?',
        (transaction_id,)
    ).fetchone()
    
    if not transaction:
        flask.flash('Transaction not found', 'error')
        return flask.redirect(flask.url_for('admin_dashboard'))
    
    # Update transaction status
    connection.execute(
        "UPDATE transactions SET status = 'complaint - paid seller' WHERE transaction_id = ?",
        (transaction_id,)
    )
    
    # Add earnings to seller's balance
    try:
        add_earnings(transaction['seller_email'], transaction['price'], transaction_id, f"Admin payment for transaction #{transaction_id}")
        flask.flash(f'Seller has been paid for transaction #{transaction_id}', 'success')
    except Exception as e:
        flask.flash(f'Error processing payment: {str(e)}', 'error')
    
    return flask.redirect(flask.url_for('admin_dashboard'))
