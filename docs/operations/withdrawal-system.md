# Withdrawal System Documentation

## Overview
The Safe Transaction withdrawal system allows sellers to withdraw their earned balance to their bank accounts. The system supports both **automatic** (via Stripe) and **manual** processing.

## Key Features

### 1. **5% Transaction Fee**
- All withdrawals have a 5% Safe Transaction fee
- Example: $100 withdrawal = $5 fee, user receives $95
- Fee is clearly displayed before confirmation

### 2. **Minimum Withdrawal**
- Minimum amount: $10.00
- Prevents micro-transactions that aren't economical

### 3. **Dual Processing Mode**

#### Automatic Processing (Stripe Connect)
- If user has `stripe_id` configured (Stripe Connect account)
- Transfer happens immediately via `stripe.Transfer.create()`
- Funds arrive in 1-3 business days
- User gets confirmation email instantly

#### Manual Processing (Fallback)
- If user doesn't have Stripe Connect set up
- Withdrawal request stored in `withdrawal_requests` table
- Admin processes manually via bank transfer
- User still gets confirmation email
- Status: "pending" → admin marks "completed"

### 4. **Security**
- Only last 4 digits of account number stored
- Bank details encrypted at rest
- Withdrawal history tracked
- Email confirmations for all withdrawals

## Database Schema

### `withdrawal_requests` Table
```sql
- id: Primary key
- user_email: User requesting withdrawal
- amount: Full amount in cents (before fee)
- fee_amount: 5% fee in cents
- transfer_amount: Net amount in cents (after fee)
- bank_name: Bank name
- routing_number: 9-digit routing number
- account_number_last4: Last 4 digits only (security)
- status: 'pending', 'completed', 'failed', 'cancelled'
- stripe_transfer_id: Stripe Transfer ID (if automatic)
- created_at: Request timestamp
- completed_at: Completion timestamp
- notes: Admin notes
```

## User Flow

1. **User clicks "Withdraw Funds"** from homepage
2. **Enters bank details**:
   - Bank name
   - Routing number (9 digits)
   - Account number
3. **Reviews summary** showing:
   - Withdrawal amount
   - 5% fee
   - Net amount they'll receive
4. **Submits request**
5. **System processes**:
   - Deducts balance immediately
   - Records fee separately
   - Attempts Stripe transfer (if configured)
   - Falls back to manual processing
   - Sends confirmation email
6. **Funds arrive** in 1-3 business days

## Admin Manual Processing

For withdrawals needing manual processing:

1. Check `withdrawal_requests` table for `status = 'pending'`
2. Verify user's balance was deducted
3. Process ACH transfer to user's bank using:
   - `bank_name`
   - `routing_number`
   - `account_number_last4` (get full number from secure storage if needed)
   - `transfer_amount` (this is AFTER the 5% fee)
4. Update status:
   ```sql
   UPDATE withdrawal_requests 
   SET status = 'completed', 
       completed_at = datetime('now'),
       notes = 'Processed via Zelle/ACH'
   WHERE id = ?
   ```

## Email Notifications

Users receive a professional HTML email showing:
- ✅ Withdrawal confirmed
- 💰 Amount breakdown (withdrawal - fee = net)
- ⏱️ Expected arrival (1-3 business days)
- 🔒 Security information
- 📧 Support contact

## Production Checklist

✅ 5% fee calculation working
✅ Minimum $10 enforcement
✅ Balance deduction atomic
✅ Withdrawal requests logged
✅ Email confirmations sent
✅ Stripe automatic processing (when available)
✅ Manual processing fallback
✅ Security: only last 4 digits stored
✅ Professional UI
✅ Clear fee disclosure

## Future Enhancements

- [ ] Stripe Connect onboarding flow for all sellers
- [ ] Automated ACH via Stripe payouts
- [ ] Withdrawal history page for users
- [ ] Admin dashboard for pending withdrawals
- [ ] Support for multiple bank accounts
- [ ] Instant payouts (1.5% fee for instant vs 5% for standard)

## Testing

To test withdrawals:

1. **Add balance to test account**:
   ```sql
   UPDATE users SET balance = 10000 WHERE email = 'test@example.com';  -- $100
   ```

2. **Submit withdrawal** through UI

3. **Check database**:
   ```sql
   SELECT * FROM withdrawal_requests WHERE user_email = 'test@example.com';
   SELECT * FROM balance_changes WHERE user_email = 'test@example.com';
   ```

4. **Verify**:
   - Balance reduced by full amount
   - Fee recorded separately
   - Withdrawal request created
   - Email sent

## Support

For withdrawal issues:
- Check `withdrawal_requests` table
- Review balance_changes for audit trail
- Check logs for Stripe errors
- Contact: support@safetransaction.app

