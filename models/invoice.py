"""
Invoice model — الفواتير النهائية.
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from models import Base


class Invoice(Base):
    """
    نموذج الفاتورة النهائية.
    تصدر تلقائياً بمجرد اعتماد عرض السعر المالي من المدير المالي.
    """
    __tablename__ = 'invoices'

    id = Column(Integer, primary_key=True)
    invoice_number = Column(String(50), unique=True, nullable=False)   # INV-YYYY-NNNN
    proposal_id = Column(Integer, ForeignKey('financial_proposals.id'), nullable=True)
    client_id = Column(Integer, ForeignKey('clients.id'), nullable=False)
    total_value = Column(Numeric(15, 2), nullable=False)
    created_at = Column(DateTime, default=func.now())

    # Relationships
    client = relationship('Client')
    proposal = relationship('FinancialProposal')
    line_items = relationship('ServiceLineItem', back_populates='invoice', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Invoice(id={self.id}, number='{self.invoice_number}')>"
