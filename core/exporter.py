"""
Document export utilities (PDF, Word, CSV, JSON).
أدوات تصدير المستندات — PDF بواسطة ReportLab، Word بواسطة python-docx.
"""
import os
import json
from datetime import datetime
from decimal import Decimal

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import arabic_reshaper
from bidi.algorithm import get_display

# Export directory
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPORTS_DIR = os.path.join(_PROJECT_ROOT, "exports")
ASSETS_DIR = os.path.join(_PROJECT_ROOT, "assets")
LOGO_PATH = os.path.join(ASSETS_DIR, "logo.png")


def register_arabic_font():
    """تسجيل الخطوط العربية لتصدير الـ PDF."""
    local_regular = os.path.join(_PROJECT_ROOT, "assets", "fonts", "tahoma.ttf")
    local_bold = os.path.join(_PROJECT_ROOT, "assets", "fonts", "tahomabd.ttf")
    
    regular_path = local_regular if os.path.exists(local_regular) else "C:\\Windows\\Fonts\\tahoma.ttf"
    bold_path = local_bold if os.path.exists(local_bold) else "C:\\Windows\\Fonts\\tahomabd.ttf"
    
    if os.path.exists(regular_path):
        pdfmetrics.registerFont(TTFont("Arabic", regular_path))
    if os.path.exists(bold_path):
        pdfmetrics.registerFont(TTFont("Arabic-Bold", bold_path))


register_arabic_font()


def reshape_arabic(text: str) -> str:
    """إعادة تشكيل النصوص العربية وتعديل اتجاهها للطباعة الصحيحة."""
    if not text:
        return ""
    text = str(text)
    reshaped_text = arabic_reshaper.reshape(text)
    bidi_text = get_display(reshaped_text)
    return bidi_text



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
    """تصدير عرض السعر بصيغة PDF باللغة العربية والخطوط المناسبة."""
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
        
        c.setFont("Arabic-Bold", 22)
        c.setFillColorRGB(0.12, 0.45, 0.36)
        c.drawString(50, height - 90, reshape_arabic("عرض سعر مالي"))
        
        c.setFont("Arabic", 10)
        c.setFillColorRGB(0.3, 0.3, 0.3)
        c.drawRightString(width - 50, height - 75, reshape_arabic("مركز التدريب والخدمات اللوجستية"))
        c.drawRightString(width - 50, height - 90, reshape_arabic("سبها، ليبيا"))
        
        c.setLineWidth(1)
        c.setStrokeColorRGB(0.8, 0.8, 0.8)
        c.line(50, height - 105, width - 50, height - 105)
        
        # Meta Info
        c.setFont("Arabic-Bold", 10)
        c.setFillColorRGB(0.1, 0.1, 0.1)
        c.drawString(50, height - 130, reshape_arabic(f"رقم العرض: {p.proposal_number}"))
        c.drawString(50, height - 145, reshape_arabic(f"التاريخ: {p.created_at.strftime('%Y-%m-%d')}"))
        
        status_val = p.status.value if hasattr(p.status, 'value') else p.status
        c.drawString(50, height - 160, reshape_arabic(f"الحالة: {status_val}"))
        
        # Client Info
        client_name = p.client.name if p.client else "غير محدد"
        c.drawRightString(width - 50, height - 130, reshape_arabic(f"اسم العميل: {client_name}"))
        
        service_val = p.service_type.value if hasattr(p.service_type, 'value') else p.service_type
        c.drawRightString(width - 50, height - 145, reshape_arabic(f"نوع الخدمة: {service_val}"))
        
        c.line(50, height - 180, width - 50, height - 180)
        
        # Table Headers
        c.setFont("Arabic-Bold", 10)
        c.setFillColorRGB(0.12, 0.45, 0.36)
        c.drawString(50, height - 200, reshape_arabic("وصف الخدمة / البند"))
        c.drawString(280, height - 200, reshape_arabic("الوحدة"))
        c.drawString(360, height - 200, reshape_arabic("الكمية"))
        c.drawString(420, height - 200, reshape_arabic("سعر الوحدة"))
        c.drawRightString(width - 50, height - 200, reshape_arabic("الإجمالي"))
        
        c.setStrokeColorRGB(0.12, 0.45, 0.36)
        c.line(50, height - 210, width - 50, height - 210)
        
        # Rows
        c.setFont("Arabic", 9)
        c.setFillColorRGB(0.2, 0.2, 0.2)
        y = height - 230
        
        for item in p.line_items:
            spec_name = item.service_type.value if hasattr(item.service_type, 'value') else str(item.service_type)
            c.drawString(50, y, reshape_arabic(spec_name))
            c.drawString(280, y, reshape_arabic(item.unit_description))
            c.drawString(360, y, reshape_arabic(f"{item.quantity:.2f}"))
            c.drawString(420, y, reshape_arabic(f"{item.unit_price:.2f} د.ل"))
            c.drawRightString(width - 50, y, reshape_arabic(f"{item.total:.2f} د.ل"))
            
            y -= 20
            if y < 100:
                c.showPage()
                y = height - 100
                c.setFont("Arabic", 9)
                
        c.setStrokeColorRGB(0.8, 0.8, 0.8)
        c.line(50, y + 10, width - 50, y + 10)
        
        # Summary
        y -= 10
        c.setFont("Arabic-Bold", 11)
        c.setFillColorRGB(0.12, 0.45, 0.36)
        c.drawString(300, y, reshape_arabic("إجمالي القيمة الكلية:"))
        c.drawRightString(width - 50, y, reshape_arabic(f"{p.total_value:.2f} د.ل"))
        
        # Signature block
        y -= 60
        c.setFont("Arabic", 9)
        c.setFillColorRGB(0.4, 0.4, 0.4)
        c.drawString(50, y, reshape_arabic("إعداد: _________________"))
        c.drawRightString(width - 50, y, reshape_arabic("اعتماد: _________________"))
        
        c.save()
        return filepath


