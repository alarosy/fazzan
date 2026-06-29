"""
Finance Form — شاشة المركز المالي المجمعة.
تجمع تبويبات عروض الأسعار، الفواتير، السندات، المصروفات، الأصول، سجل الخزينة، والتقارير المالية.
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QDialog,
    QFormLayout, QTextEdit, QFrame, QAbstractItemView, QComboBox,
    QSpinBox, QDoubleSpinBox, QDateEdit, QTabWidget, QMessageBox,
    QPushButton, QGroupBox
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont, QColor

from ui.styles import COLORS, FONTS, FONT_SIZES, SPACING
from ui.button_utils import (
    create_button, create_danger_button, confirm_delete,
    BUTTON_PRIMARY, BUTTON_SECONDARY, BUTTON_GHOST
)

import services.finance_service as finance_svc
import services.client_service as client_svc
import services.project_service as project_svc
import services.hr_service as hr_svc
import core.exporter as exporter

from models.enums import (
    ProposalStatus, ServiceType, VoucherType,
    PaymentMethod, RevenueSource, AssetCategory,
    AssetOwnership, RegisterType
)


# ─── 1. Line Items Table Widget (لإدخال بنود عروض الأسعار) ────────────────────

class LineItemsTableWidget(QWidget):
    """جدول ديناميكي لإدارة بنود الخدمات داخل نافذة عرض السعر."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayoutDirection(Qt.RightToLeft)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        hdr = QHBoxLayout()
        hdr.addWidget(QLabel("بنود الخدمات والأسعار بالتفصيل:"))
        hdr.addStretch()
        add_btn = create_button("➕ إضافة بند خدمة", BUTTON_SECONDARY)
        add_btn.clicked.connect(self._add_row)
        hdr.addWidget(add_btn)
        layout.addLayout(hdr)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "نوع الخدمة", "البيان / الوصف", "الكمية", "سعر الوحدة", "الخصم", "الإجمالي"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setFixedHeight(150)
        layout.addWidget(self.table)

    def _add_row(self):
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        # Service type
        service_combo = QComboBox()
        for st in ServiceType:
            service_combo.addItem(st.value, st)
            
        # Description
        desc_input = QLineEdit()
        desc_input.setPlaceholderText("مثال: تدريب متقدم")
        
        # Quantity
        qty_input = QDoubleSpinBox()
        qty_input.setRange(0.01, 999999)
        qty_input.setValue(1.00)
        
        # Unit Price
        price_input = QDoubleSpinBox()
        price_input.setRange(0, 9999999)
        price_input.setValue(0.00)
        price_input.setSuffix(" LYD")
        
        # Discount
        disc_input = QDoubleSpinBox()
        disc_input.setRange(0, 9999999)
        disc_input.setValue(0.00)
        disc_input.setSuffix(" LYD")
        
        # Total Label
        total_lbl = QLabel("0.00 LYD")
        total_lbl.setAlignment(Qt.AlignCenter)
        
        # Connect signals for auto calculation
        qty_input.valueChanged.connect(lambda: self._recalc_row(row))
        price_input.valueChanged.connect(lambda: self._recalc_row(row))
        disc_input.valueChanged.connect(lambda: self._recalc_row(row))
        
        self.table.setCellWidget(row, 0, service_combo)
        self.table.setCellWidget(row, 1, desc_input)
        self.table.setCellWidget(row, 2, qty_input)
        self.table.setCellWidget(row, 3, price_input)
        self.table.setCellWidget(row, 4, disc_input)
        self.table.setCellWidget(row, 5, total_lbl)

    def _recalc_row(self, row):
        qty_widget = self.table.cellWidget(row, 2)
        price_widget = self.table.cellWidget(row, 3)
        disc_widget = self.table.cellWidget(row, 4)
        total_widget = self.table.cellWidget(row, 5)
        
        if qty_widget and price_widget and disc_widget and total_widget:
            qty = qty_widget.value()
            price = price_widget.value()
            disc = disc_widget.value()
            tot = (qty * price) - disc
            total_widget.setText(f"{tot:.2f} LYD")

    def get_items(self) -> list:
        items = []
        for r in range(self.table.rowCount()):
            service_w = self.table.cellWidget(r, 0)
            desc_w = self.table.cellWidget(r, 1)
            qty_w = self.table.cellWidget(r, 2)
            price_w = self.table.cellWidget(r, 3)
            disc_w = self.table.cellWidget(r, 4)
            
            if service_w and desc_w and qty_w and price_w and disc_w:
                qty = qty_w.value()
                price = price_w.value()
                disc = disc_w.value()
                tot = (qty * price) - disc
                desc = desc_w.text().strip()
                if desc:
                    items.append({
                        "service_type": service_w.currentData(),
                        "unit_description": desc,
                        "quantity": qty,
                        "unit_price": price,
                        "discount": disc,
                        "total": tot
                    })
        return items

    def set_items(self, items_list):
        self.table.setRowCount(0)
        for item in items_list:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            service_combo = QComboBox()
            for st in ServiceType:
                service_combo.addItem(st.value, st)
            for idx in range(service_combo.count()):
                if service_combo.itemData(idx) == item.service_type:
                    service_combo.setCurrentIndex(idx)
                    break
                    
            desc_input = QLineEdit()
            desc_input.setText(item.unit_description or "")
            
            qty_input = QDoubleSpinBox()
            qty_input.setRange(0.01, 999999)
            qty_input.setValue(float(item.quantity))
            
            price_input = QDoubleSpinBox()
            price_input.setRange(0, 9999999)
            price_input.setValue(float(item.unit_price))
            price_input.setSuffix(" LYD")
            
            disc_input = QDoubleSpinBox()
            disc_input.setRange(0, 9999999)
            disc_input.setValue(float(item.discount or 0))
            disc_input.setSuffix(" LYD")
            
            tot = (float(item.quantity) * float(item.unit_price)) - float(item.discount or 0)
            total_lbl = QLabel(f"{tot:.2f} LYD")
            total_lbl.setAlignment(Qt.AlignCenter)
            
            # Rebind signals with row references (since row value is captured, this is fine)
            qty_input.valueChanged.connect(lambda _, r=row: self._recalc_row(r))
            price_input.valueChanged.connect(lambda _, r=row: self._recalc_row(r))
            disc_input.valueChanged.connect(lambda _, r=row: self._recalc_row(r))
            
            self.table.setCellWidget(row, 0, service_combo)
            self.table.setCellWidget(row, 1, desc_input)
            self.table.setCellWidget(row, 2, qty_input)
            self.table.setCellWidget(row, 3, price_input)
            self.table.setCellWidget(row, 4, disc_input)
            self.table.setCellWidget(row, 5, total_lbl)


