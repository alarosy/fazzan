"""
Hall management and scheduling form — شاشة إدارة وجدولة القاعات.
تتضمن إدارة بيانات القاعات ومخطط الحجوزات الأسبوعي التفاعلي.
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QDialog,
    QFormLayout, QSpinBox, QDoubleSpinBox, QTextEdit, QFrame,
    QAbstractItemView, QSplitter, QCheckBox, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor

from ui.styles import COLORS, FONTS, FONT_SIZES, SPACING, BORDER_RADIUS
from ui.button_utils import (
    create_button, create_danger_button, confirm_delete,
    BUTTON_PRIMARY, BUTTON_SECONDARY, BUTTON_GHOST
)

import services.hall_service as hall_svc
import services.training_service as training_svc


class HallDialog(QDialog):
    """نافذة إضافة/تعديل قاعة."""

    def __init__(self, hall=None, parent=None):
        super().__init__(parent)
        self.hall = hall
        self.result_data = None
        self.setWindowTitle("تعديل قاعة" if hall else "إضافة قاعة جديدة")
        self.setMinimumWidth(450)
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
        form.addRow("اسم القاعة *:", self.name_input)

        # Capacity
        self.capacity_input = QSpinBox()
        self.capacity_input.setRange(1, 9999)
        self.capacity_input.setValue(20)
        form.addRow("السعة الاستيعابية (طالب):", self.capacity_input)

        # Rates
        self.daily_rate_input = QDoubleSpinBox()
        self.daily_rate_input.setRange(0, 99999)
        self.daily_rate_input.setValue(0)
        self.daily_rate_input.setSuffix(" LYD")
        form.addRow("سعر الإيجار اليومي:", self.daily_rate_input)

        self.hourly_rate_input = QDoubleSpinBox()
        self.hourly_rate_input.setRange(0, 99999)
        self.hourly_rate_input.setValue(0)
        self.hourly_rate_input.setSuffix(" LYD")
        form.addRow("سعر الإيجار الساعي:", self.hourly_rate_input)

        # Location
        self.loc_input = QLineEdit()
        form.addRow("الموقع/الطابق:", self.loc_input)

        # Active Checkbox
        self.active_check = QCheckBox("نشطة ومتاحة للحجز")
        self.active_check.setChecked(True)
        form.addRow("الحالة:", self.active_check)

        # Notes
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(60)
        form.addRow("ملاحظات:", self.notes_input)

        layout.addLayout(form)

        if self.hall:
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
        h = self.hall
        self.name_input.setText(h.name or "")
        self.loc_input.setText(h.location or "")
        self.notes_input.setPlainText(h.notes or "")
        if h.capacity: self.capacity_input.setValue(h.capacity)
        if h.daily_rate: self.daily_rate_input.setValue(float(h.daily_rate))
        if h.hourly_rate: self.hourly_rate_input.setValue(float(h.hourly_rate))
        self.active_check.setChecked(h.is_active if h.is_active is not None else True)

    def _save(self):
        name = self.name_input.text().strip()
        if not name:
            self.name_input.setFocus()
            return

        self.result_data = {
            "name": name,
            "capacity": self.capacity_input.value(),
            "daily_rate": self.daily_rate_input.value() if self.daily_rate_input.value() > 0 else None,
            "hourly_rate": self.hourly_rate_input.value() if self.hourly_rate_input.value() > 0 else None,
            "location": self.loc_input.text().strip() or None,
            "is_active": self.active_check.isChecked(),
            "notes": self.notes_input.toPlainText().strip() or None,
        }
        self.accept()


class HallForm(QWidget):
    """شاشة إدارة وجدولة القاعات الرئيسية."""

    DAYS = ["السبت", "الأحد", "الإثنين", "الثلاثاء", "الأربعاء", "الخميس"]
    SLOTS = [
        "08:00 - 10:00",
        "10:00 - 12:00",
        "12:00 - 14:00",
        "14:00 - 16:00",
        "16:00 - 18:00",
        "18:00 - 20:00"
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_hall_id = None
        self.setLayoutDirection(Qt.RightToLeft)
        self._setup_ui()
        self.refresh_halls()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(SPACING["xl"], SPACING["lg"],
                                        SPACING["xl"], SPACING["lg"])
        main_layout.setSpacing(SPACING["md"])

        # Title
        title = QLabel("🏛️  إدارة وجدولة القاعات التدريبية")
        title.setFont(QFont(FONTS["display"].split(",")[0], FONT_SIZES["h2"], QFont.Bold))
        title.setStyleSheet(f"color: {COLORS['text_primary']}; background: transparent;")
        main_layout.addWidget(title)

        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background-color: {COLORS['border']};")
        main_layout.addWidget(sep)

        # Splitter to divide Halls CRUD and Scheduler Grid
        splitter = QSplitter(Qt.Horizontal)
        splitter.setStyleSheet(f"QSplitter::handle {{ background-color: {COLORS['border']}; }}")

        # ── Left Widget: Halls CRUD ──
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, SPACING["md"], 0)
        left_layout.setSpacing(SPACING["md"])

        left_header = QHBoxLayout()
        left_title = QLabel("القاعات المتاحة")
        left_title.setFont(QFont(FONTS["display"].split(",")[0], FONT_SIZES["h3"], QFont.Bold))
        left_layout.addWidget(left_title)

        add_btn = create_button("➕ إضافة قاعة", BUTTON_PRIMARY)
        add_btn.clicked.connect(self._add_hall)
        left_header.addWidget(add_btn)
        left_header.addStretch()
        left_layout.addLayout(left_header)

        self.halls_table = QTableWidget()
        self.halls_table.setColumnCount(4)
        self.halls_table.setHorizontalHeaderLabels(["الاسم", "السعة", "الإيجار/يوم", "إجراءات"])
        self.halls_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.halls_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Fixed)
        self.halls_table.setColumnWidth(3, 140)
        self.halls_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.halls_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.halls_table.verticalHeader().setVisible(False)
        self.halls_table.itemSelectionChanged.connect(self._on_hall_selection_changed)
        left_layout.addWidget(self.halls_table)

        splitter.addWidget(left_widget)

        # ── Right Widget: Scheduler ──
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(SPACING["md"], 0, 0, 0)
        right_layout.setSpacing(SPACING["md"])

        self.scheduler_title = QLabel("المخطط الأسبوعي لحجوزات القاعة")
        self.scheduler_title.setFont(QFont(FONTS["display"].split(",")[0], FONT_SIZES["h3"], QFont.Bold))
        self.scheduler_title.setStyleSheet(f"color: {COLORS['accent']};")
        right_layout.addWidget(self.scheduler_title)

        # Scheduler grid table
        self.scheduler_grid = QTableWidget()
        self.scheduler_grid.setColumnCount(len(self.DAYS))
        self.scheduler_grid.setRowCount(len(self.SLOTS))
        self.scheduler_grid.setHorizontalHeaderLabels(self.DAYS)
        self.scheduler_grid.setVerticalHeaderLabels(self.SLOTS)
        self.scheduler_grid.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.scheduler_grid.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.scheduler_grid.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.scheduler_grid.setSelectionMode(QAbstractItemView.NoSelection)
        self.scheduler_grid.verticalHeader().setStyleSheet(f"color: {COLORS['accent']}; font-weight: bold;")
        right_layout.addWidget(self.scheduler_grid)

        splitter.addWidget(right_widget)

        # Set ratio 40% left, 60% right
        splitter.setSizes([450, 750])
        main_layout.addWidget(splitter)

    def refresh_halls(self):
        halls = hall_svc.get_all_halls()
        self.halls_table.setRowCount(len(halls))

        for row, h in enumerate(halls):
            # Store ID in hidden column item
            name_item = QTableWidgetItem(h.name or "")
            name_item.setData(Qt.UserRole, h.id)
            self.halls_table.setItem(row, 0, name_item)
            
            self.halls_table.setItem(row, 1, QTableWidgetItem(str(h.capacity or 0)))
            self.halls_table.setItem(row, 2, QTableWidgetItem(f"{h.daily_rate:.2f}" if h.daily_rate else ""))

            # Actions
            actions = QWidget()
            actions_layout = QHBoxLayout(actions)
            actions_layout.setContentsMargins(4, 4, 4, 4)
            actions_layout.setSpacing(4)

            edit_btn = create_button("✏️", BUTTON_GHOST)
            edit_btn.setFixedSize(36, 32)
            edit_btn.clicked.connect(lambda _, hid=h.id: self._edit_hall(hid))
            actions_layout.addWidget(edit_btn)

            del_btn = create_danger_button("🗑️")
            del_btn.setFixedSize(36, 32)
            del_btn.clicked.connect(lambda _, hid=h.id, hname=h.name: self._delete_hall(hid, hname))
            actions_layout.addWidget(del_btn)

            self.halls_table.setCellWidget(row, 3, actions)
            self.halls_table.setRowHeight(row, 48)

        # Select first row if exists
        if len(halls) > 0:
            self.halls_table.selectRow(0)

    def _on_hall_selection_changed(self):
        selected = self.halls_table.selectedItems()
        if not selected:
            self.selected_hall_id = None
            self.scheduler_title.setText("المخطط الأسبوعي لحجوزات القاعة")
            self._clear_scheduler()
            return

        # The first column item has the ID stored in UserRole
        row = self.halls_table.row(selected[0])
        name_item = self.halls_table.item(row, 0)
        self.selected_hall_id = name_item.data(Qt.UserRole)
        self.scheduler_title.setText(f"🏛️ المخطط الأسبوعي لحجوزات قاعة: {name_item.text()}")
        
        self.refresh_scheduler()

    def _clear_scheduler(self):
        for r in range(self.scheduler_grid.rowCount()):
            for c in range(self.scheduler_grid.columnCount()):
                self.scheduler_grid.setItem(r, c, QTableWidgetItem(""))

    def refresh_scheduler(self):
        self._clear_scheduler()
        if not self.selected_hall_id:
            return

        # Query all training programs
        programs = training_svc.get_all_programs()
        # Filter for this hall and active/scheduled
        hall_courses = [p for p in programs if p.hall_id == self.selected_hall_id and p.status in ["مخطط", "جارية"]]

        for p in hall_courses:
            if not p.schedule_days or not p.schedule_time:
                continue

            # Parse schedule days (comma separated)
            days = [d.strip() for d in p.schedule_days.split(",")]
            # Map time slot
            time_slot = p.schedule_time.strip()

            # Find matching row in grid
            row_idx = -1
            for r, slot in enumerate(self.SLOTS):
                if slot == time_slot:
                    row_idx = r
                    break
            
            if row_idx == -1:
                continue  # Time slot not found

            # Fill matching columns
            for day in days:
                col_idx = -1
                for c, d in enumerate(self.DAYS):
                    if d == day:
                        col_idx = c
                        break

                if col_idx == -1:
                    continue  # Day not found
                
                # Block the cell
                cell_text = f"{p.name}\n({p.status})"
                cell_item = QTableWidgetItem(cell_text)
                cell_item.setTextAlignment(Qt.AlignCenter)
                cell_item.setBackground(QColor(COLORS["card_hover"]))
                cell_item.setForeground(QColor(COLORS["accent"]))
                self.scheduler_grid.setItem(row_idx, col_idx, cell_item)

    def _add_hall(self):
        dialog = HallDialog(parent=self)
        if dialog.exec_() == QDialog.Accepted and dialog.result_data:
            try:
                hall_svc.create_hall(dialog.result_data)
                self.refresh_halls()
            except Exception as e:
                print(f"Error creating hall: {e}")

    def _edit_hall(self, hall_id: int):
        hall = hall_svc.get_hall_by_id(hall_id)
        if not hall:
            return
        dialog = HallDialog(hall=hall, parent=self)
        if dialog.exec_() == QDialog.Accepted and dialog.result_data:
            try:
                hall_svc.update_hall(hall_id, dialog.result_data)
                self.refresh_halls()
            except Exception as e:
                print(f"Error updating hall: {e}")

    def _delete_hall(self, hall_id: int, name: str):
        if confirm_delete(self, name):
            # Check if hall is referenced by any active training program
            programs = training_svc.get_all_programs()
            referenced = any(p.hall_id == hall_id and p.status in ["مخطط", "جارية"] for p in programs)
            if referenced:
                QMessageBox.critical(self, "خطأ", "لا يمكن حذف القاعة لوجود دورات تدريبية نشطة مجدولة فيها.")
                return
            
            hall_svc.delete_hall(hall_id)
            self.refresh_halls()
