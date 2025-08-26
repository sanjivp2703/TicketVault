"""
Complete Transaction Management System
Handles all transaction states and automated processes
"""
import json
import datetime
from datetime import timedelta
import stripe
import insta485
import insta485.model
from insta485.email_automation import (
    send_seller_instructions, 
    send_buyer_notification, 
    forward_ticket_email
)


class TransactionManager:
    """Manages all transaction states and automated processes"""
    
    def __init__(self):
        self.connection = insta485.model.get_db()
    
    def create_listing(self, seller_email, buyer_email, price, event_details, 
                      ticket_deadline_hours=24, payment_deadline_hours=48):
        """
        Create new listing with automatic deadlines
        
        Args:
            seller_email: Seller's email
            buyer_email: Buyer's email  
            price: Ticket price
            event_details: Event information
            ticket_deadline_hours: Hours seller has to send ticket (default 24)
            payment_deadline_hours: Hours buyer has to pay after ticket sent (default 48)
        """
        # Create event if doesn't exist
        event_id = self._get_or_create_event(event_details)
        
        # Calculate deadlines
        now = datetime.datetime.now()
        ticket_deadline = now + timedelta(hours=ticket_deadline_hours)
        payment_deadline = now + timedelta(hours=payment_deadline_hours)
        
        # Create transaction
        cursor = self.connection.execute("""
            INSERT INTO transactions (
                seller_email, buyer_email, price, event_id,
                ticket_deadline, payment_deadline, status
            ) VALUES (?, ?, ?, ?, ?, ?, 'waiting_for_ticket')
        """, (seller_email, buyer_email, price, event_id, 
              ticket_deadline, payment_deadline))
        
        transaction_id = cursor.lastrowid
        self.connection.commit()
        
        # Generate unique email for this transaction
        ticket_email = f"ticket-{transaction_id}@safetransaction.com"
        
        # Send instructions to seller
        send_seller_instructions(transaction_id, seller_email, ticket_email, 
                                ticket_deadline, event_details)
        
        # Send notification to buyer
        send_buyer_notification(transaction_id, buyer_email, seller_email, 
                               price, event_details, payment_deadline)
        
        # Schedule deadline checks
        self._schedule_deadline_check(transaction_id, 'ticket', ticket_deadline)
        
        return {
            'transaction_id': transaction_id,
            'ticket_email': ticket_email,
            'ticket_deadline': ticket_deadline,
            'payment_deadline': payment_deadline,
            'status': 'waiting_for_ticket'
        }
    
    def process_incoming_ticket(self, transaction_id, email_data):
        """
        Process ticket email sent to ticket-{id}@safetransaction.com
        """
        # Get transaction details
        transaction = self._get_transaction(transaction_id)
        if not transaction:
            return {'success': False, 'error': 'Transaction not found'}
        
        # Verify sender is the seller
        if email_data['sender'] != transaction['seller_email']:
            return {'success': False, 'error': 'Unauthorized sender'}
        
        # Check if already received ticket
        if transaction['ticket_email_received']:
            return {'success': False, 'error': 'Ticket already received'}
        
        # Check if past deadline
        if datetime.datetime.now() > transaction['ticket_deadline']:
            self._expire_transaction(transaction_id, 'ticket_deadline_passed')
            return {'success': False, 'error': 'Ticket deadline has passed'}
        
        # Verify ticket authenticity
        verification_result = self._verify_ticket_authenticity(transaction_id, email_data)
        
        if verification_result['score'] < 70:  # Minimum verification threshold
            self._flag_suspicious_ticket(transaction_id, verification_result)
            return {'success': False, 'error': 'Ticket verification failed'}
        
        # Store ticket data
        self.connection.execute("""
            UPDATE transactions SET 
                ticket_email_received = 1,
                ticket_received_time = CURRENT_TIMESTAMP,
                ticket_email_data = ?,
                ticket_verification_score = ?
            WHERE transaction_id = ?
        """, (json.dumps(email_data), verification_result['score'], transaction_id))
        
        # Update status and check next steps
        self._advance_transaction_state(transaction_id)
        
        return {'success': True, 'verification_score': verification_result['score']}
    
    def process_payment(self, transaction_id, payment_method_id):
        """
        Process buyer payment
        """
        transaction = self._get_transaction(transaction_id)
        if not transaction:
            return {'success': False, 'error': 'Transaction not found'}
        
        # Check if payment already received
        if transaction['payment_received']:
            return {'success': False, 'error': 'Payment already processed'}
        
        # Check if past payment deadline
        if datetime.datetime.now() > transaction['payment_deadline']:
            self._expire_transaction(transaction_id, 'payment_deadline_passed')
            return {'success': False, 'error': 'Payment deadline has passed'}
        
        try:
            # Create payment intent (hold funds, don't capture yet)
            payment_intent = stripe.PaymentIntent.create(
                amount=int(transaction['price'] * 100),
                currency='usd',
                payment_method=payment_method_id,
                confirmation_method='manual',
                confirm=True,
                capture_method='manual',  # Hold funds in escrow
                metadata={'transaction_id': transaction_id}
            )
            
            # Update transaction
            self.connection.execute("""
                UPDATE transactions SET 
                    payment_received = 1,
                    payment_received_time = CURRENT_TIMESTAMP,
                    payment_intent_id = ?
                WHERE transaction_id = ?
            """, (payment_intent.id, transaction_id))
            
            # Advance transaction state
            self._advance_transaction_state(transaction_id)
            
            return {'success': True, 'payment_intent_id': payment_intent.id}
            
        except stripe.error.StripeError as e:
            return {'success': False, 'error': f'Payment failed: {str(e)}'}
    
    def _advance_transaction_state(self, transaction_id):
        """
        Check transaction state and advance to next step
        """
        transaction = self._get_transaction(transaction_id)
        
        # Both ticket and payment received - forward ticket and hold funds
        if (transaction['ticket_email_received'] and 
            transaction['payment_received'] and 
            not transaction['ticket_forwarded']):
            
            self._forward_ticket_to_buyer(transaction_id)
            self._update_status(transaction_id, 'ticket_forwarded_funds_held')
            
            # Set release deadline (24 hours from now)
            release_deadline = datetime.datetime.now() + timedelta(hours=24)
            self.connection.execute("""
                UPDATE transactions SET release_deadline = ?
                WHERE transaction_id = ?
            """, (release_deadline, transaction_id))
            
            # Schedule automatic release
            self._schedule_payment_release(transaction_id, release_deadline)
        
        # Only ticket received - notify buyer to pay
        elif (transaction['ticket_email_received'] and 
              not transaction['payment_received']):
            
            self._update_status(transaction_id, 'waiting_for_payment')
            self._send_payment_reminder(transaction_id)
        
        self.connection.commit()
    
    def _forward_ticket_to_buyer(self, transaction_id):
        """
        Forward ticket email to buyer
        """
        transaction = self._get_transaction(transaction_id)
        ticket_data = json.loads(transaction['ticket_email_data'])
        
        # Forward the email
        success = forward_ticket_email(
            to_email=transaction['buyer_email'],
            original_email_data=ticket_data,
            transaction_id=transaction_id
        )
        
        if success:
            self.connection.execute("""
                UPDATE transactions SET 
                    ticket_forwarded = 1,
                    ticket_forwarded_time = CURRENT_TIMESTAMP
                WHERE transaction_id = ?
            """, (transaction_id,))
            
            # Notify both parties
            self._notify_ticket_forwarded(transaction_id)
    
    def confirm_buyer_receipt(self, transaction_id, buyer_email):
        """
        Buyer confirms they received valid tickets
        """
        transaction = self._get_transaction(transaction_id)
        
        if transaction['buyer_email'] != buyer_email:
            return {'success': False, 'error': 'Unauthorized'}
        
        if transaction['status'] != 'ticket_forwarded_funds_held':
            return {'success': False, 'error': 'Invalid transaction state'}
        
        # Mark confirmed and release funds immediately
        self.connection.execute("""
            UPDATE transactions SET 
                buyer_confirmed_receipt = 1,
                buyer_confirmation_time = CURRENT_TIMESTAMP
            WHERE transaction_id = ?
        """, (transaction_id,))
        
        self._release_funds_to_seller(transaction_id, 'buyer_confirmed')
        return {'success': True}
    
    def file_complaint(self, transaction_id, buyer_email, complaint_reason):
        """
        Buyer files complaint about tickets
        """
        transaction = self._get_transaction(transaction_id)
        
        if transaction['buyer_email'] != buyer_email:
            return {'success': False, 'error': 'Unauthorized'}
        
        if transaction['status'] not in ['ticket_forwarded_funds_held', 'completed']:
            return {'success': False, 'error': 'Cannot file complaint at this stage'}
        
        # Update status and hold funds
        self.connection.execute("""
            UPDATE transactions SET 
                status = 'complaint_filed',
                complaint_reason = ?
            WHERE transaction_id = ?
        """, (complaint_reason, transaction_id))
        
        # Notify admin for manual review
        self._notify_admin_complaint(transaction_id, complaint_reason)
        
        return {'success': True}
    
    def _release_funds_to_seller(self, transaction_id, reason):
        """
        Release held funds to seller
        """
        transaction = self._get_transaction(transaction_id)
        
        try:
            # Capture the held payment
            stripe.PaymentIntent.capture(transaction['payment_intent_id'])
            
            # Calculate seller amount (minus platform fee)
            platform_fee_rate = 0.05  # 5% platform fee
            seller_amount = transaction['price'] * (1 - platform_fee_rate)
            
            # Transfer to seller
            stripe.Transfer.create(
                amount=int(seller_amount * 100),
                currency='usd',
                destination=self._get_seller_stripe_id(transaction['seller_email']),
                transfer_group=str(transaction_id)
            )
            
            # Update transaction
            self.connection.execute("""
                UPDATE transactions SET 
                    funds_released = 1,
                    funds_released_time = CURRENT_TIMESTAMP,
                    status = 'completed'
                WHERE transaction_id = ?
            """, (transaction_id,))
            
            # Notify parties
            self._notify_funds_released(transaction_id, reason)
            
            print(f"✅ Funds released for transaction {transaction_id}: {reason}")
            
        except Exception as e:
            print(f"❌ Error releasing funds for transaction {transaction_id}: {e}")
    
    def _expire_transaction(self, transaction_id, reason):
        """
        Handle transaction expiration
        """
        transaction = self._get_transaction(transaction_id)
        
        if reason == 'ticket_deadline_passed':
            # No ticket received - just mark as expired
            self._update_status(transaction_id, 'expired_no_ticket')
            self._notify_transaction_expired(transaction_id, 'seller', 'ticket deadline')
            
        elif reason == 'payment_deadline_passed':
            # Ticket was sent but no payment - return ticket to seller
            if transaction['ticket_email_received']:
                self._return_ticket_to_seller(transaction_id)
                self._update_status(transaction_id, 'ticket_returned')
                self._notify_transaction_expired(transaction_id, 'buyer', 'payment deadline')
    
    def _return_ticket_to_seller(self, transaction_id):
        """
        Return ticket email back to seller
        """
        transaction = self._get_transaction(transaction_id)
        ticket_data = json.loads(transaction['ticket_email_data'])
        
        # Forward ticket back to seller
        forward_ticket_email(
            to_email=transaction['seller_email'],
            original_email_data=ticket_data,
            transaction_id=transaction_id,
            return_mode=True
        )
    
    def check_scheduled_deadlines(self):
        """
        Background job to check all deadlines and auto-release funds
        Called by scheduler every 5 minutes
        """
        now = datetime.datetime.now()
        
        # Check ticket deadlines
        expired_tickets = self.connection.execute("""
            SELECT transaction_id FROM transactions 
            WHERE status = 'waiting_for_ticket' 
            AND ticket_deadline < ?
        """, (now,)).fetchall()
        
        for row in expired_tickets:
            self._expire_transaction(row['transaction_id'], 'ticket_deadline_passed')
        
        # Check payment deadlines  
        expired_payments = self.connection.execute("""
            SELECT transaction_id FROM transactions 
            WHERE status = 'waiting_for_payment' 
            AND payment_deadline < ?
        """, (now,)).fetchall()
        
        for row in expired_payments:
            self._expire_transaction(row['transaction_id'], 'payment_deadline_passed')
        
        # Check fund release deadlines
        auto_releases = self.connection.execute("""
            SELECT transaction_id FROM transactions 
            WHERE status = 'ticket_forwarded_funds_held' 
            AND release_deadline < ?
            AND complaint_reason IS NULL
        """, (now,)).fetchall()
        
        for row in auto_releases:
            self._release_funds_to_seller(row['transaction_id'], 'automatic_24hr_release')
        
        self.connection.commit()
    
    # Helper methods
    def _get_transaction(self, transaction_id):
        """Get transaction details"""
        return self.connection.execute("""
            SELECT * FROM transactions WHERE transaction_id = ?
        """, (transaction_id,)).fetchone()
    
    def _update_status(self, transaction_id, new_status):
        """Update transaction status"""
        self.connection.execute("""
            UPDATE transactions SET status = ? WHERE transaction_id = ?
        """, (new_status, transaction_id))
    
    def _verify_ticket_authenticity(self, transaction_id, email_data):
        """Verify ticket email authenticity"""
        # Implementation from previous design
        score = 0
        
        # Domain verification
        trusted_domains = ['ticketmaster.com', 'stubhub.com', 'seatgeek.com']
        sender_domain = email_data['sender'].split('@')[-1]
        if sender_domain in trusted_domains:
            score += 40
        
        # Content analysis
        content = email_data['body'].lower()
        ticket_keywords = ['ticket', 'event', 'venue', 'seat', 'section', 'row', 'barcode']
        keyword_matches = sum(1 for word in ticket_keywords if word in content)
        score += min(keyword_matches * 5, 35)
        
        # Event matching
        transaction = self._get_transaction(transaction_id)
        event = self._get_event(transaction['event_id'])
        
        if event['name'].lower() in content:
            score += 15
        if event['location'].lower() in content:
            score += 10
        
        return {'score': score, 'is_valid': score >= 70}
    
    def _get_event(self, event_id):
        """Get event details"""
        return self.connection.execute("""
            SELECT * FROM events WHERE event_id = ?
        """, (event_id,)).fetchone()
    
    def _get_or_create_event(self, event_details):
        """Get or create event entry"""
        existing = self.connection.execute("""
            SELECT event_id FROM events 
            WHERE name = ? AND location = ? AND event_datetime = ?
        """, (event_details['name'], event_details['location'], event_details['datetime'])).fetchone()
        
        if existing:
            return existing['event_id']
        
        cursor = self.connection.execute("""
            INSERT INTO events (name, location, event_datetime)
            VALUES (?, ?, ?)
        """, (event_details['name'], event_details['location'], event_details['datetime']))
        
        return cursor.lastrowid
    
    # Notification methods (basic implementations)
    def _notify_ticket_forwarded(self, transaction_id):
        """Notify both parties that ticket was forwarded"""
        print(f"📧 Ticket forwarded for transaction {transaction_id}")
    
    def _notify_funds_released(self, transaction_id, reason):
        """Notify both parties that funds were released"""
        print(f"💰 Funds released for transaction {transaction_id}: {reason}")
    
    def _notify_transaction_expired(self, transaction_id, responsible_party, deadline_type):
        """Notify about transaction expiration"""
        print(f"⏰ Transaction {transaction_id} expired: {deadline_type}")
    
    def _notify_admin_complaint(self, transaction_id, complaint_reason):
        """Notify admin about complaint"""
        print(f"🚨 Complaint filed for transaction {transaction_id}: {complaint_reason}")
    
    def _send_payment_reminder(self, transaction_id):
        """Send payment reminder to buyer"""
        print(f"📧 Payment reminder sent for transaction {transaction_id}")
    
    def _schedule_deadline_check(self, transaction_id, check_type, deadline):
        """Schedule background job for deadline checking"""
        print(f"⏰ Scheduled {check_type} deadline check for transaction {transaction_id}")
    
    def _schedule_payment_release(self, transaction_id, release_time):
        """Schedule automatic payment release"""
        print(f"⏰ Scheduled payment release for transaction {transaction_id} at {release_time}")
    
    def _get_seller_stripe_id(self, seller_email):
        """Get seller's Stripe account ID"""
        result = self.connection.execute("""
            SELECT stripe_id FROM users WHERE email = ?
        """, (seller_email,)).fetchone()
        return result['stripe_id'] if result else None
    
    def _flag_suspicious_ticket(self, transaction_id, verification_result):
        """Flag transaction for manual review"""
        self.connection.execute("""
            UPDATE transactions SET 
                status = 'requires_manual_review',
                ticket_verification_score = ?
            WHERE transaction_id = ?
        """, (verification_result['score'], transaction_id))
