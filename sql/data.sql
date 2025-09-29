PRAGMA foreign_keys = ON;

-- Michigan Football Events (Ann Arbor, MI)
INSERT INTO events (name, location, event_datetime, is_tbd, max_ticket_price) VALUES
('Wisconsin vs Michigan', 'Ann Arbor, MI', '2024-10-04 00:00:00', 1, 20000),
('Washington vs Michigan', 'Ann Arbor, MI', '2024-10-18 00:00:00', 1, 20000),
('Purdue vs Michigan', 'Ann Arbor, MI', '2024-11-01 00:00:00', 1, 20000),
('Ohio vs Michigan', 'Ann Arbor, MI', '2024-11-29 00:00:00', 1, 60000),

-- Florida Football Events (Gainesville, FL)
('Texas vs Florida', 'Gainesville, FL', '2024-10-04 00:00:00', 1, 20000),
('Mississippi State vs Florida', 'Gainesville, FL', '2024-10-18 00:00:00', 1, 20000),
('Georgia vs Florida', 'Gainesville, FL', '2024-11-01 15:30:00', 0, 20000),
('Kentucky vs Florida', 'Gainesville, FL', '2024-11-08 00:00:00', 1, 20000),
('Tennessee vs Florida', 'Gainesville, FL', '2024-11-22 00:00:00', 1, 20000),
('Florida State vs Florida', 'Gainesville, FL', '2024-11-29 00:00:00', 1, 20000);

INSERT INTO users(email, firstname, lastname, password, stripe_id, is_admin, balance)
VALUES 
    ('user1@gmail.com', 'Example', 'User', 'sha512$a45ffdcc71884853a2cba9e6bc55e812$c739cef1aec45c6e345c8463136dc1ae2fe19963106cf748baf87c7102937aa96928aa1db7fe1d8da6bd343428ff3167f4500c8a61095fb771957b4367868fb8', 'acct_1RlZSp2E8dXCmKk8', 0, 0),
    ('admin@gmail.com', 'Admin', 'User', 'sha512$a45ffdcc71884853a2cba9e6bc55e812$c739cef1aec45c6e345c8463136dc1ae2fe19963106cf748baf87c7102937aa96928aa1db7fe1d8da6bd343428ff3167f4500c8a61095fb771957b4367868fb8', 'acct_1RlZSp2E8dXCmKk8', 1, 0),
    ('sanjivp2703@gmail.com', 'Sanjiv', 'Parthasarathy', 'sha512$a45ffdcc71884853a2cba9e6bc55e812$c739cef1aec45c6e345c8463136dc1ae2fe19963106cf748baf87c7102937aa96928aa1db7fe1d8da6bd343428ff3167f4500c8a61095fb771957b4367868fb8', 'acct_1RlZSp2E8dXCmKk8', 0, 0);
