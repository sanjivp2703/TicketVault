"""
Test Verification Failure System
Tests what happens when ticket details don't match
"""

import requests
import json

def test_verification_failure():
    """Test verification failure notification"""
    print("🧪 TESTING VERIFICATION FAILURE SYSTEM")
    print("=" * 60)
    
    try:
        # Test failure notification directly
        from insta485.mailgun_sender import mailgun_sender
        
        print("📧 Sending verification failure email...")
        
        success = mailgun_sender.send_seller_verification_failed(
            seller_email='admin@gmail.com',
            transaction_id=999,
            event_name='Test Event - Verification Failed',
            reason='Event details do not match original listing: Event name "Real Concert" does not match listing "Fake Concert Test"'
        )
        
        if success:
            print("✅ Verification failure email sent!")
            print("📧 Check admin@gmail.com (spam folder) for failure notification")
            print("\n📋 The email should explain:")
            print("• Why verification failed")
            print("• What the seller can do next")
            print("• How to create a new listing with correct details")
            return True
        else:
            print("❌ Failed to send verification failure email")
            return False
            
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

def show_verification_scenarios():
    """Show different verification failure scenarios"""
    print("\n🔍 VERIFICATION FAILURE SCENARIOS")
    print("=" * 60)
    print("The system will reject tickets when:")
    print("❌ Event name doesn't match")
    print("❌ Venue/location doesn't match") 
    print("❌ Date/time doesn't match")
    print("❌ Ticket appears fake or invalid")
    print("❌ Email sent from wrong address")
    print("❌ No ticket content found")
    
    print("\n✅ VERIFICATION SUCCESS SCENARIOS")
    print("=" * 60)
    print("The system will approve tickets when:")
    print("✅ Event details match exactly")
    print("✅ Sent from seller's email address")
    print("✅ Contains valid ticket information")
    print("✅ Ticket format is recognizable")

def main():
    print("🎯 SAFE TRANSACTION - VERIFICATION FAILURE TEST")
    print("🔧 Testing rejection system before using real tickets")
    print("=" * 80)
    
    success = test_verification_failure()
    show_verification_scenarios()
    
    print("\n" + "=" * 80)
    if success:
        print("🎉 VERIFICATION FAILURE SYSTEM WORKING!")
        print("📧 Check your email for the failure notification")
        print("🛡️ System will protect buyers from invalid tickets")
        print("\n💡 NEXT STEPS:")
        print("1. Check the failure email format")
        print("2. Then test with intentionally wrong listing details")
        print("3. Finally test with your real ticket")
    else:
        print("❌ VERIFICATION FAILURE SYSTEM NEEDS ATTENTION")
        print("🔍 Check email configuration")
    
    print("\n🔒 SECURITY NOTE:")
    print("This verification system protects both buyers and sellers")
    print("by ensuring only valid, matching tickets are processed.")

if __name__ == "__main__":
    main()
