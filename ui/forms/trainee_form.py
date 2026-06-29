"""
Trainee management form — شاشة إدارة المتدربين.
جدول عرض + نموذج إضافة/تعديل + حذف ناعم.
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QDialog,
    QFormLayout, QTextEdit, QFrame, QAbstractItemView, QComboBox, QDateEdit
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont

from ui.styles import COLORS, FONTS, FONT_SIZES, SPACING
from ui.button_utils import (
    create_button, create_danger_button, confirm_delete,
    BUTTON_PRIMARY, BUTTON_GHOST
)

import services.training_service as training_svc


class TraineeDialog(QDialog):
    """نافذة إضافة/تعديل متدرب."""

    def __init__(self, trainee=None, parent=None):
        super().__init__(parent)
        self.trainee = trainee
        self.result_data = None
        self.setWindowTitle("تعديل متدرب" if trainee else "إضافة متدرب جديد")
        self.setMinimumWidth(500)
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
        form.addRow("البريد:", self.email_input)

        # ID Number
        self.id_input = QLineEdit()
        form.addRow("رقم الهوية:", self.id_input)

        # Organization
        self.org_input = QLineEdit()
        self.org_input.setPlaceholderText("الجهة أو الشركة التابع لها")
        form.addRow("المؤسسة/الجهة:", self.org_input)

        # Gender
        self.gender_combo = QComboBox()
        self.gender_combo.addItems(["ذكر", "أنثى"])
        form.addRow("الجنس:", self.gender_combo)

        # Date of birth
        self.dob_input = QDateEdit()
        self.dob_input.setCalendarPopup(True)
        self.dob_input.setDate(QDate(1995, 1, 1))
        self.dob_input.setDisplayFormat("yyyy-MM-dd")
        form.addRow("تاريخ الميلاد:", self.dob_input)

        # Address
        self.address_input = QTextEdit()
        self.address_input.setMaximumHeight(60)
        form.addRow("العنوان:", self.address_input)

        # Notes
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(60)
        form.addRow("ملاحظات:", self.notes_input)

        layout.addLayout(form)

        # Pre-fill
        if self.trainee:
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
        t = self.trainee
        self.name_input.setText(t.name or "")
        self.phone_input.setText(t.phone or "")
        self.email_input.setText(t.email or "")
        self.id_input.setText(t.id_number or "")
        self.org_input.setText(t.organization or "")
        self.address_input.setPlainText(t.address or "")
        self.notes_input.setPlainText(t.notes or "")
        
        if t.gender:
            idx = self.gender_combo.findText(t.gender)
            if idx >= 0:
                self.gender_combo.setCurrentIndex(idx)
        
        if t.date_of_birth:
            self.dob_input.setDate(QDate(
                t.date_of_birth.year,
                t.date_of_birth.month,
                t.date_of_birth.day
            ))

    def _save(self):
        name = self.name_input.text().strip()
        if not name:
            self.name_input.setFocus()
            return
        
        self.result_data = {
            "name": name,
            "phone": self.phone_input.text().strip() or None,
            "email": self.email_input.text().strip() or None,
            "id_number": self.id_input.text().strip() or None,
            "organization": self.org_input.text().strip() or None,
            "gender": self.gender_combo.currentText(),
            "date_of_birth": self.dob_input.date().toPyDate(),
            "address": self.address_input.toPlainText().strip() or None,
            "notes": self.notes_input.toPlainText().strip() or None,
        }
        self.accept()


class TraineeForm(QWidget):
    """شاشة إدارة المتدربين — جدول وتحديثات."""

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
        title = QLabel("🎓  إدارة المتدربين")
        title.setFont(QFont(FONTS["display"].split(",")[0], FONT_SIZES["h2"], QFont.Bold))
        title.setStyleSheet(f"color: {COLORS['text_primary']}; background: transparent;")
        header.addWidget(title)
        header.addStretch()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 بحث عن متدرب...")
        self.search_input.setFixedWidth(250)
        self.search_input.textChanged.connect(self._on_search)
        header.addWidget(self.search_input)

        add_btn = create_button("➕  إضافة متدرب", BUTTON_PRIMARY)
        add_btn.clicked.connect(self._add_trainee)
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
            "الاسم", "الهاتف", "البريد الإلكتروني", "رقم الهوية",
            "المؤسسة/الجهة", "الجنس", "إجراءات"
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
        trainees = training_svc.get_all_trainees()
        self._populate_table(trainees)

    def _populate_table(self, trainees):
        self.table.setRowCount(len(trainees))
        for row, t in enumerate(trainees):
            self.table.setItem(row, 0, QTableWidgetItem(t.name or ""))
            self.table.setItem(row, 1, QTableWidgetItem(t.phone or ""))
            self.table.setItem(row, 2, QTableWidgetItem(t.email or ""))
            self.table.setItem(row, 3, QTableWidgetItem(t.id_number or ""))
            self.table.setItem(row, 4, QTableWidgetItem(t.organization or ""))
            self.table.setItem(row, 5, QTableWidgetItem(t.gender or ""))

            # Actions
            actions = QWidget()
            actions_layout = QHBoxLayout(actions)
            actions_layout.setContentsMargins(4, 4, 4, 4)
            actions_layout.setSpacing(4)

            edit_btn = create_button("✏️", BUTTON_GHOST)
            edit_btn.setFixedSize(36, 32)
            edit_btn.clicked.connect(lambda _, tid=t.id: self._edit_trainee(tid))
            actions_layout.addWidget(edit_btn)

            del_btn = create_danger_button("🗑️")
            del_btn.setFixedSize(36, 32)
            del_btn.clicked.connect(lambda _, tid=t.id, tname=t.name: self._delete_trainee(tid, tname))
            actions_layout.addWidget(del_btn)

            self.table.setCellWidget(row, 6, actions)
            self.table.setRowHeight(row, 48)

    def _on_search(self, text: str):
        if text.strip():
            # Filter in-memory or query partial
            trainees = training_svc.search_existing_trainees(text.strip())
        else:
            trainees = training_svc.get_all_trainees()
        self._populate_table(trainees)

    def _add_trainee(self):
        dialog = TraineeDialog(parent=self)
        if dialog.exec_() == QDialog.Accepted and dialog.result_data:
            try:
                training_svc.create_trainee(dialog.result_data)
                self.refresh_table()
            except Exception as e:
                print(f"Error creating trainee: {e}")

    def _edit_trainee(self, trainee_id: int):
        trainee = training_svc.get_trainee_by_id(trainee_id)
        if not trainee:
            return
        dialog = TraineeDialog(trainee=trainee, parent=self)
        if dialog.exec_() == QDialog.Accepted and dialog.result_data:
            try:
                training_svc.update_trainee(trainee_id, dialog.result_data)
                self.refresh_table()
            except Exception as e:
                print(f"Error updating trainee: {e}")

    def _delete_trainee(self, trainee_id: int, name: str):
        if confirm_delete(self, name):
            training_svc.soft_delete_trainee(trainee_id)
            self.refresh_table()
