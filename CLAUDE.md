# CLAUDE.md — سياق هندسة المشروع
# نظام إدارة مركز التدريب والخدمات اللوجستية (المنظومة)

> هذا الملف هو **المرجع الرئيسي** لكل قرار تقني في هذا المشروع.
> اقرأه بالكامل قبل أي إجراء. إذا تعارض هذا الملف مع أي تعليمات أخرى، هذا الملف يسود.

---

## 1. هوية المشروع وغرضه

**المنظومة** هو نظام ERP مكتبي متكامل (Desktop App) مصمم لإدارة مركز تدريب وخدمات لوجستية في ليبيا.
الجمهور المستهدف: مدير المركز، المدير المالي، موظفو الإدارة.
اللغة الأساسية للواجهة: **العربية (RTL)**، مع دعم حقول البيانات لأي لغة.
اللغة الأساسية للكود والتعليقات: **الإنجليزية**.

### 1.1 المبدأ الحاكم للمشروع
> **كل كيانين مرتبطين منطقيًا يجب أن يكونا مرتبطين تقنيًا عبر FK حقيقي، وتظهر هذه العلاقة كرابط تفاعلي في الواجهة.**

هذا ليس خيارًا بل شرطًا. أي نموذج بيانات جديد يُعرّف Enum أو FK — تأكد من ربطه بالنماذج المجاورة قبل إغلاق المهمة.

---

## 2. البنية التقنية القائمة

```
project_root/
├── CLAUDE.md                  ← هذا الملف (اقرأه أولاً)
├── main.py                    ← نقطة الدخول
├── core/
│   ├── database.py            ← SQLAlchemy engine + session factory
│   ├── migrate.py             ← تشغيل Alembic migrations
│   └── exporter.py            ← دوال التصدير (PDF, CSV, Word)
├── models/
│   ├── __init__.py
│   ├── employee.py
│   ├── client.py
│   ├── training_program.py
│   ├── trainee.py
│   ├── trainer.py
│   ├── project.py
│   ├── hall.py
│   └── partnership.py
├── services/
│   ├── hr_service.py
│   ├── client_service.py
│   ├── training_service.py
│   ├── finance_service.py
│   └── project_service.py
├── ui/
│   ├── main_window.py         ← النافذة الرئيسية + Dashboard
│   ├── button_utils.py        ← 7 أنماط أزرار حالية
│   ├── forms/
│   └── dialogs/
├── migrations/
│   ├── 0001_initial.py
│   ├── 0002_trainers.py
│   ├── 0003_projects.py
│   ├── 0004_proposal.py
│   └── [التالية تبدأ من 0005]
├── tests/
└── assets/
    └── logo.png
```

### 2.1 Stack التقني
- **Python 3.10+**
- **PyQt5** للواجهة — RTL مفعّل عبر `Qt.RightToLeft`
- **SQLAlchemy 1.4** ORM + **Alembic** للـ migrations
- **SQLite** (ملف محلي)
- **ReportLab** لتوليد PDF
- **python-docx** لتوليد Word
- **Pillow** لمعالجة صور المصروفات

### 2.2 قواعد الكود الإلزامية
1. **Services فقط تتكلم مع DB** — UI تستدعي services، لا تستدعي DB مباشرة أبدًا
2. **كل migration له رقم تسلسلي** ويتبع نمط Alembic الحالي في `core/migrate.py`
3. **لا تحذف column موجود** — استخدم `nullable=True` أو Soft Delete (`is_deleted = Column(Boolean, default=False)`)
4. **كل Enum يُعرَّف مرة واحدة** في `models/enums.py` ويُستورد منه في أي مكان آخر
5. **Arabic RTL**: أي Widget يعرض نصًا عربيًا يحمل `setLayoutDirection(Qt.RightToLeft)`
6. **لا تغيّر tests/ موجودة** — أضف tests جديدة إذا احتجت، لا تعدّل القديمة

---

## 3. الواجهة الرئيسية (Dashboard) — مهمة الأولوية

### 3.1 الهوية البصرية
```
Palette:
  background:  #0D1B2A  (كحلي داكن — خلفية رئيسية)
  card_bg:     #2A3A4A  (رمادي متوسط — خلفية البطاقات)
  accent:      #C9A96E  (ذهبي خافت — العناصر البارزة)
  text_primary: #F0EDE8 (أبيض مكسر — النصوص الرئيسية)
  text_muted:  #8A9BAB  (رمادي فاتح — النصوص الثانوية)
  alert_bg:    #3D1A1A  (أحمر داكن — بطاقات التنبيه)
  success:     #1A3D2A  (أخضر داكن — مؤشرات الإيجابية)

Typography:
  display_font: "Cairo" أو "Tajawal" (من assets/fonts/ إذا وُجد، وإلا system Arabic font)
  body_font:    نفس العائلة بأوزان مختلفة
  mono_font:    "Courier New" للأرقام المالية

Layout:
  الشاشة مقسمة 3 صفوف من Cards
  Row 1: 4 بطاقات كبيرة (الحالة المالية والتشغيلية الفورية)
  Row 2: 4 بطاقات تنبيهية (لون مختلف، قابلة للنقر)
  Row 3: 4 بطاقات إحصائية صغيرة
  شعار المركز (assets/logo.png) + اسم المركز في أعلى يمين
```

