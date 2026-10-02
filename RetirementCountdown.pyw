# Retirement Countdown GUI
# A compact desktop countdown application for tracking a retirement date.
# Displays the target date, remaining time, and a rotating message.
# Version: 1.0.0  Initial release
# Version: 1.0.1  Added settings file to Documents folder for persistence
# Version: 1.0.2  Daily message, date validation, consistent window size, holiday support,
#                 settings follow redirected (OneDrive) Documents folder
# Licensed under the MIT License; see LICENSE.
# by Michael Jacobson

import tkinter as tk
from tkinter import simpledialog, messagebox
import datetime
import random
import json
import os

APP_NAME = "Retirement Countdown"
VERSION = "1.0.2"
WINDOW_WIDTH = 200
WINDOW_HEIGHT = 110
DATE_FORMATS = ("%B %d %Y %H:%M:%S", "%B %d %Y")

MESSAGES = [
    "Happy Retirement!",
    "Congratulations!",
    "Well deserved!",
    "Ski resorts await!",
    "Enjoy your freedom!",
    "Adventure awaits!",
    "Time for new hobbies!",
    "Relax and celebrate!",
    "We earned it!",
    "Cheers to us!",
    "No alarm clocks!",
    "Travel the world!",
    "Freedom at last!"
]

SETTINGS_FILENAME = "retirement_settings.json"

# Return the user's actual Documents folder, which may be redirected (e.g. to OneDrive).
def get_documents_dir():
    if os.name == "nt":
        try:
            import ctypes
            from ctypes import wintypes
            CSIDL_PERSONAL = 5  # My Documents
            buf = ctypes.create_unicode_buffer(wintypes.MAX_PATH)
            if ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, 0, buf) == 0 and buf.value:
                return buf.value
        except Exception:
            pass
    return os.path.join(os.path.expanduser("~"), "Documents")

