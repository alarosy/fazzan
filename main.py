"""
المنظومة — نظام إدارة مركز التدريب والخدمات اللوجستية.
Entry point for the desktop application.

نقطة الدخول الرئيسية: تهيئة قاعدة البيانات → تشغيل الترحيلات → إطلاق الواجهة.
"""
import sys
import os

# Ensure project root is in Python path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, QLocale
from PyQt5.QtGui import QFont, QFontDatabase

from core.database import init_db
from core.migrate import run_migrations
from ui.main_window import MainWindow
from ui.styles import get_global_stylesheet


def load_fonts():
    """Load custom Arabic fonts if available in assets/fonts/."""
    fonts_dir = os.path.join(PROJECT_ROOT, "assets", "fonts")
    if os.path.isdir(fonts_dir):
        for filename in os.listdir(fonts_dir):
            if filename.lower().endswith((".ttf", ".otf")):
                font_path = os.path.join(fonts_dir, filename)
                font_id = QFontDatabase.addApplicationFont(font_path)
                if font_id >= 0:
                    families = QFontDatabase.applicationFontFamilies(font_id)
                    print(f"[font] Loaded: {', '.join(families)}")


def main():
    # ── Initialize Database ──
    print("[init] Initializing database...")
    init_db()
    
    # ── Run Migrations ──
    print("[init] Running migrations...")
    run_migrations()
    
    # ── Create Application ──
    app = QApplication(sys.argv)
    
    # Set RTL layout for entire application
    app.setLayoutDirection(Qt.RightToLeft)
    
    # Set Arabic locale
    locale = QLocale(QLocale.Arabic, QLocale.Libya)
    QLocale.setDefault(locale)
    
    # Load custom fonts
    load_fonts()
    
    # Apply global stylesheet
    app.setStyleSheet(get_global_stylesheet())
    
    # Set default font
    default_font = QFont("Cairo", 12)
    default_font.setStyleStrategy(QFont.PreferAntialias)
    app.setFont(default_font)
    
    # ── Create and Show Main Window ──
    window = MainWindow()
    window.showMaximized()
    
    print("[init] Application started successfully")
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
