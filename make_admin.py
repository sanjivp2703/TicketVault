#!/usr/bin/env python3
"""
Script to make a user an admin.
Usage: python make_admin.py <email>
"""
import sqlite3
import sys

def make_admin(email):
    """Make a user an admin."""
    try:
        conn = sqlite3.connect('var/insta485.sqlite3')
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute("SELECT email, firstname, lastname FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        
        if not user:
            print(f"❌ User with email '{email}' not found.")
            return False
        
        # Make user admin
        cursor.execute("UPDATE users SET is_admin = 1 WHERE email = ?", (email,))
        conn.commit()
        
        print(f"✅ User '{user[1]} {user[2]}' ({email}) is now an admin!")
        print(f"🔗 Access admin dashboard at: http://localhost:8000/admin")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python make_admin.py <email>")
        print("Example: python make_admin.py admin@example.com")
        sys.exit(1)
    
    email = sys.argv[1]
    make_admin(email)
