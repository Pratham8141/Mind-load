import time
import psutil
import ctypes
import sqlite3
import threading
from ctypes import wintypes
from datetime import date

DB_NAME = "mindload.db"
running = True  # global control flag

# ================= WINDOWS API =================
user32 = ctypes.WinDLL("user32", use_last_error=True)
GetForegroundWindow = user32.GetForegroundWindow
GetWindowThreadProcessId = user32.GetWindowThreadProcessId


# ================= DATABASE =================
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


def cleanup_old_sessions(retention_days=30):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
        DELETE FROM sessions
        WHERE session_date < date('now', ?)
    """, (f"-{retention_days} days",))

    conn.commit()
    conn.close()


def get_daily_summary():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    today = str(date.today())

    cur.execute("""
        SELECT total_load FROM daily_summary
        WHERE session_date = ?
    """, (today,))
    today_load = cur.fetchone()

    cur.execute("""
        SELECT session_date, total_load
        FROM daily_summary
        ORDER BY session_date DESC
        LIMIT 7
    """)
    last_7_days = cur.fetchall()

    conn.close()
    return today_load, last_7_days


# ================= TRACKING =================
def get_active_process_name():
    hwnd = GetForegroundWindow()
    pid = wintypes.DWORD()
    GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    try:
        return psutil.Process(pid.value).name()
    except psutil.NoSuchProcess:
        return None


def get_task_difficulty():
    while True:
        try:
            value = int(input("Enter task difficulty (1–5): "))
            if 1 <= value <= 5:
                return value
        except ValueError:
            pass
        print("Please enter a number between 1 and 5.")


def classify_daily_load(load):
    if load < 50:
        return "Light"
    elif load < 120:
        return "Moderate"
    elif load < 200:
        return "Heavy"
    else:
        return "Overload"


def print_daily_report():
    today_load, last_7_days = get_daily_summary()

    print("\n====== DAILY SUMMARY ======")
    if today_load:
        status = classify_daily_load(today_load[0])
        print(f"Today’s Load: {round(today_load[0], 2)} ({status})")
    else:
        print("No data for today yet.")

    print("\nLast 7 Days:")
    for d, load in last_7_days:
        print(f"{d} → {round(load, 2)}")

    print("===========================\n")


# ================= GRACEFUL STOP =================
def listen_for_exit():
    global running
    while running:
        cmd = input().strip().lower()
        if cmd == "q":
            print("\nStopping MindLoad safely...")
            running = False


# ================= MAIN LOOP =================
def run_session_tracker(difficulty):
    global running

    print("\nMindLoad is running.")
    print("Type 'Q' and press Enter to stop safely.\n")

    current_app = get_active_process_name()
    session_start = time.time()
    last_activity_time = time.time()

    context_switches = 0
    break_recovery = 0
    today = str(date.today())

    while running:
        new_app = get_active_process_name()
        now = time.time()

        idle_time = now - last_activity_time

        # Break detection
        if idle_time >= 420:
            break_recovery = 10
        elif idle_time >= 180:
            break_recovery = 5

        if new_app != current_app:
            duration_seconds = int(now - session_start)
            duration_minutes = duration_seconds / 60

            base_load = difficulty * duration_minutes
            switch_penalty = context_switches * 2

            session_load = round(
                base_load + switch_penalty - break_recovery, 2
            )
            if session_load < 0:
                session_load = 0

            save_session(today, current_app, duration_seconds, session_load)

            print(f"Session ended → {current_app}")
            print(f"Session Load: {session_load}")

            print_daily_report()

            context_switches += 1
            current_app = new_app
            session_start = now
            last_activity_time = now
            break_recovery = 0

        time.sleep(1)

    print("MindLoad stopped cleanly.")


# ================= ENTRY =================
if __name__ == "__main__":
    init_db()
    cleanup_old_sessions()

    difficulty = get_task_difficulty()

    listener = threading.Thread(
        target=listen_for_exit, daemon=True
    )
    listener.start()

    run_session_tracker(difficulty)
