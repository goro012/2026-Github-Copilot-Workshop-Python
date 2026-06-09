from datetime import date, datetime

from models import Session, db


class SessionRepository:
    def save_session(self, duration: int) -> Session:
        session = Session(duration=duration, completed_at=datetime.utcnow())
        db.session.add(session)
        db.session.commit()
        return session

    def find_today_sessions(self) -> list[Session]:
        today_start = datetime.combine(date.today(), datetime.min.time())
        return (
            Session.query.filter(Session.completed_at >= today_start).all()
        )

    def find_all_sessions(self) -> list[Session]:
        return Session.query.order_by(Session.completed_at.desc()).all()

    def find_sessions_in_range(self, start: datetime, end: datetime) -> list[Session]:
        return (
            Session.query
            .filter(Session.completed_at >= start, Session.completed_at <= end)
            .all()
        )