# ─── 2. Proposal Dialog ──────────────────────────────────────────────────────

class ProposalDialog(QDialog):
    def __init__(self, proposal=None, parent=None):
        super().__init__(parent)
        self.proposal = proposal
        self.result_data = None
        self.result_items = None
        self.setWindowTitle("تعديل عرض سعر" if proposal else "إضافة عرض سعر جديد")
        self.setMinimumWidth(700)
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

        # Clients Combo
        self.client_combo = QComboBox()
        clients = client_svc.get_all_clients()
        for cl in clients:
            self.client_combo.addItem(cl.name, cl.id)
        form.addRow("العميل المستهدف *:", self.client_combo)

        # Service type main
        self.type_combo = QComboBox()
        for st in ServiceType:
            self.type_combo.addItem(st.value, st)
        form.addRow("الخدمة الأساسية:", self.type_combo)

        # Notes
        self.notes = QTextEdit()
        self.notes.setMaximumHeight(50)
        form.addRow("ملاحظات وشروط العرض:", self.notes)

        layout.addLayout(form)

        # Items Table
        self.items_manager = LineItemsTableWidget()
        layout.addWidget(self.items_manager)

        if self.proposal:
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
        p = self.proposal
        self.notes.setPlainText(p.notes or "")
        
        idx = self.client_combo.findData(p.client_id)
        if idx >= 0: self.client_combo.setCurrentIndex(idx)
        
        for idx in range(self.type_combo.count()):
            if self.type_combo.itemData(idx) == p.service_type:
                self.type_combo.setCurrentIndex(idx)
                break
                
        self.items_manager.set_items(p.line_items)

    def _save(self):
        items = self.items_manager.get_items()
        if not items:
            QMessageBox.critical(self, "خطأ", "يجب إضافة بند خدمة واحد على الأقل")
            return
            
        self.result_data = {
            "client_id": self.client_combo.currentData(),
            "service_type": self.type_combo.currentData(),
            "notes": self.notes.toPlainText().strip() or None,
        }
        self.result_items = items
        self.accept()


# ─── 3. Voucher Dialog ───────────────────────────────────────────────────────

class VoucherDialog(QDialog):
    def __init__(self, voucher=None, parent=None):
        super().__init__(parent)
        self.voucher = voucher
        self.result_data = None
        self.setWindowTitle("تعديل سند مالي" if voucher else "إصدار سند مالي")
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

        # Voucher Type
        self.type_combo = QComboBox()
        for vt in VoucherType:
            self.type_combo.addItem(vt.value, vt)
        form.addRow("نوع السند *:", self.type_combo)

        # Party name
        self.party_input = QLineEdit()
        self.party_input.setPlaceholderText("الجهة المسلمة أو المستلمة")
        form.addRow("اسم العميل / الجهة *:", self.party_input)

        # Amount
        self.amount_input = QDoubleSpinBox()
        self.amount_input.setRange(0.01, 99999999)
        self.amount_input.setSuffix(" LYD")
        form.addRow("قيمة المبلغ الرقمي *:", self.amount_input)

        # Method
        self.method_combo = QComboBox()
        for pm in PaymentMethod:
            self.method_combo.addItem(pm.value, pm)
        form.addRow("طريقة الدفع/القبض:", self.method_combo)

        # Revenue source (optional for Receipt)
        self.source_combo = QComboBox()
        self.source_combo.addItem("غير محدد", None)
        for rs in RevenueSource:
            self.source_combo.addItem(rs.value, rs)
        form.addRow("بند الإيراد (خاص بسند القبض):", self.source_combo)

        # Project ID (optional)
        self.project_combo = QComboBox()
        self.project_combo.addItem("غير مرتبط بمشروع", None)
        projects = project_svc.get_all_projects()
        for pr in projects:
            self.project_combo.addItem(pr.name, pr.id)
        form.addRow("تحميل على مشروع:", self.project_combo)

        # Notes
        self.notes = QTextEdit()
        self.notes.setMaximumHeight(60)
        form.addRow("البيان والملاحظات:", self.notes)

        layout.addLayout(form)

        if self.voucher:
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
        v = self.voucher
        self.party_input.setText(v.party_name or "")
        self.amount_input.setValue(float(v.amount))
        self.notes.setPlainText(v.notes or "")
        
        for idx in range(self.type_combo.count()):
            if self.type_combo.itemData(idx) == v.voucher_type:
                self.type_combo.setCurrentIndex(idx)
                break
        for idx in range(self.method_combo.count()):
            if self.method_combo.itemData(idx) == v.payment_method:
                self.method_combo.setCurrentIndex(idx)
                break
        for idx in range(self.source_combo.count()):
            if self.source_combo.itemData(idx) == v.revenue_source:
                self.source_combo.setCurrentIndex(idx)
                break
        idx_p = self.project_combo.findData(v.project_id)
        if idx_p >= 0: self.project_combo.setCurrentIndex(idx_p)

    def _save(self):
        party = self.party_input.text().strip()
        if not party:
            self.party_input.setFocus()
            return
            
        self.result_data = {
            "voucher_type": self.type_combo.currentData(),
            "party_name": party,
            "amount": Decimal(str(self.amount_input.value())),
            "payment_method": self.method_combo.currentData(),
            "revenue_source": self.source_combo.currentData(),
            "project_id": self.project_combo.currentData(),
            "notes": self.notes.toPlainText().strip() or None,
        }
        self.accept()


