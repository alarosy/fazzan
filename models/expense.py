"""
Expense model — المصروفات.
"""
from sqlalchemy import Column, Integer, String, Text, Numeric, Enum, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from models import Base
from models.enums import PaymentMethod


class Expense(Base):
    """
    نموذج المصروف المالي.
    يغطي المصاريف التشغيلية للمركز ومصاريف المشاريع.
    """
    __tablename__ = 'expenses'

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)                         # بيان المصروف
    quantity = Column(Numeric(10, 2), nullable=False, default=1.00)
    unit = Column(String(50), nullable=True)                          # الوحدة (يوم، شهر، قطعة)
    unit_price = Column(Numeric(12, 2), nullable=False)
    total = Column(Numeric(12, 2), nullable=False)                    # quantity * unit_price
    notes = Column(Text, nullable=True)
    invoice_image_path = Column(Text, nullable=True)                 # صورة الفاتورة الورقية
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=True)
    payment_method = Column(Enum(PaymentMethod), nullable=False, default=PaymentMethod.CASH)
    created_at = Column(DateTime, default=func.now())

    # Relationships
    project = relationship('Project')

    def __repr__(self):
        return f"<Expense(id={self.id}, name='{self.name}', total={self.total})>"
