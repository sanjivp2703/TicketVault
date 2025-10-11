-- Migration: Add school field to events and transactions tables
-- This field will store whether an event/listing is for Michigan or Florida

-- Add school column to events table (if not exists)
ALTER TABLE events ADD COLUMN school VARCHAR(50) DEFAULT 'michigan';

-- Add school column to transactions table (if not exists)
ALTER TABLE transactions ADD COLUMN school VARCHAR(50) DEFAULT 'michigan';

-- Update existing Michigan events
UPDATE events SET school = 'michigan' 
WHERE name LIKE '%Michigan%' OR location LIKE '%Ann Arbor%';

-- Update existing Florida events
UPDATE events SET school = 'florida' 
WHERE name LIKE '%Florida%' OR location LIKE '%Gainesville%';

-- Update transactions to inherit school from their associated event
UPDATE transactions 
SET school = (
    SELECT e.school 
    FROM events e 
    WHERE e.event_id = transactions.event_id
)
WHERE event_id IS NOT NULL;
