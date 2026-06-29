"""
Contract Service — خدمات العقود.
"""
from typing import List, Optional
from sqlalchemy.orm import joinedload

from core.database import get_session
from models.contract import Contract


def get_all_contracts() -> List[Contract]:
    """جلب جميع العقود النشطة."""
    with get_session() as session:
        results = session.query(Contract).options(
            joinedload(Contract.client),
            joinedload(Contract.project)
        ).filter(Contract.is_deleted == False).all()  # noqa: E712
        
        for r in results:
            if r in session:
                session.expunge(r)
                if r.client and r.client in session:
                    session.expunge(r.client)
                if r.project and r.project in session:
                    session.expunge(r.project)
        return results


def get_contract_by_id(contract_id: int) -> Optional[Contract]:
    """جلب عقد بالمعرّف."""
    with get_session() as session:
        c = session.query(Contract).options(
            joinedload(Contract.client),
            joinedload(Contract.project)
        ).filter(Contract.id == contract_id, Contract.is_deleted == False).first()  # noqa: E712
        
        if c:
            if c in session:
                session.expunge(c)
                if c.client and c.client in session:
                    session.expunge(c.client)
                if c.project and c.project in session:
                    session.expunge(c.project)
        return c


def create_contract(data: dict) -> Contract:
    """إنشاء عقد جديد."""
    if not data.get("title"):
        raise ValueError("عنوان العقد مطلوب")
    if not data.get("value") or float(data["value"]) <= 0:
        raise ValueError("قيمة العقد يجب أن تكون أكبر من الصفر")
        
    with get_session() as session:
        c = Contract(**data)
        session.add(c)
        session.flush()
        
        # Re-query
        result = session.query(Contract).options(
            joinedload(Contract.client),
            joinedload(Contract.project)
        ).filter(Contract.id == c.id).first()
        
        if result in session:
            session.expunge(result)
            if result.client and result.client in session:
                session.expunge(result.client)
            if result.project and result.project in session:
                session.expunge(result.project)
        return result


def update_contract(contract_id: int, data: dict) -> Optional[Contract]:
    """تحديث بيانات عقد."""
    with get_session() as session:
        c = session.query(Contract).filter(Contract.id == contract_id, Contract.is_deleted == False).first()  # noqa: E712
        if not c:
            return None
            
        for key, value in data.items():
            if hasattr(c, key):
                setattr(c, key, value)
                
        session.flush()
        
        # Re-query
        result = session.query(Contract).options(
            joinedload(Contract.client),
            joinedload(Contract.project)
        ).filter(Contract.id == contract_id).first()
        
        if result in session:
            session.expunge(result)
            if result.client and result.client in session:
                session.expunge(result.client)
            if result.project and result.project in session:
                session.expunge(result.project)
        return result


def soft_delete_contract(contract_id: int) -> bool:
    """حذف ناعم لعقد."""
    with get_session() as session:
        c = session.query(Contract).filter(Contract.id == contract_id).first()
        if not c:
            return False
        c.is_deleted = True
        return True
