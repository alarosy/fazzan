"""
Document export utilities (PDF, Word, CSV, JSON).
أدوات تصدير المستندات — PDF بواسطة ReportLab، Word بواسطة python-docx.
"""
import os
import json
from datetime import datetime
from decimal import Decimal

# Export directory
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPORTS_DIR = os.path.join(_PROJECT_ROOT, "exports")
ASSETS_DIR = os.path.join(_PROJECT_ROOT, "assets")
LOGO_PATH = os.path.join(ASSETS_DIR, "logo.png")


def ensure_exports_dir():
    """Create exports/ directory if it doesn't exist."""
    os.makedirs(EXPORTS_DIR, exist_ok=True)


def generate_reference_number(prefix: str, sequence: int) -> str:
    """توليد رقم مرجعي تسلسلي."""
    year = datetime.now().year
    return f"{prefix}-{year}-{sequence:04d}"


def export_to_json(data: dict, filename: str) -> str:
    """تصدير البيانات إلى ملف JSON."""
    ensure_exports_dir()
    filepath = os.path.join(EXPORTS_DIR, f"{filename}.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)
    return filepath


def export_to_csv(rows: list, headers: list, filename: str) -> str:
    """تصدير البيانات إلى ملف CSV."""
    import csv
    ensure_exports_dir()
    filepath = os.path.join(EXPORTS_DIR, f"{filename}.csv")
    with open(filepath, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)
    return filepath


# ─── PDF Exporters ─────────────────────────────────────────────────────────

def export_proposal_pdf(proposal_id: int) -> str:
    """تصدير عرض السعر بصيغة PDF."""
    from core.database import get_session
    from models.financial_proposal import FinancialProposal
    from sqlalchemy.orm import joinedload
    
    with get_session() as session:
        p = session.query(FinancialProposal).options(
            joinedload(FinancialProposal.client),
            joinedload(FinancialProposal.line_items)
        ).filter(FinancialProposal.id == proposal_id).first()
        
        if not p:
            raise ValueError("عرض السعر غير موجود")
            
        ensure_exports_dir()
        filename = f"proposal_{p.proposal_number.replace('-', '_')}.pdf"
        filepath = os.path.join(EXPORTS_DIR, filename)
        
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        
        c = canvas.Canvas(filepath, pagesize=letter)
        width, height = letter
        
        # Header / Logo placeholder
        c.setStrokeColorRGB(0.12, 0.45, 0.36) # Accent Color
        c.setLineWidth(4)
        c.line(50, height - 50, width - 50, height - 50)
        
        c.setFont("Helvetica-Bold", 24)
        c.setFillColorRGB(0.12, 0.45, 0.36)
        c.drawString(50, height - 90, "FINANCIAL PROPOSAL")
        
        c.setFont("Helvetica", 10)
        c.setFillColorRGB(0.3, 0.3, 0.3)
        c.drawRightString(width - 50, height - 75, "Al-Markaz Training Center")
        c.drawRightString(width - 50, height - 90, "Tripoli, Libya")
        
        c.setLineWidth(1)
        c.setStrokeColorRGB(0.8, 0.8, 0.8)
        c.line(50, height - 105, width - 50, height - 105)
        
        # Meta Info
        c.setFont("Helvetica-Bold", 10)
        c.setFillColorRGB(0.1, 0.1, 0.1)
        c.drawString(50, height - 130, f"Proposal No: {p.proposal_number}")
        c.drawString(50, height - 145, f"Date: {p.created_at.strftime('%Y-%m-%d')}")
        c.drawString(50, height - 160, f"Status: {p.status.value if hasattr(p.status, 'value') else p.status}")
        
        # Client Info
        c.drawRightString(width - 50, height - 130, f"Client Name: {p.client.name if p.client else 'N/A'}")
        c.drawRightString(width - 50, height - 145, f"Service Type: {p.service_type.value if hasattr(p.service_type, 'value') else p.service_type}")
        
        c.line(50, height - 180, width - 50, height - 180)
        
        # Table Headers
        c.setFont("Helvetica-Bold", 10)
        c.setFillColorRGB(0.12, 0.45, 0.36)
        c.drawString(50, height - 200, "Service / Item Description")
        c.drawString(280, height - 200, "Unit")
        c.drawString(360, height - 200, "Qty")
        c.drawString(420, height - 200, "Unit Price")
        c.drawRightString(width - 50, height - 200, "Total")
        
        c.setStrokeColorRGB(0.12, 0.45, 0.36)
        c.line(50, height - 210, width - 50, height - 210)
        
        # Rows
        c.setFont("Helvetica", 9)
        c.setFillColorRGB(0.2, 0.2, 0.2)
        y = height - 230
        
        for item in p.line_items:
            spec_name = item.service_type.value if hasattr(item.service_type, 'value') else str(item.service_type)
            c.drawString(50, y, spec_name)
            c.drawString(280, y, str(item.unit_description))
            c.drawString(360, y, f"{item.quantity:.2f}")
            c.drawString(420, y, f"{item.unit_price:.2f} LYD")
            c.drawRightString(width - 50, y, f"{item.total:.2f} LYD")
            
            y -= 20
            if y < 100:
                c.showPage()
                y = height - 100
                c.setFont("Helvetica", 9)
                
        c.setStrokeColorRGB(0.8, 0.8, 0.8)
        c.line(50, y + 10, width - 50, y + 10)
        
        # Summary
        y -= 10
        c.setFont("Helvetica-Bold", 11)
        c.setFillColorRGB(0.12, 0.45, 0.36)
        c.drawString(300, y, "Grand Total:")
        c.drawRightString(width - 50, y, f"{p.total_value:.2f} LYD")
        
        # Signature block
        y -= 60
        c.setFont("Helvetica", 9)
        c.setFillColorRGB(0.4, 0.4, 0.4)
        c.drawString(50, y, "Prepared By: _________________")
        c.drawRightString(width - 50, y, "Approved By: _________________")
        
        c.save()
        return filepath


def export_invoice_pdf(invoice_id: int) -> str:
    """تصدير الفاتورة الصادرة بصيغة PDF."""
    from core.database import get_session
    from models.invoice import Invoice
    from sqlalchemy.orm import joinedload
    
    with get_session() as session:
        inv = session.query(Invoice).options(
            joinedload(Invoice.client),
            joinedload(Invoice.line_items)
        ).filter(Invoice.id == invoice_id).first()
        
        if not inv:
            raise ValueError("الفاتورة غير موجودة")
            
        ensure_exports_dir()
        filename = f"invoice_{inv.invoice_number.replace('-', '_')}.pdf"
        filepath = os.path.join(EXPORTS_DIR, filename)
        
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        
        c = canvas.Canvas(filepath, pagesize=letter)
        width, height = letter
        
        # Layout
        c.setStrokeColorRGB(0.12, 0.45, 0.36)
        c.setLineWidth(4)
        c.line(50, height - 50, width - 50, height - 50)
        
        c.setFont("Helvetica-Bold", 24)
        c.setFillColorRGB(0.12, 0.45, 0.36)
        c.drawString(50, height - 90, "FINAL INVOICE")
        
        c.setFont("Helvetica", 10)
        c.setFillColorRGB(0.3, 0.3, 0.3)
        c.drawRightString(width - 50, height - 75, "Al-Markaz Training Center")
        c.drawRightString(width - 50, height - 90, "Tripoli, Libya")
        
        c.setLineWidth(1)
        c.setStrokeColorRGB(0.8, 0.8, 0.8)
        c.line(50, height - 105, width - 50, height - 105)
        
        # Invoice metadata
        c.setFont("Helvetica-Bold", 10)
        c.setFillColorRGB(0.1, 0.1, 0.1)
        c.drawString(50, height - 130, f"Invoice No: {inv.invoice_number}")
        c.drawString(50, height - 145, f"Date: {inv.created_at.strftime('%Y-%m-%d')}")
        
        c.drawRightString(width - 50, height - 130, f"Client Name: {inv.client.name if inv.client else 'N/A'}")
        
        c.line(50, height - 170, width - 50, height - 170)
        
        # Table Headers
        c.setFont("Helvetica-Bold", 10)
        c.setFillColorRGB(0.12, 0.45, 0.36)
        c.drawString(50, height - 190, "Item Details")
        c.drawString(280, height - 190, "Unit")
        c.drawString(360, height - 190, "Qty")
        c.drawString(420, height - 190, "Unit Price")
        c.drawRightString(width - 50, height - 190, "Total")
        
        c.line(50, height - 200, width - 50, height - 200)
        
        # Rows
        c.setFont("Helvetica", 9)
        c.setFillColorRGB(0.2, 0.2, 0.2)
        y = height - 220
        
        for item in inv.line_items:
            spec_name = item.service_type.value if hasattr(item.service_type, 'value') else str(item.service_type)
            c.drawString(50, y, spec_name)
            c.drawString(280, y, str(item.unit_description))
            c.drawString(360, y, f"{item.quantity:.2f}")
            c.drawString(420, y, f"{item.unit_price:.2f} LYD")
            c.drawRightString(width - 50, y, f"{item.total:.2f} LYD")
            y -= 20
            
        c.line(50, y + 10, width - 50, y + 10)
        
        # Summary
        y -= 10
        c.setFont("Helvetica-Bold", 11)
        c.setFillColorRGB(0.12, 0.45, 0.36)
        c.drawString(300, y, "Amount Due:")
        c.drawRightString(width - 50, y, f"{inv.total_value:.2f} LYD")
        
        # Signature
        y -= 60
        c.setFont("Helvetica", 9)
        c.setFillColorRGB(0.4, 0.4, 0.4)
        c.drawString(50, y, "Accountant Signature: _________________")
        c.drawRightString(width - 50, y, "Recipient Signature: _________________")
        
        c.save()
        return filepath


def export_voucher_pdf(voucher_id: int) -> str:
    """تصدير السند المالي (سند قبض أو سند صرف) بصيغة PDF."""
    from core.database import get_session
    from models.voucher import Voucher
    from models.enums import VoucherType
    
    with get_session() as session:
        v = session.query(Voucher).filter(Voucher.id == voucher_id).first()
        if not v:
            raise ValueError("السند غير موجود")
            
        ensure_exports_dir()
        filename = f"voucher_{v.voucher_number.replace('-', '_')}.pdf"
        filepath = os.path.join(EXPORTS_DIR, filename)
        
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        
        c = canvas.Canvas(filepath, pagesize=letter)
        width, height = letter
        
        # Accent color depending on Voucher Type (Receipt = Green, Disbursement = Red)
        is_receipt = v.voucher_type == VoucherType.RECEIPT
        color = (0.12, 0.45, 0.36) if is_receipt else (0.7, 0.15, 0.15)
        title = "RECEIPT VOUCHER" if is_receipt else "DISBURSEMENT VOUCHER"
        
        c.setStrokeColorRGB(*color)
        c.setLineWidth(4)
        c.line(50, height - 50, width - 50, height - 50)
        
        c.setFont("Helvetica-Bold", 22)
        c.setFillColorRGB(*color)
        c.drawString(50, height - 90, title)
        
        c.setFont("Helvetica", 10)
        c.setFillColorRGB(0.3, 0.3, 0.3)
        c.drawRightString(width - 50, height - 75, "Al-Markaz Training Center")
        c.drawRightString(width - 50, height - 90, "Tripoli, Libya")
        
        c.setLineWidth(1)
        c.setStrokeColorRGB(0.8, 0.8, 0.8)
        c.line(50, height - 105, width - 50, height - 105)
        
        # Meta info
        c.setFont("Helvetica-Bold", 10)
        c.setFillColorRGB(0.1, 0.1, 0.1)
        c.drawString(50, height - 130, f"Voucher No: {v.voucher_number}")
        c.drawString(50, height - 145, f"Date: {v.created_at.strftime('%Y-%m-%d')}")
        
        # Payment details
        c.setFont("Helvetica", 10)
        c.drawString(50, height - 180, f"Paid To / Received From: {v.party_name}")
        c.drawString(50, height - 200, f"Amount: {v.amount:.2f} LYD")
        
        pay_method_val = v.payment_method.value if hasattr(v.payment_method, 'value') else str(v.payment_method)
        c.drawString(50, height - 220, f"Payment Method: {pay_method_val}")
        
        # Description / Notes
        c.drawString(50, height - 250, "Description / Notes:")
        c.setFont("Helvetica-Oblique", 9)
        c.drawString(70, height - 265, v.notes or "No additional notes provided.")
        
        # Words Tafqit
        c.setFont("Helvetica-Bold", 9)
        c.drawString(50, height - 300, f"Amount in Words: {v.amount_in_words}")
        
        # Signatures
        y = height - 360
        c.setFont("Helvetica", 9)
        c.setFillColorRGB(0.4, 0.4, 0.4)
        c.drawString(50, y, "Cashier / Auditor: _________________")
        c.drawRightString(width - 50, y, "Manager Signature: _________________")
        
        c.save()
        return filepath
