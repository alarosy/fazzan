"""
Employee management form — شاشة إدارة الموظفين.
جدول عرض + نموذج إضافة/تعديل + حذف ناعم.
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QDialog,
    QFormLayout, QDateEdit, QComboBox, QTextEdit, QDoubleSpinBox,
    QFrame, QSizePolicy, QAbstractItemView
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont

from ui.styles import COLORS, FONTS, FONT_SIZES, SPACING, BORDER_RADIUS
from ui.button_utils import (
    create_button, create_danger_button, confirm_delete,
    BUTTON_PRIMARY, BUTTON_SECONDARY, BUTTON_GHOST
)

import services.hr_service as hr_svc
from models.enums import EmploymentType, PaymentMethod


class EmployeeDialog(QDialog):
    """نافذة إضافة/تعديل موظف."""

    def __init__(self, employee=None, parent=None):
        super().__init__(parent)
        self.employee = employee
        self.result_data = None
        self.setWindowTitle("تعديل موظف" if employee else "إضافة موظف جديد")
        self.setMinimumWidth(550)
        self.setLayoutDirection(Qt.RightToLeft)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS['background']};
                color: {COLORS['text_primary']};
            }}
        """)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(SPACING["md"])
        layout.setContentsMargins(SPACING["xl"], SPACING["lg"],
                                   SPACING["xl"], SPACING["lg"])

        # Title
        title = QLabel(self.windowTitle())
        title.setFont(QFont(FONTS["display"].split(",")[0], FONT_SIZES["h2"], QFont.Bold))
        title.setStyleSheet(f"color: {COLORS['accent']}; background: transparent;")
        title.setAlignment(Qt.AlignRight)
        layout.addWidget(title)

        # Form
        form = QFormLayout()
        form.setSpacing(SPACING["sm"])
        form.setLabelAlignment(Qt.AlignRight)

        # Name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("الاسم الكامل")
        form.addRow("الاسم *:", self.name_input)

        # Phone
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("09XXXXXXXX")
        form.addRow("الهاتف:", self.phone_input)

        # Email
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("example@email.com")
        form.addRow("البريد:", self.email_input)

        # Position
        self.position_input = QLineEdit()
        self.position_input.setPlaceholderText("المسمى الوظيفي")
        form.addRow("المنصب:", self.position_input)

        # ID Number
        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("رقم الهوية")
        form.addRow("رقم الهوية:", self.id_input)

        # Employment type
        self.type_combo = QComboBox()
        self.type_combo.addItem("-- اختر --", None)
        for et in EmploymentType:
            self.type_combo.addItem(et.value, et)
        form.addRow("نوع التوظيف:", self.type_combo)

        # Payment method
        self.payment_combo = QComboBox()
        self.payment_combo.addItem("-- اختر --", None)
        for pm in PaymentMethod:
            self.payment_combo.addItem(pm.value, pm)
        form.addRow("طريقة الدفع:", self.payment_combo)

        # Daily wage
        self.wage_input = QDoubleSpinBox()
        self.wage_input.setRange(0, 9999999)
        self.wage_input.setDecimals(2)
        self.wage_input.setSuffix(" LYD")
        form.addRow("الأجر اليومي:", self.wage_input)

        # Contract dates
        self.contract_start = QDateEdit()
        self.contract_start.setCalendarPopup(True)
        self.contract_start.setDate(QDate.currentDate())
        self.contract_start.setDisplayFormat("yyyy-MM-dd")
        form.addRow("بداية العقد:", self.contract_start)

        self.contract_end = QDateEdit()
        self.contract_end.setCalendarPopup(True)
        self.contract_end.setDate(QDate.currentDate().addYears(1))
        self.contract_end.setDisplayFormat("yyyy-MM-dd")
        form.addRow("نهاية العقد:", self.contract_end)

        # Address
        self.address_input = QTextEdit()
        self.address_input.setMaximumHeight(80)
        self.address_input.setPlaceholderText("العنوان")
        form.addRow("العنوان:", self.address_input)

        layout.addLayout(form)

        # Pre-fill if editing
        if self.employee:
            self._prefill()

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(SPACING["sm"])

        cancel_btn = create_button("إلغاء", BUTTON_GHOST)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        btn_layout.addStretch()

        save_btn = create_button("حفظ", BUTTON_PRIMARY)
        save_btn.clicked.connect(self._save)
        btn_layout.addWidget(save_btn)

        layout.addLayout(btn_layout)

    def _prefill(self):
        """Fill form with existing employee data."""
        e = self.employee
        self.name_input.setText(e.name or "")
        self.phone_input.setText(e.phone or "")
        self.email_input.setText(e.email or "")
        self.position_input.setText(e.position or "")
        self.id_input.setText(e.id_number or "")
        self.address_input.setPlainText(e.address or "")

        if e.daily_wage_rate:
            self.wage_input.setValue(float(e.daily_wage_rate))

        if e.contract_start_date:
            self.contract_start.setDate(QDate(
                e.contract_start_date.year,
                e.contract_start_date.month,
                e.contract_start_date.day
            ))

        if e.contract_end_date:
            self.contract_end.setDate(QDate(
                e.contract_end_date.year,
                e.contract_end_date.month,
                e.contract_end_date.day
            ))

        # Set combo boxes
        if e.employment_type:
            for i in range(self.type_combo.count()):
                if self.type_combo.itemData(i) == e.employment_type:
                    self.type_combo.setCurrentIndex(i)
                    break

        if e.payment_method:
            for i in range(self.payment_combo.count()):
                if self.payment_combo.itemData(i) == e.payment_method:
                    self.payment_combo.setCurrentIndex(i)
                    break

    def _save(self):
        name = self.name_input.text().strip()
        if not name:
            self.name_input.setFocus()
            self.name_input.setStyleSheet(f"border: 2px solid {COLORS['danger']};")
            return

        et = self.type_combo.currentData()
        pm = self.payment_combo.currentData()

        self.result_data = {
            "name": name,
            "phone": self.phone_input.text().strip() or None,
            "email": self.email_input.text().strip() or None,
            "position": self.position_input.text().strip() or None,
            "id_number": self.id_input.text().strip() or None,
            "address": self.address_input.toPlainText().strip() or None,
            "employment_type": et.value if et else None,
            "payment_method": pm.value if pm else None,
            "daily_wage_rate": self.wage_input.value() if self.wage_input.value() > 0 else None,
            "contract_start_date": self.contract_start.date().toPyDate(),
            "contract_end_date": self.contract_end.date().toPyDate(),
        }
        self.accept()


