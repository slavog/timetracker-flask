CREATE TABLE IF NOT EXISTS users (
id integer PRIMARY KEY AUTOINCREMENT,
username text NOT NULL,
psw text NOT NULL,
time integer NOT NULL);

CREATE TABLE IF NOT EXISTS journal (
id integer NOT NULL,
hourly_rate integer NOT NULL,
name text NOT NULL,
fixed_time integer NOT NULL,
date text NOT NULL,
earnings integer NOT NULL);
