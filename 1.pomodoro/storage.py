"""ポモドーロデータの永続化モジュール"""

import json
from pathlib import Path

DATA_FILE = Path(__file__).parent / "pomodoro_data.json"

DEFAULT_DATA: dict = {
    "total_xp": 0,
    "level": 1,
    "total_pomodoros": 0,
    "total_breaks": 0,
    "sessions": [],
    "achievements": {},
    "streak": {
        "current": 0,
        "longest": 0,
        "last_date": None,
    },
}


def load_data() -> dict:
    """保存データを読み込む。ファイルがなければデフォルト値を返す。"""
    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return _deep_copy_default()


def save_data(data: dict) -> None:
    """データをJSONファイルに保存する。"""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _deep_copy_default() -> dict:
    import copy
    return copy.deepcopy(DEFAULT_DATA)
