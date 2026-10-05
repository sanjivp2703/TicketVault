# Production Deployment Guide - School Column Fix

## Problem Fixed
- Error: "table transactions has no column named school" when creating tickets
- Events were filtered by name pattern instead of using a proper school column
- Users can now properly select Michigan or Florida and see respective games

## Changes Made

### 1. Database Schema Updates
- Added `school` column to `events` table (VARCHAR(50), default: 'michigan')
- Added `school` column to `transactions` table (VARCHAR(50), default: 'michigan')
- Updated sample data to include school for all events

### 2. Code Updates
- Updated `/api/events` endpoint to filter by `school` column instead of name patterns
- Transaction manager already supported school parameter

### 3. Migration File
- `migrations/0010_add_school_field.sql` - Adds columns and updates existing data

## Deployment Steps for Production Server

### Step 1: SSH into Production Server
```bash
ssh vedav@35.222.52.124
# Or however you connect to your server
```

### Step 2: Navigate to Application Directory
```bash
cd /var/www/safetransaction
```

### Step 3: Pull Latest Code from GitHub
```bash
# Use your new GitHub token
git pull origin main
# If prompted for credentials, use:
# Username: your-github-username
# Password: <GITHUB_TOKEN>
```

### Step 4: Run the Migration
```bash
# Backup the database first (IMPORTANT!)
sudo cp var/insta485.sqlite3 var/insta485.sqlite3.backup_$(date +%Y%m%d_%H%M%S)

# Run the migration
sudo sqlite3 var/insta485.sqlite3 < migrations/0010_add_school_field.sql

# Verify the migration
sudo sqlite3 var/insta485.sqlite3 "PRAGMA table_info(events);" | grep school
sudo sqlite3 var/insta485.sqlite3 "PRAGMA table_info(transactions);" | grep school
```

### Step 5: Restart the Application
```bash
# If using systemd service
sudo systemctl restart safetransaction

# Or if using supervisor
sudo supervisorctl restart safetransaction

# Or kill and restart the process manually
sudo pkill -f "python.*insta485"
# Then start it again however you normally do
```

### Step 6: Test the Fix
1. Go to https://safetransaction.app
2. Try creating a listing
3. Toggle between Michigan and Florida schools
4. Verify that:
   - Michigan shows only Michigan games
   - Florida shows only Florida games
   - Creating a listing works without errors

## Rollback Plan (If Something Goes Wrong)

```bash
# Stop the application
sudo systemctl stop safetransaction  # or your method

# Restore the backup
sudo cp var/insta485.sqlite3.backup_YYYYMMDD_HHMMSS var/insta485.sqlite3

# Restart the application
sudo systemctl start safetransaction
```

## Files Changed
- `sql/schema.sql` - Added school column to events and transactions
- `sql/data.sql` - Added school values to event inserts
- `insta485/views/index.py` - Updated event filtering to use school column
- `migrations/0010_add_school_field.sql` - Migration script

## Notes
- All existing events will be automatically categorized as Michigan or Florida based on their names/locations
- Any existing transactions will default to 'michigan' school
- The migration is safe and preserves all existing data
- No user data will be lost

## Support
If you encounter any issues during deployment:
1. Check the application logs: `sudo journalctl -u safetransaction -n 100`
2. Check for database errors: `sudo tail -f /var/www/safetransaction/var/log/database.log`
3. Verify database integrity: `sudo sqlite3 var/insta485.sqlite3 "PRAGMA integrity_check;"`

