"""
Trainer management form — شاشة إدارة المدربين.
جدول عرض + نموذج إضافة/تعديل + حذف ناعم.
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QDialog,
    QFormLayout, QTextEdit, QFrame, QAbstractItemView, QCheckBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from ui.styles import COLORS, FONTS, FONT_SIZES, SPACING
from ui.button_utils import (
    create_button, create_danger_button, confirm_delete,
    BUTTON_PRIMARY, BUTTON_GHOST
)

import services.training_service as training_svc


class TrainerDialog(QDialog):
    """نافذة إضافة/تعديل مدرب."""

    def __init__(self, trainer=None, parent=None):
        super().__init__(parent)
        self.trainer = trainer
        self.result_data = None
        self.setWindowTitle("تعديل مدرب" if trainer else "إضافة مدرب جديد")
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
        form.addRow("البريد الإلكتروني:", self.email_input)

        # Specialization
        self.spec_input = QLineEdit()
        self.spec_input.setPlaceholderText("مجالات الخبرة والتدريب")
        form.addRow("التخصص:", self.spec_input)

        # Active Checkbox
        self.active_check = QCheckBox("نشط ومتاح للعمل")
        self.active_check.setChecked(True)
        form.addRow("الحالة:", self.active_check)

        # Bio
        self.bio_input = QTextEdit()
        self.bio_input.setMaximumHeight(80)
        form.addRow("السيرة الذاتية (Bio):", self.bio_input)

        layout.addLayout(form)

        # Pre-fill
        if self.trainer:
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
        t = self.trainer
        self.name_input.setText(t.name or "")
        self.phone_input.setText(t.phone or "")
        self.email_input.setText(t.email or "")
        self.spec_input.setText(t.specialization or "")
        self.active_check.setChecked(t.is_active if t.is_active is not None else True)
        self.bio_input.setPlainText(t.bio or "")

    def _save(self):
        name = self.name_input.text().strip()
        if not name:
            self.name_input.setFocus()
            return
        
        self.result_data = {
            "name": name,
            "phone": self.phone_input.text().strip() or None,
            "email": self.email_input.text().strip() or None,
            "specialization": self.spec_input.text().strip() or None,
            "is_active": self.active_check.isChecked(),
            "bio": self.bio_input.toPlainText().strip() or None,
        }
        self.accept()


class TrainerForm(QWidget):
    """شاشة إدارة المدربين — جدول وتعديل."""

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
        title = QLabel("👨‍🏫  إدارة المدربين")
        title.setFont(QFont(FONTS["display"].split(",")[0], FONT_SIZES["h2"], QFont.Bold))
        title.setStyleSheet(f"color: {COLORS['text_primary']}; background: transparent;")
        header.addWidget(title)
        header.addStretch()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 بحث عن مدرب...")
        self.search_input.setFixedWidth(250)
        self.search_input.textChanged.connect(self._on_search)
        header.addWidget(self.search_input)

        add_btn = create_button("➕  إضافة مدرب", BUTTON_PRIMARY)
        add_btn.clicked.connect(self._add_trainer)
        header.addWidget(add_btn)

        layout.addLayout(header)

        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background-color: {COLORS['border']};")
        layout.addWidget(sep)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "الاسم", "الهاتف", "البريد الإلكتروني", "التخصص",
            "الحالة", "إجراءات"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Fixed)
        self.table.setColumnWidth(5, 180)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table)

    def refresh_table(self):
        trainers = training_svc.get_all_trainers()
        self._populate_table(trainers)

    def _populate_table(self, trainers):
        self.table.setRowCount(len(trainers))
        for row, t in enumerate(trainers):
            self.table.setItem(row, 0, QTableWidgetItem(t.name or ""))
            self.table.setItem(row, 1, QTableWidgetItem(t.phone or ""))
            self.table.setItem(row, 2, QTableWidgetItem(t.email or ""))
            self.table.setItem(row, 3, QTableWidgetItem(t.specialization or ""))
            
            status_text = "نشط" if t.is_active else "غير نشط"
            self.table.setItem(row, 4, QTableWidgetItem(status_text))

            # Actions
            actions = QWidget()
            actions_layout = QHBoxLayout(actions)
            actions_layout.setContentsMargins(4, 4, 4, 4)
            actions_layout.setSpacing(4)

            profile_btn = create_button("👤", BUTTON_GHOST)
            profile_btn.setFixedSize(36, 32)
            profile_btn.setToolTip("عرض الملف التعريفي")
            profile_btn.clicked.connect(lambda _, t_obj=t: self._view_trainer_profile(t_obj))
            actions_layout.addWidget(profile_btn)

            edit_btn = create_button("✏️", BUTTON_GHOST)
            edit_btn.setFixedSize(36, 32)
            edit_btn.clicked.connect(lambda _, tid=t.id: self._edit_trainer(tid))
            actions_layout.addWidget(edit_btn)

            del_btn = create_danger_button("🗑️")
            del_btn.setFixedSize(36, 32)
            del_btn.clicked.connect(lambda _, tid=t.id, tname=t.name: self._delete_trainer(tid, tname))
            actions_layout.addWidget(del_btn)

            self.table.setCellWidget(row, 5, actions)
            self.table.setRowHeight(row, 48)

    def _on_search(self, text: str):
        # We can implement in-memory simple filter
        trainers = training_svc.get_all_trainers()
        if text.strip():
            query = text.strip().lower()
            filtered = [t for t in trainers if query in (t.name or "").lower() or query in (t.specialization or "").lower()]
        else:
            filtered = trainers
        self._populate_table(filtered)

    def _add_trainer(self):
        dialog = TrainerDialog(parent=self)
        if dialog.exec_() == QDialog.Accepted and dialog.result_data:
            try:
                training_svc.create_trainer(dialog.result_data)
                self.refresh_table()
            except Exception as e:
                print(f"Error creating trainer: {e}")

    def _edit_trainer(self, trainer_id: int):
        trainer = training_svc.get_trainer_by_id(trainer_id)
        if not trainer:
            return
        dialog = TrainerDialog(trainer=trainer, parent=self)
        if dialog.exec_() == QDialog.Accepted and dialog.result_data:
            try:
                training_svc.update_trainer(trainer_id, dialog.result_data)
                self.refresh_table()
            except Exception as e:
                print(f"Error updating trainer: {e}")

    def _delete_trainer(self, trainer_id: int, name: str):
        if confirm_delete(self, name):
            training_svc.soft_delete_trainer(trainer_id)
            self.refresh_table()

    def _view_trainer_profile(self, trainer):
        from ui.dialogs.profile_canvas_dialog import ProfileCanvasDialog
        dialog = ProfileCanvasDialog(trainer, person_type="trainer", parent=self)
        dialog.exec_()
        self.refresh_table()
