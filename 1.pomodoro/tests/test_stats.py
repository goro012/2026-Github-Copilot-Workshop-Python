"""stats モジュールのユニットテスト"""

import sys
import os
from datetime import date, timedelta

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from stats import (
    get_daily_stats,
    get_monthly_stats,
    get_weekly_stats,
    render_bar_chart,
    render_weekly_chart,
)


# ---------------------------------------------------------------------------
# テスト用ヘルパー
# ---------------------------------------------------------------------------

def _make_data(sessions: list | None = None) -> dict:
    sessions = sessions or []
    return {
        "total_xp": 0,
        "level": 1,
        "total_pomodoros": sum(1 for s in sessions if s.get("type") == "pomodoro"),
        "total_breaks": sum(1 for s in sessions if s.get("type") == "break"),
        "sessions": sessions,
        "achievements": {},
        "streak": {"current": 0, "longest": 0, "last_date": None},
    }


def _pomodoro_session(day: date) -> dict:
    return {"date": day.isoformat(), "type": "pomodoro", "completed": True, "timestamp": ""}


def _break_session(day: date) -> dict:
    return {"date": day.isoformat(), "type": "break", "completed": True, "timestamp": ""}


# ---------------------------------------------------------------------------
# get_daily_stats
# ---------------------------------------------------------------------------

class TestGetDailyStats:
    def test_empty_data_returns_zeros(self):
        data = _make_data()
        stats = get_daily_stats(data)
        assert stats["pomodoros"] == 0
        assert stats["breaks"] == 0
        assert stats["focus_minutes"] == 0

    def test_counts_pomodoros_for_target_date(self):
        today = date.today()
        data = _make_data([_pomodoro_session(today), _pomodoro_session(today)])
        stats = get_daily_stats(data, today)
        assert stats["pomodoros"] == 2
        assert stats["focus_minutes"] == 50

    def test_counts_breaks_for_target_date(self):
        today = date.today()
        data = _make_data([_break_session(today)])
        stats = get_daily_stats(data, today)
        assert stats["breaks"] == 1

    def test_ignores_sessions_on_other_days(self):
        yesterday = date.today() - timedelta(days=1)
        data = _make_data([_pomodoro_session(yesterday)])
        stats = get_daily_stats(data, date.today())
        assert stats["pomodoros"] == 0

    def test_date_key_matches_target(self):
        today = date.today()
        data = _make_data()
        stats = get_daily_stats(data, today)
        assert stats["date"] == today.isoformat()

    def test_focus_minutes_is_25_per_pomodoro(self):
        today = date.today()
        sessions = [_pomodoro_session(today)] * 3
        data = _make_data(sessions)
        stats = get_daily_stats(data, today)
        assert stats["focus_minutes"] == 75


# ---------------------------------------------------------------------------
# get_weekly_stats
# ---------------------------------------------------------------------------

class TestGetWeeklyStats:
    def test_returns_exactly_7_days(self):
        data = _make_data()
        stats = get_weekly_stats(data)
        assert len(stats["daily"]) == 7

    def test_week_starts_on_monday(self):
        data = _make_data()
        stats = get_weekly_stats(data)
        week_start = date.fromisoformat(stats["week_start"])
        assert week_start.weekday() == 0  # 0 = Monday

    def test_total_pomodoros_sums_daily(self):
        today = date.today()
        data = _make_data([_pomodoro_session(today), _pomodoro_session(today)])
        stats = get_weekly_stats(data, today)
        assert stats["total_pomodoros"] == 2

    def test_total_focus_minutes_correct(self):
        today = date.today()
        data = _make_data([_pomodoro_session(today)])
        stats = get_weekly_stats(data, today)
        assert stats["total_focus_minutes"] == 25

    def test_avg_daily_pomodoros_correct(self):
        today = date.today()
        data = _make_data([_pomodoro_session(today)] * 7)
        stats = get_weekly_stats(data, today)
        assert abs(stats["avg_daily_pomodoros"] - 1.0) < 0.01


# ---------------------------------------------------------------------------
# get_monthly_stats
# ---------------------------------------------------------------------------

class TestGetMonthlyStats:
    def test_basic_structure(self):
        data = _make_data()
        stats = get_monthly_stats(data)
        assert "month" in stats
        assert "total_pomodoros" in stats
        assert "total_focus_minutes" in stats
        assert "active_days" in stats
        assert "avg_daily_pomodoros" in stats

    def test_active_days_counts_days_with_pomodoros(self):
        today = date.today()
        data = _make_data([_pomodoro_session(today)])
        stats = get_monthly_stats(data, today)
        assert stats["active_days"] == 1

    def test_total_pomodoros_for_current_month(self):
        today = date.today()
        data = _make_data([_pomodoro_session(today), _pomodoro_session(today)])
        stats = get_monthly_stats(data, today)
        assert stats["total_pomodoros"] == 2

    def test_month_format(self):
        data = _make_data()
        today = date.today()
        stats = get_monthly_stats(data, today)
        assert stats["month"] == today.strftime("%Y-%m")


# ---------------------------------------------------------------------------
# render_bar_chart
# ---------------------------------------------------------------------------

class TestRenderBarChart:
    def test_returns_string(self):
        result = render_bar_chart([1, 2, 3], ["A", "B", "C"])
        assert isinstance(result, str)

    def test_handles_all_zeros(self):
        result = render_bar_chart([0, 0, 0], ["A", "B", "C"])
        assert isinstance(result, str)
        assert len(result) > 0

    def test_labels_appear_in_last_line(self):
        result = render_bar_chart([1, 2, 3], ["A", "B", "C"])
        last_line = result.split("\n")[-1]
        assert "A" in last_line
        assert "B" in last_line
        assert "C" in last_line

    def test_custom_max_height(self):
        result = render_bar_chart([5], ["X"], max_height=5)
        lines = result.split("\n")
        # max_height rows + separator + label = max_height + 2
        assert len(lines) == 7  # 5 + separator + label


# ---------------------------------------------------------------------------
# render_weekly_chart
# ---------------------------------------------------------------------------

class TestRenderWeeklyChart:
    def test_returns_string(self):
        data = _make_data()
        result = render_weekly_chart(data)
        assert isinstance(result, str)

    def test_contains_total_info(self):
        data = _make_data()
        result = render_weekly_chart(data)
        assert "今週の合計" in result

    def test_contains_day_labels(self):
        data = _make_data()
        result = render_weekly_chart(data)
        assert "月" in result
