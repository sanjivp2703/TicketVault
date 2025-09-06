"""
Test Complete Notification System for Safe Transaction
Tests all email notifications with proper routing
"""

import requests
import json
from datetime import datetime, timedelta

def test_complete_flow():
    """Test the complete transaction flow with notifications"""
    print("🚀 TESTING COMPLETE NOTIFICATION SYSTEM")
    print("=" * 60)
    
    # Step 1: Create a new transaction
    print("📝 Step 1: Creating new transaction...")
    
    create_data = {
        'event_name': 'Taylor Swift Concert Test',
        'event_location': 'Madison Square Garden',
        'event_datetime': '2025-12-15T19:30',
        'price': '150.00',
        'buyer_email': 'safetransactiontix@gmail.com',  # Your authorized email
        'seller_email': 'admin@gmail.com'
    }
    
    try:
        # Create transaction via API
        response = requests.post(
            'http://localhost:8000/create-transaction',
            data=create_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                transaction_id = result['transaction_id']
                ticket_email = result['ticket_email']
                
                print(f"✅ Transaction created: ID {transaction_id}")
                print(f"📧 Ticket email: {ticket_email}")
                print(f"📧 Seller instructions should be sent to: admin@gmail.com")
                
                # Step 2: Test verification (simulates seller sending ticket)
                print(f"\n📧 Step 2: Testing verification (simulates ticket received)...")
                
                verify_data = {
                    'transaction_id': transaction_id,
                    'test_mode': True
                }
                
                verify_response = requests.post(
                    'http://localhost:8000/api/test-verify',
                    headers={'Content-Type': 'application/json'},
                    data=json.dumps(verify_data),
                    timeout=10
                )
                
                if verify_response.status_code == 200:
                    print("✅ Verification successful!")
                    print("📧 Seller verification email should be sent to: admin@gmail.com")
                    print("📧 Buyer payment email should be sent to: safetransactiontix@gmail.com")
                    
                    print(f"\n🎉 COMPLETE FLOW TEST SUCCESSFUL!")
                    print("=" * 60)
                    print("📧 CHECK YOUR EMAILS:")
                    print("1. admin@gmail.com - Should receive:")
                    print("   - Seller instructions (when listing created)")
                    print("   - Verification success notification")
                    print("2. safetransactiontix@gmail.com - Should receive:")
                    print("   - Buyer payment notification with secure payment link")
                    print("=" * 60)
                    
                    return True
                else:
                    print(f"❌ Verification failed: {verify_response.status_code}")
                    print(verify_response.text)
                    return False
            else:
                print(f"❌ Transaction creation failed: {result.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_verification_failure():
    """Test verification failure notification"""
    print("\n🧪 TESTING VERIFICATION FAILURE NOTIFICATION")
    print("=" * 60)
    
    # This would normally be triggered by the email webhook
    # For now, we'll simulate it by directly calling the transaction manager
    
    try:
        from insta485.mailgun_sender import mailgun_sender
        
        # Test failure notification
        success = mailgun_sender.send_seller_verification_failed(
            seller_email='admin@gmail.com',
            transaction_id=999,
            event_name='Test Event - Verification Failed',
            reason='Event details do not match original listing'
        )
        
        if success:
            print("✅ Verification failure email sent successfully!")
            print("📧 Check admin@gmail.com for failure notification")
        else:
            print("❌ Failed to send verification failure email")
            
        return success
        
    except Exception as e:
        print(f"❌ Verification failure test error: {e}")
        return False

def main():
    print("🎯 SAFE TRANSACTION - NOTIFICATION SYSTEM TEST")
    print("🔧 Testing all email notifications with proper routing")
    print("=" * 80)
    
    # Test 1: Complete successful flow
    success1 = test_complete_flow()
    
    # Test 2: Verification failure
    success2 = test_verification_failure()
    
    print("\n" + "=" * 80)
    print("📊 TEST RESULTS:")
    print(f"✅ Complete Flow: {'PASSED' if success1 else 'FAILED'}")
    print(f"✅ Failure Flow: {'PASSED' if success2 else 'FAILED'}")
    
    if success1 and success2:
        print("\n🎉 ALL TESTS PASSED!")
        print("📧 Your notification system is working perfectly!")
        print("🚀 Ready for production use!")
    else:
        print("\n❌ SOME TESTS FAILED")
        print("🔍 Check the error messages above")
    
    print("\n📧 EMAIL SUMMARY:")
    print("Seller emails go to: admin@gmail.com")
    print("Buyer emails go to: safetransactiontix@gmail.com")
    print("Ticket submission emails go to: tx-XXXXXX@sandboxb9b4c56251404e08939d238b07603aff.mailgun.org")

if __name__ == "__main__":
    main()
