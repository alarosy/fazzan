"""
Dashboard widget — لوحة التحكم الرئيسية.
3 صفوف من البطاقات: الحالة الفورية، التنبيهات، الإحصاءات — تطابق §3.2 من CLAUDE.md.
"""
from datetime import datetime

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QFrame, QScrollArea, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QFont, QPixmap, QCursor

from ui.styles import COLORS, FONTS, FONT_SIZES, BORDER_RADIUS, SPACING
from ui.button_utils import create_button, BUTTON_SECONDARY

import services.finance_service as finance_svc
import services.project_service as project_svc
import services.training_service as training_svc
import services.hr_service as hr_svc
import services.client_service as client_svc


class DashboardCard(QFrame):
    """
    بطاقة Dashboard قابلة لإعادة الاستخدام.
    تعرض عنوانًا، قيمة رقمية كبيرة، ووصفًا ثانويًا مع وقت آخر تحديث.
    """
    clicked = pyqtSignal()

    def __init__(self, title: str, value: str, subtitle: str = "",
                 card_type: str = "normal", clickable: bool = False,
                 parent=None):
        super().__init__(parent)
        self.clickable = clickable
        self.card_type = card_type
        self._setup_ui(title, value, subtitle)

    def _get_bg_color(self) -> str:
        if self.card_type == "alert":
            return COLORS["alert_bg"]
        elif self.card_type == "success":
            return COLORS["success"]
        else:
            return COLORS["card_bg"]

    def _get_hover_color(self) -> str:
        if self.card_type == "alert":
            return COLORS["alert_hover"]
        elif self.card_type == "success":
            return COLORS["success_hover"]
        else:
            return COLORS["card_hover"]

    def _setup_ui(self, title: str, value: str, subtitle: str):
        bg = self._get_bg_color()
        hover = self._get_hover_color()

        self.setStyleSheet(f"""
            DashboardCard {{
                background-color: {bg};
                border-radius: {BORDER_RADIUS['lg']}px;
                border: 1px solid {COLORS['border']};
            }}
            DashboardCard:hover {{
                background-color: {hover};
                border-color: {COLORS['accent']};
            }}
        """)

        if self.clickable:
            self.setCursor(QCursor(Qt.PointingHandCursor))

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setMinimumHeight(140)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING["lg"], SPACING["lg"],
                                   SPACING["lg"], SPACING["md"])
        layout.setSpacing(SPACING["sm"])
        layout.setAlignment(Qt.AlignRight)

        # Title
        self.title_label = QLabel(title)
        self.title_label.setFont(QFont(FONTS["body"].split(",")[0], FONT_SIZES["small"]))
        self.title_label.setStyleSheet(f"color: {COLORS['text_muted']}; background: transparent;")
        self.title_label.setAlignment(Qt.AlignRight)
        layout.addWidget(self.title_label)

        # Value (large number)
        self.value_label = QLabel(value)
        value_size = FONT_SIZES["stat"] if self.card_type != "small" else FONT_SIZES["stat_sm"]
        self.value_label.setFont(QFont(FONTS["mono"].split(",")[0], value_size, QFont.Bold))
        self.value_label.setStyleSheet(f"""
            color: {COLORS['accent'] if self.card_type == 'normal' else COLORS['text_primary']};
            background: transparent;
        """)
        self.value_label.setAlignment(Qt.AlignRight)
        layout.addWidget(self.value_label)

        # Subtitle
        if subtitle:
            self.subtitle_label = QLabel(subtitle)
            self.subtitle_label.setFont(QFont(FONTS["body"].split(",")[0], FONT_SIZES["small"]))
            self.subtitle_label.setStyleSheet(f"color: {COLORS['text_muted']}; background: transparent;")
            self.subtitle_label.setAlignment(Qt.AlignRight)
            layout.addWidget(self.subtitle_label)

        # Timestamp
        self.timestamp_label = QLabel("")
        self.timestamp_label.setFont(QFont(FONTS["body"].split(",")[0], FONT_SIZES["tiny"]))
        self.timestamp_label.setStyleSheet(f"color: {COLORS['border']}; background: transparent;")
        self.timestamp_label.setAlignment(Qt.AlignRight)
        layout.addWidget(self.timestamp_label)
        self.update_timestamp()

    def update_value(self, value: str, subtitle: str = None):
        """تحديث القيمة المعروضة في البطاقة."""
        self.value_label.setText(value)
        if subtitle is not None and hasattr(self, 'subtitle_label'):
            self.subtitle_label.setText(subtitle)
        self.update_timestamp()

    def update_timestamp(self):
        """تحديث وقت آخر تحديث."""
        now = datetime.now().strftime("%H:%M:%S")
        self.timestamp_label.setText(f"آخر تحديث: {now}")

    def mousePressEvent(self, event):
        if self.clickable and event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


