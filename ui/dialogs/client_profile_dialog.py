"""
Client Profile Dialog — ملف العميل المالي والقانوني.
"""
from decimal import Decimal
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QHeaderView, QTabWidget, QFrame, QWidget,
    QFormLayout
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from ui.styles import COLORS, FONTS, FONT_SIZES, SPACING, BORDER_RADIUS
from ui.button_utils import create_button, BUTTON_PRIMARY
from core.database import get_session
from models.contract import Contract
from models.invoice import Invoice
from models.voucher import Voucher
from models.project import Project


class ClientProfileDialog(QDialog):
    """ملف العميل الموحد (Account File)."""

    def __init__(self, client, parent=None):
        super().__init__(parent)
        self.client = client
        self.setWindowTitle(f"ملف العميل: {client.name}")
        self.setMinimumSize(850, 600)
        self.setLayoutDirection(Qt.RightToLeft)
        
        # Stylesheet using current colors
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS['background']};
                color: {COLORS['text_primary']};
            }}
            QTabWidget::pane {{
                border: 1px solid {COLORS['border']};
                border-radius: {BORDER_RADIUS['md']}px;
                background-color: {COLORS['card_bg']};
                padding: {SPACING['md']}px;
            }}
            QTabBar::tab {{
                background-color: {COLORS['card_bg']};
                color: {COLORS['text_muted']};
                border: 1px solid {COLORS['border']};
                border-bottom: none;
                border-top-left-radius: {BORDER_RADIUS['sm']}px;
                border-top-right-radius: {BORDER_RADIUS['sm']}px;
                padding: 10px 20px;
                margin-left: 4px;
            }}
            QTabBar::tab:selected {{
                background-color: {COLORS['background']};
                color: {COLORS['accent']};
                font-weight: bold;
                border-bottom: 2px solid {COLORS['accent']};
            }}
        """)
        
        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING["lg"], SPACING["lg"], SPACING["lg"], SPACING["lg"])
        layout.setSpacing(SPACING["md"])

        # ── Header Profile Card ──
        header_card = QFrame()
        header_card.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['card_bg']};
                border: 1px solid {COLORS['border']};
                border-radius: {BORDER_RADIUS['md']}px;
            }}
        """)
        header_layout = QHBoxLayout(header_card)
        header_layout.setContentsMargins(SPACING["lg"], SPACING["md"], SPACING["lg"], SPACING["md"])
        
        info_layout = QVBoxLayout()
        info_layout.setSpacing(SPACING["xs"])
        
        # Client name
        name_lbl = QLabel(self.client.name)
        name_lbl.setFont(QFont(FONTS["display"].split(",")[0], FONT_SIZES["h2"], QFont.Bold))
        name_lbl.setStyleSheet(f"color: {COLORS['accent']}; background: transparent; border: none;")
        info_layout.addWidget(name_lbl)
        
        # Sector & Type
        c_type = self.client.client_type.value if hasattr(self.client.client_type, "value") else str(self.client.client_type)
        c_sector = self.client.sector.value if (hasattr(self.client, "sector") and hasattr(self.client.sector, "value")) else str(self.client.sector or "غير محدد")
        meta_lbl = QLabel(f"🏢 النوع: {c_type} | القطاع: {c_sector}")
        meta_lbl.setFont(QFont(FONTS["body"].split(",")[0], FONT_SIZES["small"]))
        meta_lbl.setStyleSheet(f"color: {COLORS['text_muted']}; background: transparent; border: none;")
        info_layout.addWidget(meta_lbl)
        
        # Phone & Email
        contact_lbl = QLabel(f"📞 هاتف: {self.client.phone or 'غير متوفر'} | ✉️ بريد: {self.client.email or 'غير متوفر'}")
        contact_lbl.setFont(QFont(FONTS["body"].split(",")[0], FONT_SIZES["small"]))
        contact_lbl.setStyleSheet(f"color: {COLORS['text_muted']}; background: transparent; border: none;")
        info_layout.addWidget(contact_lbl)

        header_layout.addLayout(info_layout)
        header_layout.addStretch()

        # Address card
        address_layout = QVBoxLayout()
        address_layout.setAlignment(Qt.AlignLeft)
        addr_title = QLabel("📍 العنوان:")
        addr_title.setFont(QFont(FONTS["body"].split(",")[0], FONT_SIZES["small"], QFont.Bold))
        addr_title.setStyleSheet(f"color: {COLORS['text_primary']}; background: transparent; border: none;")
        address_layout.addWidget(addr_title)
        
        addr_val = QLabel(self.client.address or "لا يوجد عنوان مسجل")
        addr_val.setFont(QFont(FONTS["body"].split(",")[0], FONT_SIZES["small"]))
        addr_val.setStyleSheet(f"color: {COLORS['text_muted']}; background: transparent; border: none;")
        addr_val.setWordWrap(True)
        address_layout.addWidget(addr_val)
        
        header_layout.addLayout(address_layout)
        layout.addWidget(header_card)

        # ── Tabbed View ──
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Tab 1: Contracts Table
        self.contracts_table = QTableWidget()
        self.contracts_table.setColumnCount(5)
        self.contracts_table.setHorizontalHeaderLabels(["عنوان العقد", "القيمة", "تاريخ البدء", "تاريخ الانتهاء", "الحالة"])
        self.contracts_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.contracts_table.verticalHeader().setVisible(False)
        self.contracts_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.contracts_table.setAlternatingRowColors(True)
        self.tabs.addTab(self.contracts_table, "📋  العقود المبرمة")

        # Tab 2: Financial Ledger
        self.ledger_table = QTableWidget()
        self.ledger_table.setColumnCount(5)
        self.ledger_table.setHorizontalHeaderLabels(["نوع الحركة", "رقم المستند", "القيمة", "التاريخ", "ملاحظات"])
        self.ledger_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ledger_table.verticalHeader().setVisible(False)
        self.ledger_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.ledger_table.setAlternatingRowColors(True)
        self.tabs.addTab(self.ledger_table, "💰  السجل المالي للمدفوعات")

        # Tab 3: Projects list
        self.projects_table = QTableWidget()
        self.projects_table.setColumnCount(4)
        self.projects_table.setHorizontalHeaderLabels(["اسم المشروع", "الميزانية المرصودة", "المصروف الفعلي", "حالة المشروع"])
        self.projects_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.projects_table.verticalHeader().setVisible(False)
        self.projects_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.projects_table.setAlternatingRowColors(True)
        self.tabs.addTab(self.projects_table, "📊  المشاريع المرتبطة")

        # ── Footer close button ──
        footer = QHBoxLayout()
        close_btn = create_button("إغلاق الملف", BUTTON_PRIMARY)
        close_btn.clicked.connect(self.accept)
        footer.addStretch()
        footer.addWidget(close_btn)
        layout.addLayout(footer)

    def _load_data(self):
        with get_session() as session:
            # 1. Load Contracts
            contracts = session.query(Contract).filter(
                Contract.client_id == self.client.id,
                Contract.is_deleted == False  # noqa: E712
            ).all()

            self.contracts_table.setRowCount(len(contracts))
            project_ids = []
            for row, c in enumerate(contracts):
                if c.project_id:
                    project_ids.append(c.project_id)
                self.contracts_table.setItem(row, 0, QTableWidgetItem(c.title or ""))
                self.contracts_table.setItem(row, 1, QTableWidgetItem(f"{c.value:,.2f} LYD"))
                self.contracts_table.setItem(row, 2, QTableWidgetItem(str(c.start_date or "-")))
                self.contracts_table.setItem(row, 3, QTableWidgetItem(str(c.end_date or "-")))
                
                status_val = c.status.value if hasattr(c.status, "value") else str(c.status)
                self.contracts_table.setItem(row, 4, QTableWidgetItem(status_val))

            # 2. Load Invoices and Vouchers
            invoices = session.query(Invoice).filter(Invoice.client_id == self.client.id).all()
            
            # Load Vouchers matching either client name (party_name) or client project IDs
            vouchers_query = session.query(Voucher).filter(
                (Voucher.party_name.ilike(f"%{self.client.name}%"))
            )
            if project_ids:
                vouchers_query = vouchers_query.union(
                    session.query(Voucher).filter(Voucher.project_id.in_(project_ids))
                )
            vouchers = vouchers_query.all()

            # Compile into single ledger list sorted by date
            ledger_items = []
            for inv in invoices:
                ledger_items.append({
                    "type": "فاتورة صادرة",
                    "ref": inv.invoice_number,
                    "amount": inv.total_value,
                    "date": inv.created_at,
                    "notes": "فاتورة مبيعات معتمدة"
                })
            for v in vouchers:
                v_type_str = "سند قبض" if v.voucher_type.value == "receipt" or v.voucher_type == "in" else "سند صرف"
                ledger_items.append({
                    "type": v_type_str,
                    "ref": v.voucher_number,
                    "amount": v.amount,
                    "date": v.created_at,
                    "notes": v.notes or ""
                })

            # Sort ledger by date desc
            ledger_items.sort(key=lambda x: x["date"] or x["ref"], reverse=True)

            self.ledger_table.setRowCount(len(ledger_items))
            for row, item in enumerate(ledger_items):
                self.ledger_table.setItem(row, 0, QTableWidgetItem(item["type"]))
                self.ledger_table.setItem(row, 1, QTableWidgetItem(item["ref"]))
                self.ledger_table.setItem(row, 2, QTableWidgetItem(f"{item['amount']:,.2f} LYD"))
                date_str = item["date"].strftime("%Y-%m-%d") if item["date"] else "-"
                self.ledger_table.setItem(row, 3, QTableWidgetItem(date_str))
                self.ledger_table.setItem(row, 4, QTableWidgetItem(item["notes"]))

            # 3. Load Linked Projects
            if project_ids:
                projects = session.query(Project).filter(
                    Project.id.in_(project_ids),
                    Project.is_deleted == False  # noqa: E712
                ).all()
            else:
                projects = []

            self.projects_table.setRowCount(len(projects))
            for row, p in enumerate(projects):
                self.projects_table.setItem(row, 0, QTableWidgetItem(p.name or ""))
                self.projects_table.setItem(row, 1, QTableWidgetItem(f"{p.budget_allocated or 0:,.2f} LYD"))
                self.projects_table.setItem(row, 2, QTableWidgetItem(f"{p.budget_spent or 0:,.2f} LYD"))
                
                status_lbl = "مفتوح" if not p.is_deleted else "مغلق"
                self.projects_table.setItem(row, 3, QTableWidgetItem(status_lbl))
