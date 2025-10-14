-- Migration: Add waiting_for_verification status
-- This migration adds the new waiting_for_verification status to the schema
-- and updates any existing transactions that are in waiting_for_ticket status
-- (if they have ticket_email_received = 1, meaning seller confirmed sending)

-- Note: The schema constraint will be automatically updated when you recreate the database
-- This script just handles data migration for existing transactions

-- Update transactions that are waiting_for_ticket with ticket received to waiting_for_verification
UPDATE transactions 
SET status = 'waiting_for_verification' 
WHERE status = 'waiting_for_ticket' 
AND ticket_email_received = 1;

-- Leave any transactions that are waiting_for_ticket without ticket_email_received as is
-- (they are genuinely waiting for the ticket to be sent)

