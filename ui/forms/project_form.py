"""
Project Form — شاشة إدارة المشاريع والعقود والشركاء وتحليلات الـ AI.
تجمع تبويبات المشاريع، العقود، الشركاء، وتقارير الـ AI Insights.
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QDialog,
    QFormLayout, QTextEdit, QFrame, QAbstractItemView, QComboBox,
    QSpinBox, QDoubleSpinBox, QDateEdit, QTabWidget, QMessageBox,
    QProgressBar, QGroupBox
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont, QColor

from ui.styles import COLORS, FONTS, FONT_SIZES, SPACING
from ui.button_utils import (
    create_button, create_danger_button, confirm_delete,
    BUTTON_PRIMARY, BUTTON_SECONDARY, BUTTON_GHOST
)

import services.project_service as project_svc
import services.contract_service as contract_svc
import services.partner_service as partner_svc
import services.client_service as client_svc
import services.ai_report_service as ai_svc
import core.exporter as exporter

from models.enums import ContractStatus, PartnerType


# ─── 1. Project Dialog ───────────────────────────────────────────────────────

class ProjectDialog(QDialog):
    def __init__(self, project=None, parent=None):
        super().__init__(parent)
        self.project = project
        self.result_data = None
        self.setWindowTitle("تعديل مشروع" if project else "إضافة مشروع جديد")
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
        form.addRow("اسم المشروع *:", self.name_input)

        self.num_input = QLineEdit()
        self.num_input.setPlaceholderText("مثال: PROJ-2026-0001")
        form.addRow("رقم المشروع (اختياري):", self.num_input)
        
        self.scope_input = QLineEdit()
        self.scope_input.setPlaceholderText("مثال: طرابلس / بلديات المنطقة الغربية")
        form.addRow("النطاق الجغرافي للمشروع:", self.scope_input)

        # Dates
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate())
        self.start_date.setDisplayFormat("yyyy-MM-dd")
        form.addRow("تاريخ بدء المشروع:", self.start_date)

        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate().addMonths(12))
        self.end_date.setDisplayFormat("yyyy-MM-dd")
        form.addRow("تاريخ نهاية المشروع:", self.end_date)

        # Budget
        self.budget_input = QDoubleSpinBox()
        self.budget_input.setRange(0, 999999999)
        self.budget_input.setSuffix(" LYD")
        form.addRow("إجمالي قيمة المشروع الكلية:", self.budget_input)

        self.allocated_input = QDoubleSpinBox()
        self.allocated_input.setRange(0, 999999999)
        self.allocated_input.setSuffix(" LYD")
        form.addRow("الميزانية المرصودة للمصاريف:", self.allocated_input)

        self.status_combo = QComboBox()
        self.status_combo.addItems(["نشط", "مكتمل", "معلّق"])
        form.addRow("حالة المشروع:", self.status_combo)

        self.description = QTextEdit()
        self.description.setMaximumHeight(60)
        form.addRow("شرح ووصف المشروع:", self.description)

        layout.addLayout(form)

        if self.project:
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
        p = self.project
        self.name_input.setText(p.name or "")
        self.num_input.setText(p.project_number or "")
        self.scope_input.setText(p.geographic_scope or "")
        self.description.setPlainText(p.description or "")
        if p.budget: self.budget_input.setValue(float(p.budget))
        if p.budget_allocated: self.allocated_input.setValue(float(p.budget_allocated))
        
        if p.start_date: self.start_date.setDate(QDate(p.start_date.year, p.start_date.month, p.start_date.day))
        if p.end_date: self.end_date.setDate(QDate(p.end_date.year, p.end_date.month, p.end_date.day))
        
        self.status_combo.setCurrentText(p.status or "نشط")

    def _save(self):
        name = self.name_input.text().strip()
        if not name:
            self.name_input.setFocus()
            return
            
        self.result_data = {
            "name": name,
            "project_number": self.num_input.text().strip() or None,
            "geographic_scope": self.scope_input.text().strip() or None,
            "start_date": self.start_date.date().toPyDate(),
            "end_date": self.end_date.date().toPyDate(),
            "budget": self.budget_input.value() if self.budget_input.value() > 0 else None,
            "budget_allocated": self.allocated_input.value() if self.allocated_input.value() > 0 else None,
            "status": self.status_combo.currentText(),
            "description": self.description.toPlainText().strip() or None
        }
        self.accept()


# ─── 2. Contract Dialog ──────────────────────────────────────────────────────

class ContractDialog(QDialog):
    def __init__(self, contract=None, parent=None):
        super().__init__(parent)
        self.contract = contract
        self.result_data = None
        self.setWindowTitle("تعديل عقد" if contract else "إضافة عقد جديد")
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
        
        self.title_input = QLineEdit()
        form.addRow("عنوان العقد *:", self.title_input)

        # Clients
        self.client_combo = QComboBox()
        for cl in client_svc.get_all_clients():
            self.client_combo.addItem(cl.name, cl.id)
        form.addRow("الطرف الثاني (العميل) *:", self.client_combo)

        # Project link
        self.proj_combo = QComboBox()
        self.proj_combo.addItem("غير مرتبط بمشروع محدد", None)
        for pr in project_svc.get_all_projects():
            self.proj_combo.addItem(pr.name, pr.id)
        form.addRow("ربطه بمشروع:", self.proj_combo)

        # Value
        self.value_input = QDoubleSpinBox()
        self.value_input.setRange(0.01, 999999999)
        self.value_input.setSuffix(" LYD")
        form.addRow("قيمة العقد المالية *:", self.value_input)

        # Dates
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate())
        self.start_date.setDisplayFormat("yyyy-MM-dd")
        form.addRow("تاريخ سريان العقد:", self.start_date)

        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate().addMonths(6))
        self.end_date.setDisplayFormat("yyyy-MM-dd")
        form.addRow("تاريخ انتهاء العقد:", self.end_date)

        # Status
        self.status_combo = QComboBox()
        for cs in ContractStatus:
            self.status_combo.addItem(cs.value, cs)
        form.addRow("حالة العقد:", self.status_combo)

        # Details
        self.scope = QTextEdit()
        self.scope.setMaximumHeight(50)
        form.addRow("مجال العمل:", self.scope)

        self.clauses = QTextEdit()
        self.clauses.setMaximumHeight(60)
        from models.contract import Contract
        self.clauses.setPlainText(Contract.DEFAULT_CLAUSES)
        form.addRow("الشروط والبنود الجزائية:", self.clauses)

        layout.addLayout(form)

        if self.contract:
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
        c = self.contract
        self.title_input.setText(c.title or "")
        self.scope.setPlainText(c.scope or "")
        self.clauses.setPlainText(c.clauses or "")
        self.value_input.setValue(float(c.value))
        
        idx = self.client_combo.findData(c.client_id)
        if idx >= 0: self.client_combo.setCurrentIndex(idx)
        
        idx_p = self.proj_combo.findData(c.project_id)
        if idx_p >= 0: self.proj_combo.setCurrentIndex(idx_p)
        
        if c.start_date: self.start_date.setDate(QDate(c.start_date.year, c.start_date.month, c.start_date.day))
        if c.end_date: self.end_date.setDate(QDate(c.end_date.year, c.end_date.month, c.end_date.day))
        
        for idx in range(self.status_combo.count()):
            if self.status_combo.itemData(idx) == c.status:
                self.status_combo.setCurrentIndex(idx)
                break

    def _save(self):
        title = self.title_input.text().strip()
        if not title:
            self.title_input.setFocus()
            return
            
        self.result_data = {
            "title": title,
            "client_id": self.client_combo.currentData(),
            "project_id": self.proj_combo.currentData(),
            "value": self.value_input.value(),
            "start_date": self.start_date.date().toPyDate(),
            "end_date": self.end_date.date().toPyDate(),
            "status": self.status_combo.currentData(),
            "scope": self.scope.toPlainText().strip() or None,
            "clauses": self.clauses.toPlainText().strip() or None
        }
        self.accept()


# ─── 3. Partner Dialog ───────────────────────────────────────────────────────

class PartnerDialog(QDialog):
    def __init__(self, partner=None, parent=None):
        super().__init__(parent)
        self.partner = partner
        self.result_data = None
        self.setWindowTitle("تعديل شريك" if partner else "إضافة شريك جديد")
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
        
        self.name_input = QLineEdit()
        form.addRow("اسم الشريك / الجهة *:", self.name_input)

        self.type_combo = QComboBox()
        for pt in PartnerType:
            self.type_combo.addItem(pt.value, pt)
        form.addRow("التصنيف:", self.type_combo)

        self.phone_input = QLineEdit()
        form.addRow("الهاتف:", self.phone_input)

        self.email_input = QLineEdit()
        form.addRow("البريد الإلكتروني:", self.email_input)

        self.contribution = QTextEdit()
        self.contribution.setMaximumHeight(60)
        form.addRow("طبيعة المساهمة:", self.contribution)

        layout.addLayout(form)

        if self.partner:
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
        p = self.partner
        self.name_input.setText(p.name or "")
        self.phone_input.setText(p.phone or "")
        self.email_input.setText(p.email or "")
        self.contribution.setPlainText(p.contribution_details or "")
        
        for idx in range(self.type_combo.count()):
            if self.type_combo.itemData(idx) == p.type:
                self.type_combo.setCurrentIndex(idx)
                break

    def _save(self):
        name = self.name_input.text().strip()
        if not name:
            self.name_input.setFocus()
            return
            
        self.result_data = {
            "name": name,
            "type": self.type_combo.currentData(),
            "phone": self.phone_input.text().strip() or None,
            "email": self.email_input.text().strip() or None,
            "contribution_details": self.contribution.toPlainText().strip() or None
        }
        self.accept()


# ─── 4. Project Panel UI (Main TabWidget) ────────────────────────────────────

class ProjectForm(QWidget):
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
        title = QLabel("📋  إدارة المشاريع والعقود")
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

        # Setup Tabs
        self._setup_projects_tab()
        self._setup_contracts_tab()
        self._setup_partners_tab()
        self._setup_ai_tab()

        main_layout.addWidget(self.tabs)

    def refresh_all_data(self):
        self.refresh_projects_table()
        self.refresh_contracts_table()
        self.refresh_partners_table()

    # ── 4.1 Projects Tab Setup ──
    def _setup_projects_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        hdr = QHBoxLayout()
        hdr.addWidget(QLabel("تتبع موازنات ونسب استهلاك ميزانيات المشاريع الجارية"))
        hdr.addStretch()
        add_btn = create_button("➕ مشروع جديد", BUTTON_PRIMARY)
        add_btn.clicked.connect(self._add_project)
        hdr.addWidget(add_btn)
        layout.addLayout(hdr)

        self.projects_table = QTableWidget()
        self.projects_table.setColumnCount(8)
        self.projects_table.setHorizontalHeaderLabels([
            "رقم المشروع", "اسم المشروع", "النطاق الجغرافي", "الميزانية المخصصة", "المصروف الفعلي", "الحالة", "نسبة الاستهلاك", "إجراءات"
        ])
        self.projects_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.projects_table.horizontalHeader().setSectionResizeMode(7, QHeaderView.Fixed)
        self.projects_table.setColumnWidth(7, 100)
        self.projects_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.projects_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.projects_table.verticalHeader().setVisible(False)
        layout.addWidget(self.projects_table)

        self.tabs.addTab(tab, "📋  المشاريع الجارية")

    def refresh_projects_table(self):
        items = project_svc.get_all_projects()
        self.projects_table.setRowCount(len(items))
        for row, p in enumerate(items):
            self.projects_table.setItem(row, 0, QTableWidgetItem(p.project_number or ""))
            self.projects_table.setItem(row, 1, QTableWidgetItem(p.name or ""))
            self.projects_table.setItem(row, 2, QTableWidgetItem(p.geographic_scope or "عام"))
            
            allocated = p.budget_allocated or p.budget or 0
            self.projects_table.setItem(row, 3, QTableWidgetItem(f"{allocated:.2f} LYD"))
            
            spent = p.budget_spent or 0
            self.projects_table.setItem(row, 4, QTableWidgetItem(f"{spent:.2f} LYD"))
            self.projects_table.setItem(row, 5, QTableWidgetItem(p.status or "نشط"))
            
            # Progress Bar widget
            ratio = (float(spent) / float(allocated) * 100) if allocated > 0 else 0
            progress = QProgressBar()
            progress.setRange(0, 100)
            progress.setValue(int(min(ratio, 100)))
            progress.setAlignment(Qt.AlignCenter)
            progress.setStyleSheet("""
                QProgressBar {
                    border: 1px solid rgba(0, 0, 0, 0.1);
                    border-radius: 5px;
                    text-align: center;
                    background-color: #f1f5f9;
                }
                QProgressBar::chunk {
                    background-color: #12735C;
                    border-radius: 4px;
                }
            """)
            self.projects_table.setCellWidget(row, 6, progress)

            # Actions
            actions = QWidget()
            actions_layout = QHBoxLayout(actions)
            actions_layout.setContentsMargins(4, 4, 4, 4)
            actions_layout.setSpacing(4)

            edit_btn = create_button("✏️", BUTTON_GHOST)
            edit_btn.setFixedSize(32, 32)
            edit_btn.clicked.connect(lambda _, pid=p.id: self._edit_project(pid))
            actions_layout.addWidget(edit_btn)

            del_btn = create_danger_button("🗑️")
            del_btn.setFixedSize(32, 32)
            del_btn.clicked.connect(lambda _, pid=p.id, name=p.name: self._delete_project(pid, name))
            actions_layout.addWidget(del_btn)

            self.projects_table.setCellWidget(row, 7, actions)
            self.projects_table.setRowHeight(row, 48)

    def _add_project(self):
        dialog = ProjectDialog(parent=self)
        if dialog.exec_() == QDialog.Accepted and dialog.result_data:
            # Generate sequential project number if none provided
            year = QDate.currentDate().year()
            if not dialog.result_data.get("project_number"):
                # Simulating count
                count = len(project_svc.get_all_projects()) + 1
                dialog.result_data["project_number"] = f"PROJ-{year}-{count:04d}"
            project_svc.create_project(dialog.result_data)
            self.refresh_projects_table()

    def _edit_project(self, project_id: int):
        p = project_svc.get_project_by_id(project_id)
        if not p: return
        dialog = ProjectDialog(project=p, parent=self)
        if dialog.exec_() == QDialog.Accepted and dialog.result_data:
            project_svc.update_project(project_id, dialog.result_data)
            self.refresh_projects_table()

    def _delete_project(self, project_id: int, name: str):
        if confirm_delete(self, name):
            project_svc.soft_delete_project(project_id)
            self.refresh_projects_table()

    # ── 4.2 Contracts Tab Setup ──
    def _setup_contracts_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        hdr = QHBoxLayout()
        hdr.addWidget(QLabel("إدارة العقود القانونية والمالية المبرمة مع الجهات الخارجية"))
        hdr.addStretch()
        add_btn = create_button("➕ عقد جديد", BUTTON_PRIMARY)
        add_btn.clicked.connect(self._add_contract)
        hdr.addWidget(add_btn)
        layout.addLayout(hdr)

        self.contracts_table = QTableWidget()
        self.contracts_table.setColumnCount(7)
        self.contracts_table.setHorizontalHeaderLabels([
            "عنوان العقد", "العميل", "المشروع المرتبط", "قيمة العقد", "الحالة", "فترة سريان العقد", "إجراءات"
        ])
        self.contracts_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.contracts_table.horizontalHeader().setSectionResizeMode(6, QHeaderView.Fixed)
        self.contracts_table.setColumnWidth(6, 100)
        self.contracts_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.contracts_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.contracts_table.verticalHeader().setVisible(False)
        layout.addWidget(self.contracts_table)

        self.tabs.addTab(tab, "📜  العقود والاتفاقيات")

    def refresh_contracts_table(self):
        items = contract_svc.get_all_contracts()
        self.contracts_table.setRowCount(len(items))
        for row, c in enumerate(items):
            self.contracts_table.setItem(row, 0, QTableWidgetItem(c.title or ""))
            self.contracts_table.setItem(row, 1, QTableWidgetItem(c.client.name if c.client else "N/A"))
            self.contracts_table.setItem(row, 2, QTableWidgetItem(c.project.name if c.project else "غير مرتبط"))
            self.contracts_table.setItem(row, 3, QTableWidgetItem(f"{c.value:.2f} LYD"))
            
            status_val = c.status.value if hasattr(c.status, 'value') else str(c.status)
            self.contracts_table.setItem(row, 4, QTableWidgetItem(status_val))
            self.contracts_table.setItem(row, 5, QTableWidgetItem(f"{c.start_date} إلى {c.end_date}"))

            # Actions
            actions = QWidget()
            actions_layout = QHBoxLayout(actions)
            actions_layout.setContentsMargins(4, 4, 4, 4)
            actions_layout.setSpacing(4)

            edit_btn = create_button("✏️", BUTTON_GHOST)
            edit_btn.setFixedSize(32, 32)
            edit_btn.clicked.connect(lambda _, cid=c.id: self._edit_contract(cid))
            actions_layout.addWidget(edit_btn)

            del_btn = create_danger_button("🗑️")
            del_btn.setFixedSize(32, 32)
            del_btn.clicked.connect(lambda _, cid=c.id, name=c.title: self._delete_contract(cid, name))
            actions_layout.addWidget(del_btn)

            self.contracts_table.setCellWidget(row, 6, actions)
            self.contracts_table.setRowHeight(row, 48)

    def _add_contract(self):
        dialog = ContractDialog(parent=self)
        if dialog.exec_() == QDialog.Accepted and dialog.result_data:
            contract_svc.create_contract(dialog.result_data)
            self.refresh_contracts_table()

    def _edit_contract(self, contract_id: int):
        c = contract_svc.get_contract_by_id(contract_id)
        if not c: return
        dialog = ContractDialog(contract=c, parent=self)
        if dialog.exec_() == QDialog.Accepted and dialog.result_data:
            contract_svc.update_contract(contract_id, dialog.result_data)
            self.refresh_contracts_table()

    def _delete_contract(self, contract_id: int, name: str):
        if confirm_delete(self, name):
            contract_svc.soft_delete_contract(contract_id)
            self.refresh_contracts_table()

    # ── 4.3 Partners Tab Setup ──
    def _setup_partners_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        hdr = QHBoxLayout()
        hdr.addWidget(QLabel("إدارة بيانات الشركاء المساهمين والممولين محلياً ودولياً"))
        hdr.addStretch()
        add_btn = create_button("➕ شريك جديد", BUTTON_PRIMARY)
        add_btn.clicked.connect(self._add_partner)
        hdr.addWidget(add_btn)
        layout.addLayout(hdr)

        self.partners_table = QTableWidget()
        self.partners_table.setColumnCount(5)
        self.partners_table.setHorizontalHeaderLabels([
            "اسم الشريك", "التصنيف", "الهاتف", "البريد الإلكتروني", "إجراءات"
        ])
        self.partners_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.partners_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Fixed)
        self.partners_table.setColumnWidth(4, 100)
        self.partners_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.partners_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.partners_table.verticalHeader().setVisible(False)
        layout.addWidget(self.partners_table)

        self.tabs.addTab(tab, "🤝  شركاء التمويل")

    def refresh_partners_table(self):
        items = partner_svc.get_all_partners()
        self.partners_table.setRowCount(len(items))
        for row, p in enumerate(items):
            self.partners_table.setItem(row, 0, QTableWidgetItem(p.name or ""))
            
            type_val = p.type.value if hasattr(p.type, 'value') else str(p.type)
            self.partners_table.setItem(row, 1, QTableWidgetItem(type_val))
            self.partners_table.setItem(row, 2, QTableWidgetItem(p.phone or ""))
            self.partners_table.setItem(row, 3, QTableWidgetItem(p.email or ""))

            # Actions
            actions = QWidget()
            actions_layout = QHBoxLayout(actions)
            actions_layout.setContentsMargins(4, 4, 4, 4)
            actions_layout.setSpacing(4)

            edit_btn = create_button("✏️", BUTTON_GHOST)
            edit_btn.setFixedSize(32, 32)
            edit_btn.clicked.connect(lambda _, pid=p.id: self._edit_partner(pid))
            actions_layout.addWidget(edit_btn)

            del_btn = create_danger_button("🗑️")
            del_btn.setFixedSize(32, 32)
            del_btn.clicked.connect(lambda _, pid=p.id, name=p.name: self._delete_partner(pid, name))
            actions_layout.addWidget(del_btn)

            self.partners_table.setCellWidget(row, 4, actions)
            self.partners_table.setRowHeight(row, 48)

    def _add_partner(self):
        dialog = PartnerDialog(parent=self)
        if dialog.exec_() == QDialog.Accepted and dialog.result_data:
            partner_svc.create_partner(dialog.result_data)
            self.refresh_partners_table()

    def _edit_partner(self, partner_id: int):
        p = partner_svc.get_partner_by_id(partner_id)
        if not p: return
        dialog = PartnerDialog(partner=p, parent=self)
        if dialog.exec_() == QDialog.Accepted and dialog.result_data:
            partner_svc.update_partner(partner_id, dialog.result_data)
            self.refresh_partners_table()

    def _delete_partner(self, partner_id: int, name: str):
        if confirm_delete(self, name):
            partner_svc.soft_delete_partner(partner_id)
            self.refresh_partners_table()

    # ── 4.4 AI Financial Insights Tab Setup ──
    def _setup_ai_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        layout.addWidget(QLabel("تحليل الأداء الفعلي الفوري وتوقعات التدفقات النقدية والسيولة مدعوماً بمحاكاة الذكاء الاصطناعي:"))
        
        self.report_text = QTextEdit()
        self.report_text.setReadOnly(True)
        self.report_text.setFont(QFont("Courier New", FONT_SIZES["body"]))
        self.report_text.setPlaceholderText("اضغط على الزر بالأسفل لتوليد التحليل المالي الذكي...")
        self.report_text.setStyleSheet("""
            QTextEdit {
                background-color: #0f172a;
                color: #38bdf8;
                border: 1px solid #1e293b;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        layout.addWidget(self.report_text)
        
        btn_layout = QHBoxLayout()
        generate_btn = create_button("🧠 توليد التحليل المالي الذكي (AI Insights)", BUTTON_PRIMARY)
        generate_btn.clicked.connect(self._generate_ai_report)
        btn_layout.addWidget(generate_btn)
        
        export_btn = create_button("💾 تصدير التقرير الفوري", BUTTON_SECONDARY)
        export_btn.clicked.connect(self._export_ai_report)
        btn_layout.addWidget(export_btn)
        
        layout.addLayout(btn_layout)

        self.tabs.addTab(tab, "🧠  تحليلات الذكاء الاصطناعي")

    def _generate_ai_report(self):
        report = ai_svc.generate_ai_financial_report()
        self.report_text.setPlainText(report)
        QMessageBox.information(self, "نجاح التوليد", "تم قراءة الحسابات والموازنات وصياغة التوصيات الذكية.")

    def _export_ai_report(self):
        text_content = self.report_text.toPlainText().strip()
        if not text_content:
            QMessageBox.critical(self, "خطأ", "يجب توليد التقرير المالي أولاً قبل تصديره")
            return
            
        try:
            # We save as plain text inside exports/
            exporter.ensure_exports_dir()
            filename = f"ai_financial_insights_{QDate.currentDate().toString('yyyy_MM_dd')}.txt"
            filepath = os.path.join(exporter.EXPORTS_DIR, filename)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(text_content)
            QMessageBox.information(self, "تم التصدير", f"تم حفظ تقرير التحليل الذكي بنجاح في:\n{filepath}")
        except Exception as e:
            QMessageBox.critical(self, "خطأ تصدير", f"فشل تصدير التقرير: {e}")
