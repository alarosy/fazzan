"""
Trainer model — المدربون.
"""
from sqlalchemy import Column, Integer, String, Text, Date, Boolean, DateTime, Numeric
from sqlalchemy.sql import func

from models import Base


class Trainer(Base):
    """
    نموذج المدرب.
    يمثل مدربًا يقدم دورات تدريبية في المركز.
    """
    __tablename__ = 'trainers'

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    email = Column(String(200), nullable=True)
    phone = Column(String(50), nullable=True)
    specialization = Column(String(300), nullable=True)
    bio = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    def __repr__(self):
        return f"<Trainer(id={self.id}, name='{self.name}')>"
