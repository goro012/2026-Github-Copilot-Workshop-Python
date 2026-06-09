"""統計モジュール: 日次・週次・月次のポモドーロ統計とASCIIグラフ描画"""

from datetime import date, timedelta


# ---------------------------------------------------------------------------
# 統計取得
# ---------------------------------------------------------------------------

def get_daily_stats(data: dict, target_date: date | None = None) -> dict:
    """指定日の統計を返す。"""
    if target_date is None:
        target_date = date.today()

    target_str = target_date.isoformat()
    pomodoros = sum(
        1
        for s in data.get("sessions", [])
        if s.get("date") == target_str
        and s.get("type") == "pomodoro"
        and s.get("completed")
    )
    breaks = sum(
        1
        for s in data.get("sessions", [])
        if s.get("date") == target_str
        and s.get("type") == "break"
        and s.get("completed")
    )
    return {
        "date": target_str,
        "pomodoros": pomodoros,
        "breaks": breaks,
        "focus_minutes": pomodoros * 25,
    }


def get_weekly_stats(data: dict, reference_date: date | None = None) -> dict:
    """今週（月曜始まり）の統計を返す。"""
    if reference_date is None:
        reference_date = date.today()
    week_start = reference_date - timedelta(days=reference_date.weekday())

    daily = [get_daily_stats(data, week_start + timedelta(days=i)) for i in range(7)]
    total_pomodoros = sum(d["pomodoros"] for d in daily)
    total_focus = sum(d["focus_minutes"] for d in daily)

    return {
        "week_start": week_start.isoformat(),
        "daily": daily,
        "total_pomodoros": total_pomodoros,
        "total_focus_minutes": total_focus,
        "avg_daily_pomodoros": total_pomodoros / 7,
    }


def get_monthly_stats(data: dict, reference_date: date | None = None) -> dict:
    """今月の統計を返す。"""
    if reference_date is None:
        reference_date = date.today()
    month_start = reference_date.replace(day=1)
    days_in_month = (reference_date - month_start).days + 1

    daily = [
        get_daily_stats(data, month_start + timedelta(days=i))
        for i in range(days_in_month)
    ]
    total_pomodoros = sum(d["pomodoros"] for d in daily)
    total_focus = sum(d["focus_minutes"] for d in daily)
    active_days = sum(1 for d in daily if d["pomodoros"] > 0)

    return {
        "month": reference_date.strftime("%Y-%m"),
        "daily": daily,
        "total_pomodoros": total_pomodoros,
        "total_focus_minutes": total_focus,
        "active_days": active_days,
        "avg_daily_pomodoros": total_pomodoros / days_in_month,
    }


# ---------------------------------------------------------------------------
# グラフ描画
# ---------------------------------------------------------------------------

def render_bar_chart(
    values: list[int],
    labels: list[str],
    max_height: int = 10,
) -> str:
    """シンプルなASCIIバーチャートを返す。"""
    max_val = max(values) if values and max(values) > 0 else 1
    lines: list[str] = []

    for row in range(max_height, 0, -1):
        threshold = (row / max_height) * max_val
        line = " ".join("█" if v >= threshold else " " for v in values)
        lines.append(line)

    separator = "─" * max(len(labels) * 2 - 1, 1)
    lines.append(separator)
    lines.append(" ".join(lbl[:1] for lbl in labels))

    return "\n".join(lines)


def render_weekly_chart(data: dict) -> str:
    """今週のポモドーロ数をバーチャートで表示した文字列を返す。"""
    stats = get_weekly_stats(data)
    values = [d["pomodoros"] for d in stats["daily"]]
    labels = ["月", "火", "水", "木", "金", "土", "日"]

    lines = ["📊 今週の進捗", ""]
    lines.append(render_bar_chart(values, labels))
    lines.append(f"\n今週の合計: {stats['total_pomodoros']}回 / {stats['total_focus_minutes']}分")
    lines.append(f"1日平均: {stats['avg_daily_pomodoros']:.1f}回")

    return "\n".join(lines)
