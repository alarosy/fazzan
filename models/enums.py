"""
Central Enum definitions for the entire application.
الملف المركزي لجميع التعدادات (Enums) — يُستورَد منه في كل مكان آخر.

Rule: Every Enum is defined ONCE here. No duplicates allowed elsewhere.
"""
import enum


class ClientType(enum.Enum):
    """نوع العميل"""
    INDIVIDUAL = "فرد"
    INSTITUTION = "مؤسسة"
    PARTNERSHIP = "شراكة"


class PaymentMethod(enum.Enum):
    """طريقة الدفع"""
    CASH = "كاش"
    BANK = "تحويل مصرفي"


class EmploymentType(enum.Enum):
    """نوع التوظيف"""
    PERMANENT = "دائم"
    TEMPORARY = "غير دائم"


class CourseCategory(enum.Enum):
    """تصنيف الدورة التدريبية"""
    INDEPENDENT = "مستقلة"
    PARTNERSHIP = "شراكة"
    CSR = "مسؤولية اجتماعية"
    PROJECT = "تدريبات مشاريع"


class TrainerPayType(enum.Enum):
    """نوع أجر المدرب"""
    FIXED_COURSE = "مبلغ ثابت للدورة"
    PER_TRAINEE = "قيمة لكل متدرب"


class ServiceType(enum.Enum):
    """نوع الخدمة"""
    TRAINING = "تدريب"
    CONSULTING = "استشارة"
    HALL_RENT = "إيجار قاعة"
    ACCOMMODATION = "إيجار سكن"
    OTHER = "خدمات أخرى"


class SpecCategory(enum.Enum):
    """تصنيف التخصص"""
    PROFESSIONAL = "مهنية"
    HR_TRAINING = "موارد بشرية"
    TECHNICAL = "تقنية"
    ENTREPRENEURSHIP = "ريادة أعمال"
    AWARENESS = "محاضرات وتوعية"


class SectorType(enum.Enum):
    """نوع القطاع"""
    GOVERNMENT = "حكومية"
    PRIVATE = "خاصة"


class ProposalStatus(enum.Enum):
    """حالة العرض المالي"""
    PENDING = "قيد الانتظار"
    APPROVED = "معتمد"
    REJECTED = "مرفوض"


class CateringMeal(enum.Enum):
    """نوع الوجبة"""
    BREAKFAST = "فطور"
    LUNCH = "غداء"
    DINNER = "عشاء"
    COFFEE = "استراحة قهوة"


class CateringLevel(enum.Enum):
    """مستوى خدمة الضيافة"""
    BASIC = "عادي"
    SPECIAL = "خاص"
    LUXURY = "فاخر"


class RevenueSource(enum.Enum):
    """مصدر الإيراد"""
    PARTNERSHIP = "شراكة"
    GENERAL = "عام"
    TRAINING = "تدريب"
    SERVICES = "خدمات"
    CONSULTING = "استشارات"
    TRAINER_FEE = "وساطة مدرب"


class AssetCategory(enum.Enum):
    """تصنيف الأصل"""
    FURNITURE = "أثاث"
    DEVICES = "أجهزة"
    EQUIPMENT = "معدات"
    OTHER = "أخرى"


class AssetOwnership(enum.Enum):
    """ملكية الأصل"""
    OWNED = "مملوكة"
    BORROWED = "مستعارة"


class VoucherType(enum.Enum):
    """نوع السند"""
    RECEIPT = "قبض"
    DISBURSEMENT = "صرف"


class RegisterType(enum.Enum):
    """نوع السجل المالي"""
    CASH = "كاش"
    BANK = "مصرف"


class ContractStatus(enum.Enum):
    """حالة العقد"""
    PENDING = "قيد المراجعة"
    ACTIVE = "نشط"
    COMPLETED = "مكتمل"
    TERMINATED = "ملغى"


class PartnerType(enum.Enum):
    """تصنيف الشريك"""
    LOCAL = "محلي"
    INTERNATIONAL = "دولي"


class TransactionType(str, enum.Enum):
    """نوع الحركة المالية"""
    IN = "in"
    OUT = "out"

