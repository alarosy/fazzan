"""
Logistics Form — شاشة الخدمات اللوجستية المجمعة.
تجمع تبويبات الاستشارات، التموين والإعاشة، السكن والإقامة، ودراسات السوق.
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QDialog,
    QFormLayout, QTextEdit, QFrame, QAbstractItemView, QComboBox,
    QSpinBox, QDoubleSpinBox, QDateEdit, QTabWidget, QMessageBox
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont, QColor

from ui.styles import COLORS, FONTS, FONT_SIZES, SPACING
from ui.button_utils import (
    create_button, create_danger_button, confirm_delete,
    BUTTON_PRIMARY, BUTTON_SECONDARY, BUTTON_GHOST
)

import services.consultant_service as consultant_svc
import services.catering_service as catering_svc
import services.accommodation_service as accommodation_svc
import services.market_research_service as research_svc

from models.enums import SpecCategory, PaymentMethod, CateringMeal, CateringLevel


# ─── 1. Consultant Dialog & Tab ──────────────────────────────────────────────

class ConsultantDialog(QDialog):
    def __init__(self, consultant=None, parent=None):
        super().__init__(parent)
        self.consultant = consultant
        self.result_data = None
        self.setWindowTitle("تعديل مستشار" if consultant else "إضافة مستشار جديد")
        self.setMinimumWidth(500)
        self.setLayoutDirection(Qt.RightToLeft)
        self.setStyleSheet(f"QDialog {{ background-color: {COLORS['background']}; color: {COLORS['text_primary']}; }}")
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(SPACING["md"])
        
        title = QLabel(self.windowTitle())
        title.setFont(QFont(FONTS["display"].split(",")[0], FONT_SIZES["h2"], QFont.Bold))
        title.setStyleSheet(f"color: {COLORS['accent']};")
        layout.addWidget(title)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)
        
        self.name_input = QLineEdit()
        form.addRow("الاسم الكامل *:", self.name_input)
        
        self.phone_input = QLineEdit()
        form.addRow("الهاتف:", self.phone_input)
        
        self.email_input = QLineEdit()
        form.addRow("البريد الإلكتروني:", self.email_input)
        
        self.spec_combo = QComboBox()
        for spec in SpecCategory:
            self.spec_combo.addItem(spec.value, spec)
        form.addRow("التخصص الاستشاري:", self.spec_combo)
        
        self.detail_input = QTextEdit()
        self.detail_input.setMaximumHeight(60)
        form.addRow("تفاصيل الخدمة:", self.detail_input)

        # Dates
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate())
        self.start_date.setDisplayFormat("yyyy-MM-dd")
        form.addRow("تاريخ بدء العقد:", self.start_date)

        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate().addMonths(6))
        self.end_date.setDisplayFormat("yyyy-MM-dd")
        form.addRow("تاريخ انتهاء العقد:", self.end_date)

        # Money
        self.gross_input = QDoubleSpinBox()
        self.gross_input.setRange(0, 9999999)
        self.gross_input.setSuffix(" LYD")
        form.addRow("إجمالي قيمة العقد (للعميل):", self.gross_input)

        self.center_input = QDoubleSpinBox()
        self.center_input.setRange(0, 9999999)
        self.center_input.setSuffix(" LYD")
        form.addRow("حصة المركز المالية:", self.center_input)

        self.consultant_input = QDoubleSpinBox()
        self.consultant_input.setRange(0, 9999999)
        self.consultant_input.setSuffix(" LYD")
        form.addRow("حصة المستشار المالية:", self.consultant_input)

        self.pay_combo = QComboBox()
        for pm in PaymentMethod:
            self.pay_combo.addItem(pm.value, pm)
        form.addRow("طريقة الدفع:", self.pay_combo)

        self.address_input = QTextEdit()
        self.address_input.setMaximumHeight(50)
        form.addRow("العنوان:", self.address_input)

        layout.addLayout(form)

        if self.consultant:
            self._prefill()

        # Buttons
        btn_layout = QHBoxLayout()
        cancel_btn = create_button("إلغاء", BUTTON_GHOST)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        btn_layout.addStretch()
        save_btn = create_button("حفظ", BUTTON_PRIMARY)
        save_btn.clicked.connect(self._save)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)

    def _prefill(self):
        c = self.consultant
        self.name_input.setText(c.name or "")
        self.phone_input.setText(c.phone or "")
        self.email_input.setText(c.email or "")
        self.detail_input.setPlainText(c.service_detail or "")
        self.address_input.setPlainText(c.address or "")
        if c.gross_value: self.gross_input.setValue(float(c.gross_value))
        if c.center_share: self.center_input.setValue(float(c.center_share))
        if c.consultant_share: self.consultant_input.setValue(float(c.consultant_share))
        
        if c.contract_start: self.start_date.setDate(QDate(c.contract_start.year, c.contract_start.month, c.contract_start.day))
        if c.contract_end: self.end_date.setDate(QDate(c.contract_end.year, c.contract_end.month, c.contract_end.day))

        for idx in range(self.spec_combo.count()):
            if self.spec_combo.itemData(idx) == c.specialization:
                self.spec_combo.setCurrentIndex(idx)
                break
        
        for idx in range(self.pay_combo.count()):
            if self.pay_combo.itemData(idx) == c.payment_method:
                self.pay_combo.setCurrentIndex(idx)
                break

    def _save(self):
        name = self.name_input.text().strip()
        if not name:
            self.name_input.setFocus()
            return
        
        self.result_data = {
            "name": name,
            "phone": self.phone_input.text().strip() or None,
            "email": self.email_input.text().strip() or None,
            "specialization": self.spec_combo.currentData(),
            "service_detail": self.detail_input.toPlainText().strip() or None,
            "contract_start": self.start_date.date().toPyDate(),
            "contract_end": self.end_date.date().toPyDate(),
            "gross_value": self.gross_input.value() if self.gross_input.value() > 0 else None,
            "center_share": self.center_input.value() if self.center_input.value() > 0 else None,
            "consultant_share": self.consultant_input.value() if self.consultant_input.value() > 0 else None,
            "payment_method": self.pay_combo.currentData(),
            "address": self.address_input.toPlainText().strip() or None,
        }
        self.accept()


# ─── 2. Extras Sub-Table Manager (لإدارة الخدمات الفرعية للتموين والسكن) ───

class ExtrasTableWidget(QWidget):
    """جدول فرعي لإدارة الخدمات والأسعار الإضافية داخل نوافذ الإدخال."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayoutDirection(Qt.RightToLeft)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        hdr = QHBoxLayout()
        hdr.addWidget(QLabel("الخدمات الإضافية المرفقة:"))
        hdr.addStretch()
        add_btn = create_button("➕ خدمة إضافية", BUTTON_SECONDARY)
        add_btn.clicked.connect(self._add_row)
        hdr.addWidget(add_btn)
        layout.addLayout(hdr)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["البيان / الخدمة", "التكلفة", "إلغاء"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
        self.table.setColumnWidth(2, 60)
        self.table.setFixedHeight(120)
        layout.addWidget(self.table)

    def _add_row(self):
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        name_item = QLineEdit()
        name_item.setPlaceholderText("مثال: عصائر خاصة")
        price_item = QDoubleSpinBox()
        price_item.setRange(0, 99999)
        price_item.setSuffix(" LYD")
        
        del_btn = create_danger_button("❌")
        del_btn.clicked.connect(lambda _, r=row: self._delete_row(r))
        
        self.table.setCellWidget(row, 0, name_item)
        self.table.setCellWidget(row, 1, price_item)
        self.table.setCellWidget(row, 2, del_btn)

    def _delete_row(self, row_index):
        # We find widget and remove
        self.table.removeRow(self.table.currentRow())

    def get_extras(self) -> list:
        extras = []
        for r in range(self.table.rowCount()):
            name_widget = self.table.cellWidget(r, 0)
            price_widget = self.table.cellWidget(r, 1)
            if name_widget and price_widget:
                name = name_widget.text().strip()
                price = price_widget.value()
                if name:
                    extras.append({"service_name": name, "price": price})
        return extras

    def set_extras(self, extras_list):
        self.table.setRowCount(0)
        for ex in extras_list:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            name_widget = QLineEdit()
            name_widget.setText(ex.service_name or "")
            
            price_widget = QDoubleSpinBox()
            price_widget.setRange(0, 99999)
            price_widget.setValue(float(ex.price) if ex.price else 0)
            price_widget.setSuffix(" LYD")
            
            del_btn = create_danger_button("❌")
            # Simple reference binding
            del_btn.clicked.connect(lambda _, r=row: self.table.removeRow(self.table.currentRow()))
            
            self.table.setCellWidget(row, 0, name_widget)
            self.table.setCellWidget(row, 1, price_widget)
            self.table.setCellWidget(row, 2, del_btn)


# ─── 3. Catering Dialog ──────────────────────────────────────────────────────

class CateringDialog(QDialog):
    def __init__(self, order=None, parent=None):
        super().__init__(parent)
        self.order = order
        self.result_order = None
        self.result_extras = None
        self.setWindowTitle("تعديل طلبية التموين" if order else "إضافة طلبية تموين")
        self.setMinimumWidth(550)
        self.setLayoutDirection(Qt.RightToLeft)
        self.setStyleSheet(f"QDialog {{ background-color: {COLORS['background']}; color: {COLORS['text_primary']}; }}")
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(SPACING["md"])
        
        title = QLabel(self.windowTitle())
        title.setFont(QFont(FONTS["display"].split(",")[0], FONT_SIZES["h2"], QFont.Bold))
        title.setStyleSheet(f"color: {COLORS['accent']};")
        layout.addWidget(title)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)

        # Meal Type
        self.meal_combo = QComboBox()
        for m in CateringMeal:
            self.meal_combo.addItem(m.value, m)
        form.addRow("نوع الوجبة/الضيافة *:", self.meal_combo)

        # Level
        self.level_combo = QComboBox()
        for lvl in CateringLevel:
            self.level_combo.addItem(lvl.value, lvl)
        form.addRow("مستوى تقديم الخدمة:", self.level_combo)

        # Pricing Mode
        self.mode_combo = QComboBox()
        self.mode_combo.addItem("لكل شخص (per_person)", "per_person")
        self.mode_combo.addItem("لكل يوم (per_day)", "per_day")
        form.addRow("طريقة التسعير:", self.mode_combo)

        # Numbers
        self.persons = QSpinBox()
        self.persons.setRange(1, 99999)
        self.persons.setValue(20)
        form.addRow("عدد الأشخاص (إن وجد):", self.persons)

        self.days = QSpinBox()
        self.days.setRange(1, 99999)
        self.days.setValue(1)
        form.addRow("عدد الأيام (إن وجد):", self.days)

        # Unit Price
        self.price_input = QDoubleSpinBox()
        self.price_input.setRange(0.01, 999999)
        self.price_input.setSuffix(" LYD")
        form.addRow("سعر الوحدة *:", self.price_input)

        self.details = QTextEdit()
        self.details.setMaximumHeight(60)
        form.addRow("تفاصيل إضافية:", self.details)

        layout.addLayout(form)

        # Extras Table Manager
        self.extras_manager = ExtrasTableWidget()
        layout.addWidget(self.extras_manager)

        if self.order:
            self._prefill()

        # Buttons
        btn_layout = QHBoxLayout()
        cancel_btn = create_button("إلغاء", BUTTON_GHOST)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        btn_layout.addStretch()
        save_btn = create_button("حفظ", BUTTON_PRIMARY)
        save_btn.clicked.connect(self._save)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)

    def _prefill(self):
        o = self.order
        self.price_input.setValue(float(o.unit_price))
        self.details.setPlainText(o.details or "")
        if o.num_persons: self.persons.setValue(o.num_persons)
        if o.num_days: self.days.setValue(o.num_days)
        
        idx = self.mode_combo.findData(o.pricing_mode)
        if idx >= 0: self.mode_combo.setCurrentIndex(idx)
        
        for idx in range(self.meal_combo.count()):
            if self.meal_combo.itemData(idx) == o.meal_type:
                self.meal_combo.setCurrentIndex(idx)
                break

        for idx in range(self.level_combo.count()):
            if self.level_combo.itemData(idx) == o.service_level:
                self.level_combo.setCurrentIndex(idx)
                break

        self.extras_manager.set_extras(o.extra_services)

    def _save(self):
        self.result_order = {
            "meal_type": self.meal_combo.currentData(),
            "service_level": self.level_combo.currentData(),
            "pricing_mode": self.mode_combo.currentData(),
            "num_persons": self.persons.value(),
            "num_days": self.days.value(),
            "unit_price": self.price_input.value(),
            "details": self.details.toPlainText().strip() or None,
        }
        self.result_extras = self.extras_manager.get_extras()
        self.accept()


