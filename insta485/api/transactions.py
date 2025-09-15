"""
API endpoints for the automated transaction system
"""
import flask
import json
import stripe
from datetime import datetime, timedelta
import insta485
from insta485.transaction_manager import TransactionManager
# Email processing functionality will be added later


@insta485.app.route('/api/transactions/create', methods=['POST'])
def create_transaction_api():
    """
    Create new transaction listing
    
    POST /api/transactions/create
    {
        "buyer_email": "buyer@example.com",
        "price": 150.00,
        "event_name": "Taylor Swift Concert",
        "event_location": "MetLife Stadium",
        "event_datetime": "2024-07-15 20:00:00",
        "ticket_deadline_hours": 24,
        "payment_deadline_hours": 48
    }
    """
    if 'email' not in flask.session:
        return flask.jsonify({'error': 'Authentication required'}), 401
    
    seller_email = flask.session['email']
    data = flask.request.get_json()
    
    # Validate required fields
    required_fields = ['buyer_email', 'price', 'event_name', 'event_location', 'event_datetime']
    for field in required_fields:
        if field not in data:
            return flask.jsonify({'error': f'Missing field: {field}'}), 400
    
    # Validate seller isn't creating transaction with themselves
    if seller_email == data['buyer_email']:
        return flask.jsonify({'error': 'Cannot create transaction with yourself'}), 400
    
    try:
        transaction_manager = TransactionManager()
        
        event_details = {
            'name': data['event_name'],
            'location': data['event_location'],
            'datetime': data['event_datetime']
        }
        
        result = transaction_manager.create_listing(
            seller_email=seller_email,
            buyer_email=data['buyer_email'],
            price=float(data['price']),
            event_details=event_details,
            ticket_deadline_hours=data.get('ticket_deadline_hours', 24),
            payment_deadline_hours=data.get('payment_deadline_hours', 48)
        )
        
        return flask.jsonify({
            'success': True,
            'transaction_id': result['transaction_id'],
            'ticket_email': result['ticket_email'],
            'ticket_deadline': result['ticket_deadline'].isoformat(),
            'payment_deadline': result['payment_deadline'].isoformat(),
            'instructions': f"Send your tickets to: {result['ticket_email']}"
        })
        
    except Exception as e:
        return flask.jsonify({'error': str(e)}), 500


@insta485.app.route('/api/transactions/<int:transaction_id>/pay', methods=['POST'])
def get_payment_checkout_url(transaction_id):
    """
    Get Stripe checkout URL for buyer payment
    
    POST /api/transactions/123/pay
    Returns: {"success": true, "checkout_url": "https://checkout.stripe.com/..."}
    """
    try:
        connection = insta485.model.get_db()
        transaction = connection.execute(
            "SELECT price FROM transactions WHERE transaction_id = ?",
            (transaction_id,)
        ).fetchone()

        if not transaction:
            return flask.jsonify({'success': False, 'error': 'Transaction not found'}), 404

        amount = int(transaction['price'] * 100)  # Convert to cents as integer
        
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
            success_url=flask.url_for('payment_success', transaction_id=transaction_id, _external=True),
            cancel_url=flask.url_for('payment_cancel', _external=True),
        )
        
        # Store transaction_id in session for success page
        flask.session['transaction_id'] = transaction_id
        
        return flask.jsonify({
            'success': True,
            'checkout_url': session.url
        })
            
    except Exception as e:
        return flask.jsonify({'success': False, 'error': str(e)}), 500


@insta485.app.route('/api/transactions/<int:transaction_id>/confirm', methods=['POST'])
def confirm_receipt_api(transaction_id):
    """
    Buyer confirms receipt of valid tickets
    
    POST /api/transactions/123/confirm
    """
    if 'email' not in flask.session:
        return flask.jsonify({'error': 'Authentication required'}), 401
    
    buyer_email = flask.session['email']
    
    try:
        transaction_manager = TransactionManager()
        result = transaction_manager.confirm_buyer_receipt(
            transaction_id=transaction_id,
            buyer_email=buyer_email
        )
        
        if result['success']:
            return flask.jsonify({
                'success': True,
                'message': 'Receipt confirmed, funds released to seller'
            })
        else:
            return flask.jsonify({'error': result['error']}), 400
            
    except Exception as e:
        return flask.jsonify({'error': str(e)}), 500


