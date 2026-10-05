# Safe Transaction - Automated System Setup Guide

## 🎯 System Overview

Your Safe Transaction platform now has a **fully automated verification and payment system**. Here's how it works:

### Seller Flow:
1. **Create Listing** → System generates unique email (tx-123456@safetransaction.com)
2. **Send Ticket Email** → Seller forwards ticket to generated email
3. **Auto-Verification** → System verifies ticket details automatically
4. **Buyer Notification** → If verified, buyer gets payment link with 1-hour deadline
5. **Payment Processing** → Once paid, funds held until completion
6. **Auto-Release** → Funds released to seller after event completion

### Buyer Flow:
1. **Receive Email** → Gets notification with secure payment link
2. **Pay Securely** → 1-hour window to complete payment via Stripe
3. **Receive Ticket** → Ticket forwarded immediately after payment
4. **Confirm Receipt** → Optional confirmation to release funds early

---

## 🛠️ Required Setup Steps

### 1. Email Service Configuration (CRITICAL)

**Option A: Mailgun (Recommended)**
```bash
# Set up Mailgun domain
Domain: safetransaction.com
API Key: [Your Mailgun API Key]
Webhook URL: https://yourdomain.com/webhook/mailgun
```

**Option B: SendGrid**
```bash
# Set up SendGrid Inbound Parse
Domain: safetransaction.com  
Webhook URL: https://yourdomain.com/webhook/sendgrid
```

**Option C: Custom IMAP (Advanced)**
- Configure IMAP monitoring in `insta485/email_monitor.py`
- Update credentials in environment variables

### 2. Domain Setup

**DNS Configuration:**
```
MX Record: safetransaction.com → [Email Service MX]
A Record: safetransaction.com → [Your Server IP]
```

**Subdomain for Transactions:**
- All transaction emails use format: `tx-123456@safetransaction.com`
- Configure email service to forward these to your webhook

### 3. Environment Variables

Create `.env` file:
```bash
# Email Configuration
MAILGUN_API_KEY=your_mailgun_api_key
MAILGUN_DOMAIN=safetransaction.com

# Stripe Configuration  
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...

# Database
DATABASE_URL=sqlite:///var/insta485.sqlite3

# Flask Configuration
FLASK_SECRET_KEY=your_secret_key_here
FLASK_ENV=production
```

### 4. Webhook Configuration

**Mailgun Webhook Settings:**
- URL: `https://yourdomain.com/webhook/mailgun`
- Events: `delivered`, `stored`
- Method: POST

**SendGrid Inbound Parse:**
- URL: `https://yourdomain.com/webhook/sendgrid`
- Hostname: `safetransaction.com`

---

## 🚀 Current System Status

### ✅ Already Implemented:
- **UI Fixes**: Active listings now show below "Create Listing" with proper spacing
- **Listing Creation**: Popup system with email instructions
- **Database Schema**: Complete with all necessary tracking fields
- **Transaction Manager**: Full automation for verification and payment
- **Email Automation**: Modern buyer/seller notifications
- **API Endpoints**: Test verification, payment processing, status tracking
- **Error Handling**: Comprehensive failure scenario management
- **Webhook System**: Ready for Mailgun/SendGrid integration

### ⚠️ Needs Configuration:
1. **Email Service**: Set up Mailgun or SendGrid account
2. **Domain**: Configure DNS and email routing
3. **Stripe**: Add your live Stripe keys
4. **SSL Certificate**: Ensure HTTPS for webhooks

---

## 🧪 Testing the System

### 1. Test Mode (No Email Required)
```javascript
// Use the "Test Verify" button in the popup
// This bypasses email verification for testing
```

### 2. Email Simulation
```bash
# Create test email file
curl -X POST http://localhost:8000/api/simulate-ticket-email \
  -H "Content-Type: application/json" \
  -d '{"transaction_id": 123, "subject": "Your Event Tickets"}'
```

### 3. Full Integration Test
1. Create a listing
2. Send actual email to tx-123456@safetransaction.com
3. Verify automatic processing
4. Test buyer payment flow

---

## 📧 Email Service Integration

### Mailgun Integration (Recommended)

**1. Account Setup:**
- Sign up at mailgun.com
- Verify domain: safetransaction.com
- Get API key from dashboard

**2. Webhook Configuration:**
```bash
curl -X POST https://api.mailgun.net/v3/domains/safetransaction.com/webhooks \
  -u api:YOUR_API_KEY \
  -d url=https://yourdomain.com/webhook/mailgun \
  -d event=delivered
```

**3. Test Webhook:**
```bash
# Send test email
curl -X POST https://api.mailgun.net/v3/safetransaction.com/messages \
  -u api:YOUR_API_KEY \
  -d from="test@safetransaction.com" \
  -d to="tx-000001@safetransaction.com" \
  -d subject="Test Ticket" \
  -d text="Test ticket content"
```

---

## 🔄 Automated Processes

### 1. Email Monitoring
- **File**: `insta485/email_monitor.py`
- **Frequency**: Every 10 seconds
- **Function**: Checks for new ticket emails

### 2. Deadline Management
- **File**: `insta485/deadline_manager.py`
- **Function**: Handles payment timeouts, fund releases
- **Triggers**: Automatic based on deadlines

### 3. Background Jobs
- **Payment Processing**: Stripe webhook handling
- **Fund Releases**: Automatic after event completion
- **Reminder Emails**: Payment and deadline notifications

---

## 🛡️ Security Considerations

### 1. Email Verification
- Sender validation (must match seller email)
- Content analysis (event name matching)
- Domain reputation checking
- Attachment verification

### 2. Payment Security
- Stripe secure payment processing
- Funds held in escrow until completion
- Automatic refunds for failed transactions

### 3. Fraud Prevention
- Duplicate email detection
- Verification score thresholds
- Admin review for suspicious transactions

---

## 📊 Monitoring & Analytics

### 1. Transaction Tracking
- Real-time status updates
- Verification scores and notes
- Payment processing logs

### 2. Error Handling
- Failed verification alerts
- Payment processing errors
- Email delivery failures

### 3. Performance Metrics
- Average verification time
- Payment completion rates
- User satisfaction scores

---

## 🚨 Troubleshooting

### Common Issues:

**1. Emails Not Being Processed:**
- Check webhook URL is accessible
- Verify email service configuration
- Check server logs for errors

**2. Verification Failures:**
- Review verification criteria
- Check event name matching
- Verify sender email addresses

**3. Payment Issues:**
- Confirm Stripe configuration
- Check webhook endpoints
- Verify SSL certificates

### Debug Commands:
```bash
# Check email monitor status
python -c "from insta485.email_monitor import email_monitor; print(email_monitor.running)"

# Test verification manually
curl -X POST http://localhost:8000/api/test-verify \
  -H "Content-Type: application/json" \
  -d '{"transaction_id": 123, "test_mode": true}'

# Check transaction status
curl http://localhost:8000/api/transactions/123/status
```

---

## 🎉 Next Steps

1. **Set up email service** (Mailgun recommended)
2. **Configure domain and DNS**
3. **Add Stripe live keys**
4. **Test full workflow**
5. **Monitor and optimize**

Your system is now ready for full automation! The only manual step required is the initial email service setup.
