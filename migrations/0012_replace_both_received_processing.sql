-- Migration: Replace both_received_processing with waiting_for_payment_processing
-- This migration renames the obsolete both_received_processing status to the clearer
-- waiting_for_payment_processing status

-- Update any existing transactions using the old status
UPDATE transactions 
SET status = 'waiting_for_payment_processing' 
WHERE status = 'both_received_processing';

-- Note: The schema CHECK constraint will be updated when you recreate the database
-- This script only handles data migration for existing transactions

