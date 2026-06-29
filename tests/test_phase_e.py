"""
Tests for Phase E — Contracts and Advanced Features.
اختبارات المرحلة الخامسة — العقود والتقارير المتقدمة.
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
from models.project import Project
from models.contract import Contract
from models.partner import Partner
from models.client import Client
from models.enums import ContractStatus, PartnerType, VoucherType, PaymentMethod


@pytest.fixture(autouse=True)
def mock_db(tmp_path):
    """تهيئة قاعدة بيانات مؤقتة لكل اختبار."""
    db_path = str(tmp_path / "test_phase_e.db")
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


class TestPhaseEAdvanced:

    def test_project_extensions(self):
        """التحقق من حقول المشاريع الإضافية ومتابعة الميزانيات."""
        import services.project_service as ps
        
        proj = ps.create_project({
            "name": "مشروع حفر الآبار",
            "project_number": "PROJ-2026-999",
            "geographic_scope": "سبها، ليبيا",
            "budget_allocated": Decimal("80000.00"),
            "budget_spent": Decimal("20000.00")
        })
        
        assert proj.id is not None
        assert proj.project_number == "PROJ-2026-999"
        assert proj.geographic_scope == "سبها، ليبيا"
        assert proj.budget_allocated == Decimal("80000.00")
        assert proj.budget_spent == Decimal("20000.00")
        
        # Verify update budget spent works
        updated = ps.update_project(proj.id, {"budget_spent": Decimal("30000.00")})
        assert updated.budget_spent == Decimal("30000.00")

    def test_contracts_crud(self):
        """التحقق من إنشاء وتعديل وحذف العقود والاتفاقيات."""
        import services.contract_service as cs
        import services.client_service as cls
        import services.project_service as ps
        
        cl = cls.create_client({"name": "وزارة المياه", "client_type": "مؤسسة"})
        proj = ps.create_project({"name": "مشروع السدود"})
        
        c = cs.create_contract({
            "title": "عقد صيانة السدود المائية",
            "client_id": cl.id,
            "project_id": proj.id,
            "value": Decimal("150000.00"),
            "start_date": date.today(),
            "end_date": date.today(),
            "status": ContractStatus.ACTIVE,
            "scope": "صيانة كاملة وشاملة",
            "clauses": "بند 1: الغرامة 1%"
        })
        
        assert c.id is not None
        assert c.title == "عقد صيانة السدود المائية"
        assert c.status == ContractStatus.ACTIVE
        
        # Update
        updated = cs.update_contract(c.id, {"status": ContractStatus.COMPLETED})
        assert updated.status == ContractStatus.COMPLETED
        
        # Delete
        assert cs.soft_delete_contract(c.id) is True
        assert len(cs.get_all_contracts()) == 0

    def test_partners_crud(self):
        """التحقق من إدارة بيانات الشركاء المساهمين."""
        import services.partner_service as pts
        
        p = pts.create_partner({
            "name": "مؤسسة التنمية الألمانية GIZ",
            "type": PartnerType.INTERNATIONAL,
            "phone": "021334455",
            "email": "info@giz.de",
            "contribution_details": "تمويل بقيمة 50 ألف يورو"
        })
        
        assert p.id is not None
        assert p.name == "مؤسسة التنمية الألمانية GIZ"
        assert p.type == PartnerType.INTERNATIONAL
        
        # Soft delete
        assert pts.soft_delete_partner(p.id) is True
        assert len(pts.get_all_partners()) == 0

    def test_ai_reports_generation(self):
        """التحقق من خوارزمية توليد تحليلات الـ AI Insights المالية."""
        import services.ai_report_service as ai_s
        import services.project_service as ps
        import services.finance_service as fs
        
        # Seed cash log and project data
        ps.create_project({
            "name": "مشروع التعليم الإلكتروني",
            "budget_allocated": Decimal("10000.00"),
            "budget_spent": Decimal("9500.00") # Over 90%
        })
        
        # Create cash register entries
        fs.create_voucher({
            "voucher_type": VoucherType.RECEIPT,
            "party_name": "ممول",
            "amount": Decimal("2000.00"),
            "payment_method": PaymentMethod.CASH
        })
        
        report = ai_s.generate_ai_financial_report()
        assert report is not None
        assert "AI Insights" in report
        # Verify it detected warning for over budget project
        assert "مشروع التعليم الإلكتروني" in report
