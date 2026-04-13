"""
document_model.py - SQLite database model for document management
"""

import sqlite3
from config import Config


def get_db_connection():
    """Create and return a database connection with row factory."""
    conn = sqlite3.connect(Config.DATABASE)
    conn.row_factory = sqlite3.Row  # Allows dict-like row access
    return conn


def init_db():
    """Initialize the database and create tables if they don't exist."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create documents table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_name TEXT NOT NULL,
            stored_name TEXT NOT NULL,
            file_type TEXT NOT NULL,
            converted_name TEXT,
            size INTEGER,
            status TEXT DEFAULT 'uploaded',
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create merged_documents table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS merged_documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            merged_name TEXT NOT NULL,
            source_ids TEXT NOT NULL,
            size INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()
    print("Database initialized successfully.")


def insert_document(original_name, stored_name, file_type, size):
    """Insert a new uploaded document record into the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO documents (original_name, stored_name, file_type, size, status)
        VALUES (?, ?, ?, ?, 'uploaded')
    ''', (original_name, stored_name, file_type, size))
    doc_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return doc_id


def update_document_converted(doc_id, converted_name):
    """Update a document record with its converted PDF name."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE documents SET converted_name = ?, status = 'converted'
        WHERE id = ?
    ''', (converted_name, doc_id))
    conn.commit()
    conn.close()


def get_all_documents():
    """Retrieve all uploaded documents from the database."""
    conn = get_db_connection()
    rows = conn.execute('SELECT * FROM documents ORDER BY uploaded_at DESC').fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_document_by_id(doc_id):
    """Retrieve a single document by its ID."""
    conn = get_db_connection()
    row = conn.execute('SELECT * FROM documents WHERE id = ?', (doc_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def insert_merged_document(merged_name, source_ids, size):
    """Insert a merged document record into the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    source_str = ','.join(str(i) for i in source_ids)
    cursor.execute('''
        INSERT INTO merged_documents (merged_name, source_ids, size)
        VALUES (?, ?, ?)
    ''', (merged_name, source_str, size))
    merged_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return merged_id


def get_all_merged_documents():
    """Retrieve all merged documents from the database."""
    conn = get_db_connection()
    rows = conn.execute('SELECT * FROM merged_documents ORDER BY created_at DESC').fetchall()
    conn.close()
    return [dict(row) for row in rows]


def delete_document(doc_id):
    """Delete a document record from the database."""
    conn = get_db_connection()
    conn.execute('DELETE FROM documents WHERE id = ?', (doc_id,))
    conn.commit()
    conn.close()
