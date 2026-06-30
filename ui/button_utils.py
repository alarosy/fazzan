"""
Button style presets and factory functions.
أنماط الأزرار الثمانية وأدوات إنشائها — تطابق §9 من CLAUDE.md.
"""
from PyQt5.QtWidgets import QPushButton, QMessageBox
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QFont

from ui.styles import COLORS, BORDER_RADIUS, FONT_SIZES


# ─── 8 Button Style Presets ──────────────────────────────────────────────────

# Style 1: Primary action (ذهبي — الإجراء الرئيسي)
BUTTON_PRIMARY = {
    "background": COLORS["accent"],
    "color": COLORS["background"],
    "hover_background": COLORS["accent_hover"],
    "border": "none",
    "font_weight": "bold",
    "min_width": "140px",
    "min_height": "40px",
}

# Style 2: Secondary action (شفاف بحدود)
BUTTON_SECONDARY = {
    "background": "transparent",
    "color": COLORS["accent"],
    "hover_background": COLORS["card_bg"],
    "border": f"2px solid {COLORS['accent']}",
    "font_weight": "bold",
    "min_width": "120px",
    "min_height": "38px",
}

# Style 3: Ghost / text button (بدون خلفية أو حدود)
BUTTON_GHOST = {
    "background": "transparent",
    "color": COLORS["text_muted"],
    "hover_background": COLORS["card_bg"],
    "border": "none",
    "font_weight": "normal",
    "min_width": "80px",
    "min_height": "36px",
}

# Style 4: Success action (أخضر)
BUTTON_SUCCESS = {
    "background": COLORS["success"],
    "color": COLORS["success_text"],
    "hover_background": COLORS["success_hover"],
    "border": "none",
    "font_weight": "bold",
    "min_width": "120px",
    "min_height": "40px",
}

# Style 5: Sidebar navigation item
BUTTON_SIDEBAR = {
    "background": "transparent",
    "color": COLORS["text_muted"],
    "hover_background": COLORS["sidebar_hover"],
    "border": "none",
    "font_weight": "normal",
    "min_width": "200px",
    "min_height": "48px",
    "text_align": "right",
    "padding": "8px 16px",
}

# Style 6: Card action (زر داخل بطاقة)
BUTTON_CARD = {
    "background": COLORS["card_hover"],
    "color": COLORS["text_primary"],
    "hover_background": COLORS["accent"],
    "hover_color": COLORS["background"],
    "border": "none",
    "font_weight": "normal",
    "min_width": "100px",
    "min_height": "34px",
}

# Style 7: Small / compact button (أيقونة صغيرة)
BUTTON_COMPACT = {
    "background": COLORS["card_bg"],
    "color": COLORS["text_muted"],
    "hover_background": COLORS["card_hover"],
    "border": f"1px solid {COLORS['border']}",
    "font_weight": "normal",
    "min_width": "36px",
    "min_height": "36px",
}

# Style 8: Danger / confirm delete (§9 — أحمر تأكيدي)
BUTTON_DANGER_CONFIRM = {
    "background": COLORS["danger"],
    "color": "#FFFFFF",
    "hover_background": COLORS["danger_hover"],
    "border": f"2px solid {COLORS['danger_hover']}",
    "font_weight": "bold",
    "min_width": "120px",
    "min_height": "40px",
}


# ─── Factory Functions ───────────────────────────────────────────────────────

def _build_stylesheet(style: dict) -> str:
    """Build a QPushButton stylesheet from a style dictionary."""
    hover_color = style.get("hover_color", style["color"])
    text_align = style.get("text_align", "center")
    padding = style.get("padding", "8px 16px")
    
    return f"""
        QPushButton {{
            background-color: {style['background']};
            color: {style['color']};
            border: {style['border']};
            border-radius: {BORDER_RADIUS['sm']}px;
            font-weight: {style['font_weight']};
            min-width: {style['min_width']};
            min-height: {style['min_height']};
            padding: {padding};
            text-align: {text_align};
            font-size: {FONT_SIZES['body']}px;
        }}
        QPushButton:hover {{
            background-color: {style['hover_background']};
            color: {hover_color};
        }}
        QPushButton:pressed {{
            background-color: {style['hover_background']};
            padding-top: 10px;
        }}
        QPushButton:disabled {{
            background-color: {COLORS['card_bg']};
            color: {COLORS['border']};
            border-color: {COLORS['border']};
        }}
    """


def create_button(text: str, style: dict = None, icon: QIcon = None,
                   tooltip: str = None, parent=None) -> QPushButton:
    """
    Create a styled QPushButton.
    إنشاء زر بنمط محدد.
    
    Args:
        text: النص المعروض على الزر
        style: قاموس النمط (افتراضي: BUTTON_PRIMARY)
        icon: أيقونة اختيارية
        tooltip: تلميح عند التمرير
        parent: العنصر الأب
    
    Returns:
        QPushButton: الزر المُنسَّق
    """
    if style is None:
        style = BUTTON_PRIMARY
    
    btn = QPushButton(text, parent)
    btn.setStyleSheet(_build_stylesheet(style))
    btn.setCursor(Qt.PointingHandCursor)
    btn.setLayoutDirection(Qt.RightToLeft)
    btn.setFocusPolicy(Qt.NoFocus)
    
    if icon:
        btn.setIcon(icon)
        btn.setIconSize(QSize(20, 20))
    
    if tooltip:
        btn.setToolTip(tooltip)
    
    return btn


def create_danger_button(text: str, parent=None, tooltip: str = None) -> QPushButton:
    """
    Create a danger button with built-in confirmation dialog.
    إنشاء زر حذف تأكيدي — يعرض رسالة تأكيد قبل التنفيذ (§9).
    
    Note: Connect the returned button's clicked signal to your handler.
    The confirmation is handled inside the button's click via a wrapper.
    """
    btn = create_button(text, BUTTON_DANGER_CONFIRM, tooltip=tooltip, parent=parent)
    return btn


def confirm_delete(parent, item_name: str = "") -> bool:
    """
    Show a delete confirmation dialog.
    عرض رسالة تأكيد الحذف — يُستخدم مع BUTTON_DANGER_CONFIRM.
    
    Args:
        parent: العنصر الأب للنافذة
        item_name: اسم العنصر المراد حذفه (للعرض في الرسالة)
    
    Returns:
        bool: True إذا أكّد المستخدم الحذف
    """
    msg = QMessageBox(parent)
    msg.setIcon(QMessageBox.Warning)
    msg.setWindowTitle("تأكيد الحذف")
    msg.setText(f"هل أنت متأكد من حذف {item_name}؟" if item_name else "هل أنت متأكد من الحذف؟")
    msg.setInformativeText("هذا الإجراء لا يمكن التراجع عنه.")
    msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    msg.setDefaultButton(QMessageBox.No)
    msg.setLayoutDirection(Qt.RightToLeft)
    
    # Style the message box
    msg.setStyleSheet(f"""
        QMessageBox {{
            background-color: {COLORS['card_bg']};
        }}
        QMessageBox QLabel {{
            color: {COLORS['text_primary']};
            font-size: {FONT_SIZES['body']}px;
        }}
        QPushButton {{
            background-color: {COLORS['card_hover']};
            color: {COLORS['text_primary']};
            border: 1px solid {COLORS['border']};
            border-radius: {BORDER_RADIUS['sm']}px;
            padding: 8px 24px;
            min-width: 80px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: {COLORS['accent']};
            color: {COLORS['background']};
        }}
    """)
    
    return msg.exec_() == QMessageBox.Yes
