PRAGMA foreign_keys = ON;

CREATE TABLE users(
  username VARCHAR(20) NOT NULL,
  fullname VARCHAR(40) NOT NULL,
  email VARCHAR(40),
  bio VARCHAR(40) NOT NULL,
  filename VARCHAR(64),
  password VARCHAR(256),
  created DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY(username)
);
CREATE TABLE transactions(
  transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
  sender_username VARCHAR(20),
  receiver_username VARCHAR(20),
  amount INTEGER,
  status VARCHAR(20) NOT NULL,
  FOREIGN KEY (sender_username) REFERENCES users(username),
  FOREIGN KEY (receiver_username) REFERENCES users(username)
);
