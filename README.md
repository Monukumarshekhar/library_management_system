# 📚 Library Management System

A database-driven Library Management System built with **Python, SQLite, and Streamlit**.

## Features

- 📖 **Book Inventory** — Add, search, and track books with availability
- 🎓 **Student Records** — Register and manage student data
- 📤 **Issue Books** — Issue books with due date tracking
- 📥 **Return Books** — Return books with automatic fine calculation
- ⚠️ **Overdue Tracking** — List overdue books with $1/day fine
- 📊 **Transaction Reports** — Full history of all issue/return activity

## Tech Stack

- **Python** — Core logic
- **SQLite** — Relational database (SQL, DBMS concepts)
- **Streamlit** — Web interface

## Database Schema

```sql
-- Students Table
CREATE TABLE students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone TEXT,
    enrolled_date TEXT DEFAULT CURRENT_DATE
);

-- Books Table
CREATE TABLE books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    genre TEXT,
    total_copies INTEGER DEFAULT 1,
    available_copies INTEGER DEFAULT 1
);

-- Transactions Table
CREATE TABLE transactions (
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
);
```

## Key SQL Queries

### Overdue Books with Fine
```sql
SELECT s.name, b.title, t.due_date,
       JULIANDAY('now') - JULIANDAY(t.due_date) AS days_overdue,
       ROUND((JULIANDAY('now') - JULIANDAY(t.due_date)) * 1.0, 2) AS total_fine
FROM transactions t
JOIN students s ON t.student_id = s.id
JOIN books b ON t.book_id = b.id
WHERE t.returned = 0 AND t.due_date < DATE('now');
```

### Book Availability Report
```sql
SELECT title, author, total_copies, available_copies,
       (total_copies - available_copies) AS issued_copies
FROM books;
```

## How to Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Cloud

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo
4. Set main file as `app.py`
5. Deploy — done!

---

Built by **Monu Kumar Shekhar** | NIE Mysore, CSE AI-ML