class RetirementCountdown:
    # Initialize the countdown window and application state.
    def __init__(self, master):
        self.default_date = "June 1 2027 17:00:00"
        # Store the settings file in the user's Documents folder (follows OneDrive redirection).
        self.settings_file = os.path.join(get_documents_dir(), SETTINGS_FILENAME)
        # Location used by earlier versions; settings are read from here if not yet migrated.
        self.legacy_settings_file = os.path.join(os.path.expanduser("~"), "Documents", SETTINGS_FILENAME)
        self.settings = self.load_settings()
        self.master = master
        master.title("Retirement Countdown")
        master.configure(bg="#1a1a1a")
        master.overrideredirect(True)  # Remove title bar
        master.attributes('-alpha', 0.7)  # Make window translucent
        self.is_topmost = tk.BooleanVar(value=True)

        # Try to load a previously saved retirement date; if not available, prompt the user.
        saved_date = self.load_saved_date()
        if saved_date:
            self.retirement_date = saved_date
        else:
            self.retirement_date = self.prompt_for_date(self.default_date) or self.default_date
            self.save_retirement_date(self.retirement_date)
        self.target_dt = self.parse_date(self.retirement_date)
        self.holidays = self.load_holidays()
        self.setup_ui()
        self.update_countdown()
        self.setup_popup_menu()
        self.set_topmost()
        # Restore previous window position if available; otherwise use default reset.
        if not self.restore_window_position():
            self.reset_position()
        self.master.protocol("WM_DELETE_WINDOW", self.on_close)

    # Build the visible labels and mouse bindings for the window.
    def setup_ui(self):
        self.frame = tk.Frame(self.master, bg="#1a1a1a")
        self.frame.pack(expand=True, fill=tk.BOTH)
        self.target_label = tk.Label(self.frame, text="", font=("Helvetica", 10, "italic"), fg="#888888", bg="#1a1a1a")
        self.target_label.pack(pady=(1,1))
        self.countdown_label = tk.Label(self.frame, text="", font=("Helvetica", 16, "bold"), fg="#00ffcc", bg="#1a1a1a")
        self.countdown_label.pack(pady=(2,2))
        self.workdays_label = tk.Label(self.frame, text="", font=("Helvetica", 10), fg="#99ddff", bg="#1a1a1a")
        self.workdays_label.pack(pady=(1,2))
        self.message_label = tk.Label(self.frame, text="", font=("Helvetica", 12), fg="#cccccc", bg="#1a1a1a")
        self.message_label.pack(pady=(1,3))
        self.frame.bind("<Button-3>", self.show_popup)
        self.master.bind("<Button-3>", self.show_popup)
        # Left click (Button-1) to drag and Right click (Button-2) to popup menu
        self.frame.bind("<ButtonPress-1>", self.start_move)
        self.frame.bind("<B1-Motion>", self.do_move)
        self.master.bind("<ButtonPress-1>", self.start_move)
        self.master.bind("<B1-Motion>", self.do_move)
        self.frame.bind("<ButtonPress-2>", self.start_move)
        self.frame.bind("<B2-Motion>", self.do_move)
        self.master.bind("<ButtonPress-2>", self.start_move)
        self.master.bind("<B2-Motion>", self.do_move)

    # Create the right-click popup menu and its commands.
    def setup_popup_menu(self):
        self.menu = tk.Menu(self.master, tearoff=0, bg="#222", fg="#fff", activebackground="#444", activeforeground="#fff")
        self.menu.add_checkbutton(label="Stay on Top", variable=self.is_topmost, command=self.set_topmost)
        self.menu.add_command(label="Reset Position", command=self.reset_position)
        self.menu.add_separator()
        self.menu.add_command(label="Update Retirement Date", command=self.update_retirement_date)
        self.menu.add_separator()
        self.menu.add_command(label="About", command=self.show_about)
        self.menu.add_separator()
        self.menu.add_command(label="Close App", command=self.on_close)

    # Record the starting mouse and window position for dragging.
    def start_move(self, event):
        self._drag_start_x = event.x_root
        self._drag_start_y = event.y_root
        self._start_win_x = self.master.winfo_x()
        self._start_win_y = self.master.winfo_y()

    # Move the window based on mouse drag distance.
    def do_move(self, event):
        dx = event.x_root - self._drag_start_x
        dy = event.y_root - self._drag_start_y
        new_x = self._start_win_x + dx
        new_y = self._start_win_y + dy
        self.master.geometry(f"+{new_x}+{new_y}")

    # Show the popup menu at the mouse position.
    def show_popup(self, event):
        try:
            self.menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.menu.grab_release()

    # Show an About dialog with version information.
    def show_about(self):
        about_text = (
            f"{APP_NAME}\n"
            f"Version {VERSION}\n"
            "By Michael Jacobson\n\n"
            "A compact desktop countdown for tracking a retirement date, "
            "with saved settings in your Documents folder.\n\n"
            "Released under the MIT License.\n\n"
            "To skip holidays in the workday count, add a \"holidays\" list "
            "of \"YYYY-MM-DD\" dates to retirement_settings.json."
        )
        messagebox.showinfo(f"About {APP_NAME}", about_text, parent=self.master)

    # Apply the current stay-on-top setting to the window.
    def set_topmost(self):
        self.master.attributes("-topmost", self.is_topmost.get())

    # Reset the window to the default position in the bottom-right corner, above the taskbar.
    def reset_position(self):
        w, h = WINDOW_WIDTH, WINDOW_HEIGHT
        screen_w = self.master.winfo_screenwidth()
        screen_h = self.master.winfo_screenheight()
        x = screen_w - w - 5
        y = screen_h - h - 50
        self.master.geometry(f"{w}x{h}+{x}+{y}")

    # Prompt until the user enters a valid retirement date string.
    # Returns the date string, or None if the user cancels.
    def prompt_for_date(self, initial):
        while True:
            date_str = self.ask_date_string(initial)
            if not date_str:
                return None
            date_str = date_str.strip()
            try:
                self.parse_date(date_str)
                return date_str
            except ValueError:
                messagebox.showerror(
                    "Invalid date",
                    "Could not understand that date.\n"
                    "Use a format like: June 1 2027 17:00:00 or June 1 2027",
                    parent=self.master
                )
                initial = date_str

    # Show the date entry dialog centered on the screen.
    def ask_date_string(self, initial):
        self.master.update_idletasks()
        temp_parent = tk.Toplevel(self.master)
        temp_parent.withdraw()
        temp_parent.transient(self.master)
        dialog_width = 320
        dialog_height = 120
        screen_w = self.master.winfo_screenwidth()
        screen_h = self.master.winfo_screenheight()
        x = (screen_w - dialog_width) // 2
        y = (screen_h - dialog_height) // 2
        temp_parent.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
        date_str = simpledialog.askstring(
            "Set Retirement Date",
            "Enter retirement date (e.g. June 1 2027 17:00:00):",
            initialvalue=initial,
            parent=temp_parent
        )
        temp_parent.destroy()
        return date_str

    # Load all settings from JSON (retirement date, window position, etc.).
    def load_settings(self):
        try:
            path = self.settings_file
            if not os.path.exists(path):
                # Fall back to the old location; the next save writes to the new one.
                path = self.legacy_settings_file
            if not os.path.exists(path):
                return {}
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                return data
            return {}
        except Exception:
            return {}

    # Load a previously saved retirement date from JSON, if available.
    def load_saved_date(self):
        date_str = self.settings.get("retirement_date")
        if not date_str:
            return None
        # Validate the date string can be parsed; if not, ignore it.
        try:
            self.parse_date(date_str)
        except (ValueError, TypeError):
            return None
        return date_str

    # Load optional holidays (list of "YYYY-MM-DD" strings) from settings.
    # Invalid entries are ignored. Holidays are excluded from the workday count.
    def load_holidays(self):
        holidays = set()
        entries = self.settings.get("holidays", [])
        if not isinstance(entries, list):
            return holidays
        for entry in entries:
            try:
                holidays.add(datetime.datetime.strptime(str(entry), "%Y-%m-%d").date())
            except ValueError:
                pass
        return holidays

    # Save the current retirement date to JSON.
    def save_retirement_date(self, date_str):
        try:
            self.settings["retirement_date"] = date_str
            self.save_settings()
        except Exception:
            # If saving fails, fail silently; the app still functions, just without persistence.
            pass

    # Save all settings to JSON.
    def save_settings(self):
        try:
            os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
            with open(self.settings_file, "w", encoding="utf-8") as f:
                json.dump(self.settings, f)
        except Exception:
            pass

    # Restore window position from settings, if available.
    def restore_window_position(self):
        try:
            pos = self.settings.get("window_position")
            if not pos:
                return False
            x = pos.get("x")
            y = pos.get("y")
            w = pos.get("width", WINDOW_WIDTH)
            h = pos.get("height", WINDOW_HEIGHT)
            if x is None or y is None:
                return False
            self.master.geometry(f"{w}x{h}+{x}+{y}")
            return True
        except Exception:
            return False

    # Save the current window position into settings.
    def save_window_position(self):
        try:
            x = self.master.winfo_x()
            y = self.master.winfo_y()
            w = self.master.winfo_width()
            h = self.master.winfo_height()
            self.settings["window_position"] = {"x": x, "y": y, "width": w, "height": h}
            self.save_settings()
        except Exception:
            pass

    # Handle application close: save window position and then close.
    def on_close(self):
        self.save_window_position()
        self.master.destroy()

    # Ask for a new retirement date and refresh the display.
    # Cancelling the dialog keeps the current date.
    def update_retirement_date(self):
        date_str = self.prompt_for_date(self.retirement_date)
        if not date_str:
            return
        self.retirement_date = date_str
        self.target_dt = self.parse_date(date_str)
        self.save_retirement_date(self.retirement_date)
        self.update_countdown(force=True)

    # Convert a date string into a datetime value. Raises ValueError if it can't be parsed.
    def parse_date(self, date_str):
        for fmt in DATE_FORMATS:
            try:
                return datetime.datetime.strptime(date_str, fmt)
            except ValueError:
                pass
        raise ValueError(f"Unrecognized date: {date_str!r}")

    # Return the message for today; it stays the same all day and changes at midnight.
    def get_daily_message(self):
        return random.Random(datetime.date.today().toordinal()).choice(MESSAGES)

    # Count weekdays (excluding holidays) after today, up to and including the target date.
    # Today is not counted; the retirement day itself is, since it is still a day of work.
    def get_workdays_remaining(self, now, target_dt):
        start_date = now.date()
        end_date = target_dt.date()
        if end_date <= start_date:
            return 0
        workdays = 0
        current = start_date
        while current < end_date:
            current += datetime.timedelta(days=1)
            if current.weekday() < 5 and current not in self.holidays:
                workdays += 1
        return workdays

    # Refresh the countdown text and schedule the next update.
    def update_countdown(self, force=False):
        now = datetime.datetime.now()
        diff = self.target_dt - now
        if diff.total_seconds() <= 0:
            self.countdown_label.config(text="Retired!")
            self.workdays_label.config(text="0 workdays")
        else:
            days = diff.days
            hours = diff.seconds // 3600
            mins = (diff.seconds % 3600) // 60
            self.countdown_label.config(text=f"{days}d, {hours}h, {mins}m")
            workdays = self.get_workdays_remaining(now, self.target_dt)
            self.workdays_label.config(text=f"{workdays} workdays")
        self.target_label.config(text=f"Target: {self.target_dt.strftime('%b %d, %Y')}")
        self.message_label.config(text=self.get_daily_message())
        if not force:
            self.master.after(30000, self.update_countdown)

if __name__ == "__main__":
    root = tk.Tk()
    app = RetirementCountdown(root)
    root.mainloop()