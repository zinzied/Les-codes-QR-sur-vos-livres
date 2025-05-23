import sqlite3
import io
from PIL import Image

def get_connection():
    conn = sqlite3.connect('books.db')
    c = conn.cursor()
    return conn, c

def initialize_database():
    conn, c = get_connection()

    # Check if the books table exists
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='books'")
    table_exists = c.fetchone()

    if table_exists:
        # Check if the table has the new columns
        c.execute("PRAGMA table_info(books)")
        columns = [column[1] for column in c.fetchall()]

        # If the table exists but doesn't have the new columns, alter the table
        if 'description' not in columns:
            try:
                c.execute('ALTER TABLE books ADD COLUMN description TEXT')
            except:
                pass  # Column might already exist

        if 'category' not in columns:
            try:
                c.execute('ALTER TABLE books ADD COLUMN category TEXT')
            except:
                pass  # Column might already exist
    else:
        # Create a table to store book names, year, author, and QR codes
        c.execute('''
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                year INTEGER NOT NULL,
                author TEXT NOT NULL,
                description TEXT,
                category TEXT,
                qr_code BLOB NOT NULL
            )
        ''')

    # Create a table to store user preferences
    c.execute('''
        CREATE TABLE IF NOT EXISTS preferences (
            id INTEGER PRIMARY KEY,
            key TEXT UNIQUE NOT NULL,
            value TEXT NOT NULL
        )
    ''')

    # Initialize default preferences if they don't exist
    c.execute('INSERT OR IGNORE INTO preferences (key, value) VALUES (?, ?)', ('dark_mode', 'false'))

    conn.commit()
    conn.close()

def save_book(book_name, year, author, qr_code_data, description=None, category=None):
    conn, c = get_connection()
    # Insert book name, year, author, description, category, and QR code into the database
    c.execute('''
        INSERT INTO books (name, year, author, description, category, qr_code)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (book_name, year, author, description, category, qr_code_data))
    conn.commit()
    conn.close()

def search_book(book_name):
    conn, c = get_connection()
    # Search for the book in the database
    c.execute('SELECT qr_code FROM books WHERE name = ?', (book_name,))
    result = c.fetchone()
    conn.close()

    if result:
        qr_code_data = result[0]

        # Convert bytes back to an image
        img = Image.open(io.BytesIO(qr_code_data))
        return img
    else:
        print("Book not found")
        return None

def delete_book(book_name):
    conn, c = get_connection()
    # Delete the book from the database
    c.execute('DELETE FROM books WHERE name = ?', (book_name,))
    conn.commit()
    conn.close()

def get_all_books():
    conn, c = get_connection()
    # Get all book information from the database ordered by insertion (oldest first)
    c.execute('SELECT name, year, author, description, category FROM books ORDER BY id ASC')
    books = c.fetchall()
    conn.close()
    return books

def get_book_categories():
    conn, c = get_connection()

    # Check if the category column exists
    c.execute("PRAGMA table_info(books)")
    columns = [column[1] for column in c.fetchall()]

    if 'category' in columns:
        # Get all unique categories
        c.execute('SELECT DISTINCT category FROM books WHERE category IS NOT NULL')
        categories = [row[0] for row in c.fetchall()]
    else:
        categories = []

    conn.close()
    return categories

def get_preference(key, default=None):
    conn, c = get_connection()
    c.execute('SELECT value FROM preferences WHERE key = ?', (key,))
    result = c.fetchone()
    conn.close()

    if result:
        return result[0]
    return default

def set_preference(key, value):
    conn, c = get_connection()
    c.execute('INSERT OR REPLACE INTO preferences (key, value) VALUES (?, ?)', (key, value))
    conn.commit()
    conn.close()

def close_connection():
    # This function is kept for backward compatibility
    pass

# Initialize the database when the module is imported
initialize_database()