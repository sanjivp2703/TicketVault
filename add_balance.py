#!/usr/bin/env python3
import sqlite3

# Connect to database
conn = sqlite3.connect('var/insta485.sqlite3')

# Add balance to test user
conn.execute('UPDATE users SET balance = 150.00 WHERE email = "awdeorio@umich.edu"')
conn.commit()

print("✓ Added $150.00 balance to awdeorio@umich.edu")
print("Now refresh your browser to see the Secure Withdrawal button!")

conn.close() 