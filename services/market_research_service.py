"""
MarketResearch Service — خدمات بحوث ودراسات السوق.
"""
from typing import List, Optional

from core.database import get_session
from models.market_research import MarketResearch


def get_all_research() -> List[MarketResearch]:
    """جلب جميع أبحاث السوق."""
    with get_session() as session:
        results = session.query(MarketResearch).order_by(MarketResearch.created_at.desc()).all()
        for r in results:
            session.expunge(r)
        return results


def get_research_by_id(research_id: int) -> Optional[MarketResearch]:
    """جلب بحث سوق بالمعرّف."""
    with get_session() as session:
        research = session.query(MarketResearch).filter(MarketResearch.id == research_id).first()
        if research:
            session.expunge(research)
        return research


def create_research(data: dict) -> MarketResearch:
    """إنشاء طلب بحث سوق جديد."""
    if not data.get("collection_type"):
        raise ValueError("نوع البيانات المستهدفة مطلوب")
    
    with get_session() as session:
        research = MarketResearch(**data)
        session.add(research)
        session.flush()
        session.refresh(research)
        session.expunge(research)
        return research


def update_research(research_id: int, data: dict) -> Optional[MarketResearch]:
    """تحديث طلب بحث سوق."""
    with get_session() as session:
        research = session.query(MarketResearch).filter(MarketResearch.id == research_id).first()
        if not research:
            return None
        
        for key, value in data.items():
            if hasattr(research, key):
                setattr(research, key, value)
        
        session.flush()
        session.refresh(research)
        session.expunge(research)
        return research


def delete_research(research_id: int) -> bool:
    """حذف طلب بحث سوق."""
    with get_session() as session:
        research = session.query(MarketResearch).filter(MarketResearch.id == research_id).first()
        if not research:
            return False
        session.delete(research)
        return True
