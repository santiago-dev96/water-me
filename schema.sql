DROP INDEX IF EXISTS email_idx;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS plants;

CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL,
    password_hash TEXT NOT NULL
);

CREATE UNIQUE INDEX email_idx ON users(username);

CREATE TABLE plants (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    name TEXT NOT NULL,
    picture_filename TEXT NOT NULL,
    times_it_was_watered INTEGER NOT NULL DEFAULT 0
);
