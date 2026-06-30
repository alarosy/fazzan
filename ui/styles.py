"""
Central theme and palette constants for the application UI.
ثوابت الألوان والأنماط المركزية للواجهة — تطابق §3.1 من CLAUDE.md.
"""

# ─── Theme Palettes ──────────────────────────────────────────────────────────
THEMES = {
    "light": {
        "background":   "#F4F4F6",   # رمادي فاتح مريح — خلفية رئيسية
        "card_bg":      "#FFFFFF",   # أبيض ناصع — خلفية البطاقات
        "card_hover":   "#EBECEF",   # بطاقة عند التمرير
        "accent":       "#FF5E3A",   # برتقالي مرجاني (Coral) مضيء — العناصر البارزة
        "accent_hover": "#FF7554",   # برتقالي أفتح عند التمرير
        "text_primary": "#1C1C1E",   # داكن جداً — النصوص الرئيسية
        "text_muted":   "#707078",   # رمادي متوسط — النصوص الثانوية
        "alert_bg":     "#FDF2F2",   # أحمر/وردي فاتح جداً — بطاقات التنبيه
        "alert_hover":  "#FDE8E8",   # تنبيه عند التمرير
        "success":      "#DEF7EC",   # أخضر فاتح — مؤشرات إيجابية
        "success_text": "#03543F",   # أخضر داكن للنص
        "success_hover":"#C6F6D5",   # أخضر عند التمرير
        "danger":       "#E02424",   # أحمر للحذف
        "danger_hover": "#C81E1E",   # أحمر عند التمرير
        "sidebar_bg":   "#FFFFFF",   # خلفية الشريط الجانبي الفاتحة
        "sidebar_hover":"#F1F3F5",   # شريط جانبي عند التمرير
        "sidebar_active":"#EAEBED",  # عنصر نشط في الشريط
        "border":       "#E2E2E8",   # حدود خفيفة
        "input_bg":     "#FFFFFF",   # خلفية حقول الإدخال البيضاء
    },
    "dark": {
        "background":   "#1C1C1E",   # رمادي دافئ داكن فاخر — خلفية رئيسية
        "card_bg":      "#28282B",   # رمادي دافئ متوسط — خلفية البطاقات
        "card_hover":   "#333336",   # بطاقة عند التمرير
        "accent":       "#FF5E3A",   # برتقالي مرجاني (Coral) مضيء — العناصر البارزة
        "accent_hover": "#FF7554",   # برتقالي أفتح عند التمرير
        "text_primary": "#FFFFFF",   # أبيض ناصع — النصوص الرئيسية
        "text_muted":   "#9E9E9E",   # رمادي متوسط — النصوص الثانوية
        "alert_bg":     "#3D1B1B",   # أحمر داكن — بطاقات التنبيه
        "alert_hover":  "#4D2525",   # تنبيه عند التمرير
        "success":      "#1F382B",   # أخضر داكن — مؤشرات إيجابية
        "success_text": "#22C55E",   # أخضر زمردي للنص (مثل المؤشرات الإيجابية)
        "success_hover":"#2E533A",   # أخضر عند التمرير
        "danger":       "#EF4444",   # أحمر للحذف
        "danger_hover": "#F87171",   # أحمر عند التمرير
        "sidebar_bg":   "#121214",   # خلفية الشريط الجانبي الداكنة جداً للهيكلية
        "sidebar_hover":"#1D1D20",   # شريط جانبي عند التمرير
        "sidebar_active":"#28282B",  # عنصر نشط في الشريط (يتطابق مع البطاقات)
        "border":       "#2E2E33",   # حدود خفيفة وأنيقة
        "input_bg":     "#161618",   # خلفية حقول الإدخال المحفورة
    }
}

_current_theme_name = "light"
COLORS = dict(THEMES[_current_theme_name])

def get_current_theme() -> str:
    """الحصول على اسم المظهر الحالي."""
    global _current_theme_name
    return _current_theme_name

def set_theme(theme_name: str):
    """تعيين المظهر النشط وتحديث ثوابت COLORS."""
    global _current_theme_name, COLORS
    if theme_name in THEMES:
        _current_theme_name = theme_name
        COLORS.clear()
        COLORS.update(THEMES[theme_name])

def toggle_theme() -> str:
    """التبديل بين المظهر الفاتح والداكن."""
    new_theme = "dark" if get_current_theme() == "light" else "light"
    set_theme(new_theme)
    return new_theme

# ─── Font Settings ───────────────────────────────────────────────────────────
FONTS = {
    "display":  "Cairo, Tajawal, 'Segoe UI', Arial",
    "body":     "Cairo, Tajawal, 'Segoe UI', Arial",
    "mono":     "'Courier New', Consolas, monospace",
}

FONT_SIZES = {
    "h1":       28,
    "h2":       22,
    "h3":       18,
    "body":     14,
    "small":    12,
    "tiny":     10,
    "stat":     36,   # Dashboard large numbers
    "stat_sm":  24,   # Dashboard small numbers
}

# ─── Spacing ─────────────────────────────────────────────────────────────────
SPACING = {
    "xs":  4,
    "sm":  8,
    "md":  16,
    "lg":  24,
    "xl":  32,
}