### 3.2 مؤشرات Dashboard

**Row 1 — الحالة الفورية (Card كبيرة مع رقم بارز):**
| المؤشر | الدالة |
|---|---|
| الرصيد النقدي (كاش) | `finance_service.get_cash_balance()` |
| الرصيد المصرفي | `finance_service.get_bank_balance()` |
| المشاريع النشطة | `project_service.count_active()` |
| الدورات الجارية | `training_service.count_active_courses()` |

**Row 2 — التنبيهات (Card بخلفية alert_bg، قابلة للنقر — تفتح الشاشة المرتبطة):**
| المؤشر | الشرط | الوجهة عند النقر |
|---|---|---|
| عقود تنتهي خلال 30 يومًا | `contract_end_date <= today+30` | HR → فلتر العقود المنتهية |
| دورات اقتربت من الحد الأدنى | `enrolled == min_trainees` | Training → الدورة |
| دورات تجاوزت الحد الأعلى | `enrolled > max_trainees` | Training → الدورة |
| عروض بانتظار الاعتماد | `proposal_status == PENDING` | Finance → العروض |

**Row 3 — إحصاءات عامة (Card صغيرة):**
| الموظفون | المدربون النشطون | متدربو الشهر | إجمالي العملاء |

### 3.3 قواعد التحديث
- Dashboard يُحدَّث عند كل فتح للتطبيق
- زر "تحديث" يدوي في أعلى الشاشة
- كل Card تعرض وقت آخر تحديث (timestamp صغير أسفل القيمة)

---

## 4. نماذج البيانات الجديدة

### 4.1 models/enums.py — الملف المركزي لكل Enums

```python
from enum import Enum

class ClientType(Enum):
    INDIVIDUAL   = "فرد"
    INSTITUTION  = "مؤسسة"
    PARTNERSHIP  = "شراكة"

class PaymentMethod(Enum):
    CASH = "كاش"
    BANK = "تحويل مصرفي"

class EmploymentType(Enum):
    PERMANENT  = "دائم"
    TEMPORARY  = "غير دائم"

class CourseCategory(Enum):
    INDEPENDENT = "مستقلة"
    PARTNERSHIP = "شراكة"
    CSR         = "مسؤولية اجتماعية"
    PROJECT     = "تدريبات مشاريع"

class TrainerPayType(Enum):
    FIXED_COURSE   = "مبلغ ثابت للدورة"
    PER_TRAINEE    = "قيمة لكل متدرب"

class ServiceType(Enum):
    TRAINING      = "تدريب"
    CONSULTING    = "استشارة"
    HALL_RENT     = "إيجار قاعة"
    ACCOMMODATION = "إيجار سكن"
    OTHER         = "خدمات أخرى"

class SpecCategory(Enum):
    PROFESSIONAL     = "مهنية"
    HR_TRAINING      = "موارد بشرية"
    TECHNICAL        = "تقنية"
    ENTREPRENEURSHIP = "ريادة أعمال"
    AWARENESS        = "محاضرات وتوعية"

class SectorType(Enum):
    GOVERNMENT = "حكومية"
    PRIVATE    = "خاصة"

class ProposalStatus(Enum):
    PENDING  = "قيد الانتظار"
    APPROVED = "معتمد"
    REJECTED = "مرفوض"

class CateringMeal(Enum):
    BREAKFAST = "فطور"
    LUNCH     = "غداء"
    DINNER    = "عشاء"
    COFFEE    = "استراحة قهوة"

class CateringLevel(Enum):
    BASIC   = "عادي"
    SPECIAL = "خاص"
    LUXURY  = "فاخر"

class RevenueSource(Enum):
    PARTNERSHIP  = "شراكة"
    GENERAL      = "عام"
    TRAINING     = "تدريب"
    SERVICES     = "خدمات"
    CONSULTING   = "استشارات"
    TRAINER_FEE  = "وساطة مدرب"

class AssetCategory(Enum):
    FURNITURE  = "أثاث"
    DEVICES    = "أجهزة"
    EQUIPMENT  = "معدات"
    OTHER      = "أخرى"

class AssetOwnership(Enum):
    OWNED    = "مملوكة"
    BORROWED = "مستعارة"

class VoucherType(Enum):
    RECEIPT      = "قبض"
    DISBURSEMENT = "صرف"

class RegisterType(Enum):
    CASH = "كاش"
    BANK = "مصرف"
```

