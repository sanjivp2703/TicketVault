"""
Mailgun Configuration for Safe Transaction
Run this to set up your Mailgun integration
"""

# MAILGUN CONFIGURATION
# Replace these with your actual Mailgun details

# Option 1: Sandbox Domain (for testing)
MAILGUN_SANDBOX_DOMAIN = "sandboxb9b4c56251404e08939d238b07603aff.mailgun.org"  # Your actual sandbox domain
MAILGUN_API_KEY = "<MAILGUN_API_KEY>"  # Your actual Mailgun API key
MAILGUN_SENDING_KEY = "<MAILGUN_API_KEY>"  # Your sending API key
MAILGUN_WEBHOOK_SIGNING_KEY = "491deb91a47f367eb4ad777a961dfd8d"  # Your webhook signing key

# Option 2: Custom Domain (for production)
MAILGUN_CUSTOM_DOMAIN = "safetransaction.com"  # Replace with your actual domain

# Email addresses that will receive emails in sandbox mode
AUTHORIZED_RECIPIENTS = [
    "safetransactiontix@gmail.com",  # Your Gmail
    "vedavyasj1@gmail.com",  # Add any other emails you want to test with
]

def get_mailgun_config(use_sandbox=True):
    """Get Mailgun configuration"""
    if use_sandbox:
        return {
            'domain': MAILGUN_SANDBOX_DOMAIN,
            'api_key': MAILGUN_API_KEY,
            'base_url': f'https://api.mailgun.net/v3/{MAILGUN_SANDBOX_DOMAIN}',
            'webhook_url': 'https://your-ngrok-url.ngrok.io/webhook/mailgun',  # We'll set this up
            'authorized_recipients': AUTHORIZED_RECIPIENTS
        }
    else:
        return {
            'domain': MAILGUN_CUSTOM_DOMAIN,
            'api_key': MAILGUN_API_KEY,
            'base_url': f'https://api.mailgun.net/v3/{MAILGUN_CUSTOM_DOMAIN}',
            'webhook_url': 'https://yourdomain.com/webhook/mailgun',
            'authorized_recipients': None  # No restrictions with custom domain
        }

if __name__ == "__main__":
    print("🔧 MAILGUN SETUP INSTRUCTIONS")
    print("=" * 50)
    print()
    print("1. Go to your Mailgun dashboard")
    print("2. Find your sandbox domain (looks like: sandbox123abc.mailgun.org)")
    print("3. Get your Private API Key from Settings → API Keys")
    print("4. Update the values in this file:")
    print(f"   - MAILGUN_SANDBOX_DOMAIN = '{MAILGUN_SANDBOX_DOMAIN}'")
    print(f"   - MAILGUN_API_KEY = '{MAILGUN_API_KEY}'")
    print()
    print("5. Add authorized recipients (emails that can receive in sandbox mode):")
    for email in AUTHORIZED_RECIPIENTS:
        print(f"   - {email}")
    print()
    print("6. Run: python setup_mailgun.py")
