"""models/db.py — SQLite database initialisation and helpers"""
import sqlite3, json
from config import Config


def get_conn():
    conn = sqlite3.connect(Config.DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables if they don't exist."""
    conn = get_conn()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS operations (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            tool        TEXT    NOT NULL,
            input_files TEXT,
            output_files TEXT,
            created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
    print("[DB] Initialized.")


def log_operation(tool, input_files, output_files):
    """Record a completed operation in the database."""
    conn = get_conn()
    conn.execute(
        'INSERT INTO operations (tool, input_files, output_files) VALUES (?, ?, ?)',
        (tool, json.dumps(input_files), json.dumps(output_files))
    )
    conn.commit()
    conn.close()


def get_history(limit=50):
    """Return recent operations."""
    conn = get_conn()
    rows = conn.execute(
        'SELECT * FROM operations ORDER BY created_at DESC LIMIT ?', (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
