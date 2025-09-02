-- Add reminder tracking columns to transactions table
-- Migration: 0005_add_reminder_columns.sql

-- Add columns for tracking reminder emails
ALTER TABLE transactions ADD COLUMN reminder_sent_ticket BOOLEAN DEFAULT 0;
ALTER TABLE transactions ADD COLUMN reminder_sent_payment BOOLEAN DEFAULT 0;
ALTER TABLE transactions ADD COLUMN expired_time DATETIME;

-- Add index for deadline queries (performance optimization)
CREATE INDEX IF NOT EXISTS idx_transactions_ticket_deadline 
ON transactions(status, ticket_deadline) 
WHERE status = 'waiting_for_ticket';

CREATE INDEX IF NOT EXISTS idx_transactions_payment_deadline 
ON transactions(status, payment_deadline) 
WHERE status = 'waiting_for_payment';

-- Update existing transactions to have reminder flags
UPDATE transactions 
SET reminder_sent_ticket = 0, 
    reminder_sent_payment = 0 
WHERE reminder_sent_ticket IS NULL 
   OR reminder_sent_payment IS NULL;
