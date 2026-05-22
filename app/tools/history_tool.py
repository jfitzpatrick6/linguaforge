from sqlalchemy.orm import Session
from app.models import LearningSession
from app.exceptions import ToolError
from datetime import datetime
from typing import List


class HistoryTool:
    """Manage user learning session history."""

    def __init__(self, db: Session):
        self.db = db

    def log_session(self, user_id: int, duration: int, topics: List[str]) -> LearningSession:
        """Log a new learning session."""
        session = LearningSession(
            user_id=user_id,
            duration=duration,
            topics=topics,
            timestamp=datetime.utcnow()
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def get_recent_sessions(self, user_id: int, limit: int = 10) -> List[LearningSession]:
        """Retrieve the most recent learning sessions."""
        return self.db.query(LearningSession).filter(
            LearningSession.user_id == user_id
        ).order_by(LearningSession.timestamp.desc()).limit(limit).all()