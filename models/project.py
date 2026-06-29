"""
Project model — المشاريع.
"""
from sqlalchemy import Column, Integer, String, Text, Date, Boolean, DateTime, Numeric
from sqlalchemy.sql import func

from models import Base


class Project(Base):
    """
    نموذج المشروع.
    يمثل مشروعًا تنفيذيًا يرتبط به موظفون ودورات ومصروفات.
    
    Note: Extended fields (project_number, geographic_scope, etc.)
    will be added in Phase E (migration 0009).
    """
    __tablename__ = 'projects'

    id = Column(Integer, primary_key=True)
    project_number = Column(String(50), unique=True, nullable=True)     # PROJ-YYYY-NNNN
    name = Column(String(300), nullable=False)
    description = Column(Text, nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    geographic_scope = Column(String(100), nullable=True)
    status = Column(String(20), default="نشط")  # "نشط" / "مكتمل" / "معلّق"
    budget = Column(Numeric(15, 2), nullable=True)                     # القيمة الكلية للمشروع
    budget_allocated = Column(Numeric(15, 2), nullable=True)           # الميزانية المرصودة للمصاريف
    budget_spent = Column(Numeric(15, 2), default=0.00, nullable=False) # المصروف الفعلي المحمل
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    def __repr__(self):
        return f"<Project(id={self.id}, name='{self.name}')>"
