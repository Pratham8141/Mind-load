import sqlite3
from datetime import date
from config import DB_NAME

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_date TEXT,
            app_name TEXT,
            duration REAL,
            session_load REAL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS daily_summary (
            session_date TEXT PRIMARY KEY,
            total_load REAL
        )
    """)

    conn.commit()
    conn.close()


def save_session(session_date, app, duration, load):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO sessions (session_date, app_name, duration, session_load)
        VALUES (?, ?, ?, ?)
    """, (session_date, app, duration, load))

    cur.execute("""
        INSERT INTO daily_summary (session_date, total_load)
        VALUES (?, ?)
        ON CONFLICT(session_date)
        DO UPDATE SET total_load = total_load + ?
    """, (session_date, load, load))

    conn.commit()
    conn.close()


def cleanup_old_sessions(days):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        DELETE FROM sessions
        WHERE session_date < date('now', ?)
    """, (f"-{days} days",))
    conn.commit()
    conn.close()


def get_daily_summary():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    today = str(date.today())

    cur.execute("""
        SELECT total_load FROM daily_summary WHERE session_date = ?
    """, (today,))
    today_load = cur.fetchone()

    cur.execute("""
        SELECT session_date, total_load
        FROM daily_summary
        ORDER BY session_date DESC
        LIMIT 7
    """)
    history = cur.fetchall()

    conn.close()
    return today_load, history
