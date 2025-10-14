# Transaction Status Reference

This document lists all valid transaction statuses in the Safe Transaction system, organized by workflow stage.

## Valid Statuses (21 total)

### 📝 Initial Setup
- **`pending_ticket_submission`** - Listing created, waiting for seller to send ticket to Safe Transaction

### 🎫 Ticket Transfer Stage
- **`waiting_for_ticket`** - Waiting for seller to physically send the ticket
- **`waiting_for_verification`** - Seller confirmed sending ticket, admin needs to verify it
- **`ticket_sent`** - Ticket has been sent to buyer
- **`ticket_returned`** - Ticket was returned to seller (e.g., after rejection)

### 💰 Payment Stage
- **`waiting_for_payment`** - Ticket verified, waiting for buyer to complete payment
- **`waiting_for_payment_processing`** - Payment is being processed by Stripe
- **`payment_deadline_expired`** - Buyer didn't pay within the deadline

### 🔄 Processing Stage
- **`waiting_for_payment_processing`** - Payment is being processed by Stripe
- **`ticket_forwarded_funds_held`** - Ticket forwarded to buyer, funds held for seller

### ✅ Completion Stage
- **`completed`** - Transaction successfully completed
- **`validated`** - Transaction validated (legacy status)

### ❌ Cancellation/Expiration
- **`cancelled`** - Transaction cancelled (generic)
- **`cancelled_by_seller`** - Seller cancelled the transaction
- **`expired_no_ticket`** - Transaction expired because ticket wasn't sent
- **`expired_no_payment`** - Transaction expired because payment wasn't completed

### 🚨 Complaints/Issues
- **`complaint_filed`** - Buyer filed a complaint
- **`complaint - refunded buyer`** - Complaint resolved in favor of buyer (refunded)
- **`complaint - paid seller`** - Complaint resolved in favor of seller (paid out)

### ⚠️ Special Cases
- **`rejected`** - Transaction rejected (e.g., invalid ticket)
- **`requires_manual_review`** - Transaction needs manual admin review

---

## Status Flow Examples

### Normal Flow
```
pending_ticket_submission
    ↓ (seller clicks "I've Sent the Ticket")
waiting_for_verification
    ↓ (admin clicks "Accept")
waiting_for_payment
    ↓ (buyer pays)
waiting_for_payment_processing
    ↓ (payment confirmed, ticket forwarded)
ticket_forwarded_funds_held
    ↓ (event passes / buyer confirms)
completed
```

### Rejection Flow
```
pending_ticket_submission
    ↓ (seller clicks "I've Sent the Ticket")
waiting_for_verification
    ↓ (admin clicks "Reject")
pending_ticket_submission (back to start with rejection reason)
```

### Expiration Flows
```
pending_ticket_submission
    ↓ (deadline passes without ticket)
expired_no_ticket
```

```
waiting_for_payment
    ↓ (payment deadline passes)
payment_deadline_expired → expired_no_payment
```

### Complaint Flow
```
ticket_forwarded_funds_held
    ↓ (buyer reports issue)
complaint_filed
    ↓ (admin resolves)
complaint - refunded buyer  OR  complaint - paid seller
```

---

## Removed Statuses

The following statuses were defined in the schema but never used in code:
- ❌ `cancelled_by_buyer` - Never implemented (use `cancelled` instead)
- ❌ `complaint_resolved_buyer` - Replaced by `complaint - refunded buyer`
- ❌ `complaint_resolved_seller` - Replaced by `complaint - paid seller`

These have been removed from the schema CHECK constraint.

---

**Last Updated:** October 13, 2025
**Total Active Statuses:** 21