BORDER_RADIUS = {
    "sm":  8,
    "md":  12,
    "lg":  18,
}

# ─── Global Stylesheet ──────────────────────────────────────────────────────
def get_global_stylesheet() -> str:
    """
    Generate the global QApplication stylesheet.
    توليد ورقة الأنماط العامة لكل التطبيق.
    """
    c = COLORS
    f = FONTS
    return f"""
        /* ── Global ── */
        QMainWindow, QWidget {{
            background-color: {c['background']};
            color: {c['text_primary']};
            font-family: {f['body']};
            font-size: {FONT_SIZES['body']}px;
        }}

        /* ── Labels ── */
        QLabel {{
            color: {c['text_primary']};
            background: transparent;
        }}

        /* ── Line Edit / Text Edit ── */
        QLineEdit, QTextEdit, QPlainTextEdit {{
            background-color: {c['input_bg']};
            color: {c['text_primary']};
            border: 1px solid {c['border']};
            border-radius: {BORDER_RADIUS['sm']}px;
            padding: 8px 12px;
            font-size: {FONT_SIZES['body']}px;
            selection-background-color: {c['accent']};
        }}
        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
            border-color: {c['accent']};
        }}

        /* ── ComboBox ── */
        QComboBox {{
            background-color: {c['input_bg']};
            color: {c['text_primary']};
            border: 1px solid {c['border']};
            border-radius: {BORDER_RADIUS['sm']}px;
            padding: 8px 12px;
            min-width: 120px;
        }}
        QComboBox:focus {{
            border-color: {c['accent']};
        }}
        QComboBox::drop-down {{
            border: none;
            width: 30px;
        }}
        QComboBox QAbstractItemView {{
            background-color: {c['card_bg']};
            color: {c['text_primary']};
            border: 1px solid {c['border']};
            selection-background-color: {c['accent']};
        }}

        /* ── SpinBox / DateEdit ── */
        QSpinBox, QDoubleSpinBox, QDateEdit {{
            background-color: {c['input_bg']};
            color: {c['text_primary']};
            border: 1px solid {c['border']};
            border-radius: {BORDER_RADIUS['sm']}px;
            padding: 6px 10px;
        }}
        QSpinBox:focus, QDoubleSpinBox:focus, QDateEdit:focus {{
            border-color: {c['accent']};
        }}

        /* ── Table ── */
        QTableWidget, QTableView {{
            background-color: {c['card_bg']};
            color: {c['text_primary']};
            border: 1px solid {c['border']};
            border-radius: {BORDER_RADIUS['sm']}px;
            gridline-color: {c['border']};
            selection-background-color: {c['accent']};
            selection-color: {c['background']};
            alternate-background-color: {c['sidebar_bg']};
        }}
        QHeaderView::section {{
            background-color: {c['sidebar_bg']};
            color: {c['accent']};
            border: 1px solid {c['border']};
            padding: 8px;
            font-weight: bold;
            font-size: {FONT_SIZES['body']}px;
        }}

        /* ── Scroll Bars ── */
        QScrollBar:vertical {{
            background: {c['background']};
            width: 10px;
            border-radius: 5px;
        }}
        QScrollBar::handle:vertical {{
            background: {c['border']};
            border-radius: 5px;
            min-height: 30px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: {c['text_muted']};
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0;
        }}
        QScrollBar:horizontal {{
            background: {c['background']};
            height: 10px;
            border-radius: 5px;
        }}
        QScrollBar::handle:horizontal {{
            background: {c['border']};
            border-radius: 5px;
            min-width: 30px;
        }}

        /* ── Tab Widget ── */
        QTabWidget::pane {{
            border: 1px solid {c['border']};
            border-radius: {BORDER_RADIUS['sm']}px;
            background: {c['background']};
        }}
        QTabBar::tab {{
            background: {c['card_bg']};
            color: {c['text_muted']};
            border: 1px solid {c['border']};
            padding: 10px 20px;
            margin-right: 2px;
            border-top-left-radius: {BORDER_RADIUS['sm']}px;
            border-top-right-radius: {BORDER_RADIUS['sm']}px;
        }}
        QTabBar::tab:selected {{
            background: {c['background']};
            color: {c['accent']};
            border-bottom-color: {c['background']};
        }}

        /* ── GroupBox ── */
        QGroupBox {{
            border: 1px solid {c['border']};
            border-radius: {BORDER_RADIUS['md']}px;
            margin-top: 16px;
            padding-top: 20px;
            font-weight: bold;
            color: {c['accent']};
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top right;
            padding: 4px 12px;
        }}

        /* ── Message Box ── */
        QMessageBox {{
            background-color: {c['card_bg']};
        }}
        QMessageBox QLabel {{
            color: {c['text_primary']};
            font-size: {FONT_SIZES['body']}px;
        }}

        /* ── ToolTip ── */
        QToolTip {{
            background-color: {c['card_bg']};
            color: {c['text_primary']};
            border: 1px solid {c['accent']};
            padding: 6px;
            border-radius: 4px;
        }}

        /* ── CheckBox / Radio ── */
        QCheckBox, QRadioButton {{
            color: {c['text_primary']};
            spacing: 8px;
        }}
        QCheckBox::indicator, QRadioButton::indicator {{
            width: 18px;
            height: 18px;
        }}
    """
