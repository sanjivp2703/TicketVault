-- Migration to restructure for pending ticket flow
-- Date: 2024

-- First backup existing data
DROP TABLE IF EXISTS transactions_backup;
CREATE TABLE transactions_backup AS SELECT * FROM transactions;

-- Add new columns for pending flow
ALTER TABLE transactions ADD COLUMN listing_created_time DATETIME DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE transactions ADD COLUMN awaiting_ticket_email TEXT; -- The email address seller should send to
ALTER TABLE transactions ADD COLUMN original_event_details TEXT; -- JSON of what seller entered
ALTER TABLE transactions ADD COLUMN ticket_details_match INTEGER DEFAULT 0; -- 1 if verified details match
ALTER TABLE transactions ADD COLUMN verification_notes TEXT; -- Details about verification

-- Update status constraints to include new states
-- Drop existing constraint and recreate with new states
CREATE TABLE transactions_new (
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    seller_email VARCHAR(255) NOT NULL,
    buyer_email VARCHAR(255) NOT NULL,
    event_id INTEGER,
    price DECIMAL(10,2) NOT NULL,
    listing_created_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    awaiting_ticket_email TEXT,
    original_event_details TEXT,
    ticket_details_match INTEGER DEFAULT 0,
    verification_notes TEXT,
    
    -- Existing timing columns
    created_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    ticket_deadline DATETIME,
    payment_deadline DATETIME,
    release_deadline DATETIME,
    
    -- Email and verification columns
    ticket_email_received INTEGER DEFAULT 0,
    ticket_received_time DATETIME,
    ticket_email_data TEXT,
    ticket_verification_score INTEGER DEFAULT 0,
    ticket_forwarded INTEGER DEFAULT 0,
    ticket_forwarded_time DATETIME,
    
    -- Payment columns
    payment_received INTEGER DEFAULT 0,
    payment_intent_id VARCHAR(255),
    payment_received_time DATETIME,
    funds_released INTEGER DEFAULT 0,
    funds_released_time DATETIME,
    
    -- Buyer confirmation
    buyer_confirmed_receipt INTEGER DEFAULT 0,
    buyer_confirmation_time DATETIME,
    
    -- Status tracking
    status VARCHAR(50) DEFAULT 'pending_ticket_submission' CHECK (status IN (
        'pending_ticket_submission',    -- NEW: Waiting for seller to send ticket
        'waiting_for_ticket',
        'waiting_for_payment', 
        'both_received_processing',
        'ticket_forwarded_funds_held',
        'expired_no_ticket',
        'expired_no_payment', 
        'cancelled_by_seller',
        'cancelled_by_buyer',
        'ticket_returned',
        'complaint_filed',
        'complaint_resolved_buyer',
        'complaint_resolved_seller',
        'completed'
    )),
    
    -- Reminder tracking
    ticket_reminder_sent_2h INTEGER DEFAULT 0,
    ticket_reminder_sent_30m INTEGER DEFAULT 0,
    ticket_reminder_sent_5m INTEGER DEFAULT 0,
    payment_reminder_sent_4h INTEGER DEFAULT 0,
    payment_reminder_sent_1h INTEGER DEFAULT 0,
    
    FOREIGN KEY (event_id) REFERENCES events (event_id)
);

-- Copy data from old table to new structure (only columns that exist)
INSERT INTO transactions_new (
    transaction_id, seller_email, buyer_email, event_id, price,
    status
)
SELECT 
    transaction_id, seller_email, buyer_email, event_id, price,
    COALESCE(status, 'pending_ticket_submission')
FROM transactions;

-- Replace old table with new structure
DROP TABLE transactions;
ALTER TABLE transactions_new RENAME TO transactions;

-- Update existing pending transactions to new flow
UPDATE transactions 
SET status = 'pending_ticket_submission',
    listing_created_time = created_time,
    awaiting_ticket_email = 'tx-' || printf('%06d', transaction_id) || '@safetransaction.com'
WHERE status = 'waiting_for_ticket';

COMMIT;