# ─── 4. Expense Dialog ───────────────────────────────────────────────────────

class ExpenseDialog(QDialog):
    def __init__(self, expense=None, parent=None):
        super().__init__(parent)
        self.expense = expense
        self.result_data = None
        self.setWindowTitle("تعديل مصروف مالي" if expense else "تسجيل مصروف جديد")
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

        # Name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("مثال: شراء أحبار طابعات")
        form.addRow("بيان المصروف *:", self.name_input)

        # Qty & Price
        self.qty = QDoubleSpinBox()
        self.qty.setRange(0.01, 9999)
        self.qty.setValue(1.00)
        form.addRow("الكمية:", self.qty)

        self.unit = QLineEdit()
        self.unit.setPlaceholderText("مثال: علبة / قطعة / يوم")
        form.addRow("الوحدة:", self.unit)

        self.price = QDoubleSpinBox()
        self.price.setRange(0.01, 9999999)
        self.price.setSuffix(" LYD")
        form.addRow("سعر الوحدة *:", self.price)

        # Project ID (optional)
        self.project_combo = QComboBox()
        self.project_combo.addItem("مصروف تشغيلي عام", None)
        projects = project_svc.get_all_projects()
        for pr in projects:
            self.project_combo.addItem(pr.name, pr.id)
        form.addRow("تحميل على مشروع:", self.project_combo)

        # Method
        self.method_combo = QComboBox()
        for pm in PaymentMethod:
            self.method_combo.addItem(pm.value, pm)
        form.addRow("طريقة الدفع (الخصم من):", self.method_combo)

        # Invoice image path
        self.img_path = QLineEdit()
        self.img_path.setPlaceholderText("مسار أو رابط الفاتورة الورقية")
        form.addRow("صورة/مسار الفاتورة:", self.img_path)

        # Notes
        self.notes = QTextEdit()
        self.notes.setMaximumHeight(50)
        form.addRow("ملاحظات إضافية:", self.notes)

        layout.addLayout(form)

        if self.expense:
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
        ex = self.expense
        self.name_input.setText(ex.name or "")
        self.qty.setValue(float(ex.quantity))
        self.unit.setText(ex.unit or "")
        self.price.setValue(float(ex.unit_price))
        self.img_path.setText(ex.invoice_image_path or "")
        self.notes.setPlainText(ex.notes or "")
        
        idx_p = self.project_combo.findData(ex.project_id)
        if idx_p >= 0: self.project_combo.setCurrentIndex(idx_p)
        
        for idx in range(self.method_combo.count()):
            if self.method_combo.itemData(idx) == ex.payment_method:
                self.method_combo.setCurrentIndex(idx)
                break

    def _save(self):
        name = self.name_input.text().strip()
        if not name:
            self.name_input.setFocus()
            return
            
        self.result_data = {
            "name": name,
            "quantity": Decimal(str(self.qty.value())),
            "unit": self.unit.text().strip() or None,
            "unit_price": Decimal(str(self.price.value())),
            "project_id": self.project_combo.currentData(),
            "payment_method": self.method_combo.currentData(),
            "invoice_image_path": self.img_path.text().strip() or None,
            "notes": self.notes.toPlainText().strip() or None,
        }
        self.accept()


# ─── 5. Salary Charge Dialog (لتحميل أجور الموظفين على المشاريع) ──────────────

class SalaryChargeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.employee_id = None
        self.project_id = None
        self.work_days = 0
        self.setWindowTitle("تحميل أجر موظف على مشروع")
        self.setMinimumWidth(450)
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

        # Employees Combo
        self.emp_combo = QComboBox()
        employees = hr_svc.get_all_employees()
        for emp in employees:
            self.emp_combo.addItem(f"{emp.name} (أجر يومي: {emp.daily_wage_rate or 0} LYD)", emp.id)
        form.addRow("الموظف المستهدف *:", self.emp_combo)

        # Project Combo
        self.proj_combo = QComboBox()
        projects = project_svc.get_all_projects()
        for pr in projects:
            self.proj_combo.addItem(pr.name, pr.id)
        form.addRow("المشروع المحمل عليه *:", self.proj_combo)

        # Work Days
        self.days = QSpinBox()
        self.days.setRange(1, 365)
        self.days.setValue(5)
        form.addRow("عدد أيام العمل الفعلية *:", self.days)

        layout.addLayout(form)

        # Buttons
        btn_layout = QHBoxLayout()
        cancel_btn = create_button("إلغاء", BUTTON_GHOST)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        btn_layout.addStretch()
        save_btn = create_button("تأكيد وشحن الميزانية", BUTTON_PRIMARY)
        save_btn.clicked.connect(self._save)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)

    def _save(self):
        if not self.emp_combo.currentData() or not self.proj_combo.currentData():
            QMessageBox.critical(self, "خطأ", "يجب اختيار موظف ومشروع")
            return
            
        self.employee_id = self.emp_combo.currentData()
        self.project_id = self.proj_combo.currentData()
        self.work_days = self.days.value()
        self.accept()


# ─── 6. Asset Dialog ─────────────────────────────────────────────────────────

