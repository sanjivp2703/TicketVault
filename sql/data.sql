PRAGMA foreign_keys = ON;

-- Michigan Football Events (Ann Arbor, MI)
INSERT INTO events (name, location, event_datetime, is_tbd, max_ticket_price, school) VALUES
('Wisconsin vs Michigan', 'Ann Arbor, MI', '2025-10-04 00:00:00', 1, 20000, 'michigan'),
('Washington vs Michigan', 'Ann Arbor, MI', '2025-10-18 00:00:00', 1, 20000, 'michigan'),
('Purdue vs Michigan', 'Ann Arbor, MI', '2025-11-01 00:00:00', 1, 20000, 'michigan'),
('Ohio vs Michigan', 'Ann Arbor, MI', '2025-11-29 00:00:00', 1, 60000, 'michigan'),

-- Florida Football Events (Gainesville, FL)
('Texas vs Florida', 'Gainesville, FL', '2025-10-04 00:00:00', 1, 20000, 'florida'),
('Mississippi State vs Florida', 'Gainesville, FL', '2025-10-18 00:00:00', 1, 20000, 'florida'),
('Georgia vs Florida', 'Gainesville, FL', '2025-11-01 15:30:00', 0, 20000, 'florida'),
('Kentucky vs Florida', 'Gainesville, FL', '2025-11-08 00:00:00', 1, 20000, 'florida'),
('Tennessee vs Florida', 'Gainesville, FL', '2025-11-22 00:00:00', 1, 20000, 'florida'),
('Florida State vs Florida', 'Gainesville, FL', '2025-11-29 00:00:00', 1, 20000, 'florida');

INSERT INTO users(email, firstname, lastname, password, stripe_id, is_admin, balance)
VALUES 
    ('user1@gmail.com', 'Example', 'User', 'sha512$a45ffdcc71884853a2cba9e6bc55e812$c739cef1aec45c6e345c8463136dc1ae2fe19963106cf748baf87c7102937aa96928aa1db7fe1d8da6bd343428ff3167f4500c8a61095fb771957b4367868fb8', 'acct_1RlZSp2E8dXCmKk8', 0, 0),
    ('admin@gmail.com', 'Admin', 'User', 'sha512$a45ffdcc71884853a2cba9e6bc55e812$c739cef1aec45c6e345c8463136dc1ae2fe19963106cf748baf87c7102937aa96928aa1db7fe1d8da6bd343428ff3167f4500c8a61095fb771957b4367868fb8', 'acct_1RlZSp2E8dXCmKk8', 1, 0),
    ('sanjivp2703@gmail.com', 'Sanjiv', 'Parthasarathy', 'sha512$a45ffdcc71884853a2cba9e6bc55e812$c739cef1aec45c6e345c8463136dc1ae2fe19963106cf748baf87c7102937aa96928aa1db7fe1d8da6bd343428ff3167f4500c8a61095fb771957b4367868fb8', 'acct_1RlZSp2E8dXCmKk8', 0, 0);
