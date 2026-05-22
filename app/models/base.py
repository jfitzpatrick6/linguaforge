from sqlalchemy import Column, DateTime, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base
from datetime import datetime

# Base class for all models
Base = declarative_base()

# Common base model with standard fields
class TimestampedBase(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    user_id = Column(Integer, nullable=False, index=True)

    # Index on user_id for query performance
    __table_args__ = (
        {'sqlite_autoincrement': True},
    )
