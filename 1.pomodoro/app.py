# Pomodoro Timer App
import tkinter as tk
import math
import random


# ---------------------------------------------------------------------------
# Color helpers
# ---------------------------------------------------------------------------

def lerp_color(c1: tuple, c2: tuple, t: float) -> str:
    """Linear interpolation between two RGB tuples; returns a hex color string."""
    r = int(c1[0] + (c2[0] - c1[0]) * t)
    g = int(c1[1] + (c2[1] - c1[1]) * t)
    b = int(c1[2] + (c2[2] - c1[2]) * t)
    return f"#{r:02x}{g:02x}{b:02x}"


def progress_color(progress: float) -> str:
    """Return a hex color that smoothly transitions blue→yellow→red.

    progress: 1.0 = time just started (full), 0.0 = time almost up.
    """
    BLUE   = (30, 144, 255)   # dodger blue
    YELLOW = (255, 215,   0)  # golden yellow
    RED    = (255,  50,  50)  # vivid red

    if progress >= 0.5:
        t = (progress - 0.5) / 0.5   # 1.0 → 0.0 as progress goes 1.0 → 0.5
        return lerp_color(YELLOW, BLUE, t)
    else:
        t = progress / 0.5            # 1.0 → 0.0 as progress goes 0.5 → 0.0
        return lerp_color(RED, YELLOW, t)


# ---------------------------------------------------------------------------
# Particle / ripple data helpers
# ---------------------------------------------------------------------------

def make_particle(width: int, height: int) -> dict:
    return {
        "x": random.uniform(0, width),
        "y": random.uniform(0, height),
        "size": random.uniform(1.5, 3.5),
        "vy": random.uniform(0.3, 1.2),   # upward drift speed
        "vx": random.uniform(-0.3, 0.3),
    }


def make_ripple(width: int, height: int) -> dict:
    return {
        "x": random.uniform(width * 0.15, width * 0.85),
        "y": random.uniform(height * 0.15, height * 0.85),
        "r": 4.0,
        "max_r": random.uniform(40, 90),
    }


# ---------------------------------------------------------------------------
# Main application class
# ---------------------------------------------------------------------------

