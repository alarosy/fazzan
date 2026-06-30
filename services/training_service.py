"""
Training Service — خدمات التدريب.
طبقة الخدمات للتعامل مع البرامج التدريبية والمتدربين والمدربين.
"""
from datetime import date
from typing import List, Optional

from sqlalchemy import func
from sqlalchemy.orm import joinedload

from core.database import get_session
from models.training_program import TrainingProgram
from models.trainee import Trainee
from models.trainer import Trainer
from models.course_enrollment import CourseEnrollment


def get_all_programs() -> List[TrainingProgram]:
    """
    جلب جميع البرامج التدريبية النشطة.
    
    Returns:
        list[TrainingProgram]: قائمة البرامج
    """
    with get_session() as session:
        results = session.query(TrainingProgram).filter(
            TrainingProgram.is_deleted == False  # noqa: E712
        ).order_by(TrainingProgram.start_date.desc()).all()
        for r in results:
            session.expunge(r)
        return results


def create_program(data: dict) -> TrainingProgram:
    """
    إنشاء برنامج تدريبي جديد.
    
    Args:
        data: بيانات البرنامج (name, description, start_date, ...)
    
    Returns:
        TrainingProgram: البرنامج المُنشأ
    """
    if not data.get("name"):
        raise ValueError("اسم البرنامج التدريبي مطلوب")
    
    with get_session() as session:
        program = TrainingProgram(**data)
        session.add(program)
        session.flush()
        session.refresh(program)
        session.expunge(program)
        return program


def count_active_courses() -> int:
    """
    عدد الدورات الجارية حاليًا — يُستخدم في Dashboard.
    
    Returns:
        int: عدد الدورات التي حالتها "جارية"
    """
    with get_session() as session:
        return session.query(TrainingProgram).filter(
            TrainingProgram.status == "جارية",
            TrainingProgram.is_deleted == False  # noqa: E712
        ).count()


def count_active_trainers() -> int:
    """
    عدد المدربين النشطين — يُستخدم في Dashboard.
    
    Returns:
        int: عدد المدربين النشطين
    """
    with get_session() as session:
        return session.query(Trainer).filter(
            Trainer.is_active == True,  # noqa: E712
            Trainer.is_deleted == False  # noqa: E712
        ).count()


def count_month_trainees() -> int:
    """
    عدد المتدربين المسجلين هذا الشهر — يُستخدم في Dashboard.
    
    Returns:
        int: عدد المتدربين الجدد هذا الشهر
    """
    today = date.today()
    first_of_month = today.replace(day=1)
    
    with get_session() as session:
        return session.query(Trainee).filter(
            Trainee.created_at >= first_of_month,
            Trainee.is_deleted == False  # noqa: E712
        ).count()


def search_existing_trainees(partial_name: str) -> List[Trainee]:
    """
    بحث عن متدربين بالاسم الجزئي — يُستدعى أثناء الكتابة (§5.4).
    
    Args:
        partial_name: جزء من اسم المتدرب
    
    Returns:
        list[Trainee]: أقرب 10 نتائج مطابقة
    """
    with get_session() as session:
        results = session.query(Trainee).filter(
            Trainee.name.ilike(f"%{partial_name}%"),
            Trainee.is_deleted == False  # noqa: E712
        ).limit(10).all()
        for r in results:
            session.expunge(r)
        return results


def get_all_trainees() -> List[Trainee]:
    """
    جلب جميع المتدربين النشطين.
    
    Returns:
        list[Trainee]: قائمة المتدربين
    """
    with get_session() as session:
        results = session.query(Trainee).filter(
            Trainee.is_deleted == False  # noqa: E712
        ).order_by(Trainee.name).all()
        for r in results:
            session.expunge(r)
        return results


