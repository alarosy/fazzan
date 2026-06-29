"""
Hall model — القاعات.
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Numeric
from sqlalchemy.sql import func

from models import Base


class Hall(Base):
    """
    نموذج القاعة.
    يمثل قاعة تدريب أو اجتماعات في المركز.
    """
    __tablename__ = 'halls'

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    capacity = Column(Integer, nullable=True)
    daily_rate = Column(Numeric(10, 2), nullable=True)
    hourly_rate = Column(Numeric(10, 2), nullable=True)
    location = Column(String(200), nullable=True)
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())

    def __repr__(self):
        return f"<Hall(id={self.id}, name='{self.name}')>"
