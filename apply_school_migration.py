#!/usr/bin/env python3
"""
Apply the school field migration to the database
"""
import sqlite3
import os

def apply_migration():
    """Apply the school field migration"""
    
    # Path to the database
    db_path = 'var/insta485.sqlite3'
    
    if not os.path.exists(db_path):
        print("❌ Database not found at var/insta485.sqlite3")
        return False
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if school column already exists
        cursor.execute("PRAGMA table_info(transactions)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'school' in columns:
            print("✅ School column already exists in transactions table")
            return True
            
        # Apply migration
        print("📊 Adding school column to transactions table...")
        cursor.execute("ALTER TABLE transactions ADD COLUMN school VARCHAR(20) DEFAULT 'michigan'")
        
        # Commit changes
        conn.commit()
        conn.close()
        
        print("✅ Migration applied successfully!")
        print("   - Added 'school' column to transactions table")
        print("   - Default value: 'michigan'")
        return True
        
    except Exception as e:
        print(f"❌ Error applying migration: {e}")
        return False

if __name__ == "__main__":
    apply_migration()
