"""
Complete System Test for Safe Transaction
Tests the entire flow with real email notifications
"""

import requests
import json
import time

def test_complete_transaction_flow():
    """Test complete transaction flow with notifications"""
    print("🚀 TESTING COMPLETE TRANSACTION FLOW")
    print("=" * 60)
    
    # Step 1: Create a new transaction via web interface
    print("📝 Step 1: Creating new transaction...")
    
    # First, let's create a transaction using the API
    create_url = "http://localhost:8000/create-transaction"
    
    create_data = {
        'event_name': 'Email Test Concert',
        'event_location': 'Test Venue',
        'event_datetime': '2025-12-20T20:00',
        'price': '75.50',
        'buyer_email': 'safetransactiontix@gmail.com',  # Your authorized email
        'seller_email': 'admin@gmail.com'  # This should be in your system
    }
    
    try:
        # Create transaction
        print("🔄 Sending transaction creation request...")
        response = requests.post(create_url, data=create_data, timeout=15)
        
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                if result.get('success'):
                    transaction_id = result['transaction_id']
                    ticket_email = result['ticket_email']
                    
                    print(f"✅ Transaction created successfully!")
                    print(f"🆔 Transaction ID: {transaction_id}")
                    print(f"📧 Ticket email: {ticket_email}")
                    
                    # Wait a moment for seller instructions email
                    print("\n⏳ Waiting 3 seconds for seller instructions email...")
                    time.sleep(3)
                    
                    # Step 2: Test verification (simulates ticket received)
                    print(f"\n🔍 Step 2: Testing ticket verification...")
                    
                    verify_url = "http://localhost:8000/api/test-verify"
                    verify_data = {
                        'transaction_id': transaction_id,
                        'test_mode': True
                    }
                    
                    verify_response = requests.post(
                        verify_url,
                        headers={'Content-Type': 'application/json'},
                        data=json.dumps(verify_data),
                        timeout=15
                    )
                    
                    print(f"📊 Verification response: {verify_response.status_code}")
                    
                    if verify_response.status_code == 200:
                        print("✅ Verification successful!")
                        
                        # Wait for emails to be sent
                        print("\n⏳ Waiting 5 seconds for notification emails...")
                        time.sleep(5)
                        
                        print("\n🎉 COMPLETE FLOW TEST FINISHED!")
                        print("=" * 60)
                        print("📧 CHECK YOUR EMAILS:")
                        print("1. admin@gmail.com should have received:")
                        print("   - 📧 Seller instructions (when listing created)")
                        print("   - 📧 Verification success notification")
                        print()
                        print("2. safetransactiontix@gmail.com should have received:")
                        print("   - 📧 Buyer payment notification with payment link")
                        print("=" * 60)
                        
                        return True
                    else:
                        print(f"❌ Verification failed: {verify_response.status_code}")
                        if verify_response.text:
                            print(f"Response: {verify_response.text}")
                        return False
                else:
                    print(f"❌ Transaction creation failed: {result}")
                    return False
            except json.JSONDecodeError:
                print(f"❌ Invalid JSON response: {response.text[:200]}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    print("🎯 SAFE TRANSACTION - COMPLETE SYSTEM TEST")
    print("🔧 Testing transaction creation + verification + notifications")
    print("=" * 80)
    
    success = test_complete_transaction_flow()
    
    print("\n" + "=" * 80)
    if success:
        print("🎉 SYSTEM TEST COMPLETED!")
        print("📧 Check both email addresses for notifications")
        print("🚀 If emails arrived, the system is working perfectly!")
    else:
        print("❌ SYSTEM TEST FAILED")
        print("🔍 Check Flask server logs for errors")
    
    print("\n📧 EMAIL ROUTING SUMMARY:")
    print("• Seller emails → admin@gmail.com")
    print("• Buyer emails → safetransactiontix@gmail.com") 
    print("• Ticket emails → tx-XXXXXX@sandboxb9b4c56251404e08939d238b07603aff.mailgun.org")

if __name__ == "__main__":
    main()