@insta485.app.route('/api/transactions/<int:transaction_id>/complaint', methods=['POST'])
def file_complaint_api(transaction_id):
    """
    File complaint about transaction
    
    POST /api/transactions/123/complaint
    {
        "reason": "Fake tickets received"
    }
    """
    if 'email' not in flask.session:
        return flask.jsonify({'error': 'Authentication required'}), 401
    
    buyer_email = flask.session['email']
    data = flask.request.get_json()
    
    if 'reason' not in data:
        return flask.jsonify({'error': 'Missing complaint reason'}), 400
    
    try:
        from insta485.error_handler import error_handler
        result = error_handler.handle_complaint_filed(
            transaction_id=transaction_id,
            complaint_reason=data['reason'],
            buyer_email=buyer_email
        )
        
        if result['success']:
            return flask.jsonify({
                'success': True,
                'message': 'Complaint filed, funds are now held for review'
            })
        else:
            return flask.jsonify({'error': result['error']}), 400
            
    except Exception as e:
        return flask.jsonify({'error': str(e)}), 500


@insta485.app.route('/api/transactions/<int:transaction_id>/status', methods=['GET'])
def get_transaction_status_api(transaction_id):
    """
    Get current transaction status
    
    GET /api/transactions/123/status
    """
    try:
        connection = insta485.model.get_db()
        transaction = connection.execute("""
            SELECT t.*, e.name as event_name, e.location as event_location,
                   e.event_datetime
            FROM transactions t
            JOIN events e ON t.event_id = e.event_id
            WHERE t.transaction_id = ?
        """, (transaction_id,)).fetchone()
        
        if not transaction:
            return flask.jsonify({'error': 'Transaction not found'}), 404
        
        # Convert to dict and handle datetime serialization
        result = dict(transaction)
        for key, value in result.items():
            if isinstance(value, datetime):
                result[key] = value.isoformat()
        
        return flask.jsonify({
            'success': True,
            'transaction': result
        })
        
    except Exception as e:
        return flask.jsonify({'error': str(e)}), 500


@insta485.app.route('/webhook/email/ticket/<int:transaction_id>', methods=['POST'])
def receive_ticket_email(transaction_id):
    """
    Webhook endpoint for receiving ticket emails
    Called by email service when email sent to ticket-{id}@safetransaction.com
    """
    try:
        # Parse incoming email data
        email_data = {
            'sender': flask.request.form.get('sender'),
            'subject': flask.request.form.get('subject'),
            'body': flask.request.form.get('body-plain', ''),
            'html_body': flask.request.form.get('body-html', ''),
            'attachments': [],  # Handle attachments if needed
            'received_time': datetime.now()
        }
        
        # Process through transaction manager
        transaction_manager = TransactionManager()
        result = transaction_manager.process_incoming_ticket(
            transaction_id=transaction_id,
            email_data=email_data
        )
        
        if result['success']:
            return flask.jsonify({
                'success': True,
                'message': 'Ticket processed successfully',
                'verification_score': result['verification_score']
            })
        else:
            return flask.jsonify({'error': result['error']}), 400
            
    except Exception as e:
        return flask.jsonify({'error': str(e)}), 500


