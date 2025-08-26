# 🚀 Safe Transaction Automated System Deployment Guide

This guide will help you deploy the new automated transaction system that eliminates manual intervention and provides 100% automated escrow for ticket sales.

## 📋 What's New

### ✨ Key Features
- **100% Automated Escrow**: No manual intervention required
- **Email-Based Ticket Transfer**: Works with any ticket platform
- **Smart Deadline Management**: Configurable timeouts with automatic actions
- **Automatic Payment Release**: Funds released after 24 hours or buyer confirmation
- **Real-time Status Tracking**: Complete transaction visibility
- **Built-in Fraud Protection**: Multi-layer verification system

### 🔄 Migration from Old System
- Existing transactions will continue to work
- New transactions use the automated system
- Database schema safely upgraded
- All existing data preserved

---

## 🛠️ Step-by-Step Deployment

### Step 1: Run Database Migration

```bash
# Navigate to your project directory
cd /path/to/Safe-Transaction

# Run the migration script
python bin/run_migration.py
```

**What this does:**
- Safely backs up your existing data
- Adds new columns for automated system
- Migrates existing transactions to new format
- Creates necessary indexes

### Step 2: Install Required Dependencies

```bash
# Install the schedule library for background jobs
pip install schedule

# Make sure you have all existing dependencies
pip install -r requirements.txt
```

### Step 3: Configure Email Receiving

You need to set up email receiving for `*@safetransaction.com`. Choose one option:

#### Option A: Using Mailgun (Recommended)
1. Sign up for Mailgun account
2. Add your domain `safetransaction.com`
3. Set up webhook URL: `https://yourdomain.com/webhook/email/ticket/{transaction_id}`
4. Configure DNS records as per Mailgun instructions

#### Option B: Using Gmail API
1. Set up Gmail API credentials
2. Configure email forwarding rules
3. Parse incoming emails in your application

#### Option C: Using Email Parsing Service
1. Use services like Zapier or IFTTT
2. Set up email parsing webhooks
3. Forward parsed data to your application

### Step 4: Start Background Jobs

```bash
# Start the background job processor
python bin/start_background_jobs.py
```

**What background jobs do:**
- Check deadlines every 5 minutes
- Auto-expire listings without tickets
- Return tickets when payment deadlines pass
- Release funds after 24 hours
- Send reminder emails

### Step 5: Update Environment Variables

Add these to your environment configuration:

```bash
# Stripe configuration (you should already have these)
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...

# Email configuration
MAIL_SERVER=your-email-server.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@domain.com
MAIL_PASSWORD=your-email-password

# Your domain for email generation
DOMAIN_NAME=safetransaction.com
```

### Step 6: Deploy Updated Application

```bash
# Stop your current application
# Deploy the updated code
# Restart your application

# If using systemd, you might do:
sudo systemctl restart your-app
sudo systemctl restart nginx  # if applicable
```

---

## 🧪 Testing the New System

### Test 1: Basic Transaction Flow

1. **Create a listing** with yourself as buyer
2. **Check email generation**: Should get unique email like `ticket-123@safetransaction.com`
3. **Send test ticket email**: Forward any email to the generated address
4. **Verify processing**: Check transaction status updates
5. **Test payment flow**: Use Stripe test cards
6. **Verify auto-forwarding**: Check ticket delivery
7. **Test confirmation**: Try early confirmation and auto-release

### Test 2: Deadline Scenarios

1. **Create listing with short deadline** (6 hours)
2. **Let it expire**: Verify auto-expiration
3. **Test payment deadline**: Send ticket, don't pay, verify return

### Test 3: Error Handling

1. **Test wrong email sender**: Send from different email
2. **Test invalid tickets**: Send non-ticket email
3. **Test payment failures**: Use declined test cards

---

## 📊 Monitoring and Maintenance

### Background Job Monitoring

Keep an eye on the background job logs:

```bash
# Check if background jobs are running
ps aux | grep start_background_jobs

# View logs
tail -f /var/log/safe-transaction/background-jobs.log
```

### Database Monitoring

Monitor key metrics:

```sql
-- Active transactions by status
SELECT status, COUNT(*) 
FROM transactions 
GROUP BY status;

-- Transactions created in last 24 hours
SELECT COUNT(*) 
FROM transactions 
WHERE created_time > datetime('now', '-24 hours');

-- Average time to completion
SELECT AVG(
  julianday(funds_released_time) - julianday(created_time)
) * 24 as avg_hours_to_completion
FROM transactions 
WHERE status = 'completed';
```

