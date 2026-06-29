"""
Client Service — خدمات العملاء.
طبقة الخدمات للتعامل مع بيانات العملاء.
"""
from typing import List, Optional

from core.database import get_session
from models.client import Client


def get_all_clients() -> List[Client]:
    """
    جلب جميع العملاء النشطين.
    
    Returns:
        list[Client]: قائمة العملاء
    """
    with get_session() as session:
        results = session.query(Client).filter(
            Client.is_deleted == False  # noqa: E712
        ).order_by(Client.name).all()
        for r in results:
            session.expunge(r)
        return results


def get_client_by_id(client_id: int) -> Optional[Client]:
    """
    جلب عميل بالمعرّف.
    
    Args:
        client_id: معرّف العميل
    
    Returns:
        Client أو None
    """
    with get_session() as session:
        return session.query(Client).filter(
            Client.id == client_id,
            Client.is_deleted == False  # noqa: E712
        ).first()


def create_client(data: dict) -> Client:
    """
    إنشاء عميل جديد.
    
    Args:
        data: بيانات العميل (client_type, name, ...)
    
    Returns:
        Client: العميل المُنشأ
    
    Raises:
        ValueError: إذا كان الاسم أو النوع فارغًا
    """
    if not data.get("name"):
        raise ValueError("اسم العميل مطلوب")
    if not data.get("client_type"):
        raise ValueError("نوع العميل مطلوب")
    
    with get_session() as session:
        client = Client(**data)
        session.add(client)
        session.flush()
        session.refresh(client)
        session.expunge(client)
        return client


def update_client(client_id: int, data: dict) -> Optional[Client]:
    """
    تحديث بيانات عميل.
    
    Args:
        client_id: معرّف العميل
        data: القيم المراد تحديثها
    
    Returns:
        Client المحدّث أو None
    """
    with get_session() as session:
        client = session.query(Client).filter(
            Client.id == client_id,
            Client.is_deleted == False  # noqa: E712
        ).first()
        
        if not client:
            return None
        
        for key, value in data.items():
            if hasattr(client, key):
                setattr(client, key, value)
        
        session.flush()
        session.refresh(client)
        session.expunge(client)
        return client


def soft_delete_client(client_id: int) -> bool:
    """
    حذف ناعم لعميل.
    
    Args:
        client_id: معرّف العميل
    
    Returns:
        bool: True إذا تم الحذف
    """
    with get_session() as session:
        client = session.query(Client).filter(
            Client.id == client_id
        ).first()
        
        if not client:
            return False
        
        client.is_deleted = True
        return True


def count_clients() -> int:
    """
    عدد العملاء النشطين — يُستخدم في Dashboard.
    
    Returns:
        int: عدد العملاء
    """
    with get_session() as session:
        return session.query(Client).filter(
            Client.is_deleted == False  # noqa: E712
        ).count()


def search_clients(query: str) -> List[Client]:
    """
    بحث عن عملاء بالاسم.
    
    Args:
        query: نص البحث
    
    Returns:
        list[Client]: النتائج المطابقة
    """
    with get_session() as session:
        results = session.query(Client).filter(
            Client.is_deleted == False,  # noqa: E712
            Client.name.ilike(f"%{query}%")
        ).order_by(Client.name).all()
        for r in results:
            session.expunge(r)
        return results
