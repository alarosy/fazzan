"""
Main application window — النافذة الرئيسية.
شريط جانبي للتنقل + QStackedWidget لعرض الصفحات.
"""
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel,
    QStackedWidget, QFrame, QSizePolicy, QPushButton
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QPixmap, QIcon

from ui.styles import COLORS, FONTS, FONT_SIZES, BORDER_RADIUS, SPACING
from ui.dashboard import Dashboard
from ui.forms.employee_form import EmployeeForm
from ui.forms.client_form import ClientForm
from ui.forms.training_form import TrainingForm
from ui.forms.hall_form import HallForm


class SidebarButton(QPushButton):
    """زر في الشريط الجانبي مع حالة نشطة."""

    def __init__(self, text: str, icon_text: str = "", parent=None):
        super().__init__(parent)
        display = f"  {text}  {icon_text}" if icon_text else f"  {text}"
        self.setText(display)
        self.setCheckable(True)
        self.setLayoutDirection(Qt.RightToLeft)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(48)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._apply_style(False)

    def _apply_style(self, active: bool):
        if active:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLORS['sidebar_active']};
                    color: {COLORS['accent']};
                    border: none;
                    border-right: 3px solid {COLORS['accent']};
                    text-align: right;
                    padding: 8px 16px;
                    font-size: {FONT_SIZES['body']}px;
                    font-weight: bold;
                    font-family: {FONTS['body']};
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {COLORS['text_muted']};
                    border: none;
                    border-right: 3px solid transparent;
                    text-align: right;
                    padding: 8px 16px;
                    font-size: {FONT_SIZES['body']}px;
                    font-family: {FONTS['body']};
                }}
                QPushButton:hover {{
                    background-color: {COLORS['sidebar_hover']};
                    color: {COLORS['text_primary']};
                }}
            """)

    def set_active(self, active: bool):
        self.setChecked(active)
        self._apply_style(active)


class MainWindow(QMainWindow):
    """
    النافذة الرئيسية للتطبيق.
    
    تتكون من:
    - شريط جانبي (Sidebar) على اليمين للتنقل
    - منطقة محتوى رئيسية (QStackedWidget) تعرض الصفحة الحالية
    """

    # Map page names to indices
    PAGE_MAP = {
        "dashboard":  0,
        "employees":  1,
        "clients":    2,
        "training":   3,
        "finance":    4,
        "projects":   5,
        "halls":      6,
        "settings":   7,
        "logistics":  8,
    }

    def __init__(self):
        super().__init__()
        self.setWindowTitle("المنظومة — نظام إدارة مركز التدريب")
        self.setMinimumSize(1200, 750)
        self.setLayoutDirection(Qt.RightToLeft)

        self._setup_ui()
        self._navigate_to("dashboard")

    def _setup_ui(self):
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ── Sidebar ──
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(240)
        self.sidebar.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['sidebar_bg']};
                border-left: 1px solid {COLORS['border']};
            }}
        """)

        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        # Sidebar header — logo + app name
        self.header_widget = QWidget()
        self.header_widget.setStyleSheet(f"""
            background-color: {COLORS['sidebar_bg']};
            border-bottom: 1px solid {COLORS['border']};
        """)
        header_layout = QVBoxLayout(self.header_widget)
        header_layout.setContentsMargins(SPACING["md"], SPACING["lg"],
                                          SPACING["md"], SPACING["lg"])
        header_layout.setSpacing(SPACING["sm"])
        header_layout.setAlignment(Qt.AlignCenter)

        self.app_name = QLabel("المنظومة")
        self.app_name.setFont(QFont(FONTS["display"].split(",")[0], FONT_SIZES["h2"], QFont.Bold))
        self.app_name.setStyleSheet(f"color: {COLORS['accent']}; background: transparent;")
        self.app_name.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(self.app_name)

        self.app_desc = QLabel("نظام الإدارة المتكامل")
        self.app_desc.setFont(QFont(FONTS["body"].split(",")[0], FONT_SIZES["small"]))
        self.app_desc.setStyleSheet(f"color: {COLORS['text_muted']}; background: transparent;")
        self.app_desc.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(self.app_desc)

        sidebar_layout.addWidget(self.header_widget)

        # Navigation buttons
        self.nav_buttons = {}
        nav_items = [
            ("dashboard",  "لوحة التحكم",   "📊"),
            ("employees",  "الموظفون",       "👥"),
            ("clients",    "العملاء",        "🏢"),
            ("training",   "التدريب",        "📚"),
            ("finance",    "المالية",        "💰"),
            ("projects",   "المشاريع",       "📋"),
            ("halls",      "القاعات",        "🏛️"),
            ("settings",   "الإعدادات",      "⚙️"),
            ("logistics",  "الخدمات اللوجستية", "🛠️"),
        ]

        nav_spacer = QWidget()
        nav_spacer.setFixedHeight(SPACING["md"])
        nav_spacer.setStyleSheet("background: transparent;")
        sidebar_layout.addWidget(nav_spacer)

        for key, label, icon in nav_items:
            btn = SidebarButton(label, icon)
            btn.clicked.connect(lambda checked, k=key: self._navigate_to(k))
            sidebar_layout.addWidget(btn)
            self.nav_buttons[key] = btn

        sidebar_layout.addStretch()

        # Theme switcher button
        self.theme_btn = create_button("🌓  تبديل المظهر", BUTTON_SECONDARY)
        self.theme_btn.setFixedHeight(36)
        self.theme_btn.setFixedWidth(200)
        self.theme_btn.clicked.connect(self._toggle_theme_action)
        
        theme_btn_layout = QHBoxLayout()
        theme_btn_layout.setContentsMargins(0, 0, 0, SPACING["sm"])
        theme_btn_layout.setAlignment(Qt.AlignCenter)
        theme_btn_layout.addWidget(self.theme_btn)
        sidebar_layout.addLayout(theme_btn_layout)

        # Version info at bottom
        self.version_label = QLabel("الإصدار 1.0.0")
        self.version_label.setFont(QFont(FONTS["body"].split(",")[0], FONT_SIZES["tiny"]))
        self.version_label.setStyleSheet(f"color: {COLORS['border']}; background: transparent;")
        self.version_label.setAlignment(Qt.AlignCenter)
        self.version_label.setContentsMargins(0, 0, 0, SPACING["md"])
        sidebar_layout.addWidget(self.version_label)

        main_layout.addWidget(self.sidebar)

        # ── Content Area (Stacked Widget) ──
        self.stack = QStackedWidget()
        self.stack.setStyleSheet(f"background-color: {COLORS['background']};")

        # Page 0: Dashboard
        self.dashboard = Dashboard()
        self.dashboard.navigate_to.connect(self._navigate_to)
        self.stack.addWidget(self.dashboard)

        # Page 1: Employees
        self.employee_form = EmployeeForm()
        self.stack.addWidget(self.employee_form)

        # Page 2: Clients
        self.client_form = ClientForm()
        self.stack.addWidget(self.client_form)

        # Page 3: Training
        self.training_form = TrainingForm()
        self.stack.addWidget(self.training_form)

        # Page 4: Finance
        from ui.forms.finance_form import FinanceForm
        self.finance_form = FinanceForm()
        self.stack.addWidget(self.finance_form)

        # Page 5: Projects
        from ui.forms.project_form import ProjectForm
        self.project_form = ProjectForm()
        self.stack.addWidget(self.project_form)

        # Page 6: Halls
        self.hall_form = HallForm()
        self.stack.addWidget(self.hall_form)

        # Page 7: Settings (placeholder)
        self.stack.addWidget(self._create_placeholder("الإعدادات", "قريبًا"))

        # Page 8: Logistics
        from ui.forms.logistics_form import LogisticsForm
        self.logistics_form = LogisticsForm()
        self.stack.addWidget(self.logistics_form)

        main_layout.addWidget(self.stack)

    def _create_placeholder(self, title: str, message: str) -> QWidget:
        """Create a placeholder page for unimplemented sections."""
        page = QWidget()
        page.setLayoutDirection(Qt.RightToLeft)
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignCenter)

        icon = QLabel("🚧")
        icon.setFont(QFont(FONTS["body"].split(",")[0], 48))
        icon.setAlignment(Qt.AlignCenter)
        icon.setStyleSheet("background: transparent;")
        layout.addWidget(icon)

        title_label = QLabel(title)
        title_label.setFont(QFont(FONTS["display"].split(",")[0], FONT_SIZES["h1"], QFont.Bold))
        title_label.setStyleSheet(f"color: {COLORS['text_primary']}; background: transparent;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        msg_label = QLabel(message)
        msg_label.setFont(QFont(FONTS["body"].split(",")[0], FONT_SIZES["body"]))
        msg_label.setStyleSheet(f"color: {COLORS['text_muted']}; background: transparent;")
        msg_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(msg_label)

        return page

    def _navigate_to(self, page_name: str):
        """
        Navigate to a specific page.
        التنقل إلى صفحة محددة — يُحدّث الشريط الجانبي والمحتوى.
        """
        idx = self.PAGE_MAP.get(page_name, 0)
        self.stack.setCurrentIndex(idx)

        # Update sidebar active states
        for key, btn in self.nav_buttons.items():
            btn.set_active(key == page_name)

        # Refresh dashboard when navigating to it
        if page_name == "dashboard":
            self.dashboard.refresh_data()
        elif page_name == "training":
            self.training_form.programs_view.refresh_table()
            self.training_form.trainees_tab.refresh_table()
            self.training_form.trainers_tab.refresh_table()
        elif page_name == "halls":
            self.hall_form.refresh_halls()
        elif page_name == "finance":
            self.finance_form.refresh_all_data()
        elif page_name == "projects":
            self.project_form.refresh_all_data()
        elif page_name == "logistics":
            self.logistics_form._refresh_all_tables()

    def _toggle_theme_action(self):
        """التبديل بين المظهر الفاتح والداكن وتحديث كامل واجهة التطبيق."""
        from ui.styles import toggle_theme, get_global_stylesheet, COLORS
        toggle_theme()

        # Update style on application level
        from PyQt5.QtWidgets import QApplication
        QApplication.instance().setStyleSheet(get_global_stylesheet())

        # Update styling of main window widgets manually to ensure immediate redraw
        self.centralWidget().setStyleSheet(f"background-color: {COLORS['background']};")
        self.sidebar.setStyleSheet(f"background-color: {COLORS['sidebar_bg']}; border-left: 1px solid {COLORS['border']};")
        self.header_widget.setStyleSheet(f"background-color: {COLORS['sidebar_bg']}; border-bottom: 1px solid {COLORS['border']};")
        self.app_name.setStyleSheet(f"color: {COLORS['accent']}; background: transparent;")
        self.app_desc.setStyleSheet(f"color: {COLORS['text_muted']}; background: transparent;")
        self.version_label.setStyleSheet(f"color: {COLORS['border']}; background: transparent;")
        
        # Reload sidebar buttons styling
        for key, btn in self.nav_buttons.items():
            btn._apply_style(btn.isChecked())
            
        # Re-apply self theme switcher button styling
        self.theme_btn.setStyleSheet(self.theme_btn.styleSheet())

        # Force refresh active pages
        self.dashboard.refresh_data()
        self.dashboard.setStyleSheet(f"background-color: {COLORS['background']};")

