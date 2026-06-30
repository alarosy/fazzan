"""
FinancialProposal model stub — عرض السعر المالي.
نموذج أولي لتجنب أخطاء المفاتيح الخارجية في المرحلة C، وسيتم توسعته بالكامل في المرحلة D.
"""
from sqlalchemy import Column, Integer, String, DateTime, Numeric, Enum, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from models import Base
from models.enums import ProposalStatus, ServiceType


class FinancialProposal(Base):
    """
    نموذج عرض السعر المالي.
    """
    __tablename__ = 'financial_proposals'

    id = Column(Integer, primary_key=True)
    proposal_number = Column(String(50), unique=True)          # PRO-YYYY-NNNN
    client_id = Column(Integer, ForeignKey('clients.id'), nullable=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=True)
    service_type = Column(Enum(ServiceType), nullable=True)
    status = Column(Enum(ProposalStatus), default=ProposalStatus.PENDING)
    approved_by = Column(String(100), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    total_value = Column(Numeric(15, 2), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())

    # Relationships
    line_items = relationship('ServiceLineItem', back_populates='proposal', cascade='all, delete-orphan')
    client = relationship('Client')
    project = relationship('Project')

    def __repr__(self):
        return f"<FinancialProposal(id={self.id}, number='{self.proposal_number}')>"
