DROP INDEX IF EXISTS email_idx;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL,
    password_hash TEXT NOT NULL
);

CREATE UNIQUE INDEX email_idx ON users(username);