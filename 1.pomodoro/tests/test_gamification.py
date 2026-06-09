"""gamification モジュールのユニットテスト"""

import sys
import os
from datetime import date, timedelta

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gamification import (
    XP_PER_BREAK,
    XP_PER_POMODORO,
    LEVEL_THRESHOLDS,
    _check_achievements,
    _update_streak,
    add_break,
    add_pomodoro,
    compute_level,
    xp_for_next_level,
)


# ---------------------------------------------------------------------------
# テスト用フィクスチャ
# ---------------------------------------------------------------------------

def _empty_data() -> dict:
    return {
        "total_xp": 0,
        "level": 1,
        "total_pomodoros": 0,
        "total_breaks": 0,
        "sessions": [],
        "achievements": {},
        "streak": {"current": 0, "longest": 0, "last_date": None},
    }


# ---------------------------------------------------------------------------
# compute_level
# ---------------------------------------------------------------------------

class TestComputeLevel:
    def test_level_1_at_zero_xp(self):
        assert compute_level(0) == 1

    def test_level_1_just_below_threshold(self):
        assert compute_level(99) == 1

    def test_level_2_at_exactly_100_xp(self):
        assert compute_level(100) == 2

    def test_level_3_at_250_xp(self):
        assert compute_level(250) == 3

    def test_level_5_at_1000_xp(self):
        assert compute_level(1000) == 5

    def test_max_level_with_large_xp(self):
        assert compute_level(999_999) == 10

    def test_each_threshold_gives_correct_level(self):
        for lvl, threshold in LEVEL_THRESHOLDS:
            assert compute_level(threshold) == lvl


# ---------------------------------------------------------------------------
# xp_for_next_level
# ---------------------------------------------------------------------------

class TestXpForNextLevel:
    def test_returns_100_for_level_1(self):
        assert xp_for_next_level(1) == 100

    def test_returns_none_for_max_level(self):
        max_level = LEVEL_THRESHOLDS[-1][0]
        assert xp_for_next_level(max_level) is None

    def test_returns_next_threshold(self):
        for i in range(len(LEVEL_THRESHOLDS) - 1):
            current_lvl = LEVEL_THRESHOLDS[i][0]
            next_threshold = LEVEL_THRESHOLDS[i + 1][1]
            assert xp_for_next_level(current_lvl) == next_threshold


# ---------------------------------------------------------------------------
# add_pomodoro
# ---------------------------------------------------------------------------

class TestAddPomodoro:
    def test_returns_correct_xp(self):
        data = _empty_data()
        xp, _, _ = add_pomodoro(data)
        assert xp == XP_PER_POMODORO

    def test_total_xp_incremented(self):
        data = _empty_data()
        add_pomodoro(data)
        assert data["total_xp"] == XP_PER_POMODORO

    def test_total_pomodoros_incremented(self):
        data = _empty_data()
        add_pomodoro(data)
        assert data["total_pomodoros"] == 1

    def test_session_recorded_as_pomodoro(self):
        data = _empty_data()
        add_pomodoro(data)
        assert len(data["sessions"]) == 1
        session = data["sessions"][0]
        assert session["type"] == "pomodoro"
        assert session["completed"] is True
        assert "date" in session
        assert "timestamp" in session

    def test_level_up_when_xp_crosses_threshold(self):
        data = _empty_data()
        data["total_xp"] = 80  # +25 = 105 >= 100 → level 2
        _, leveled_up, _ = add_pomodoro(data)
        assert leveled_up is True
        assert data["level"] == 2

    def test_no_level_up_when_xp_stays_below_threshold(self):
        data = _empty_data()
        data["total_xp"] = 0
        _, leveled_up, _ = add_pomodoro(data)
        assert leveled_up is False
        assert data["level"] == 1

    def test_first_pomodoro_achievement_unlocked(self):
        data = _empty_data()
        _, _, achievements = add_pomodoro(data)
        assert any("初めの一歩" in a for a in achievements)

    def test_streak_starts_at_1(self):
        data = _empty_data()
        add_pomodoro(data)
        assert data["streak"]["current"] == 1


# ---------------------------------------------------------------------------
# add_break
# ---------------------------------------------------------------------------

