"""
Catering Service — خدمات التموين والإعاشة.
"""
from typing import List, Optional
from sqlalchemy.orm import joinedload

from core.database import get_session
from models.catering import CateringOrder, CateringExtra


def get_all_catering_orders() -> List[CateringOrder]:
    """جلب جميع طلبيات التموين."""
    with get_session() as session:
        results = session.query(CateringOrder).options(
            joinedload(CateringOrder.extra_services)
        ).order_by(CateringOrder.created_at.desc()).all()
        
        for r in results:
            if r in session:
                session.expunge(r)
                for ex in r.extra_services:
                    if ex in session:
                        session.expunge(ex)
        return results


def get_catering_order_by_id(order_id: int) -> Optional[CateringOrder]:
    """جلب طلبية تموين بالمعرّف."""
    with get_session() as session:
        order = session.query(CateringOrder).options(
            joinedload(CateringOrder.extra_services)
        ).filter(CateringOrder.id == order_id).first()
        
        if order:
            if order in session:
                session.expunge(order)
                for ex in order.extra_services:
                    if ex in session:
                        session.expunge(ex)
        return order


def create_catering_order(order_data: dict, extras: List[dict] = None) -> CateringOrder:
    """إنشاء طلبية تموين جديدة مع خدماتها الإضافية."""
    with get_session() as session:
        order = CateringOrder(**order_data)
        session.add(order)
        session.flush()
        
        if extras:
            for ex in extras:
                extra = CateringExtra(order_id=order.id, **ex)
                session.add(extra)
        
        session.flush()
        
        # Re-query with joinedload to return clean expunged object
        result = session.query(CateringOrder).options(
            joinedload(CateringOrder.extra_services)
        ).filter(CateringOrder.id == order.id).first()
        
        if result in session:
            session.expunge(result)
            for ex in result.extra_services:
                if ex in session:
                    session.expunge(ex)
        return result


def update_catering_order(order_id: int, order_data: dict, extras: List[dict] = None) -> Optional[CateringOrder]:
    """تحديث طلبية تموين وخدماتها الإضافية."""
    with get_session() as session:
        order = session.query(CateringOrder).filter(CateringOrder.id == order_id).first()
        if not order:
            return None
        
        for key, value in order_data.items():
            if hasattr(order, key):
                setattr(order, key, value)
        
        # If extras provided, clear old and add new
        if extras is not None:
            session.query(CateringExtra).filter(CateringExtra.order_id == order_id).delete()
            for ex in extras:
                extra = CateringExtra(order_id=order_id, **ex)
                session.add(extra)
        
        session.flush()
        
        # Re-query
        result = session.query(CateringOrder).options(
            joinedload(CateringOrder.extra_services)
        ).filter(CateringOrder.id == order_id).first()
        
        if result in session:
            session.expunge(result)
            for ex in result.extra_services:
                if ex in session:
                    session.expunge(ex)
        return result


def delete_catering_order(order_id: int) -> bool:
    """حذف طلبية تموين بالكامل."""
    with get_session() as session:
        order = session.query(CateringOrder).filter(CateringOrder.id == order_id).first()
        if not order:
            return False
        session.delete(order)
        return True