def get_current_trainees() -> List[Trainee]:
    """جلب جميع المتدربين المسجلين في دورات جارية حالياً."""
    with get_session() as session:
        # Get active course IDs (status is 'جارية')
        active_course_ids = [c.id for c in session.query(TrainingProgram).filter(
            TrainingProgram.status == "جارية",
            TrainingProgram.is_deleted == False  # noqa: E712
        ).all()]
        
        if not active_course_ids:
            return []
            
        # Get trainees enrolled in those courses
        trainees = session.query(Trainee).join(
            CourseEnrollment, CourseEnrollment.trainee_id == Trainee.id
        ).filter(
            CourseEnrollment.course_id.in_(active_course_ids),
            Trainee.is_deleted == False  # noqa: E712
        ).distinct().order_by(Trainee.name).all()
        
        for t in trainees:
            session.expunge(t)
        return trainees


def get_past_trainees() -> List[Trainee]:
    """جلب المتدربين السابقين (الذين لديهم دورات سابقة وليس لديهم أي دورات جارية)."""
    with get_session() as session:
        # Get active course IDs
        active_course_ids = [c.id for c in session.query(TrainingProgram).filter(
            TrainingProgram.status == "جارية",
            TrainingProgram.is_deleted == False  # noqa: E712
        ).all()]
        
        active_trainee_ids = []
        if active_course_ids:
            active_trainee_ids = [e.trainee_id for e in session.query(CourseEnrollment).filter(
                CourseEnrollment.course_id.in_(active_course_ids)
            ).all()]
            
        # Get trainees enrolled in any course, but exclude those currently in active courses
        query = session.query(Trainee).join(
            CourseEnrollment, CourseEnrollment.trainee_id == Trainee.id
        ).filter(
            Trainee.is_deleted == False  # noqa: E712
        )
        
        if active_trainee_ids:
            query = query.filter(~Trainee.id.in_(active_trainee_ids))
            
        trainees = query.distinct().order_by(Trainee.name).all()
        for t in trainees:
            session.expunge(t)
        return trainees


def create_trainee(data: dict) -> Trainee:
    """
    إنشاء متدرب جديد.
    
    Args:
        data: بيانات المتدرب (name, email, phone, ...)
    
    Returns:
        Trainee: المتدرب المُنشأ
    """
    if not data.get("name"):
        raise ValueError("اسم المتدرب مطلوب")
    
    with get_session() as session:
        trainee = Trainee(**data)
        session.add(trainee)
        session.flush()
        session.refresh(trainee)
        session.expunge(trainee)
        return trainee


def get_all_trainers() -> List[Trainer]:
    """
    جلب جميع المدربين النشطين.
    
    Returns:
        list[Trainer]: قائمة المدربين
    """
    with get_session() as session:
        results = session.query(Trainer).filter(
            Trainer.is_deleted == False  # noqa: E712
        ).order_by(Trainer.name).all()
        for r in results:
            session.expunge(r)
        return results


def create_trainer(data: dict) -> Trainer:
    """
    إنشاء مدرب جديد.
    
    Args:
        data: بيانات المدرب (name, specialization, ...)
    
    Returns:
        Trainer: المدرب المُنشأ
    """
    if not data.get("name"):
        raise ValueError("اسم المدرب مطلوب")
    
    with get_session() as session:
        trainer = Trainer(**data)
        session.add(trainer)
        session.flush()
        session.refresh(trainer)
        session.expunge(trainer)
        return trainer


# ─── Training Program Extension CRUD ──────────────────────────────────────────

def get_program_by_id(program_id: int) -> Optional[TrainingProgram]:
    """جلب برنامج تدريبي بالمعرّف."""
    with get_session() as session:
        program = session.query(TrainingProgram).filter(
            TrainingProgram.id == program_id,
            TrainingProgram.is_deleted == False  # noqa: E712
        ).first()
        if program:
            session.expunge(program)
        return program


def update_program(program_id: int, data: dict) -> Optional[TrainingProgram]:
    """تحديث بيانات برنامج تدريبي."""
    with get_session() as session:
        program = session.query(TrainingProgram).filter(
            TrainingProgram.id == program_id,
            TrainingProgram.is_deleted == False  # noqa: E712
        ).first()
        
        if not program:
            return None
        
        for key, value in data.items():
            if hasattr(program, key):
                setattr(program, key, value)
        
        session.flush()
        session.refresh(program)
        session.expunge(program)
        return program


