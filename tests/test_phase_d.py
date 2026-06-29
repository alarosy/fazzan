"""
Tests for Phase D — Financial System.
اختبارات المرحلة الرابعة — النظام المالي والمستندات.
"""
import os
import sys
import pytest
from datetime import date
from decimal import Decimal

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from models import Base
from models.financial_proposal import FinancialProposal
from models.invoice import Invoice
from models.voucher import Voucher
from models.expense import Expense
from models.asset import Asset
from models.cash_register import CashRegister
from models.employee import Employee
from models.project import Project
from models.client import Client
from models.enums import (
    ProposalStatus, VoucherType, PaymentMethod,
    RegisterType, RevenueSource, ServiceType,
    AssetCategory, AssetOwnership, ClientType,
    EmploymentType
)


@pytest.fixture(autouse=True)
def mock_db(tmp_path):
    """تهيئة قاعدة بيانات مؤقتة لكل اختبار."""
    db_path = str(tmp_path / "test_phase_d.db")
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


class TestPhaseDFinance:

    def test_proposal_crud_and_approval(self):
        """التحقق من دورة حياة عروض الأسعار واعتمادها إلى فواتير وقيود."""
        import services.finance_service as fs
        import services.client_service as cs
        
        # Create Client
        cl = cs.create_client({"name": "الشركة الليبية للاتصالات", "client_type": ClientType.INSTITUTION})
        
        # Create Proposal
        prop = fs.create_proposal(
            data={
                "client_id": cl.id,
                "service_type": ServiceType.TRAINING,
                "notes": "عرض تدريب لموظفي الاتصالات"
            },
            line_items=[
                {
                    "service_type": ServiceType.TRAINING,
                    "unit_description": "متدرب",
                    "quantity": Decimal("15"),
                    "unit_price": Decimal("100.00"),
                    "discount": Decimal("50.00"),
                    "total": Decimal("1450.00") # 15 * 100 - 50 = 1450
                }
            ]
        )
        
        assert prop.id is not None
        assert prop.total_value == Decimal("1450.00")
        assert prop.status == ProposalStatus.PENDING
        
        # Approve Proposal -> Should generate Invoice & CashRegister (BANK)
        inv = fs.approve_proposal(prop.id)
        assert inv is not None
        assert inv.invoice_number.startswith("INV-")
        assert inv.total_value == Decimal("1450.00")
        
        # Verify CashRegister entry
        assert fs.get_bank_balance() == Decimal("1450.00")
        assert fs.get_cash_balance() == Decimal("0.00")

    def test_vouchers_sequential_numbers_and_tafqit(self):
        """التحقق من تسلسل السندات وتوليد التفقيط العربي وحركة الخزينة."""
        import services.finance_service as fs
        
        # Create Receipt Voucher (قبض)
        v1 = fs.create_voucher({
            "voucher_type": VoucherType.RECEIPT,
            "party_name": "أحمد الطالب",
            "amount": Decimal("1250.50"),
            "payment_method": PaymentMethod.CASH,
            "revenue_source": RevenueSource.TRAINING,
            "notes": "رسوم دورة شبكات"
        })
        
        assert v1.voucher_number.startswith("REC-")
        assert v1.amount_in_words == "ألف ومئتان وخمسون ديناراً ليبياً وخمسمئة درهم"
        assert fs.get_cash_balance() == Decimal("1250.50")
        
        # Create Disbursement Voucher (صرف)
        v2 = fs.create_voucher({
            "voucher_type": VoucherType.DISBURSEMENT,
            "party_name": "مكتبة الفرجاني",
            "amount": Decimal("250.00"),
            "payment_method": PaymentMethod.CASH,
            "notes": "شراء قرطاسية"
        })
        
        assert v2.voucher_number.startswith("DISB-")
        assert fs.get_cash_balance() == Decimal("1000.50") # 1250.50 - 250 = 1000.50

    def test_employee_salary_charge_to_project(self):
        """التحقق من تحميل أجر الموظف اليومي على المشاريع."""
        import services.finance_service as fs
        import services.hr_service as hr_s
        import services.project_service as proj_s
        
        # Create Project & Employee
        emp = hr_s.create_employee({
            "name": "المهندس علي",
            "daily_wage_rate": Decimal("100.00"),
            "employment_type": EmploymentType.PERMANENT
        })
        proj = proj_s.create_project({
            "name": "مشروع حوسبة السحابية",
            "budget": Decimal("50000.00")
        })
        
        # Charge salary
        # Initialize register with some cash
        fs.create_voucher({
            "voucher_type": VoucherType.RECEIPT,
            "party_name": "ممول خارجي",
            "amount": Decimal("5000.00"),
            "payment_method": PaymentMethod.CASH
        })
        
        expense = fs.charge_employee_to_project(emp.id, proj.id, work_days=10)
        assert expense.total == Decimal("1000.00")
        assert expense.project_id == proj.id
        
        # Check cash balance was deducted
        assert fs.get_cash_balance() == Decimal("4000.00") # 5000 - 1000

    def test_pdf_exporters(self):
        """التأكد من تشغيل مصدرات مستندات الـ PDF دون أخطاء."""
        import services.finance_service as fs
        import services.client_service as cs
        import core.exporter as exp
        
        cl = cs.create_client({"name": "الجامعة الليبية", "client_type": ClientType.INSTITUTION})
        p = fs.create_proposal(
            data={"client_id": cl.id, "service_type": ServiceType.TRAINING},
            line_items=[{"service_type": ServiceType.TRAINING, "unit_description": "برنامج", "quantity": 1, "unit_price": 500, "total": 500}]
        )
        
        # Test export proposal PDF
        p_path = exp.export_proposal_pdf(p.id)
        assert os.path.exists(p_path)
        
        # Test export invoice PDF (approve proposal first)
        inv = fs.approve_proposal(p.id)
        inv_path = exp.export_invoice_pdf(inv.id)
        assert os.path.exists(inv_path)
        
        # Test export voucher PDF
        v = fs.create_voucher({
            "voucher_type": VoucherType.RECEIPT,
            "party_name": "د. أحمد",
            "amount": Decimal("200"),
            "payment_method": PaymentMethod.BANK
        })
        v_path = exp.export_voucher_pdf(v.id)
        assert os.path.exists(v_path)
        
        # Clean up files
        for path in [p_path, inv_path, v_path]:
            if os.path.exists(path):
                os.remove(path)
