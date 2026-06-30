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


    def test_trainee_status_filtering(self):
        from services import training_service
        
        # Create courses
        c1 = training_service.create_program({"name": "دورة جارية حالياً", "status": "جارية"})
        c2 = training_service.create_program({"name": "دورة مكتملة سابقة", "status": "مكتملة"})
        
        # Create trainees
        t1 = training_service.create_trainee({"name": "متدرب حالي"})
        t2 = training_service.create_trainee({"name": "متدرب سابق"})
        t3 = training_service.create_trainee({"name": "متدرب غير مسجل"})
        
        # Enroll t1 in active c1
        training_service.enroll_trainee(c1.id, t1.id, None, {"enrollment_status": "نهائي"})
        # Enroll t2 in completed c2
        training_service.enroll_trainee(c2.id, t2.id, None, {"enrollment_status": "نهائي"})
        
        # Fetch current trainees
        current = training_service.get_current_trainees()
        current_ids = [t.id for t in current]
        assert t1.id in current_ids
        assert t2.id not in current_ids
        assert t3.id not in current_ids
        
        # Fetch past trainees
        past = training_service.get_past_trainees()
        past_ids = [t.id for t in past]
        assert t2.id in past_ids
        assert t1.id not in past_ids
        assert t3.id not in past_ids


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

    def test_voucher_deletion_and_balance_recalculation(self):
        from services import finance_service
        from models.enums import VoucherType, PaymentMethod, RegisterType
        from core.database import get_session
        from models.cash_register import CashRegister

        # Create Receipt Voucher 1 (CASH)
        v1 = finance_service.create_voucher({
            "voucher_type": VoucherType.RECEIPT,
            "party_name": "الطرف الأول",
            "amount": Decimal("1000.00"),
            "payment_method": PaymentMethod.CASH
        })
        # Create Receipt Voucher 2 (CASH)
        v2 = finance_service.create_voucher({
            "voucher_type": VoucherType.RECEIPT,
            "party_name": "الطرف الثاني",
            "amount": Decimal("500.00"),
            "payment_method": PaymentMethod.CASH
        })
        # Create Receipt Voucher 3 (CASH)
        v3 = finance_service.create_voucher({
            "voucher_type": VoucherType.RECEIPT,
            "party_name": "الطرف الثالث",
            "amount": Decimal("300.00"),
            "payment_method": PaymentMethod.CASH
        })

        assert finance_service.get_cash_balance() == Decimal("1800.00")

        # Delete the middle voucher (v2)
        finance_service.delete_voucher(v2.id)

        # Cash balance should be recalculated to 1300 (v1 + v3)
        assert finance_service.get_cash_balance() == Decimal("1300.00")

        # Verify running balance (balance_after) in the remaining logs
        with get_session() as session:
            logs = session.query(CashRegister).filter(
                CashRegister.register_type == RegisterType.CASH
            ).order_by(CashRegister.created_at.asc(), CashRegister.id.asc()).all()
            
            assert len(logs) == 2
            assert logs[0].balance_after == Decimal("1000.00")
            assert logs[1].balance_after == Decimal("1300.00")

    def test_expense_deletion_and_cascade_recalculation(self):
        from services import finance_service
        from models.enums import VoucherType, PaymentMethod, RegisterType
        from core.database import get_session
        from models.cash_register import CashRegister

        # Seed register with cash
        finance_service.create_voucher({
            "voucher_type": VoucherType.RECEIPT,
            "party_name": "تمويل",
            "amount": Decimal("5000.00"),
            "payment_method": PaymentMethod.CASH
        })

        # Create manual expense 1
        ex1 = finance_service.create_expense({
            "name": "صيانة أجهزة",
            "unit_price": Decimal("1000.00"),
            "quantity": Decimal("1"),
            "payment_method": PaymentMethod.CASH
        })
        # Create manual expense 2
        ex2 = finance_service.create_expense({
            "name": "قرطاسية",
            "unit_price": Decimal("500.00"),
            "quantity": Decimal("1"),
            "payment_method": PaymentMethod.CASH
        })

        assert finance_service.get_cash_balance() == Decimal("3500.00")

        # Delete manual expense 1
        finance_service.delete_expense(ex1.id)

        # Balance should be recalculated to 4500 (5000 - 500)
        assert finance_service.get_cash_balance() == Decimal("4500.00")

        with get_session() as session:
            # Verify the cash register log of ex1 is deleted
            logs = session.query(CashRegister).filter(CashRegister.related_expense_id == ex1.id).all()
            assert len(logs) == 0

    def test_invoice_deletion_and_recalculation(self):
        from services import finance_service, client_service
        from models.enums import ClientType, ServiceType, ProposalStatus, RegisterType
        from core.database import get_session
        from models.cash_register import CashRegister

        cl = client_service.create_client({"name": "وزارة التعليم", "client_type": ClientType.INSTITUTION})
        prop = finance_service.create_proposal(
            data={"client_id": cl.id, "service_type": ServiceType.TRAINING},
            line_items=[{"service_type": ServiceType.TRAINING, "unit_description": "عقد", "quantity": 1, "unit_price": 2000, "total": 2000}]
        )

        # Approve proposal to generate Invoice and CashRegister (BANK)
        inv = finance_service.approve_proposal(prop.id)
        assert inv is not None
        assert finance_service.get_bank_balance() == Decimal("2000.00")

        # Delete the Invoice
        finance_service.delete_invoice(inv.id)

        # Bank balance should recalculate to 0
        assert finance_service.get_bank_balance() == Decimal("0.00")

        with get_session() as session:
            # Check the cash log was deleted
            logs = session.query(CashRegister).filter(CashRegister.related_invoice_id == inv.id).all()
            assert len(logs) == 0
            
            # Check proposal reverted to PENDING
            p_reverted = session.query(prop.__class__).filter_by(id=prop.id).first()
            assert p_reverted.status == ProposalStatus.PENDING

    def test_proposal_approval_updates_project_budget_spent(self):
        from services import finance_service, client_service, project_service
        from models.enums import ClientType, ServiceType

        cl = client_service.create_client({"name": "شركة الخليج", "client_type": ClientType.INSTITUTION})
        proj = project_service.create_project({"name": "مشروع التدريب النفطي", "budget_allocated": Decimal("10000.00")})
        
        prop = finance_service.create_proposal(
            data={"client_id": cl.id, "service_type": ServiceType.TRAINING, "project_id": proj.id},
            line_items=[{"service_type": ServiceType.TRAINING, "unit_description": "برنامج", "quantity": 1, "unit_price": 4000, "total": 4000}]
        )

        assert proj.budget_spent == Decimal("0.00")

        # Approve proposal
        finance_service.approve_proposal(prop.id)

        # Project budget_spent should be updated to 4000
        proj_updated = project_service.get_project_by_id(proj.id)
        assert proj_updated.budget_spent == Decimal("4000.00")

