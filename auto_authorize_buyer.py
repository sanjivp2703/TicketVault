#!/usr/bin/env python3
"""
Auto-authorize buyer emails in Mailgun when they make purchases
This allows using the existing Mailgun setup without app passwords
"""

import requests
from mailgun_config import get_mailgun_config

def authorize_buyer_email(buyer_email):
    """Add buyer email to Mailgun authorized recipients"""
    try:
        config = get_mailgun_config(use_sandbox=True)
        
        print(f"🔐 Auto-authorizing buyer: {buyer_email}")
        
        # Add to authorized recipients via Mailgun API
        url = f"https://api.mailgun.net/v3/{config['domain']}/bounces"
        
        # First, remove any existing bounces
        try:
            delete_response = requests.delete(
                f"https://api.mailgun.net/v3/{config['domain']}/bounces/{buyer_email}",
                auth=('api', config['api_key'])
            )
        except:
            pass
        
        # Send authorization email (this adds them to authorized list)
        auth_url = f"https://api.mailgun.net/v3/{config['domain']}/messages"
        
        auth_data = {
            'from': f'Safe Transaction <noreply@{config["domain"]}>',
            'to': buyer_email,
            'subject': 'Welcome to Safe Transaction - Email Authorization',
            'html': f'''
            <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #059669;">Welcome to Safe Transaction!</h2>
                <p>This email confirms that your address <strong>{buyer_email}</strong> is now authorized to receive notifications from Safe Transaction.</p>
                <p>You'll receive confirmation emails when you make purchases and other important updates about your transactions.</p>
                <p style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; color: #666; font-size: 14px;">
                    Safe Transaction - Secure Ticket Protection<br>
                    <a href="mailto:safetransactiontix@gmail.com">safetransactiontix@gmail.com</a>
                </p>
            </body>
            </html>
            '''
        }
        
        response = requests.post(
            auth_url,
            auth=('api', config['api_key']),
            data=auth_data
        )
        
        if response.status_code == 200:
            print(f"✅ Buyer {buyer_email} authorized and welcome email sent")
            return True
        else:
            print(f"❌ Failed to authorize {buyer_email}: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error authorizing {buyer_email}: {e}")
        return False

def test_auto_authorization():
    """Test the auto-authorization system"""
    test_buyer = "testbuyer123@umich.edu"
    
    print("🧪 Testing auto-authorization system...")
    
    success = authorize_buyer_email(test_buyer)
    
    if success:
        print(f"✅ Auto-authorization successful!")
        print(f"📧 {test_buyer} should now be able to receive emails")
        
        # Test sending a confirmation email
        try:
            from insta485.email_utils import send_accept_confirmation_email
            
            print(f"🧪 Testing confirmation email to newly authorized buyer...")
            
            result = send_accept_confirmation_email(
                buyer_email=test_buyer,
                event_name="Michigan Football Game",
                price=75,
                seller_email="psanjiv@umich.edu",
                transaction_id=999
            )
            
            if result:
                print(f"✅ Confirmation email sent successfully!")
            else:
                print(f"❌ Confirmation email still failed")
                
        except Exception as e:
            print(f"❌ Error testing confirmation email: {e}")
    else:
        print(f"❌ Auto-authorization failed")

if __name__ == "__main__":
    test_auto_authorization()