### Email System Health

Monitor email processing:

```bash
# Check email webhook logs
tail -f /var/log/nginx/access.log | grep webhook

# Monitor email sending
grep "Email sent" /var/log/safe-transaction/app.log
```

---

## 🚨 Troubleshooting

### Common Issues

#### Background Jobs Not Running
```bash
# Check if script is running
ps aux | grep start_background_jobs

# Restart if needed
python bin/start_background_jobs.py &
```

#### Emails Not Being Received
1. Check DNS configuration for your domain
2. Verify webhook URL is accessible
3. Check email service provider logs
4. Test with curl:
```bash
curl -X POST https://yourdomain.com/webhook/email/ticket/123 \
  -d "sender=test@gmail.com" \
  -d "subject=Test ticket" \
  -d "body-plain=Test body"
```

#### Payments Not Processing
1. Check Stripe configuration
2. Verify webhook endpoints
3. Check API keys are correct
4. Monitor Stripe dashboard for errors

#### Database Migration Issues
```bash
# Check current schema
sqlite3 var/insta485.sqlite3 ".schema transactions"

# Rollback if needed (restore from transactions_backup)
sqlite3 var/insta485.sqlite3 "DROP TABLE transactions; ALTER TABLE transactions_backup RENAME TO transactions;"
```

---

## 🔧 Configuration Options

### Deadline Defaults
You can modify default deadlines in `insta485/transaction_manager.py`:

```python
# Default deadlines (in hours)
DEFAULT_TICKET_DEADLINE = 24
DEFAULT_PAYMENT_DEADLINE = 48
DEFAULT_RELEASE_DEADLINE = 24
```

### Verification Thresholds
Adjust fraud detection sensitivity:

```python
# Minimum verification score (0-100)
MIN_VERIFICATION_SCORE = 70

# Trusted email domains
TRUSTED_DOMAINS = ['ticketmaster.com', 'stubhub.com', 'seatgeek.com']
```

### Platform Fees
Configure your revenue model:

```python
# Platform fee percentage (0.05 = 5%)
PLATFORM_FEE_RATE = 0.05
```

---

## 📈 Performance Optimization

### Database Indexes
The migration creates these indexes for performance:

```sql
CREATE INDEX idx_transactions_status ON transactions(status);
CREATE INDEX idx_transactions_deadlines ON transactions(ticket_deadline, payment_deadline, release_deadline);
CREATE INDEX idx_transactions_emails ON transactions(buyer_email, seller_email);
```

### Background Job Frequency
Adjust background job frequency in `insta485/background_jobs.py`:

```python
# Check deadlines every 5 minutes (current)
schedule.every(5).minutes.do(self._check_all_deadlines)

# Or make it more/less frequent:
schedule.every(1).minutes.do(self._check_all_deadlines)  # More frequent
schedule.every(10).minutes.do(self._check_all_deadlines)  # Less frequent
```

---

## 🆘 Support and Maintenance

### Log Locations
- Application logs: `/var/log/safe-transaction/app.log`
- Background job logs: `/var/log/safe-transaction/background-jobs.log`
- Nginx logs: `/var/log/nginx/access.log` and `/var/log/nginx/error.log`

### Regular Maintenance Tasks

#### Weekly
- Check background job health
- Review failed transactions
- Monitor email delivery rates
- Check Stripe webhook health

#### Monthly
- Analyze transaction completion rates
- Review fraud detection effectiveness
- Update trusted domain lists
- Performance optimization review

#### Quarterly
- Database cleanup (archive old transactions)
- Security audit
- Update dependencies
- Review and optimize fees

---

## 🎯 Success Metrics

Monitor these KPIs for system health:

- **Transaction completion rate**: Should be >95%
- **Average time to completion**: Target <48 hours
- **Email delivery success rate**: Should be >99%
- **Payment success rate**: Should be >90%
- **User satisfaction**: Monitor complaint rates

---

## 🚀 You're Ready!

Once you've completed all steps:

1. ✅ Database migrated
2. ✅ Background jobs running
3. ✅ Email receiving configured
4. ✅ Application deployed
5. ✅ Testing completed

Your new automated system is ready to handle transactions with zero manual intervention!

**Need help?** Check the troubleshooting section or contact support.
