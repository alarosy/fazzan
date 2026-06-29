"""
Partner Service — خدمات الشركاء.
"""
from typing import List, Optional

from core.database import get_session
from models.partner import Partner


def get_all_partners() -> List[Partner]:
    """جلب جميع الشركاء النشطين."""
    with get_session() as session:
        results = session.query(Partner).filter(
            Partner.is_deleted == False  # noqa: E712
        ).order_by(Partner.name).all()
        for r in results:
            session.expunge(r)
        return results


def get_partner_by_id(partner_id: int) -> Optional[Partner]:
    """جلب شريك بالمعرّف."""
    with get_session() as session:
        p = session.query(Partner).filter(
            Partner.id == partner_id,
            Partner.is_deleted == False  # noqa: E712
        ).first()
        if p:
            session.expunge(p)
        return p


def create_partner(data: dict) -> Partner:
    """إنشاء شريك جديد."""
    if not data.get("name"):
        raise ValueError("اسم الشريك مطلوب")
        
    with get_session() as session:
        p = Partner(**data)
        session.add(p)
        session.flush()
        session.refresh(p)
        session.expunge(p)
        return p


def update_partner(partner_id: int, data: dict) -> Optional[Partner]:
    """تحديث بيانات شريك."""
    with get_session() as session:
        p = session.query(Partner).filter(
            Partner.id == partner_id,
            Partner.is_deleted == False  # noqa: E712
        ).first()
        if not p:
            return None
            
        for key, value in data.items():
            if hasattr(p, key):
                setattr(p, key, value)
                
        session.flush()
        session.refresh(p)
        session.expunge(p)
        return p


def soft_delete_partner(partner_id: int) -> bool:
    """حذف ناعم لشريك."""
    with get_session() as session:
        p = session.query(Partner).filter(
            Partner.id == partner_id
        ).first()
        if not p:
            return False
        p.is_deleted = True
        return True
