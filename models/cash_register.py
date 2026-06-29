"""
CashRegister model — سجل حركات الخزينة والبنك.
"""
from sqlalchemy import Column, Integer, String, Text, Numeric, Enum, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from models import Base
from models.enums import RegisterType


class CashRegister(Base):
    """
    نموذج سجل النقدية.
    يتابع العمليات المقبوضة والمصروفة من الخزينة النقدية أو الحساب البنكي للمركز.
    """
    __tablename__ = 'cash_register'

    id = Column(Integer, primary_key=True)
    register_type = Column(Enum(RegisterType), nullable=False)        # كاش / مصرف
    transaction_type = Column(String(5), nullable=False)              # "in" (إيراد) / "out" (مصروف)
    amount = Column(Numeric(12, 2), nullable=False)
    description = Column(Text, nullable=False)
    related_voucher_id = Column(Integer, ForeignKey('vouchers.id'), nullable=True)
    balance_after = Column(Numeric(15, 2), nullable=False)             # الرصيد بعد الحركة لتاريخه
    created_at = Column(DateTime, default=func.now())

    # Relationships
    related_voucher = relationship('Voucher')

    def __repr__(self):
        return f"<CashRegister(id={self.id}, type={self.register_type}, tx={self.transaction_type}, amount={self.amount})>"
