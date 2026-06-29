"""
Consultant model — المستشارون.
"""
from sqlalchemy import Column, Integer, String, Text, Date, Boolean, Numeric, Enum
from models import Base
from models.enums import SpecCategory, PaymentMethod


class Consultant(Base):
    """
    نموذج المستشار.
    يمثل المستشارين الخارجيين المتعاقد معهم لتقديم خدمات استشارية.
    """
    __tablename__ = 'consultants'

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    email = Column(String(200), nullable=True)
    phone = Column(String(50), nullable=True)
    address = Column(Text, nullable=True)
    specialization = Column(Enum(SpecCategory), nullable=False)
    service_detail = Column(Text, nullable=True)
    contract_start = Column(Date, nullable=True)
    contract_end = Column(Date, nullable=True)
    gross_value = Column(Numeric(10, 2), nullable=True)       # القيمة الإجمالية للعقد المعروضة للعميل
    center_share = Column(Numeric(10, 2), nullable=True)      # حصة المركز المالية (داخلية)
    consultant_share = Column(Numeric(10, 2), nullable=True)  # حصة المستشار المالية (داخلية)
    payment_method = Column(Enum(PaymentMethod), nullable=True)
    is_deleted = Column(Boolean, default=False)

    def __repr__(self):
        return f"<Consultant(id={self.id}, name='{self.name}')>"
