"""
CourseEnrollment model — تسجيل الطلاب بالدورات.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Numeric, ForeignKey, Date, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from models import Base
from models.enums import PaymentMethod


class CourseEnrollment(Base):
    """
    نموذج التسجيل في الدورة التدريبية.
    يربط المتدرب بالدورة التدريبية مع متابعة المدفوعات والاسترجاع.
    """
    __tablename__ = 'course_enrollments'

    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey('training_programs.id'), nullable=False)
    trainee_id = Column(Integer, ForeignKey('trainees.id'), nullable=False)
    enrollment_status = Column(String(20), default="مبدئي")  # "مبدئي" / "نهائي"
    payment_method = Column(Enum(PaymentMethod), nullable=True)
    amount_paid = Column(Numeric(10, 2), nullable=True)
    refund_requested = Column(Boolean, default=False)
    refund_amount = Column(Numeric(10, 2), nullable=True)
    refund_date = Column(Date, nullable=True)
    created_at = Column(DateTime, default=func.now())

    # Relationships
    course = relationship("TrainingProgram", back_populates="enrollments")
    trainee = relationship("Trainee")

    def __repr__(self):
        return f"<CourseEnrollment(id={self.id}, course_id={self.course_id}, trainee_id={self.trainee_id})>"
