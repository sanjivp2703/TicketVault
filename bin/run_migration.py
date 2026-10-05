#!/usr/bin/env python3
"""
Run database migration to upgrade to automated system
"""

import sys
import os
import sqlite3
import pathlib

# Add parent directory to path
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))


def run_migration():
    """Run the database migration"""

    # Database path
    db_path = os.environ.get("INSTA485_DATABASE", "var/insta485.sqlite3")

    if not os.path.exists(db_path):
        print(f"❌ Database not found at {db_path}")
        return False

    print(f"📀 Running migration on database: {db_path}")

    # Read migration file
    migration_file = (
        pathlib.Path(__file__).parent.parent
        / "migrations"
        / "0004_automated_system_upgrade.sql"
    )

    if not migration_file.exists():
        print(f"❌ Migration file not found: {migration_file}")
        return False

    with open(migration_file, "r") as f:
        migration_sql = f.read()

    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row

        # Execute migration
        print("🔄 Backing up existing data...")
        print("🔄 Creating new schema...")
        print("🔄 Migrating existing transactions...")

        # Execute the migration (it's designed to be safe)
        conn.executescript(migration_sql)

        print("✅ Migration completed successfully!")

        # Verify migration worked
        cursor = conn.execute("SELECT COUNT(*) as count FROM transactions")
        count = cursor.fetchone()["count"]
        print(f"📊 Total transactions after migration: {count}")

        conn.close()
        return True

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False


if __name__ == "__main__":
    print("🗃️  Safe Transaction Database Migration")
    print("This will upgrade your database to support the new automated system")
    print()

    response = input("Do you want to proceed? (y/N): ").strip().lower()

    if response == "y" or response == "yes":
        success = run_migration()
        if success:
            print("\n🎉 Migration completed! You can now use the new automated system.")
        else:
            print("\n💥 Migration failed. Please check the errors above.")
            sys.exit(1)
    else:
        print("Migration cancelled.")
        sys.exit(0)
