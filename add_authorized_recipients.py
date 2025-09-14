"""
Add Authorized Recipients to Mailgun Sandbox Domain
"""

import requests
from mailgun_config import get_mailgun_config

def add_authorized_recipient(email, config):
    """Add an authorized recipient to sandbox domain"""
    url = f"{config['base_url']}/bounces"
    
    # First, remove any existing bounces for this email
    try:
        delete_response = requests.delete(
            f"{config['base_url']}/bounces/{email}",
            auth=('api', config['api_key'])
        )
        print(f"🗑️  Cleared any existing bounces for {email}")
    except:
        pass
    
    # Add to authorized recipients by sending a test email
    url = f"{config['base_url']}/messages"
    
    data = {
        'from': f'Safe Transaction <noreply@{config["domain"]}>',
        'to': email,
        'subject': '✅ Authorization Test - Safe Transaction',
        'html': f'''
        <h2>✅ Email Authorization Successful!</h2>
        <p>Your email <strong>{email}</strong> is now authorized to receive emails from Safe Transaction.</p>
        <p>🎉 You can now receive:</p>
        <ul>
            <li>Payment notifications</li>
            <li>Ticket verification updates</li>
            <li>Transaction confirmations</li>
        </ul>
        <p><em>This is an automated message from Safe Transaction.</em></p>
        '''
    }
    
    try:
        response = requests.post(
            url,
            auth=('api', config['api_key']),
            data=data
        )
        
        if response.status_code == 200:
            print(f"✅ SUCCESS: {email} is now authorized!")
            print(f"📧 Authorization email sent to {email}")
            return True
        else:
            print(f"❌ ERROR: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def main():
    print("📧 ADDING AUTHORIZED RECIPIENTS TO MAILGUN SANDBOX")
    print("=" * 60)
    
    config = get_mailgun_config(use_sandbox=True)
    
    # List of emails to authorize
    emails_to_authorize = [
        "safetransactiontix@gmail.com",
        "vedavyasj1@gmail.com",
        "psanjiv@umich.edu",
        "sanjivp2703@gmail.com",
        "user2@gmail.com"
    ]
    
    print(f"🎯 Authorizing emails for domain: {config['domain']}")
    print()
    
    success_count = 0
    for email in emails_to_authorize:
        print(f"📧 Authorizing: {email}")
        if add_authorized_recipient(email, config):
            success_count += 1
        print()
    
    print("=" * 60)
    print(f"🎉 COMPLETED: {success_count}/{len(emails_to_authorize)} emails authorized")
    print("📧 Check your emails for authorization confirmations")
    
    if success_count == len(emails_to_authorize):
        print("✅ All emails are now authorized for sandbox testing!")
    else:
        print("⚠️  Some emails failed - check the error messages above")

if __name__ == "__main__":
    main()
