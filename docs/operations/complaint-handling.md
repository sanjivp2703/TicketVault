# TicketVault Complaint Handling Guide

## Overview
This document outlines all possible complaint scenarios and the proper resolution process for each. All complaints should be handled through support@safetransaction.app.

---

## Complaint Categories

### 1. **Ticket Never Received by Buyer**

**Scenario:** Buyer paid but never received the ticket transfer

**Investigation Steps:**
1. Check Michigan Athletics account for ticket@swap account
2. Check if seller actually sent the ticket
3. Verify payment was completed
4. Check transaction status and timestamps

**Resolution Options:**

#### If Seller Didn't Send Ticket:
- **Action:** Refund buyer immediately
- **Email to Buyer:**
  - Subject: `Refund Issued - Transaction #[ID] | Ticket Not Sent`
  - Body: "We've confirmed the seller did not transfer the ticket. Full refund of $[AMOUNT] has been issued to your payment method. You should see it within 3-5 business days."
- **Email to Seller:**
  - Subject: `Warning - Transaction #[ID] | Ticket Not Transferred`
  - Body: "Your account has been flagged for failing to transfer tickets. Buyer has been refunded. This may affect your ability to use TicketVault in the future."
- **Database:** Update transaction status to `complaint - refunded buyer (ticket not sent)`

#### If Seller Did Send Ticket:
- **Action:** Contact Michigan Athletics to trace ticket transfer
- **Email to Buyer:**
  - Subject: `Investigating - Transaction #[ID] | Ticket Transfer`
  - Body: "We're investigating with Michigan Athletics. The seller has proof of sending. We'll update you within 24 hours."
- **Follow-up:** If ticket found in buyer's account, mark resolved. If not, refund buyer and investigate seller's proof.

---

### 2. **Ticket is Invalid/Fake**

**Scenario:** Buyer received ticket but it doesn't work at the event

**Investigation Steps:**
1. Request screenshot/photo from buyer showing the issue
2. Check seller's Michigan Athletics account history
3. Verify if ticket was legitimate when sold
4. Check if seller sold same ticket multiple times

**Resolution:**

#### If Ticket was Fake/Invalid:
- **Action:** Full refund to buyer + $20 compensation for inconvenience
- **Email to Buyer:**
  - Subject: `Refund + Compensation - Transaction #[ID] | Invalid Ticket`
  - Body: "We've confirmed the ticket was invalid. Refund of $[AMOUNT] + $20 compensation = $[TOTAL] has been issued. We sincerely apologize for this experience."
- **Email to Seller:**
  - Subject: `Account Suspended - Transaction #[ID] | Fraudulent Activity`
  - Body: "Your account has been permanently suspended for selling invalid tickets. This is a serious violation of our terms of service. No payment will be issued."
- **Database:** Update status to `complaint - fraud refunded buyer`, flag seller account
- **Action:** Ban seller from platform permanently

#### If Ticket Was Legitimate:
- **Action:** Work with Michigan Athletics to resolve entry issue
- **Database:** Mark as `complaint - resolved buyer error`

---

### 3. **Wrong Ticket/Event**

**Scenario:** Buyer received a ticket but it's for the wrong game/seat/section

**Investigation Steps:**
1. Compare listing description with actual ticket sent
2. Check original listing details in database
3. Verify what ticket was actually transferred

**Resolution:**

#### If Seller Sent Wrong Ticket:
- **Action:** Partial or full refund depending on severity
- **Email to Buyer:**
  - Subject: `Refund Issued - Transaction #[ID] | Incorrect Ticket`
  - Body: "We've confirmed the ticket doesn't match the listing. Refund of $[AMOUNT] issued."
- **Email to Seller:**
  - Subject: `Warning - Transaction #[ID] | Incorrect Ticket Sent`  
  - Body: "You sent a ticket that doesn't match your listing. Buyer has been refunded. Please ensure accuracy in future listings."
- **Database:** `complaint - refunded buyer (wrong ticket)`

#### If Listing Was Unclear:
- **Action:** Partial refund ($10-20) to buyer for confusion
- **Email to Both:** Explain the miscommunication and resolution
- **Database:** `complaint - partial refund buyer`

---

### 4. **Ticket Won't Transfer**

**Scenario:** Ticket is stuck in seller's account and won't transfer

**Investigation Steps:**
1. Check if ticket is transferable on Michigan Athletics
2. Verify if there are transfer restrictions
3. Check if seller has other tickets they can send

