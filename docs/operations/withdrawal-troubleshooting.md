# Withdrawal System Troubleshooting Guide

## 🔧 Issues Fixed

### 1. **Column Name Mismatch (CRITICAL FIX)**
**Problem:** Database columns didn't match the code's expectations.

**Fixed:**
- Updated `mark_withdrawal_complete()` function to use correct column names:
  - `fee_amount` (not `safe_transaction_fee`)
  - `bank_name` (not `payment_method`)
  - `account_number_last4` (not `destination`)

### 2. **Better Error Messages**
**Fixed:** Added detailed error messages so you can see exactly what's failing instead of generic "Failed to process" messages.

---

## 🎯 Common Errors & Solutions

### Error: "Failed to create Stripe update link"

**Cause:** You're trying to update a Stripe account that doesn't exist yet.

**Solution:**
1. First, click **"Connect Bank Account"** (not "Update Bank Account")
2. Complete Stripe onboarding
3. After onboarding is complete, THEN you can use "Update Bank Account"

**How to check if you need onboarding:**
```python
# Run this to check your Stripe status:
python -c "import sqlite3; conn = sqlite3.connect('var/insta485.sqlite3'); cur = conn.cursor(); email = input('Enter your email: '); result = cur.execute('SELECT stripe_id FROM users WHERE email = ?', (email,)).fetchone(); print(f'Stripe ID: {result[0] if result and result[0] else \"NOT CONNECTED - Need to do onboarding first!\"}')"
```

### Error: "Failed to process withdrawal"

**Now with detailed error message!** The new error will show you exactly what went wrong.

**Common causes:**
1. **No payment method selected** - Make sure you click on one of the payment method cards (Venmo, Cash App, or Stripe)
2. **Empty destination field** - Make sure you entered your @username or $cashtag
3. **Insufficient balance** - Can't withdraw more than you have
4. **Database error** - Check the console/terminal for detailed error message

---

## 📋 Step-by-Step: How to Use Each Method

### 🟦 **Venmo Withdrawal (Manual)**

1. **Navigate to withdrawal page** - Click "Withdraw Funds" from dashboard
2. **Click the Venmo card** - It will highlight in blue
3. **Enter your Venmo username** (without the @)
   - Example: Enter `johnsmith` (NOT `@johnsmith`)
   - The @ will be added automatically
4. **Review the fee breakdown** - 5% fee is shown
5. **Read the WARNING** - Make absolutely sure your username is correct!
6. **Click "Withdraw Funds" button**
7. **Check your email** - You'll receive "Withdrawal Request Received" email
8. **Wait for admin** - We'll manually send via Venmo
9. **Get second email** - When sent, you'll receive "Money Sent!" email

### 💚 **Cash App Withdrawal (Manual)**

1. **Navigate to withdrawal page**
2. **Click the Cash App card** - It will highlight in green
3. **Enter your $Cashtag** (without the $)
   - Example: Enter `JohnSmith` (NOT `$JohnSmith`)
   - The $ will be added automatically
4. **Review the fee breakdown** - 5% fee is shown
5. **Read the WARNING** - Make absolutely sure your $Cashtag is correct!
6. **Click "Withdraw Funds" button**
7. **Check your email** - You'll receive "Withdrawal Request Received" email
8. **Wait for admin** - We'll manually send via Cash App
9. **Get second email** - When sent, you'll receive "Money Sent!" email

### 🏦 **Stripe Connect Withdrawal (Automatic or Manual)**

#### **First Time Setup:**

1. **Navigate to withdrawal page**
2. **Click the Stripe Connect card**
3. **Click "Connect Bank Account" button** (DON'T click "Update" if you haven't set up yet!)
4. **You'll be redirected to Stripe**
   - In TEST mode, use Stripe test bank accounts
   - Fill in your information
   - Verify your identity (test mode is lenient)
5. **Complete onboarding**
6. **Return to Safe Transaction** - Your bank account will now be connected
7. **See your bank details** - Bank name and last 4 digits will display

#### **Making a Withdrawal:**

1. **Click the Stripe Connect card** - It will show your connected bank account
2. **Review bank details** - Make sure it's the right account
3. **Click "Withdraw Funds"**
4. **Check email** - You'll receive "Withdrawal Request Received"
5. **Automatic processing:**
   - If Stripe transfer succeeds: Money sent automatically in 1-3 business days
   - If Stripe transfer fails: Admin will process manually
6. **Get second email** - When sent/processed, you'll receive "Money Sent!" email

#### **Updating Your Bank Account:**

1. **Navigate to withdrawal page**
2. **Click Stripe Connect card**
3. **Click "Update Bank Account" button** (ONLY if you already completed onboarding)
4. **Redirected to Stripe**
5. **Update your bank information**
6. **Return to Safe Transaction**

---

## 🔍 Debugging Steps

### Step 1: Check Console Output

When you try to withdraw, look at the terminal/console where Flask is running. You should see detailed error messages like:

```
[WITHDRAWAL ERROR] no such column: payment_method
```

