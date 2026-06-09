"""ゲーミフィケーションモジュール: XP・レベル・実績・ストリーク"""

from datetime import date, datetime
from typing import Optional

XP_PER_POMODORO = 25
XP_PER_BREAK = 5

# (レベル, そのレベルに必要な累計XP)
LEVEL_THRESHOLDS: list[tuple[int, int]] = [
    (1, 0),
    (2, 100),
    (3, 250),
    (4, 500),
    (5, 1000),
    (6, 2000),
    (7, 3500),
    (8, 5500),
    (9, 8000),
    (10, 11000),
]

ACHIEVEMENTS: dict[str, dict] = {
    "first_pomodoro": {
        "name": "🍅 初めの一歩",
        "description": "最初のポモドーロを完了",
        "condition": lambda data: data["total_pomodoros"] >= 1,
    },
    "streak_3": {
        "name": "🔥 3日連続",
        "description": "3日連続でポモドーロを完了",
        "condition": lambda data: data["streak"]["current"] >= 3,
    },
    "streak_7": {
        "name": "⚡ 7日連続",
        "description": "7日連続でポモドーロを完了",
        "condition": lambda data: data["streak"]["current"] >= 7,
    },
    "week_warrior": {
        "name": "🏆 週の戦士",
        "description": "1週間で10回のポモドーロを完了",
        "condition": lambda data: _weekly_pomodoro_count(data) >= 10,
    },
    "focus_master": {
        "name": "🎯 集中マスター",
        "description": "合計50回のポモドーロを完了",
        "condition": lambda data: data["total_pomodoros"] >= 50,
    },
    "century": {
        "name": "💯 100回達成",
        "description": "合計100回のポモドーロを完了",
        "condition": lambda data: data["total_pomodoros"] >= 100,
    },
    "level_5": {
        "name": "⭐ レベル5到達",
        "description": "レベル5に到達",
        "condition": lambda data: data["level"] >= 5,
    },
    "level_10": {
        "name": "🌟 レベル10到達",
        "description": "レベル10に到達",
        "condition": lambda data: data["level"] >= 10,
    },
}


# ---------------------------------------------------------------------------
# 内部ヘルパー
# ---------------------------------------------------------------------------

def _weekly_pomodoro_count(data: dict) -> int:
    """今週（月曜始まり）の完了ポモドーロ数を返す。"""
    today = date.today()
    week_start_ordinal = today.toordinal() - today.weekday()
    count = 0
    for session in data.get("sessions", []):
        if session.get("type") == "pomodoro" and session.get("completed"):
            session_date = date.fromisoformat(session["date"])
            if session_date.toordinal() >= week_start_ordinal:
                count += 1
    return count


def _update_streak(data: dict, today_str: str) -> None:
    """ストリークを更新する。"""
    last_date = data["streak"]["last_date"]
    if last_date is None:
        data["streak"]["current"] = 1
    else:
        last = date.fromisoformat(last_date)
        today_date = date.fromisoformat(today_str)
        delta = (today_date - last).days
        if delta == 0:
            return  # 同日は変更なし
        elif delta == 1:
            data["streak"]["current"] += 1
        else:
            data["streak"]["current"] = 1

    data["streak"]["last_date"] = today_str
    if data["streak"]["current"] > data["streak"]["longest"]:
        data["streak"]["longest"] = data["streak"]["current"]


def _check_achievements(data: dict) -> list[str]:
    """未解除の実績を確認し、新たに解除されたものの名前リストを返す。"""
    if "achievements" not in data:
        data["achievements"] = {}

    new_achievements: list[str] = []
    for key, achievement in ACHIEVEMENTS.items():
        already_unlocked = data["achievements"].get(key, {}).get("unlocked", False)
        if not already_unlocked and achievement["condition"](data):
            data["achievements"][key] = {
                "unlocked": True,
                "unlocked_at": datetime.now().isoformat(),
            }
            new_achievements.append(achievement["name"])

    return new_achievements


# ---------------------------------------------------------------------------
# 公開API
# ---------------------------------------------------------------------------

def compute_level(xp: int) -> int:
    """XP値から現在のレベルを計算する。"""
    level = 1
    for lvl, threshold in LEVEL_THRESHOLDS:
        if xp >= threshold:
            level = lvl
    return level


def xp_for_next_level(current_level: int) -> Optional[int]:
    """次のレベルに必要な累計XPを返す。最大レベルの場合は None。"""
    for lvl, threshold in LEVEL_THRESHOLDS:
        if lvl == current_level + 1:
            return threshold
    return None


def add_pomodoro(data: dict) -> tuple[int, bool, list[str]]:
    """完了したポモドーロを記録する。

    Returns:
        (獲得XP, レベルアップしたか, 新たに解除された実績名リスト)
    """
    old_level = data["level"]
    data["total_xp"] += XP_PER_POMODORO
    data["total_pomodoros"] += 1
    data["level"] = compute_level(data["total_xp"])

    today_str = date.today().isoformat()
    data["sessions"].append(
        {
            "date": today_str,
            "type": "pomodoro",
            "completed": True,
            "timestamp": datetime.now().isoformat(),
        }
    )

    _update_streak(data, today_str)
    new_achievements = _check_achievements(data)
    leveled_up = data["level"] > old_level

    return XP_PER_POMODORO, leveled_up, new_achievements


def add_break(data: dict) -> int:
    """完了した休憩を記録する。

    Returns:
        獲得XP
    """
    data["total_xp"] += XP_PER_BREAK
    data["total_breaks"] += 1
    data["level"] = compute_level(data["total_xp"])

    today_str = date.today().isoformat()
    data["sessions"].append(
        {
            "date": today_str,
            "type": "break",
            "completed": True,
            "timestamp": datetime.now().isoformat(),
        }
    )

    return XP_PER_BREAK
