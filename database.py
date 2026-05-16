import sqlite3
from datetime import date

DB_NAME = "library.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Students table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            roll_number TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            enrolled_date TEXT DEFAULT CURRENT_DATE
        )
    """)

    # Books table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            genre TEXT,
            total_copies INTEGER DEFAULT 1,
            available_copies INTEGER DEFAULT 1
        )
    """)

    # Transactions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            book_id INTEGER NOT NULL,
            issue_date TEXT DEFAULT CURRENT_DATE,
            due_date TEXT NOT NULL,
            return_date TEXT,
            returned INTEGER DEFAULT 0,
            fine_amount REAL DEFAULT 0.0,
            FOREIGN KEY (student_id) REFERENCES students(id),
            FOREIGN KEY (book_id) REFERENCES books(id)
        )
    """)

    conn.commit()

    # Seed sample data if empty
    cursor.execute("SELECT COUNT(*) FROM students")
    if cursor.fetchone()[0] == 0:
        seed_data(cursor)
        conn.commit()

    conn.close()

def seed_data(cursor):
    students = [
        ("NIE2022CS001", "Monu Kumar",  "monu@nie.ac.in",  "8002116605"),
        ("NIE2022CS002", "Riya Sharma", "riya@nie.ac.in",  "9876543210"),
        ("NIE2022CS003", "Arjun Patel", "arjun@nie.ac.in", "9123456789"),
        ("NIE2022CS004", "Priya Nair",  "priya@nie.ac.in", "9988776655"),
    ]
    cursor.executemany(
        "INSERT INTO students (roll_number, name, email, phone) VALUES (?, ?, ?, ?)",
        students
    )

    books = [
        ("Database System Concepts", "Silberschatz", "DBMS", 3, 2),
        ("Introduction to Algorithms", "Cormen", "DSA", 2, 1),
        ("Clean Code", "Robert Martin", "Programming", 4, 4),
        ("Artificial Intelligence", "Russell & Norvig", "AI", 2, 2),
        ("Operating System Concepts", "Galvin", "OS", 3, 1),
    ]
    cursor.executemany(
        "INSERT INTO books (title, author, genre, total_copies, available_copies) VALUES (?, ?, ?, ?, ?)",
        books
    )

    # Sample transactions
    transactions = [
        (1, 1, "2025-04-01", "2025-04-15", "2025-04-14", 1, 0.0),
        (2, 2, "2025-04-10", "2025-04-24", None, 0, 0.0),
        (3, 5, "2025-04-05", "2025-04-19", None, 0, 0.0),
    ]
    cursor.executemany(
        "INSERT INTO transactions (student_id, book_id, issue_date, due_date, return_date, returned, fine_amount) VALUES (?, ?, ?, ?, ?, ?, ?)",
        transactions
    )

# ─── BOOK OPERATIONS ────────────────────────────────────────────────────────

def get_all_books():
    conn = get_connection()
    books = conn.execute("SELECT * FROM books ORDER BY title").fetchall()
    conn.close()
    return books

def add_book(title, author, genre, copies):
    conn = get_connection()
    conn.execute(
        "INSERT INTO books (title, author, genre, total_copies, available_copies) VALUES (?, ?, ?, ?, ?)",
        (title, author, genre, copies, copies)
    )
    conn.commit()
    conn.close()

def search_books(keyword):
    conn = get_connection()
    results = conn.execute(
        "SELECT * FROM books WHERE title LIKE ? OR author LIKE ? OR genre LIKE ?",
        (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%")
    ).fetchall()
    conn.close()
    return results

# ─── STUDENT OPERATIONS ─────────────────────────────────────────────────────

def get_all_students():
    conn = get_connection()
    students = conn.execute("SELECT id, roll_number, name, email, phone, enrolled_date FROM students ORDER BY roll_number").fetchall()
    conn.close()
    return students

def add_student(roll_number, name, email, phone):
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO students (roll_number, name, email, phone) VALUES (?, ?, ?, ?)",
            (roll_number, name, email, phone)
        )
        conn.commit()
        conn.close()
        return True, "Student added successfully."
    except sqlite3.IntegrityError as e:
        conn.close()
        if "roll_number" in str(e):
            return False, "Roll number already exists."
        return False, "Email already exists."

# ─── TRANSACTION OPERATIONS ─────────────────────────────────────────────────

def issue_book(student_id, book_id, due_date):
    conn = get_connection()
    book = conn.execute("SELECT available_copies FROM books WHERE id = ?", (book_id,)).fetchone()
    if not book or book["available_copies"] <= 0:
        conn.close()
        return False, "Book not available."

    conn.execute(
        "INSERT INTO transactions (student_id, book_id, issue_date, due_date) VALUES (?, ?, CURRENT_DATE, ?)",
        (student_id, book_id, due_date)
    )
    conn.execute("UPDATE books SET available_copies = available_copies - 1 WHERE id = ?", (book_id,))
    conn.commit()
    conn.close()
    return True, "Book issued successfully."

def return_book(transaction_id):
    conn = get_connection()
    txn = conn.execute(
        "SELECT * FROM transactions WHERE id = ? AND returned = 0", (transaction_id,)
    ).fetchone()

    if not txn:
        conn.close()
        return False, "Transaction not found or already returned."

    today = date.today().isoformat()
    due = txn["due_date"]
    fine = 0.0

    if today > due:
        days_overdue = (date.today() - date.fromisoformat(due)).days
        fine = days_overdue * 1.0  # $1 per day

    conn.execute(
        "UPDATE transactions SET return_date = ?, returned = 1, fine_amount = ? WHERE id = ?",
        (today, fine, transaction_id)
    )
    conn.execute(
        "UPDATE books SET available_copies = available_copies + 1 WHERE id = ?",
        (txn["book_id"],)
    )
    conn.commit()
    conn.close()
    return True, f"Book returned. Fine: ${fine:.2f}"

def get_overdue_books():
    conn = get_connection()
    results = conn.execute("""
        SELECT s.name AS student_name, b.title AS book_title,
               t.due_date, t.id AS transaction_id,
               (JULIANDAY('now') - JULIANDAY(t.due_date)) AS days_overdue,
               ROUND((JULIANDAY('now') - JULIANDAY(t.due_date)) * 1.0, 2) AS total_fine
        FROM transactions t
        JOIN students s ON t.student_id = s.id
        JOIN books b ON t.book_id = b.id
        WHERE t.returned = 0 AND t.due_date < DATE('now')
        ORDER BY days_overdue DESC
    """).fetchall()
    conn.close()
    return results

def get_all_transactions():
    conn = get_connection()
    results = conn.execute("""
        SELECT t.id, s.name AS student_name, b.title AS book_title,
               t.issue_date, t.due_date, t.return_date,
               t.returned, t.fine_amount
        FROM transactions t
        JOIN students s ON t.student_id = s.id
        JOIN books b ON t.book_id = b.id
        ORDER BY t.issue_date DESC
    """).fetchall()
    conn.close()
    return results

def get_active_transactions():
    conn = get_connection()
    results = conn.execute("""
        SELECT t.id, s.name AS student_name, b.title AS book_title,
               t.issue_date, t.due_date
        FROM transactions t
        JOIN students s ON t.student_id = s.id
        JOIN books b ON t.book_id = b.id
        WHERE t.returned = 0
        ORDER BY t.due_date
    """).fetchall()
    conn.close()
    return results

def get_dashboard_stats():
    conn = get_connection()
    total_books = conn.execute("SELECT SUM(total_copies) FROM books").fetchone()[0] or 0
    available = conn.execute("SELECT SUM(available_copies) FROM books").fetchone()[0] or 0
    total_students = conn.execute("SELECT COUNT(*) FROM students").fetchone()[0] or 0
    active_issues = conn.execute("SELECT COUNT(*) FROM transactions WHERE returned = 0").fetchone()[0] or 0
    overdue = conn.execute(
        "SELECT COUNT(*) FROM transactions WHERE returned = 0 AND due_date < DATE('now')"
    ).fetchone()[0] or 0
    total_fines = conn.execute("SELECT SUM(fine_amount) FROM transactions").fetchone()[0] or 0
    conn.close()
    return {
        "total_books": total_books,
        "available": available,
        "total_students": total_students,
        "active_issues": active_issues,
        "overdue": overdue,
        "total_fines": round(total_fines, 2)
    }