def soft_delete_program(program_id: int) -> bool:
    """حذف ناعم لبرنامج تدريبي."""
    with get_session() as session:
        program = session.query(TrainingProgram).filter(
            TrainingProgram.id == program_id
        ).first()
        
        if not program:
            return False
        
        program.is_deleted = True
        return True


# ─── Trainee CRUD ────────────────────────────────────────────────────────────

def get_trainee_by_id(trainee_id: int) -> Optional[Trainee]:
    """جلب متدرب بالمعرّف."""
    with get_session() as session:
        trainee = session.query(Trainee).filter(
            Trainee.id == trainee_id,
            Trainee.is_deleted == False  # noqa: E712
        ).first()
        if trainee:
            session.expunge(trainee)
        return trainee


def update_trainee(trainee_id: int, data: dict) -> Optional[Trainee]:
    """تحديث بيانات متدرب."""
    with get_session() as session:
        trainee = session.query(Trainee).filter(
            Trainee.id == trainee_id,
            Trainee.is_deleted == False  # noqa: E712
        ).first()
        
        if not trainee:
            return None
        
        for key, value in data.items():
            if hasattr(trainee, key):
                setattr(trainee, key, value)
        
        session.flush()
        session.refresh(trainee)
        session.expunge(trainee)
        return trainee


def soft_delete_trainee(trainee_id: int) -> bool:
    """حذف ناعم لمتدرب."""
    with get_session() as session:
        trainee = session.query(Trainee).filter(
            Trainee.id == trainee_id
        ).first()
        
        if not trainee:
            return False
        
        trainee.is_deleted = True
        return True


# ─── Trainer CRUD ────────────────────────────────────────────────────────────

def get_trainer_by_id(trainer_id: int) -> Optional[Trainer]:
    """جلب مدرب بالمعرّف."""
    with get_session() as session:
        trainer = session.query(Trainer).filter(
            Trainer.id == trainer_id,
            Trainer.is_deleted == False  # noqa: E712
        ).first()
        if trainer:
            session.expunge(trainer)
        return trainer


def update_trainer(trainer_id: int, data: dict) -> Optional[Trainer]:
    """تحديث بيانات مدرب."""
    with get_session() as session:
        trainer = session.query(Trainer).filter(
            Trainer.id == trainer_id,
            Trainer.is_deleted == False  # noqa: E712
        ).first()
        
        if not trainer:
            return None
        
        for key, value in data.items():
            if hasattr(trainer, key):
                setattr(trainer, key, value)
        
        session.flush()
        session.refresh(trainer)
        session.expunge(trainer)
        return trainer


def soft_delete_trainer(trainer_id: int) -> bool:
    """حذف ناعم لمدرب."""
    with get_session() as session:
        trainer = session.query(Trainer).filter(
            Trainer.id == trainer_id
        ).first()
        
        if not trainer:
            return False
        
        trainer.is_deleted = True
        return True


# ─── Course Enrollment Operations ─────────────────────────────────────────────

def enroll_trainee(course_id: int, trainee_id: Optional[int], trainee_data: Optional[dict], enrollment_data: dict) -> CourseEnrollment:
    """
    تسجيل متدرب في دورة تدريبية.
    إذا تم توفير trainee_id، يتم استخدامه.
    إذا تم توفير trainee_data، يتم إنشاء متدرب جديد أولاً.
    """
    with get_session() as session:
        if trainee_id:
            trainee = session.query(Trainee).filter(Trainee.id == trainee_id, Trainee.is_deleted == False).first() # noqa: E712
            if not trainee:
                raise ValueError("المتدرب المحدد غير موجود")
        elif trainee_data:
            if not trainee_data.get("name"):
                raise ValueError("اسم المتدرب مطلوب")
            trainee = Trainee(**trainee_data)
            session.add(trainee)
            session.flush()
        else:
            raise ValueError("يجب تحديد متدرب أو إدخال بيانات متدرب جديد")

        # Check if already enrolled in this course
        existing = session.query(CourseEnrollment).filter(
            CourseEnrollment.course_id == course_id,
            CourseEnrollment.trainee_id == trainee.id
        ).first()
        if existing:
            raise ValueError("المتدرب مسجل بالفعل في هذه الدورة")

        # Create enrollment
        enrollment = CourseEnrollment(
            course_id=course_id,
            trainee_id=trainee.id,
            enrollment_status=enrollment_data.get("enrollment_status", "مبدئي"),
            payment_method=enrollment_data.get("payment_method"),
            amount_paid=enrollment_data.get("amount_paid"),
        )
        session.add(enrollment)
        session.flush()
        session.refresh(enrollment)
        session.expunge(enrollment)
        return enrollment


