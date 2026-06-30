"""
Client management form — شاشة إدارة العملاء.
جدول عرض + نموذج إضافة/تعديل مع حقول ديناميكية حسب نوع العميل.
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QDialog,
    QFormLayout, QComboBox, QTextEdit, QDoubleSpinBox,
    QFrame, QAbstractItemView, QGroupBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from ui.styles import COLORS, FONTS, FONT_SIZES, SPACING
from ui.button_utils import (
    create_button, create_danger_button, confirm_delete,
    BUTTON_PRIMARY, BUTTON_GHOST
)

import services.client_service as client_svc
from models.enums import ClientType, PaymentMethod, SectorType


class ClientDialog(QDialog):
    """نافذة إضافة/تعديل عميل — حقول ديناميكية حسب النوع."""

    def __init__(self, client=None, parent=None):
        super().__init__(parent)
        self.client = client
        self.result_data = None
        self.setWindowTitle("تعديل عميل" if client else "إضافة عميل جديد")
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

        # Common fields
        form = QFormLayout()
        form.setSpacing(SPACING["sm"])
        form.setLabelAlignment(Qt.AlignRight)

        # Client type
        self.type_combo = QComboBox()
        for ct in ClientType:
            self.type_combo.addItem(ct.value, ct)
        self.type_combo.currentIndexChanged.connect(self._on_type_changed)
        form.addRow("نوع العميل *:", self.type_combo)

        # Name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("اسم العميل أو المؤسسة")
        form.addRow("الاسم *:", self.name_input)

        # Phone
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("09XXXXXXXX")
        form.addRow("الهاتف:", self.phone_input)

        # Email
        self.email_input = QLineEdit()
        form.addRow("البريد:", self.email_input)

        # Payment method
        self.payment_combo = QComboBox()
        self.payment_combo.addItem("-- اختر --", None)
        for pm in PaymentMethod:
            self.payment_combo.addItem(pm.value, pm)
        form.addRow("طريقة الدفع:", self.payment_combo)

        # Address
        self.address_input = QTextEdit()
        self.address_input.setMaximumHeight(60)
        form.addRow("العنوان:", self.address_input)

        layout.addLayout(form)

        # Institution-specific group
        self.institution_group = QGroupBox("بيانات المؤسسة")
        inst_form = QFormLayout(self.institution_group)
        inst_form.setSpacing(SPACING["sm"])
        inst_form.setLabelAlignment(Qt.AlignRight)

        self.sector_combo = QComboBox()
        self.sector_combo.addItem("-- اختر --", None)
        for st in SectorType:
            self.sector_combo.addItem(st.value, st)
        inst_form.addRow("القطاع:", self.sector_combo)

        self.project_name_input = QLineEdit()
        self.project_name_input.setPlaceholderText("اسم المشروع")
        inst_form.addRow("المشروع:", self.project_name_input)

        self.project_summary_input = QTextEdit()
        self.project_summary_input.setMaximumHeight(60)
        inst_form.addRow("ملخص المشروع:", self.project_summary_input)

        self.contract_value_input = QDoubleSpinBox()
        self.contract_value_input.setRange(0, 999999999)
        self.contract_value_input.setDecimals(2)
        self.contract_value_input.setSuffix(" LYD")
        inst_form.addRow("قيمة العقد:", self.contract_value_input)

        self.roles_input = QTextEdit()
        self.roles_input.setMaximumHeight(60)
        self.roles_input.setPlaceholderText("توزيع الأدوار")
        inst_form.addRow("توزيع الأدوار:", self.roles_input)

        layout.addWidget(self.institution_group)

        # Pre-fill
        if self.client:
            self._prefill()
        
        self._on_type_changed()

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

    def _on_type_changed(self):
        """Show/hide institution fields based on client type."""
        ct = self.type_combo.currentData()
        show = ct in (ClientType.INSTITUTION, ClientType.PARTNERSHIP)
        self.institution_group.setVisible(show)

    def _prefill(self):
        c = self.client
        self.name_input.setText(c.name or "")
        self.phone_input.setText(c.phone or "")
        self.email_input.setText(c.email or "")
        self.address_input.setPlainText(c.address or "")

        # Set type combo
        for i in range(self.type_combo.count()):
            if self.type_combo.itemData(i) and self.type_combo.itemData(i).value == c.client_type:
                self.type_combo.setCurrentIndex(i)
                break

        if c.payment_method:
            for i in range(self.payment_combo.count()):
                data = self.payment_combo.itemData(i)
                if data and data.value == c.payment_method:
                    self.payment_combo.setCurrentIndex(i)
                    break

        # Institution fields
        if c.sector:
            for i in range(self.sector_combo.count()):
                data = self.sector_combo.itemData(i)
                if data and data.value == c.sector:
                    self.sector_combo.setCurrentIndex(i)
                    break

        self.project_name_input.setText(c.project_name or "")
        self.project_summary_input.setPlainText(c.project_summary or "")
        if c.contract_value:
            self.contract_value_input.setValue(float(c.contract_value))
        self.roles_input.setPlainText(c.roles_distribution or "")

    def _save(self):
        name = self.name_input.text().strip()
        ct = self.type_combo.currentData()
        
        if not name:
            self.name_input.setFocus()
            return

        pm = self.payment_combo.currentData()
        sector = self.sector_combo.currentData()

        self.result_data = {
            "client_type": ct.value if ct else ClientType.INDIVIDUAL.value,
            "name": name,
            "phone": self.phone_input.text().strip() or None,
            "email": self.email_input.text().strip() or None,
            "address": self.address_input.toPlainText().strip() or None,
            "payment_method": pm.value if pm else None,
        }

        # Institution fields
        if ct in (ClientType.INSTITUTION, ClientType.PARTNERSHIP):
            self.result_data.update({
                "sector": sector.value if sector else None,
                "project_name": self.project_name_input.text().strip() or None,
                "project_summary": self.project_summary_input.toPlainText().strip() or None,
                "contract_value": self.contract_value_input.value() if self.contract_value_input.value() > 0 else None,
                "roles_distribution": self.roles_input.toPlainText().strip() or None,
            })

        self.accept()


class ClientForm(QWidget):
    """شاشة إدارة العملاء — جدول + أزرار CRUD."""

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

        title = QLabel("🏢  إدارة العملاء")
        title.setFont(QFont(FONTS["display"].split(",")[0], FONT_SIZES["h2"], QFont.Bold))
        title.setStyleSheet(f"color: {COLORS['text_primary']}; background: transparent;")
        header.addWidget(title)
        header.addStretch()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 بحث عن عميل...")
        self.search_input.setFixedWidth(250)
        self.search_input.textChanged.connect(self._on_search)
        header.addWidget(self.search_input)

        add_btn = create_button("➕  إضافة عميل", BUTTON_PRIMARY)
        add_btn.clicked.connect(self._add_client)
        header.addWidget(add_btn)

        layout.addLayout(header)

        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background-color: {COLORS['border']};")
        layout.addWidget(sep)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "الاسم", "النوع", "الهاتف", "البريد",
            "القطاع", "طريقة الدفع", "إجراءات"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(6, QHeaderView.Fixed)
        self.table.setColumnWidth(6, 180)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table)

    def refresh_table(self):
        clients = client_svc.get_all_clients()
        self.table.setRowCount(len(clients))

        for row, cl in enumerate(clients):
            self.table.setItem(row, 0, QTableWidgetItem(cl.name or ""))
            self.table.setItem(row, 1, QTableWidgetItem(
                cl.client_type if isinstance(cl.client_type, str)
                else (cl.client_type.value if cl.client_type else "")
            ))
            self.table.setItem(row, 2, QTableWidgetItem(cl.phone or ""))
            self.table.setItem(row, 3, QTableWidgetItem(cl.email or ""))
            self.table.setItem(row, 4, QTableWidgetItem(
                cl.sector if isinstance(cl.sector, str)
                else (cl.sector.value if cl.sector else "")
            ))
            self.table.setItem(row, 5, QTableWidgetItem(
                cl.payment_method if isinstance(cl.payment_method, str)
                else (cl.payment_method.value if cl.payment_method else "")
            ))

            # Actions
            actions = QWidget()
            actions_layout = QHBoxLayout(actions)
            actions_layout.setContentsMargins(4, 4, 4, 4)
            actions_layout.setSpacing(4)

            profile_btn = create_button("📂", BUTTON_GHOST)
            profile_btn.setFixedSize(36, 32)
            profile_btn.setToolTip("عرض ملف العميل")
            profile_btn.clicked.connect(lambda _, c_obj=cl: self._view_client_profile(c_obj))
            actions_layout.addWidget(profile_btn)

            edit_btn = create_button("✏️", BUTTON_GHOST)
            edit_btn.setFixedSize(36, 32)
            edit_btn.clicked.connect(lambda _, cid=cl.id: self._edit_client(cid))
            actions_layout.addWidget(edit_btn)

            del_btn = create_danger_button("🗑️")
            del_btn.setFixedSize(36, 32)
            del_btn.clicked.connect(lambda _, cid=cl.id, cname=cl.name: self._delete_client(cid, cname))
            actions_layout.addWidget(del_btn)

            self.table.setCellWidget(row, 6, actions)
            self.table.setRowHeight(row, 48)

    def _on_search(self, text: str):
        if text.strip():
            clients = client_svc.search_clients(text.strip())
        else:
            clients = client_svc.get_all_clients()
        
        self.table.setRowCount(len(clients))
        for row, cl in enumerate(clients):
            self.table.setItem(row, 0, QTableWidgetItem(cl.name or ""))
            self.table.setItem(row, 1, QTableWidgetItem(
                cl.client_type if isinstance(cl.client_type, str)
                else (cl.client_type.value if cl.client_type else "")
            ))
            self.table.setItem(row, 2, QTableWidgetItem(cl.phone or ""))
            self.table.setItem(row, 3, QTableWidgetItem(cl.email or ""))
            self.table.setRowHeight(row, 48)

    def _add_client(self):
        dialog = ClientDialog(parent=self)
        if dialog.exec_() == QDialog.Accepted and dialog.result_data:
            try:
                client_svc.create_client(dialog.result_data)
                self.refresh_table()
            except Exception as e:
                print(f"Error creating client: {e}")

    def _edit_client(self, client_id: int):
        client = client_svc.get_client_by_id(client_id)
        if not client:
            return
        dialog = ClientDialog(client=client, parent=self)
        if dialog.exec_() == QDialog.Accepted and dialog.result_data:
            try:
                client_svc.update_client(client_id, dialog.result_data)
                self.refresh_table()
            except Exception as e:
                print(f"Error updating client: {e}")

    def _delete_client(self, client_id: int, name: str):
        if confirm_delete(self, name):
            client_svc.soft_delete_client(client_id)
            self.refresh_table()

    def _view_client_profile(self, client):
        from ui.dialogs.client_profile_dialog import ClientProfileDialog
        dialog = ClientProfileDialog(client, parent=self)
        dialog.exec_()
