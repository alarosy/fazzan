"""
Catering models — خدمات التموين والإعاشة.
"""
from sqlalchemy import Column, Integer, String, Text, Numeric, Enum, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from models import Base
from models.enums import CateringMeal, CateringLevel


class CateringOrder(Base):
    """
    نموذج طلبية التموين.
    يتابع توفير الوجبات والضيافة للمتدربين والمحاضرين.
    """
    __tablename__ = 'catering_orders'

    id = Column(Integer, primary_key=True)
    proposal_id = Column(Integer, ForeignKey('financial_proposals.id'), nullable=True) # ForeignKey للمرحلة D
    meal_type = Column(Enum(CateringMeal), nullable=False)
    service_level = Column(Enum(CateringLevel), nullable=False)
    pricing_mode = Column(String(20), default="per_person")   # "per_person" (لكل شخص) / "per_day" (لكل يوم)
    num_persons = Column(Integer, nullable=True)
    num_days = Column(Integer, nullable=True)
    unit_price = Column(Numeric(10, 2), nullable=False)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())

    # Relationships
    extra_services = relationship('CateringExtra', back_populates='order', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<CateringOrder(id={self.id}, meal_type={self.meal_type})>"


class CateringExtra(Base):
    """
    الخدمات الإضافية المرفقة بطلبية التموين.
    مثال: مياه معدنية إضافية، عصائر خاصة، ضيافة VIP.
    """
    __tablename__ = 'catering_extras'

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('catering_orders.id'), nullable=False)
    service_name = Column(String(200), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)

    # Relationships
    order = relationship('CateringOrder', back_populates='extra_services')

    def __repr__(self):
        return f"<CateringExtra(id={self.id}, service_name='{self.service_name}')>"