### 4.2 التوسعة على Employee (migration 0005)
يُضاف لملف `models/employee.py` الحالي — لا تحذف أي column موجود:

```python
# الحقول الجديدة فقط
contract_start_date  = Column(Date, nullable=True)
contract_end_date    = Column(Date, nullable=True)
daily_wage_rate      = Column(Numeric(10,2), nullable=True)
employment_type      = Column(Enum(EmploymentType), default=EmploymentType.PERMANENT, nullable=True)
payment_method       = Column(Enum(PaymentMethod), nullable=True)
current_project_id   = Column(Integer, ForeignKey('projects.id'), nullable=True)
# Soft delete
is_deleted           = Column(Boolean, default=False, nullable=False)
```

### 4.3 إعادة بناء Client (migration 0005)

```python
class Client(Base):
    __tablename__ = 'clients'
    id              = Column(Integer, primary_key=True)
    created_at      = Column(DateTime, default=func.now())
    updated_at      = Column(DateTime, onupdate=func.now())
    is_deleted      = Column(Boolean, default=False)

    # حقول مشتركة
    client_type     = Column(Enum(ClientType), nullable=False)
    name            = Column(String(200), nullable=False)
    email           = Column(String(200), nullable=True)
    phone           = Column(String(50), nullable=True)
    address         = Column(Text, nullable=True)
    payment_method  = Column(Enum(PaymentMethod), nullable=True)
    partnership_status = Column(String(20), nullable=True)     # "قائم" / "منقضٍ"

    # حقول المؤسسات فقط (nullable للأفراد)
    sector          = Column(Enum(SectorType), nullable=True)
    project_name    = Column(String(300), nullable=True)
    project_summary = Column(Text, nullable=True)
    contract_value  = Column(Numeric(15,2), nullable=True)
    roles_distribution = Column(Text, nullable=True)           # نص حر متعدد الأسطر

    # الشراكة كمرجع فقط
    partnership_id  = Column(Integer, ForeignKey('partnerships.id'), nullable=True)
```

### 4.4 التوسعة على TrainingProgram (migration 0006)
يُضاف لـ `models/training_program.py`:

```python
# إضافة حقول جديدة
course_category     = Column(Enum(CourseCategory), nullable=True)
hall_id             = Column(Integer, ForeignKey('halls.id'), nullable=True)
min_trainees        = Column(Integer, nullable=True)
max_trainees        = Column(Integer, nullable=True)
fee_per_trainee     = Column(Numeric(10,2), nullable=True)
trainer_pay_type    = Column(Enum(TrainerPayType), nullable=True)
trainer_pay_value   = Column(Numeric(10,2), nullable=True)
project_id          = Column(Integer, ForeignKey('projects.id'), nullable=True)
# project_id مطلوب (NOT NULL logically) عندما course_category == PROJECT — تُفرض في Service لا في DB
```

```python
# جدول جديد: models/course_enrollment.py
class CourseEnrollment(Base):
    __tablename__ = 'course_enrollments'
    id              = Column(Integer, primary_key=True)
    course_id       = Column(Integer, ForeignKey('training_programs.id'), nullable=False)
    trainee_id      = Column(Integer, ForeignKey('trainees.id'), nullable=False)
    enrollment_status = Column(String(20), default='مبدئي')   # مبدئي / نهائي
    payment_method  = Column(Enum(PaymentMethod), nullable=True)
    amount_paid     = Column(Numeric(10,2), nullable=True)
    refund_requested = Column(Boolean, default=False)
    refund_amount   = Column(Numeric(10,2), nullable=True)
    refund_date     = Column(Date, nullable=True)
    created_at      = Column(DateTime, default=func.now())
```

### 4.5 نماذج المالية (migration 0007)