def export_invoice_pdf(invoice_id: int) -> str:
    """تصدير الفاتورة الصادرة بصيغة PDF باللغة العربية والخطوط المناسبة."""
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
        
        c.setFont("Arabic-Bold", 22)
        c.setFillColorRGB(0.12, 0.45, 0.36)
        c.drawString(50, height - 90, reshape_arabic("فاتورة نهائية"))
        
        c.setFont("Arabic", 10)
        c.setFillColorRGB(0.3, 0.3, 0.3)
        c.drawRightString(width - 50, height - 75, reshape_arabic("مركز التدريب والخدمات اللوجستية"))
        c.drawRightString(width - 50, height - 90, reshape_arabic("سبها، ليبيا"))
        
        c.setLineWidth(1)
        c.setStrokeColorRGB(0.8, 0.8, 0.8)
        c.line(50, height - 105, width - 50, height - 105)
        
        # Invoice metadata
        c.setFont("Arabic-Bold", 10)
        c.setFillColorRGB(0.1, 0.1, 0.1)
        c.drawString(50, height - 130, reshape_arabic(f"رقم الفاتورة: {inv.invoice_number}"))
        c.drawString(50, height - 145, reshape_arabic(f"التاريخ: {inv.created_at.strftime('%Y-%m-%d')}"))
        
        client_name = inv.client.name if inv.client else "غير محدد"
        c.drawRightString(width - 50, height - 130, reshape_arabic(f"اسم العميل: {client_name}"))
        
        c.line(50, height - 170, width - 50, height - 170)
        
        # Table Headers
        c.setFont("Arabic-Bold", 10)
        c.setFillColorRGB(0.12, 0.45, 0.36)
        c.drawString(50, height - 190, reshape_arabic("تفاصيل البند"))
        c.drawString(280, height - 190, reshape_arabic("الوحدة"))
        c.drawString(360, height - 190, reshape_arabic("الكمية"))
        c.drawString(420, height - 190, reshape_arabic("سعر الوحدة"))
        c.drawRightString(width - 50, height - 190, reshape_arabic("الإجمالي"))
        
        c.line(50, height - 200, width - 50, height - 200)
        
        # Rows
        c.setFont("Arabic", 9)
        c.setFillColorRGB(0.2, 0.2, 0.2)
        y = height - 220
        
        for item in inv.line_items:
            spec_name = item.service_type.value if hasattr(item.service_type, 'value') else str(item.service_type)
            c.drawString(50, y, reshape_arabic(spec_name))
            c.drawString(280, y, reshape_arabic(item.unit_description))
            c.drawString(360, y, reshape_arabic(f"{item.quantity:.2f}"))
            c.drawString(420, y, reshape_arabic(f"{item.unit_price:.2f} د.ل"))
            c.drawRightString(width - 50, y, reshape_arabic(f"{item.total:.2f} د.ل"))
            y -= 20
            
        c.line(50, y + 10, width - 50, y + 10)
        
        # Summary
        y -= 10
        c.setFont("Arabic-Bold", 11)
        c.setFillColorRGB(0.12, 0.45, 0.36)
        c.drawString(300, y, reshape_arabic("المبلغ المطلوب:"))
        c.drawRightString(width - 50, y, reshape_arabic(f"{inv.total_value:.2f} د.ل"))
        
        # Signature
        y -= 60
        c.setFont("Arabic", 9)
        c.setFillColorRGB(0.4, 0.4, 0.4)
        c.drawString(50, y, reshape_arabic("توقيع المحاسب: _________________"))
        c.drawRightString(width - 50, y, reshape_arabic("توقيع المستلم: _________________"))
        
        c.save()
        return filepath


