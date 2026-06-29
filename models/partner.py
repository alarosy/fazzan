"""
Partner model — الشركاء.
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, Enum

from models import Base
from models.enums import PartnerType


class Partner(Base):
    """
    نموذج الشريك.
    يمثل الشركاء والجهات الداعمة أو المتعاونة محلياً أو دولياً.
    """
    __tablename__ = 'partners'

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    type = Column(Enum(PartnerType), nullable=False, default=PartnerType.LOCAL)
    email = Column(String(200), nullable=True)
    phone = Column(String(50), nullable=True)
    contribution_details = Column(Text, nullable=True)                  # تفاصيل المساهمة
    is_deleted = Column(Boolean, default=False)

    def __repr__(self):
        return f"<Partner(id={self.id}, name='{self.name}', type={self.type})>"
