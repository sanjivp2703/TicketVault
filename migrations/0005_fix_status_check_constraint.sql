-- Migration to fix CHECK constraint for transaction status
-- Add missing status values that are used in the code

PRAGMA foreign_keys = OFF;

-- Create temporary table with updated CHECK constraint
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
    'validated',
    'rejected',
    'waiting_for_payment_processing',
    'cancelled',
    'complaint - refunded buyer',
    'complaint - paid seller',
    'complete'
  ))
);

-- Copy data from old table to new table
INSERT INTO transactions_new SELECT * FROM transactions;

-- Drop old table
DROP TABLE transactions;

-- Rename new table to original name
ALTER TABLE transactions_new RENAME TO transactions;

PRAGMA foreign_keys = ON;
