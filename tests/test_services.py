"""
Tests for service layer — CRUD operations via services.
اختبار طبقة الخدمات — عمليات CRUD عبر الخدمات.
"""
import os
import sys
import pytest
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from models import Base


@pytest.fixture(autouse=True)
def mock_db(tmp_path):
    """
    Patch core.database to use a temporary SQLite for each test.
    يستبدل اتصال قاعدة البيانات بقاعدة مؤقتة لكل اختبار.
    """
    db_path = str(tmp_path / "test.db")
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


class TestHRService:

    def test_create_employee(self):
        from services import hr_service
        emp = hr_service.create_employee({"name": "أحمد", "phone": "0912345678"})
        assert emp.id is not None
        assert emp.name == "أحمد"

    def test_get_all_employees(self):
        from services import hr_service
        hr_service.create_employee({"name": "سالم"})
        hr_service.create_employee({"name": "خالد"})
        employees = hr_service.get_all_employees()
        assert len(employees) >= 2

    def test_soft_delete_employee(self):
        from services import hr_service
        emp = hr_service.create_employee({"name": "للحذف"})
        result = hr_service.soft_delete_employee(emp.id)
        assert result == True
        
        all_emps = hr_service.get_all_employees()
        assert all(e.name != "للحذف" for e in all_emps)

    def test_count_active_employees(self):
        from services import hr_service
        hr_service.create_employee({"name": "موظف1"})
        hr_service.create_employee({"name": "موظف2"})
        count = hr_service.count_active_employees()
        assert count >= 2

    def test_expiring_contracts(self):
        from services import hr_service
        # Employee with contract ending in 15 days
        hr_service.create_employee({
            "name": "عقد قريب",
            "contract_end_date": date.today() + timedelta(days=15)
        })
        # Employee with contract ending in 60 days (outside window)
        hr_service.create_employee({
            "name": "عقد بعيد",
            "contract_end_date": date.today() + timedelta(days=60)
        })
        
        expiring = hr_service.get_expiring_contracts(30)
        names = [e.name for e in expiring]
        assert "عقد قريب" in names
        assert "عقد بعيد" not in names

    def test_create_employee_no_name_raises(self):
        from services import hr_service
        with pytest.raises(ValueError):
            hr_service.create_employee({"phone": "0912345678"})

    def test_search_employees(self):
        from services import hr_service
        hr_service.create_employee({"name": "محمد أحمد"})
        hr_service.create_employee({"name": "سالم علي"})
        
        results = hr_service.search_employees("محمد")
        assert len(results) >= 1
        assert any("محمد" in e.name for e in results)


class TestClientService:

    def test_create_client(self):
        from services import client_service
        client = client_service.create_client({
            "name": "شركة التقنية",
            "client_type": "مؤسسة"
        })
        assert client.id is not None

    def test_count_clients(self):
        from services import client_service
        client_service.create_client({"name": "عميل1", "client_type": "فرد"})
        count = client_service.count_clients()
        assert count >= 1

    def test_soft_delete_client(self):
        from services import client_service
        client = client_service.create_client({"name": "للحذف", "client_type": "فرد"})
        result = client_service.soft_delete_client(client.id)
        assert result == True

    def test_create_client_no_name_raises(self):
        from services import client_service
        with pytest.raises(ValueError):
            client_service.create_client({"client_type": "فرد"})


class TestProjectService:

    def test_create_project(self):
        from services import project_service
        project = project_service.create_project({"name": "مشروع تجريبي"})
        assert project.id is not None

    def test_count_active(self):
        from services import project_service
        project_service.create_project({"name": "مشروع نشط", "status": "نشط"})
        count = project_service.count_active()
        assert count >= 1

    def test_soft_delete_project(self):
        from services import project_service
        project = project_service.create_project({"name": "للحذف"})
        result = project_service.soft_delete_project(project.id)
        assert result == True


class TestTrainingService:

    def test_create_program(self):
        from services import training_service
        program = training_service.create_program({"name": "دورة اختبار"})
        assert program.id is not None

    def test_count_active_courses(self):
        from services import training_service
        training_service.create_program({"name": "دورة جارية", "status": "جارية"})
        count = training_service.count_active_courses()
        assert count >= 1

    def test_create_trainer(self):
        from services import training_service
        trainer = training_service.create_trainer({
            "name": "د. محمد",
            "specialization": "إدارة"
        })
        assert trainer.id is not None

    def test_create_trainee(self):
        from services import training_service
        trainee = training_service.create_trainee({"name": "متدرب جديد"})
        assert trainee.id is not None

    def test_search_trainees(self):
        from services import training_service
        training_service.create_trainee({"name": "أحمد الصغير"})
        results = training_service.search_existing_trainees("أحمد")
        assert len(results) >= 1


class TestFinanceService:

    def test_cash_balance_stub(self):
        from services import finance_service
        balance = finance_service.get_cash_balance()
        assert balance == Decimal("0")

    def test_bank_balance_stub(self):
        from services import finance_service
        balance = finance_service.get_bank_balance()
        assert balance == Decimal("0")

    def test_pending_proposals_stub(self):
        from services import finance_service
        count = finance_service.count_pending_proposals()
        assert count == 0
