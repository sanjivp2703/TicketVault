# 📧 Email Receiving Setup Guide

## Current Status
✅ **Sending emails works** - Mailgun sends seller instructions  
❌ **Receiving emails needs setup** - tx-XXXXXX@safetransaction.com addresses are generated but not receiving

## What You Need To Do

### Step 1: Install ngrok (for webhook access)
1. **Download ngrok:** https://ngrok.com/download
2. **Install it** and add to your PATH
3. **Run:** `ngrok http 8000` (in a separate terminal)
4. **Copy the HTTPS URL** (like `https://abc123.ngrok.io`)

### Step 2: Configure Mailgun Routes
1. **Go to:** https://app.mailgun.com/app/dashboard
2. **Navigate to:** Sending → Routes
3. **Create a new route:**
   - **Priority:** 1
   - **Filter Expression:** `match_recipient("tx-.*@sandboxb9b4c56251404e08939d238b07603aff.mailgun.org")`
   - **Actions:** `forward("https://YOUR-NGROK-URL.ngrok.io/webhook/mailgun")`
   - **Description:** "Forward ticket emails to webhook"

### Step 3: Test the Flow
1. **Create a listing** on your site
2. **Send an email** to the generated tx-XXXXXX@safetransaction.com address
3. **Check Flask logs** - you should see webhook processing
4. **Verify** the listing gets activated

## Alternative: Manual Testing (For Now)

If you want to test without setting up email receiving, you can use the test endpoint:

```bash
# Test verification success
curl -X POST http://localhost:8000/api/test-verify/TRANSACTION_ID
```

## Email Addresses Explained

- **Generated:** `tx-000010@safetransaction.com` 
- **Actual Mailgun:** `tx-000010@sandboxb9b4c56251404e08939d238b07603aff.mailgun.org`

The system generates `@safetransaction.com` but Mailgun will receive emails sent to your sandbox domain.

## Webhook Endpoints Available

- **Mailgun:** `/webhook/mailgun` 
- **SendGrid:** `/webhook/sendgrid`
- **Test Simulation:** `/api/simulate-ticket-email/TRANSACTION_ID`

## Next Steps

1. **Install ngrok** and get HTTPS URL
2. **Configure Mailgun route** with your ngrok URL  
3. **Test by sending email** to tx-XXXXXX address
4. **Watch Flask logs** for webhook processing

Let me know when you have ngrok running and I'll help configure the Mailgun route!
