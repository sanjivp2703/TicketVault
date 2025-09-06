#!/usr/bin/env python3
"""
Email Service Setup Helper for Safe Transaction
Helps configure Mailgun or SendGrid for automated email processing
"""

import os
import requests
import json
from datetime import datetime

class EmailServiceSetup:
    """Helper class to set up email services"""
    
    def __init__(self):
        self.domain = "safetransaction.com"  # Change this to your domain
        
    def setup_mailgun(self, api_key, webhook_url):
        """
        Set up Mailgun for email processing
        
        Args:
            api_key: Your Mailgun API key
            webhook_url: Your webhook URL (e.g., https://yourdomain.com/webhook/mailgun)
        """
        print("🚀 Setting up Mailgun integration...")
        
        # Configure webhook for incoming emails
        webhook_response = requests.post(
            f"https://api.mailgun.net/v3/domains/{self.domain}/webhooks",
            auth=("api", api_key),
            data={
                "id": "delivered",
                "url": webhook_url
            }
        )
        
        if webhook_response.status_code == 200:
            print("✅ Mailgun webhook configured successfully")
        else:
            print(f"❌ Mailgun webhook setup failed: {webhook_response.text}")
            
        # Test the configuration
        self.test_mailgun_config(api_key)
        
    def test_mailgun_config(self, api_key):
        """Test Mailgun configuration"""
        print("🧪 Testing Mailgun configuration...")
        
        # Send a test email to verify setup
        test_response = requests.post(
            f"https://api.mailgun.net/v3/{self.domain}/messages",
            auth=("api", api_key),
            data={
                "from": f"test@{self.domain}",
                "to": f"tx-000001@{self.domain}",
                "subject": "Test Email - Safe Transaction Setup",
                "text": "This is a test email to verify Mailgun integration."
            }
        )
        
        if test_response.status_code == 200:
            print("✅ Mailgun test email sent successfully")
            print("📧 Check your webhook endpoint for incoming test email")
        else:
            print(f"❌ Mailgun test failed: {test_response.text}")
    
    def setup_sendgrid(self, api_key, webhook_url):
        """
        Set up SendGrid Inbound Parse
        
        Args:
            api_key: Your SendGrid API key  
            webhook_url: Your webhook URL (e.g., https://yourdomain.com/webhook/sendgrid)
        """
        print("🚀 Setting up SendGrid integration...")
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Configure inbound parse webhook
        inbound_data = {
            "hostname": self.domain,
            "url": webhook_url,
            "spam_check": True,
            "send_raw": False
        }
        
        response = requests.post(
            "https://api.sendgrid.com/v3/user/webhooks/parse/settings",
            headers=headers,
            json=inbound_data
        )
        
        if response.status_code in [200, 201]:
            print("✅ SendGrid inbound parse configured successfully")
        else:
            print(f"❌ SendGrid setup failed: {response.text}")
    
    def generate_env_file(self, email_service, api_key, domain=None):
        """Generate .env file with email service configuration"""
        if domain:
            self.domain = domain
            
        env_content = f"""# Safe Transaction Email Configuration
# Generated on {datetime.now().isoformat()}

# Email Service Configuration
EMAIL_SERVICE={email_service.upper()}
"""
        
        if email_service.lower() == "mailgun":
            env_content += f"""MAILGUN_API_KEY={api_key}
MAILGUN_DOMAIN={self.domain}
"""
        elif email_service.lower() == "sendgrid":
            env_content += f"""SENDGRID_API_KEY={api_key}
SENDGRID_DOMAIN={self.domain}
"""
        
        env_content += f"""
# Domain Configuration
DOMAIN={self.domain}
WEBHOOK_BASE_URL=https://{self.domain}

# Stripe Configuration (Add your keys)
STRIPE_PUBLISHABLE_KEY=pk_test_your_key_here
STRIPE_SECRET_KEY=sk_test_your_key_here

# Flask Configuration
FLASK_SECRET_KEY=your_secret_key_here
FLASK_ENV=production
"""
        
        with open('.env', 'w') as f:
            f.write(env_content)
            
        print(f"✅ Generated .env file with {email_service} configuration")
        print("⚠️  Remember to update Stripe keys and Flask secret key!")
    
    def verify_dns_setup(self):
        """Verify DNS configuration for the domain"""
        print(f"🔍 Checking DNS setup for {self.domain}...")
        
        try:
            import socket
            
            # Check if domain resolves
            ip = socket.gethostbyname(self.domain)
            print(f"✅ Domain {self.domain} resolves to {ip}")
            
            # Check MX records (basic check)
            print("📧 MX record check - configure with your email service provider")
            
        except socket.gaierror:
            print(f"❌ Domain {self.domain} does not resolve")
            print("⚠️  Make sure to configure DNS records with your domain provider")
    
    def create_test_transaction(self):
        """Create a test transaction for testing"""
        print("🧪 Creating test transaction...")
        
        test_data = {
            "buyer_email": "test.buyer@example.com",
            "seller_email": "test.seller@example.com", 
            "event_name": "Test Concert",
            "location": "Test Venue",
            "price": 100,
            "event_datetime": "2024-12-31 20:00:00"
        }
        
        print("📝 Test transaction data:")
        print(json.dumps(test_data, indent=2))
        print("\n🔗 Use this data to create a test listing in your application")


def main():
    """Interactive setup wizard"""
    print("🎉 Welcome to Safe Transaction Email Service Setup!")
    print("=" * 50)
    
    setup = EmailServiceSetup()
    
    # Get domain
    domain = input(f"Enter your domain (default: {setup.domain}): ").strip()
    if domain:
        setup.domain = domain
    
    # Choose email service
    print("\nChoose your email service:")
    print("1. Mailgun (Recommended)")
    print("2. SendGrid")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        print("\n📧 Setting up Mailgun...")
        api_key = input("Enter your Mailgun API key: ").strip()
        webhook_url = input(f"Enter your webhook URL (e.g., https://{setup.domain}/webhook/mailgun): ").strip()
        
        if api_key and webhook_url:
            setup.setup_mailgun(api_key, webhook_url)
            setup.generate_env_file("mailgun", api_key, setup.domain)
        else:
            print("❌ API key and webhook URL are required")
            
    elif choice == "2":
        print("\n📧 Setting up SendGrid...")
        api_key = input("Enter your SendGrid API key: ").strip()
        webhook_url = input(f"Enter your webhook URL (e.g., https://{setup.domain}/webhook/sendgrid): ").strip()
        
        if api_key and webhook_url:
            setup.setup_sendgrid(api_key, webhook_url)
            setup.generate_env_file("sendgrid", api_key, setup.domain)
        else:
            print("❌ API key and webhook URL are required")
    else:
        print("❌ Invalid choice")
        return
    
    # Additional setup steps
    print("\n🔍 Running additional checks...")
    setup.verify_dns_setup()
    setup.create_test_transaction()
    
    print("\n🎉 Setup complete!")
    print("📋 Next steps:")
    print("1. Configure DNS records with your domain provider")
    print("2. Update Stripe keys in .env file")
    print("3. Deploy your application with HTTPS")
    print("4. Test the full workflow")


if __name__ == "__main__":
    main()
