import threading
import sys
import time

from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageDraw

from config import RETENTION_DAYS
from storage.database import init_db, cleanup_old_sessions
from main import run
from gui.dashboard import open_dashboard
from gui.settings_window import open_settings
from settings.config_store import load_settings

# ---------------- GLOBAL STATE ----------------
tracking_thread = None
dashboard_thread = None
settings_thread = None

running = False
paused = False
app_alive = True   # 👈 keeps EXE alive


# ---------------- ICON ----------------
def create_icon():
    img = Image.new("RGB", (64, 64), color=(30, 30, 30))
    d = ImageDraw.Draw(img)
    d.rectangle((16, 16, 48, 48), fill=(0, 200, 200))
    return img


# ---------------- DASHBOARD ----------------
def launch_dashboard():
    global dashboard_thread
    if dashboard_thread and dashboard_thread.is_alive():
        return

    dashboard_thread = threading.Thread(
        target=open_dashboard,
        daemon=True
    )
    dashboard_thread.start()


# ---------------- SETTINGS ----------------
def launch_settings():
    global settings_thread
    if settings_thread and settings_thread.is_alive():
        return

    settings_thread = threading.Thread(
        target=open_settings,
        daemon=True
    )
    settings_thread.start()


# ---------------- TRACKING ----------------
def start_tracking(icon, item):
    global tracking_thread, running, paused

    if running:
        return

    running = True
    paused = False

    def tracking_loop():
        global running, paused
        difficulty = load_settings()["difficulty"]

        while running:
            if not paused:
                run(difficulty)
            time.sleep(1)

    tracking_thread = threading.Thread(
        target=tracking_loop,
        daemon=True
    )
    tracking_thread.start()


def toggle_pause(icon, item):
    global paused
    paused = not paused


def exit_app(icon, item):
    global running, app_alive
    running = False
    app_alive = False
    icon.stop()
    sys.exit(0)


# ---------------- MAIN ----------------
def main():
    global app_alive

    init_db()
    cleanup_old_sessions(RETENTION_DAYS)

    icon = Icon(
        "MindLoad",
        create_icon(),
        "MindLoad – Cognitive Load Monitor",
        menu=Menu(
            MenuItem("Start Tracking", start_tracking),
            MenuItem("Pause / Resume", toggle_pause),
            MenuItem("Open Dashboard", lambda icon, item: launch_dashboard()),
            MenuItem("Settings", lambda icon, item: launch_settings()),
            MenuItem("Exit", exit_app)
        )
    )

    # ✅ CORRECT for PyInstaller Windows EXE
    icon.run_detached()

    # 🔒 Keep process alive
    while app_alive:
        time.sleep(1)


if __name__ == "__main__":
    main()
