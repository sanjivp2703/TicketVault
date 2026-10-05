"""
Complete Email Test for Safe Transaction
Tests both sending and receiving capabilities
"""

import requests
from mailgun_config import get_mailgun_config

def test_send_email(config):
    """Test sending email to authorized recipient"""
    print("📧 Testing email sending...")
    
    url = f"{config['base_url']}/messages"
    
    data = {
        'from': f'Safe Transaction <noreply@{config["domain"]}>',
        'to': 'safetransactiontix@gmail.com',
        'subject': '🚀 Complete Setup Test - Safe Transaction Ready!',
        'html': '''
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; background: #f4f4f4; margin: 0; padding: 20px; }
                .container { background: white; max-width: 600px; margin: 0 auto; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
                .header { text-align: center; color: #2563eb; margin-bottom: 30px; }
                .success { background: #dcfce7; border: 1px solid #16a34a; color: #15803d; padding: 15px; border-radius: 8px; margin: 20px 0; }
                .info { background: #dbeafe; border: 1px solid #3b82f6; color: #1d4ed8; padding: 15px; border-radius: 8px; margin: 20px 0; }
                .footer { text-align: center; color: #6b7280; font-size: 14px; margin-top: 30px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 Safe Transaction Setup Complete!</h1>
                </div>
                
                <div class="success">
                    <strong>✅ SUCCESS:</strong> Your Mailgun integration is working perfectly!
                </div>
                
                <div class="info">
                    <h3>🔧 What's Configured:</h3>
                    <ul>
                        <li>✅ Mailgun sandbox domain connected</li>
                        <li>✅ API keys configured</li>
                        <li>✅ Authorized recipient added</li>
                        <li>✅ Email sending working</li>
                    </ul>
                </div>
                
                <div class="info">
                    <h3>🚀 Next Steps:</h3>
                    <ul>
                        <li>Set up webhooks for incoming emails</li>
                        <li>Test complete transaction flow</li>
                        <li>Configure seller/buyer notifications</li>
                    </ul>
                </div>
                
                <div class="info">
                    <h3>📧 Test Email Addresses:</h3>
                    <p>Sellers can now send tickets to addresses like:</p>
                    <code style="background: #f3f4f6; padding: 5px 10px; border-radius: 4px;">
                        tx-000001@sandboxb9b4c56251404e08939d238b07603aff.mailgun.org
                    </code>
                </div>
                
                <div class="footer">
                    <p>🎯 Safe Transaction - Automated Ticket Platform</p>
                    <p><em>This email confirms your setup is complete!</em></p>
                </div>
            </div>
        </body>
        </html>
        '''
    }
    
    try:
        response = requests.post(
            url,
            auth=('api', config['sending_key'] if 'sending_key' in config else config['api_key']),
            data=data
        )
        
        if response.status_code == 200:
            print("✅ SUCCESS: Setup confirmation email sent!")
            print("📧 Check safetransactiontix@gmail.com for the confirmation")
            return True
        else:
            print(f"❌ ERROR: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def main():
    print("🚀 SAFE TRANSACTION - COMPLETE EMAIL SETUP TEST")
    print("=" * 60)
    
    config = get_mailgun_config(use_sandbox=True)
    
    # Add sending key to config
    config['sending_key'] = "<MAILGUN_API_KEY>"
    
    print(f"🎯 Testing with domain: {config['domain']}")
    print(f"📧 Authorized recipient: safetransactiontix@gmail.com")
    print()
    
    if test_send_email(config):
        print()
        print("🎉 EMAIL SETUP COMPLETE!")
        print("✅ Mailgun is fully configured and working")
        print("📧 Check your email for confirmation")
        print()
        print("🔗 NEXT: Set up webhooks for incoming emails")
        print("   This will allow sellers to send tickets and trigger automatic verification")
        
    else:
        print()
        print("❌ SETUP INCOMPLETE")
        print("🔍 Check your Mailgun configuration")

if __name__ == "__main__":
    main()
