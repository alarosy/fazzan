"""
Tests for Phase C — Logistics Services.
اختبارات المرحلة الثالثة — الخدمات اللوجستية والجانبية.
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
from models.consultant import Consultant
from models.catering import CateringOrder
from models.accommodation import AccommodationBooking
from models.market_research import MarketResearch
from models.enums import SpecCategory, PaymentMethod, CateringMeal, CateringLevel


@pytest.fixture(autouse=True)
def mock_db(tmp_path):
    """تهيئة قاعدة بيانات مؤقتة لكل اختبار."""
    db_path = str(tmp_path / "test_phase_c.db")
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


class TestPhaseCService:

    def test_consultant_crud(self):
        """التحقق من إنشاء وتعديل وحذف مستشار."""
        import services.consultant_service as cs
        
        c = cs.create_consultant({
            "name": "د. محمد المستشار",
            "specialization": SpecCategory.TECHNICAL,
            "gross_value": Decimal("1000.00"),
            "consultant_share": Decimal("700.00"),
            "center_share": Decimal("300.00")
        })
        assert c.id is not None
        assert c.name == "د. محمد المستشار"
        
        # Update
        updated = cs.update_consultant(c.id, {"phone": "0911234567"})
        assert updated.phone == "0911234567"
        
        # Soft delete
        assert cs.soft_delete_consultant(c.id) is True
        assert len(cs.get_all_consultants()) == 0

    def test_catering_order_with_extras(self):
        """التحقق من إنشاء طلبية تموين بملحقاتها وحساب تكلفة إضافية."""
        import services.catering_service as cat_s
        
        order = cat_s.create_catering_order(
            order_data={
                "meal_type": CateringMeal.LUNCH,
                "service_level": CateringLevel.SPECIAL,
                "pricing_mode": "per_person",
                "num_persons": 10,
                "num_days": 2,
                "unit_price": Decimal("25.00")
            },
            extras=[
                {"service_name": "عصائر طبيعية", "price": Decimal("50.00")},
                {"service_name": "مياه VIP", "price": Decimal("20.00")}
            ]
        )
        
        assert order.id is not None
        assert len(order.extra_services) == 2
        
        # Verify total price formula
        extras_sum = sum(float(ex.price) for ex in order.extra_services)
        assert extras_sum == pytest.approx(70.00)
        
        # Update
        updated = cat_s.update_catering_order(order.id, {"unit_price": Decimal("30.00")}, extras=[
            {"service_name": "ضيافة VIP", "price": Decimal("100.00")}
        ])
        assert updated.unit_price == Decimal("30.00")
        assert len(updated.extra_services) == 1

    def test_accommodation_booking(self):
        """التحقق من حجز السكن والتحقق من حساب الأيام والتاريخ."""
        import services.accommodation_service as acc_s
        
        in_d = date.today()
        out_d = date.today() + timedelta(days=5)
        
        booking = acc_s.create_booking(
            booking_data={
                "apartment_type": "A1",
                "check_in_date": in_d,
                "check_out_date": out_d
            },
            extras=[
                {"service_name": "إنترنت سريع", "price": Decimal("45.00")}
            ]
        )
        
        assert booking.id is not None
        assert (booking.check_out_date - booking.check_in_date).days == 5
        
        # Try invalid dates (check-in >= check-out)
        with pytest.raises(ValueError, match="تاريخ الدخول يجب أن يكون قبل تاريخ المغادرة"):
            acc_s.create_booking({
                "apartment_type": "B2",
                "check_in_date": out_d,
                "check_out_date": in_d
            })

    def test_market_research_crud(self):
        """التحقق من إنشاء ودراسات بحوث السوق."""
        import services.market_research_service as mr_s
        
        r = mr_s.create_research({
            "collection_method": "field",
            "collection_type": "دراسة جدوى الاتصالات",
            "min_samples": 50,
            "max_samples": 500,
            "min_price": Decimal("2000.00"),
            "max_price": Decimal("5000.00")
        })
        
        assert r.id is not None
        assert r.collection_method == "field"
        
        # Delete
        assert mr_s.delete_research(r.id) is True
