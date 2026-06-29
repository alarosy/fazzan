"""
Consultant Service — خدمات الاستشارات والمستشارين.
"""
from typing import List, Optional

from core.database import get_session
from models.consultant import Consultant


def get_all_consultants() -> List[Consultant]:
    """جلب جميع المستشارين النشطين."""
    with get_session() as session:
        results = session.query(Consultant).filter(
            Consultant.is_deleted == False  # noqa: E712
        ).order_by(Consultant.name).all()
        for r in results:
            session.expunge(r)
        return results


def get_consultant_by_id(consultant_id: int) -> Optional[Consultant]:
    """جلب مستشار بالمعرّف."""
    with get_session() as session:
        consultant = session.query(Consultant).filter(
            Consultant.id == consultant_id,
            Consultant.is_deleted == False  # noqa: E712
        ).first()
        if consultant:
            session.expunge(consultant)
        return consultant


def create_consultant(data: dict) -> Consultant:
    """إنشاء مستشار جديد."""
    if not data.get("name"):
        raise ValueError("اسم المستشار مطلوب")
    
    with get_session() as session:
        consultant = Consultant(**data)
        session.add(consultant)
        session.flush()
        session.refresh(consultant)
        session.expunge(consultant)
        return consultant


def update_consultant(consultant_id: int, data: dict) -> Optional[Consultant]:
    """تحديث بيانات مستشار."""
    with get_session() as session:
        consultant = session.query(Consultant).filter(
            Consultant.id == consultant_id,
            Consultant.is_deleted == False  # noqa: E712
        ).first()
        
        if not consultant:
            return None
        
        for key, value in data.items():
            if hasattr(consultant, key):
                setattr(consultant, key, value)
        
        session.flush()
        session.refresh(consultant)
        session.expunge(consultant)
        return consultant


def soft_delete_consultant(consultant_id: int) -> bool:
    """حذف ناعم لمستشار."""
    with get_session() as session:
        consultant = session.query(Consultant).filter(
            Consultant.id == consultant_id
        ).first()
        if not consultant:
            return False
        consultant.is_deleted = True
        return True
