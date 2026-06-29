"""
Tests for Phase B — Training and Course Enrollments.
اختبارات المرحلة الثانية — إدارة التدريب وحجوزات القاعات.
"""
import os
import sys
import pytest
from datetime import date, timedelta
from decimal import Decimal

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from models import Base
from models.training_program import TrainingProgram
from models.trainee import Trainee
from models.course_enrollment import CourseEnrollment
from models.enums import CourseCategory, TrainerPayType, PaymentMethod


@pytest.fixture(autouse=True)
def mock_db(tmp_path):
    """
    Patch database to use a temporary SQLite for each test.
    تهيئة قاعدة بيانات مؤقتة مع تفعيل القيود لكل اختبار.
    """
    db_path = str(tmp_path / "test_phase_b.db")
    test_engine = create_engine(f"sqlite:///{db_path}", echo=False)
    
    @event.listens_for(test_engine, "connect")
    def _pragma(dbapi_conn, conn_rec):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
    
    Base.metadata.create_all(test_engine)
    TestSession = sessionmaker(bind=test_engine, autoflush=True, autocommit=False)
    
    import core.database as db_mod
    original_session = db_mod.SessionLocal
    db_mod.SessionLocal = TestSession
    
    yield TestSession
    
    db_mod.SessionLocal = original_session


class TestPhaseBModels:

    def test_course_enrollment_creation(self, db_session=None):
        """التحقق من إنشاء نموذج التسجيل بنجاح."""
        import services.training_service as ts
        
        course = ts.create_program({"name": "دورة اختبارية B"})
        trainee = ts.create_trainee({"name": "متدرب تجريبي B", "phone": "0910000000"})
        
        enrollment = ts.enroll_trainee(
            course_id=course.id,
            trainee_id=trainee.id,
            trainee_data=None,
            enrollment_data={
                "enrollment_status": "نهائي",
                "payment_method": PaymentMethod.CASH,
                "amount_paid": Decimal("250.00")
            }
        )
        
        assert enrollment.id is not None
        assert enrollment.course_id == course.id
        assert enrollment.trainee_id == trainee.id
        assert enrollment.enrollment_status == "نهائي"
        assert enrollment.amount_paid == Decimal("250.00")


class TestPhaseBServices:

    def test_enroll_new_trainee_on_the_fly(self):
        """تسجيل متدرب جديد كلياً وإنشاؤه تلقائياً أثناء التسجيل."""
        import services.training_service as ts
        
        course = ts.create_program({"name": "دورة إدارة الأعمال"})
        
        # Enroll with trainee_data
        enrollment = ts.enroll_trainee(
            course_id=course.id,
            trainee_id=None,
            trainee_data={
                "name": "أحمد الجديد",
                "phone": "0921111111",
                "gender": "ذكر"
            },
            enrollment_data={
                "enrollment_status": "مبدئي",
                "payment_method": PaymentMethod.BANK,
                "amount_paid": Decimal("150.00")
            }
        )
        
        assert enrollment.id is not None
        
        # Verify trainee was created
        trainee = ts.get_trainee_by_id(enrollment.trainee_id)
        assert trainee is not None
        assert trainee.name == "أحمد الجديد"
        assert trainee.phone == "0921111111"

    def test_duplicate_enrollment_raises(self):
        """التحقق من منع تسجيل نفس المتدرب في نفس الدورة مرتين."""
        import services.training_service as ts
        
        course = ts.create_program({"name": "دورة البرمجة"})
        trainee = ts.create_trainee({"name": "علي", "phone": "0912222222"})
        
        # First enroll
        ts.enroll_trainee(course.id, trainee.id, None, {"enrollment_status": "مبدئي"})
        
        # Second enroll (should raise ValueError)
        with pytest.raises(ValueError, match="المتدرب مسجل بالفعل"):
            ts.enroll_trainee(course.id, trainee.id, None, {"enrollment_status": "مبدئي"})

    def test_courses_at_min_capacity(self):
        """التحقق من جلب الدورات التي وصلت للحد الأدنى بنجاح."""
        import services.training_service as ts
        
        course1 = ts.create_program({"name": "دورة 1", "min_trainees": 2})
        course2 = ts.create_program({"name": "دورة 2", "min_trainees": 5})
        
        t1 = ts.create_trainee({"name": "متدرب 1"})
        t2 = ts.create_trainee({"name": "متدرب 2"})
        
        # Enroll 2 trainees in course1 (reaches min of 2)
        ts.enroll_trainee(course1.id, t1.id, None, {})
        ts.enroll_trainee(course1.id, t2.id, None, {})
        
        min_courses = ts.get_courses_at_min_capacity()
        ids = [c.id for c in min_courses]
        
        assert course1.id in ids
        assert course2.id not in ids

    def test_courses_over_capacity(self):
        """التحقق من جلب الدورات التي تجاوزت الحد الأقصى بنجاح."""
        import services.training_service as ts
        
        course = ts.create_program({"name": "دورة تجريبية", "max_trainees": 1})
        
        t1 = ts.create_trainee({"name": "متدرب 1"})
        t2 = ts.create_trainee({"name": "متدرب 2"})
        
        # Enroll 2 trainees (limit is 1)
        ts.enroll_trainee(course.id, t1.id, None, {})
        ts.enroll_trainee(course.id, t2.id, None, {})
        
        over_courses = ts.get_courses_over_capacity()
        ids = [c.id for c in over_courses]
        
        assert course.id in ids

    def test_refund_enrollment(self):
        """التحقق من تحديث بيانات التسجيل وإرجاع الرسوم."""
        import services.training_service as ts
        
        course = ts.create_program({"name": "دورة مالي"})
        t = ts.create_trainee({"name": "سعيد"})
        en = ts.enroll_trainee(course.id, t.id, None, {"amount_paid": Decimal("500.00")})
        
        # Request refund
        updated = ts.update_enrollment(en.id, {
            "refund_requested": True,
            "refund_amount": Decimal("500.00"),
            "refund_date": date.today()
        })
        
        assert updated.refund_requested is True
        assert updated.refund_amount == Decimal("500.00")
