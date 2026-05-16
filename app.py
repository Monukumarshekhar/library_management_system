import streamlit as st
from database import (
    init_db, get_all_books, add_book, search_books,
    get_all_students, add_student,
    issue_book, return_book,
    get_overdue_books, get_all_transactions, get_active_transactions,
    get_dashboard_stats
)
import pandas as pd

# ─── PAGE CONFIG ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Library Management System",
    page_icon="📚",
    layout="wide"
)

# ─── STYLES ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Inter:wght@400;500;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    .main-title {
        font-family: 'Playfair Display', serif;
        font-size: 2.4rem;
        color: #1a1a2e;
        margin-bottom: 0;
    }
    .subtitle {
        color: #6c757d;
        font-size: 0.95rem;
        margin-top: 0;
    }
    .metric-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border-radius: 12px;
        padding: 20px;
        color: white;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.08);
    }
    .metric-number {
        font-size: 2.2rem;
        font-weight: 700;
        color: #e2b96f;
    }
    .metric-label {
        font-size: 0.8rem;
        color: #adb5bd;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 4px;
    }
    .overdue-badge {
        background-color: #dc3545;
        color: white;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .active-badge {
        background-color: #198754;
        color: white;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .section-header {
        font-family: 'Playfair Display', serif;
        font-size: 1.4rem;
        color: #1a1a2e;
        border-bottom: 2px solid #e2b96f;
        padding-bottom: 6px;
        margin-bottom: 16px;
    }
    div[data-testid="stTabs"] button {
        font-weight: 600;
        font-size: 0.9rem;
    }
    .stAlert {
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ─── INIT ────────────────────────────────────────────────────────────────────
init_db()

# ─── HEADER ──────────────────────────────────────────────────────────────────
col_logo, col_title = st.columns([1, 11])
with col_title:
    st.markdown('<p class="main-title">📚 Library Management System</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Automated book inventory, student records, issue/return tracking & fine calculation</p>', unsafe_allow_html=True)

st.divider()

# ─── DASHBOARD STATS ─────────────────────────────────────────────────────────
stats = get_dashboard_stats()
c1, c2, c3, c4, c5, c6 = st.columns(6)
metrics = [
    (c1, stats["total_books"], "Total Books"),
    (c2, stats["available"], "Available"),
    (c3, stats["total_students"], "Students"),
    (c4, stats["active_issues"], "Active Issues"),
    (c5, stats["overdue"], "Overdue"),
    (c6, f"${stats['total_fines']}", "Total Fines"),
]
for col, val, label in metrics:
    with col:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-number">{val}</div>
            <div class="metric-label">{label}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─── TABS ────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📖 Books", "🎓 Students", "📤 Issue Book",
    "📥 Return Book", "⚠️ Overdue", "📊 All Transactions"
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — BOOKS
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown('<p class="section-header">Book Inventory</p>', unsafe_allow_html=True)

    col_search, col_spacer = st.columns([3, 5])
    with col_search:
        keyword = st.text_input("🔍 Search by title, author, or genre", placeholder="e.g. Algorithms")

    if keyword:
        books = search_books(keyword)
    else:
        books = get_all_books()

    if books:
        df = pd.DataFrame([dict(b) for b in books])
        df.columns = ["ID", "Title", "Author", "Genre", "Total Copies", "Available"]
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No books found.")

    st.markdown("---")
    st.markdown('<p class="section-header">➕ Add New Book</p>', unsafe_allow_html=True)
    with st.form("add_book_form"):
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("Book Title")
            author = st.text_input("Author")
        with col2:
            genre = st.text_input("Genre")
            copies = st.number_input("Number of Copies", min_value=1, value=1)
        submitted = st.form_submit_button("Add Book", use_container_width=True)
        if submitted:
            if title and author:
                add_book(title, author, genre, copies)
                st.success(f"✅ '{title}' added to library!")
                st.rerun()
            else:
                st.error("Title and Author are required.")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — STUDENTS
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<p class="section-header">Student Records</p>', unsafe_allow_html=True)

    students = get_all_students()
    if students:
        df = pd.DataFrame([dict(s) for s in students])
        df.columns = ["ID", "Roll Number", "Name", "Email", "Phone", "Enrolled Date"]
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No students registered.")

    st.markdown("---")
    st.markdown('<p class="section-header">➕ Register New Student</p>', unsafe_allow_html=True)
    with st.form("add_student_form"):
        col1, col2 = st.columns(2)
        with col1:
            roll_number = st.text_input("Roll Number (e.g. NIE2022CS005)")
            name = st.text_input("Full Name")
        with col2:
            email = st.text_input("Email (e.g. student@nie.ac.in)")
            phone = st.text_input("Phone Number (10 digits)")
        submitted = st.form_submit_button("Register Student", use_container_width=True)
        if submitted:
            import re
            if not roll_number:
                st.error("❌ Roll number is required.")
            elif not name:
                st.error("❌ Name is required.")
            elif not re.match(r"^[\w\.-]+@[\w\.-]+\.\w{2,}$", email):
                st.error("❌ Enter a valid email address (e.g. student@nie.ac.in)")
            elif not re.match(r"^\d{10}$", phone):
                st.error("❌ Phone number must be exactly 10 digits.")
            else:
                success, msg = add_student(roll_number, name, email, phone)
                if success:
                    st.success(f"✅ {msg}")
                    st.rerun()
                else:
                    st.error(f"❌ {msg}")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — ISSUE BOOK
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<p class="section-header">Issue a Book to Student</p>', unsafe_allow_html=True)

    students = get_all_students()
    books = get_all_books()

    student_options = {f"{s['name']} (ID: {s['id']})": s['id'] for s in students}
    book_options = {
        f"{b['title']} — {b['author']} [Available: {b['available_copies']}]": b['id']
        for b in books
    }

    with st.form("issue_form"):
        selected_student = st.selectbox("Select Student", list(student_options.keys()))
        selected_book = st.selectbox("Select Book", list(book_options.keys()))
        due_date = st.date_input("Due Date")
        submitted = st.form_submit_button("Issue Book", use_container_width=True)
        if submitted:
            student_id = student_options[selected_student]
            book_id = book_options[selected_book]
            success, msg = issue_book(student_id, book_id, str(due_date))
            if success:
                st.success(f"✅ {msg}")
                st.rerun()
            else:
                st.error(f"❌ {msg}")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — RETURN BOOK
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<p class="section-header">Return a Book</p>', unsafe_allow_html=True)

    active_txns = get_active_transactions()

    if active_txns:
        txn_options = {
            f"[#{t['id']}] {t['student_name']} — {t['book_title']} (Due: {t['due_date']})": t['id']
            for t in active_txns
        }
        with st.form("return_form"):
            selected_txn = st.selectbox("Select Active Transaction", list(txn_options.keys()))
            submitted = st.form_submit_button("Return Book", use_container_width=True)
            if submitted:
                txn_id = txn_options[selected_txn]
                success, msg = return_book(txn_id)
                if success:
                    st.success(f"✅ {msg}")
                    st.rerun()
                else:
                    st.error(f"❌ {msg}")
    else:
        st.info("No active transactions to return.")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — OVERDUE BOOKS
# ══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown('<p class="section-header">⚠️ Overdue Books & Fines</p>', unsafe_allow_html=True)

    st.markdown("""
    **SQL Query Used:**
    ```sql
    SELECT s.name, b.title, t.due_date,
           JULIANDAY('now') - JULIANDAY(t.due_date) AS days_overdue,
           ROUND((JULIANDAY('now') - JULIANDAY(t.due_date)) * 1.0, 2) AS total_fine
    FROM transactions t
    JOIN students s ON t.student_id = s.id
    JOIN books b ON t.book_id = b.id
    WHERE t.returned = 0 AND t.due_date < DATE('now')
    ```
    *Fine = $1 per overdue day*
    """)

    overdue = get_overdue_books()
    if overdue:
        df = pd.DataFrame([dict(o) for o in overdue])
        df.columns = ["Student", "Book", "Due Date", "Transaction ID", "Days Overdue", "Fine ($)"]
        df["Days Overdue"] = df["Days Overdue"].apply(lambda x: f"⚠️ {int(x)} days")
        df["Fine ($)"] = df["Fine ($)"].apply(lambda x: f"${x:.2f}")
        st.dataframe(df[["Student", "Book", "Due Date", "Days Overdue", "Fine ($)"]], use_container_width=True, hide_index=True)
    else:
        st.success("✅ No overdue books right now!")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 6 — ALL TRANSACTIONS
# ══════════════════════════════════════════════════════════════════════════════
with tab6:
    st.markdown('<p class="section-header">All Transactions</p>', unsafe_allow_html=True)

    txns = get_all_transactions()
    if txns:
        df = pd.DataFrame([dict(t) for t in txns])
        df.columns = ["ID", "Student", "Book", "Issue Date", "Due Date", "Return Date", "Returned", "Fine ($)"]
        df["Returned"] = df["Returned"].apply(lambda x: "✅ Yes" if x else "❌ No")
        df["Fine ($)"] = df["Fine ($)"].apply(lambda x: f"${x:.2f}" if x else "$0.00")
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No transactions yet.")

# ─── FOOTER ──────────────────────────────────────────────────────────────────
st.divider()
st.markdown(
    "<center><small>Library Management System — Built with Python, SQLite, Streamlit | Monu Kumar Shekhar</small></center>",
    unsafe_allow_html=True
)