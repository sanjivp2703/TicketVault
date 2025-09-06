@echo off
echo Adding missing columns to database...

sqlite3 var/insta485.sqlite3 "ALTER TABLE users ADD COLUMN phone_number VARCHAR(20);" 2>nul
sqlite3 var/insta485.sqlite3 "ALTER TABLE users ADD COLUMN email_verified BOOLEAN DEFAULT 0;" 2>nul
sqlite3 var/insta485.sqlite3 "ALTER TABLE users ADD COLUMN phone_verified BOOLEAN DEFAULT 0;" 2>nul
sqlite3 var/insta485.sqlite3 "ALTER TABLE users ADD COLUMN last_login DATETIME;" 2>nul

sqlite3 var/insta485.sqlite3 "CREATE TABLE IF NOT EXISTS verification_codes(id INTEGER PRIMARY KEY AUTOINCREMENT, email VARCHAR(40) NOT NULL, code VARCHAR(6) NOT NULL, code_type VARCHAR(20) NOT NULL, expires_at DATETIME NOT NULL, used BOOLEAN DEFAULT 0, created_at DATETIME DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (email) REFERENCES users(email));" 2>nul

echo Database columns added successfully!
echo You can now enable verification features.
pause
