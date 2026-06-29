"""
Voucher model — سندات القبض والصرف.
"""
from sqlalchemy import Column, Integer, String, Text, Numeric, Enum, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from models import Base
from models.enums import VoucherType, PaymentMethod, RevenueSource


class Voucher(Base):
    """
    نموذج السند المالي.
    يمثل سندات القبض (مداخيل للمركز) أو الصرف (مدفوعات خارجية).
    """
    __tablename__ = 'vouchers'

    id = Column(Integer, primary_key=True)
    voucher_type = Column(Enum(VoucherType), nullable=False)
    voucher_number = Column(String(50), unique=True, nullable=False) # REC-YYYY-NNNN / DISB-YYYY-NNNN
    party_name = Column(String(200), nullable=False)                 # اسم الجهة المستلِمة / المسلِمة
    amount = Column(Numeric(12, 2), nullable=False)
    amount_in_words = Column(String(300), nullable=False)            # تفقيط المبلغ بالعربية
    payment_method = Column(Enum(PaymentMethod), nullable=False)
    revenue_source = Column(Enum(RevenueSource), nullable=True)      # مصدر الإيراد (عند القبض)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())

    # Relationships
    project = relationship('Project')

    def __repr__(self):
        return f"<Voucher(id={self.id}, number='{self.voucher_number}', type={self.voucher_type})>"
