# Pomodoro Timer App
import tkinter as tk
from tkinter import ttk, font
import threading
import time


# ---------------------------------------------------------------------------
# Theme definitions
# ---------------------------------------------------------------------------
THEMES = {
    "light": {
        "bg": "#FFFFFF",
        "panel_bg": "#F5F5F5",
        "fg": "#333333",
        "timer_fg": "#333333",
        "btn_bg": "#4CAF50",
        "btn_fg": "#FFFFFF",
        "btn_stop_bg": "#F44336",
        "btn_stop_fg": "#FFFFFF",
        "accent": "#4CAF50",
        "select_bg": "#4CAF50",
        "select_fg": "#FFFFFF",
        "check_fg": "#333333",
        "border": "#CCCCCC",
    },
    "dark": {
        "bg": "#1E1E1E",
        "panel_bg": "#2D2D2D",
        "fg": "#FFFFFF",
        "timer_fg": "#FFFFFF",
        "btn_bg": "#BB86FC",
        "btn_fg": "#000000",
        "btn_stop_bg": "#CF6679",
        "btn_stop_fg": "#000000",
        "accent": "#BB86FC",
        "select_bg": "#BB86FC",
        "select_fg": "#000000",
        "check_fg": "#FFFFFF",
        "border": "#444444",
    },
    "focus": {
        "bg": "#F7F7F7",
        "panel_bg": "#F7F7F7",
        "fg": "#555555",
        "timer_fg": "#222222",
        "btn_bg": "#DDDDDD",
        "btn_fg": "#333333",
        "btn_stop_bg": "#BBBBBB",
        "btn_stop_fg": "#333333",
        "accent": "#888888",
        "select_bg": "#CCCCCC",
        "select_fg": "#333333",
        "check_fg": "#555555",
        "border": "#DDDDDD",
    },
}

WORK_TIMES = [15, 25, 35, 45]   # minutes
BREAK_TIMES = [5, 10, 15]        # minutes
SESSION_WORK = "work"
SESSION_BREAK = "break"


# ---------------------------------------------------------------------------
# Core timer logic (framework-independent)
# ---------------------------------------------------------------------------
class PomodoroEngine:
    """Pure-logic timer engine; no GUI dependencies."""

    def __init__(self, work_minutes: int = 25, break_minutes: int = 5) -> None:
        self.work_minutes = work_minutes
        self.break_minutes = break_minutes
        self.session_type: str = SESSION_WORK
        self.time_remaining: int = work_minutes * 60
        self.running: bool = False
        self._thread: threading.Thread | None = None
        self._lock = threading.Lock()

        # Callbacks (set by the GUI layer)
        self.on_tick = None       # called every second with remaining seconds
        self.on_session_end = None  # called when a session completes
        self.on_start = None
        self.on_pause = None
        self.on_reset = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def start(self) -> None:
        with self._lock:
            if self.running:
                return
            self.running = True
        if self.on_start:
            self.on_start(self.session_type)
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def pause(self) -> None:
        with self._lock:
            self.running = False
        if self.on_pause:
            self.on_pause()

    def reset(self) -> None:
        with self._lock:
            self.running = False
        self.session_type = SESSION_WORK
        self.time_remaining = self.work_minutes * 60
        if self.on_reset:
            self.on_reset()

    def set_work_time(self, minutes: int) -> None:
        self.work_minutes = minutes
        if self.session_type == SESSION_WORK and not self.running:
            self.time_remaining = minutes * 60

    def set_break_time(self, minutes: int) -> None:
        self.break_minutes = minutes
        if self.session_type == SESSION_BREAK and not self.running:
            self.time_remaining = minutes * 60

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------
    def _run(self) -> None:
        while True:
            with self._lock:
                if not self.running:
                    break
                if self.time_remaining <= 0:
                    self.running = False
                    break
                self.time_remaining -= 1
            if self.on_tick:
                self.on_tick(self.time_remaining)
            time.sleep(1)

        # Session finished naturally
        if self.time_remaining <= 0:
            self._switch_session()
            if self.on_session_end:
                self.on_session_end(self.session_type)

    def _switch_session(self) -> None:
        if self.session_type == SESSION_WORK:
            self.session_type = SESSION_BREAK
            self.time_remaining = self.break_minutes * 60
        else:
            self.session_type = SESSION_WORK
            self.time_remaining = self.work_minutes * 60