# ─── 4. Accommodation Dialog ──────────────────────────────────────────────────

class AccommodationDialog(QDialog):
    def __init__(self, booking=None, parent=None):
        super().__init__(parent)
        self.booking = booking
        self.result_booking = None
        self.result_extras = None
        self.setWindowTitle("تعديل حجز السكن" if booking else "حجز سكن جديد")
        self.setMinimumWidth(550)
        self.setLayoutDirection(Qt.RightToLeft)
        self.setStyleSheet(f"QDialog {{ background-color: {COLORS['background']}; color: {COLORS['text_primary']}; }}")
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(SPACING["md"])
        
        title = QLabel(self.windowTitle())
        title.setFont(QFont(FONTS["display"].split(",")[0], FONT_SIZES["h2"], QFont.Bold))
        title.setStyleSheet(f"color: {COLORS['accent']};")
        layout.addWidget(title)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)

        # Apartment type
        self.type_input = QLineEdit()
        self.type_input.setPlaceholderText("مثال: شقة A2 أو A")
        form.addRow("رقم/نوع الشقة *:", self.type_input)

        # Check-in
        self.in_date = QDateEdit()
        self.in_date.setCalendarPopup(True)
        self.in_date.setDate(QDate.currentDate())
        self.in_date.setDisplayFormat("yyyy-MM-dd")
        form.addRow("تاريخ الدخول *:", self.in_date)

        # Check-out
        self.out_date = QDateEdit()
        self.out_date.setCalendarPopup(True)
        self.out_date.setDate(QDate.currentDate().addDays(7))
        self.out_date.setDisplayFormat("yyyy-MM-dd")
        form.addRow("تاريخ المغادرة *:", self.out_date)

        layout.addLayout(form)

        # Extras Table Manager
        self.extras_manager = ExtrasTableWidget()
        layout.addWidget(self.extras_manager)

        if self.booking:
            self._prefill()

        # Buttons
        btn_layout = QHBoxLayout()
        cancel_btn = create_button("إلغاء", BUTTON_GHOST)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        btn_layout.addStretch()
        save_btn = create_button("حفظ", BUTTON_PRIMARY)
        save_btn.clicked.connect(self._save)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)

    def _prefill(self):
        b = self.booking
        self.type_input.setText(b.apartment_type or "")
        self.in_date.setDate(QDate(b.check_in_date.year, b.check_in_date.month, b.check_in_date.day))
        self.out_date.setDate(QDate(b.check_out_date.year, b.check_out_date.month, b.check_out_date.day))
        self.extras_manager.set_extras(b.extra_services)

    def _save(self):
        in_d = self.in_date.date().toPyDate()
        out_d = self.out_date.date().toPyDate()
        
        if in_d >= out_d:
            QMessageBox.critical(self, "خطأ في التواريخ", "يجب أن يكون تاريخ الدخول قبل المغادرة.")
            return

        self.result_booking = {
            "apartment_type": self.type_input.text().strip(),
            "check_in_date": in_d,
            "check_out_date": out_d
        }
        self.result_extras = self.extras_manager.get_extras()
        self.accept()


