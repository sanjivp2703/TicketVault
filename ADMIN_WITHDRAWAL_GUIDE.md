# 💸 Admin Quick Guide - Processing Withdrawals

## Overview
Users can now withdraw funds via **Venmo/PayPal**, **Cash App**, or **Stripe Connect**. Venmo/Cash App require **manual processing** by you. Stripe is automatic.

---

## How to Access

1. Go to `/admin` (Admin Dashboard)
2. Look at top stats - you'll see **💸 Pending Withdrawals** count
3. Scroll down - there's a **dedicated orange section** for pending withdrawals
4. It shows up **right after "Action Needed" section**

---

## What You'll See

### Pending Withdrawals Section (Orange):
```
💸 Pending Withdrawals - Manual Processing Required
X withdrawal(s) waiting for you to process
```

### Table Columns:
- **ID**: Withdrawal request ID
- **User**: Name + email
- **Method**: Venmo/PayPal/Cash App/Stripe badge
- **Send To**: @username or $cashtag or email
- **Amount Requested**: What user asked for
- **5% Fee**: Our platform fee
- **💰 Send Amount**: **THIS IS THE AMOUNT YOU SEND** (highlighted in green)
- **Created**: When they requested it
- **Action**: Step-by-step instructions

---

## How to Process (Step-by-Step)

### Venmo / PayPal Withdrawal:
```
1. Read the blue action box on the right
2. It says:
   "1. Open Venmo or PayPal app
    2. Send $XX.XX to: @username (or email)
    3. After sending, click below"
3. Open your Venmo/PayPal app
4. Send the exact amount shown to the username/email shown
5. Click "✅ Mark as Sent" button
6. Confirm the popup
7. ✅ Done! It disappears from the list
```

### Cash App Withdrawal:
```
1. Read the green action box on the right
2. It says:
   "1. Open Cash App
    2. Send $XX.XX to: $cashtag
    3. After sending, click below"
3. Open your Cash App
4. Send the exact amount shown to the $cashtag shown
5. Click "✅ Mark as Sent" button
6. Confirm the popup
7. ✅ Done! It disappears from the list
```

### Stripe Withdrawal (Automatic):
- **Usually doesn't appear here** - it's automatic!
- If it does appear: Stripe failed, you need to process manually
- Yellow box with warning
- Contact user or process via bank transfer
- Click "✅ Mark as Completed" when done

---

## Important Details

### The Green Amount is What You Send!
The **💰 Send Amount** column (highlighted in green) is the amount you actually send to the user. This is **after** the 5% fee has been deducted.

Example:
- User requested: $100.00
- 5% fee: -$5.00
- **Send amount: $95.00** ← This is what you send!

### Double-Check Payment Details
The **Send To** column shows:
- `@username` for Venmo
- `email@example.com` for PayPal
- `$cashtag` for Cash App

Make sure you send to the **exact** username/email/$cashtag shown!

### Processing Time
- Try to process within **one business day**
- Users are told "typically within one business day"
- Faster is better for user satisfaction!

---

## The Button Workflow

When you click **"✅ Mark as Sent"**:
1. Popup appears asking for confirmation
2. Warning: "Make sure you've sent the money!"
3. If you click OK:
   - Status changes to 'completed'
   - Timestamp recorded
   - Withdrawal disappears from pending list
   - User can check their Venmo/Cash App/PayPal

---

## Example Workflow

**User: John Smith requests withdrawal**

1. You see in admin:
   ```
   ID: #15
   User: John Smith (john@umich.edu)
   Method: 💳 Venmo/PayPal
   Send To: @johnsmith
   Amount Requested: $100.00
   5% Fee: -$5.00
   💰 Send Amount: $95.00
   Created: 2025-01-20 14:30:00
   
   Action: [Blue box]
   📱 Action Required:
   1. Open Venmo or PayPal app
   2. Send $95.00 to: @johnsmith
   3. After sending, click below:
   
   [✅ Mark as Sent button]
   ```

2. You:
   - Open Venmo app on your phone
   - Send $95.00 to @johnsmith
   - Return to admin dashboard
   - Click "✅ Mark as Sent"
   - Confirm popup

3. Result:
   - ✅ Withdrawal #15 marked as completed!
   - Disappears from pending list
   - John Smith sees money in his Venmo!

---

## Quick Checklist

Before clicking "Mark as Sent":
- [ ] Opened correct app (Venmo/PayPal/Cash App)
- [ ] Sent exact amount shown (the **green** amount)
- [ ] Sent to exact username/email/$cashtag shown
- [ ] Transaction confirmed in app
- [ ] Ready to mark as complete in dashboard

---

## Troubleshooting

### "I accidentally marked it complete but didn't send money"
- **Check database**: `SELECT * FROM withdrawal_requests WHERE id = X;`
- If needed, manually send money to user
- Record in notes

### "User says they didn't receive money"
- Check your Venmo/Cash App/PayPal transaction history
- Verify you sent to correct username/$cashtag
- Check if it's still pending in the payment app
- Contact user with transaction ID from payment app

### "What if I send to the wrong person?"
- **Prevention is key!** Always double-check before sending
- If it happens: Try to cancel in payment app (if still pending)
- Contact the recipient and request a refund
- Contact Safe Transaction support
- May need to manually refund user from our funds

### "Withdrawal stuck in pending?"
- Check if you clicked "Mark as Sent" after sending money
- If you sent money but forgot to mark: Click the button now
- If not sent yet: Process it ASAP (within one business day)

---

## Statistics

Track your performance:
- **Pending count** shown in top stats (orange if > 0)
- **Response time** matters for user satisfaction
- **Goal**: Process within 4 hours during business hours

---

## Best Practices

1. **Check dashboard 2-3 times per day** during business hours
2. **Process immediately** when you see pending withdrawals
3. **Always double-check** payment details before sending
4. **Mark as sent immediately** after sending (don't forget!)
5. **Keep your payment apps open** for quick processing
6. **Reply to "Did you send it?" messages** quickly

---

## Summary

**You have 3 jobs:**
1. ✅ Check admin dashboard regularly
2. ✅ Send money via Venmo/Cash App when you see pending withdrawals
3. ✅ Click "Mark as Sent" after sending

**It's that simple!** The dashboard tells you exactly what to do. Just follow the step-by-step instructions in the blue/green action boxes.

---

## Need Help?

- Database issue: Check `withdrawal_requests` table
- Payment app issue: Check Venmo/Cash App/PayPal support
- User complaint: Check transaction history, verify you sent correctly

**Emergency contact**: Your own email or Safe Transaction support