class SmallStatCard(QFrame):
    """بطاقة إحصائية صغيرة — Row 3."""

    def __init__(self, title: str, value: str, parent=None):
        super().__init__(parent)
        self._setup_ui(title, value)

    def _setup_ui(self, title: str, value: str):
        self.setStyleSheet(f"""
            SmallStatCard {{
                background-color: {COLORS['card_bg']};
                border-radius: {BORDER_RADIUS['md']}px;
                border: 1px solid {COLORS['border']};
            }}
            SmallStatCard:hover {{
                border-color: {COLORS['accent']};
            }}
        """)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setMinimumHeight(100)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING["md"], SPACING["md"],
                                   SPACING["md"], SPACING["md"])
        layout.setSpacing(SPACING["xs"])
        layout.setAlignment(Qt.AlignCenter)

        # Value
        self.value_label = QLabel(value)
        self.value_label.setFont(QFont(FONTS["mono"].split(",")[0], FONT_SIZES["stat_sm"], QFont.Bold))
        self.value_label.setStyleSheet(f"color: {COLORS['accent']}; background: transparent;")
        self.value_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.value_label)

        # Title
        self.title_label = QLabel(title)
        self.title_label.setFont(QFont(FONTS["body"].split(",")[0], FONT_SIZES["small"]))
        self.title_label.setStyleSheet(f"color: {COLORS['text_muted']}; background: transparent;")
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)

    def update_value(self, value: str):
        self.value_label.setText(value)


