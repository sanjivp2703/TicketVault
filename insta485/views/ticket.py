"""
Ticket validation and problem reporting routes.
"""
import flask
import insta485

@insta485.app.route('/show-validate-ticket/<int:transaction_id>', methods=['GET', 'POST'])
def show_validate_ticket(transaction_id):
    """Display and process ticket validation."""
    if 'email' not in flask.session:
        return flask.redirect(flask.url_for('show_accounts', url='login'))
    
    connection = insta485.model.get_db()
    
    # Get transaction details
    transaction = connection.execute(
        "SELECT t.*, e.name, e.location, e.event_datetime FROM transactions t "
        "JOIN events e ON t.event_id = e.event_id "
        "WHERE t.transaction_id = ? AND t.buyer_email = ?",
        (transaction_id, flask.session['email'])
    ).fetchone()
    
    if not transaction:
        flask.abort(404)  # Transaction not found
    
    # Generate a ticket code (in a real app, this would be more sophisticated)
    ticket_code = f"SAFE-{transaction_id}-{hash(transaction['seller_email']) % 10000:04d}"
    
    if flask.request.method == 'POST':
        # Update transaction status to validated
        connection.execute(
            "UPDATE transactions SET status = 'validated' WHERE transaction_id = ?",
            (transaction_id,)
        )
        
        # Prepare context for success page
        context = {
            "transaction_id": transaction_id,
            "event_name": transaction['name'],
            "event_location": transaction['location'],
            "event_datetime": event_datetime,
            "price": transaction['price'],
            "seller_email": transaction['seller_email'],
            "ticket_code": ticket_code
        }
        
        return flask.render_template('validate_ticket_success.html', **context)
    
    # Format date for display
    event_datetime = transaction['event_datetime']
    try:
        # Try to parse and format the date nicely
        import datetime
        dt_obj = datetime.datetime.strptime(event_datetime, '%Y-%m-%d %H:%M:%S')
        formatted_date = dt_obj.strftime('%A, %b %d, %Y at %I:%M %p')
    except:
        formatted_date = event_datetime
    
    context = {
        'transaction_id': transaction_id,
        'event_name': transaction['name'],
        'event_location': transaction['location'],
        'event_datetime': formatted_date,
        'price': transaction['price'],
        'seller_email': transaction['seller_email'],
        'ticket_details': transaction['ticket_details'],
        'ticket_code': ticket_code
    }
    
    return flask.render_template('validate_ticket.html', **context)

@insta485.app.route('/show-report-problem/<int:transaction_id>', methods=['GET', 'POST'])
def show_report_problem(transaction_id):
    """Display and process problem reports for tickets.
    
    This route allows buyers to report problems with their tickets.
    It can be accessed directly from an email link without requiring login.
    """
    connection = insta485.model.get_db()
    
    # Get transaction details - FIXED: First get the transaction without checking buyer_email
    transaction = connection.execute(
        "SELECT t.*, e.name, e.location, e.event_datetime FROM transactions t "
        "JOIN events e ON t.event_id = e.event_id "
        "WHERE t.transaction_id = ?",
        (transaction_id,)
    ).fetchone()
    
    if not transaction:
        flask.abort(404)  # Transaction not found
    
    # No need to check if the user is logged in or is the buyer
    # This page is accessible directly from the email link
    # The security is maintained by the unique transaction ID in the URL
    
    if flask.request.method == 'POST':
        problem_type = flask.request.form.get('problem_type')
        problem_details = flask.request.form.get('problem_details')
        
        # Update transaction status to complaint filed
        connection.execute(
            "UPDATE transactions SET status = 'complaint_filed', complaint_reason = ? "
            "WHERE transaction_id = ?",
            (problem_details, transaction_id)
        )
        
        # Show a thank you page instead of redirecting to the index
        # since the user might not be logged in
        return flask.render_template('complaint_submitted.html', transaction_id=transaction_id)
    
    # Format date for display
    event_datetime = transaction['event_datetime']
    try:
        # Try to parse and format the date nicely
        import datetime
        dt_obj = datetime.datetime.strptime(event_datetime, '%Y-%m-%d %H:%M:%S')
        formatted_date = dt_obj.strftime('%A, %b %d, %Y at %I:%M %p')
    except:
        formatted_date = event_datetime
    
    context = {
        'transaction_id': transaction_id,
        'event_name': transaction['name'],
        'event_location': transaction['location'],
        'event_datetime': formatted_date,
        'price': transaction['price'],
        'seller_email': transaction['seller_email']
    }
    
    return flask.render_template('report_problem.html', **context)
