from repositories import SessionRepository


class PomodoroService:
    def __init__(self, repo: SessionRepository | None = None):
        self.repo = repo or SessionRepository()

    def complete_session(self, duration: int) -> dict:
        if not isinstance(duration, int) or duration <= 0:
            raise ValueError("duration must be a positive integer")
        session = self.repo.save_session(duration)
        return {"id": session.id, "duration": session.duration}

    def get_today_stats(self) -> dict:
        sessions = self.repo.find_today_sessions()
        return {
            "completed": len(sessions),
            "total_minutes": sum(s.duration for s in sessions),
        }
