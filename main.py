import time
import threading
from datetime import date

from config import RETENTION_DAYS
from tracker.activity import get_active_process_name
from engine.cognitive import calculate_session_load
from storage.database import (
    init_db, save_session, cleanup_old_sessions
)
from reporting.summary import print_daily_report

running = True

def listen_for_exit():
    global running
    while running:
        if input().strip().lower() == "q":
            print("\nStopping MindLoad safely...")
            running = False


def get_task_difficulty():
    while True:
        try:
            v = int(input("Enter task difficulty (1–5): "))
            if 1 <= v <= 5:
                return v
        except ValueError:
            pass
        print("Please enter a number between 1 and 5.")


def run(difficulty):
    global running
    print("\nMindLoad is running.")
    print("Type 'Q' and press Enter to stop safely.\n")

    current_app = get_active_process_name()
    start = time.time()
    last_activity = time.time()
    context_switches = 0
    break_recovery = 0
    today = str(date.today())

    while running:
        new_app = get_active_process_name()
        now = time.time()
        idle = now - last_activity

        if idle >= 420:
            break_recovery = 10
        elif idle >= 180:
            break_recovery = 5

        if new_app != current_app:
            duration = int(now - start)
            load = calculate_session_load(
                difficulty, duration / 60,
                context_switches, break_recovery
            )

            save_session(today, current_app, duration, load)
            print(f"Session ended → {current_app}")
            print(f"Session Load: {load}")
            print_daily_report()

            context_switches += 1
            current_app = new_app
            start = now
            last_activity = now
            break_recovery = 0

        time.sleep(1)

    print("MindLoad stopped cleanly.")


if __name__ == "__main__":
    init_db()
    cleanup_old_sessions(RETENTION_DAYS)

    difficulty = get_task_difficulty()

    listener = threading.Thread(target=listen_for_exit, daemon=True)
    listener.start()

    run(difficulty)