```python
# models/financial_proposal.py
class FinancialProposal(Base):
    __tablename__ = 'financial_proposals'
    id              = Column(Integer, primary_key=True)
    proposal_number = Column(String(50), unique=True)          # توليد تلقائي: PRO-YYYY-NNNN
    client_id       = Column(Integer, ForeignKey('clients.id'))
    service_type    = Column(Enum(ServiceType))
    status          = Column(Enum(ProposalStatus), default=ProposalStatus.PENDING)
    approved_by     = Column(String(100), nullable=True)
    approved_at     = Column(DateTime, nullable=True)
    total_value     = Column(Numeric(15,2))
    notes           = Column(Text, nullable=True)
    created_at      = Column(DateTime, default=func.now())
    line_items      = relationship('ServiceLineItem', back_populates='proposal', cascade='all, delete-orphan')
    client          = relationship('Client')

# models/service_line_item.py
class ServiceLineItem(Base):
    __tablename__ = 'service_line_items'
    id              = Column(Integer, primary_key=True)
    proposal_id     = Column(Integer, ForeignKey('financial_proposals.id'), nullable=True)
    invoice_id      = Column(Integer, ForeignKey('invoices.id'), nullable=True)
    service_type    = Column(Enum(ServiceType))
    unit_description = Column(String(100))                     # متدرب / يوم / شخص / قطعة
    quantity        = Column(Numeric(10,2))
    unit_price      = Column(Numeric(10,2))
    currency        = Column(String(10), default='LYD')
    discount        = Column(Numeric(10,2), default=0)
    total           = Column(Numeric(10,2))                    # quantity * unit_price - discount
    notes           = Column(Text, nullable=True)
    proposal        = relationship('FinancialProposal', back_populates='line_items')

# models/voucher.py
class Voucher(Base):
    __tablename__ = 'vouchers'
    id              = Column(Integer, primary_key=True)
    voucher_type    = Column(Enum(VoucherType), nullable=False)
    voucher_number  = Column(String(50), unique=True)
    party_name      = Column(String(200))
    amount          = Column(Numeric(15,2))
    amount_in_words = Column(String(500))                      # يُولَّد تلقائيًا بالعربية
    payment_method  = Column(Enum(PaymentMethod))
    revenue_source  = Column(Enum(RevenueSource), nullable=True)
    project_id      = Column(Integer, ForeignKey('projects.id'), nullable=True)
    notes           = Column(Text, nullable=True)
    created_at      = Column(DateTime, default=func.now())

# models/expense.py
class Expense(Base):
    __tablename__ = 'expenses'
    id              = Column(Integer, primary_key=True)
    name            = Column(String(200))
    quantity        = Column(Numeric(10,2))
    unit            = Column(String(50))                       # قطعة / صندوق / أخرى
    unit_price      = Column(Numeric(10,2))
    total           = Column(Numeric(10,2))                    # محسوب
    notes           = Column(Text, nullable=True)
    invoice_image_path = Column(String(500), nullable=True)
    project_id      = Column(Integer, ForeignKey('projects.id'), nullable=True)
    payment_method  = Column(Enum(PaymentMethod), nullable=True)
    created_at      = Column(DateTime, default=func.now())

# models/asset.py
class Asset(Base):
    __tablename__ = 'assets'
    id              = Column(Integer, primary_key=True)
    name            = Column(String(200))
    category        = Column(Enum(AssetCategory))
    acquisition_date = Column(Date)
    depreciation_months = Column(Integer, nullable=True)
    ownership       = Column(Enum(AssetOwnership), default=AssetOwnership.OWNED)
    lender_name     = Column(String(200), nullable=True)       # عند الاستعارة
    notes           = Column(Text, nullable=True)

# models/cash_register.py
class CashRegister(Base):
    __tablename__ = 'cash_register'
    id              = Column(Integer, primary_key=True)
    register_type   = Column(Enum(RegisterType), nullable=False)
    transaction_type = Column(String(5))                       # 'in' أو 'out'
    amount          = Column(Numeric(15,2))
    description     = Column(String(500))
    related_voucher_id = Column(Integer, ForeignKey('vouchers.id'), nullable=True)
    balance_after   = Column(Numeric(15,2))                    # رصيد تراكمي بعد الحركة
    created_at      = Column(DateTime, default=func.now())
```

### 4.6 نماذج الخدمات الجانبية (migration 0008)

