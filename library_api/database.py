# -*- coding: utf-8 -*-

import sqlite3
import random
import string


class Book:
    def __init__(self, id, title, author):
        self.id = id
        self.title = title
        self.author = author


class Page:
    def __init__(self, id, book_id, content, page_number):
        self.id = id
        self.book_id = book_id
        self.content = content
        self.page_number = page_number


def create_database():
    with sqlite3.connect('library.db') as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS books
                     (id INTEGER PRIMARY KEY, title TEXT, author TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS pages
                     (id INTEGER PRIMARY KEY, book_id INTEGER, content TEXT, page_number INTEGER)''')
        conn.commit()


def seed_database():
    with sqlite3.connect('library.db') as conn:
        c = conn.cursor()
        c.execute("INSERT INTO books (title, author) VALUES (?, ?)", ('Clean Code', 'Robert C. Martin'))
        for i in range(1, 11):
            title = f"Programming Book {i}"
            author = "Unknown"

            c.execute("INSERT INTO books (title, author) VALUES (?, ?)", (title, author))

            # Seed pages for each book
            for j in range(1, 11):
                # Generate random content for each page
                content = ''.join(random.choices(string.ascii_letters + string.digits, k=random.randint(500, 700)))
                c.execute("INSERT INTO pages (book_id, content, page_number) VALUES (?, ?, ?)", (i, content, j))
        conn.commit()


def get_books():
    with sqlite3.connect('library.db') as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM books")
        books = [Book(*row) for row in c.fetchall()]
        return books


def get_book(book_id):
    with sqlite3.connect('library.db') as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM books WHERE id=?", (book_id,))
        row = c.fetchone()
        if row is None:
            return None
        book = Book(*row)
        c.execute("SELECT * FROM pages WHERE book_id=?", (book_id,))
        pages = [Page(*row) for row in c.fetchall()]
        book.pages = pages
        return book



def get_page(book_id, page_number):
    with sqlite3.connect('library.db') as conn:
        c = conn.cursor()
        c.execute("SELECT content FROM pages WHERE book_id=? AND page_number=?", (book_id, page_number))
        row = c.fetchone()
        if not row:
            return None
        content = row[0]
        return content

def get_total_pages(book_id):
    with sqlite3.connect('library.db') as conn:
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM pages WHERE book_id=?", (book_id,))
        row = c.fetchone()
        if not row:
            return None
        total_pages = row[0]
    return total_pages
