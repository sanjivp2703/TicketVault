-- Add phone number and verification features to users table
ALTER TABLE users ADD COLUMN phone_number VARCHAR(20);
ALTER TABLE users ADD COLUMN email_verified BOOLEAN DEFAULT 0;
ALTER TABLE users ADD COLUMN phone_verified BOOLEAN DEFAULT 0;
ALTER TABLE users ADD COLUMN verification_code VARCHAR(6);
ALTER TABLE users ADD COLUMN verification_code_expires DATETIME;
ALTER TABLE users ADD COLUMN last_login DATETIME;

-- Create verification codes table for better tracking
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
