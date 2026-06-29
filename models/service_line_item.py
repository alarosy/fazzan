"""
ServiceLineItem model — بنود خدمات عروض الأسعار والفواتير.
"""
from sqlalchemy import Column, Integer, String, Numeric, Enum, ForeignKey
from sqlalchemy.orm import relationship

from models import Base
from models.enums import ServiceType


class ServiceLineItem(Base):
    """
    نموذج بند الخدمة المالي.
    يمثل عنصراً تفصيلياً (مثل عدد الأيام، عدد الطلاب، سعر السكن) داخل عرض السعر أو الفاتورة.
    """
    __tablename__ = 'service_line_items'

    id = Column(Integer, primary_key=True)
    proposal_id = Column(Integer, ForeignKey('financial_proposals.id'), nullable=True)
    invoice_id = Column(Integer, ForeignKey('invoices.id'), nullable=True)
    service_type = Column(Enum(ServiceType), nullable=False)
    unit_description = Column(String(100), nullable=False)    # متدرب / يوم / شخص / قطعة
    quantity = Column(Numeric(10, 2), nullable=False, default=1.0)
    unit_price = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(10), default='LYD')
    discount = Column(Numeric(10, 2), default=0.0)
    total = Column(Numeric(10, 2), nullable=False)            # quantity * unit_price - discount

    # Relationships
    proposal = relationship('FinancialProposal', back_populates='line_items')
    invoice = relationship('Invoice', back_populates='line_items')

    def __repr__(self):
        return f"<ServiceLineItem(id={self.id}, total={self.total})>"
