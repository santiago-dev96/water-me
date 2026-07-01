DROP INDEX IF EXISTS username_idx;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS operations;
DROP TABLE IF EXISTS cultivation_plots;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    created_at INTEGER DEFAULT CURRENT_TIMESTAMP,
    updated_at INTEGER
);

CREATE UNIQUE INDEX username_idx ON users(username);

CREATE TABLE cultivation_plots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    name TEXT NOT NULL,
    crop TEXT NOT NULL,
    number_of_plants INTEGER NOT NULL DEFAULT 0,
    water_spent REAL NOT NULL DEFAULT 0,
    harvest REAL NOT NULL DEFAULT 0,
    created_at INTEGER DEFAULT CURRENT_TIMESTAMP,
    updated_at INTEGER,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE operations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cultivation_plot_id INTEGER,
    number_of_plants INTEGER NOT NULL,
    water_spent REAL NOT NULL,
    harvest REAL NOT NULL,
    created_at INTEGER DEFAULT CURRENT_TIMESTAMP,
    updated_at INTEGER,
    FOREIGN KEY (cultivation_plot_id) REFERENCES cultivation_plots(id) ON DELETE CASCADE
);