# ---------------------------------------------------------------------------
# GUI Application
# ---------------------------------------------------------------------------
class PomodoroApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Pomodoro Timer")
        self.root.resizable(False, False)

        # ---- Settings variables ----
        self.theme_var = tk.StringVar(value="light")
        self.work_time_var = tk.IntVar(value=25)
        self.break_time_var = tk.IntVar(value=5)
        self.sound_start_var = tk.BooleanVar(value=True)
        self.sound_end_var = tk.BooleanVar(value=True)
        self.sound_tick_var = tk.BooleanVar(value=False)

        # ---- Timer engine ----
        self.engine = PomodoroEngine(
            work_minutes=self.work_time_var.get(),
            break_minutes=self.break_time_var.get(),
        )
        self.engine.on_tick = self._on_tick
        self.engine.on_session_end = self._on_session_end
        self.engine.on_start = self._on_start
        self.engine.on_pause = self._on_pause
        self.engine.on_reset = self._on_reset_cb

        # ---- Build UI ----
        self._build_ui()
        self._apply_theme()
        self._refresh_display(self.engine.time_remaining)

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------
    def _build_ui(self) -> None:
        pad = {"padx": 10, "pady": 6}

        # --- Main container ---
        self.main_frame = tk.Frame(self.root, padx=20, pady=20)
        self.main_frame.pack(fill="both", expand=True)

        # --- Title ---
        self.title_label = tk.Label(
            self.main_frame, text="🍅 Pomodoro Timer", font=("Helvetica", 18, "bold")
        )
        self.title_label.pack(**pad)

        # --- Session indicator ---
        self.session_label = tk.Label(
            self.main_frame, text="Work Session", font=("Helvetica", 12)
        )
        self.session_label.pack(**pad)

        # --- Timer display ---
        timer_font = font.Font(family="Courier", size=60, weight="bold")
        self.timer_label = tk.Label(
            self.main_frame, text="25:00", font=timer_font
        )
        self.timer_label.pack(pady=10)

        # --- Control buttons ---
        btn_frame = tk.Frame(self.main_frame)
        btn_frame.pack(**pad)

        self.start_btn = tk.Button(
            btn_frame, text="▶  Start", width=10,
            command=self._toggle_start_pause, font=("Helvetica", 12)
        )
        self.start_btn.grid(row=0, column=0, padx=6)

        self.reset_btn = tk.Button(
            btn_frame, text="⏹  Reset", width=10,
            command=self._reset, font=("Helvetica", 12)
        )
        self.reset_btn.grid(row=0, column=1, padx=6)

        # --- Settings panel ---
        settings_frame = tk.LabelFrame(
            self.main_frame, text=" Settings ", font=("Helvetica", 10), padx=10, pady=8
        )
        settings_frame.pack(fill="x", **pad)

        # Work time
        tk.Label(settings_frame, text="Work time (min):", anchor="w").grid(
            row=0, column=0, sticky="w", pady=4
        )
        work_sel = tk.Frame(settings_frame)
        work_sel.grid(row=0, column=1, sticky="w")
        self._work_btns: dict[int, tk.Button] = {}
        for val in WORK_TIMES:
            b = tk.Button(
                work_sel, text=str(val), width=4,
                command=lambda v=val: self._set_work_time(v)
            )
            b.pack(side="left", padx=2)
            self._work_btns[val] = b

        # Break time
        tk.Label(settings_frame, text="Break time (min):", anchor="w").grid(
            row=1, column=0, sticky="w", pady=4
        )
        break_sel = tk.Frame(settings_frame)
        break_sel.grid(row=1, column=1, sticky="w")
        self._break_btns: dict[int, tk.Button] = {}
        for val in BREAK_TIMES:
            b = tk.Button(
                break_sel, text=str(val), width=4,
                command=lambda v=val: self._set_break_time(v)
            )
            b.pack(side="left", padx=2)
            self._break_btns[val] = b

        # Theme
        tk.Label(settings_frame, text="Theme:", anchor="w").grid(
            row=2, column=0, sticky="w", pady=4
        )
        theme_sel = tk.Frame(settings_frame)
        theme_sel.grid(row=2, column=1, sticky="w")
        self._theme_btns: dict[str, tk.Button] = {}
        for t in ("light", "dark", "focus"):
            label = t.capitalize()
            b = tk.Button(
                theme_sel, text=label, width=7,
                command=lambda th=t: self._set_theme(th)
            )
            b.pack(side="left", padx=2)
            self._theme_btns[t] = b

        # Sound settings
        tk.Label(settings_frame, text="Sounds:", anchor="w").grid(
            row=3, column=0, sticky="w", pady=4
        )
        sound_frame = tk.Frame(settings_frame)
        sound_frame.grid(row=3, column=1, sticky="w")
        self.chk_start = tk.Checkbutton(
            sound_frame, text="Start", variable=self.sound_start_var
        )
        self.chk_start.pack(side="left")
        self.chk_end = tk.Checkbutton(
            sound_frame, text="End", variable=self.sound_end_var
        )
        self.chk_end.pack(side="left")
        self.chk_tick = tk.Checkbutton(
            sound_frame, text="Tick", variable=self.sound_tick_var
        )
        self.chk_tick.pack(side="left")

        # Status bar
        self.status_label = tk.Label(
            self.main_frame, text="Ready", font=("Helvetica", 10), anchor="center"
        )
        self.status_label.pack(pady=(8, 0))

    # ------------------------------------------------------------------
    # Theme
    # ------------------------------------------------------------------
    def _apply_theme(self) -> None:
        t = THEMES[self.theme_var.get()]
        self.root.configure(bg=t["bg"])

        def style_widget(w: tk.Widget) -> None:
            cls = w.winfo_class()
            try:
                if cls in ("Frame", "Toplevel"):
                    w.configure(bg=t["bg"])
                elif cls == "LabelFrame":
                    w.configure(bg=t["bg"], fg=t["fg"])
                elif cls == "Label":
                    w.configure(bg=t["bg"], fg=t["fg"])
                elif cls == "Button":
                    w.configure(bg=t["btn_bg"], fg=t["btn_fg"],
                                activebackground=t["accent"],
                                activeforeground=t["btn_fg"],
                                relief="flat", bd=0)
                elif cls == "Checkbutton":
                    w.configure(bg=t["bg"], fg=t["check_fg"],
                                activebackground=t["bg"],
                                selectcolor=t["panel_bg"])
            except tk.TclError:
                pass
            for child in w.winfo_children():
                style_widget(child)

        style_widget(self.main_frame)

        # Timer label gets its own color
        self.timer_label.configure(bg=t["bg"], fg=t["timer_fg"])

        # Highlight selected work/break/theme buttons
        self._highlight_selector_btns()

    def _highlight_selector_btns(self) -> None:
        t = THEMES[self.theme_var.get()]
        for val, btn in self._work_btns.items():
            if val == self.work_time_var.get():
                btn.configure(bg=t["select_bg"], fg=t["select_fg"])
            else:
                btn.configure(bg=t["btn_bg"], fg=t["btn_fg"])
        for val, btn in self._break_btns.items():
            if val == self.break_time_var.get():
                btn.configure(bg=t["select_bg"], fg=t["select_fg"])
            else:
                btn.configure(bg=t["btn_bg"], fg=t["btn_fg"])
        for name, btn in self._theme_btns.items():
            if name == self.theme_var.get():
                btn.configure(bg=t["select_bg"], fg=t["select_fg"])
            else:
                btn.configure(bg=t["btn_bg"], fg=t["btn_fg"])

    # ------------------------------------------------------------------
    # Timer callbacks (called from background thread via root.after)
    # ------------------------------------------------------------------
    def _on_tick(self, remaining: int) -> None:
        self.root.after(0, self._refresh_display, remaining)
        if self.sound_tick_var.get():
            # Play tick every minute boundary
            if remaining % 60 == 0 and remaining > 0:
                self.root.after(0, self.root.bell)

    def _on_session_end(self, next_session: str) -> None:
        def _update() -> None:
            if self.sound_end_var.get():
                self.root.bell()
                self.root.bell()
            label = "Break Session" if next_session == SESSION_BREAK else "Work Session"
            self.session_label.configure(text=label)
            self._refresh_display(self.engine.time_remaining)
            self.start_btn.configure(text="▶  Start")
            self.status_label.configure(
                text=f"Session complete! {'Break' if next_session == SESSION_BREAK else 'Work'} time starts."
            )

        self.root.after(0, _update)

    def _on_start(self, session_type: str) -> None:
        def _update() -> None:
            if self.sound_start_var.get():
                self.root.bell()
            self.start_btn.configure(text="⏸  Pause")
            label = "Work Session" if session_type == SESSION_WORK else "Break Session"
            self.session_label.configure(text=label)
            self.status_label.configure(text="Running…")

        self.root.after(0, _update)

    def _on_pause(self) -> None:
        self.root.after(
            0,
            lambda: (
                self.start_btn.configure(text="▶  Resume"),
                self.status_label.configure(text="Paused"),
            ),
        )

    def _on_reset_cb(self) -> None:
        def _update() -> None:
            self.start_btn.configure(text="▶  Start")
            self.session_label.configure(text="Work Session")
            self._refresh_display(self.engine.time_remaining)
            self.status_label.configure(text="Ready")

        self.root.after(0, _update)

    # ------------------------------------------------------------------
    # User actions
    # ------------------------------------------------------------------
    def _toggle_start_pause(self) -> None:
        if self.engine.running:
            self.engine.pause()
        else:
            self.engine.start()

    def _reset(self) -> None:
        self.engine.reset()

    def _set_work_time(self, minutes: int) -> None:
        self.work_time_var.set(minutes)
        self.engine.set_work_time(minutes)
        if not self.engine.running and self.engine.session_type == SESSION_WORK:
            self._refresh_display(self.engine.time_remaining)
        self._highlight_selector_btns()

    def _set_break_time(self, minutes: int) -> None:
        self.break_time_var.set(minutes)
        self.engine.set_break_time(minutes)
        if not self.engine.running and self.engine.session_type == SESSION_BREAK:
            self._refresh_display(self.engine.time_remaining)
        self._highlight_selector_btns()

    def _set_theme(self, theme: str) -> None:
        self.theme_var.set(theme)
        self._apply_theme()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _refresh_display(self, remaining: int) -> None:
        minutes, seconds = divmod(remaining, 60)
        self.timer_label.configure(text=f"{minutes:02d}:{seconds:02d}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main() -> None:
    root = tk.Tk()
    app = PomodoroApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
