"""
Comprehensive Error Handling and Edge Case Management for Safe Transaction
Handles all possible failure scenarios and edge cases
"""
import json
from datetime import datetime, timedelta
import insta485
from insta485.email_automation import send_email


class ErrorHandler:
    """Handles all error scenarios and edge cases"""
    
    def __init__(self):
        pass
    
    def handle_verification_failure(self, transaction_id, verification_result, email_data):
        """
        Handle when ticket verification fails
        
        Scenarios:
        1. Event name doesn't match
        2. Suspicious email content
        3. Untrusted sender domain
        4. Low verification score
        """
        connection = insta485.model.get_db()
        
        # Get transaction details
        transaction = connection.execute(
            """
            SELECT t.*, e.name as event_name
            FROM transactions t
            JOIN events e ON t.event_id = e.event_id
            WHERE t.transaction_id = ?
            """,
            (transaction_id,)
        ).fetchone()
        
        if not transaction:
            return
        
        # Update transaction with failure details
        connection.execute("""
            UPDATE transactions 
            SET status = 'rejected',
                verification_notes = ?,
                ticket_verification_score = ?
            WHERE transaction_id = ?
        """, (
            f"VERIFICATION FAILED: {verification_result['reason']} | Notes: {verification_result['notes']}",
            verification_result['score'],
            transaction_id
        ))
        connection.commit()
        
        # Send notification to seller about verification failure
        self._notify_seller_verification_failed(transaction, verification_result, email_data)
        
        # Send notification to buyer about potential scam attempt
        self._notify_buyer_scam_prevented(transaction, verification_result)
        
        # Return original ticket to seller
        self._return_ticket_to_seller(transaction_id, email_data, "verification_failed")
        
        print(f"🚨 VERIFICATION FAILED: Transaction {transaction_id} rejected - {verification_result['reason']}")
    
    def handle_payment_timeout(self, transaction_id):
        """
        Handle when buyer doesn't pay within the deadline
        
        Actions:
        1. Return ticket to seller
        2. Notify both parties
        3. Update transaction status
        """
        connection = insta485.model.get_db()
        
        transaction = connection.execute(
            """
            SELECT t.*, e.name as event_name
            FROM transactions t
            JOIN events e ON t.event_id = e.event_id
            WHERE t.transaction_id = ?
            """,
            (transaction_id,)
        ).fetchone()
        
        if not transaction:
            return
        
        # Update status
        connection.execute("""
            UPDATE transactions 
            SET status = 'expired_no_payment'
            WHERE transaction_id = ?
        """, (transaction_id,))
        connection.commit()
        
        # Return ticket to seller if we have it
        if transaction['ticket_email_data']:
            ticket_data = json.loads(transaction['ticket_email_data'])
            self._return_ticket_to_seller(transaction_id, ticket_data, "payment_timeout")
        
        # Send notifications
        self._notify_payment_timeout(transaction)
        
        print(f"⏰ PAYMENT TIMEOUT: Transaction {transaction_id} expired - returning ticket to seller")
    
    def handle_ticket_timeout(self, transaction_id):
        """
        Handle when seller doesn't send ticket within deadline
        
        Actions:
        1. Cancel transaction
        2. Notify both parties
        3. Update status
        """
        connection = insta485.model.get_db()
        
        transaction = connection.execute(
            """
            SELECT t.*, e.name as event_name
            FROM transactions t
            JOIN events e ON t.event_id = e.event_id
            WHERE t.transaction_id = ?
            """,
            (transaction_id,)
        ).fetchone()
        
        if not transaction:
            return
        
        # Update status
        connection.execute("""
            UPDATE transactions 
            SET status = 'expired_no_ticket'
            WHERE transaction_id = ?
        """, (transaction_id,))
        connection.commit()
        
        # Send notifications
        self._notify_ticket_timeout(transaction)
        
        print(f"⏰ TICKET TIMEOUT: Transaction {transaction_id} expired - seller didn't send ticket")
    
    def handle_complaint_filed(self, transaction_id, complaint_reason, buyer_email):
        """
        Handle when buyer files a complaint about tickets
        
        Actions:
        1. Hold funds
        2. Notify admin
        3. Start investigation process
        """
        connection = insta485.model.get_db()
        
        transaction = connection.execute(
            """
            SELECT t.*, e.name as event_name
            FROM transactions t
            JOIN events e ON t.event_id = e.event_id
            WHERE t.transaction_id = ?
            """,
            (transaction_id,)
        ).fetchone()
        
        if not transaction:
            return {'success': False, 'error': 'Transaction not found'}
        
        # Verify buyer authorization
        if transaction['buyer_email'] != buyer_email:
            return {'success': False, 'error': 'Unauthorized'}
        
        # Update transaction
        connection.execute("""
            UPDATE transactions 
            SET status = 'complaint_filed',
                complaint_reason = ?
            WHERE transaction_id = ?
        """, (complaint_reason, transaction_id))
        connection.commit()
        
        # Send notifications
        self._notify_complaint_filed(transaction, complaint_reason)
        
        print(f"🚨 COMPLAINT FILED: Transaction {transaction_id} - {complaint_reason}")
        
        return {'success': True, 'message': 'Complaint filed successfully'}
    
    def handle_duplicate_email(self, transaction_id, email_data):
        """
        Handle when seller sends multiple emails for same transaction
        
        Actions:
        1. Check if already processed
        2. Update with latest email if needed
        3. Prevent duplicate processing
        """
        connection = insta485.model.get_db()
        
        transaction = connection.execute(
            "SELECT * FROM transactions WHERE transaction_id = ?",
            (transaction_id,)
        ).fetchone()
        
        if not transaction:
            return {'error': 'Transaction not found'}
        
        # If already verified and activated, ignore duplicate
        if transaction['status'] in ['waiting_for_payment', 'both_received_processing', 'ticket_forwarded_funds_held', 'completed']:
            print(f"⚠️ DUPLICATE EMAIL: Ignoring duplicate ticket email for transaction {transaction_id}")
            return {'error': 'Transaction already processed'}
        
        # If in pending state, allow reprocessing (seller might have sent updated ticket)
        if transaction['status'] == 'pending_ticket_submission':
            print(f"🔄 UPDATED EMAIL: Processing updated ticket email for transaction {transaction_id}")
            return {'success': True, 'message': 'Processing updated ticket email'}
        
        return {'error': 'Transaction in invalid state for email processing'}
    
    def handle_invalid_sender(self, transaction_id, sender_email, expected_seller):
        """
        Handle when email comes from wrong sender
        
        Actions:
        1. Reject email
        2. Log security incident
        3. Notify seller of unauthorized attempt
        """
        print(f"🚨 SECURITY ALERT: Invalid sender for transaction {transaction_id}")
        print(f"   Expected: {expected_seller}")
        print(f"   Received: {sender_email}")
        
        # Send security alert to legitimate seller
        try:
            subject = "🚨 Security Alert - Unauthorized Email Attempt"
            html_content = f"""
            <h2>🚨 Security Alert</h2>
            <p>Someone attempted to send a ticket email for your transaction #{transaction_id} from an unauthorized email address.</p>
            <p><strong>Unauthorized sender:</strong> {sender_email}</p>
            <p><strong>Your registered email:</strong> {expected_seller}</p>
            <p>If this was you, please send the ticket from your registered email address. If not, please contact support immediately.</p>
            <p>Your transaction remains secure and unaffected.</p>
            """
            
            send_email(expected_seller, subject, html_content)
            
        except Exception as e:
            print(f"❌ Failed to send security alert: {e}")
        
        return {'error': 'Unauthorized sender - security alert sent to seller'}
    
    # Notification methods
    def _notify_seller_verification_failed(self, transaction, verification_result, email_data):
        """Notify seller that their ticket verification failed"""
        try:
            original_details = json.loads(transaction['original_event_details'])
            event_name = original_details['event_name']
            
            subject = f"❌ Ticket Verification Failed - {event_name}"
            html_content = f"""
            <h2>❌ Ticket Verification Failed</h2>
            <p>Unfortunately, the ticket you sent for <strong>{event_name}</strong> could not be verified.</p>
            
            <h3>📋 Verification Details:</h3>
            <p><strong>Score:</strong> {verification_result['score']}/100 (minimum 70 required)</p>
            <p><strong>Reason:</strong> {verification_result['reason']}</p>
            <p><strong>Notes:</strong> {verification_result['notes']}</p>
            
            <h3>🔄 What to do next:</h3>
            <ul>
                <li>Check that the event name matches exactly: <strong>{event_name}</strong></li>
                <li>Ensure you're forwarding the original ticket email from the ticket provider</li>
                <li>Make sure the email contains ticket details (seats, sections, etc.)</li>
                <li>Send from a recognized ticket provider if possible</li>
            </ul>
            
            <p>Your original ticket has been returned to you. You can try sending it again.</p>
            <p><strong>Transaction ID:</strong> {transaction['transaction_id']}</p>
            """
            
            send_email(transaction['seller_email'], subject, html_content)
            
        except Exception as e:
            print(f"❌ Failed to send verification failure notification to seller: {e}")
    
    def _notify_buyer_scam_prevented(self, transaction, verification_result):
        """Notify buyer that we prevented a potential scam"""
        try:
            original_details = json.loads(transaction['original_event_details'])
            event_name = original_details['event_name']
            
            subject = f"🛡️ Scam Prevented - {event_name} Transaction Cancelled"
            html_content = f"""
            <h2>🛡️ We Protected You From a Potential Scam!</h2>
            <p>Good news! Our security system detected suspicious activity in your transaction for <strong>{event_name}</strong> and automatically cancelled it to protect you.</p>
            
            <h3>🔍 What we found:</h3>
            <p>The seller's ticket failed our verification process with a score of {verification_result['score']}/100.</p>
            <p><strong>Issues detected:</strong> {verification_result['reason']}</p>
            
            <h3>✅ You're fully protected:</h3>
            <ul>
                <li>No payment was processed</li>
                <li>No personal information was shared</li>
                <li>The transaction has been cancelled</li>
                <li>You can safely look for tickets elsewhere</li>
            </ul>
            
            <p>This is exactly why Safe Transaction exists - to protect you from scams and fake tickets!</p>
            <p><strong>Transaction ID:</strong> {transaction['transaction_id']}</p>
            """
            
            send_email(transaction['buyer_email'], subject, html_content)
            
        except Exception as e:
            print(f"❌ Failed to send scam prevention notification to buyer: {e}")
    
    def _notify_payment_timeout(self, transaction):
        """Notify both parties about payment timeout"""
        try:
            original_details = json.loads(transaction['original_event_details'])
            event_name = original_details['event_name']
            
            # Notify buyer
            buyer_subject = f"⏰ Payment Deadline Passed - {event_name}"
            buyer_html = f"""
            <h2>⏰ Payment Deadline Passed</h2>
            <p>The payment deadline for your <strong>{event_name}</strong> tickets has passed.</p>
            <p>The transaction has been automatically cancelled and the tickets have been returned to the seller.</p>
            <p>If you still want these tickets, you'll need to create a new transaction.</p>
            <p><strong>Transaction ID:</strong> {transaction['transaction_id']}</p>
            """
            
            send_email(transaction['buyer_email'], buyer_subject, buyer_html)
            
            # Notify seller
            seller_subject = f"🔄 Tickets Returned - {event_name} Payment Timeout"
            seller_html = f"""
            <h2>🔄 Tickets Returned</h2>
            <p>The buyer for your <strong>{event_name}</strong> tickets didn't pay within the deadline.</p>
            <p>Your tickets have been automatically returned to you and you can create a new listing.</p>
            <p><strong>Transaction ID:</strong> {transaction['transaction_id']}</p>
            """
            
            send_email(transaction['seller_email'], seller_subject, seller_html)
            
        except Exception as e:
            print(f"❌ Failed to send payment timeout notifications: {e}")
    
    def _notify_ticket_timeout(self, transaction):
        """Notify both parties about ticket timeout"""
        try:
            original_details = json.loads(transaction['original_event_details'])
            event_name = original_details['event_name']
            
            # Notify seller
            seller_subject = f"⏰ Ticket Deadline Passed - {event_name}"
            seller_html = f"""
            <h2>⏰ Ticket Deadline Passed</h2>
            <p>The deadline to send your tickets for <strong>{event_name}</strong> has passed.</p>
            <p>The transaction has been automatically cancelled.</p>
            <p>If you still have the tickets, you can create a new listing.</p>
            <p><strong>Transaction ID:</strong> {transaction['transaction_id']}</p>
            """
            
            send_email(transaction['seller_email'], seller_subject, seller_html)
            
            # Notify buyer
            buyer_subject = f"❌ Listing Cancelled - {event_name}"
            buyer_html = f"""
            <h2>❌ Listing Cancelled</h2>
            <p>Unfortunately, the seller for <strong>{event_name}</strong> didn't send their tickets within the deadline.</p>
            <p>The transaction has been automatically cancelled for your protection.</p>
            <p>You can look for other tickets for this event.</p>
            <p><strong>Transaction ID:</strong> {transaction['transaction_id']}</p>
            """
            
            send_email(transaction['buyer_email'], buyer_subject, buyer_html)
            
        except Exception as e:
            print(f"❌ Failed to send ticket timeout notifications: {e}")
    
    def _notify_complaint_filed(self, transaction, complaint_reason):
        """Notify all parties about filed complaint"""
        try:
            original_details = json.loads(transaction['original_event_details'])
            event_name = original_details['event_name']
            
            # Notify buyer (confirmation)
            buyer_subject = f"📋 Complaint Filed - {event_name}"
            buyer_html = f"""
            <h2>📋 Complaint Filed Successfully</h2>
            <p>Your complaint about <strong>{event_name}</strong> has been filed and is under investigation.</p>
            <p><strong>Complaint:</strong> {complaint_reason}</p>
            <p>Funds are being held while we investigate. You'll hear from us within 24 hours.</p>
            <p><strong>Transaction ID:</strong> {transaction['transaction_id']}</p>
            """
            
            send_email(transaction['buyer_email'], buyer_subject, buyer_html)
            
            # Notify seller
            seller_subject = f"🚨 Complaint Filed - {event_name}"
            seller_html = f"""
            <h2>🚨 Complaint Filed Against Your Transaction</h2>
            <p>A complaint has been filed regarding your <strong>{event_name}</strong> tickets.</p>
            <p><strong>Complaint:</strong> {complaint_reason}</p>
            <p>Funds are being held while we investigate. Please be prepared to provide additional information if requested.</p>
            <p><strong>Transaction ID:</strong> {transaction['transaction_id']}</p>
            """
            
            send_email(transaction['seller_email'], seller_subject, seller_html)
            
            # Notify admin
            admin_subject = f"🚨 ADMIN: Complaint Filed - Transaction {transaction['transaction_id']}"
            admin_html = f"""
            <h2>🚨 New Complaint Requires Investigation</h2>
            <p><strong>Transaction ID:</strong> {transaction['transaction_id']}</p>
            <p><strong>Event:</strong> {event_name}</p>
            <p><strong>Buyer:</strong> {transaction['buyer_email']}</p>
            <p><strong>Seller:</strong> {transaction['seller_email']}</p>
            <p><strong>Amount:</strong> ${transaction['price']}</p>
            <p><strong>Complaint:</strong> {complaint_reason}</p>
            <p>Please investigate and resolve within 24 hours.</p>
            """
            
            send_email('admin@safetransaction.com', admin_subject, admin_html)
            
        except Exception as e:
            print(f"❌ Failed to send complaint notifications: {e}")
    
    def _return_ticket_to_seller(self, transaction_id, ticket_data, reason):
        """Return original ticket email to seller"""
        try:
            from insta485.email_automation import forward_ticket_email
            
            connection = insta485.model.get_db()
            transaction = connection.execute(
                "SELECT seller_email FROM transactions WHERE transaction_id = ?",
                (transaction_id,)
            ).fetchone()
            
            if transaction:
                success = forward_ticket_email(
                    to_email=transaction['seller_email'],
                    original_email_data=ticket_data,
                    transaction_id=transaction_id,
                    return_mode=True
                )
                
                if success:
                    print(f"📧 Ticket returned to seller for transaction {transaction_id} - {reason}")
                else:
                    print(f"❌ Failed to return ticket to seller for transaction {transaction_id}")
            
        except Exception as e:
            print(f"❌ Error returning ticket to seller: {e}")


# Global error handler instance
error_handler = ErrorHandler()
