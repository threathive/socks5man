CREATE TABLE IF NOT EXISTS server (
    server_id TEXT PRIMARY KEY NOT NULL,
    ip TEXT NOT NULL,
    port INT NOT NULL,
    username TEXT,
    password TEXT,
    country TEXT,
    last_checked INT NOT NULL,
    last_used INT NOT NULL,
    active INT NOT NULL
)
