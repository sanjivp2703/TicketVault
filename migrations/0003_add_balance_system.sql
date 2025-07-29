-- Migration: Add seller balance and withdrawal system
PRAGMA foreign_keys = ON;

-- Add balance column to users table
ALTER TABLE users ADD COLUMN balance INTEGER DEFAULT 0;

-- Create withdrawals table for tracking withdrawal requests
CREATE TABLE withdrawals(
  withdrawal_id INTEGER PRIMARY KEY AUTOINCREMENT,
  seller_email VARCHAR(40) NOT NULL,
  amount INTEGER NOT NULL,
  status VARCHAR(20) DEFAULT 'pending',
  bank_account_last_four VARCHAR(4),
  routing_number_last_four VARCHAR(4),
  bank_name VARCHAR(100),
  requested_date DATETIME DEFAULT CURRENT_TIMESTAMP,
  processed_date DATETIME,
  admin_notes VARCHAR(500),
  
  FOREIGN KEY (seller_email) REFERENCES users(email),
  CHECK (status IN ('pending', 'processing', 'completed', 'failed', 'cancelled')),
  CHECK (amount > 0)
);

-- Create balance_transactions table for tracking all balance changes
CREATE TABLE balance_transactions(
  balance_transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_email VARCHAR(40) NOT NULL,
  transaction_id INTEGER,
  withdrawal_id INTEGER,
  amount INTEGER NOT NULL,
  transaction_type VARCHAR(20) NOT NULL,
  description VARCHAR(200),
  created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
  
  FOREIGN KEY (user_email) REFERENCES users(email),
  FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id),
  FOREIGN KEY (withdrawal_id) REFERENCES withdrawals(withdrawal_id),
  CHECK (transaction_type IN ('earning', 'withdrawal', 'refund', 'fee', 'adjustment'))
);

-- Add some initial sample data for testing
-- Update existing users to have some balance
UPDATE users SET balance = 0 WHERE email IN ('user1@gmail.com', 'user2@gmail.com', 'sanjivp2703@gmail.com'); 