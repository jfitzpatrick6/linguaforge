"""
Shared model base classes and mixins.

TimestampedBase provides standard created_at / updated_at columns
using the project's central Base (async DeclarativeBase).

Prefer importing Base directly from app.core.database for new concrete
models unless you specifically need the timestamp columns.
"""
from app.core.database import Base
from sqlalchemy import Column, DateTime
from datetime import datetime, timezone


class TimestampedBase(Base):
    """Abstract base that adds standard audit timestamps."""
    __abstract__ = True

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
