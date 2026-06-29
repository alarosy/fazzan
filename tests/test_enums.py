"""
Tests for enum definitions.
اختبار تعريفات التعدادات — التحقق من القيم العربية والاكتمال.
"""
import pytest
from models.enums import (
    ClientType, PaymentMethod, EmploymentType, CourseCategory,
    TrainerPayType, ServiceType, SpecCategory, SectorType,
    ProposalStatus, CateringMeal, CateringLevel, RevenueSource,
    AssetCategory, AssetOwnership, VoucherType, RegisterType
)


class TestEnums:
    """Test all 16 enum classes have correct members and Arabic values."""

    def test_client_type(self):
        assert len(ClientType) == 3
        assert ClientType.INDIVIDUAL.value == "فرد"
        assert ClientType.INSTITUTION.value == "مؤسسة"
        assert ClientType.PARTNERSHIP.value == "شراكة"

    def test_payment_method(self):
        assert len(PaymentMethod) == 2
        assert PaymentMethod.CASH.value == "كاش"
        assert PaymentMethod.BANK.value == "تحويل مصرفي"

    def test_employment_type(self):
        assert len(EmploymentType) == 2
        assert EmploymentType.PERMANENT.value == "دائم"
        assert EmploymentType.TEMPORARY.value == "غير دائم"

    def test_course_category(self):
        assert len(CourseCategory) == 4
        assert CourseCategory.INDEPENDENT.value == "مستقلة"
        assert CourseCategory.PROJECT.value == "تدريبات مشاريع"

    def test_trainer_pay_type(self):
        assert len(TrainerPayType) == 2
        assert TrainerPayType.FIXED_COURSE.value == "مبلغ ثابت للدورة"
        assert TrainerPayType.PER_TRAINEE.value == "قيمة لكل متدرب"

    def test_service_type(self):
        assert len(ServiceType) == 5
        assert ServiceType.TRAINING.value == "تدريب"
        assert ServiceType.CONSULTING.value == "استشارة"

    def test_spec_category(self):
        assert len(SpecCategory) == 5
        assert SpecCategory.PROFESSIONAL.value == "مهنية"
        assert SpecCategory.AWARENESS.value == "محاضرات وتوعية"

    def test_sector_type(self):
        assert len(SectorType) == 2
        assert SectorType.GOVERNMENT.value == "حكومية"
        assert SectorType.PRIVATE.value == "خاصة"

    def test_proposal_status(self):
        assert len(ProposalStatus) == 3
        assert ProposalStatus.PENDING.value == "قيد الانتظار"
        assert ProposalStatus.APPROVED.value == "معتمد"
        assert ProposalStatus.REJECTED.value == "مرفوض"

    def test_catering_meal(self):
        assert len(CateringMeal) == 4
        assert CateringMeal.BREAKFAST.value == "فطور"
        assert CateringMeal.COFFEE.value == "استراحة قهوة"

    def test_catering_level(self):
        assert len(CateringLevel) == 3
        assert CateringLevel.BASIC.value == "عادي"
        assert CateringLevel.LUXURY.value == "فاخر"

    def test_revenue_source(self):
        assert len(RevenueSource) == 6
        assert RevenueSource.TRAINING.value == "تدريب"
        assert RevenueSource.TRAINER_FEE.value == "وساطة مدرب"

    def test_asset_category(self):
        assert len(AssetCategory) == 4
        assert AssetCategory.FURNITURE.value == "أثاث"
        assert AssetCategory.DEVICES.value == "أجهزة"

    def test_asset_ownership(self):
        assert len(AssetOwnership) == 2
        assert AssetOwnership.OWNED.value == "مملوكة"
        assert AssetOwnership.BORROWED.value == "مستعارة"

    def test_voucher_type(self):
        assert len(VoucherType) == 2
        assert VoucherType.RECEIPT.value == "قبض"
        assert VoucherType.DISBURSEMENT.value == "صرف"

    def test_register_type(self):
        assert len(RegisterType) == 2
        assert RegisterType.CASH.value == "كاش"
        assert RegisterType.BANK.value == "مصرف"

    def test_all_enums_have_string_values(self):
        """Every enum value must be an Arabic string."""
        all_enums = [
            ClientType, PaymentMethod, EmploymentType, CourseCategory,
            TrainerPayType, ServiceType, SpecCategory, SectorType,
            ProposalStatus, CateringMeal, CateringLevel, RevenueSource,
            AssetCategory, AssetOwnership, VoucherType, RegisterType
        ]
        for enum_cls in all_enums:
            for member in enum_cls:
                assert isinstance(member.value, str), (
                    f"{enum_cls.__name__}.{member.name} value is not str: {member.value}"
                )
                assert len(member.value) > 0, (
                    f"{enum_cls.__name__}.{member.name} has empty value"
                )
