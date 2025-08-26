-- Migration to upgrade to automated transaction system
-- This safely migrates existing data to new schema

-- First, let's backup the old table structure (drop if exists)
DROP TABLE IF EXISTS transactions_backup;
CREATE TABLE transactions_backup AS SELECT * FROM transactions;

-- Add new columns to existing transactions table (if they don't exist)
-- Note: SQLite doesn't support ADD COLUMN IF NOT EXISTS, so we'll use a safer approach

-- Create new transactions table with full schema (drop if exists)
DROP TABLE IF EXISTS transactions_new;
CREATE TABLE transactions_new(
  transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
  buyer_email VARCHAR(40),
  seller_email VARCHAR(40),
  price INTEGER,
  event_id INTEGER,
  status VARCHAR(50) DEFAULT 'waiting_for_ticket',
  
  -- Timing controls
  created_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  ticket_deadline DATETIME,  -- When seller must send ticket by
  payment_deadline DATETIME, -- When buyer must pay by
  release_deadline DATETIME, -- When funds auto-release
  
  -- Ticket handling
  ticket_email_received BOOLEAN DEFAULT 0,
  ticket_received_time DATETIME,
  ticket_email_data TEXT, -- JSON of email content
  ticket_verification_score INTEGER DEFAULT 0,
  ticket_forwarded BOOLEAN DEFAULT 0,
  ticket_forwarded_time DATETIME,
  
  -- Payment handling  
  payment_received BOOLEAN DEFAULT 0,
  payment_intent_id VARCHAR(64),
  payment_received_time DATETIME,
  funds_released BOOLEAN DEFAULT 0,
  funds_released_time DATETIME,
  
  -- User actions
  buyer_confirmed_receipt BOOLEAN DEFAULT 0,
  buyer_confirmation_time DATETIME,
  complaint_reason VARCHAR(256),
  buyer_cancel_requested INTEGER DEFAULT 0,
  seller_cancel_requested INTEGER DEFAULT 0,
  
  -- Legacy columns for backward compatibility
  expected_ticket_send_time DATETIME,
  payment_processed_time DATETIME,

  FOREIGN KEY (buyer_email) REFERENCES users(email),
  FOREIGN KEY (seller_email) REFERENCES users(email),
  FOREIGN KEY (event_id) REFERENCES events(event_id),
  CHECK (status IN (
    'waiting_for_ticket', 
    'waiting_for_payment', 
    'both_received_processing', 
    'ticket_forwarded_funds_held',
    'completed',
    'expired_no_ticket',
    'expired_no_payment', 
    'cancelled_by_seller',
    'cancelled_by_buyer',
    'ticket_returned',
    'complaint_filed',
    'complaint_resolved_buyer',
    'complaint_resolved_seller',
    -- Legacy statuses for existing data
    'pending', 'rejected', 'waiting_for_payment_processing', 
    'waiting_for_ticket_transfer', 'ticket_sent', 'event_occurred', 
    'success', 'cancelled', 'complaint - refunded buyer', 'complaint - paid seller'
  ))
);

-- Migrate existing data with status mapping
INSERT INTO transactions_new (
  transaction_id, buyer_email, seller_email, price, event_id,
  status, created_time, complaint_reason, buyer_cancel_requested, 
  seller_cancel_requested, expected_ticket_send_time, payment_processed_time,
  -- Set defaults for new columns based on old status
  ticket_deadline, payment_deadline, 
  payment_received, funds_released, ticket_email_received
)
SELECT 
  transaction_id, buyer_email, seller_email, price, event_id,
  -- Map old statuses to new statuses
  CASE 
    WHEN status = 'pending' THEN 'waiting_for_ticket'
    WHEN status = 'waiting_for_payment_processing' THEN 'waiting_for_payment'
    WHEN status = 'waiting_for_ticket_transfer' THEN 'waiting_for_payment'
    WHEN status = 'ticket_sent' THEN 'ticket_forwarded_funds_held'
    WHEN status = 'success' THEN 'completed'
    WHEN status = 'cancelled' THEN 'cancelled_by_seller'
    WHEN status = 'complaint_filed' THEN 'complaint_filed'
    WHEN status = 'complaint - refunded buyer' THEN 'complaint_resolved_buyer'
    WHEN status = 'complaint - paid seller' THEN 'complaint_resolved_seller'
    ELSE status
  END as status,
  CURRENT_TIMESTAMP as created_time,  -- Use current time for all existing records
  complaint_reason, buyer_cancel_requested, seller_cancel_requested,
  expected_ticket_send_time, payment_processed_time,
  -- Set reasonable defaults for deadlines (24 hours from now)
  DATETIME(CURRENT_TIMESTAMP, '+24 hours') as ticket_deadline,
  DATETIME(CURRENT_TIMESTAMP, '+48 hours') as payment_deadline,
  -- Infer payment status from old statuses
  CASE WHEN status IN ('waiting_for_ticket_transfer', 'ticket_sent', 'success') THEN 1 ELSE 0 END as payment_received,
  CASE WHEN status = 'success' THEN 1 ELSE 0 END as funds_released,
  CASE WHEN status IN ('waiting_for_ticket_transfer', 'ticket_sent', 'success') THEN 1 ELSE 0 END as ticket_email_received
FROM transactions_backup;

-- Replace old table with new one
DROP TABLE transactions;
ALTER TABLE transactions_new RENAME TO transactions;

-- Create indexes for performance
CREATE INDEX idx_transactions_status ON transactions(status);
CREATE INDEX idx_transactions_deadlines ON transactions(ticket_deadline, payment_deadline, release_deadline);
CREATE INDEX idx_transactions_emails ON transactions(buyer_email, seller_email);

-- Update any existing monetary_transactions references if needed
-- (Keep this table as-is for accounting purposes)