```python
# models/consultant.py
class Consultant(Base):
    __tablename__ = 'consultants'
    id              = Column(Integer, primary_key=True)
    name            = Column(String(200))
    email           = Column(String(200), nullable=True)
    phone           = Column(String(50), nullable=True)
    address         = Column(Text, nullable=True)
    specialization  = Column(Enum(SpecCategory))
    service_detail  = Column(Text, nullable=True)
    contract_start  = Column(Date, nullable=True)
    contract_end    = Column(Date, nullable=True)
    gross_value     = Column(Numeric(10,2), nullable=True)     # يظهر للعميل
    center_share    = Column(Numeric(10,2), nullable=True)     # داخلي فقط
    consultant_share = Column(Numeric(10,2), nullable=True)    # داخلي فقط
    payment_method  = Column(Enum(PaymentMethod), nullable=True)
    is_deleted      = Column(Boolean, default=False)

# models/catering.py
class CateringOrder(Base):
    __tablename__ = 'catering_orders'
    id              = Column(Integer, primary_key=True)
    proposal_id     = Column(Integer, ForeignKey('financial_proposals.id'), nullable=True)
    meal_type       = Column(Enum(CateringMeal))
    service_level   = Column(Enum(CateringLevel))
    pricing_mode    = Column(String(20))                       # 'per_person' أو 'per_day'
    num_persons     = Column(Integer, nullable=True)
    num_days        = Column(Integer, nullable=True)
    unit_price      = Column(Numeric(10,2))
    details         = Column(Text, nullable=True)
    created_at      = Column(DateTime, default=func.now())
    extra_services  = relationship('CateringExtra', back_populates='order', cascade='all, delete-orphan')

class CateringExtra(Base):
    __tablename__ = 'catering_extras'
    id          = Column(Integer, primary_key=True)
    order_id    = Column(Integer, ForeignKey('catering_orders.id'))
    service_name = Column(String(200))
    price       = Column(Numeric(10,2))
    order       = relationship('CateringOrder', back_populates='extra_services')

# models/accommodation.py
class AccommodationBooking(Base):
    __tablename__ = 'accommodation_bookings'
    id              = Column(Integer, primary_key=True)
    proposal_id     = Column(Integer, ForeignKey('financial_proposals.id'), nullable=True)
    apartment_type  = Column(String(5))                        # 'A' أو 'B'
    check_in_date   = Column(Date)
    check_out_date  = Column(Date)
    # num_days = (check_out - check_in).days — يُحسب في Service
    extra_services  = relationship('AccommodationExtra', back_populates='booking', cascade='all, delete-orphan')

class AccommodationExtra(Base):
    __tablename__ = 'accommodation_extras'
    id          = Column(Integer, primary_key=True)
    booking_id  = Column(Integer, ForeignKey('accommodation_bookings.id'))
    service_name = Column(String(200))
    price       = Column(Numeric(10,2))
    booking     = relationship('AccommodationBooking', back_populates='extra_services')

# models/market_research.py
class MarketResearch(Base):
    __tablename__ = 'market_research'
    id                  = Column(Integer, primary_key=True)
    collection_method   = Column(String(20))                   # 'field' أو 'online'
    collection_type     = Column(String(200))                  # نص حر
    min_samples         = Column(Integer)
    min_price           = Column(Numeric(10,2))
    max_samples         = Column(Integer)
    max_price           = Column(Numeric(10,2))
    created_at          = Column(DateTime, default=func.now())

# models/contract_template.py
class ContractTemplate(Base):
    __tablename__ = 'contract_templates'
    id              = Column(Integer, primary_key=True)
    template_name   = Column(String(200))                      # "موظف دائم" / "مدرب" / "مستشار"
    template_type   = Column(String(50))                       # 'employee' / 'trainer' / 'consultant'
    body_text       = Column(Text)                             # نص العقد مع متغيرات {name} {date} إلخ
    is_active       = Column(Boolean, default=True)
    updated_at      = Column(DateTime, onupdate=func.now())
```

---

## 5. منطق الأعمال الحرج

### 5.1 دورة العرض المالي → فاتورة → سندات

```
FinancialProposal (status=PENDING)
    ↓ [زر "اعتماد مدير مالي" — يظهر للمدير المالي فقط]
    ↓ تُنفَّذ هذه الخطوات في finance_service.approve_proposal():
    1. proposal.status = APPROVED
    2. proposal.approved_at = datetime.now()
    3. إنشاء Invoice مرتبط (نفس client, line_items, total_value)
    4. إنشاء CashRegister entry (register_type=BANK أو CASH حسب payment_method, transaction_type='in')
    5. تحديث project.budget_actual إن كانت الفاتورة مرتبطة بمشروع
    ↓
Invoice (نهائية)
    ↓ من داخل الفاتورة يمكن إنشاء:
    - Voucher(type=RECEIPT)      → صياغة PDF: "استلمنا من: [party_name] مبلغ [amount] ..."
    - Voucher(type=DISBURSEMENT) → صياغة PDF: "سلّمنا إلى: [party_name] مبلغ [amount] ..."
```

### 5.2 تحميل رواتب الموظفين على ميزانية المشروع

```python
# services/finance_service.py
def charge_employee_to_project(employee_id: int, project_id: int, work_days: int) -> Decimal:
    employee = session.get(Employee, employee_id)
    project  = session.get(Project, project_id)
    
    if not employee.daily_wage_rate:
        raise ValueError(f"لم يُحدَّد معدل الأجر اليومي للموظف {employee.name}")
    if employee.current_project_id != project_id:
        raise ValueError("الموظف غير مُسنَد لهذا المشروع")
    
    cost = employee.daily_wage_rate * work_days
    
    # خصم من ميزانية المشروع
    project.budget_spent = (project.budget_spent or 0) + cost
    
    # تسجيل كمصروف مرتبط بالمشروع
    expense = Expense(
        name=f"راتب {employee.name} — {work_days} يوم",
        quantity=work_days,
        unit="يوم",
        unit_price=employee.daily_wage_rate,
        total=cost,
        project_id=project_id
    )
    session.add(expense)
    session.commit()
    return cost
```

