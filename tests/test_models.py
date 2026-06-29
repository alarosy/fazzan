"""
Tests for data models — creation, FK constraints, soft delete.
اختبار نماذج البيانات — الإنشاء، مفاتيح العلاقات، الحذف الناعم.
"""
import os
import sys
import pytest
from datetime import date
from decimal import Decimal

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Base
from models.employee import Employee
from models.client import Client
from models.project import Project
from models.partnership import Partnership
from models.hall import Hall
from models.training_program import TrainingProgram
from models.trainee import Trainee
from models.trainer import Trainer


@pytest.fixture
def db_session():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


class TestEmployeeModel:

    def test_create_employee(self, db_session):
        emp = Employee(name="أحمد محمد", phone="0912345678", position="مدير")
        db_session.add(emp)
        db_session.commit()
        
        assert emp.id is not None
        assert emp.name == "أحمد محمد"
        assert emp.is_deleted == False

    def test_employee_with_contract(self, db_session):
        emp = Employee(
            name="سالم علي",
            contract_start_date=date(2025, 1, 1),
            contract_end_date=date(2025, 12, 31),
            daily_wage_rate=Decimal("150.00"),
            employment_type="دائم"
        )
        db_session.add(emp)
        db_session.commit()
        
        assert emp.daily_wage_rate == Decimal("150.00")
        assert emp.contract_end_date == date(2025, 12, 31)

    def test_soft_delete_employee(self, db_session):
        emp = Employee(name="خالد حسن")
        db_session.add(emp)
        db_session.commit()
        
        emp.is_deleted = True
        db_session.commit()
        
        active = db_session.query(Employee).filter(Employee.is_deleted == False).all()
        assert len(active) == 0

    def test_employee_project_fk(self, db_session):
        project = Project(name="مشروع ألف")
        db_session.add(project)
        db_session.flush()
        
        emp = Employee(name="علي عمر", current_project_id=project.id)
        db_session.add(emp)
        db_session.commit()
        
        assert emp.current_project_id == project.id


class TestClientModel:

    def test_create_individual_client(self, db_session):
        client = Client(client_type="فرد", name="محمد الأمين")
        db_session.add(client)
        db_session.commit()
        
        assert client.id is not None
        assert client.sector is None  # Not required for individuals

    def test_create_institution_client(self, db_session):
        client = Client(
            client_type="مؤسسة",
            name="شركة التقنية",
            sector="خاصة",
            contract_value=Decimal("50000.00"),
            project_name="مشروع تدريبي"
        )
        db_session.add(client)
        db_session.commit()
        
        assert client.contract_value is not None
        assert float(client.contract_value) == pytest.approx(50000.00)
        assert client.sector is not None
        # SAEnum may return the enum member or the raw value depending on config
        sector_val = client.sector.value if hasattr(client.sector, 'value') else client.sector
        assert sector_val == "خاصة"

    def test_client_partnership_fk(self, db_session):
        partnership = Partnership(name="شراكة مع جامعة طرابلس")
        db_session.add(partnership)
        db_session.flush()
        
        client = Client(
            client_type="شراكة",
            name="جامعة طرابلس",
            partnership_id=partnership.id
        )
        db_session.add(client)
        db_session.commit()
        
        assert client.partnership_id == partnership.id


class TestProjectModel:

    def test_create_project(self, db_session):
        project = Project(name="مشروع الإعمار", status="نشط")
        db_session.add(project)
        db_session.commit()
        
        assert project.id is not None
        assert project.status == "نشط"

    def test_project_soft_delete(self, db_session):
        project = Project(name="مشروع مؤقت")
        db_session.add(project)
        db_session.commit()
        
        project.is_deleted = True
        db_session.commit()
        
        active = db_session.query(Project).filter(Project.is_deleted == False).all()
        assert len(active) == 0


class TestHallModel:

    def test_create_hall(self, db_session):
        hall = Hall(name="قاعة A", capacity=30, daily_rate=Decimal("500.00"))
        db_session.add(hall)
        db_session.commit()
        
        assert hall.id is not None
        assert hall.capacity == 30
        assert hall.is_active == True


class TestTrainingProgramModel:

    def test_create_program(self, db_session):
        program = TrainingProgram(
            name="دورة إدارة المشاريع",
            start_date=date(2025, 3, 1),
            end_date=date(2025, 3, 15),
            duration_hours=60,
            status="جارية"
        )
        db_session.add(program)
        db_session.commit()
        
        assert program.id is not None
        assert program.status == "جارية"


class TestTraineeModel:

    def test_create_trainee(self, db_session):
        trainee = Trainee(
            name="فاطمة أحمد",
            phone="0923456789",
            organization="وزارة التعليم"
        )
        db_session.add(trainee)
        db_session.commit()
        
        assert trainee.id is not None
        assert trainee.is_deleted == False


class TestTrainerModel:

    def test_create_trainer(self, db_session):
        trainer = Trainer(
            name="د. عبدالله الكبير",
            specialization="إدارة الأعمال",
            is_active=True
        )
        db_session.add(trainer)
        db_session.commit()
        
        assert trainer.id is not None
        assert trainer.is_active == True
