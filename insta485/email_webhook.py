"""
Email Webhook System for Safe Transaction
Receives and processes incoming ticket emails from sellers
"""
import json
import email
import base64
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import re
import insta485


class EmailWebhookHandler:
    """Handles incoming email webhooks for ticket processing"""
    
    def __init__(self):
        pass
    
    def process_incoming_email(self, webhook_data):
        """
        Process incoming email from webhook
        Expected webhook format from email service (like Mailgun, SendGrid, etc.)
        """
        try:
            connection = insta485.model.get_db()
            
            # Extract email data from webhook
            email_data = self._parse_webhook_data(webhook_data)
            
            # Extract transaction ID from recipient email
            transaction_id = self._extract_transaction_id(email_data['to'])
            
            if not transaction_id:
                return {'error': 'Invalid recipient email format'}
            
            # Get transaction details
            transaction = self._get_transaction(transaction_id, connection)
            if not transaction:
                return {'error': 'Transaction not found'}
            
            # Verify transaction is in correct state
            if transaction['status'] != 'waiting_for_ticket':
                return {'error': f'Transaction in wrong state: {transaction["status"]}'}
            
            # Verify ticket deadline hasn't passed
            if datetime.now() > datetime.fromisoformat(transaction['ticket_deadline']):
                return {'error': 'Ticket deadline has passed'}
            
            # Process and verify the ticket email
            verification_result = self._verify_ticket_email(email_data, transaction)
            
            # Store email data and update transaction
            self._store_ticket_email(transaction_id, email_data, verification_result, connection)
            
            # Update transaction status and trigger payment window
            if verification_result['is_valid']:
                self._activate_payment_window(transaction_id, transaction, connection)
                return {'success': True, 'message': 'Ticket verified and payment window activated'}
            else:
                return {'error': f'Ticket verification failed: {verification_result["reason"]}'}
                
        except Exception as e:
            print(f"Error processing email webhook: {e}")
            return {'error': 'Internal processing error'}
    
    def _parse_webhook_data(self, webhook_data):
        """Parse webhook data from email service"""
        # This will vary based on your email service (Mailgun, SendGrid, etc.)
        # For now, assuming a standard format
        return {
            'from': webhook_data.get('sender', ''),
            'to': webhook_data.get('recipient', ''),
            'subject': webhook_data.get('subject', ''),
            'body_text': webhook_data.get('body-plain', ''),
            'body_html': webhook_data.get('body-html', ''),
            'attachments': webhook_data.get('attachments', []),
            'timestamp': datetime.now().isoformat()
        }
    
    def _extract_transaction_id(self, recipient_email):
        """Extract transaction ID from tx-123456@safetransaction.com format"""
        match = re.match(r'tx-(\d+)@', recipient_email.lower())
        return int(match.group(1)) if match else None
    
    def _get_transaction(self, transaction_id, connection):
        """Get transaction details from database"""
        return connection.execute(
            """
            SELECT t.*, e.name as event_name, e.location, e.event_datetime
            FROM transactions t
            JOIN events e ON t.event_id = e.event_id
            WHERE t.transaction_id = ?
            """,
            (transaction_id,)
        ).fetchone()
    
    def _verify_ticket_email(self, email_data, transaction):
        """Verify the ticket email is authentic and matches the transaction"""
        verification_score = 0
        reasons = []
        
        # 1. Check sender domain (basic verification)
        sender_domain = email_data['from'].split('@')[-1].lower()
        trusted_domains = [
            'ticketmaster.com', 'stubhub.com', 'seatgeek.com', 
            'vivid-seats.com', 'tickpick.com', 'gametime.co'
        ]
        
        if any(domain in sender_domain for domain in trusted_domains):
            verification_score += 30
            reasons.append("Trusted sender domain")
        else:
            reasons.append(f"Unknown sender domain: {sender_domain}")
        
        # 2. Check for ticket-related keywords
        content = (email_data['body_text'] + ' ' + email_data['subject']).lower()
        ticket_keywords = ['ticket', 'seat', 'section', 'row', 'event', 'venue', 'admission']
        
        keyword_matches = sum(1 for keyword in ticket_keywords if keyword in content)
        if keyword_matches >= 3:
            verification_score += 25
            reasons.append(f"Contains {keyword_matches} ticket keywords")
        
        # 3. Check for event name match
        event_name = transaction['event_name'].lower()
        if any(word in content for word in event_name.split() if len(word) > 3):
            verification_score += 20
            reasons.append("Event name matches")
        
        # 4. Check for attachments (PDFs, images)
        if email_data['attachments']:
            verification_score += 15
            reasons.append(f"Has {len(email_data['attachments'])} attachments")
        
        # 5. Check email structure (not automated reply)
        if 'noreply' not in email_data['from'].lower() and 'donotreply' not in email_data['from'].lower():
            verification_score += 10
            reasons.append("Not an automated reply")
        
        return {
            'is_valid': verification_score >= 60,  # Require 60+ points for approval
            'score': verification_score,
            'reasons': reasons,
            'max_score': 100
        }
    
    def _store_ticket_email(self, transaction_id, email_data, verification_result, connection):
        """Store the ticket email data in the database"""
        connection.execute(
            """
            UPDATE transactions 
            SET ticket_email_received = 1,
                ticket_received_time = CURRENT_TIMESTAMP,
                ticket_email_data = ?,
                ticket_verification_score = ?
            WHERE transaction_id = ?
            """,
            (
                json.dumps(email_data),
                verification_result['score'],
                transaction_id
            )
        )
        connection.commit()
    
    def _activate_payment_window(self, transaction_id, transaction, connection):
        """Activate the 5-minute payment window for the buyer"""
        # Set payment deadline to 5 minutes from now
        payment_deadline = datetime.now() + timedelta(minutes=5)
        
        # Update transaction status
        connection.execute(
            """
            UPDATE transactions 
            SET status = 'waiting_for_payment',
                payment_deadline = ?
            WHERE transaction_id = ?
            """,
            (payment_deadline.isoformat(), transaction_id)
        )
        connection.commit()
        
        # Send notifications
        from insta485.email_automation import send_buyer_notification, send_seller_instructions
        
        # Notify buyer that tickets are ready and payment is required
        event_details = {
            'name': transaction['event_name'],
            'location': transaction['location'],
            'datetime': transaction['event_datetime']
        }
        
        send_buyer_notification(
            transaction_id=transaction_id,
            buyer_email=transaction['buyer_email'],
            seller_email=transaction['seller_email'],
            price=transaction['price'],
            event_details=event_details,
            payment_deadline=payment_deadline
        )
        
        # Notify seller that tickets were verified
        print(f"✅ Tickets verified for transaction {transaction_id}")
        print(f"📧 Payment window activated for buyer: {transaction['buyer_email']}")


def create_webhook_route():
    """Create Flask route for email webhook"""
    import flask
    
    @insta485.app.route('/webhook/email/ticket', methods=['POST'])
    def handle_email_webhook():
        """Handle incoming email webhook from email service"""
        try:
            # Get webhook data
            webhook_data = flask.request.get_json() or flask.request.form.to_dict()
            
            # Process the email
            handler = EmailWebhookHandler()
            result = handler.process_incoming_email(webhook_data)
            
            if 'error' in result:
                return flask.jsonify(result), 400
            else:
                return flask.jsonify(result), 200
                
        except Exception as e:
            print(f"Webhook error: {e}")
            return flask.jsonify({'error': 'Webhook processing failed'}), 500

# Initialize the webhook route
create_webhook_route()