### 5.3 قيمة الشريك خارج الميزانية الرئيسية

```python
# services/project_service.py
def get_center_net_budget(project_id: int) -> Decimal:
    """الميزانية التي تعود للمركز فعلاً، بعد استثناء حصة الشريك"""
    project = session.get(Project, project_id)
    return (project.total_budget or 0) - (project.partner_share_value or 0)
```

### 5.4 إعادة استخدام بيانات المتدربين

```python
# services/training_service.py
def search_existing_trainees(partial_name: str) -> list[Trainee]:
    """يُستدعى أثناء كتابة اسم متدرب جديد — يرجع المطابقات الجزئية"""
    return session.query(Trainee).filter(
        Trainee.name.ilike(f"%{partial_name}%"),
        Trainee.is_deleted == False
    ).limit(10).all()

def enroll_trainee(course_id: int, trainee_id: int | None, trainee_data: dict | None) -> CourseEnrollment:
    """
    إذا trainee_id → استخدم متدربًا موجودًا
    إذا trainee_data → أنشئ متدربًا جديدًا ثم سجّله
    """
    if trainee_id:
        trainee = session.get(Trainee, trainee_id)
    else:
        trainee = Trainee(**trainee_data)
        session.add(trainee)
        session.flush()  # للحصول على ID قبل commit
    
    enrollment = CourseEnrollment(course_id=course_id, trainee_id=trainee.id)
    session.add(enrollment)
    session.commit()
    return enrollment
```

### 5.5 تنبيهات Dashboard

```python
# services/hr_service.py
def get_expiring_contracts(days_ahead: int = 30) -> list[Employee]:
    threshold = date.today() + timedelta(days=days_ahead)
    return session.query(Employee).filter(
        Employee.contract_end_date.isnot(None),
        Employee.contract_end_date <= threshold,
        Employee.contract_end_date >= date.today(),
        Employee.is_deleted == False
    ).all()

# services/training_service.py
def get_courses_at_min_capacity() -> list[TrainingProgram]:
    # يستخدم subquery لحساب enrolled count
    enrolled_count = session.query(func.count(CourseEnrollment.id)).filter(
        CourseEnrollment.course_id == TrainingProgram.id
    ).correlate(TrainingProgram).scalar_subquery()
    return session.query(TrainingProgram).filter(
        TrainingProgram.min_trainees.isnot(None),
        enrolled_count >= TrainingProgram.min_trainees
    ).all()
```

### 5.6 توليد المبلغ بالحروف العربية
```python
# core/arabic_number.py — ملف جديد
def amount_to_arabic_words(amount: Decimal, currency: str = 'دينار ليبي') -> str:
    """يحوّل 1250.500 إلى 'ألف ومئتان وخمسون دينارًا ليبيًا وخمسمئة درهم'"""
    # استخدم مكتبة num2words مع locale='ar' أو نفّذ يدويًا للعربية الليبية
    ...
```

---

## 6. المستندات المطبوعة

### 6.1 القواعد العامة
- **كل مستند: زر "معاينة" منفصل عن زر "طباعة"** — المعاينة لا تؤدي للطباعة تلقائيًا
- كل PDF يحمل في الأعلى: `assets/logo.png` + اسم المركز + رقم مرجعي + تاريخ الإصدار
- كل مبلغ مالي يُكتب بالأرقام **والحروف** (Arabic words)
- أرقام مرجعية تسلسلية لكل نوع مستند مستقلة

### 6.2 قائمة المستندات المطلوبة

| المستند | المصدر | الدالة |
|---|---|---|
| عرض السعر (مبدئي) | FinancialProposal | `export_proposal_pdf(proposal_id)` |
| الفاتورة النهائية | Invoice | `export_invoice_pdf(invoice_id)` |
| سند قبض | Voucher(RECEIPT) | `export_receipt_voucher_pdf(voucher_id)` |
| سند صرف | Voucher(DISBURSEMENT) | `export_disbursement_voucher_pdf(voucher_id)` |
| عقد (موظف/مدرب/مستشار) | ContractTemplate + بيانات | `export_contract_pdf(template_id, person_data)` |
| ورقة قبول متدرب | CourseEnrollment | `export_trainee_acceptance_pdf(enrollment_id)` |
| تقرير مالي شامل | كل وحدات المالية | `export_comprehensive_financial_pdf(period)` |
| ملف تحليل AI | كل وحدات المالية | `export_ai_analysis_json(period)` |
| بطاقة تواصل المركز | إعدادات النظام | `export_contact_card_pdf()` |

