"""
Trainee model — المتدربون.
"""
from sqlalchemy import Column, Integer, String, Text, Date, Boolean, DateTime
from sqlalchemy.sql import func

from models import Base


class Trainee(Base):
    """
    نموذج المتدرب.
    يمثل شخصًا يلتحق بدورات المركز. يمكن إعادة استخدام بياناته
    عند التسجيل في دورات متعددة (§5.4).
    """
    __tablename__ = 'trainees'

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    email = Column(String(200), nullable=True)
    phone = Column(String(50), nullable=True)
    id_number = Column(String(50), nullable=True)
    organization = Column(String(200), nullable=True)
    address = Column(Text, nullable=True)
    date_of_birth = Column(Date, nullable=True)
    gender = Column(String(10), nullable=True)  # "ذكر" / "أنثى"
    notes = Column(Text, nullable=True)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    def __repr__(self):
        return f"<Trainee(id={self.id}, name='{self.name}')>"
