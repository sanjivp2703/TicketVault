-- Migration: Add withdrawal_requests table for tracking withdrawal requests
-- This allows manual processing of withdrawals and keeps audit trail

CREATE TABLE IF NOT EXISTS withdrawal_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_email TEXT NOT NULL,
    amount INTEGER NOT NULL,  -- Amount in cents (before fee)
    fee_amount INTEGER NOT NULL,  -- 5% fee in cents
    transfer_amount INTEGER NOT NULL,  -- Actual transfer amount (after fee) in cents
    bank_name TEXT NOT NULL,
    routing_number TEXT NOT NULL,
    account_number_last4 TEXT NOT NULL,  -- Only store last 4 digits for security
    status TEXT NOT NULL DEFAULT 'pending',  -- pending, completed, failed, cancelled
    stripe_transfer_id TEXT,  -- Stripe Transfer ID if automated
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    notes TEXT,  -- Admin notes
    FOREIGN KEY (user_email) REFERENCES users(email)
);

CREATE INDEX IF NOT EXISTS idx_withdrawal_requests_user_email ON withdrawal_requests(user_email);
CREATE INDEX IF NOT EXISTS idx_withdrawal_requests_status ON withdrawal_requests(status);
CREATE INDEX IF NOT EXISTS idx_withdrawal_requests_created_at ON withdrawal_requests(created_at);

