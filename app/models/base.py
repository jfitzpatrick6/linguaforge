from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, DateTime
from datetime import datetime

class Base(DeclarativeBase):
    """Global base class for all models"""
    pass


class TimestampedBase(Base):
    """Base with common timestamp fields"""
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)