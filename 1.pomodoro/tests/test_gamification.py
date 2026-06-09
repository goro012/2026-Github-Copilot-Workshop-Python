from datetime import date, datetime, timedelta
from unittest.mock import MagicMock

import pytest

from services import GamificationService


@pytest.fixture()
def mock_repo():
    return MagicMock()


@pytest.fixture()
def service(mock_repo):
    return GamificationService(repo=mock_repo)


def make_session(duration=25, days_ago=0):
    s = MagicMock()
    s.duration = duration
    s.completed_at = datetime.combine(
        date.today() - timedelta(days=days_ago), datetime.min.time()
    )
    return s


class TestGetGamificationStats:
    def test_セッションなしのとき初期値を返す(self, service, mock_repo):
        mock_repo.find_all_sessions.return_value = []

        result = service.get_gamification_stats()

        assert result["total_xp"] == 0
        assert result["level"] == 1
        assert result["xp_in_level"] == 0
        assert result["xp_to_next_level"] == 500
        assert result["streak"] == 0
        assert result["badges"] == []

    def test_1セッション完了でXPが100になる(self, service, mock_repo):
        mock_repo.find_all_sessions.return_value = [make_session()]

        result = service.get_gamification_stats()

        assert result["total_xp"] == 100
        assert result["xp_in_level"] == 100

    def test_5セッション完了でXPが500になりレベル2になる(self, service, mock_repo):
        mock_repo.find_all_sessions.return_value = [make_session() for _ in range(5)]

        result = service.get_gamification_stats()

        assert result["total_xp"] == 500
        assert result["level"] == 2
        assert result["xp_in_level"] == 0

    def test_6セッション完了でレベル2でXP100になる(self, service, mock_repo):
        mock_repo.find_all_sessions.return_value = [make_session() for _ in range(6)]

        result = service.get_gamification_stats()

        assert result["level"] == 2
        assert result["xp_in_level"] == 100
        assert result["xp_to_next_level"] == 400


class TestCalculateStreak:
    def test_今日のセッションでストリーク1(self, service, mock_repo):
        sessions = [make_session(days_ago=0)]
        mock_repo.find_all_sessions.return_value = sessions

        result = service.get_gamification_stats()

        assert result["streak"] == 1

    def test_連続3日でストリーク3(self, service, mock_repo):
        sessions = [make_session(days_ago=i) for i in range(3)]
        mock_repo.find_all_sessions.return_value = sessions

        result = service.get_gamification_stats()

        assert result["streak"] == 3

    def test_途切れた場合はストリークがリセットされる(self, service, mock_repo):
        # 今日と3日前のみ（2日前は抜け）
        sessions = [make_session(days_ago=0), make_session(days_ago=3)]
        mock_repo.find_all_sessions.return_value = sessions

        result = service.get_gamification_stats()

        assert result["streak"] == 1

    def test_昨日のみのセッションはストリーク0(self, service, mock_repo):
        # 今日のセッションなし
        sessions = [make_session(days_ago=1)]
        mock_repo.find_all_sessions.return_value = sessions

        result = service.get_gamification_stats()

        assert result["streak"] == 0


class TestCalculateBadges:
    def test_初回達成バッジが付与される(self, service, mock_repo):
        mock_repo.find_all_sessions.return_value = [make_session()]

        result = service.get_gamification_stats()

        badge_ids = [b["id"] for b in result["badges"]]
        assert "first" in badge_ids

    def test_5回達成バッジが付与される(self, service, mock_repo):
        mock_repo.find_all_sessions.return_value = [make_session() for _ in range(5)]

        result = service.get_gamification_stats()

        badge_ids = [b["id"] for b in result["badges"]]
        assert "five" in badge_ids

    def test_10回達成バッジが付与される(self, service, mock_repo):
        mock_repo.find_all_sessions.return_value = [make_session() for _ in range(10)]

        result = service.get_gamification_stats()

        badge_ids = [b["id"] for b in result["badges"]]
        assert "ten" in badge_ids

    def test_3日連続バッジが付与される(self, service, mock_repo):
        sessions = [make_session(days_ago=i) for i in range(3)]
        mock_repo.find_all_sessions.return_value = sessions

        result = service.get_gamification_stats()

        badge_ids = [b["id"] for b in result["badges"]]
        assert "streak3" in badge_ids

    def test_7日連続バッジが付与される(self, service, mock_repo):
        sessions = [make_session(days_ago=i) for i in range(7)]
        mock_repo.find_all_sessions.return_value = sessions

        result = service.get_gamification_stats()

        badge_ids = [b["id"] for b in result["badges"]]
        assert "streak7" in badge_ids

    def test_4回以下ではfiveバッジがつかない(self, service, mock_repo):
        mock_repo.find_all_sessions.return_value = [make_session() for _ in range(4)]

        result = service.get_gamification_stats()

        badge_ids = [b["id"] for b in result["badges"]]
        assert "five" not in badge_ids


class TestGetWeeklyStats:
    def test_セッションなしのとき0を返す(self, service, mock_repo):
        mock_repo.find_sessions_in_range.return_value = []

        result = service.get_weekly_stats()

        assert result["total_completed"] == 0
        assert result["total_minutes"] == 0
        assert len(result["days"]) == 7

    def test_7日分のデータが返される(self, service, mock_repo):
        mock_repo.find_sessions_in_range.return_value = []

        result = service.get_weekly_stats()

        assert len(result["days"]) == 7

    def test_今日のセッションが集計される(self, service, mock_repo):
        session = make_session(duration=25, days_ago=0)
        mock_repo.find_sessions_in_range.return_value = [session]

        result = service.get_weekly_stats()

        today_str = str(date.today())
        today_data = next(d for d in result["days"] if d["date"] == today_str)
        assert today_data["completed"] == 1
        assert today_data["total_minutes"] == 25


class TestGetMonthlyStats:
    def test_30日分のデータが返される(self, service, mock_repo):
        mock_repo.find_sessions_in_range.return_value = []

        result = service.get_monthly_stats()

        assert len(result["days"]) == 30

    def test_セッションなしのとき0を返す(self, service, mock_repo):
        mock_repo.find_sessions_in_range.return_value = []

        result = service.get_monthly_stats()

        assert result["total_completed"] == 0
        assert result["total_minutes"] == 0
