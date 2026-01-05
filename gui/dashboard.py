import tkinter as tk
from tkinter import ttk

from storage.database import get_daily_summary
from engine.cognitive import classify_daily_load

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class Dashboard(tk.Tk):
    def __init__(self):
        super().__init__()

        # Proper close handling
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.title("MindLoad Dashboard")
        self.geometry("520x520")
        self.resizable(False, False)
        self.configure(bg="#1e1e1e")

        self.build_ui()
        self.refresh_data()

    def build_ui(self):
        title = tk.Label(
            self,
            text="MindLoad",
            font=("Segoe UI", 18, "bold"),
            fg="white",
            bg="#1e1e1e"
        )
        title.pack(pady=8)

        self.today_label = tk.Label(
            self,
            text="Today: --",
            font=("Segoe UI", 12),
            fg="white",
            bg="#1e1e1e"
        )
        self.today_label.pack(pady=2)

        self.status_label = tk.Label(
            self,
            text="Status: --",
            font=("Segoe UI", 12, "bold"),
            fg="white",
            bg="#1e1e1e"
        )
        self.status_label.pack(pady=2)

        sep = ttk.Separator(self, orient="horizontal")
        sep.pack(fill="x", padx=20, pady=10)

        # -------- Chart Area --------
        self.figure = Figure(figsize=(5, 2.5), dpi=100)
        self.ax = self.figure.add_subplot(111)

        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas.get_tk_widget().pack(padx=20, pady=10)

        sep2 = ttk.Separator(self, orient="horizontal")
        sep2.pack(fill="x", padx=20, pady=10)

        history_title = tk.Label(
            self,
            text="Last 7 Days (Exact Values)",
            font=("Segoe UI", 11, "bold"),
            fg="white",
            bg="#1e1e1e"
        )
        history_title.pack(pady=4)

        self.history_box = tk.Listbox(
            self,
            height=7,
            bg="#2b2b2b",
            fg="white",
            font=("Consolas", 10),
            border=0,
            highlightthickness=0
        )
        self.history_box.pack(fill="x", padx=40, pady=5)

        refresh_btn = tk.Button(
            self,
            text="Refresh",
            command=self.refresh_data,
            bg="#00bcd4",
            fg="black",
            border=0,
            padx=12,
            pady=6
        )
        refresh_btn.pack(pady=10)

    def refresh_data(self):
        today, history = get_daily_summary()

        # ----- Today -----
        if today:
            load = round(today[0], 2)
            status = classify_daily_load(load)

            self.today_label.config(text=f"Today: {load}")
            self.status_label.config(text=f"Status: {status}")

            color_map = {
                "Light": "#00e676",
                "Moderate": "#ffeb3b",
                "Heavy": "#ff9800",
                "Overload": "#f44336"
            }
            self.status_label.config(fg=color_map.get(status, "white"))
        else:
            self.today_label.config(text="Today: No data")
            self.status_label.config(text="Status: --")

        # ----- History List -----
        self.history_box.delete(0, tk.END)
        dates = []
        loads = []

        for d, load in reversed(history):
            self.history_box.insert(tk.END, f"{d}  →  {round(load, 2)}")
            dates.append(d[5:])  # MM-DD
            loads.append(round(load, 2))

        # ----- Chart -----
        self.ax.clear()
        self.ax.bar(dates, loads, color="#00bcd4")

        self.ax.set_title("Weekly Cognitive Load", fontsize=10)
        self.ax.set_ylabel("Load")
        self.ax.set_xlabel("Date")

        self.ax.tick_params(axis='x', rotation=45)
        self.figure.tight_layout()

        self.canvas.draw()

    def on_close(self):
        self.destroy()


def open_dashboard():
    app = Dashboard()
    app.mainloop()
