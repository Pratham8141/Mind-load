import tkinter as tk
from tkinter import ttk

from settings.config_store import load_settings, save_settings


class SettingsWindow(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("MindLoad Settings")
        self.geometry("320x220")
        self.resizable(False, False)

        self.settings = load_settings()

        self.build_ui()

    def build_ui(self):
        ttk.Label(self, text="Default Difficulty (1–5)").pack(pady=8)

        self.diff_var = tk.IntVar(value=self.settings["difficulty"])
        ttk.Scale(
            self,
            from_=1, to=5,
            orient="horizontal",
            variable=self.diff_var
        ).pack(fill="x", padx=20)

        ttk.Label(self, text="Overload Threshold").pack(pady=12)

        self.threshold_var = tk.IntVar(
            value=self.settings["overload_threshold"]
        )
        ttk.Entry(self, textvariable=self.threshold_var).pack()

        ttk.Button(
            self,
            text="Save",
            command=self.save_and_close
        ).pack(pady=15)

    def save_and_close(self):
        self.settings["difficulty"] = int(self.diff_var.get())
        self.settings["overload_threshold"] = int(self.threshold_var.get())
        save_settings(self.settings)
        self.destroy()


def open_settings():
    app = SettingsWindow()
    app.mainloop()