class AssetDialog(QDialog):
    def __init__(self, asset=None, parent=None):
        super().__init__(parent)
        self.asset = asset
        self.result_data = None
        self.setWindowTitle("تعديل أصل ثابت" if asset else "تسجيل أصل جديد")
        self.setMinimumWidth(450)
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

        # Name
        self.name_input = QLineEdit()
        form.addRow("اسم الأصل *:", self.name_input)

        # Category
        self.cat_combo = QComboBox()
        for ac in AssetCategory:
            self.cat_combo.addItem(ac.value, ac)
        form.addRow("تصنيف الأصل:", self.cat_combo)

        # Acquisition date
        self.ac_date = QDateEdit()
        self.ac_date.setCalendarPopup(True)
        self.ac_date.setDate(QDate.currentDate())
        self.ac_date.setDisplayFormat("yyyy-MM-dd")
        form.addRow("تاريخ الحيازة:", self.ac_date)

        # Depreciation months
        self.months = QSpinBox()
        self.months.setRange(1, 240)
        self.months.setValue(12)
        form.addRow("أشهر الاستهلاك (الاستهلاك الكلي):", self.months)

        # Ownership
        self.own_combo = QComboBox()
        for ao in AssetOwnership:
            self.own_combo.addItem(ao.value, ao)
        form.addRow("الملكية:", self.own_combo)

        # Lender name
        self.lender_input = QLineEdit()
        self.lender_input.setPlaceholderText("في حال كانت مستعارة")
        form.addRow("اسم المعير / المالك:", self.lender_input)

        # Notes
        self.notes = QTextEdit()
        self.notes.setMaximumHeight(50)
        form.addRow("ملاحظات إضافية:", self.notes)

        layout.addLayout(form)

        if self.asset:
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
        a = self.asset
        self.name_input.setText(a.name or "")
        self.months.setValue(a.depreciation_months)
        self.lender_input.setText(a.lender_name or "")
        self.notes.setPlainText(a.notes or "")
        
        if a.acquisition_date:
            self.ac_date.setDate(QDate(a.acquisition_date.year, a.acquisition_date.month, a.acquisition_date.day))
        
        for idx in range(self.cat_combo.count()):
            if self.cat_combo.itemData(idx) == a.category:
                self.cat_combo.setCurrentIndex(idx)
                break
        for idx in range(self.own_combo.count()):
            if self.own_combo.itemData(idx) == a.ownership:
                self.own_combo.setCurrentIndex(idx)
                break

    def _save(self):
        name = self.name_input.text().strip()
        if not name:
            self.name_input.setFocus()
            return
            
        self.result_data = {
            "name": name,
            "category": self.cat_combo.currentData(),
            "acquisition_date": self.ac_date.date().toPyDate(),
            "depreciation_months": self.months.value(),
            "ownership": self.own_combo.currentData(),
            "lender_name": self.lender_input.text().strip() or None,
            "notes": self.notes.toPlainText().strip() or None
        }
        self.accept()


# ─── 7. Main Finance Dashboard Panel ─────────────────────────────────────────