def get_enrolled_trainees(course_id: int) -> List[CourseEnrollment]:
    """جلب جميع المتدربين المسجلين في دورة معينة."""
    with get_session() as session:
        results = session.query(CourseEnrollment).options(
            joinedload(CourseEnrollment.trainee)
        ).filter(
            CourseEnrollment.course_id == course_id
        ).all()
        for r in results:
            session.expunge(r)
            if r.trainee:
                session.expunge(r.trainee)
        return results


def get_enrollment_by_id(enrollment_id: int) -> Optional[CourseEnrollment]:
    """جلب تسجيل بالمعرّف."""
    with get_session() as session:
        enrollment = session.query(CourseEnrollment).filter(
            CourseEnrollment.id == enrollment_id
        ).first()
        if enrollment:
            session.expunge(enrollment)
        return enrollment


def update_enrollment(enrollment_id: int, data: dict) -> Optional[CourseEnrollment]:
    """تحديث بيانات التسجيل (مثل حالة الدفع أو طلب الاسترجاع)."""
    with get_session() as session:
        enrollment = session.query(CourseEnrollment).filter(
            CourseEnrollment.id == enrollment_id
        ).first()
        
        if not enrollment:
            return None
        
        for key, value in data.items():
            if hasattr(enrollment, key):
                setattr(enrollment, key, value)
        
        session.flush()
        session.refresh(enrollment)
        session.expunge(enrollment)
        return enrollment


def delete_enrollment(enrollment_id: int) -> bool:
    """إلغاء وحذف تسجيل طالب بالكامل من الدورة."""
    with get_session() as session:
        enrollment = session.query(CourseEnrollment).filter(
            CourseEnrollment.id == enrollment_id
        ).first()
        if not enrollment:
            return False
        session.delete(enrollment)
        return True


def get_courses_at_min_capacity() -> List[TrainingProgram]:
    """
    جلب الدورات التي وصلت للحد الأدنى (عدد المسجلين >= min_trainees).
    """
    with get_session() as session:
        programs = session.query(TrainingProgram).options(
            joinedload(TrainingProgram.enrollments)
        ).filter(
            TrainingProgram.is_deleted == False,  # noqa: E712
            TrainingProgram.min_trainees.isnot(None)
        ).all()
        
        results = []
        for p in programs:
            enrolled = len([e for e in p.enrollments if not e.refund_requested])
            if enrolled >= p.min_trainees:
                for e in p.enrollments:
                    if e in session:
                        session.expunge(e)
                if p in session:
                    session.expunge(p)
                results.append(p)
        return results


def get_courses_over_capacity() -> List[TrainingProgram]:
    """
    جلب الدورات التي تجاوزت الحد الأعلى (عدد المسجلين > max_trainees).
    """
    with get_session() as session:
        programs = session.query(TrainingProgram).options(
            joinedload(TrainingProgram.enrollments)
        ).filter(
            TrainingProgram.is_deleted == False,  # noqa: E712
            TrainingProgram.max_trainees.isnot(None)
        ).all()
        
        results = []
        for p in programs:
            enrolled = len([e for e in p.enrollments if not e.refund_requested])
            if enrolled > p.max_trainees:
                for e in p.enrollments:
                    if e in session:
                        session.expunge(e)
                if p in session:
                    session.expunge(p)
                results.append(p)
        return results

