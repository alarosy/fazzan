"""
Employee model — الموظفون.
"""
from sqlalchemy import (
    Column, Integer, String, Text, Date, Boolean, DateTime, Numeric,
    ForeignKey, Enum as SAEnum
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from models import Base
from models.enums import EmploymentType, PaymentMethod


class Employee(Base):
    """
    نموذج الموظف.
    يمثل موظفًا في المركز مع بيانات العقد والراتب.
    
    FK relationships:
        - current_project_id → projects.id (المشروع الحالي المسنَد إليه)
    """
    __tablename__ = 'employees'

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    email = Column(String(200), nullable=True)
    phone = Column(String(50), nullable=True)
    position = Column(String(200), nullable=True)
    hire_date = Column(Date, nullable=True)
    address = Column(Text, nullable=True)
    id_number = Column(String(50), nullable=True)

    # Contract fields (§4.2)
    contract_start_date = Column(Date, nullable=True)
    contract_end_date = Column(Date, nullable=True)
    daily_wage_rate = Column(Numeric(10, 2), nullable=True)
    employment_type = Column(
        SAEnum(EmploymentType, values_callable=lambda x: [e.value for e in x]),
        default=EmploymentType.PERMANENT.value,
        nullable=True
    )
    payment_method = Column(
        SAEnum(PaymentMethod, values_callable=lambda x: [e.value for e in x]),
        nullable=True
    )

    # FK: assigned project
    current_project_id = Column(Integer, ForeignKey('projects.id'), nullable=True)

    # Soft delete
    is_deleted = Column(Boolean, default=False, nullable=False)

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    # Relationships
    current_project = relationship("Project", foreign_keys=[current_project_id])

    def __repr__(self):
        return f"<Employee(id={self.id}, name='{self.name}')>"
