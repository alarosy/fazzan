"""
Enrollment Dialog — نافذة تسجيل متدرب في دورة تدريبية.
تدعم البحث الذكي (Autocomplete) أو التسجيل الجديد المباشر.
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QDoubleSpinBox, QFormLayout, QTabWidget, QWidget
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from ui.styles import COLORS, FONTS, FONT_SIZES, SPACING
from ui.button_utils import create_button, BUTTON_PRIMARY, BUTTON_GHOST

import services.training_service as training_svc
from models.enums import PaymentMethod


class EnrollmentDialog(QDialog):
    """نافذة تسجيل متدرب في دورة تدريبية."""

    def __init__(self, course_id: int, parent=None):
        super().__init__(parent)
        self.course_id = course_id
        self.result_enrollment = None
        
        self.setWindowTitle("تسجيل متدرب في الدورة")
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

        # Header Title
        title = QLabel("🎓  تسجيل متدرب جديد بالدورة")
        title.setFont(QFont(FONTS["display"].split(",")[0], FONT_SIZES["h2"], QFont.Bold))
        title.setStyleSheet(f"color: {COLORS['accent']}; background: transparent;")
        title.setAlignment(Qt.AlignRight)
        layout.addWidget(title)

        # Tab Widget to choose between Existing Trainee vs New Trainee
        self.tabs = QTabWidget()
        
        # Tab 1: Existing Trainee
        self.tab_existing = QWidget()
        existing_layout = QVBoxLayout(self.tab_existing)
        existing_layout.setContentsMargins(0, SPACING["md"], 0, 0)
        
        existing_form = QFormLayout()
        existing_form.setSpacing(SPACING["sm"])
        existing_form.setLabelAlignment(Qt.AlignRight)
        
        self.trainee_search_combo = QComboBox()
        self.trainee_search_combo.setEditable(True)
        self.trainee_search_combo.setPlaceholderText("اكتب للبحث عن متدرب...")
        self.trainee_search_combo.lineEdit().textEdited.connect(self._on_search_text_changed)
        existing_form.addRow("ابحث عن متدرب *:", self.trainee_search_combo)
        
        existing_layout.addLayout(existing_form)
        existing_layout.addStretch()
        self.tabs.addTab(self.tab_existing, "متدرب مسجل مسبقاً")

        # Tab 2: New Trainee
        self.tab_new = QWidget()
        new_layout = QVBoxLayout(self.tab_new)
        new_layout.setContentsMargins(0, SPACING["md"], 0, 0)
        
        new_form = QFormLayout()
        new_form.setSpacing(SPACING["sm"])
        new_form.setLabelAlignment(Qt.AlignRight)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("الاسم الكامل للمتدرب الجديد")
        new_form.addRow("الاسم *:", self.name_input)
        
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("09XXXXXXXX")
        new_form.addRow("الهاتف:", self.phone_input)
        
        self.email_input = QLineEdit()
        new_form.addRow("البريد:", self.email_input)
        
        self.id_input = QLineEdit()
        new_form.addRow("رقم الهوية:", self.id_input)
        
        self.org_input = QLineEdit()
        new_form.addRow("الجهة/المؤسسة:", self.org_input)
        
        self.gender_combo = QComboBox()
        self.gender_combo.addItems(["ذكر", "أنثى"])
        new_form.addRow("الجنس:", self.gender_combo)
        
        new_layout.addLayout(new_form)
        self.tabs.addTab(self.tab_new, "متدرب جديد كلياً")
        
        layout.addWidget(self.tabs)

        # Common Enrollment Options Frame
        enroll_frame = QFrame()
        enroll_frame.setStyleSheet(f"""
            QFrame {{
                border-top: 1px solid {COLORS['border']};
                margin-top: 10px;
                padding-top: 10px;
            }}
        """)
        enroll_layout = QVBoxLayout(enroll_frame)
        enroll_layout.setContentsMargins(0, 0, 0, 0)
        
        form_enroll = QFormLayout()
        form_enroll.setSpacing(SPACING["sm"])
        form_enroll.setLabelAlignment(Qt.AlignRight)
        
        self.status_combo = QComboBox()
        self.status_combo.addItems(["مبدئي", "نهائي"])
        form_enroll.addRow("حالة التسجيل:", self.status_combo)
        
        self.payment_combo = QComboBox()
        for pm in PaymentMethod:
            self.payment_combo.addItem(pm.value, pm)
        form_enroll.addRow("طريقة الدفع:", self.payment_combo)
        
        self.amount_input = QDoubleSpinBox()
        self.amount_input.setRange(0, 999999)
        self.amount_input.setDecimals(2)
        self.amount_input.setSuffix(" LYD")
        form_enroll.addRow("المبلغ المدفوع:", self.amount_input)
        
        enroll_layout.addLayout(form_enroll)
        layout.addWidget(enroll_frame)

        # Buttons
        btn_layout = QHBoxLayout()
        cancel_btn = create_button("إلغاء", BUTTON_GHOST)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        btn_layout.addStretch()
        
        save_btn = create_button("تسجيل الدخول", BUTTON_PRIMARY)
        save_btn.clicked.connect(self._save)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)

    def _on_search_text_changed(self, text: str):
        """تنبيه عند تغيير النص للبحث التلقائي في قاعدة البيانات."""
        if len(text.strip()) < 2:
            return
        
        # Search DB
        trainees = training_svc.search_existing_trainees(text.strip())
        
        # Suppress textChanged signals temporarily
        self.trainee_search_combo.lineEdit().textEdited.disconnect(self._on_search_text_changed)
        
        current_text = self.trainee_search_combo.currentText()
        self.trainee_search_combo.clear()
        
        for t in trainees:
            # We display name + phone
            display = f"{t.name} ({t.phone or 'بدون هاتف'})"
            self.trainee_search_combo.addItem(display, t.id)
            
        self.trainee_search_combo.setEditText(current_text)
        self.trainee_search_combo.showPopup()
        
        self.trainee_search_combo.lineEdit().textEdited.connect(self._on_search_text_changed)

    def _save(self):
        use_existing = self.tabs.currentIndex() == 0
        
        trainee_id = None
        trainee_data = None
        
        if use_existing:
            idx = self.trainee_search_combo.currentIndex()
            if idx < 0 or self.trainee_search_combo.itemData(idx) is None:
                self.trainee_search_combo.setFocus()
                return
            trainee_id = self.trainee_search_combo.itemData(idx)
        else:
            name = self.name_input.text().strip()
            if not name:
                self.name_input.setFocus()
                return
            trainee_data = {
                "name": name,
                "phone": self.phone_input.text().strip() or None,
                "email": self.email_input.text().strip() or None,
                "id_number": self.id_input.text().strip() or None,
                "organization": self.org_input.text().strip() or None,
                "gender": self.gender_combo.currentText(),
            }

        # Enrollment data
        pm = self.payment_combo.currentData()
        enrollment_data = {
            "enrollment_status": self.status_combo.currentText(),
            "payment_method": pm if pm else None,
            "amount_paid": self.amount_input.value() if self.amount_input.value() > 0 else 0.0,
        }

        try:
            self.result_enrollment = training_svc.enroll_trainee(
                self.course_id, trainee_id, trainee_data, enrollment_data
            )
            self.accept()
        except Exception as e:
            # Show warning or error log
            print(f"Error enrolling: {e}")
            self.reject()
