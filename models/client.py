"""
Client model — العملاء.
"""
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, Numeric,
    ForeignKey, Enum as SAEnum
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from models import Base
from models.enums import ClientType, PaymentMethod, SectorType


class Client(Base):
    """
    نموذج العميل.
    يدعم ثلاثة أنواع: فرد، مؤسسة، شراكة.
    حقول المؤسسات (sector, project_name, etc.) تكون nullable للأفراد.
    
    FK relationships:
        - partnership_id → partnerships.id (مرجع الشراكة)
    """
    __tablename__ = 'clients'

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    is_deleted = Column(Boolean, default=False)

    # Common fields
    client_type = Column(
        SAEnum(ClientType, values_callable=lambda x: [e.value for e in x]),
        nullable=False
    )
    name = Column(String(200), nullable=False)
    email = Column(String(200), nullable=True)
    phone = Column(String(50), nullable=True)
    address = Column(Text, nullable=True)
    payment_method = Column(
        SAEnum(PaymentMethod, values_callable=lambda x: [e.value for e in x]),
        nullable=True
    )
    partnership_status = Column(String(20), nullable=True)  # "قائم" / "منقضٍ"

    # Institution-specific fields (nullable for individuals)
    sector = Column(
        SAEnum(SectorType, values_callable=lambda x: [e.value for e in x]),
        nullable=True
    )
    project_name = Column(String(300), nullable=True)
    project_summary = Column(Text, nullable=True)
    contract_value = Column(Numeric(15, 2), nullable=True)
    roles_distribution = Column(Text, nullable=True)

    # FK: Partnership reference
    partnership_id = Column(Integer, ForeignKey('partnerships.id'), nullable=True)

    # Relationships
    partnership = relationship("Partnership", foreign_keys=[partnership_id])

    def __repr__(self):
        return f"<Client(id={self.id}, name='{self.name}', type={self.client_type})>"