or

```
[STRIPE UPDATE ERROR] No such account: acct_xxxxx
```

### Step 2: Verify Database Schema

Run this to check if the withdrawal_requests table exists:

```bash
python -c "import sqlite3; conn = sqlite3.connect('var/insta485.sqlite3'); cur = conn.cursor(); cur.execute(\"SELECT sql FROM sqlite_master WHERE type='table' AND name='withdrawal_requests'\"); result = cur.fetchone(); print(result[0] if result else 'Table does not exist!')"
```

### Step 3: Check Your User Account

Check if you have a Stripe ID:

```bash
python -c "import sqlite3; conn = sqlite3.connect('var/insta485.sqlite3'); cur = conn.cursor(); email = input('Your email: '); user = cur.execute('SELECT email, balance, stripe_id FROM users WHERE email = ?', (email,)).fetchone(); print(f'Email: {user[0]}\nBalance: ${user[1]/100:.2f}\nStripe ID: {user[2] if user[2] else \"Not connected\"}')"
```

### Step 4: Test Form Submission

Open browser developer tools (F12) and check the Network tab when you submit:
1. Look for POST request to `/withdraw/process`
2. Check the Form Data being sent
3. Should include: `payment_method`, `amount`, and method-specific fields

---

## ⚠️ Important Notes

### **Stripe Connect Test Mode**

In test mode, Stripe has special requirements:
- Use test bank accounts (routing number: 110000000, account: 000123456789)
- Real money is NOT transferred
- Transfers show as "pending" but won't actually move money

### **Common Mistakes**

1. ❌ Clicking "Update Bank Account" before doing initial onboarding
   - ✅ Do: Click "Connect Bank Account" first

2. ❌ Entering @username or $cashtag with the symbol
   - ✅ Do: Enter just the username/tag, symbols are added automatically

3. ❌ Not reading the warning messages
   - ✅ Do: TRIPLE CHECK your destination before submitting!

4. ❌ Expecting instant transfers
   - ✅ Do: Understand timing:
     - Venmo/Cash App: Within 1 business day (manual)
     - Stripe: 1-3 business days (automatic)

---

## 🧪 Testing in Development

### Test Venmo/Cash App Withdrawal:

1. Make sure you have balance (earn some from selling tickets or add test balance)
2. Go to `/withdraw`
3. Select Venmo or Cash App
4. Enter a test username/tag (like `testuser` or `testcashtag`)
5. Submit
6. Check Flask console for success messages
7. Check database: `SELECT * FROM withdrawal_requests ORDER BY created_at DESC LIMIT 1;`
8. Go to `/admin` and verify withdrawal appears in pending list
9. Click "Mark as Sent"
10. Verify completion email would be sent

### Test Stripe Connect:

1. Click "Connect Bank Account"
2. Use Stripe test account:
   - Routing: 110000000
   - Account: 000123456789
   - Complete the form
3. Return to platform
4. Submit withdrawal
5. Check console for Stripe transfer attempt
6. If auto-transfer succeeds, great!
7. If it fails, it should appear in admin pending list

---

## 📞 Still Having Issues?

### Check These Files:

1. **`insta485/views/balance.py`** - All withdrawal logic
2. **`insta485/templates/withdraw_modern.html`** - Withdrawal form
3. **`migrations/0013_add_withdrawal_requests.sql`** - Database schema
4. **`insta485/email_automation.py`** - Email functions

### Enable Debug Mode:

In your Flask app, make sure you're running with:
```bash
flask run --debug
```

This will show detailed error pages with stack traces.

### Database Issues:

If the table doesn't exist or has wrong columns:
```bash
# Re-run migration
python -c "import sqlite3; conn = sqlite3.connect('var/insta485.sqlite3'); conn.executescript(open('migrations/0013_add_withdrawal_requests.sql').read()); conn.commit(); print('Migration applied')"
```

---

## ✅ Verification Checklist

Before declaring it "working":

- [ ] Can submit Venmo withdrawal
- [ ] Can submit Cash App withdrawal
- [ ] Can click "Connect Bank Account" for Stripe
- [ ] Stripe onboarding redirects work
- [ ] Can see bank details after Stripe onboarding
- [ ] Can submit Stripe withdrawal
- [ ] All withdrawals appear in admin dashboard
- [ ] Admin can click "Mark as Sent"
- [ ] Detailed error messages show when things fail
- [ ] Email #1 (Request Received) is sent upon submission
- [ ] Email #2 (Money Sent) is sent when admin marks complete

---

## 🚀 Production Readiness

For production:

1. **Use live Stripe keys** - Replace test keys with live keys
2. **Set up real bank account** - Use actual bank details in Stripe
3. **Test with small amount** - Try $0.50 withdrawal first
4. **Monitor admin dashboard** - Check for failed Stripe transfers
5. **Set up email alerts** - Get notified of pending withdrawals

---

**Last Updated:** October 18, 2025
**Status:** ✅ All critical bugs fixed, ready for testing

