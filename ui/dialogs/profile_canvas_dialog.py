"""
Profile Canvas Dialog — ملف السيرة الذاتية والبيانات الشخصية للمدرب أو المستشار.
"""
import os
import shutil
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QFileDialog,
    QFrame, QWidget, QFormLayout, QSizePolicy
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QPixmap, QCursor

from ui.styles import COLORS, FONTS, FONT_SIZES, SPACING, BORDER_RADIUS
from ui.button_utils import create_button, BUTTON_PRIMARY


class ProfileCanvasDialog(QDialog):
    """لوحة تعريعية تفاعلية للمدرب/المستشار تدعم رفع صورة شخصية."""

    def __init__(self, person, person_type="trainer", parent=None):
        super().__init__(parent)
        self.person = person
        self.person_type = person_type
        
        display_type = "مدرب" if person_type == "trainer" else "مستشار"
        self.setWindowTitle(f"الملف التعريفي لل{display_type}: {person.name}")
        self.setMinimumSize(500, 580)
        self.setLayoutDirection(Qt.RightToLeft)
        
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS['background']};
                color: {COLORS['text_primary']};
            }}
        """)
        
        self._setup_ui()
        self._load_photo()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING["xl"], SPACING["xl"], SPACING["xl"], SPACING["xl"])
        layout.setSpacing(SPACING["lg"])
        layout.setAlignment(Qt.AlignHCenter)

        # ── Profile Photo Section (Interactive Circle) ──
        self.photo_label = QLabel()
        self.photo_label.setFixedSize(130, 130)
        self.photo_label.setCursor(QCursor(Qt.PointingHandCursor))
        self.photo_label.setAlignment(Qt.AlignCenter)
        self.photo_label.setToolTip("انقر هنا لرفع أو تغيير الصورة الشخصية")
        self.photo_label.mousePressEvent = self._on_photo_clicked
        layout.addWidget(self.photo_label)

        # Help label under photo
        photo_help = QLabel("انقر على الدائرة لرفع صورة شخصية")
        photo_help.setFont(QFont(FONTS["body"].split(",")[0], FONT_SIZES["tiny"]))
        photo_help.setStyleSheet(f"color: {COLORS['text_muted']}; background: transparent; border: none;")
        photo_help.setAlignment(Qt.AlignCenter)
        layout.addWidget(photo_help)

        # ── Profile Details Card ──
        card = QFrame()
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['card_bg']};
                border: 1px solid {COLORS['border']};
                border-radius: {BORDER_RADIUS['lg']}px;
            }}
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(SPACING["lg"], SPACING["lg"], SPACING["lg"], SPACING["lg"])
        card_layout.setSpacing(SPACING["md"])
        card_layout.setAlignment(Qt.AlignTop)

        # Centered Name
        name_lbl = QLabel(self.person.name)
        name_lbl.setFont(QFont(FONTS["display"].split(",")[0], FONT_SIZES["h2"], QFont.Bold))
        name_lbl.setStyleSheet(f"color: {COLORS['accent']}; border: none; background: transparent;")
        name_lbl.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(name_lbl)

        # Specialty Badge / Specialization
        spec_text = self.person.specialization
        # Handle if it is an Enum in consultant
        if hasattr(spec_text, "value"):
            spec_text = spec_text.value
        spec_lbl = QLabel(f"🎓 التخصص: {spec_text or 'عام'}")
        spec_lbl.setFont(QFont(FONTS["body"].split(",")[0], FONT_SIZES["body"], QFont.Bold))
        spec_lbl.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            background-color: {COLORS['background']};
            padding: 6px 12px;
            border-radius: {BORDER_RADIUS['sm']}px;
            border: 1px solid {COLORS['border']};
        """)
        spec_lbl.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(spec_lbl)

        # Info Grid
        grid = QFormLayout()
        grid.setSpacing(SPACING["sm"])
        grid.setLabelAlignment(Qt.AlignRight)
        
        self.phone_lbl = QLabel(self.person.phone or "غير متوفر")
        self.phone_lbl.setFont(QFont(FONTS["body"].split(",")[0], FONT_SIZES["body"]))
        self.phone_lbl.setStyleSheet("border: none; background: transparent;")
        grid.addRow("📞 الهاتف:", self.phone_lbl)
        
        self.email_lbl = QLabel(self.person.email or "غير متوفر")
        self.email_lbl.setFont(QFont(FONTS["body"].split(",")[0], FONT_SIZES["body"]))
        self.email_lbl.setStyleSheet("border: none; background: transparent;")
        grid.addRow("✉️ البريد الإلكتروني:", self.email_lbl)

        if self.person_type == "trainer":
            status_text = "نشط ومتاح للتدريب" if self.person.is_active else "غير متاح حالياً"
            self.status_lbl = QLabel(status_text)
            self.status_lbl.setFont(QFont(FONTS["body"].split(",")[0], FONT_SIZES["body"]))
            self.status_lbl.setStyleSheet("border: none; background: transparent;")
            grid.addRow("⚙️ حالة العمل:", self.status_lbl)
        else:
            # Consultant contract details
            start_str = str(self.person.contract_start or "-")
            end_str = str(self.person.contract_end or "-")
            self.contract_lbl = QLabel(f"من {start_str} إلى {end_str}")
            self.contract_lbl.setFont(QFont(FONTS["body"].split(",")[0], FONT_SIZES["body"]))
            self.contract_lbl.setStyleSheet("border: none; background: transparent;")
            grid.addRow("📅 فترة التعاقد:", self.contract_lbl)

        card_layout.addLayout(grid)

        # Bio / Biography (نبذة تعريفية)
        bio_title = QLabel("📝 نبذة تعريفية / السيرة الذاتية:")
        bio_title.setFont(QFont(FONTS["body"].split(",")[0], FONT_SIZES["small"], QFont.Bold))
        bio_title.setStyleSheet(f"color: {COLORS['text_muted']}; border: none; background: transparent;")
        card_layout.addWidget(bio_title)

        bio_content = self.person.bio if self.person_type == "trainer" else self.person.service_detail
        self.bio_lbl = QLabel(bio_content or "لا توجد سيرة ذاتية مسجلة حالياً.")
        self.bio_lbl.setFont(QFont(FONTS["body"].split(",")[0], FONT_SIZES["body"]))
        self.bio_lbl.setStyleSheet(f"""
            QLabel {{
                background-color: {COLORS['background']};
                border: 1px solid {COLORS['border']};
                border-radius: {BORDER_RADIUS['md']}px;
                padding: {SPACING['md']}px;
                color: {COLORS['text_primary']};
            }}
        """)
        self.bio_lbl.setWordWrap(True)
        self.bio_lbl.setMinimumHeight(100)
        self.bio_lbl.setAlignment(Qt.AlignTop | Qt.AlignRight)
        card_layout.addWidget(self.bio_lbl)

        layout.addWidget(card)

        # ── Footer Button ──
        footer = QHBoxLayout()
        close_btn = create_button("إغلاق الملف", BUTTON_PRIMARY)
        close_btn.clicked.connect(self.accept)
        footer.addStretch()
        footer.addWidget(close_btn)
        layout.addLayout(footer)

    def _load_photo(self):
        """تحميل وعرض الصورة الشخصية أو عرض الحرف الأول كحالة افتراضية."""
        if self.person.image_path and os.path.exists(self.person.image_path):
            pixmap = QPixmap(self.person.image_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(130, 130, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
                self.photo_label.setPixmap(scaled_pixmap)
                
                # Apply circular crop using stylesheet
                self.photo_label.setStyleSheet(f"""
                    border-radius: 65px;
                    border: 3px solid {COLORS['accent']};
                    background-color: {COLORS['card_bg']};
                """)
                return

        # Default premium placeholder (Initials)
        initial = (self.person.name[0] if self.person.name else "👤").upper()
        self.photo_label.setText(initial)
        self.photo_label.setFont(QFont(FONTS["display"].split(",")[0], 36, QFont.Bold))
        self.photo_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['accent']};
                background-color: {COLORS['card_bg']};
                border: 3px dashed {COLORS['border']};
                border-radius: 65px;
            }}
            QLabel:hover {{
                border-color: {COLORS['accent']};
            }}
        """)

    def _on_photo_clicked(self, event):
        """فتح نافذة اختيار صورة ونسخها محلياً وحفظ المسار في قاعدة البيانات."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "اختر الصورة الشخصية", "", "Images (*.png *.jpg *.jpeg *.bmp)"
        )
        if not file_path:
            return

        try:
            # Create local storage directory
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            dest_dir = os.path.join(project_root, "assets", "profiles")
            os.makedirs(dest_dir, exist_ok=True)

            # Build destination path
            _, ext = os.path.splitext(file_path)
            filename = f"{self.person_type}_{self.person.id}{ext.lower()}"
            dest_path = os.path.join(dest_dir, filename)

            # Copy file
            shutil.copy2(file_path, dest_path)

            # Update database record
            new_image_path = os.path.relative_path = dest_path
            
            if self.person_type == "trainer":
                import services.training_service as training_svc
                training_svc.update_trainer(self.person.id, {"image_path": new_image_path})
            else:
                import services.consultant_service as consultant_svc
                consultant_svc.update_consultant(self.person.id, {"image_path": new_image_path})

            # Update local state and reload UI
            self.person.image_path = new_image_path
            self._load_photo()

        except Exception as e:
            print(f"Error copying profile photo: {e}")
