from datetime import date, datetime, timedelta

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


class GamificationService:
    XP_PER_SESSION = 100
    XP_PER_LEVEL = 500

    def __init__(self, repo: SessionRepository | None = None):
        self.repo = repo or SessionRepository()

    def _calculate_streak(self, sessions: list) -> int:
        if not sessions:
            return 0
        dates = sorted(
            {s.completed_at.date() for s in sessions},
            reverse=True,
        )
        today = date.today()
        streak = 0
        expected = today
        for d in dates:
            if d == expected:
                streak += 1
                expected -= timedelta(days=1)
            elif d < expected:
                break
        return streak

    def _calculate_badges(self, sessions: list, streak: int) -> list[dict]:
        total = len(sessions)
        badges = []
        if total >= 1:
            badges.append({
                "id": "first",
                "name": "初回達成",
                "description": "最初のポモドーロを完了",
            })
        if total >= 5:
            badges.append({
                "id": "five",
                "name": "5回達成",
                "description": "5回のポモドーロを完了",
            })
        if total >= 10:
            badges.append({
                "id": "ten",
                "name": "10回達成",
                "description": "10回のポモドーロを完了",
            })
        if streak >= 3:
            badges.append({
                "id": "streak3",
                "name": "3日連続",
                "description": "3日連続でポモドーロを完了",
            })
        if streak >= 7:
            badges.append({
                "id": "streak7",
                "name": "7日連続",
                "description": "7日連続でポモドーロを完了",
            })
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        week_start_dt = datetime.combine(week_start, datetime.min.time())
        week_count = sum(1 for s in sessions if s.completed_at >= week_start_dt)
        if week_count >= 10:
            badges.append({
                "id": "week10",
                "name": "今週10回完了",
                "description": "今週10回のポモドーロを完了",
            })
        return badges

    def get_gamification_stats(self) -> dict:
        sessions = self.repo.find_all_sessions()
        total_xp = len(sessions) * self.XP_PER_SESSION
        level = total_xp // self.XP_PER_LEVEL + 1
        xp_in_level = total_xp % self.XP_PER_LEVEL
        streak = self._calculate_streak(sessions)
        badges = self._calculate_badges(sessions, streak)
        return {
            "total_xp": total_xp,
            "level": level,
            "xp_in_level": xp_in_level,
            "xp_to_next_level": self.XP_PER_LEVEL - xp_in_level,
            "xp_per_level": self.XP_PER_LEVEL,
            "streak": streak,
            "total_sessions": len(sessions),
            "badges": badges,
        }

    def get_weekly_stats(self) -> dict:
        today = date.today()
        start = today - timedelta(days=6)
        start_dt = datetime.combine(start, datetime.min.time())
        end_dt = datetime.combine(today, datetime.max.time())
        sessions = self.repo.find_sessions_in_range(start_dt, end_dt)

        daily: dict[str, dict[str, int | str]] = {}
        for i in range(7):
            d = str(start + timedelta(days=i))
            daily[d] = {"date": d, "completed": 0, "total_minutes": 0}

        for s in sessions:
            d = str(s.completed_at.date())
            if d in daily:
                daily[d]["completed"] += 1  # type: ignore[operator]
                daily[d]["total_minutes"] += s.duration  # type: ignore[operator]

        days = list(daily.values())
        return {
            "days": days,
            "total_completed": sum(d["completed"] for d in days),
            "total_minutes": sum(d["total_minutes"] for d in days),
        }

    def get_monthly_stats(self) -> dict:
        today = date.today()
        start = today - timedelta(days=29)
        start_dt = datetime.combine(start, datetime.min.time())
        end_dt = datetime.combine(today, datetime.max.time())
        sessions = self.repo.find_sessions_in_range(start_dt, end_dt)

        daily: dict[str, dict[str, int | str]] = {}
        for i in range(30):
            d = str(start + timedelta(days=i))
            daily[d] = {"date": d, "completed": 0, "total_minutes": 0}

        for s in sessions:
            d = str(s.completed_at.date())
            if d in daily:
                daily[d]["completed"] += 1  # type: ignore[operator]
                daily[d]["total_minutes"] += s.duration  # type: ignore[operator]

        days = list(daily.values())
        return {
            "days": days,
            "total_completed": sum(d["completed"] for d in days),
            "total_minutes": sum(d["total_minutes"] for d in days),
        }