# ─── 5. Market Research Dialog ────────────────────────────────────────────────

class ResearchDialog(QDialog):
    def __init__(self, research=None, parent=None):
        super().__init__(parent)
        self.research = research
        self.result_data = None
        self.setWindowTitle("تعديل طلب بحث السوق" if research else "إضافة طلب بحث سوق")
        self.setMinimumWidth(500)
        self.setLayoutDirection(Qt.RightToLeft)
        self.setStyleSheet(f"QDialog {{ background-color: {COLORS['background']}; color: {COLORS['text_primary']}; }}")
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(SPACING["md"])
        
        title = QLabel(self.windowTitle())
        title.setFont(QFont(FONTS["display"].split(",")[0], FONT_SIZES["h2"], QFont.Bold))
        title.setStyleSheet(f"color: {COLORS['accent']};")
        layout.addWidget(title)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)

        # Method
        self.method_combo = QComboBox()
        self.method_combo.addItem("ميداني (field)", "field")
        self.method_combo.addItem("إلكتروني (online)", "online")
        form.addRow("طريقة جمع البيانات *:", self.method_combo)

        # Type
        self.type_input = QLineEdit()
        self.type_input.setPlaceholderText("مثال: دراسة جدوى تسويقية، استبيان آراء")
        form.addRow("نوع البيانات المستهدفة *:", self.type_input)

        # Sample min/max
        self.min_sample = QSpinBox()
        self.min_sample.setRange(1, 9999999)
        self.min_sample.setValue(100)
        form.addRow("الحد الأدنى للعينات:", self.min_sample)

        self.max_sample = QSpinBox()
        self.max_sample.setRange(1, 9999999)
        self.max_sample.setValue(1000)
        form.addRow("الحد الأقصى للعينات:", self.max_sample)

        # Prices
        self.min_price = QDoubleSpinBox()
        self.min_price.setRange(0, 9999999)
        self.min_price.setSuffix(" LYD")
        form.addRow("السعر التقديري الأدنى:", self.min_price)

        self.max_price = QDoubleSpinBox()
        self.max_price.setRange(0, 9999999)
        self.max_price.setSuffix(" LYD")
        form.addRow("السعر التقديري الأقصى:", self.max_price)

        layout.addLayout(form)

        if self.research:
            self._prefill()

        # Buttons
        btn_layout = QHBoxLayout()
        cancel_btn = create_button("إلغاء", BUTTON_GHOST)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        btn_layout.addStretch()
        save_btn = create_button("حفظ", BUTTON_PRIMARY)
        save_btn.clicked.connect(self._save)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)

    def _prefill(self):
        r = self.research
        self.type_input.setText(r.collection_type or "")
        self.min_sample.setValue(r.min_samples)
        self.max_sample.setValue(r.max_samples)
        if r.min_price: self.min_price.setValue(float(r.min_price))
        if r.max_price: self.max_price.setValue(float(r.max_price))
        
        idx = self.method_combo.findData(r.collection_method)
        if idx >= 0: self.method_combo.setCurrentIndex(idx)

    def _save(self):
        col_type = self.type_input.text().strip()
        if not col_type:
            self.type_input.setFocus()
            return
        
        self.result_data = {
            "collection_method": self.method_combo.currentData(),
            "collection_type": col_type,
            "min_samples": self.min_sample.value(),
            "max_samples": self.max_sample.value(),
            "min_price": self.min_price.value(),
            "max_price": self.max_price.value(),
        }
        self.accept()


