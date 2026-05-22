from sqlalchemy import Column, String, Integer, DateTime, Text
from sqlalchemy.orm import relationship

from app.models.base import TimestampedBase


class SessionLog(TimestampedBase):
    __tablename__ = "session_logs"

    session_id = Column(String(50), nullable=False, index=True)
    activity_type = Column(String(50), nullable=False)
    duration_seconds = Column(Integer, nullable=False)
    content_type = Column(String(50), nullable=True)
    content_id = Column(Integer, nullable=True)
    feedback = Column(Text, nullable=True)
    metadata = Column(Text, nullable=True)

    # Index on user_id and session_id
    __table_args__ = (
        {'sqlite_autoincrement': True},
    )

    # Relationships
    # No back_populates needed - immutable log