**Resolution:**
- **Action:** Refund buyer immediately
- **Email to Buyer:**
  - Subject: `Refund Issued - Transaction #[ID] | Transfer Issue`
  - Body: "The ticket cannot be transferred due to Michigan Athletics restrictions. Full refund of $[AMOUNT] issued."
- **Email to Seller:**
  - Subject: `Transaction Cancelled - Transaction #[ID] | Transfer Restriction`
  - Body: "The ticket cannot be transferred. Buyer has been refunded. Your ticket has been returned to your account."
- **Database:** `complaint - refunded buyer (transfer restriction)`

---

### 5. **Payment Issues**

**Scenario:** Buyer claims they were double-charged or unauthorized charge

**Investigation Steps:**
1. Check Stripe transaction history
2. Verify payment completion timestamps
3. Look for duplicate transactions

**Resolution:**

#### If Double Charged:
- **Action:** Refund duplicate charge immediately
- **Email to Buyer:**
  - Subject: `Refund Processed - Transaction #[ID] | Duplicate Charge`
  - Body: "We've confirmed a duplicate charge and issued a full refund of $[AMOUNT]."
- **Database:** Create refund in Stripe, mark transaction as `resolved - duplicate charge refunded`

#### If Single Charge (Buyer Error):
- **Email to Buyer:**
  - Subject: `Transaction Verification - Transaction #[ID]`
  - Body: "Our records show a single charge of $[AMOUNT] on [DATE]. If this is unauthorized, please contact your bank and we'll provide supporting documentation."

---

### 6. **Event Cancelled**

**Scenario:** The event is cancelled/postponed and ticket is no longer valid

**Investigation Steps:**
1. Verify event cancellation with official sources
2. Check if Michigan Athletics is issuing refunds
3. Determine responsibility

**Resolution:**

#### If Event Officially Cancelled:
- **Action:** Full refund to buyer if they haven't attended yet
- **Email to Buyer & Seller:**
  - Subject: `Event Cancelled - Transaction #[ID] | Full Refund`
  - Body: "The [EVENT] has been officially cancelled. Buyer: Your payment of $[AMOUNT] will be refunded. Seller: Your ticket will be returned for Michigan Athletics refund."
- **Database:** `cancelled - event cancelled (refunded both parties)`
- **Note:** Work with Michigan Athletics to ensure seller gets their refund from original source

---

### 7. **Seller Never Got Paid**

**Scenario:** Seller transferred ticket but claims they weren't paid

**Investigation Steps:**
1. Check transaction status in database
2. Verify Stripe payment to seller
3. Check if event date has passed
4. Verify ticket was actually sent

**Resolution:**

#### If Payment Legitimately Missed:
- **Action:** Issue immediate payment to seller
- **Email to Seller:**
  - Subject: `Payment Issued - Transaction #[ID] | Payment Delay`
  - Body: "We apologize for the delay. Payment of $[AMOUNT] has been processed to your account."
- **Database:** Mark as `completed - late payment to seller`

#### If Waiting for Event to Pass:
- **Email to Seller:**
  - Subject: `Payment Schedule - Transaction #[ID]`
  - Body: "Payments are released after the event date ([DATE]). Your payment of $[AMOUNT] will be processed on [DATE]."

---

### 8. **Buyer Claims Didn't Receive Ticket (But They Did)**

**Scenario:** Buyer files false complaint after receiving valid ticket

**Investigation Steps:**
1. Check Michigan Athletics transfer logs
2. Verify ticket was received at buyer's account
3. Check if buyer attended the event
4. Get proof of transfer from seller

**Resolution:**
- **Action:** No refund - complaint denied
- **Email to Buyer:**
  - Subject: `Complaint Resolution - Transaction #[ID]`
  - Body: "Our investigation confirms the ticket was successfully transferred to your Michigan Athletics account on [DATE]. We have proof from both TicketVault and Michigan Athletics systems. Your complaint cannot be honored."
- **Email to Seller:**
  - Subject: `Complaint Resolved - Transaction #[ID] | In Your Favor`
  - Body: "The buyer's complaint has been investigated and denied. Your payment of $[AMOUNT] has been processed as scheduled."
- **Database:** `complaint - denied (false claim)`
- **Action:** Flag buyer account for suspicious activity

---

### 9. **Communication Issues**

**Scenario:** Buyer and seller having direct communication problems

**Investigation Steps:**
1. Review any messages if shared through platform
2. Determine if there's a legitimate issue