# ─── 6. Logistics Main Panel (LogisticsForm) ──────────────────────────────────

class LogisticsForm(QWidget):
    """الشاشة الرئيسية المجمعة لتبويبات الخدمات اللوجستية والجانبية."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayoutDirection(Qt.RightToLeft)
        self._setup_ui()
        self._refresh_all_tables()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(SPACING["xl"], SPACING["lg"],
                                        SPACING["xl"], SPACING["lg"])
        main_layout.setSpacing(SPACING["md"])

        # Header Title
        title = QLabel("🛠️  الخدمات اللوجستية والجانبية")
        title.setFont(QFont(FONTS["display"].split(",")[0], FONT_SIZES["h2"], QFont.Bold))
        title.setStyleSheet(f"color: {COLORS['text_primary']}; background: transparent;")
        main_layout.addWidget(title)

        # Separator line
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background-color: {COLORS['border']};")
        main_layout.addWidget(sep)

        # Tab Widget
        self.tabs = QTabWidget()
        self.tabs.setFont(QFont(FONTS["body"].split(",")[0], FONT_SIZES["body"]))

        # Setup individual tabs
        self._setup_consultants_tab()
        self._setup_catering_tab()
        self._setup_accommodation_tab()
        self._setup_research_tab()

        main_layout.addWidget(self.tabs)

    def _refresh_all_tables(self):
        self.refresh_consultants_table()
        self.refresh_catering_table()
        self.refresh_accommodation_table()
        self.refresh_research_table()

    # ── 6.1 Consultant Tab Setup ──
    def _setup_consultants_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        hdr = QHBoxLayout()
        hdr.addWidget(QLabel("إدارة المستشارين الخارجيين وعقودهم الاستشارية"))
        hdr.addStretch()
        add_btn = create_button("➕ إضافة مستشار", BUTTON_PRIMARY)
        add_btn.clicked.connect(self._add_consultant)
        hdr.addWidget(add_btn)
        layout.addLayout(hdr)

        self.consultants_table = QTableWidget()
        self.consultants_table.setColumnCount(8)
        self.consultants_table.setHorizontalHeaderLabels([
            "الاسم", "الهاتف", "التخصص", "قيمة العقد", "صافي ربح المركز", "تاريخ البدء", "تاريخ الانتهاء", "إجراءات"
        ])
        self.consultants_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.consultants_table.horizontalHeader().setSectionResizeMode(7, QHeaderView.Fixed)
        self.consultants_table.setColumnWidth(7, 160)
        self.consultants_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.consultants_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.consultants_table.verticalHeader().setVisible(False)
        layout.addWidget(self.consultants_table)

        self.tabs.addTab(tab, "💼  الاستشارات والمستشارين")

    def refresh_consultants_table(self):
        items = consultant_svc.get_all_consultants()
        self.consultants_table.setRowCount(len(items))
        for row, c in enumerate(items):
            self.consultants_table.setItem(row, 0, QTableWidgetItem(c.name or ""))
            self.consultants_table.setItem(row, 1, QTableWidgetItem(c.phone or ""))
            
            spec_val = c.specialization.value if hasattr(c.specialization, 'value') else str(c.specialization or "")
            self.consultants_table.setItem(row, 2, QTableWidgetItem(spec_val))
            
            gross = f"{c.gross_value:.2f} LYD" if c.gross_value else ""
            self.consultants_table.setItem(row, 3, QTableWidgetItem(gross))

            # Profit = center_share or gross_value - consultant_share
            profit_val = c.center_share if c.center_share else ((c.gross_value or 0) - (c.consultant_share or 0))
            profit_str = f"{profit_val:.2f} LYD" if profit_val else ""
            self.consultants_table.setItem(row, 4, QTableWidgetItem(profit_str))

            self.consultants_table.setItem(row, 5, QTableWidgetItem(str(c.contract_start) if c.contract_start else ""))
            self.consultants_table.setItem(row, 6, QTableWidgetItem(str(c.contract_end) if c.contract_end else ""))

            # Actions
            actions = QWidget()
            actions_layout = QHBoxLayout(actions)
            actions_layout.setContentsMargins(4, 4, 4, 4)
            actions_layout.setSpacing(4)

            profile_btn = create_button("👤", BUTTON_GHOST)
            profile_btn.setFixedSize(36, 32)
            profile_btn.setToolTip("عرض الملف التعريفي")
            profile_btn.clicked.connect(lambda _, c_obj=c: self._view_consultant_profile(c_obj))
            actions_layout.addWidget(profile_btn)

            edit_btn = create_button("✏️", BUTTON_GHOST)
            edit_btn.setFixedSize(36, 32)
            edit_btn.clicked.connect(lambda _, cid=c.id: self._edit_consultant(cid))
            actions_layout.addWidget(edit_btn)

            del_btn = create_danger_button("🗑️")
            del_btn.setFixedSize(36, 32)
            del_btn.clicked.connect(lambda _, cid=c.id, name=c.name: self._delete_consultant(cid, name))
            actions_layout.addWidget(del_btn)

            self.consultants_table.setCellWidget(row, 7, actions)
            self.consultants_table.setRowHeight(row, 48)

    def _add_consultant(self):
        dialog = ConsultantDialog(parent=self)
        if dialog.exec_() == QDialog.Accepted and dialog.result_data:
            consultant_svc.create_consultant(dialog.result_data)
            self.refresh_consultants_table()

    def _edit_consultant(self, consultant_id: int):
        c = consultant_svc.get_consultant_by_id(consultant_id)
        if not c: return
        dialog = ConsultantDialog(consultant=c, parent=self)
        if dialog.exec_() == QDialog.Accepted and dialog.result_data:
            consultant_svc.update_consultant(consultant_id, dialog.result_data)
            self.refresh_consultants_table()

    def _delete_consultant(self, consultant_id: int, name: str):
        if confirm_delete(self, name):
            consultant_svc.soft_delete_consultant(consultant_id)
            self.refresh_consultants_table()

    def _view_consultant_profile(self, consultant):
        from ui.dialogs.profile_canvas_dialog import ProfileCanvasDialog
        dialog = ProfileCanvasDialog(consultant, person_type="consultant", parent=self)
        dialog.exec_()
        self.refresh_consultants_table()

    # ── 6.2 Catering Tab Setup ──
    def _setup_catering_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        hdr = QHBoxLayout()
        hdr.addWidget(QLabel("إدارة طلبيات التموين والضيافة المجهزة للدورات والقاعات"))
        hdr.addStretch()
        add_btn = create_button("➕ طلبية تموين جديدة", BUTTON_PRIMARY)
        add_btn.clicked.connect(self._add_catering)
        hdr.addWidget(add_btn)
        layout.addLayout(hdr)

        self.catering_table = QTableWidget()
        self.catering_table.setColumnCount(8)
        self.catering_table.setHorizontalHeaderLabels([
            "نوع الوجبة", "مستوى الخدمة", "طريقة التسعير", "العدد", "الأيام", "سعر الوحدة", "التكلفة الكلية (بالإضافات)", "إجراءات"
        ])
        self.catering_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.catering_table.horizontalHeader().setSectionResizeMode(7, QHeaderView.Fixed)
        self.catering_table.setColumnWidth(7, 120)
        self.catering_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.catering_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.catering_table.verticalHeader().setVisible(False)
        layout.addWidget(self.catering_table)

        self.tabs.addTab(tab, "🍏  التموين والإعاشة")

    def refresh_catering_table(self):
        items = catering_svc.get_all_catering_orders()
        self.catering_table.setRowCount(len(items))
        for row, o in enumerate(items):
            meal_val = o.meal_type.value if hasattr(o.meal_type, 'value') else str(o.meal_type or "")
            self.catering_table.setItem(row, 0, QTableWidgetItem(meal_val))
            
            lvl_val = o.service_level.value if hasattr(o.service_level, 'value') else str(o.service_level or "")
            self.catering_table.setItem(row, 1, QTableWidgetItem(lvl_val))
            
            pricing_mode = "لكل شخص" if o.pricing_mode == "per_person" else "لكل يوم"
            self.catering_table.setItem(row, 2, QTableWidgetItem(pricing_mode))
            self.catering_table.setItem(row, 3, QTableWidgetItem(str(o.num_persons or "")))
            self.catering_table.setItem(row, 4, QTableWidgetItem(str(o.num_days or "")))
            self.catering_table.setItem(row, 5, QTableWidgetItem(f"{o.unit_price:.2f} LYD"))

            # Calculate total = (unit_price * persons or 1 * days or 1) + sum of extras
            multiplier = 1
            if o.pricing_mode == "per_person" and o.num_persons:
                multiplier *= o.num_persons
            if o.num_days:
                multiplier *= o.num_days
            
            total = o.unit_price * multiplier
            for ex in o.extra_services:
                total += ex.price

            self.catering_table.setItem(row, 6, QTableWidgetItem(f"{total:.2f} LYD"))

            # Actions
            actions = QWidget()
            actions_layout = QHBoxLayout(actions)
            actions_layout.setContentsMargins(4, 4, 4, 4)
            actions_layout.setSpacing(4)

            edit_btn = create_button("✏️", BUTTON_GHOST)
            edit_btn.setFixedSize(36, 32)
            edit_btn.clicked.connect(lambda _, oid=o.id: self._edit_catering(oid))
            actions_layout.addWidget(edit_btn)

            del_btn = create_danger_button("🗑️")
            del_btn.setFixedSize(36, 32)
            del_btn.clicked.connect(lambda _, oid=o.id, name=f"وجبة {meal_val}": self._delete_catering(oid, name))
            actions_layout.addWidget(del_btn)

            self.catering_table.setCellWidget(row, 7, actions)
            self.catering_table.setRowHeight(row, 48)

    def _add_catering(self):
        dialog = CateringDialog(parent=self)
        if dialog.exec_() == QDialog.Accepted and dialog.result_order:
            catering_svc.create_catering_order(dialog.result_order, dialog.result_extras)
            self.refresh_catering_table()

    def _edit_catering(self, order_id: int):
        o = catering_svc.get_catering_order_by_id(order_id)
        if not o: return
        dialog = CateringDialog(order=o, parent=self)
        if dialog.exec_() == QDialog.Accepted and dialog.result_order:
            catering_svc.update_catering_order(order_id, dialog.result_order, dialog.result_extras)
            self.refresh_catering_table()

    def _delete_catering(self, order_id: int, name: str):
        if confirm_delete(self, name):
            catering_svc.delete_catering_order(order_id)
            self.refresh_catering_table()

    # ── 6.3 Accommodation Tab Setup ──
    def _setup_accommodation_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        hdr = QHBoxLayout()
        hdr.addWidget(QLabel("إدارة حجوزات الشقق السكنية التابعة للمركز"))
        hdr.addStretch()
        add_btn = create_button("➕ حجز سكن جديد", BUTTON_PRIMARY)
        add_btn.clicked.connect(self._add_accommodation)
        hdr.addWidget(add_btn)
        layout.addLayout(hdr)

        self.accommodation_table = QTableWidget()
        self.accommodation_table.setColumnCount(6)
        self.accommodation_table.setHorizontalHeaderLabels([
            "رقم/نوع الشقة", "تاريخ الدخول", "تاريخ المغادرة", "مدة الإقامة (يوم)", "تكلفة الخدمات الإضافية", "إجراءات"
        ])
        self.accommodation_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.accommodation_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Fixed)
        self.accommodation_table.setColumnWidth(5, 120)
        self.accommodation_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.accommodation_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.accommodation_table.verticalHeader().setVisible(False)
        layout.addWidget(self.accommodation_table)

        self.tabs.addTab(tab, "🏨  السكن والإقامة")

    def refresh_accommodation_table(self):
        items = accommodation_svc.get_all_bookings()
        self.accommodation_table.setRowCount(len(items))
        for row, b in enumerate(items):
            self.accommodation_table.setItem(row, 0, QTableWidgetItem(b.apartment_type or ""))
            self.accommodation_table.setItem(row, 1, QTableWidgetItem(str(b.check_in_date)))
            self.accommodation_table.setItem(row, 2, QTableWidgetItem(str(b.check_out_date)))
            
            # Duration Calculation
            days = (b.check_out_date - b.check_in_date).days
            self.accommodation_table.setItem(row, 3, QTableWidgetItem(f"{days} يوم"))
            
            # Extra services sum
            extras_total = sum(ex.price for ex in b.extra_services)
            self.accommodation_table.setItem(row, 4, QTableWidgetItem(f"{extras_total:.2f} LYD"))

            # Actions
            actions = QWidget()
            actions_layout = QHBoxLayout(actions)
            actions_layout.setContentsMargins(4, 4, 4, 4)
            actions_layout.setSpacing(4)

            edit_btn = create_button("✏️", BUTTON_GHOST)
            edit_btn.setFixedSize(36, 32)
            edit_btn.clicked.connect(lambda _, bid=b.id: self._edit_accommodation(bid))
            actions_layout.addWidget(edit_btn)

            del_btn = create_danger_button("🗑️")
            del_btn.setFixedSize(36, 32)
            del_btn.clicked.connect(lambda _, bid=b.id, name=f"حجز الشقة {b.apartment_type}": self._delete_accommodation(bid, name))
            actions_layout.addWidget(del_btn)

            self.accommodation_table.setCellWidget(row, 5, actions)
            self.accommodation_table.setRowHeight(row, 48)

    def _add_accommodation(self):
        dialog = AccommodationDialog(parent=self)
        if dialog.exec_() == QDialog.Accepted and dialog.result_booking:
            try:
                accommodation_svc.create_booking(dialog.result_booking, dialog.result_extras)
                self.refresh_accommodation_table()
            except Exception as e:
                print(f"Error creating booking: {e}")

    def _edit_accommodation(self, booking_id: int):
        b = accommodation_svc.get_booking_by_id(booking_id)
        if not b: return
        dialog = AccommodationDialog(booking=b, parent=self)
        if dialog.exec_() == QDialog.Accepted and dialog.result_booking:
            try:
                accommodation_svc.update_booking(booking_id, dialog.result_booking, dialog.result_extras)
                self.refresh_accommodation_table()
            except Exception as e:
                print(f"Error updating booking: {e}")

    def _delete_accommodation(self, booking_id: int, name: str):
        if confirm_delete(self, name):
            accommodation_svc.delete_booking(booking_id)
            self.refresh_accommodation_table()

    # ── 6.4 Market Research Tab Setup ──
    def _setup_research_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        hdr = QHBoxLayout()
        hdr.addWidget(QLabel("إدارة طلبات استمارات دراسات وبحوث وتجهيز البيانات الإحصائية"))
        hdr.addStretch()
        add_btn = create_button("➕ طلب بحث سوق جديد", BUTTON_PRIMARY)
        add_btn.clicked.connect(self._add_research)
        hdr.addWidget(add_btn)
        layout.addLayout(hdr)

        self.research_table = QTableWidget()
        self.research_table.setColumnCount(6)
        self.research_table.setHorizontalHeaderLabels([
            "طريقة الجمع", "البيانات المستهدفة", "الحد الأدنى للعينات", "الحد الأقصى للعينات", "التسعير التقديري", "إجراءات"
        ])
        self.research_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.research_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Fixed)
        self.research_table.setColumnWidth(5, 120)
        self.research_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.research_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.research_table.verticalHeader().setVisible(False)
        layout.addWidget(self.research_table)

        self.tabs.addTab(tab, "📊  بحوث ودراسات السوق")

    def refresh_research_table(self):
        items = research_svc.get_all_research()
        self.research_table.setRowCount(len(items))
        for row, r in enumerate(items):
            method = "ميداني (field)" if r.collection_method == "field" else "إلكتروني (online)"
            self.research_table.setItem(row, 0, QTableWidgetItem(method))
            self.research_table.setItem(row, 1, QTableWidgetItem(r.collection_type or ""))
            self.research_table.setItem(row, 2, QTableWidgetItem(str(r.min_samples)))
            self.research_table.setItem(row, 3, QTableWidgetItem(str(r.max_samples)))
            
            pricing = f"{r.min_price:.2f} - {r.max_price:.2f} LYD"
            self.research_table.setItem(row, 4, QTableWidgetItem(pricing))

            # Actions
            actions = QWidget()
            actions_layout = QHBoxLayout(actions)
            actions_layout.setContentsMargins(4, 4, 4, 4)
            actions_layout.setSpacing(4)

            edit_btn = create_button("✏️", BUTTON_GHOST)
            edit_btn.setFixedSize(36, 32)
            edit_btn.clicked.connect(lambda _, rid=r.id: self._edit_research(rid))
            actions_layout.addWidget(edit_btn)

            del_btn = create_danger_button("🗑️")
            del_btn.setFixedSize(36, 32)
            del_btn.clicked.connect(lambda _, rid=r.id, name=f"دراسة {r.collection_type}": self._delete_research(rid, name))
            actions_layout.addWidget(del_btn)

            self.research_table.setCellWidget(row, 5, actions)
            self.research_table.setRowHeight(row, 48)

    def _add_research(self):
        dialog = ResearchDialog(parent=self)
        if dialog.exec_() == QDialog.Accepted and dialog.result_data:
            research_svc.create_research(dialog.result_data)
            self.refresh_research_table()

    def _edit_research(self, research_id: int):
        r = research_svc.get_research_by_id(research_id)
        if not r: return
        dialog = ResearchDialog(research=r, parent=self)
        if dialog.exec_() == QDialog.Accepted and dialog.result_data:
            research_svc.update_research(research_id, dialog.result_data)
            self.refresh_research_table()

    def _delete_research(self, research_id: int, name: str):
        if confirm_delete(self, name):
            research_svc.delete_research(research_id)
            self.refresh_research_table()
