"""
MarketResearch model — بحوث ودراسات السوق.
"""
from sqlalchemy import Column, Integer, String, Numeric, DateTime
from sqlalchemy.sql import func

from models import Base


class MarketResearch(Base):
    """
    نموذج دراسات وبحوث السوق.
    يتابع مشاريع دراسة الجدوى وجمع البيانات الميدانية أو الإلكترونية.
    """
    __tablename__ = 'market_research'

    id = Column(Integer, primary_key=True)
    collection_method = Column(String(20), nullable=False)   # "field" (ميداني) / "online" (إلكتروني)
    collection_type = Column(String(200), nullable=False)     # نوع البيانات المستهدفة
    min_samples = Column(Integer, nullable=False)
    min_price = Column(Numeric(10, 2), nullable=False)
    max_samples = Column(Integer, nullable=False)
    max_price = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime, default=func.now())

    def __repr__(self):
        return f"<MarketResearch(id={self.id}, collection_type='{self.collection_type}')>"
