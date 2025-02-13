PRAGMA foreign_keys = ON;

INSERT INTO users(username, fullname, email, filename, password, bio)
VALUES 
    ('user1', 'Example User', 'sanjivp2703@gmail.com', 'blankuser.jpg', 'sha512$a45ffdcc71884853a2cba9e6bc55e812$c739cef1aec45c6e345c8463136dc1ae2fe19963106cf748baf87c7102937aa96928aa1db7fe1d8da6bd343428ff3167f4500c8a61095fb771957b4367868fb8', 'Hi, I am an example user to allow you to check out this platform!'),
    ('user2', 'Example User2', 'psanjiv@umich.edu', 'blankuser.jpg', 'sha512$a45ffdcc71884853a2cba9e6bc55e812$c739cef1aec45c6e345c8463136dc1ae2fe19963106cf748baf87c7102937aa96928aa1db7fe1d8da6bd343428ff3167f4500c8a61095fb771957b4367868fb8', 'Hi, I am an example user to allow you to check out this platform!');
