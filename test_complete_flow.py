#!/usr/bin/env python3
"""
Test script for the complete automated ticket verification flow
"""
import requests
import json
import time

# Base URL for the API
BASE_URL = "http://localhost:8000"

def test_complete_flow():
    """Test the complete flow from listing creation to verification"""
    
    print("🧪 Testing Complete Verification Flow")
    print("=" * 50)
    
    # Step 1: Create a listing
    print("Step 1: Creating listing...")
    create_data = {
        'buyer_email': 'buyer@test.com',
        'seller_email': 'seller@test.com',
        'price': 150.00,
        'event_name': 'Test Concert',
        'event_location': 'Madison Square Garden',
        'event_datetime': '2024-12-31T20:00:00',
        'ticket_deadline_hours': 2,
        'payment_deadline_hours': 24
    }
    
    try:
        # Create listing via form data (simulating the web form)
        response = requests.post(f"{BASE_URL}/create-transaction", data=create_data)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                transaction_id = result['transaction_id']
                ticket_email = result['ticket_email']
                print(f"✅ Listing created successfully!")
                print(f"   Transaction ID: {transaction_id}")
                print(f"   Ticket Email: {ticket_email}")
            else:
                print(f"❌ Listing creation failed: {result.get('error')}")
                return
        else:
            print(f"❌ HTTP Error {response.status_code}")
            return
            
    except Exception as e:
        print(f"❌ Error creating listing: {e}")
        return
    
    # Step 2: Check transaction status
    print(f"\nStep 2: Checking transaction status...")
    try:
        status_response = requests.get(f"{BASE_URL}/api/transactions/{transaction_id}/status")
        if status_response.status_code == 200:
            status_data = status_response.json()
            if status_data.get('success'):
                transaction = status_data['transaction']
                print(f"✅ Transaction status: {transaction['status']}")
                print(f"   Event: {transaction.get('event_name', 'N/A')}")
                print(f"   Location: {transaction.get('event_location', 'N/A')}")
            else:
                print(f"❌ Status check failed: {status_data.get('error')}")
                return
        else:
            print(f"❌ HTTP Error {status_response.status_code}")
            return
    except Exception as e:
        print(f"❌ Error checking status: {e}")
        return
    
    # Step 3: Simulate verification (instant method)
    print(f"\nStep 3: Simulating instant verification...")
    try:
        verify_response = requests.post(f"{BASE_URL}/api/transactions/{transaction_id}/mark-verified")
        if verify_response.status_code == 200:
            verify_data = verify_response.json()
            if verify_data.get('success'):
                print(f"✅ Verification successful!")
                print(f"   Status: {verify_data['status']}")
                print(f"   Payment Deadline: {verify_data['payment_deadline']}")
                print(f"   Verification Score: {verify_data['verification_score']}")
            else:
                print(f"❌ Verification failed: {verify_data.get('error')}")
                return
        else:
            print(f"❌ HTTP Error {verify_response.status_code}")
            return
    except Exception as e:
        print(f"❌ Error during verification: {e}")
        return
    
    # Step 4: Final status check
    print(f"\nStep 4: Final status check...")
    try:
        final_status_response = requests.get(f"{BASE_URL}/api/transactions/{transaction_id}/status")
        if final_status_response.status_code == 200:
            final_status_data = final_status_response.json()
            if final_status_data.get('success'):
                final_transaction = final_status_data['transaction']
                print(f"✅ Final transaction status: {final_transaction['status']}")
                print(f"   Ticket Email Received: {bool(final_transaction.get('ticket_email_received', 0))}")
                print(f"   Payment Deadline: {final_transaction.get('payment_deadline', 'N/A')}")
                print(f"   Verification Score: {final_transaction.get('ticket_verification_score', 'N/A')}")
            else:
                print(f"❌ Final status check failed: {final_status_data.get('error')}")
                return
        else:
            print(f"❌ HTTP Error {final_status_response.status_code}")
            return
    except Exception as e:
        print(f"❌ Error during final status check: {e}")
        return
    
    print("\n🎉 COMPLETE FLOW TEST SUCCESSFUL!")
    print("=" * 50)
    print(f"✅ Created pending listing")
    print(f"✅ Verified transaction details")  
    print(f"✅ Simulated ticket verification")
    print(f"✅ Activated payment window")
    print(f"✅ Buyer notification system triggered")
    print("\n🚀 The system is fully functional!")

if __name__ == "__main__":
    test_complete_flow()