class Dashboard(QWidget):
    """
    لوحة التحكم الرئيسية — 3 صفوف من البطاقات.
    
    Signals:
        navigate_to: يُصدر عند النقر على بطاقة تنبيه — يحمل اسم الشاشة المستهدفة
    """
    navigate_to = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayoutDirection(Qt.RightToLeft)
        self._setup_ui()
        self.refresh_data()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(SPACING["xl"], SPACING["lg"],
                                        SPACING["xl"], SPACING["lg"])
        main_layout.setSpacing(SPACING["lg"])

        # ── Header: Logo + Center Name + Refresh Button ──
        header = QHBoxLayout()
        header.setSpacing(SPACING["md"])

        # Logo placeholder
        import os
        logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                  "assets", "logo.png")
        logo_label = QLabel()
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path).scaled(60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(pixmap)
        else:
            logo_label.setText("🏢")
            logo_label.setFont(QFont(FONTS["body"].split(",")[0], 32))
        logo_label.setStyleSheet("background: transparent;")
        header.addWidget(logo_label)

        # Center name
        center_name = QLabel("مركز التدريب والخدمات اللوجستية")
        center_name.setFont(QFont(FONTS["display"].split(",")[0], FONT_SIZES["h1"], QFont.Bold))
        center_name.setStyleSheet(f"color: {COLORS['text_primary']}; background: transparent;")
        header.addWidget(center_name)

        header.addStretch()

        # Refresh button
        refresh_btn = create_button("🔄  تحديث", BUTTON_SECONDARY)
        refresh_btn.clicked.connect(self.refresh_data)
        header.addWidget(refresh_btn)

        main_layout.addLayout(header)

        # ── Separator ──
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background-color: {COLORS['border']};")
        main_layout.addWidget(sep)

        # ── Scroll Area for Cards ──
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: transparent;")

        scroll_widget = QWidget()
        scroll_widget.setStyleSheet("background: transparent;")
        cards_layout = QVBoxLayout(scroll_widget)
        cards_layout.setSpacing(SPACING["lg"])
        cards_layout.setContentsMargins(0, SPACING["md"], 0, 0)

        # ── Row 1: الحالة الفورية (4 بطاقات كبيرة) ──
        row1_label = QLabel("الحالة الفورية")
        row1_label.setFont(QFont(FONTS["body"].split(",")[0], FONT_SIZES["h3"], QFont.Bold))
        row1_label.setStyleSheet(f"color: {COLORS['accent']}; background: transparent;")
        cards_layout.addWidget(row1_label)

        row1 = QHBoxLayout()
        row1.setSpacing(SPACING["md"])

        self.card_cash = DashboardCard("الرصيد النقدي (كاش)", "0", "LYD")
        self.card_bank = DashboardCard("الرصيد المصرفي", "0", "LYD")
        self.card_projects = DashboardCard("المشاريع النشطة", "0", "مشروع")
        self.card_courses = DashboardCard("الدورات الجارية", "0", "دورة")

        row1.addWidget(self.card_cash)
        row1.addWidget(self.card_bank)
        row1.addWidget(self.card_projects)
        row1.addWidget(self.card_courses)
        cards_layout.addLayout(row1)

        # ── Row 2: التنبيهات (4 بطاقات تنبيهية قابلة للنقر) ──
        row2_label = QLabel("التنبيهات")
        row2_label.setFont(QFont(FONTS["body"].split(",")[0], FONT_SIZES["h3"], QFont.Bold))
        row2_label.setStyleSheet(f"color: {COLORS['accent']}; background: transparent;")
        cards_layout.addWidget(row2_label)

        row2 = QHBoxLayout()
        row2.setSpacing(SPACING["md"])

        self.card_contracts = DashboardCard(
            "عقود تنتهي خلال 30 يومًا", "0",
            "اضغط للتفاصيل", card_type="alert", clickable=True
        )
        self.card_contracts.clicked.connect(lambda: self.navigate_to.emit("employees"))

        self.card_min_cap = DashboardCard(
            "دورات بالحد الأدنى", "0",
            "اضغط للتفاصيل", card_type="alert", clickable=True
        )
        self.card_min_cap.clicked.connect(lambda: self.navigate_to.emit("training"))

        self.card_max_cap = DashboardCard(
            "دورات تجاوزت الحد الأعلى", "0",
            "اضغط للتفاصيل", card_type="alert", clickable=True
        )
        self.card_max_cap.clicked.connect(lambda: self.navigate_to.emit("training"))

        self.card_proposals = DashboardCard(
            "عروض بانتظار الاعتماد", "0",
            "اضغط للتفاصيل", card_type="alert", clickable=True
        )
        self.card_proposals.clicked.connect(lambda: self.navigate_to.emit("finance"))

        row2.addWidget(self.card_contracts)
        row2.addWidget(self.card_min_cap)
        row2.addWidget(self.card_max_cap)
        row2.addWidget(self.card_proposals)
        cards_layout.addLayout(row2)

        # ── Row 3: إحصاءات عامة (4 بطاقات صغيرة) ──
        row3_label = QLabel("إحصاءات عامة")
        row3_label.setFont(QFont(FONTS["body"].split(",")[0], FONT_SIZES["h3"], QFont.Bold))
        row3_label.setStyleSheet(f"color: {COLORS['accent']}; background: transparent;")
        cards_layout.addWidget(row3_label)

        row3 = QHBoxLayout()
        row3.setSpacing(SPACING["md"])

        self.stat_employees = SmallStatCard("الموظفون", "0")
        self.stat_trainers = SmallStatCard("المدربون النشطون", "0")
        self.stat_trainees = SmallStatCard("متدربو الشهر", "0")
        self.stat_clients = SmallStatCard("إجمالي العملاء", "0")

        row3.addWidget(self.stat_employees)
        row3.addWidget(self.stat_trainers)
        row3.addWidget(self.stat_trainees)
        row3.addWidget(self.stat_clients)
        cards_layout.addLayout(row3)

        cards_layout.addStretch()
        scroll.setWidget(scroll_widget)
        main_layout.addWidget(scroll)

    def refresh_data(self):
        """
        تحديث جميع بيانات Dashboard من Services.
        يُستدعى عند فتح التطبيق وعند الضغط على زر التحديث (§3.3).
        """
        try:
            # Row 1: Immediate status
            cash = finance_svc.get_cash_balance()
            bank = finance_svc.get_bank_balance()
            active_projects = project_svc.count_active()
            active_courses = training_svc.count_active_courses()

            self.card_cash.update_value(f"{cash:,.3f}", "LYD")
            self.card_bank.update_value(f"{bank:,.3f}", "LYD")
            self.card_projects.update_value(str(active_projects), "مشروع")
            self.card_courses.update_value(str(active_courses), "دورة")

            # Row 2: Alerts
            expiring = hr_svc.get_expiring_contracts(30)
            self.card_contracts.update_value(str(len(expiring)),
                                              "اضغط للتفاصيل" if expiring else "لا توجد تنبيهات")

            # Course capacity alerts
            min_cap_courses = training_svc.get_courses_at_min_capacity()
            self.card_min_cap.update_value(str(len(min_cap_courses)),
                                            "اضغط للتفاصيل" if min_cap_courses else "لا توجد تنبيهات")

            max_cap_courses = training_svc.get_courses_over_capacity()
            self.card_max_cap.update_value(str(len(max_cap_courses)),
                                            "اضغط للتفاصيل" if max_cap_courses else "لا توجد تنبيهات")

            pending = finance_svc.count_pending_proposals()
            self.card_proposals.update_value(str(pending),
                                              "اضغط للتفاصيل" if pending else "لا توجد تنبيهات")

            # Row 3: General stats
            self.stat_employees.update_value(str(hr_svc.count_active_employees()))
            self.stat_trainers.update_value(str(training_svc.count_active_trainers()))
            self.stat_trainees.update_value(str(training_svc.count_month_trainees()))
            self.stat_clients.update_value(str(client_svc.count_clients()))

        except Exception as e:
            print(f"[Dashboard] Error refreshing data: {e}")
