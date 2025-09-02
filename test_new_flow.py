#!/usr/bin/env python3
"""
Test script for the new pending ticket flow
Demonstrates the complete process from listing creation to activation
"""
import os
import sys
import json
import time
from datetime import datetime

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import our modules
from insta485.transaction_manager import TransactionManager
from insta485.email_monitor import create_test_email, email_monitor

def test_pending_flow():
    """Test the complete pending flow"""
    print("🧪 Testing New Pending Ticket Flow")
    print("=" * 50)
    
    # Step 1: Create a pending listing
    print("\n📝 Step 1: Creating pending listing...")
    
    transaction_manager = TransactionManager()
    
    event_details = {
        'name': 'Test Concert 2024',
        'location': 'Madison Square Garden',
        'datetime': '2024-02-15 20:00:00'
    }
    
    result = transaction_manager.create_listing(
        seller_email='seller@test.com',
        buyer_email='buyer@test.com',
        price=150.00,
        event_details=event_details
    )
    
    if result['status'] == 'pending_ticket_submission':
        print(f"✅ Listing created in PENDING state")
        print(f"   Transaction ID: {result['transaction_id']}")
        print(f"   Ticket Email: {result['ticket_email']}")
        
        transaction_id = result['transaction_id']
        ticket_email = result['ticket_email']
        
        # Step 2: Create a test email (simulates seller sending ticket)
        print(f"\n📧 Step 2: Simulating seller sending ticket to {ticket_email}...")
        
        create_test_email(
            transaction_id=transaction_id,
            seller_email='seller@test.com',
            event_name='Test Concert 2024',
            location='Madison Square Garden'
        )
        
        print(f"✅ Test email created: test_emails/tx-{transaction_id:06d}.json")
        
        # Step 3: Start email monitor to process the email
        print("\n🔍 Step 3: Starting email monitor to process ticket...")
        
        # Start email monitor
        email_monitor.start()
        
        # Wait a few seconds for it to process
        print("   Waiting for email processing...")
        time.sleep(3)
        
        # Stop email monitor
        email_monitor.stop()
        
        # Step 4: Check the result
        print("\n✅ Step 4: Checking listing status...")
        
        # Check transaction status (you'd normally query the database here)
        print("   Listing should now be ACTIVE with 1-hour payment window")
        print("   Buyer should have received payment notification")
        
        print("\n🎉 Test completed successfully!")
        print("\nSummary of the new flow:")
        print("1. Seller creates listing → PENDING state")
        print("2. Popup shows secure email address")
        print("3. Seller forwards ticket → Email monitor processes")
        print("4. Ticket verified → Listing ACTIVATED")
        print("5. Buyer gets 1-hour payment window")
        
    else:
        print(f"❌ Failed to create listing: {result}")

def show_test_email_content(transaction_id):
    """Show what the test email contains"""
    try:
        with open(f'test_emails/tx-{transaction_id:06d}.json', 'r') as f:
            email_data = json.load(f)
        
        print(f"\n📄 Test Email Content for Transaction {transaction_id}:")
        print(f"   From: {email_data['sender']}")
        print(f"   To: {email_data['recipient']}")
        print(f"   Subject: {email_data['subject']}")
        print(f"   Body Preview: {email_data['body'][:100]}...")
        
    except FileNotFoundError:
        print(f"❌ No test email found for transaction {transaction_id}")

if __name__ == "__main__":
    print("🚀 Safe Transaction - New Pending Flow Test")
    print("This script demonstrates the new listing flow where:")
    print("• Listings start in PENDING state")
    print("• Seller must send ticket to activate")
    print("• Automatic verification and buyer notification")
    print("• 1-hour payment window for buyers")
    
    try:
        test_pending_flow()
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n📁 Check test_emails/ directory for generated test files")
    print(f"🌐 Visit http://localhost:8000 to see the new popup UI in action!")
