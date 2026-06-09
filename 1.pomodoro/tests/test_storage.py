"""storage モジュールのユニットテスト"""

import copy
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import storage


# ---------------------------------------------------------------------------
# load_data
# ---------------------------------------------------------------------------

class TestLoadData:
    def test_returns_default_when_file_does_not_exist(self, monkeypatch, tmp_path):
        test_file = tmp_path / "nonexistent.json"
        monkeypatch.setattr(storage, "DATA_FILE", test_file)

        data = storage.load_data()

        assert data["total_xp"] == 0
        assert data["level"] == 1
        assert data["total_pomodoros"] == 0
        assert data["total_breaks"] == 0
        assert data["sessions"] == []
        assert data["achievements"] == {}
        assert data["streak"]["current"] == 0
        assert data["streak"]["longest"] == 0
        assert data["streak"]["last_date"] is None

    def test_loads_existing_file(self, monkeypatch, tmp_path):
        test_file = tmp_path / "data.json"
        payload = {
            "total_xp": 250,
            "level": 3,
            "total_pomodoros": 10,
            "total_breaks": 4,
            "sessions": [],
            "achievements": {},
            "streak": {"current": 5, "longest": 7, "last_date": "2026-06-09"},
        }
        test_file.write_text(json.dumps(payload), encoding="utf-8")
        monkeypatch.setattr(storage, "DATA_FILE", test_file)

        data = storage.load_data()

        assert data["total_xp"] == 250
        assert data["level"] == 3
        assert data["streak"]["current"] == 5


# ---------------------------------------------------------------------------
# save_data
# ---------------------------------------------------------------------------

class TestSaveData:
    def test_creates_file(self, monkeypatch, tmp_path):
        test_file = tmp_path / "data.json"
        monkeypatch.setattr(storage, "DATA_FILE", test_file)

        storage.save_data({"total_xp": 0, "level": 1})

        assert test_file.exists()

    def test_saved_content_is_valid_json(self, monkeypatch, tmp_path):
        test_file = tmp_path / "data.json"
        monkeypatch.setattr(storage, "DATA_FILE", test_file)

        storage.save_data({"total_xp": 42})

        loaded = json.loads(test_file.read_text(encoding="utf-8"))
        assert loaded["total_xp"] == 42

    def test_roundtrip_preserves_data(self, monkeypatch, tmp_path):
        test_file = tmp_path / "data.json"
        monkeypatch.setattr(storage, "DATA_FILE", test_file)

        original = {
            "total_xp": 100,
            "level": 2,
            "total_pomodoros": 5,
            "total_breaks": 2,
            "sessions": [{"date": "2026-06-09", "type": "pomodoro", "completed": True, "timestamp": ""}],
            "achievements": {"first_pomodoro": {"unlocked": True, "unlocked_at": "2026-06-09"}},
            "streak": {"current": 3, "longest": 5, "last_date": "2026-06-09"},
        }

        storage.save_data(copy.deepcopy(original))
        loaded = storage.load_data()

        assert loaded["total_xp"] == original["total_xp"]
        assert loaded["streak"]["current"] == original["streak"]["current"]
        assert len(loaded["sessions"]) == 1
        assert loaded["achievements"]["first_pomodoro"]["unlocked"] is True
