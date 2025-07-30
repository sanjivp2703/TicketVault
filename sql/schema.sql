PRAGMA foreign_keys = ON;

CREATE TABLE users(
  email VARCHAR(40) NOT NULL,
  firstname VARCHAR(20) NOT NULL,
  lastname VARCHAR(20) NOT NULL,
  password VARCHAR(256) NOT NULL,
  stripe_id VARCHAR(64),
  is_admin BOOLEAN DEFAULT 0,
  balance INTEGER DEFAULT 0,
  created DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY(email)
);
CREATE TABLE events(
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(128) NOT NULL,
    location VARCHAR(256),
    event_datetime DATETIME
);

CREATE TABLE transactions(
  transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
  buyer_email VARCHAR(40),
  seller_email VARCHAR(40),
  price INTEGER,
  event_id INTEGER,
  status VARCHAR(30) DEFAULT 'pending',
  expected_ticket_send_time DATETIME,
  payment_processed_time DATETIME,
  complaint_reason VARCHAR(256),
  buyer_cancel_requested INTEGER DEFAULT 0,
  seller_cancel_requested INTEGER DEFAULT 0,

  FOREIGN KEY (buyer_email) REFERENCES users(email),
  FOREIGN KEY (seller_email) REFERENCES users(email),
  FOREIGN KEY (event_id) REFERENCES events(event_id),
  CHECK (status IN ('pending', 'rejected', 'waiting_for_payment_processing', 'waiting_for_ticket_transfer', 'ticket_sent', 'event_occurred', 'success', 'complaint_filed', 'cancelled', 'complaint - refunded buyer', 'complaint - paid seller'))
);

CREATE TABLE balance_transactions(
  transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_email VARCHAR(40) NOT NULL,
  transaction_id_ref INTEGER,
  withdrawal_id INTEGER,
  amount INTEGER NOT NULL,
  transaction_type VARCHAR(20) NOT NULL,
  description TEXT,
  created DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_email) REFERENCES users(email),
  FOREIGN KEY (transaction_id_ref) REFERENCES transactions(transaction_id),
  CHECK (transaction_type IN ("earning", "withdrawal"))
);