@insta485.app.route('/pay/<int:transaction_id>')
def show_payment_page(transaction_id):
    """
    Redirect directly to Stripe Checkout for buyer payment
    """
    try:
        connection = insta485.model.get_db()
        transaction = connection.execute("""
            SELECT t.*, e.name as event_name, e.location as event_location,
                   e.event_datetime
            FROM transactions t
            JOIN events e ON t.event_id = e.event_id
            WHERE t.transaction_id = ?
        """, (transaction_id,)).fetchone()
        
        if not transaction:
            flask.abort(404)
        
        # Check if transaction is in valid state for payment
        if transaction['status'] not in ['waiting_for_payment', 'both_received_processing']:
            return flask.render_template('payment_error.html', 
                                       error='This transaction is no longer available for payment')
        
        # Check if payment deadline has passed
        payment_deadline = transaction['payment_deadline']
        if isinstance(payment_deadline, str):
            # Convert string to datetime
            try:
                if 'T' in payment_deadline:
                    # ISO format
                    payment_deadline = datetime.fromisoformat(payment_deadline.replace('Z', '+00:00'))
                else:
                    # SQLite format
                    payment_deadline = datetime.strptime(payment_deadline, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                return flask.render_template('payment_error.html',
                                           error='Invalid payment deadline format')
        
        if datetime.now() > payment_deadline:
            return flask.render_template('payment_error.html',
                                       error='Payment deadline has passed')
        
        # Use the existing send_payment_buyer function to redirect to Stripe Checkout
        from insta485.views.manage import send_payment_buyer
        return send_payment_buyer(transaction_id)
        
    except Exception as e:
        return flask.render_template('payment_error.html', error=str(e))


@insta485.app.route('/payment/complete/<int:transaction_id>')
def payment_complete(transaction_id):
    """
    Handle successful payment return from Stripe Checkout
    """
    try:
        # Update transaction status to indicate payment received
        connection = insta485.model.get_db()
        connection.execute("""
            UPDATE transactions 
            SET payment_received = 1,
                payment_received_time = CURRENT_TIMESTAMP,
                status = 'both_received_processing'
            WHERE transaction_id = ?
        """, (transaction_id,))
        connection.commit()
        
        # Redirect to ticket status page
        return flask.redirect(flask.url_for('show_ticket_status', transaction_id=transaction_id))
        
    except Exception as e:
        return flask.render_template('payment_error.html', error=f'Payment processing error: {str(e)}')


@insta485.app.route('/ticket/<int:transaction_id>')
def show_ticket_status(transaction_id):
    """
    Show ticket status page for buyer
    """
    try:
        connection = insta485.model.get_db()
        transaction = connection.execute("""
            SELECT t.*, e.name as event_name, e.location as event_location,
                   e.event_datetime
            FROM transactions t
            JOIN events e ON t.event_id = e.event_id
            WHERE t.transaction_id = ?
        """, (transaction_id,)).fetchone()
        
        if not transaction:
            flask.abort(404)
        
        context = {
            'transaction': transaction,
            'can_pay': transaction['status'] in ['waiting_for_payment', 'both_received_processing'],
            'can_confirm': transaction['status'] == 'ticket_forwarded_funds_held',
            'can_complain': transaction['status'] in ['ticket_forwarded_funds_held', 'completed']
        }
        
        return flask.render_template('ticket_status.html', **context)
        
    except Exception as e:
        flask.abort(500)


# Background job endpoint (for cron/scheduler)
@insta485.app.route('/api/background/check-deadlines', methods=['POST'])
def run_deadline_check():
    """
    Manually trigger deadline check (for cron jobs)
    """
    try:
        transaction_manager = TransactionManager()
        transaction_manager.check_scheduled_deadlines()
        
        return flask.jsonify({
            'success': True,
            'message': 'Deadline check completed'
        })
        
    except Exception as e:
        return flask.jsonify({'error': str(e)}), 500


# Testing endpoint for simulation
@insta485.app.route('/api/transactions/<int:transaction_id>/simulate-verification', methods=['POST'])
def simulate_verification(transaction_id):
    """
    Testing endpoint: Simulate ticket email verification process
    This bypasses the email monitoring and directly processes a fake ticket email
    """
    try:
        email_data = flask.request.get_json()
        
        if not email_data:
            return flask.jsonify({'success': False, 'error': 'No email data provided'})
        
        # Use TransactionManager to process the simulated ticket
        transaction_manager = TransactionManager()
        result = transaction_manager.process_incoming_ticket(transaction_id, email_data)
        
        if result['success']:
            print(f"🧪 SIMULATION: Transaction {transaction_id} activated successfully")
            print(f"📧 SIMULATION: Buyer notification would be sent")
            print(f"⏰ SIMULATION: Payment deadline set to {result.get('payment_deadline', 'N/A')}")
            print(f"🔍 SIMULATION: Verification score: {result.get('verification_score', 'N/A')}")
            
            return flask.jsonify({
                'success': True,
                'status': result.get('status', 'listing_activated'),
                'payment_deadline': result.get('payment_deadline'),
                'verification_score': result.get('verification_score')
            })
        else:
            return flask.jsonify({'success': False, 'error': result.get('error', 'Unknown error')})
            
    except Exception as e:
        print(f"❌ SIMULATION ERROR: {e}")
        return flask.jsonify({'success': False, 'error': str(e)})


# Testing endpoint for direct verification
@insta485.app.route('/api/transactions/<int:transaction_id>/mark-verified', methods=['POST'])
def mark_as_verified(transaction_id):
    """
    Testing endpoint: Directly mark transaction as verified and activate listing
    This bypasses both email sending and verification, directly setting status to waiting_for_payment
    """
    try:
        connection = insta485.model.get_db()
        
        # Get transaction details
        transaction = connection.execute(
            "SELECT * FROM transactions WHERE transaction_id = ?",
            (transaction_id,)
        ).fetchone()
        
        if not transaction:
            return flask.jsonify({'success': False, 'error': 'Transaction not found'})
        
        # Must be in pending state
        if transaction['status'] != 'pending_ticket_submission':
            return flask.jsonify({'success': False, 'error': f'Transaction in wrong state: {transaction["status"]}'})
        
        # Set 1-hour payment deadline
        payment_deadline = datetime.now() + timedelta(hours=1)
        
        # Format payment deadline for SQLite (no microseconds, space instead of T)
        payment_deadline_str = payment_deadline.strftime('%Y-%m-%d %H:%M:%S')
        
        # Mark as verified and activate listing
        connection.execute("""
            UPDATE transactions 
            SET status = 'waiting_for_payment',
                ticket_email_received = 1,
                ticket_received_time = CURRENT_TIMESTAMP,
                ticket_verification_score = 100,
                ticket_details_match = 1,
                verification_notes = 'TEST: Manually marked as verified',
                created_time = CURRENT_TIMESTAMP,
                payment_deadline = ?
            WHERE transaction_id = ?
        """, (payment_deadline_str, transaction_id))
        
        connection.commit()
        
        # Send buyer notification (same as in verification flow)
        try:
            from insta485.email_automation import send_modern_buyer_notification
            original_details = json.loads(transaction['original_event_details'])
            
            # Prepare event details for email
            event_details = {
                'name': original_details['event_name'],
                'location': original_details.get('location', 'TBD'),
                'datetime': original_details.get('datetime', 'TBD')
            }
            
            send_modern_buyer_notification(
                transaction_id=transaction_id,
                buyer_email=transaction['buyer_email'],
                seller_email=transaction['seller_email'],
                price=transaction['price'],
                event_details=event_details,
                payment_deadline=payment_deadline
            )
            print(f"📧 TEST: Buyer notification sent to {transaction['buyer_email']}")
        except Exception as e:
            print(f"📧 TEST: Failed to send buyer notification: {e}")
            import traceback
            traceback.print_exc()
        
        print(f"✅ TEST: Transaction {transaction_id} manually marked as verified and activated")
        print(f"⏰ TEST: Payment deadline set to {payment_deadline}")
        
        return flask.jsonify({
            'success': True,
            'status': 'waiting_for_payment',
            'payment_deadline': payment_deadline_str,
            'verification_score': 100,
            'message': 'Listing manually verified and activated'
        })
        
    except Exception as e:
        print(f"❌ TEST ERROR: {e}")
        return flask.jsonify({'success': False, 'error': str(e)})


# New Test Verify API endpoint
@insta485.app.route('/api/test-verify', methods=['POST'])
def test_verify_transaction():
    """
    ⚡ TEST: Mark as Verified - Testing endpoint
    Instantly marks a transaction as verified and sends buyer notification,
    bypassing the normal email verification flow.
    
    POST /api/test-verify
    {
        "transaction_id": 123,
        "test_mode": true
    }
    """
    try:
        data = flask.request.get_json()
        
        if not data or 'transaction_id' not in data:
            return flask.jsonify({'success': False, 'error': 'Missing transaction_id'})
        
        transaction_id = data['transaction_id']
        connection = insta485.model.get_db()
        
        # Get transaction details
        transaction = connection.execute(
            "SELECT * FROM transactions WHERE transaction_id = ?",
            (transaction_id,)
        ).fetchone()
        
        if not transaction:
            return flask.jsonify({'success': False, 'error': 'Transaction not found'})
        
        # Must be in pending_ticket_submission state
        if transaction['status'] != 'pending_ticket_submission':
            return flask.jsonify({
                'success': False, 
                'error': f'Transaction must be in pending_ticket_submission state. Current: {transaction["status"]}'
            })
        
        # Set 1-hour payment deadline from now
        payment_deadline = datetime.now() + timedelta(hours=1)
        payment_deadline_str = payment_deadline.strftime('%Y-%m-%d %H:%M:%S')
        
        # Update transaction: instant verification (100%) and move to waiting_for_payment
        connection.execute("""
            UPDATE transactions 
            SET status = 'waiting_for_payment',
                ticket_email_received = 1,
                ticket_received_time = CURRENT_TIMESTAMP,
                ticket_verification_score = 100,
                ticket_details_match = 1,
                verification_notes = '⚡ TEST: Instant verification via Test Verify button',
                payment_deadline = ?
            WHERE transaction_id = ?
        """, (payment_deadline_str, transaction_id))
        
        connection.commit()
        
        # Send notifications using new Mailgun system
        try:
            from insta485.mailgun_sender import mailgun_sender
            original_details = json.loads(transaction['original_event_details'])
            
            # 1. Send SUCCESS notification to SELLER
            mailgun_sender.send_seller_verification_success(
                seller_email=transaction['seller_email'],
                transaction_id=transaction_id,
                event_name=original_details['event_name'],
                buyer_email=transaction['buyer_email'],
                payment_deadline=payment_deadline
            )
            
            # 2. Send PAYMENT notification to BUYER
            payment_url = f"http://localhost:8000/pay/{transaction_id}"
            
            # Parse datetime if it's a string
            event_datetime = original_details.get('datetime', 'TBD')
            if isinstance(event_datetime, str) and event_datetime != 'TBD':
                try:
                    event_datetime = datetime.strptime(event_datetime, '%Y-%m-%d %H:%M:%S')
                except:
                    pass
            
            # Use modern email template
            from insta485.email_automation import send_modern_buyer_notification
            
            # Prepare event details for email
            event_details = {
                'name': original_details['event_name'],
                'location': original_details.get('location', 'TBD'),
                'datetime': original_details.get('datetime', 'TBD')
            }
            
            send_modern_buyer_notification(
                transaction_id=transaction_id,
                buyer_email=transaction['buyer_email'],
                seller_email=transaction['seller_email'],
                price=transaction['price'],
                event_details=event_details,
                payment_deadline=payment_deadline
            )
            
            print(f"📧 TEST VERIFY: Notifications sent to seller ({transaction['seller_email']}) and buyer ({transaction['buyer_email']})")
            email_sent = True
            
        except Exception as e:
            print(f"📧 TEST VERIFY: Failed to send buyer notification: {e}")
            import traceback
            traceback.print_exc()
            email_sent = False
        
        # Log the test verification
        print(f"⚡ TEST VERIFY: Transaction {transaction_id} instantly verified")
        print(f"📈 TEST VERIFY: Verification score set to 100%")
        print(f"⏰ TEST VERIFY: Payment deadline set to {payment_deadline}")
        print(f"🔄 TEST VERIFY: Status: pending_ticket_submission → waiting_for_payment")
        
        return flask.jsonify({
            'success': True,
            'message': '⚡ TEST VERIFICATION COMPLETE',
            'details': {
                'verification_score': 100,
                'status_change': 'pending_ticket_submission → waiting_for_payment',
                'payment_deadline': payment_deadline_str,
                'buyer_notification_sent': email_sent,
                'test_metadata': {
                    'verification_method': 'test_verify_button',
                    'instant_verification': True,
                    'bypass_email_flow': True
                }
            }
        })
        
    except Exception as e:
        print(f"❌ TEST VERIFY ERROR: {e}")
        import traceback
        traceback.print_exc()
        return flask.jsonify({'success': False, 'error': str(e)})


# API endpoint to get transaction status
@insta485.app.route('/api/transactions/<int:transaction_id>/status', methods=['GET'])
def get_transaction_status(transaction_id):
    """
    Get current transaction status and details
    """
    try:
        connection = insta485.model.get_db()
        
        # Get transaction details with event info
        transaction = connection.execute(
            """
            SELECT t.*, e.name as event_name, e.location as event_location
            FROM transactions t
            LEFT JOIN events e ON t.event_id = e.event_id
            WHERE t.transaction_id = ?
            """,
            (transaction_id,)
        ).fetchone()
        
        if not transaction:
            return flask.jsonify({'success': False, 'error': 'Transaction not found'})
        
        # Convert row to dict for JSON serialization
        transaction_dict = dict(transaction)
        
        return flask.jsonify({
            'success': True,
            'transaction': transaction_dict
        })
        
    except Exception as e:
        print(f"❌ STATUS API ERROR: {e}")
        return flask.jsonify({'success': False, 'error': str(e)})