class EmployeeForm(QWidget):
    """شاشة إدارة الموظفين — جدول + أزرار CRUD."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayoutDirection(Qt.RightToLeft)
        self._setup_ui()
        self.refresh_table()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING["xl"], SPACING["lg"],
                                   SPACING["xl"], SPACING["lg"])
        layout.setSpacing(SPACING["md"])

        # Header
        header = QHBoxLayout()

        title = QLabel("👥  إدارة الموظفين")
        title.setFont(QFont(FONTS["display"].split(",")[0], FONT_SIZES["h2"], QFont.Bold))
        title.setStyleSheet(f"color: {COLORS['text_primary']}; background: transparent;")
        header.addWidget(title)

        header.addStretch()

        # Search
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 بحث عن موظف...")
        self.search_input.setFixedWidth(250)
        self.search_input.textChanged.connect(self._on_search)
        header.addWidget(self.search_input)

        # Add button
        add_btn = create_button("➕  إضافة موظف", BUTTON_PRIMARY)
        add_btn.clicked.connect(self._add_employee)
        header.addWidget(add_btn)

        layout.addLayout(header)

        # Separator
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background-color: {COLORS['border']};")
        layout.addWidget(sep)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "الاسم", "المنصب", "الهاتف", "نوع التوظيف",
            "بداية العقد", "نهاية العقد", "الأجر اليومي", "إجراءات"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(7, QHeaderView.Fixed)
        self.table.setColumnWidth(7, 180)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table)

    def refresh_table(self):
        """تحديث جدول الموظفين من قاعدة البيانات."""
        employees = hr_svc.get_all_employees()
        self.table.setRowCount(len(employees))

        for row, emp in enumerate(employees):
            self.table.setItem(row, 0, QTableWidgetItem(emp.name or ""))
            self.table.setItem(row, 1, QTableWidgetItem(emp.position or ""))
            self.table.setItem(row, 2, QTableWidgetItem(emp.phone or ""))
            self.table.setItem(row, 3, QTableWidgetItem(
                emp.employment_type if isinstance(emp.employment_type, str)
                else (emp.employment_type.value if emp.employment_type else "")
            ))
            self.table.setItem(row, 4, QTableWidgetItem(
                str(emp.contract_start_date) if emp.contract_start_date else ""
            ))
            self.table.setItem(row, 5, QTableWidgetItem(
                str(emp.contract_end_date) if emp.contract_end_date else ""
            ))
            self.table.setItem(row, 6, QTableWidgetItem(
                f"{emp.daily_wage_rate:.2f} LYD" if emp.daily_wage_rate else ""
            ))

            # Action buttons
            actions = QWidget()
            actions_layout = QHBoxLayout(actions)
            actions_layout.setContentsMargins(4, 4, 4, 4)
            actions_layout.setSpacing(4)

            edit_btn = create_button("✏️", BUTTON_GHOST)
            edit_btn.setFixedSize(36, 32)
            edit_btn.setToolTip("تعديل")
            edit_btn.clicked.connect(lambda _, eid=emp.id: self._edit_employee(eid))
            actions_layout.addWidget(edit_btn)

            del_btn = create_danger_button("🗑️")
            del_btn.setFixedSize(36, 32)
            del_btn.setToolTip("حذف")
            del_btn.clicked.connect(lambda _, eid=emp.id, ename=emp.name: self._delete_employee(eid, ename))
            actions_layout.addWidget(del_btn)

            self.table.setCellWidget(row, 7, actions)
            self.table.setRowHeight(row, 48)

    def _on_search(self, text: str):
        """Filter table by search text."""
        if text.strip():
            employees = hr_svc.search_employees(text.strip())
        else:
            employees = hr_svc.get_all_employees()
        
        self.table.setRowCount(len(employees))
        for row, emp in enumerate(employees):
            self.table.setItem(row, 0, QTableWidgetItem(emp.name or ""))
            self.table.setItem(row, 1, QTableWidgetItem(emp.position or ""))
            self.table.setItem(row, 2, QTableWidgetItem(emp.phone or ""))
            self.table.setItem(row, 3, QTableWidgetItem(
                emp.employment_type if isinstance(emp.employment_type, str)
                else (emp.employment_type.value if emp.employment_type else "")
            ))
            self.table.setItem(row, 4, QTableWidgetItem(
                str(emp.contract_start_date) if emp.contract_start_date else ""
            ))
            self.table.setItem(row, 5, QTableWidgetItem(
                str(emp.contract_end_date) if emp.contract_end_date else ""
            ))
            self.table.setItem(row, 6, QTableWidgetItem(
                f"{emp.daily_wage_rate:.2f} LYD" if emp.daily_wage_rate else ""
            ))
            self.table.setRowHeight(row, 48)

    def _add_employee(self):
        dialog = EmployeeDialog(parent=self)
        if dialog.exec_() == QDialog.Accepted and dialog.result_data:
            try:
                hr_svc.create_employee(dialog.result_data)
                self.refresh_table()
            except Exception as e:
                print(f"Error creating employee: {e}")

    def _edit_employee(self, employee_id: int):
        employee = hr_svc.get_employee_by_id(employee_id)
        if not employee:
            return
        
        dialog = EmployeeDialog(employee=employee, parent=self)
        if dialog.exec_() == QDialog.Accepted and dialog.result_data:
            try:
                hr_svc.update_employee(employee_id, dialog.result_data)
                self.refresh_table()
            except Exception as e:
                print(f"Error updating employee: {e}")

    def _delete_employee(self, employee_id: int, name: str):
        if confirm_delete(self, name):
            hr_svc.soft_delete_employee(employee_id)
            self.refresh_table()