class PomodoroTimer:
    FOCUS_TIME      = 25 * 60   # seconds
    SHORT_BREAK     = 5  * 60
    LONG_BREAK      = 15 * 60

    # Canvas dimensions
    W = 520
    H = 560

    # Progress arc geometry
    CX = W // 2
    CY = H // 2 - 20
    RADIUS        = 185
    ARC_WIDTH     = 18
    TICK_MS       = 50    # animation frame interval (ms)

    # Ripple animation constants
    RIPPLE_SPAWN_PROBABILITY = 0.04
    RIPPLE_GROWTH_RATE       = 1.8
    RIPPLE_MAX_WIDTH         = 2.5

    # Background gradient colors
    BACKGROUND_COLORS = ["#0d1117", "#0f1320", "#0d1117"]

    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("ポモドーロタイマー")
        self.root.configure(bg="#0d1117")
        self.root.resizable(False, False)

        # Timer state
        self.total_time     = self.FOCUS_TIME
        self.remaining      = self.FOCUS_TIME
        self.is_running     = False
        self.is_focus       = True
        self.session_count  = 0

        # Animation state
        self.particles: list[dict] = [
            make_particle(self.W, self.H)
            for _ in range(int(self.W * self.H / 5000))
        ]
        self.ripples:   list[dict] = []
        self._elapsed_ticks = 0   # counts animation frames for 1-second countdown

        self._build_ui()
        self._tick()   # start the animation + timer loop

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        self.canvas = tk.Canvas(
            self.root,
            width=self.W,
            height=self.H,
            bg="#0d1117",
            highlightthickness=0,
        )
        self.canvas.pack()

        btn_frame = tk.Frame(self.root, bg="#0d1117")
        btn_frame.pack(pady=(0, 16))

        btn_kw = dict(
            font=("Helvetica", 14, "bold"),
            bg="#161b22",
            fg="#e6edf3",
            activebackground="#21262d",
            activeforeground="#ffffff",
            relief="flat",
            cursor="hand2",
            padx=22,
            pady=9,
            bd=0,
        )

        self.start_btn = tk.Button(
            btn_frame,
            text="▶  スタート",
            command=self._toggle,
            **btn_kw,
        )
        self.start_btn.grid(row=0, column=0, padx=10)

        tk.Button(
            btn_frame,
            text="↺  リセット",
            command=self._reset,
            **btn_kw,
        ).grid(row=0, column=1, padx=10)

        self.session_lbl = tk.Label(
            self.root,
            text="セッション: 0",
            font=("Helvetica", 11),
            bg="#0d1117",
            fg="#484f58",
        )
        self.session_lbl.pack(pady=(0, 10))

    # ------------------------------------------------------------------
    # Animation + timer tick (single loop for both)
    # ------------------------------------------------------------------

    def _tick(self) -> None:
        """Called every TICK_MS milliseconds – drives animation AND countdown."""
        # ---- countdown logic (once per 1000 ms / TICK_MS frames) --------
        ticks_per_second = 1000 // self.TICK_MS
        if self.is_running:
            self._elapsed_ticks += 1
            if self._elapsed_ticks >= ticks_per_second:
                self._elapsed_ticks = 0
                if self.remaining > 0:
                    self.remaining -= 1
                else:
                    self._on_complete()

        # ---- particle / ripple update ------------------------------------
        if self.is_running and self.is_focus:
            self._update_particles()
            self._update_ripples()

        # ---- draw --------------------------------------------------------
        self._draw()

        self.root.after(self.TICK_MS, self._tick)

    # ------------------------------------------------------------------
    # Particle & ripple animation helpers
    # ------------------------------------------------------------------

    def _update_particles(self) -> None:
        for p in self.particles:
            p["y"] -= p["vy"]
            p["x"] += p["vx"]
            if p["y"] < -6 or p["x"] < -6 or p["x"] > self.W + 6:
                # Respawn at bottom with fresh random values
                p["x"]   = random.uniform(0, self.W)
                p["y"]   = self.H + random.uniform(0, 20)
                p["size"] = random.uniform(1.5, 3.5)
                p["vy"]  = random.uniform(0.3, 1.2)
                p["vx"]  = random.uniform(-0.3, 0.3)

    def _update_ripples(self) -> None:
        # Spawn new ripple with low probability
        if random.random() < self.RIPPLE_SPAWN_PROBABILITY:
            self.ripples.append(make_ripple(self.W, self.H))

        alive = []
        for r in self.ripples:
            r["r"] += self.RIPPLE_GROWTH_RATE
            if r["r"] < r["max_r"]:
                alive.append(r)
        self.ripples = alive

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------

    def _draw(self) -> None:
        c = self.canvas
        c.delete("all")

        # Background gradient via stacked rectangles (subtle radial feel)
        for i, shade in enumerate(self.BACKGROUND_COLORS):
            margin = i * 80
            c.create_rectangle(
                margin, margin, self.W - margin, self.H - margin,
                fill=shade, outline="",
            )

        progress = self.remaining / self.total_time if self.total_time else 0.0
        color    = progress_color(progress)

        # ---- particles (behind everything) -------------------------------
        if self.is_running and self.is_focus:
            for p in self.particles:
                x, y, s = p["x"], p["y"], p["size"]
                c.create_oval(x - s, y - s, x + s, y + s, fill=color, outline="")

        # ---- ripples (behind arc) ----------------------------------------
        if self.is_running and self.is_focus:
            for r in self.ripples:
                alpha_ratio = 1.0 - r["r"] / r["max_r"]
                lw = max(1, int(self.RIPPLE_MAX_WIDTH * alpha_ratio))
                rx, ry, rr = r["x"], r["y"], r["r"]
                c.create_oval(
                    rx - rr, ry - rr, rx + rr, ry + rr,
                    outline=color,
                    width=lw,
                    fill="",
                )

        # ---- background arc (full circle, dark track) --------------------
        cx, cy, R = self.CX, self.CY, self.RADIUS
        c.create_arc(
            cx - R, cy - R, cx + R, cy + R,
            start=90, extent=-360,
            style="arc", outline="#21262d", width=self.ARC_WIDTH,
        )

        # ---- progress arc ------------------------------------------------
        extent = -360.0 * progress
        if abs(extent) > 0.5:
            c.create_arc(
                cx - R, cy - R, cx + R, cy + R,
                start=90, extent=extent,
                style="arc", outline=color, width=self.ARC_WIDTH,
            )

            # Glowing dot at the arc tip
            angle_rad = math.radians(90 + extent)
            tip_x = cx + R * math.cos(angle_rad)
            tip_y = cy - R * math.sin(angle_rad)
            gs = self.ARC_WIDTH // 2 + 2
            c.create_oval(
                tip_x - gs, tip_y - gs, tip_x + gs, tip_y + gs,
                fill=color, outline="",
            )

        # ---- inner circle (mask over background elements) ----------------
        inner_r = R - self.ARC_WIDTH // 2 - 4
        c.create_oval(
            cx - inner_r, cy - inner_r,
            cx + inner_r, cy + inner_r,
            fill="#0d1117", outline="",
        )

        # ---- time text ---------------------------------------------------
        mins = self.remaining // 60
        secs = self.remaining % 60
        c.create_text(
            cx, cy,
            text=f"{mins:02d}:{secs:02d}",
            font=("Helvetica", 52, "bold"),
            fill="#e6edf3",
        )

        # ---- mode label --------------------------------------------------
        mode_txt = "集中" if self.is_focus else ("休憩（長）" if self.total_time == self.LONG_BREAK else "休憩")
        c.create_text(
            cx, cy + 58,
            text=mode_txt,
            font=("Helvetica", 15),
            fill=color,
        )

        # ---- small session dots (up to 4) --------------------------------
        dot_y = cy - R - 28
        dot_spacing = 14
        for i in range(4):
            dx = cx - (4 - 1) * dot_spacing / 2 + i * dot_spacing
            dot_fill = color if i < (self.session_count % 4) else "#21262d"
            c.create_oval(dx - 5, dot_y - 5, dx + 5, dot_y + 5, fill=dot_fill, outline="")

    # ------------------------------------------------------------------
    # Timer state transitions
    # ------------------------------------------------------------------

    def _on_complete(self) -> None:
        self.is_running = False
        self.root.bell()

        if self.is_focus:
            self.session_count += 1
            self.session_lbl.config(text=f"セッション: {self.session_count}")
            self.is_focus    = False
            self.total_time  = self.LONG_BREAK if self.session_count % 4 == 0 else self.SHORT_BREAK
        else:
            self.is_focus   = True
            self.total_time = self.FOCUS_TIME

        self.remaining      = self.total_time
        self._elapsed_ticks = 0
        self.ripples.clear()
        self.start_btn.config(text="▶  スタート")

    def _toggle(self) -> None:
        self.is_running = not self.is_running
        self._elapsed_ticks = 0
        label = "⏸  一時停止" if self.is_running else "▶  スタート"
        self.start_btn.config(text=label)

    def _reset(self) -> None:
        self.is_running     = False
        self.is_focus       = True
        self.total_time     = self.FOCUS_TIME
        self.remaining      = self.FOCUS_TIME
        self._elapsed_ticks = 0
        self.ripples.clear()
        self.start_btn.config(text="▶  スタート")

    # ------------------------------------------------------------------
    # Entry point
    # ------------------------------------------------------------------

    def run(self) -> None:
        self.root.mainloop()


if __name__ == "__main__":
    app = PomodoroTimer()
    app.run()