class TestAddBreak:
    def test_returns_correct_xp(self):
        data = _empty_data()
        xp = add_break(data)
        assert xp == XP_PER_BREAK

    def test_total_xp_incremented(self):
        data = _empty_data()
        add_break(data)
        assert data["total_xp"] == XP_PER_BREAK

    def test_total_breaks_incremented(self):
        data = _empty_data()
        add_break(data)
        assert data["total_breaks"] == 1

    def test_session_recorded_as_break(self):
        data = _empty_data()
        add_break(data)
        assert len(data["sessions"]) == 1
        assert data["sessions"][0]["type"] == "break"


# ---------------------------------------------------------------------------
# _update_streak
# ---------------------------------------------------------------------------

class TestUpdateStreak:
    def test_first_session_sets_streak_to_1(self):
        data = _empty_data()
        _update_streak(data, date.today().isoformat())
        assert data["streak"]["current"] == 1
        assert data["streak"]["longest"] == 1

    def test_consecutive_days_increments_streak(self):
        data = _empty_data()
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        data["streak"]["current"] = 1
        data["streak"]["longest"] = 1
        data["streak"]["last_date"] = yesterday
        _update_streak(data, date.today().isoformat())
        assert data["streak"]["current"] == 2
        assert data["streak"]["longest"] == 2

    def test_same_day_does_not_change_streak(self):
        data = _empty_data()
        today = date.today().isoformat()
        data["streak"]["current"] = 3
        data["streak"]["longest"] = 3
        data["streak"]["last_date"] = today
        _update_streak(data, today)
        assert data["streak"]["current"] == 3

    def test_gap_resets_current_streak(self):
        data = _empty_data()
        old_date = (date.today() - timedelta(days=3)).isoformat()
        data["streak"]["current"] = 5
        data["streak"]["longest"] = 5
        data["streak"]["last_date"] = old_date
        _update_streak(data, date.today().isoformat())
        assert data["streak"]["current"] == 1

    def test_gap_preserves_longest_streak(self):
        data = _empty_data()
        old_date = (date.today() - timedelta(days=3)).isoformat()
        data["streak"]["current"] = 5
        data["streak"]["longest"] = 5
        data["streak"]["last_date"] = old_date
        _update_streak(data, date.today().isoformat())
        assert data["streak"]["longest"] == 5

    def test_longest_updated_when_exceeded(self):
        data = _empty_data()
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        data["streak"]["current"] = 9
        data["streak"]["longest"] = 9
        data["streak"]["last_date"] = yesterday
        _update_streak(data, date.today().isoformat())
        assert data["streak"]["current"] == 10
        assert data["streak"]["longest"] == 10


# ---------------------------------------------------------------------------
# _check_achievements
# ---------------------------------------------------------------------------

class TestCheckAchievements:
    def test_first_pomodoro_unlocked_at_1(self):
        data = _empty_data()
        data["total_pomodoros"] = 1
        new = _check_achievements(data)
        assert any("初めの一歩" in a for a in new)

    def test_streak_3_unlocked_at_streak_3(self):
        data = _empty_data()
        data["streak"]["current"] = 3
        new = _check_achievements(data)
        assert any("3日連続" in a for a in new)

    def test_streak_7_unlocked_at_streak_7(self):
        data = _empty_data()
        data["streak"]["current"] = 7
        new = _check_achievements(data)
        assert any("7日連続" in a for a in new)

    def test_focus_master_at_50_pomodoros(self):
        data = _empty_data()
        data["total_pomodoros"] = 50
        new = _check_achievements(data)
        assert any("集中マスター" in a for a in new)

    def test_century_at_100_pomodoros(self):
        data = _empty_data()
        data["total_pomodoros"] = 100
        new = _check_achievements(data)
        assert any("100回達成" in a for a in new)

    def test_already_unlocked_achievement_not_repeated(self):
        data = _empty_data()
        data["total_pomodoros"] = 1
        data["achievements"]["first_pomodoro"] = {
            "unlocked": True,
            "unlocked_at": "2026-01-01T00:00:00",
        }
        new = _check_achievements(data)
        assert not any("初めの一歩" in a for a in new)

    def test_level_5_achievement(self):
        data = _empty_data()
        data["level"] = 5
        new = _check_achievements(data)
        assert any("レベル5" in a for a in new)