def export_voucher_pdf(voucher_id: int) -> str:
    """تصدير السند المالي (سند قبض أو صرف) بصيغة PDF باللغة العربية والخطوط المناسبة."""
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
        
        is_receipt = v.voucher_type == VoucherType.RECEIPT
        color = (0.12, 0.45, 0.36) if is_receipt else (0.7, 0.15, 0.15)
        title = "سند قبض" if is_receipt else "سند صرف"
        
        c.setStrokeColorRGB(*color)
        c.setLineWidth(4)
        c.line(50, height - 50, width - 50, height - 50)
        
        c.setFont("Arabic-Bold", 22)
        c.setFillColorRGB(*color)
        c.drawString(50, height - 90, reshape_arabic(title))
        
        c.setFont("Arabic", 10)
        c.setFillColorRGB(0.3, 0.3, 0.3)
        c.drawRightString(width - 50, height - 75, reshape_arabic("مركز التدريب والخدمات اللوجستية"))
        c.drawRightString(width - 50, height - 90, reshape_arabic("سبها، ليبيا"))
        
        c.setLineWidth(1)
        c.setStrokeColorRGB(0.8, 0.8, 0.8)
        c.line(50, height - 105, width - 50, height - 105)
        
        # Meta info
        c.setFont("Arabic-Bold", 10)
        c.setFillColorRGB(0.1, 0.1, 0.1)
        c.drawString(50, height - 130, reshape_arabic(f"رقم السند: {v.voucher_number}"))
        c.drawString(50, height - 145, reshape_arabic(f"التاريخ: {v.created_at.strftime('%Y-%m-%d')}"))
        
        # Payment details
        c.setFont("Arabic", 10)
        party_label = "استلمنا من" if is_receipt else "صرف إلى"
        c.drawString(50, height - 180, reshape_arabic(f"{party_label}: {v.party_name}"))
        c.drawString(50, height - 200, reshape_arabic(f"القيمة: {v.amount:.2f} د.ل"))
        
        pay_method_val = v.payment_method.value if hasattr(v.payment_method, 'value') else str(v.payment_method)
        c.drawString(50, height - 220, reshape_arabic(f"طريقة الدفع: {pay_method_val}"))
        
        # Description / Notes
        c.drawString(50, height - 250, reshape_arabic("الوصف / ملاحظات:"))
        c.setFont("Arabic", 9)
        c.drawString(70, height - 265, reshape_arabic(v.notes or "لا توجد ملاحظات إضافية."))
        
        # Words Tafqit
        c.setFont("Arabic-Bold", 9)
        c.drawString(50, height - 300, reshape_arabic(f"المبلغ تفقيطاً: {v.amount_in_words}"))
        
        # Signatures
        y = height - 360
        c.setFont("Arabic", 9)
        c.setFillColorRGB(0.4, 0.4, 0.4)
        c.drawString(50, y, reshape_arabic("أمين الصندوق / المراجع: _________________"))
        c.drawRightString(width - 50, y, reshape_arabic("اعتماد الإدارة: _________________"))
        
        c.save()
        return filepath

