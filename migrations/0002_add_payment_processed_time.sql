-- Add payment_processed_time column to transactions table
ALTER TABLE transactions ADD COLUMN payment_processed_time DATETIME;
