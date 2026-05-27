from sqlalchemy import Column, Integer, String, JSON, DateTime
from app.core.database import Base
from datetime import datetime, timezone


class SessionLog(Base):
    """Log of learning sessions (lessons, quizzes, voice chats, etc.)"""
    __tablename__ = "session_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False, index=True)

    session_type = Column(String, nullable=False)  # "lesson", "quiz", "voice_chat", "assessment"
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    duration_minutes = Column(Integer, default=0)

    data = Column(JSON, nullable=True)  # Flexible JSON field for session details
    summary = Column(String, nullable=True)

