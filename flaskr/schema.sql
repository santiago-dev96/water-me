DROP INDEX IF EXISTS username_idx;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS cultivation_plots;

CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL,
    password_hash TEXT NOT NULL
);

CREATE UNIQUE INDEX username_idx ON users(username);

CREATE TABLE cultivation_plots (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    name TEXT NOT NULL,
    crop TEXT NOT NULL,
    number_of_plants INTEGER NOT NULL DEFAULT 0,
    water_spent REAL NOT NULL DEFAULT 0,
    harvest REAL NOT NULL DEFAULT 0
);