### 6.3 محتوى عرض السعر (FinancialProposal PDF)
```
[شعار المركز]          [تاريخ]   [رقم العرض]
─────────────────────────────────────────────
عرض سعر مقدَّم إلى: [اسم العميل / المؤسسة]
بيان الخدمة: [service_type]

┌────────────────┬──────┬──────────┬──────────┬──────────┐
│ الخدمة        │ الوحدة│ الكمية   │ السعر   │ الإجمالي │
├────────────────┼──────┼──────────┼──────────┼──────────┤
│ [line_item 1] │ يوم  │ 5        │ 500 LYD │ 2500 LYD │
│ ...           │      │          │          │          │
└────────────────┴──────┴──────────┴──────────┴──────────┘
                            الإجمالي: [total_value] LYD
                  المبلغ بالحروف: [amount_in_words]

ملاحظات: [notes]
─────────────────────────────────────────────
        اعتماد المدير المالي
توقيع: ___________________    تاريخ: ________
```

**آلية الاعتماد**: زر "اعتماد" في شاشة العروض يُغيّر status → APPROVED ويضع ختمًا "معتمد" (نص بارز باللون الأخضر) على PDF عند إعادة الطباعة.

### 6.4 محتوى سند القبض
```
سند قبض رقم: [voucher_number]        التاريخ: [date]
استلمنا من السيد/الجهة: [party_name]
مبلغ وقدره: [amount_in_words]
ما يعادل رقمًا: [amount] [currency]
وذلك مقابل: [description]
طريقة الدفع: [payment_method]
توقيع المستلم: _______________
```

### 6.5 محتوى العقد
العقد يُولَّد من `ContractTemplate.body_text` بعد استبدال المتغيرات:
```
المتغيرات المدعومة:
{name}, {id_number}, {phone}, {email}, {address},
{contract_start}, {contract_end},
{daily_rate}, {monthly_rate}, {hourly_rate},
{project_name}, {responsibilities},
{center_name}, {today_date}
```
في أسفل كل عقد: توقيع الطرف الأول (ممثل المركز) + توقيع الطرف الثاني.
ملاحظة: القوالب النصية للبنود القانونية تُدخَل يدويًا من المستخدم أو بمساعدة محامٍ.

---

## 7. التقارير

### 7.1 تقارير المالية (finance_service.py)
```python
def generate_monthly_report(year: int, month: int) -> dict:
    """
    يرجع:
    - revenues: مجموع الإيرادات مقسّمة حسب RevenueSource
    - expenses: مجموع المصروفات مقسّمة حسب project_id / عامة
    - net_profit: revenues.total - expenses.total
    - cash_balance: رصيد الكاش في نهاية الفترة
    - bank_balance: رصيد المصرف في نهاية الفترة
    - active_projects: عدد ومبالغ المشاريع النشطة
    """

def generate_quarterly_report(year: int, quarter: int) -> dict:
    """نفس المنطق لـ 3 أشهر مع مقارنة بالربع السابق"""

def generate_comprehensive_report(period: str = 'ytd') -> dict:
    """period: 'last_month' | 'last_quarter' | 'ytd' | 'all_time'"""
```

### 7.2 تقارير المشاريع
```python
# models/project_report.py
class ProjectReport(Base):
    __tablename__ = 'project_reports'
    id              = Column(Integer, primary_key=True)
    project_id      = Column(Integer, ForeignKey('projects.id'))
    report_type     = Column(String(20))                       # 'technical' أو 'financial'
    period_type     = Column(String(20))                       # 'monthly' / 'milestone' / 'final'
    period_label    = Column(String(100))                      # "مارس 2025" أو "المرحلة الأولى"
    file_path       = Column(String(500))                      # مسار الملف المرفوع
    file_format     = Column(String(20))                       # 'pdf' / 'docx' / 'other'
    uploaded_at     = Column(DateTime, default=func.now())
    notes           = Column(Text, nullable=True)
```

### 7.3 ملف التحليل بالذكاء الاصطناعي
```python
# core/exporter.py
def export_ai_analysis_json(period: str = 'last_month') -> str:
    """
    يُنتج ملف JSON منظم في مجلد exports/:
    {
      "export_date": "...",
      "period": "...",
      "revenues": {"by_source": {...}, "total": ...},
      "expenses": {"by_project": {...}, "general": {...}, "total": ...},
      "net": ...,
      "projects": [{"name": ..., "budget": ..., "spent": ..., "remaining": ...}],
      "trainings": {"courses_count": ..., "trainees_count": ..., "revenue": ...},
      "contracts": {"active": ..., "expiring_soon": ..., "expired_last_month": ...},
      "assets": {"count": ..., "categories": {...}}
    }
    """
```

