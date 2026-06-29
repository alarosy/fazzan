"""
HR Service — خدمات الموارد البشرية.
طبقة الخدمات للتعامل مع بيانات الموظفين — الواجهة لا تتكلم مع DB مباشرة.
"""
from datetime import date, timedelta
from typing import List, Optional

from sqlalchemy.orm import Session

from core.database import get_session
from models.employee import Employee


def get_all_employees() -> List[Employee]:
    """
    جلب جميع الموظفين النشطين (غير المحذوفين).
    
    Returns:
        list[Employee]: قائمة الموظفين النشطين
    """
    with get_session() as session:
        results = session.query(Employee).filter(
            Employee.is_deleted == False  # noqa: E712
        ).order_by(Employee.name).all()
        for r in results:
            session.expunge(r)
        return results


def get_employee_by_id(employee_id: int) -> Optional[Employee]:
    """
    جلب موظف بالمعرّف.
    
    Args:
        employee_id: معرّف الموظف
    
    Returns:
        Employee أو None
    """
    with get_session() as session:
        return session.query(Employee).filter(
            Employee.id == employee_id,
            Employee.is_deleted == False  # noqa: E712
        ).first()


def create_employee(data: dict) -> Employee:
    """
    إنشاء موظف جديد.
    
    Args:
        data: قاموس يحوي بيانات الموظف (name, email, phone, position, ...)
    
    Returns:
        Employee: الموظف المُنشأ
    
    Raises:
        ValueError: إذا كان الاسم فارغًا
    """
    if not data.get("name"):
        raise ValueError("اسم الموظف مطلوب")
    
    with get_session() as session:
        employee = Employee(**data)
        session.add(employee)
        session.flush()
        session.refresh(employee)
        # Expunge to use outside session
        session.expunge(employee)
        return employee


def update_employee(employee_id: int, data: dict) -> Optional[Employee]:
    """
    تحديث بيانات موظف.
    
    Args:
        employee_id: معرّف الموظف
        data: القيم المراد تحديثها
    
    Returns:
        Employee المحدّث أو None إذا لم يوجد
    """
    with get_session() as session:
        employee = session.query(Employee).filter(
            Employee.id == employee_id,
            Employee.is_deleted == False  # noqa: E712
        ).first()
        
        if not employee:
            return None
        
        for key, value in data.items():
            if hasattr(employee, key):
                setattr(employee, key, value)
        
        session.flush()
        session.refresh(employee)
        session.expunge(employee)
        return employee


def soft_delete_employee(employee_id: int) -> bool:
    """
    حذف ناعم لموظف (تعيين is_deleted = True).
    
    Args:
        employee_id: معرّف الموظف
    
    Returns:
        bool: True إذا تم الحذف، False إذا لم يوجد الموظف
    """
    with get_session() as session:
        employee = session.query(Employee).filter(
            Employee.id == employee_id
        ).first()
        
        if not employee:
            return False
        
        employee.is_deleted = True
        return True


def count_active_employees() -> int:
    """
    عدد الموظفين النشطين — يُستخدم في Dashboard.
    
    Returns:
        int: عدد الموظفين غير المحذوفين
    """
    with get_session() as session:
        return session.query(Employee).filter(
            Employee.is_deleted == False  # noqa: E712
        ).count()


def get_expiring_contracts(days_ahead: int = 30) -> List[Employee]:
    """
    جلب الموظفين الذين تنتهي عقودهم خلال الأيام القادمة — لتنبيهات Dashboard.
    
    Args:
        days_ahead: عدد الأيام للبحث (افتراضي 30)
    
    Returns:
        list[Employee]: الموظفون الذين تنتهي عقودهم قريبًا
    """
    today = date.today()
    threshold = today + timedelta(days=days_ahead)
    
    with get_session() as session:
        results = session.query(Employee).filter(
            Employee.contract_end_date.isnot(None),
            Employee.contract_end_date <= threshold,
            Employee.contract_end_date >= today,
            Employee.is_deleted == False  # noqa: E712
        ).order_by(Employee.contract_end_date).all()
        for r in results:
            session.expunge(r)
        return results


def search_employees(query: str) -> List[Employee]:
    """
    بحث عن موظفين بالاسم أو المنصب.
    
    Args:
        query: نص البحث
    
    Returns:
        list[Employee]: النتائج المطابقة
    """
    with get_session() as session:
        results = session.query(Employee).filter(
            Employee.is_deleted == False,  # noqa: E712
            (Employee.name.ilike(f"%{query}%")) |
            (Employee.position.ilike(f"%{query}%"))
        ).order_by(Employee.name).all()
        for r in results:
            session.expunge(r)
        return results
