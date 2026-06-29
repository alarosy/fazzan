"""
Partnership model — الشراكات.
"""
from sqlalchemy import Column, Integer, String, Text, Date, Boolean, DateTime, Numeric
from sqlalchemy.sql import func

from models import Base


class Partnership(Base):
    """
    نموذج الشراكة.
    يمثل شراكة بين المركز وجهة خارجية.
    """
    __tablename__ = 'partnerships'

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    partner_entity = Column(String(200), nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    agreement_value = Column(Numeric(15, 2), nullable=True)
    status = Column(String(20), default="قائم")  # "قائم" / "منقضٍ"
    notes = Column(Text, nullable=True)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    def __repr__(self):
        return f"<Partnership(id={self.id}, name='{self.name}')>"
