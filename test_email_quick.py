"""
Quick Email Test for Safe Transaction
Tests if Mailgun integration is working
"""

import requests

def test_mailgun_direct():
    """Test Mailgun API directly"""
    print("📧 Testing Mailgun API directly...")
    
    url = "https://api.mailgun.net/v3/sandboxb9b4c56251404e08939d238b07603aff.mailgun.org/messages"
    
    data = {
        'from': 'Safe Transaction <noreply@sandboxb9b4c56251404e08939d238b07603aff.mailgun.org>',
        'to': 'safetransactiontix@gmail.com',
        'subject': '🧪 Direct Mailgun Test - Safe Transaction',
        'html': '''
        <h2>✅ Mailgun Direct Test Successful!</h2>
        <p>This email was sent directly via Mailgun API to test the integration.</p>
        <p><strong>If you receive this, Mailgun is working correctly!</strong></p>
        <p>🎉 Ready to test the complete notification system!</p>
        '''
    }
    
    try:
        response = requests.post(
            url,
            auth=('api', 'd3fac427288306d90280459b2faddb07-1ae02a08-43aa9974'),
            data=data,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ SUCCESS: Direct Mailgun test email sent!")
            print("📧 Check safetransactiontix@gmail.com for the test email")
            return True
        else:
            print(f"❌ ERROR: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    print("🚀 QUICK EMAIL TEST")
    print("=" * 40)
    
    if test_mailgun_direct():
        print("\n🎉 EMAIL SYSTEM WORKING!")
        print("📧 Check your email and then we can test the full system")
    else:
        print("\n❌ EMAIL SYSTEM FAILED")
        print("🔍 Check Mailgun configuration")
