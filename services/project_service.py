"""
Project Service — خدمات المشاريع.
طبقة الخدمات للتعامل مع بيانات المشاريع.
"""
from typing import List, Optional

from core.database import get_session
from models.project import Project


def get_all_projects() -> List[Project]:
    """
    جلب جميع المشاريع النشطة.
    
    Returns:
        list[Project]: قائمة المشاريع
    """
    with get_session() as session:
        results = session.query(Project).filter(
            Project.is_deleted == False  # noqa: E712
        ).order_by(Project.created_at.desc()).all()
        for r in results:
            session.expunge(r)
        return results


def get_project_by_id(project_id: int) -> Optional[Project]:
    """
    جلب مشروع بالمعرّف.
    
    Args:
        project_id: معرّف المشروع
    
    Returns:
        Project أو None
    """
    with get_session() as session:
        proj = session.query(Project).filter(
            Project.id == project_id,
            Project.is_deleted == False  # noqa: E712
        ).first()
        if proj:
            session.expunge(proj)
        return proj


def create_project(data: dict) -> Project:
    """
    إنشاء مشروع جديد.
    
    Args:
        data: بيانات المشروع (name, description, ...)
    
    Returns:
        Project: المشروع المُنشأ
    """
    if not data.get("name"):
        raise ValueError("اسم المشروع مطلوب")
    
    with get_session() as session:
        project = Project(**data)
        session.add(project)
        session.flush()
        session.refresh(project)
        session.expunge(project)
        return project


def update_project(project_id: int, data: dict) -> Optional[Project]:
    """
    تحديث بيانات مشروع.
    
    Args:
        project_id: معرّف المشروع
        data: القيم المراد تحديثها
    
    Returns:
        Project المحدّث أو None
    """
    with get_session() as session:
        project = session.query(Project).filter(
            Project.id == project_id,
            Project.is_deleted == False  # noqa: E712
        ).first()
        
        if not project:
            return None
        
        for key, value in data.items():
            if hasattr(project, key):
                setattr(project, key, value)
        
        session.flush()
        session.refresh(project)
        session.expunge(project)
        return project


def soft_delete_project(project_id: int) -> bool:
    """
    حذف ناعم لمشروع.
    
    Args:
        project_id: معرّف المشروع
    
    Returns:
        bool: True إذا تم الحذف
    """
    with get_session() as session:
        project = session.query(Project).filter(
            Project.id == project_id
        ).first()
        
        if not project:
            return False
        
        project.is_deleted = True
        return True


def count_active() -> int:
    """
    عدد المشاريع النشطة — يُستخدم في Dashboard.
    
    Returns:
        int: عدد المشاريع بحالة "نشط"
    """
    with get_session() as session:
        return session.query(Project).filter(
            Project.status == "نشط",
            Project.is_deleted == False  # noqa: E712
        ).count()