---

## 8. جدولة القاعات (Hall Scheduler)

شاشة القاعة (`ui/forms/hall_form.py`) تتضمن:
- **معلومات القاعة**: الاسم، الطاقة الاستيعابية، سعر الإيجار اليومي/الساعي
- **جدول بصري أسبوعي**: Grid يعرض أيام الأسبوع × ساعات اليوم
  - الخلايا المشغولة (مرتبطة بدورة) → لون داكن مع اسم الدورة
  - الخلايا الفارغة (متاحة) → لون فاتح
- النقر على خلية مشغولة → فتح صفحة الدورة المرتبطة
- البيانات: `session.query(TrainingProgram).filter(TrainingProgram.hall_id == hall.id)`

---

## 9. الأزرار — button_utils.py

الأنماط الـ7 الحالية تبقى كما هي. يُضاف نمط ثامن:
```python
# نمط رقم 8: زر الحذف التأكيدي
BUTTON_DANGER_CONFIRM = {
    "background": "#8B1A1A",    # أحمر داكن
    "color": "#FFFFFF",
    "border": "2px solid #CC3333",
    "hover_background": "#CC3333",
    "font_weight": "bold",
    "min_width": "120px"
}
# يستخدم مع QMessageBox تأكيد من نوع Warning قبل تنفيذ أي حذف
```

---

## 10. الحقول الجديدة للمشاريع (migration 0009)

يُضاف لـ `models/project.py`:
```python
project_number      = Column(String(50), unique=True, nullable=True)
geographic_scope    = Column(String(200), nullable=True)
partner_name        = Column(String(200), nullable=True)
donor_name          = Column(String(200), nullable=True)
total_budget        = Column(Numeric(15,2), nullable=True)
currency            = Column(String(10), default='LYD')
partner_share_value = Column(Numeric(15,2), nullable=True)    # لا يدخل الميزانية الرئيسية
budget_spent        = Column(Numeric(15,2), default=0)
# budget_remaining يُحسب: total_budget - partner_share_value - budget_spent
project_details     = Column(Text, nullable=True)
attachment_folder   = Column(String(500), nullable=True)      # مسار مجلد المرفقات
is_deleted          = Column(Boolean, default=False)
```

---

## 11. أسئلة معلّقة — لا تفترض، اسأل

قبل تنفيذ أي من هذه النقاط، اعرضها على المستخدم واحتفظ بإجاباته في هذا الملف:

**Q1 — الضريبة**: هل تُحذف من رسوم الدورات فقط، أم من كل النظام بما فيه الفواتير؟
**Q2 — التسوية النقدية**: هل تريد تتبع سعر الصرف (دينار مصرفي vs. سوق موازٍ) داخل النظام؟
**Q3 — عميل "فرد"**: هل يحمل حقل "القطاع: حكومية/خاصة"؟
**Q4 — ترقيم العقود**: ترقيم مستقل لكل نوع (موظف/مدرب/مستشار) أم ترقيم موحد؟
**Q5 — صلاحيات المستخدمين**: هل يستخدم النظام شخص واحد أم أكثر؟ هل تحتاج roles (Admin / مدير مالي / موظف)؟

---

## 12. ترتيب تنفيذ المهام (Phases)

**القاعدة الذهبية**: لا تنتقل لمرحلة قبل اجتياز `pytest tests/` للمرحلة السابقة.

| المرحلة | المهام | Migrations |
|---|---|---|
| **A — الأساسيات** | enums.py، Employee extensions، Client rebuild، Dashboard cards | 0005 |
| **B — التدريب** | CourseEnrollment، Training extensions، Hall scheduler | 0006 |
| **C — الخدمات** | Consultant، Catering، Accommodation، MarketResearch | 0007 |
| **D — المالية** | FinancialProposal، ServiceLineItem، Voucher، Expense، Asset، CashRegister | 0008 |
| **E — المشاريع والعقود** | Project extensions، ContractTemplate، ProjectReport، exporter updates | 0009 |

---

## 13. ملاحظات ختامية

- **الـ README الحالي يُحدَّث** في نهاية كل مرحلة ليعكس الوضع الجديد
- **لا تُنشئ ملفات مؤقتة** في جذر المشروع — استخدم `temp/` أو `.gitignore` المناسب
- **كل دالة service تُوثَّق** بـ docstring عربي يصف المدخلات والمخرجات والأخطاء المحتملة
- عند اكتشاف تعارض بين هذا الملف وكود موجود: **هذا الملف يُعدَّل ليعكس الواقع**، لا يُعدَّل الكود ليطابق الملف دون تقييم
