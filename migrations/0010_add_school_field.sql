-- Migration: Add school field to transactions table
-- This field will store whether a listing is for Michigan or Florida events

ALTER TABLE transactions ADD COLUMN school VARCHAR(20) DEFAULT 'michigan';

-- Update check constraint to include school validation
-- Note: SQLite doesn't support modifying constraints directly, 
-- but we can add a separate check for the school field
