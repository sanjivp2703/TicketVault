PRAGMA foreign_keys = ON;

CREATE TABLE users(
  email VARCHAR(40) NOT NULL,
  firstname VARCHAR(20) NOT NULL,
  lastname VARCHAR(20) NOT NULL,
  password VARCHAR(256) NOT NULL,
  phone_number VARCHAR(20),
  stripe_id VARCHAR(64),
  is_admin BOOLEAN DEFAULT 0,
  balance INTEGER DEFAULT 0,
  email_verified BOOLEAN DEFAULT 0,
  phone_verified BOOLEAN DEFAULT 0,
  verification_code VARCHAR(6),
  verification_code_expires DATETIME,
  last_login DATETIME,
  created DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY(email)
);
CREATE TABLE events(
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(128) NOT NULL,
    location VARCHAR(256),
    event_datetime DATETIME,
    is_tbd BOOLEAN DEFAULT 0,
    max_ticket_price INTEGER DEFAULT 20000,
    school VARCHAR(50) DEFAULT 'michigan'
);

CREATE TABLE transactions(
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
  
  -- Pending flow columns
  listing_created_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  awaiting_ticket_email TEXT, -- The email address seller should send to
  original_event_details TEXT, -- JSON of what seller entered
  ticket_details_match INTEGER DEFAULT 0, -- 1 if verified details match
  verification_notes TEXT, -- Details about verification
  
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
  
  -- Reminder tracking
  ticket_reminder_sent_2h INTEGER DEFAULT 0,
  ticket_reminder_sent_30m INTEGER DEFAULT 0,
  ticket_reminder_sent_5m INTEGER DEFAULT 0,
  payment_reminder_sent_4h INTEGER DEFAULT 0,
  payment_reminder_sent_1h INTEGER DEFAULT 0,
  
  -- School association
  school VARCHAR(50) DEFAULT 'michigan',

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
    'pending_ticket_submission'
  ))
);

CREATE TABLE verification_codes(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email VARCHAR(40) NOT NULL,
  code VARCHAR(6) NOT NULL,
  code_type VARCHAR(20) NOT NULL, -- 'email_verification', 'phone_verification', 'password_reset'
  expires_at DATETIME NOT NULL,
  used BOOLEAN DEFAULT 0,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (email) REFERENCES users(email)
);

CREATE TABLE monetary_transactions(
  transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
  sender VARCHAR(40) NOT NULL,
  recipient VARCHAR(40) NOT NULL,
  transaction_id_ref INTEGER,
  amount INTEGER NOT NULL,
  transaction_type VARCHAR(20) NOT NULL,
  created DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (transaction_id_ref) REFERENCES transactions(transaction_id),
  FOREIGN KEY (sender) REFERENCES users(email),
  FOREIGN KEY (recipient) REFERENCES users(email),
  CHECK (transaction_type IN ("purchase", "refund", "withdrawal"))
  -- Using sanjivp2703@gmail.com as the company account for transactions
);

CREATE TABLE balance_changes(
  change_id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_email VARCHAR(40) NOT NULL,
  amount INTEGER NOT NULL,
  change_type VARCHAR(20) NOT NULL,
  transaction_id_ref INTEGER,
  created DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_email) REFERENCES users(email),
  FOREIGN KEY (transaction_id_ref) REFERENCES transactions(transaction_id),
  CHECK (change_type IN ("earning", "withdrawal"))
);
