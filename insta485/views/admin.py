import flask
import insta485

@insta485.app.route('/admin', methods=['GET'], endpoint='admin_dashboard')
def admin_dashboard():
    """Admin dashboard: show all complaints using admin.html with admin context."""
    if 'email' not in flask.session:
        return flask.abort(403)
    connection = insta485.model.get_db()
    user = connection.execute(
        'SELECT is_admin FROM users WHERE email = ?',
        (flask.session['email'],)
    ).fetchone()
    if not user or not user['is_admin']:
        return flask.abort(403)
    # Fetch all complaints (transactions with status 'complaint_filed')
    complaints = connection.execute(
        "SELECT t.*, e.name AS ticket_description, e.location, e.event_datetime FROM transactions t JOIN events e ON t.event_id = e.event_id WHERE t.status = 'complaint_filed' ORDER BY t.transaction_id DESC"
    ).fetchall()
    context = {
        'is_admin': True,
        'logemail': flask.session['email'],
        'complaints': complaints,
        'user_type': 'admin',
        'transactions': [],  # not used for admin
    }
    return flask.render_template('admin.html', **context)

@insta485.app.route('/admin/refund_buyer/<int:transaction_id>', methods=['POST'], endpoint='admin_refund_buyer')
def admin_refund_buyer(transaction_id):
    """Admin action: refund buyer and set status to 'Complaint - Refunded Buyer'."""
    if 'email' not in flask.session:
        return flask.abort(403)
    connection = insta485.model.get_db()
    user = connection.execute(
        'SELECT is_admin FROM users WHERE email = ?',
        (flask.session['email'],)
    ).fetchone()
    if not user or not user['is_admin']:
        return flask.abort(403)
    connection.execute(
        "UPDATE transactions SET status = 'complaint - refunded buyer' WHERE transaction_id = ?",
        (transaction_id,)
    )
    print(f"[PAYMENT] Admin: Safe-Transaction refunded buyer for transaction {transaction_id}.")
    flask.flash('Buyer refunded and status updated.')
    return flask.redirect(flask.url_for('admin_dashboard'))

@insta485.app.route('/admin/pay_seller/<int:transaction_id>', methods=['POST'], endpoint='admin_pay_seller')
def admin_pay_seller(transaction_id):
    """Admin action: pay seller and set status to 'Complaint - Paid Seller'."""
    if 'email' not in flask.session:
        return flask.abort(403)
    connection = insta485.model.get_db()
    user = connection.execute(
        'SELECT is_admin FROM users WHERE email = ?',
        (flask.session['email'],)
    ).fetchone()
    if not user or not user['is_admin']:
        return flask.abort(403)
    connection.execute(
        "UPDATE transactions SET status = 'complaint - paid seller' WHERE transaction_id = ?",
        (transaction_id,)
    )
    print(f"[PAYMENT] Admin: Safe-Transaction paid seller for transaction {transaction_id}.")
    flask.flash('Seller paid and status updated.')
    return flask.redirect(flask.url_for('admin_dashboard'))
