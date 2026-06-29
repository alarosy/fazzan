"""
TrainingProgram model — البرامج التدريبية.
"""
from sqlalchemy import Column, Integer, String, Text, Date, Boolean, DateTime, Numeric, Enum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from models import Base
from models.enums import CourseCategory, TrainerPayType


class TrainingProgram(Base):
    """
    نموذج البرنامج/الدورة التدريبية.
    """
    __tablename__ = 'training_programs'

    id = Column(Integer, primary_key=True)
    name = Column(String(300), nullable=False)
    description = Column(Text, nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    duration_hours = Column(Integer, nullable=True)
    status = Column(String(20), default="مخطط")  # "مخطط" / "جارية" / "مكتملة" / "ملغاة"
    notes = Column(Text, nullable=True)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    # Phase B Extended Fields
    course_category = Column(Enum(CourseCategory), nullable=True)
    hall_id = Column(Integer, ForeignKey('halls.id'), nullable=True)
    min_trainees = Column(Integer, nullable=True)
    max_trainees = Column(Integer, nullable=True)
    fee_per_trainee = Column(Numeric(10, 2), nullable=True)
    trainer_pay_type = Column(Enum(TrainerPayType), nullable=True)
    trainer_pay_value = Column(Numeric(10, 2), nullable=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=True)
    
    # Schedule Fields
    schedule_days = Column(String(100), nullable=True)  # e.g., "السبت, الإثنين, الأربعاء"
    schedule_time = Column(String(50), nullable=True)   # e.g., "08:00 - 10:00"

    # Relationships
    hall = relationship("Hall")
    project = relationship("Project")
    enrollments = relationship("CourseEnrollment", back_populates="course", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<TrainingProgram(id={self.id}, name='{self.name}')>"
