"""
Contract model — العقود.
"""
from sqlalchemy import Column, Integer, String, Text, Date, Boolean, ForeignKey, Numeric, Enum
from sqlalchemy.orm import relationship

from models import Base
from models.enums import ContractStatus


class Contract(Base):
    """
    نموذج العقد.
    يمثل عقدًا قانونيًا وماليًا مبرمًا مع العملاء لتنفيذ مشاريع أو خدمات.
    """
    __tablename__ = 'contracts'

    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey('clients.id'), nullable=False)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=True)
    title = Column(String(200), nullable=False)
    status = Column(Enum(ContractStatus), nullable=False, default=ContractStatus.PENDING)
    value = Column(Numeric(15, 2), nullable=False)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    scope = Column(Text, nullable=True)                              # نطاق العمل
    clauses = Column(Text, nullable=True)                            # البنود والشروط
    is_deleted = Column(Boolean, default=False)

    # Relationships
    client = relationship('Client')
    project = relationship('Project')

    def __repr__(self):
        return f"<Contract(id={self.id}, title='{self.title}', value={self.value})>"