class FinanceForm(QWidget):
    """المركز المالي للتحكم بكافة المدخلات والحركات وتدفق التقارير."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayoutDirection(Qt.RightToLeft)
        self._setup_ui()
        self.refresh_all_data()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(SPACING["xl"], SPACING["lg"],
                                        SPACING["xl"], SPACING["lg"])
        main_layout.setSpacing(SPACING["md"])

        # Header Title
        title = QLabel("💰  المركز المالي والحسابات")
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
        self._setup_proposals_tab()
        self._setup_invoices_tab()
        self._setup_vouchers_tab()
        self._setup_expenses_tab()
        self._setup_assets_tab()
        self._setup_register_tab()
        self._setup_reports_tab()

        main_layout.addWidget(self.tabs)

    def refresh_all_data(self):
        self.refresh_proposals_table()
        self.refresh_invoices_table()
        self.refresh_vouchers_table()
        self.refresh_expenses_table()
        self.refresh_assets_table()
        self.refresh_register_table()
        self.refresh_reports_info()

    # ── 7.1 Proposals Tab Setup ──
    def _setup_proposals_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        hdr = QHBoxLayout()
        hdr.addWidget(QLabel("عروض الأسعار المالية الصادرة للعملاء"))
        hdr.addStretch()
        add_btn = create_button("➕ عرض سعر جديد", BUTTON_PRIMARY)
        add_btn.clicked.connect(self._add_proposal)
        hdr.addWidget(add_btn)
        layout.addLayout(hdr)

        self.proposals_table = QTableWidget()
        self.proposals_table.setColumnCount(7)
        self.proposals_table.setHorizontalHeaderLabels([
            "رقم العرض", "العميل", "الخدمة", "القيمة الكلية", "تاريخ الإصدار", "الحالة", "إجراءات"
        ])
        self.proposals_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.proposals_table.horizontalHeader().setSectionResizeMode(6, QHeaderView.Fixed)
        self.proposals_table.setColumnWidth(6, 180)
        self.proposals_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.proposals_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.proposals_table.verticalHeader().setVisible(False)
        layout.addWidget(self.proposals_table)

        self.tabs.addTab(tab, "📄  عروض الأسعار")

    def refresh_proposals_table(self):
        items = finance_svc.get_all_proposals()
        self.proposals_table.setRowCount(len(items))
        for row, p in enumerate(items):
            self.proposals_table.setItem(row, 0, QTableWidgetItem(p.proposal_number or ""))
            self.proposals_table.setItem(row, 1, QTableWidgetItem(p.client.name if p.client else "N/A"))
            
            st_val = p.service_type.value if hasattr(p.service_type, 'value') else str(p.service_type)
            self.proposals_table.setItem(row, 2, QTableWidgetItem(st_val))
            self.proposals_table.setItem(row, 3, QTableWidgetItem(f"{p.total_value:.2f} LYD" if p.total_value else ""))
            self.proposals_table.setItem(row, 4, QTableWidgetItem(p.created_at.strftime('%Y-%m-%d') if p.created_at else ""))
            
            status_val = p.status.value if hasattr(p.status, 'value') else str(p.status)
            self.proposals_table.setItem(row, 5, QTableWidgetItem(status_val))

            # Actions
            actions = QWidget()
            actions_layout = QHBoxLayout(actions)
            actions_layout.setContentsMargins(4, 4, 4, 4)
            actions_layout.setSpacing(4)

            # Print PDF
            print_btn = create_button("🖨️", BUTTON_GHOST)
            print_btn.setFixedSize(32, 32)
            print_btn.clicked.connect(lambda _, pid=p.id: self._export_proposal_pdf(pid))
            actions_layout.addWidget(print_btn)

            if p.status == ProposalStatus.PENDING:
                # Approve
                app_btn = create_button("✔️ اعتماد", BUTTON_SECONDARY)
                app_btn.setFixedSize(65, 32)
                app_btn.clicked.connect(lambda _, pid=p.id: self._approve_proposal(pid))
                actions_layout.addWidget(app_btn)
                
                # Edit
                edit_btn = create_button("✏️", BUTTON_GHOST)
                edit_btn.setFixedSize(32, 32)
                edit_btn.clicked.connect(lambda _, pid=p.id: self._edit_proposal(pid))
                actions_layout.addWidget(edit_btn)
                
                # Delete
                del_btn = create_danger_button("🗑️")
                del_btn.setFixedSize(32, 32)
                del_btn.clicked.connect(lambda _, pid=p.id, name=p.proposal_number: self._delete_proposal(pid, name))
                actions_layout.addWidget(del_btn)
                
            self.proposals_table.setCellWidget(row, 6, actions)
            self.proposals_table.setRowHeight(row, 48)

    def _add_proposal(self):
        dialog = ProposalDialog(parent=self)
        if dialog.exec_() == QDialog.Accepted and dialog.result_data:
            finance_svc.create_proposal(dialog.result_data, dialog.result_items)
            self.refresh_proposals_table()

    def _edit_proposal(self, proposal_id: int):
        p = finance_svc.get_proposal_by_id(proposal_id)
        if not p: return
        dialog = ProposalDialog(proposal=p, parent=self)
        if dialog.exec_() == QDialog.Accepted and dialog.result_data:
            finance_svc.update_proposal(proposal_id, dialog.result_data, dialog.result_items)
            self.refresh_proposals_table()

    def _delete_proposal(self, proposal_id: int, name: str):
        if confirm_delete(self, name):
            finance_svc.delete_proposal(proposal_id)
            self.refresh_proposals_table()

    def _approve_proposal(self, proposal_id: int):
        ret = finance_svc.approve_proposal(proposal_id)
        if ret:
            QMessageBox.information(self, "نجاح الاعتماد", f"تم اعتماد العرض وتوليد الفاتورة برقم {ret.invoice_number} وقيد الإيراد بالخزينة.")
            self.refresh_all_data()

    def _export_proposal_pdf(self, proposal_id: int):
        try:
            path = exporter.export_proposal_pdf(proposal_id)
            QMessageBox.information(self, "تم التصدير", f"تم توليد ملف PDF بنجاح وحفظه في:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "خطأ التصدير", f"فشل تصدير الملف: {e}")

    # ── 7.2 Invoices Tab Setup ──
    def _setup_invoices_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        layout.addWidget(QLabel("الفواتير النهائية المعتمدة والملزمة مالياً"))

        self.invoices_table = QTableWidget()
        self.invoices_table.setColumnCount(6)
        self.invoices_table.setHorizontalHeaderLabels([
            "رقم الفاتورة", "العميل", "رقم العرض الأصلي", "القيمة الكلية", "تاريخ الفاتورة", "إجراءات"
        ])
        self.invoices_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.invoices_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Fixed)
        self.invoices_table.setColumnWidth(5, 140)
        self.invoices_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.invoices_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.invoices_table.verticalHeader().setVisible(False)
        layout.addWidget(self.invoices_table)

        self.tabs.addTab(tab, "🧾  الفواتير النهائية")

    def refresh_invoices_table(self):
        items = finance_svc.get_all_invoices()
        self.invoices_table.setRowCount(len(items))
        for row, inv in enumerate(items):
            self.invoices_table.setItem(row, 0, QTableWidgetItem(inv.invoice_number or ""))
            self.invoices_table.setItem(row, 1, QTableWidgetItem(inv.client.name if inv.client else "N/A"))
            self.invoices_table.setItem(row, 2, QTableWidgetItem(inv.proposal.proposal_number if inv.proposal else ""))
            self.invoices_table.setItem(row, 3, QTableWidgetItem(f"{inv.total_value:.2f} LYD"))
            self.invoices_table.setItem(row, 4, QTableWidgetItem(inv.created_at.strftime('%Y-%m-%d') if inv.created_at else ""))

            # Actions
            actions = QWidget()
            actions_layout = QHBoxLayout(actions)
            actions_layout.setContentsMargins(4, 4, 4, 4)
            actions_layout.setSpacing(4)

            # Print
            print_btn = create_button("🖨️", BUTTON_GHOST)
            print_btn.setFixedSize(32, 32)
            print_btn.clicked.connect(lambda _, iid=inv.id: self._export_invoice_pdf(iid))
            actions_layout.addWidget(print_btn)

            # Edit
            edit_btn = create_button("✏️", BUTTON_GHOST)
            edit_btn.setFixedSize(32, 32)
            edit_btn.clicked.connect(lambda _, iid=inv.id: self._edit_invoice(iid))
            actions_layout.addWidget(edit_btn)

            # Delete
            del_btn = create_danger_button("🗑️")
            del_btn.setFixedSize(32, 32)
            del_btn.clicked.connect(lambda _, iid=inv.id, name=inv.invoice_number: self._delete_invoice(iid, name))
            actions_layout.addWidget(del_btn)

            self.invoices_table.setCellWidget(row, 5, actions)
            self.invoices_table.setRowHeight(row, 48)

    def _export_invoice_pdf(self, invoice_id: int):
        try:
            path = exporter.export_invoice_pdf(invoice_id)
            QMessageBox.information(self, "تم التصدير", f"تم توليد الفاتورة بنجاح في:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل تصدير الفاتورة: {e}")

    def _edit_invoice(self, invoice_id: int):
        inv = finance_svc.get_invoice_by_id(invoice_id)
        if not inv: return
        dialog = InvoiceDialog(invoice=inv, parent=self)
        if dialog.exec_() == QDialog.Accepted and dialog.result_data:
            finance_svc.update_invoice(invoice_id, dialog.result_data)
            self.refresh_all_data()

    def _delete_invoice(self, invoice_id: int, name: str):
        if confirm_delete(self, name):
            finance_svc.delete_invoice(invoice_id)
            self.refresh_all_data()

    # ── 7.3 Vouchers Tab Setup ──
    def _setup_vouchers_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        hdr = QHBoxLayout()
        hdr.addWidget(QLabel("إصدار سندات القبض (Receipt) وسندات الصرف (Disbursement)"))
        hdr.addStretch()
        add_btn = create_button("➕ إصدار سند جديد", BUTTON_PRIMARY)
        add_btn.clicked.connect(self._add_voucher)
        hdr.addWidget(add_btn)
        layout.addLayout(hdr)

        self.vouchers_table = QTableWidget()
        self.vouchers_table.setColumnCount(7)
        self.vouchers_table.setHorizontalHeaderLabels([
            "رقم السند", "النوع", "الجهة / الاسم", "قيمة المبلغ", "طريقة الدفع", "المشروع", "إجراءات"
        ])
        self.vouchers_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.vouchers_table.horizontalHeader().setSectionResizeMode(6, QHeaderView.Fixed)
        self.vouchers_table.setColumnWidth(6, 140)
        self.vouchers_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.vouchers_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.vouchers_table.verticalHeader().setVisible(False)
        layout.addWidget(self.vouchers_table)

        self.tabs.addTab(tab, "🎫  السندات المالية")

    def refresh_vouchers_table(self):
        items = finance_svc.get_all_vouchers()
        self.vouchers_table.setRowCount(len(items))
        for row, v in enumerate(items):
            self.vouchers_table.setItem(row, 0, QTableWidgetItem(v.voucher_number or ""))
            
            type_val = v.voucher_type.value if hasattr(v.voucher_type, 'value') else str(v.voucher_type)
            self.vouchers_table.setItem(row, 1, QTableWidgetItem(type_val))
            self.vouchers_table.setItem(row, 2, QTableWidgetItem(v.party_name or ""))
            self.vouchers_table.setItem(row, 3, QTableWidgetItem(f"{v.amount:.2f} LYD"))
            
            pm_val = v.payment_method.value if hasattr(v.payment_method, 'value') else str(v.payment_method)
            self.vouchers_table.setItem(row, 4, QTableWidgetItem(pm_val))
            self.vouchers_table.setItem(row, 5, QTableWidgetItem(v.project.name if v.project else "عام"))

            # Actions
            actions = QWidget()
            actions_layout = QHBoxLayout(actions)
            actions_layout.setContentsMargins(4, 4, 4, 4)
            actions_layout.setSpacing(4)

            # Print
            print_btn = create_button("🖨️", BUTTON_GHOST)
            print_btn.setFixedSize(32, 32)
            print_btn.clicked.connect(lambda _, vid=v.id: self._export_voucher_pdf(vid))
            actions_layout.addWidget(print_btn)

            # Edit
            edit_btn = create_button("✏️", BUTTON_GHOST)
            edit_btn.setFixedSize(32, 32)
            edit_btn.clicked.connect(lambda _, vid=v.id: self._edit_voucher(vid))
            actions_layout.addWidget(edit_btn)

            # Delete
            del_btn = create_danger_button("🗑️")
            del_btn.setFixedSize(32, 32)
            del_btn.clicked.connect(lambda _, vid=v.id, name=v.voucher_number: self._delete_voucher(vid, name))
            actions_layout.addWidget(del_btn)

            self.vouchers_table.setCellWidget(row, 6, actions)
            self.vouchers_table.setRowHeight(row, 48)

    def _add_voucher(self):
        dialog = VoucherDialog(parent=self)
        if dialog.exec_() == QDialog.Accepted and dialog.result_data:
            v = finance_svc.create_voucher(dialog.result_data)
            self.refresh_all_data()
            # Auto open print
            self._export_voucher_pdf(v.id)

    def _export_voucher_pdf(self, voucher_id: int):
        try:
            path = exporter.export_voucher_pdf(voucher_id)
            QMessageBox.information(self, "تم التصدير", f"تم طباعة السند بنجاح في:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل طباعة السند: {e}")

    def _edit_voucher(self, voucher_id: int):
        v = finance_svc.get_all_vouchers() # Wait, get_all returns list, we need to find it
        # Actually, let's write a simple helper or query by id
        # Let's find it in self.vouchers_table items:
        target = None
        for item in finance_svc.get_all_vouchers():
            if item.id == voucher_id:
                target = item
                break
        if not target: return
        
        dialog = VoucherDialog(voucher=target, parent=self)
        if dialog.exec_() == QDialog.Accepted and dialog.result_data:
            finance_svc.update_voucher(voucher_id, dialog.result_data)
            self.refresh_all_data()

    def _delete_voucher(self, voucher_id: int, name: str):
        if confirm_delete(self, name):
            finance_svc.delete_voucher(voucher_id)
            self.refresh_all_data()

    # ── 7.4 Expenses Tab Setup ──
    def _setup_expenses_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        hdr = QHBoxLayout()
        hdr.addWidget(QLabel("تسجيل وتحميل المصاريف التشغيلية للمركز وللمشاريع"))
        hdr.addStretch()
        
        charge_btn = create_button("💸 تحميل أجر موظف على مشروع", BUTTON_SECONDARY)
        charge_btn.clicked.connect(self._charge_employee)
        hdr.addWidget(charge_btn)
        
        add_btn = create_button("➕ تسجيل مصروف", BUTTON_PRIMARY)
        add_btn.clicked.connect(self._add_expense)
        hdr.addWidget(add_btn)
        layout.addLayout(hdr)

        self.expenses_table = QTableWidget()
        self.expenses_table.setColumnCount(8)
        self.expenses_table.setHorizontalHeaderLabels([
            "البيان", "الكمية", "الوحدة", "السعر", "الإجمالي", "طريقة الدفع", "المشروع المحمل", "إجراءات"
        ])
        self.expenses_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.expenses_table.horizontalHeader().setSectionResizeMode(7, QHeaderView.Fixed)
        self.expenses_table.setColumnWidth(7, 100)
        self.expenses_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.expenses_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.expenses_table.verticalHeader().setVisible(False)
        layout.addWidget(self.expenses_table)

        self.tabs.addTab(tab, "💸  المصروفات")

    def refresh_expenses_table(self):
        items = finance_svc.get_all_expenses()
        self.expenses_table.setRowCount(len(items))
        for row, ex in enumerate(items):
            self.expenses_table.setItem(row, 0, QTableWidgetItem(ex.name or ""))
            self.expenses_table.setItem(row, 1, QTableWidgetItem(f"{ex.quantity:.2f}"))
            self.expenses_table.setItem(row, 2, QTableWidgetItem(ex.unit or ""))
            self.expenses_table.setItem(row, 3, QTableWidgetItem(f"{ex.unit_price:.2f} LYD"))
            self.expenses_table.setItem(row, 4, QTableWidgetItem(f"{ex.total:.2f} LYD"))
            
            pm_val = ex.payment_method.value if hasattr(ex.payment_method, 'value') else str(ex.payment_method)
            self.expenses_table.setItem(row, 5, QTableWidgetItem(pm_val))
            self.expenses_table.setItem(row, 6, QTableWidgetItem(ex.project.name if ex.project else "تشغيلي عام"))

            # Actions
            actions = QWidget()
            actions_layout = QHBoxLayout(actions)
            actions_layout.setContentsMargins(4, 4, 4, 4)
            actions_layout.setSpacing(4)

            # Edit
            edit_btn = create_button("✏️", BUTTON_GHOST)
            edit_btn.setFixedSize(32, 32)
            edit_btn.clicked.connect(lambda _, eid=ex.id: self._edit_expense(eid))
            actions_layout.addWidget(edit_btn)

            # Delete
            del_btn = create_danger_button("🗑️")
            del_btn.setFixedSize(32, 32)
            del_btn.clicked.connect(lambda _, eid=ex.id, name=ex.name: self._delete_expense(eid, name))
            actions_layout.addWidget(del_btn)

            self.expenses_table.setCellWidget(row, 7, actions)
            self.expenses_table.setRowHeight(row, 48)

    def _add_expense(self):
        dialog = ExpenseDialog(parent=self)
        if dialog.exec_() == QDialog.Accepted and dialog.result_data:
            finance_svc.create_expense(dialog.result_data)
            self.refresh_all_data()

    def _edit_expense(self, expense_id: int):
        target = None
        for item in finance_svc.get_all_expenses():
            if item.id == expense_id:
                target = item
                break
        if not target: return
        
        dialog = ExpenseDialog(expense=target, parent=self)
        if dialog.exec_() == QDialog.Accepted and dialog.result_data:
            finance_svc.update_expense(expense_id, dialog.result_data)
            self.refresh_all_data()

    def _delete_expense(self, expense_id: int, name: str):
        if confirm_delete(self, name):
            finance_svc.delete_expense(expense_id)
            self.refresh_all_data()

    def _charge_employee(self):
        dialog = SalaryChargeDialog(parent=self)
        if dialog.exec_() == QDialog.Accepted and dialog.employee_id:
            try:
                finance_svc.charge_employee_to_project(
                    dialog.employee_id, dialog.project_id, dialog.work_days
                )
                QMessageBox.information(self, "نجاح العملية", "تم احتساب أجر الموظف وشحن ميزانية المشروع المقابل.")
                self.refresh_all_data()
            except Exception as e:
                QMessageBox.critical(self, "فشل العملية", str(e))

    # ── 7.5 Assets Tab Setup ──
    def _setup_assets_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        hdr = QHBoxLayout()
        hdr.addWidget(QLabel("سجل الأصول الثابتة للمركز ومعدل استهلاكها"))
        hdr.addStretch()
        add_btn = create_button("➕ تسجيل أصل جديد", BUTTON_PRIMARY)
        add_btn.clicked.connect(self._add_asset)
        hdr.addWidget(add_btn)
        layout.addLayout(hdr)

        self.assets_table = QTableWidget()
        self.assets_table.setColumnCount(6)
        self.assets_table.setHorizontalHeaderLabels([
            "اسم الأصل", "التصنيف", "تاريخ الحيازة", "أشهر الاستهلاك", "الملكية", "إجراءات"
        ])
        self.assets_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.assets_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Fixed)
        self.assets_table.setColumnWidth(5, 100)
        self.assets_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.assets_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.assets_table.verticalHeader().setVisible(False)
        layout.addWidget(self.assets_table)

        self.tabs.addTab(tab, "🏛️  الأصول")

    def refresh_assets_table(self):
        items = finance_svc.get_all_assets()
        self.assets_table.setRowCount(len(items))
        for row, a in enumerate(items):
            self.assets_table.setItem(row, 0, QTableWidgetItem(a.name or ""))
            
            cat_val = a.category.value if hasattr(a.category, 'value') else str(a.category)
            self.assets_table.setItem(row, 1, QTableWidgetItem(cat_val))
            self.assets_table.setItem(row, 2, QTableWidgetItem(str(a.acquisition_date)))
            self.assets_table.setItem(row, 3, QTableWidgetItem(f"{a.depreciation_months} شهر"))
            
            own_val = a.ownership.value if hasattr(a.ownership, 'value') else str(a.ownership)
            self.assets_table.setItem(row, 4, QTableWidgetItem(own_val))

            # Actions
            actions = QWidget()
            actions_layout = QHBoxLayout(actions)
            actions_layout.setContentsMargins(4, 4, 4, 4)
            actions_layout.setSpacing(4)

            # Edit
            edit_btn = create_button("✏️", BUTTON_GHOST)
            edit_btn.setFixedSize(32, 32)
            edit_btn.clicked.connect(lambda _, aid=a.id: self._edit_asset(aid))
            actions_layout.addWidget(edit_btn)

            # Delete
            del_btn = create_danger_button("🗑️")
            del_btn.setFixedSize(32, 32)
            del_btn.clicked.connect(lambda _, aid=a.id, name=a.name: self._delete_asset(aid, name))
            actions_layout.addWidget(del_btn)

            self.assets_table.setCellWidget(row, 5, actions)
            self.assets_table.setRowHeight(row, 48)

    def _add_asset(self):
        dialog = AssetDialog(parent=self)
        if dialog.exec_() == QDialog.Accepted and dialog.result_data:
            finance_svc.create_asset(dialog.result_data)
            self.refresh_assets_table()

    def _edit_asset(self, asset_id: int):
        target = None
        for item in finance_svc.get_all_assets():
            if item.id == asset_id:
                target = item
                break
        if not target: return
        
        dialog = AssetDialog(asset=target, parent=self)
        if dialog.exec_() == QDialog.Accepted and dialog.result_data:
            finance_svc.update_asset(asset_id, dialog.result_data)
            self.refresh_assets_table()

    def _delete_asset(self, asset_id: int, name: str):
        if confirm_delete(self, name):
            finance_svc.delete_asset(asset_id)
            self.refresh_assets_table()

    # ── 7.6 Cash Register Tab Setup ──
    def _setup_register_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        layout.addWidget(QLabel("سجل الحركات الجارية وتدفق السيولة (الخزينة والبنك)"))

        self.register_table = QTableWidget()
        self.register_table.setColumnCount(6)
        self.register_table.setHorizontalHeaderLabels([
            "الحساب", "الحركة", "المبلغ", "البيان / الحركة", "الرصيد بعدها", "التاريخ"
        ])
        self.register_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.register_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.register_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.register_table.verticalHeader().setVisible(False)
        layout.addWidget(self.register_table)

        self.tabs.addTab(tab, "💳  الخزينة والبنك")

    def refresh_register_table(self):
        items = finance_svc.get_all_logs = finance_svc.get_all_cash_logs()
        self.register_table.setRowCount(len(items))
        for row, r in enumerate(items):
            reg_val = "خزينة نقدية (CASH)" if r.register_type == RegisterType.CASH else "حساب مصرفي (BANK)"
            self.register_table.setItem(row, 0, QTableWidgetItem(reg_val))
            
            tx_val = "🟢 إيداع (+)" if r.transaction_type == "in" else "🔴 سحب (-)"
            self.register_table.setItem(row, 1, QTableWidgetItem(tx_val))
            
            self.register_table.setItem(row, 2, QTableWidgetItem(f"{r.amount:.2f} LYD"))
            self.register_table.setItem(row, 3, QTableWidgetItem(r.description or ""))
            self.register_table.setItem(row, 4, QTableWidgetItem(f"{r.balance_after:.2f} LYD"))
            self.register_table.setItem(row, 5, QTableWidgetItem(r.created_at.strftime('%Y-%m-%d %H:%M') if r.created_at else ""))
            self.register_table.setRowHeight(row, 40)

    # ── 7.7 Reports Tab Setup ──
    def _setup_reports_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        title_grp = QGroupBox("الأرصدة الحالية في الحسابات")
        title_layout = QFormLayout(title_grp)
        title_layout.setLabelAlignment(Qt.AlignRight)
        
        self.cash_balance_lbl = QLabel("0.00 LYD")
        self.cash_balance_lbl.setFont(QFont(FONTS["body"].split(",")[0], FONT_SIZES["body"], QFont.Bold))
        self.cash_balance_lbl.setStyleSheet(f"color: {COLORS['accent']};")
        title_layout.addRow("رصيد الخزينة النقدية (CASH):", self.cash_balance_lbl)
        
        self.bank_balance_lbl = QLabel("0.00 LYD")
        self.bank_balance_lbl.setFont(QFont(FONTS["body"].split(",")[0], FONT_SIZES["body"], QFont.Bold))
        self.bank_balance_lbl.setStyleSheet(f"color: {COLORS['accent']};")
        title_layout.addRow("رصيد الحساب المصرفي (BANK):", self.bank_balance_lbl)
        
        layout.addWidget(title_grp)
        
        # Reports Generator Action
        rep_grp = QGroupBox("أدوات وتصدير التقارير المالية")
        rep_layout = QVBoxLayout(rep_grp)
        
        rep_layout.addWidget(QLabel("يمكنك توليد وتصدير كشف حساب شامل لأرباح ومصروفات المركز خلال الفترات المحددة:"))
        
        h_btn = QHBoxLayout()
        m_btn = create_button("📊 توليد تقرير الإيرادات والربحية الحالي", BUTTON_PRIMARY)
        m_btn.clicked.connect(self._generate_custom_report)
        h_btn.addWidget(m_btn)
        
        rep_layout.addLayout(h_btn)
        layout.addWidget(rep_grp)
        layout.addStretch()

        self.tabs.addTab(tab, "📈  التحليل والتقارير")

    def refresh_reports_info(self):
        c_bal = finance_svc.get_cash_balance()
        b_bal = finance_svc.get_bank_balance()
        self.cash_balance_lbl.setText(f"{c_bal:.2f} LYD")
        self.bank_balance_lbl.setText(f"{b_bal:.2f} LYD")

    def _generate_custom_report(self):
        c_bal = finance_svc.get_cash_balance()
        b_bal = finance_svc.get_bank_balance()
        total_rev = Decimal("0.00")
        total_exp = Decimal("0.00")
        
        # Calculate sum
        logs = finance_svc.get_all_cash_logs()
        for log in logs:
            if log.transaction_type == "in":
                total_rev += log.amount
            else:
                total_exp += log.amount
                
        QMessageBox.information(
            self, "التقرير المالي الفوري",
            f"إحصاءات المركز الحالية:\n\n"
            f"إجمالي الإيرادات المقبوضة: {total_rev:.2f} LYD\n"
            f"إجمالي المصروفات المدفوعة: {total_exp:.2f} LYD\n"
            f"صافي السيولة النقدية: {total_rev - total_exp:.2f} LYD\n\n"
            f"رصيد الخزينة: {c_bal:.2f} LYD\n"
            f"رصيد البنك: {b_bal:.2f} LYD"
        )
