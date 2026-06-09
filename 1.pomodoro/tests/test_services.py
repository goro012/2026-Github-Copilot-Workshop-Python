from unittest.mock import MagicMock

import pytest

from services import PomodoroService


@pytest.fixture()
def mock_repo():
    return MagicMock()


@pytest.fixture()
def service(mock_repo):
    return PomodoroService(repo=mock_repo)


class TestCompleteSession:
    def test_正常なdurationでセッションが保存される(self, service, mock_repo):
        mock_session = MagicMock()
        mock_session.id = 1
        mock_session.duration = 25
        mock_repo.save_session.return_value = mock_session

        result = service.complete_session(25)

        mock_repo.save_session.assert_called_once_with(25)
        assert result == {"id": 1, "duration": 25}

    def test_duration_0はValueErrorを送出する(self, service, mock_repo):
        with pytest.raises(ValueError, match="positive"):
            service.complete_session(0)
        mock_repo.save_session.assert_not_called()

    def test_負のdurationはValueErrorを送出する(self, service, mock_repo):
        with pytest.raises(ValueError, match="positive"):
            service.complete_session(-5)
        mock_repo.save_session.assert_not_called()

    def test_整数以外のdurationはValueErrorを送出する(self, service, mock_repo):
        with pytest.raises(ValueError):
            service.complete_session("25")
        mock_repo.save_session.assert_not_called()


class TestGetTodayStats:
    def test_セッションが0件のとき統計が0を返す(self, service, mock_repo):
        mock_repo.find_today_sessions.return_value = []

        result = service.get_today_stats()

        assert result == {"completed": 0, "total_minutes": 0}

    def test_複数セッションの集計が正しい(self, service, mock_repo):
        s1 = MagicMock()
        s1.duration = 25
        s2 = MagicMock()
        s2.duration = 50
        mock_repo.find_today_sessions.return_value = [s1, s2]

        result = service.get_today_stats()

        assert result == {"completed": 2, "total_minutes": 75}
