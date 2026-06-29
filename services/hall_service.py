"""
Hall Service — خدمات القاعات.
طبقة الخدمات للتعامل مع بيانات القاعات وجدولتها.
"""
from typing import List, Optional

from core.database import get_session
from models.hall import Hall


def get_all_halls() -> List[Hall]:
    """
    جلب جميع القاعات النشطة.
    
    Returns:
        list[Hall]: قائمة القاعات
    """
    with get_session() as session:
        results = session.query(Hall).filter(
            Hall.is_active == True  # noqa: E712
        ).order_by(Hall.name).all()
        for r in results:
            session.expunge(r)
        return results


def get_hall_by_id(hall_id: int) -> Optional[Hall]:
    """جلب قاعة بالمعرّف."""
    with get_session() as session:
        hall = session.query(Hall).filter(Hall.id == hall_id).first()
        if hall:
            session.expunge(hall)
        return hall


def create_hall(data: dict) -> Hall:
    """إنشاء قاعة جديدة."""
    if not data.get("name"):
        raise ValueError("اسم القاعة مطلوب")
    
    with get_session() as session:
        hall = Hall(**data)
        session.add(hall)
        session.flush()
        session.refresh(hall)
        session.expunge(hall)
        return hall


def update_hall(hall_id: int, data: dict) -> Optional[Hall]:
    """تحديث بيانات قاعة."""
    with get_session() as session:
        hall = session.query(Hall).filter(Hall.id == hall_id).first()
        if not hall:
            return None
        
        for key, value in data.items():
            if hasattr(hall, key):
                setattr(hall, key, value)
        
        session.flush()
        session.refresh(hall)
        session.expunge(hall)
        return hall


def delete_hall(hall_id: int) -> bool:
    """حذف قاعة."""
    with get_session() as session:
        hall = session.query(Hall).filter(Hall.id == hall_id).first()
        if not hall:
            return False
        session.delete(hall)
        return True
