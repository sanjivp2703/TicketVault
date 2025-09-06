"""
Mailgun Setup Script for Safe Transaction
This script will configure Mailgun integration and test email sending
"""

import requests
import json
import os
from mailgun_config import get_mailgun_config

def test_mailgun_connection(config):
    """Test Mailgun API connection"""
    print("🔍 Testing Mailgun connection...")
    
    url = f"{config['base_url']}/messages"
    
    # Test email
    data = {
        'from': f'Safe Transaction <noreply@{config["domain"]}>',
        'to': config['authorized_recipients'][0] if config['authorized_recipients'] else 'test@example.com',
        'subject': '🚀 Mailgun Test - Safe Transaction Setup',
        'html': '''
        <h2>✅ Mailgun Integration Successful!</h2>
        <p>Your Safe Transaction platform is now connected to Mailgun.</p>
        <p><strong>Next steps:</strong></p>
        <ul>
            <li>Set up webhooks for incoming emails</li>
            <li>Configure your domain DNS (if using custom domain)</li>
            <li>Test the complete transaction flow</li>
        </ul>
        <p>🎉 You're ready to process automated ticket transactions!</p>
        '''
    }
    
    try:
        response = requests.post(
            url,
            auth=('api', config['api_key']),
            data=data,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ SUCCESS: Mailgun connection working!")
            print(f"📧 Test email sent to: {data['to']}")
            return True
        else:
            print(f"❌ ERROR: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ CONNECTION ERROR: {e}")
        return False

def setup_webhook(config):
    """Set up Mailgun webhook for incoming emails"""
    print("🔗 Setting up Mailgun webhook...")
    
    # For now, we'll show instructions since we need ngrok or a public URL
    print("""
    📋 WEBHOOK SETUP INSTRUCTIONS:
    
    1. Install ngrok (for local testing):
       Download from: https://ngrok.com/download
       
    2. Run your Flask app:
       flask --app insta485 run --port 8000
       
    3. In another terminal, run ngrok:
       ngrok http 8000
       
    4. Copy the ngrok URL (like: https://abc123.ngrok.io)
    
    5. In Mailgun dashboard:
       - Go to Sending → Webhooks
       - Add webhook URL: https://abc123.ngrok.io/webhook/mailgun
       - Select events: "Incoming Messages"
    
    6. Test by sending email to: tx-000001@{domain}
    """.format(domain=config['domain']))

def update_flask_config(config):
    """Update Flask app configuration"""
    print("⚙️  Updating Flask configuration...")
    
    # Create environment file
    env_content = f"""
# Mailgun Configuration
MAILGUN_DOMAIN={config['domain']}
MAILGUN_API_KEY={config['api_key']}
MAILGUN_BASE_URL={config['base_url']}

# Flask Mail Configuration
MAIL_SERVER=smtp.mailgun.org
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=postmaster@{config['domain']}
MAIL_PASSWORD={config['api_key']}
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Created .env file with Mailgun configuration")
    print("📝 Add this to your Flask app initialization:")
    print("""
    # In insta485/__init__.py, add:
    from flask_mail import Mail
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    app.config['MAILGUN_DOMAIN'] = os.getenv('MAILGUN_DOMAIN')
    app.config['MAILGUN_API_KEY'] = os.getenv('MAILGUN_API_KEY')
    """)

def main():
    print("🚀 SAFE TRANSACTION - MAILGUN SETUP")
    print("=" * 50)
    
    # Get configuration
    print("📋 Choose setup option:")
    print("1. Sandbox Domain (Quick testing)")
    print("2. Custom Domain (Production)")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        config = get_mailgun_config(use_sandbox=True)
        print(f"🧪 Using sandbox domain: {config['domain']}")
    elif choice == "2":
        config = get_mailgun_config(use_sandbox=False)
        print(f"🌐 Using custom domain: {config['domain']}")
    else:
        print("❌ Invalid choice")
        return
    
    # Validate configuration
    if config['api_key'] == 'your-private-api-key-here':
        print("❌ ERROR: Please update mailgun_config.py with your actual API key!")
        print("📝 Go to Mailgun dashboard → Settings → API Keys")
        return
    
    if 'sandbox123abc' in config['domain']:
        print("❌ ERROR: Please update mailgun_config.py with your actual sandbox domain!")
        print("📝 Go to Mailgun dashboard → Sending → Domains")
        return
    
    # Test connection
    if test_mailgun_connection(config):
        print()
        setup_webhook(config)
        print()
        update_flask_config(config)
        
        print("\n🎉 SETUP COMPLETE!")
        print("✅ Mailgun is configured and working")
        print("📧 Check your email for the test message")
        print("🔗 Follow webhook instructions to complete setup")
        
    else:
        print("\n❌ SETUP FAILED")
        print("🔍 Check your API key and domain configuration")

if __name__ == "__main__":
    main()
