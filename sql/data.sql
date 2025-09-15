PRAGMA foreign_keys = ON;

INSERT INTO events (name, location, event_datetime) VALUES
('Taylor Swift Concert', 'Levi''s Stadium', '2025-08-15 20:00:00'),
('Michigan Football Game', 'Michigan Stadium', '2025-11-29 12:00:00'),
('Lollapalooza', 'Grant Park, Chicago', '2025-08-01 11:00:00'),
('Hamilton Musical', 'Richard Rodgers Theatre, NYC', '2025-09-20 19:30:00');

INSERT INTO users(email, firstname, lastname, password, stripe_id, is_admin, balance)
VALUES 
    ('user1@gmail.com', 'Example', 'User', 'sha512$a45ffdcc71884853a2cba9e6bc55e812$c739cef1aec45c6e345c8463136dc1ae2fe19963106cf748baf87c7102937aa96928aa1db7fe1d8da6bd343428ff3167f4500c8a61095fb771957b4367868fb8', 'acct_1RlZSp2E8dXCmKk8', 0, 0),
    ('admin@gmail.com', 'Admin', 'User', 'sha512$a45ffdcc71884853a2cba9e6bc55e812$c739cef1aec45c6e345c8463136dc1ae2fe19963106cf748baf87c7102937aa96928aa1db7fe1d8da6bd343428ff3167f4500c8a61095fb771957b4367868fb8', 'acct_1RlZSp2E8dXCmKk8', 1, 0),
    ('sanjivp2703@gmail.com', 'Sanjiv', 'Parthasarathy', 'sha512$a45ffdcc71884853a2cba9e6bc55e812$c739cef1aec45c6e345c8463136dc1ae2fe19963106cf748baf87c7102937aa96928aa1db7fe1d8da6bd343428ff3167f4500c8a61095fb771957b4367868fb8', 'acct_1RlZSp2E8dXCmKk8', 0, 0);
