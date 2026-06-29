"""
Training Management Form — شاشة إدارة التدريب.
تدعم التبويبات المتعددة (البرامج، المتدربين، المدربين) وإدارة المسجلين بالدورات.
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QDialog,
    QFormLayout, QTextEdit, QFrame, QAbstractItemView, QComboBox,
    QSpinBox, QDoubleSpinBox, QDateEdit, QTabWidget, QStackedWidget,
    QMessageBox
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont

from ui.styles import COLORS, FONTS, FONT_SIZES, SPACING, BORDER_RADIUS
from ui.button_utils import (
    create_button, create_danger_button, confirm_delete,
    BUTTON_PRIMARY, BUTTON_SECONDARY, BUTTON_GHOST
)

from ui.forms.trainee_form import TraineeForm
from ui.forms.trainer_form import TrainerForm
from ui.dialogs.enrollment_dialog import EnrollmentDialog

import services.training_service as training_svc
import services.hall_service as hall_svc
import services.project_service as project_svc
from models.enums import CourseCategory, TrainerPayType, PaymentMethod


class ProgramDialog(QDialog):
    """نافذة إضافة/تعديل برنامج تدريبي."""

    def __init__(self, program=None, parent=None):
        super().__init__(parent)
        self.program = program
        self.result_data = None
        self.setWindowTitle("تعديل دورة تدريبية" if program else "إضافة دورة تدريبية جديدة")
        self.setMinimumWidth(600)
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

        title = QLabel(self.windowTitle())
        title.setFont(QFont(FONTS["display"].split(",")[0], FONT_SIZES["h2"], QFont.Bold))
        title.setStyleSheet(f"color: {COLORS['accent']}; background: transparent;")
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(SPACING["sm"])
        form.setLabelAlignment(Qt.AlignRight)

        # Name
        self.name_input = QLineEdit()
        form.addRow("اسم الدورة *:", self.name_input)

        # Description
        self.desc_input = QTextEdit()
        self.desc_input.setMaximumHeight(60)
        form.addRow("الوصف:", self.desc_input)

        # Category
        self.category_combo = QComboBox()
        for cat in CourseCategory:
            self.category_combo.addItem(cat.value, cat)
        form.addRow("تصنيف الدورة:", self.category_combo)

        # Hall
        self.hall_combo = QComboBox()
        self.hall_combo.addItem("-- لا توجد قاعة --", None)
        for h in hall_svc.get_all_halls():
            self.hall_combo.addItem(f"{h.name} (سعة {h.capacity})", h.id)
        form.addRow("القاعة:", self.hall_combo)

        form.addRow("المشروع المرتبط:", self.project_combo)

        # Schedule
        self.schedule_days_input = QLineEdit()
        self.schedule_days_input.setPlaceholderText("مثال: السبت, الإثنين, الأربعاء")
        form.addRow("أيام التدريب:", self.schedule_days_input)

        self.schedule_time_combo = QComboBox()
        self.schedule_time_combo.addItems([
            "-- اختر وقتاً --",
            "08:00 - 10:00",
            "10:00 - 12:00",
            "12:00 - 14:00",
            "14:00 - 16:00",
            "16:00 - 18:00",
            "18:00 - 20:00"
        ])
        form.addRow("وقت التدريب (فترة):", self.schedule_time_combo)

        # Capacity (Min / Max)
        self.min_trainees_input = QSpinBox()
        self.min_trainees_input.setRange(1, 999)
        self.min_trainees_input.setValue(5)
        form.addRow("الحد الأدنى للطلاب:", self.min_trainees_input)

        self.max_trainees_input = QSpinBox()
        self.max_trainees_input.setRange(1, 999)
        self.max_trainees_input.setValue(25)
        form.addRow("الحد الأقصى للطلاب:", self.max_trainees_input)

        # Fee
        self.fee_input = QDoubleSpinBox()
        self.fee_input.setRange(0, 999999)
        self.fee_input.setDecimals(2)
        self.fee_input.setSuffix(" LYD")
        form.addRow("رسوم الدورة للطالب الواحد:", self.fee_input)

        # Dates
        self.start_date_input = QDateEdit()
        self.start_date_input.setCalendarPopup(True)
        self.start_date_input.setDate(QDate.currentDate())
        self.start_date_input.setDisplayFormat("yyyy-MM-dd")
        form.addRow("تاريخ البدء:", self.start_date_input)

        self.end_date_input = QDateEdit()
        self.end_date_input.setCalendarPopup(True)
        self.end_date_input.setDate(QDate.currentDate().addDays(14))
        self.end_date_input.setDisplayFormat("yyyy-MM-dd")
        form.addRow("تاريخ الانتهاء:", self.end_date_input)

        # Hours
        self.hours_input = QSpinBox()
        self.hours_input.setRange(1, 999)
        self.hours_input.setValue(30)
        form.addRow("عدد الساعات التدريبية:", self.hours_input)

        # Trainer pay config
        self.trainer_pay_combo = QComboBox()
        for tpt in TrainerPayType:
            self.trainer_pay_combo.addItem(tpt.value, tpt)
        form.addRow("طريقة حساب أجر المدرب:", self.trainer_pay_combo)

        self.trainer_pay_value_input = QDoubleSpinBox()
        self.trainer_pay_value_input.setRange(0, 999999)
        self.trainer_pay_value_input.setDecimals(2)
        self.trainer_pay_value_input.setSuffix(" LYD")
        form.addRow("قيمة مستحقات المدرب:", self.trainer_pay_value_input)

        # Status
        self.status_combo = QComboBox()
        self.status_combo.addItems(["مخطط", "جارية", "مكتملة", "ملغاة"])
        form.addRow("الحالة:", self.status_combo)

        # Notes
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(60)
        form.addRow("ملاحظات:", self.notes_input)

        layout.addLayout(form)

        if self.program:
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
        p = self.program
        self.name_input.setText(p.name or "")
        self.desc_input.setPlainText(p.description or "")
        self.notes_input.setPlainText(p.notes or "")
        
        if p.min_trainees: self.min_trainees_input.setValue(p.min_trainees)
        if p.max_trainees: self.max_trainees_input.setValue(p.max_trainees)
        if p.fee_per_trainee: self.fee_input.setValue(float(p.fee_per_trainee))
        if p.duration_hours: self.hours_input.setValue(p.duration_hours)
        if p.trainer_pay_value: self.trainer_pay_value_input.setValue(float(p.trainer_pay_value))

        # Set status
        idx = self.status_combo.findText(p.status or "مخطط")
        if idx >= 0:
            self.status_combo.setCurrentIndex(idx)

        # Set dates
        if p.start_date:
            self.start_date_input.setDate(QDate(p.start_date.year, p.start_date.month, p.start_date.day))
        if p.end_date:
            self.end_date_input.setDate(QDate(p.end_date.year, p.end_date.month, p.end_date.day))

        # Set combos
        for i in range(self.category_combo.count()):
            if self.category_combo.itemData(i) == p.course_category:
                self.category_combo.setCurrentIndex(i)
                break

        for i in range(self.hall_combo.count()):
            if self.hall_combo.itemData(i) == p.hall_id:
                self.hall_combo.setCurrentIndex(i)
                break

        for i in range(self.project_combo.count()):
            if self.project_combo.itemData(i) == p.project_id:
                self.project_combo.setCurrentIndex(i)
                break

        for i in range(self.trainer_pay_combo.count()):
            if self.trainer_pay_combo.itemData(i) == p.trainer_pay_type:
                self.trainer_pay_combo.setCurrentIndex(i)
                break

        if p.schedule_days:
            self.schedule_days_input.setText(p.schedule_days)
        if p.schedule_time:
            idx = self.schedule_time_combo.findText(p.schedule_time)
            if idx >= 0:
                self.schedule_time_combo.setCurrentIndex(idx)

    def _save(self):
        name = self.name_input.text().strip()
        if not name:
            self.name_input.setFocus()
            return

        cat = self.category_combo.currentData()
        hall_id = self.hall_combo.currentData()
        proj_id = self.project_combo.currentData()
        pay_type = self.trainer_pay_combo.currentData()

        # Logical constraint: if category == PROJECT, project_id is mandatory
        if cat == CourseCategory.PROJECT and not proj_id:
            QMessageBox.critical(self, "خطأ", "يجب تحديد مشروع مرتبط إذا كان تصنيف الدورة 'تدريبات مشاريع'.")
            self.project_combo.setFocus()
            return

        self.result_data = {
            "name": name,
            "description": self.desc_input.toPlainText().strip() or None,
            "course_category": cat,
            "hall_id": hall_id,
            "project_id": proj_id,
            "min_trainees": self.min_trainees_input.value(),
            "max_trainees": self.max_trainees_input.value(),
            "fee_per_trainee": self.fee_input.value() if self.fee_input.value() > 0 else None,
            "start_date": self.start_date_input.date().toPyDate(),
            "end_date": self.end_date_input.date().toPyDate(),
            "duration_hours": self.hours_input.value(),
            "trainer_pay_type": pay_type,
            "trainer_pay_value": self.trainer_pay_value_input.value() if self.trainer_pay_value_input.value() > 0 else None,
            "status": self.status_combo.currentText(),
            "notes": self.notes_input.toPlainText().strip() or None,
            "schedule_days": self.schedule_days_input.text().strip() or None,
            "schedule_time": self.schedule_time_combo.currentText() if self.schedule_time_combo.currentIndex() > 0 else None,
        }
        self.accept()


class ProgramTraineesView(QWidget):
    """لوحة تفاصيل المسجلين في دورة تدريبية محددة."""

    def __init__(self, on_back_callback, parent=None):
        super().__init__(parent)
        self.on_back = on_back_callback
        self.course_id = None
        self.setLayoutDirection(Qt.RightToLeft)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING["md"])

        # Title bar
        title_bar = QHBoxLayout()
        
        back_btn = create_button("⬅️ العودة للبرامج", BUTTON_SECONDARY)
        back_btn.clicked.connect(self.on_back)
        title_bar.addWidget(back_btn)
        
        self.course_title = QLabel("تفاصيل المسجلين بالدورة:")
        self.course_title.setFont(QFont(FONTS["display"].split(",")[0], FONT_SIZES["h3"], QFont.Bold))
        self.course_title.setStyleSheet(f"color: {COLORS['accent']}; background: transparent;")
        title_bar.addWidget(self.course_title)
        
        title_bar.addStretch()
        
        # Add enrollment button
        add_enroll_btn = create_button("➕ تسجيل متدرب بالدورة", BUTTON_PRIMARY)
        add_enroll_btn.clicked.connect(self._add_enrollment)
        title_bar.addWidget(add_enroll_btn)
        
        layout.addLayout(title_bar)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "اسم المتدرب", "الهاتف", "تاريخ التسجيل", "حالة القبول",
            "طريقة الدفع", "المبلغ المدفوع", "إجراءات"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(6, QHeaderView.Fixed)
        self.table.setColumnWidth(6, 220)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table)

    def load_course(self, course_id: int):
        self.course_id = course_id
        course = training_svc.get_program_by_id(course_id)
        if not course:
            self.on_back()
            return
        
        self.course_title.setText(f"🎓 المسجلين بدورة: {course.name}")
        self.refresh_table()

    def refresh_table(self):
        if not self.course_id:
            return
        
        enrollments = training_svc.get_enrolled_trainees(self.course_id)
        self.table.setRowCount(len(enrollments))
        
        for row, en in enumerate(enrollments):
            trainee_name = en.trainee.name if en.trainee else f"طالب #{en.trainee_id}"
            trainee_phone = en.trainee.phone if en.trainee else ""
            
            self.table.setItem(row, 0, QTableWidgetItem(trainee_name))
            self.table.setItem(row, 1, QTableWidgetItem(trainee_phone))
            self.table.setItem(row, 2, QTableWidgetItem(str(en.created_at)[:10]))
            
            # Status
            status_item = QTableWidgetItem(en.enrollment_status or "")
            if en.enrollment_status == "نهائي":
                status_item.setForeground(Qt.green)
            self.table.setItem(row, 3, QTableWidgetItem(status_item))
            
            pm_val = en.payment_method.value if hasattr(en.payment_method, 'value') else str(en.payment_method or "")
            self.table.setItem(row, 4, QTableWidgetItem(pm_val))
            
            amount_str = f"{en.amount_paid:.2f} LYD" if en.amount_paid is not None else ""
            if en.refund_requested:
                amount_str += " (مسترجع)"
            self.table.setItem(row, 5, QTableWidgetItem(amount_str))

            # Actions layout
            actions = QWidget()
            actions_layout = QHBoxLayout(actions)
            actions_layout.setContentsMargins(4, 4, 4, 4)
            actions_layout.setSpacing(4)

            # Mark final/confirm
            if en.enrollment_status != "نهائي":
                conf_btn = create_button("تأكيد", BUTTON_GHOST)
                conf_btn.setFixedSize(60, 32)
                conf_btn.clicked.connect(lambda _, eid=en.id: self._confirm_enrollment(eid))
                actions_layout.addWidget(conf_btn)

            # Refund action
            if not en.refund_requested:
                ref_btn = create_button("استرجاع", BUTTON_GHOST)
                ref_btn.setFixedSize(60, 32)
                ref_btn.clicked.connect(lambda _, eid=en.id: self._refund_enrollment(eid))
                actions_layout.addWidget(ref_btn)

            # Delete enrollment
            del_btn = create_danger_button("إلغاء")
            del_btn.setFixedSize(50, 32)
            del_btn.clicked.connect(lambda _, eid=en.id, name=trainee_name: self._delete_enrollment(eid, name))
            actions_layout.addWidget(del_btn)

            self.table.setCellWidget(row, 6, actions)
            self.table.setRowHeight(row, 48)

    def _add_enrollment(self):
        if not self.course_id:
            return
        
        dialog = EnrollmentDialog(self.course_id, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            self.refresh_table()

    def _confirm_enrollment(self, enrollment_id: int):
        training_svc.update_enrollment(enrollment_id, {"enrollment_status": "نهائي"})
        self.refresh_table()

    def _refund_enrollment(self, enrollment_id: int):
        en = training_svc.get_enrollment_by_id(enrollment_id)
        if not en:
            return
        
        # We simulate refunding full amount paid
        training_svc.update_enrollment(enrollment_id, {
            "refund_requested": True,
            "refund_amount": en.amount_paid,
            "refund_date": QDate.currentDate().toPyDate()
        })
        self.refresh_table()

    def _delete_enrollment(self, enrollment_id: int, name: str):
        if confirm_delete(self, f"تسجيل المتدرب: {name}"):
            training_svc.delete_enrollment(enrollment_id)
            self.refresh_table()


class TrainingProgramsView(QWidget):
    """اللوحة الرئيسية لعرض البرامج التدريبية CRUD."""

    def __init__(self, on_manage_enrollment_callback, parent=None):
        super().__init__(parent)
        self.on_manage_enrollment = on_manage_enrollment_callback
        self.setLayoutDirection(Qt.RightToLeft)
        self._setup_ui()
        self.refresh_table()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING["md"])

        # Header
        header = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 بحث عن دورة...")
        self.search_input.setFixedWidth(250)
        self.search_input.textChanged.connect(self._on_search)
        header.addWidget(self.search_input)
        
        header.addStretch()

        add_btn = create_button("➕  إضافة دورة تدريبية", BUTTON_PRIMARY)
        add_btn.clicked.connect(self._add_program)
        header.addWidget(add_btn)

        layout.addLayout(header)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "اسم الدورة", "التصنيف", "تاريخ البدء", "تاريخ الانتهاء",
            "الساعات", "الحد الأدنى/الأقصى", "الحالة", "إجراءات"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(7, QHeaderView.Fixed)
        self.table.setColumnWidth(7, 240)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table)

    def refresh_table(self):
        programs = training_svc.get_all_programs()
        self._populate_table(programs)

    def _populate_table(self, programs):
        self.table.setRowCount(len(programs))
        for row, p in enumerate(programs):
            self.table.setItem(row, 0, QTableWidgetItem(p.name or ""))
            
            cat_val = p.course_category.value if hasattr(p.course_category, 'value') else str(p.course_category or "")
            self.table.setItem(row, 1, QTableWidgetItem(cat_val))
            
            self.table.setItem(row, 2, QTableWidgetItem(str(p.start_date) if p.start_date else ""))
            self.table.setItem(row, 3, QTableWidgetItem(str(p.end_date) if p.end_date else ""))
            self.table.setItem(row, 4, QTableWidgetItem(f"{p.duration_hours or 0} س"))
            self.table.setItem(row, 5, QTableWidgetItem(f"{p.min_trainees or 0} / {p.max_trainees or 0}"))
            self.table.setItem(row, 6, QTableWidgetItem(p.status or ""))

            # Actions
            actions = QWidget()
            actions_layout = QHBoxLayout(actions)
            actions_layout.setContentsMargins(4, 4, 4, 4)
            actions_layout.setSpacing(4)

            # Manage enrollments
            en_btn = create_button("🎓 المسجلين", BUTTON_GHOST)
            en_btn.setFixedSize(90, 32)
            en_btn.clicked.connect(lambda _, pid=p.id: self.on_manage_enrollment(pid))
            actions_layout.addWidget(en_btn)

            edit_btn = create_button("✏️", BUTTON_GHOST)
            edit_btn.setFixedSize(36, 32)
            edit_btn.clicked.connect(lambda _, pid=p.id: self._edit_program(pid))
            actions_layout.addWidget(edit_btn)

            del_btn = create_danger_button("🗑️")
            del_btn.setFixedSize(36, 32)
            del_btn.clicked.connect(lambda _, pid=p.id, pname=p.name: self._delete_program(pid, pname))
            actions_layout.addWidget(del_btn)

            self.table.setCellWidget(row, 7, actions)
            self.table.setRowHeight(row, 48)

    def _on_search(self, text: str):
        programs = training_svc.get_all_programs()
        if text.strip():
            query = text.strip().lower()
            filtered = [p for p in programs if query in (p.name or "").lower() or query in (p.notes or "").lower()]
        else:
            filtered = programs
        self._populate_table(filtered)

    def _add_program(self):
        dialog = ProgramDialog(parent=self)
        if dialog.exec_() == QDialog.Accepted and dialog.result_data:
            try:
                training_svc.create_program(dialog.result_data)
                self.refresh_table()
            except Exception as e:
                print(f"Error creating program: {e}")

    def _edit_program(self, program_id: int):
        program = training_svc.get_program_by_id(program_id)
        if not program:
            return
        dialog = ProgramDialog(program=program, parent=self)
        if dialog.exec_() == QDialog.Accepted and dialog.result_data:
            try:
                training_svc.update_program(program_id, dialog.result_data)
                self.refresh_table()
            except Exception as e:
                print(f"Error updating program: {e}")

    def _delete_program(self, program_id: int, name: str):
        if confirm_delete(self, name):
            training_svc.soft_delete_program(program_id)
            self.refresh_table()


class TrainingForm(QWidget):
    """الشاشة الحاضنة لوحدة التدريب بالكامل عبر التبويبات الثلاثة."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayoutDirection(Qt.RightToLeft)
        self._setup_ui()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(SPACING["md"], SPACING["md"],
                                        SPACING["md"], SPACING["md"])
        main_layout.setSpacing(SPACING["md"])

        # Tab Widget
        self.tabs = QTabWidget()
        self.tabs.setFont(QFont(FONTS["body"].split(",")[0], FONT_SIZES["body"]))

        # Tab 1: Stacked Widget (Courses table OR Course Detail)
        self.courses_tab = QWidget()
        courses_layout = QVBoxLayout(self.courses_tab)
        courses_layout.setContentsMargins(0, 0, 0, 0)
        
        self.courses_stack = QStackedWidget()
        
        # State 0: Program list
        self.programs_view = TrainingProgramsView(self._show_course_details, self)
        self.courses_stack.addWidget(self.programs_view)
        
        # State 1: Program detail
        self.trainees_view = ProgramTraineesView(self._show_programs_list, self)
        self.courses_stack.addWidget(self.trainees_view)
        
        courses_layout.addWidget(self.courses_stack)
        self.tabs.addTab(self.courses_tab, "📚  البرامج التدريبية")

        # Tab 2: Trainees Form
        self.trainees_tab = TraineeForm(self)
        self.tabs.addTab(self.trainees_tab, "🎓  إدارة المتدربين")

        # Tab 3: Trainers Form
        self.trainers_tab = TrainerForm(self)
        self.tabs.addTab(self.trainers_tab, "👨‍🏫  إدارة المدربين")

        main_layout.addWidget(self.tabs)

    def _show_course_details(self, course_id: int):
        self.trainees_view.load_course(course_id)
        self.courses_stack.setCurrentIndex(1)

    def _show_programs_list(self):
        self.programs_view.refresh_table()
        self.courses_stack.setCurrentIndex(0)
