from datetime import datetime, timedelta

import pytest

from models import Session, db
from repositories import SessionRepository


@pytest.fixture()
def repo():
    return SessionRepository()


class TestSaveSession:
    def test_セッションがDBに保存される(self, app, repo):
        with app.app_context():
            session = repo.save_session(25)

            assert session.id is not None
            assert session.duration == 25
            assert isinstance(session.completed_at, datetime)

    def test_保存したセッションがDBから取得できる(self, app, repo):
        with app.app_context():
            repo.save_session(25)

            sessions = Session.query.all()
            assert len(sessions) == 1
            assert sessions[0].duration == 25


class TestFindTodaySessions:
    def test_今日のセッションのみ返す(self, app, repo):
        with app.app_context():
            # 今日のセッション
            repo.save_session(25)
            repo.save_session(25)

            # 昨日のセッション（直接DBに挿入）
            yesterday = datetime.utcnow() - timedelta(days=1)
            old = Session(duration=25, completed_at=yesterday)
            db.session.add(old)
            db.session.commit()

            sessions = repo.find_today_sessions()
            assert len(sessions) == 2

    def test_セッションが0件のとき空リストを返す(self, app, repo):
        with app.app_context():
            sessions = repo.find_today_sessions()
            assert sessions == []