**Resolution:**
- **Action:** Mediate or escalate
- **Email to Both Parties:**
  - Subject: `Support Mediation - Transaction #[ID]`
  - Body: "We're here to help resolve any issues. Please communicate through support@safetransaction.app for mediation."
- **Note:** TicketVault discourages direct buyer-seller contact to prevent issues

---

### 10. **Ticket Forwarded to Wrong Account**

**Scenario:** Seller sent ticket to wrong Michigan Athletics email

**Investigation Steps:**
1. Verify which email ticket was sent to
2. Compare with buyer's Michigan Athletics email on file
3. Check if ticket can be retrieved

**Resolution:**

#### If Seller's Error:
- **Action:** Seller must retrieve and resend, or refund buyer
- **Email to Buyer:**
  - Subject: `Ticket Misdirected - Transaction #[ID] | Resolution in Progress`
  - Body: "The ticket was sent to the wrong account. We're working with the seller to correct this. If not resolved within 24 hours, full refund will be issued."
- **Email to Seller:**
  - Subject: `Action Required - Transaction #[ID] | Wrong Email`
  - Body: "You sent the ticket to [WRONG_EMAIL] instead of [CORRECT_EMAIL]. Please retrieve and resend immediately or buyer will be refunded."

#### If Buyer Provided Wrong Email:
- **Action:** Buyer responsible for retrieving ticket
- **Email to Buyer:**
  - Subject: `Ticket Transfer Issue - Transaction #[ID] | Email Verification`
  - Body: "The ticket was sent to the email you provided: [EMAIL]. Please verify this is your Michigan Athletics account. If incorrect, you'll need to contact Michigan Athletics to retrieve the ticket."

---

## Email Templates

### Standard Refund Email
```
Subject: Refund Processed - Transaction #[ID]

Dear [BUYER_NAME],

Your complaint regarding Transaction #[ID] has been reviewed and approved.

Transaction Details:
- Event: [EVENT_NAME]
- Price: $[AMOUNT]
- Transaction ID: #[ID]
- Complaint Filed: [DATE]

Resolution: Full refund issued
Refund Amount: $[AMOUNT]
Expected in Account: 3-5 business days

If you have any questions, please contact support@safetransaction.app.

Best regards,
TicketVault Support Team
```

### Seller Warning Email
```
Subject: Warning - Transaction #[ID] | Complaint Filed

Dear [SELLER_NAME],

A complaint has been filed against Transaction #[ID] and has been resolved in favor of the buyer.

Transaction Details:
- Event: [EVENT_NAME]
- Price: $[AMOUNT]
- Issue: [ISSUE_DESCRIPTION]

This incident has been noted on your account. Multiple complaints may result in account suspension.

To maintain good standing:
1. Always transfer tickets promptly
2. Ensure tickets match your listing
3. Verify buyer's Michigan Athletics email before sending

Questions? Contact support@safetransaction.app.

Best regards,
TicketVault Support Team
```

---

## Complaint Processing Workflow

1. **Receive Complaint** (support@safetransaction.app)
   - Log in admin dashboard
   - Document all details
   - Respond within 2 hours acknowledging receipt

2. **Investigation** (24-48 hours max)
   - Gather evidence from both parties
   - Check system logs
   - Verify with Michigan Athletics if needed
   - Review Stripe transaction history

3. **Decision**
   - Full refund buyer
   - Partial refund buyer  
   - Pay seller
   - Deny complaint
   - Other resolution

4. **Communication**
   - Email both parties with resolution
   - Update transaction status in database
   - Process refunds/payments through Stripe

5. **Follow-up**
   - Confirm resolution received
   - Update account flags if needed
   - Document for future reference

---

## Escalation Guidelines

**Escalate to Senior Support if:**
- Complaint value > $500
- Fraud suspected
- Legal threats made
- Pattern of similar complaints
- Unclear resolution path

**Contact:** [SENIOR_SUPPORT_EMAIL]

---

## Prevention Best Practices

1. **Clear Listing Requirements:** Enforce accurate event details
2. **Email Verification:** Require verified Michigan Athletics emails
3. **Proof of Transfer:** Sellers must confirm ticket sent
4. **Rapid Response:** Handle complaints within 48 hours
5. **Communication Logs:** Keep records of all interactions
6. **Automated Checks:** Verify ticket transfer through Michigan Athletics API (future)

---

## Metrics to Track

- Total complaints received
- Average resolution time
- Refund rate
- Seller complaint ratio
- Buyer false claim rate
- Most common complaint types

---

**Last Updated:** [DATE]  
**Contact:** support@safetransaction.app

