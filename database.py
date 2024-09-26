import sqlite3
import io
from PIL import Image

def get_connection():
    conn = sqlite3.connect('books.db')
    c = conn.cursor()
    return conn, c

def initialize_database():
    conn, c = get_connection()
    # Create a table to store book names, year, author, and QR codes
    c.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            year INTEGER NOT NULL,
            author TEXT NOT NULL,
            qr_code BLOB NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def save_book(book_name, year, author, qr_code_data):
    conn, c = get_connection()
    # Insert book name, year, author, and QR code into the database
    c.execute('INSERT INTO books (name, year, author, qr_code) VALUES (?, ?, ?, ?)', (book_name, year, author, qr_code_data))
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
    # Get all book names from the database ordered by insertion (oldest first)
    c.execute('SELECT name, year, author FROM books ORDER BY id ASC')
    books = c.fetchall()
    conn.close()
    return books

def close_connection(conn):
    # Close the database connection
    conn.close()

# Initialize the database when the module is imported
initialize_database()