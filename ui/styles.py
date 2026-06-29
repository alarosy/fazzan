"""
Central theme and palette constants for the application UI.
ثوابت الألوان والأنماط المركزية للواجهة — تطابق §3.1 من CLAUDE.md.
"""

# ─── Color Palette ───────────────────────────────────────────────────────────
COLORS = {
    "background":   "#0D1B2A",   # كحلي داكن — خلفية رئيسية
    "card_bg":      "#2A3A4A",   # رمادي متوسط — خلفية البطاقات
    "card_hover":   "#344C5E",   # بطاقة عند التمرير
    "accent":       "#C9A96E",   # ذهبي خافت — العناصر البارزة
    "accent_hover": "#D4B87A",   # ذهبي أفتح عند التمرير
    "text_primary": "#F0EDE8",   # أبيض مكسر — النصوص الرئيسية
    "text_muted":   "#8A9BAB",   # رمادي فاتح — النصوص الثانوية
    "alert_bg":     "#3D1A1A",   # أحمر داكن — بطاقات التنبيه
    "alert_hover":  "#4D2525",   # تنبيه عند التمرير
    "success":      "#1A3D2A",   # أخضر داكن — مؤشرات إيجابية
    "success_text": "#4ADE80",   # أخضر فاتح للنص
    "danger":       "#8B1A1A",   # أحمر للحذف
    "danger_hover": "#CC3333",   # أحمر عند التمرير
    "sidebar_bg":   "#0A1628",   # خلفية الشريط الجانبي
    "sidebar_hover":"#1B2B3D",   # شريط جانبي عند التمرير
    "sidebar_active":"#2A3A4A",  # عنصر نشط في الشريط
    "border":       "#3A4A5A",   # حدود خفيفة
    "input_bg":     "#1A2A3A",   # خلفية حقول الإدخال
}

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
    "sm":  6,
    "md":  10,
    "lg":  16,
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
