"""
Asset model — الأصول الثابتة.
"""
from sqlalchemy import Column, Integer, String, Text, Date, Enum

from models import Base
from models.enums import AssetCategory, AssetOwnership


class Asset(Base):
    """
    نموذج الأصول الثابتة.
    يتابع الأصول المملوكة للمركز أو المستعارة مع حساب استهلاكها الزمني.
    """
    __tablename__ = 'assets'

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    category = Column(Enum(AssetCategory), nullable=False)
    acquisition_date = Column(Date, nullable=False)
    depreciation_months = Column(Integer, nullable=False, default=12) # مدة الاستهلاك بالأشهر
    ownership = Column(Enum(AssetOwnership), nullable=False)
    lender_name = Column(String(200), nullable=True)                  # اسم الجهة المعيرة (إذا كان مستعاراً)
    notes = Column(Text, nullable=True)

    def __repr__(self):
        return f"<Asset(id={self.id}, name='{self.name}', category={self.category})>"
