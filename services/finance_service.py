"""
Finance Service — خدمات المالية.
طبقة الخدمات للتعامل مع البيانات المالية والمعاملات الحسابية.
"""
from typing import List, Optional
from decimal import Decimal
import datetime as dt
from sqlalchemy.orm import joinedload

from core.database import get_session
from models.financial_proposal import FinancialProposal
from models.service_line_item import ServiceLineItem
from models.invoice import Invoice
from models.voucher import Voucher
from models.expense import Expense
from models.asset import Asset
from models.cash_register import CashRegister
from models.employee import Employee
from models.project import Project
from models.enums import ProposalStatus, VoucherType, PaymentMethod, RegisterType, RevenueSource, TransactionType
from core.arabic_number import amount_to_arabic_words


def recalculate_balances(session, register_type: RegisterType):
    """إعادة احتساب الأرصدة المتراكمة (balance_after) لسجل حركات الخزينة/البنك."""
    logs = session.query(CashRegister).filter(
        CashRegister.register_type == register_type
    ).order_by(CashRegister.created_at.asc(), CashRegister.id.asc()).all()
    
    current_balance = Decimal("0.00")
    for log in logs:
        if log.transaction_type in ("in", TransactionType.IN):
            current_balance += Decimal(str(log.amount))
        else:
            current_balance -= Decimal(str(log.amount))
        log.balance_after = current_balance
    session.flush()



# ─── 1. Dashboard Metrics ───────────────────────────────────────────────────

def get_cash_balance() -> Decimal:
    """جلب الرصيد النقدي الحالي (كاش)."""
    with get_session() as session:
        latest = session.query(CashRegister).filter(
            CashRegister.register_type == RegisterType.CASH
        ).order_by(CashRegister.created_at.desc(), CashRegister.id.desc()).first()
        return latest.balance_after if latest else Decimal("0.00")


def get_bank_balance() -> Decimal:
    """جلب الرصيد المصرفي الحالي (بنك)."""
    with get_session() as session:
        latest = session.query(CashRegister).filter(
            CashRegister.register_type == RegisterType.BANK
        ).order_by(CashRegister.created_at.desc(), CashRegister.id.desc()).first()
        return latest.balance_after if latest else Decimal("0.00")


def count_pending_proposals() -> int:
    """عدد عروض الأسعار قيد الانتظار."""
    with get_session() as session:
        return session.query(FinancialProposal).filter(
            FinancialProposal.status == ProposalStatus.PENDING
        ).count()


# ─── 2. Financial Proposal CRUD ─────────────────────────────────────────────

def get_all_proposals() -> List[FinancialProposal]:
    """جلب جميع عروض الأسعار."""
    with get_session() as session:
        results = session.query(FinancialProposal).options(
            joinedload(FinancialProposal.client),
            joinedload(FinancialProposal.line_items)
        ).order_by(FinancialProposal.created_at.desc()).all()
        for r in results:
            if r in session:
                session.expunge(r)
                for item in r.line_items:
                    if item in session:
                        session.expunge(item)
                if r.client and r.client in session:
                    session.expunge(r.client)
        return results


def get_proposal_by_id(proposal_id: int) -> Optional[FinancialProposal]:
    """جلب عرض سعر بالمعرّف."""
    with get_session() as session:
        p = session.query(FinancialProposal).options(
            joinedload(FinancialProposal.client),
            joinedload(FinancialProposal.line_items)
        ).filter(FinancialProposal.id == proposal_id).first()
        if p:
            if p in session:
                session.expunge(p)
                for item in p.line_items:
                    if item in session:
                        session.expunge(item)
                if p.client and p.client in session:
                    session.expunge(p.client)
        return p


def create_proposal(data: dict, line_items: List[dict] = None) -> FinancialProposal:
    """إنشاء عرض سعر جديد مع بنوده التفصيلية."""
    # Generate Proposal Number: PRO-YYYY-XXXX
    year = dt.datetime.now().year
    with get_session() as session:
        count = session.query(FinancialProposal).count() + 1
        data["proposal_number"] = f"PRO-{year}-{count:04d}"
        
        # Calculate total value
        total_val = Decimal("0.00")
        if line_items:
            for item in line_items:
                total_val += Decimal(str(item.get("total", 0.00)))
        data["total_value"] = total_val
        
        proposal = FinancialProposal(**data)
        session.add(proposal)
        session.flush()
        
        if line_items:
            for item in line_items:
                li = ServiceLineItem(proposal_id=proposal.id, **item)
                session.add(li)
        
        session.flush()
        
        # Re-query
        result = session.query(FinancialProposal).options(
            joinedload(FinancialProposal.line_items)
        ).filter(FinancialProposal.id == proposal.id).first()
        
        if result in session:
            session.expunge(result)
            for item in result.line_items:
                if item in session:
                    session.expunge(item)
        return result


def update_proposal(proposal_id: int, data: dict, line_items: List[dict] = None) -> Optional[FinancialProposal]:
    """تحديث عرض سعر وبنوده."""
    with get_session() as session:
        proposal = session.query(FinancialProposal).filter(FinancialProposal.id == proposal_id).first()
        if not proposal:
            return None
            
        for key, value in data.items():
            if hasattr(proposal, key):
                setattr(proposal, key, value)
                
        if line_items is not None:
            # Delete old items
            session.query(ServiceLineItem).filter(ServiceLineItem.proposal_id == proposal_id).delete()
            # Calculate total
            total_val = Decimal("0.00")
            for item in line_items:
                total_val += Decimal(str(item.get("total", 0.00)))
                li = ServiceLineItem(proposal_id=proposal_id, **item)
                session.add(li)
            proposal.total_value = total_val
            
        session.flush()
        
        result = session.query(FinancialProposal).options(
            joinedload(FinancialProposal.line_items)
        ).filter(FinancialProposal.id == proposal_id).first()
        
        if result in session:
            session.expunge(result)
            for item in result.line_items:
                if item in session:
                    session.expunge(item)
        return result


def delete_proposal(proposal_id: int) -> bool:
    """حذف عرض السعر نهائياً."""
    with get_session() as session:
        proposal = session.query(FinancialProposal).filter(FinancialProposal.id == proposal_id).first()
        if not proposal:
            return False
        session.delete(proposal)
        return True


# ─── 3. Invoices CRUD ───────────────────────────────────────────────────────

def get_all_invoices() -> List[Invoice]:
    """جلب جميع الفواتير."""
    with get_session() as session:
        results = session.query(Invoice).options(
            joinedload(Invoice.client),
            joinedload(Invoice.line_items)
        ).order_by(Invoice.created_at.desc()).all()
        for r in results:
            if r in session:
                session.expunge(r)
                for item in r.line_items:
                    if item in session:
                        session.expunge(item)
                if r.client and r.client in session:
                    session.expunge(r.client)
        return results


def get_invoice_by_id(invoice_id: int) -> Optional[Invoice]:
    """جلب فاتورة بالمعرّف."""
    with get_session() as session:
        inv = session.query(Invoice).options(
            joinedload(Invoice.client),
            joinedload(Invoice.line_items)
        ).filter(Invoice.id == invoice_id).first()
        if inv:
            if inv in session:
                session.expunge(inv)
                for item in inv.line_items:
                    if item in session:
                        session.expunge(item)
                if inv.client and inv.client in session:
                    session.expunge(inv.client)
        return inv


# ─── 4. Vouchers CRUD ───────────────────────────────────────────────────────

def get_all_vouchers() -> List[Voucher]:
    """جلب جميع السندات."""
    with get_session() as session:
        results = session.query(Voucher).options(
            joinedload(Voucher.project)
        ).order_by(Voucher.created_at.desc()).all()
        for r in results:
            if r in session:
                session.expunge(r)
                if r.project and r.project in session:
                    session.expunge(r.project)
        return results


def create_voucher(data: dict) -> Voucher:
    """إنشاء سند مالي (قبض أو صرف) وحساب حركات الخزينة."""
    if not data.get("amount") or Decimal(str(data["amount"])) <= 0:
        raise ValueError("قيمة السند يجب أن تكون أكبر من الصفر")
    
    with get_session() as session:
        # Generate number
        year = dt.datetime.now().year
        v_type = data["voucher_type"]
        if v_type == VoucherType.RECEIPT:
            count = session.query(Voucher).filter(Voucher.voucher_type == VoucherType.RECEIPT).count() + 1
            data["voucher_number"] = f"REC-{year}-{count:04d}"
        else:
            count = session.query(Voucher).filter(Voucher.voucher_type == VoucherType.DISBURSEMENT).count() + 1
            data["voucher_number"] = f"DISB-{year}-{count:04d}"
            
        # Amount in words conversion (Arabic Tafqit)
        val = Decimal(str(data["amount"]))
        data["amount_in_words"] = amount_to_arabic_words(val)
        
        voucher = Voucher(**data)
        session.add(voucher)
        session.flush()
        
        # Cash register tracking
        reg_type = RegisterType.BANK if data["payment_method"] == PaymentMethod.BANK else RegisterType.CASH
        tx_type = TransactionType.IN if v_type == VoucherType.RECEIPT else TransactionType.OUT
        
        # Calculate balance after
        latest = session.query(CashRegister).filter(
            CashRegister.register_type == reg_type
        ).order_by(CashRegister.created_at.desc(), CashRegister.id.desc()).first()
        
        prev_bal = latest.balance_after if latest else Decimal("0.00")
        if tx_type == TransactionType.IN:
            new_bal = prev_bal + val
        else:
            new_bal = prev_bal - val
            
        tx = CashRegister(
            register_type=reg_type,
            transaction_type=tx_type,
            amount=val,
            description=f"حركة مرتبطة بالسند {voucher.voucher_number} للجهة {voucher.party_name}",
            related_voucher_id=voucher.id,
            balance_after=new_bal
        )
        session.add(tx)
        
        # If Disbursement linked to project, charge as project expense
        if v_type == VoucherType.DISBURSEMENT and data.get("project_id"):
            proj = session.query(Project).filter(Project.id == data["project_id"]).first()
            if proj:
                # Add spent budget
                if hasattr(proj, "budget_spent") and proj.budget_spent is not None:
                    proj.budget_spent += val
                elif proj.budget is not None:
                    proj.budget = max(Decimal("0.00"), proj.budget - val)
                
                # Create Expense
                expense = Expense(
                    name=f"مصروف مرتبط بسند صرف {voucher.voucher_number}",
                    quantity=Decimal("1.00"),
                    unit="سند",
                    unit_price=val,
                    total=val,
                    project_id=proj.id,
                    payment_method=data["payment_method"],
                    notes=data.get("notes")
                )
                session.add(expense)

        # If Receipt linked to project, increase project actual budget
        if v_type == VoucherType.RECEIPT and data.get("project_id"):
            proj = session.query(Project).filter(Project.id == data["project_id"]).first()
            if proj and hasattr(proj, "budget_spent"):
                proj.budget_spent = (proj.budget_spent or 0) + val

        session.flush()
        session.refresh(voucher)
        session.expunge(voucher)
        return voucher


# ─── 5. Expenses CRUD ───────────────────────────────────────────────────────

def get_all_expenses() -> List[Expense]:
    """جلب جميع المصروفات."""
    with get_session() as session:
        results = session.query(Expense).options(
            joinedload(Expense.project)
        ).order_by(Expense.created_at.desc()).all()
        for r in results:
            if r in session:
                session.expunge(r)
                if r.project and r.project in session:
                    session.expunge(r.project)
        return results


def create_expense(data: dict) -> Expense:
    """تسجيل مصروف يدوي وحسمه من الخزينة."""
    val = Decimal(str(data["unit_price"])) * Decimal(str(data.get("quantity", 1.00)))
    data["total"] = val
    
    with get_session() as session:
        expense = Expense(**data)
        session.add(expense)
        session.flush()
        
        # Deduct from Cash Register
        reg_type = RegisterType.BANK if data.get("payment_method") == PaymentMethod.BANK else RegisterType.CASH
        latest = session.query(CashRegister).filter(
            CashRegister.register_type == reg_type
        ).order_by(CashRegister.created_at.desc(), CashRegister.id.desc()).first()
        
        prev_bal = latest.balance_after if latest else Decimal("0.00")
        new_bal = prev_bal - val
        
        tx = CashRegister(
            register_type=reg_type,
            transaction_type=TransactionType.OUT,
            amount=val,
            description=f"مصروف تشغيلي: {expense.name}",
            related_expense_id=expense.id,
            balance_after=new_bal
        )
        session.add(tx)
        
        # Deduct/Charge project if linked
        if data.get("project_id"):
            proj = session.query(Project).filter(Project.id == data["project_id"]).first()
            if proj:
                if hasattr(proj, "budget_spent") and proj.budget_spent is not None:
                    proj.budget_spent += val
                elif proj.budget is not None:
                    proj.budget = max(Decimal("0.00"), proj.budget - val)
                    
        session.flush()
        session.refresh(expense)
        session.expunge(expense)
        return expense


# ─── 6. Assets CRUD ─────────────────────────────────────────────────────────

def get_all_assets() -> List[Asset]:
    """جلب جميع الأصول."""
    with get_session() as session:
        results = session.query(Asset).all()
        for r in results:
            session.expunge(r)
        return results


def create_asset(data: dict) -> Asset:
    """تسجيل أصل جديد."""
    with get_session() as session:
        asset = Asset(**data)
        session.add(asset)
        session.flush()
        session.refresh(asset)
        session.expunge(asset)
        return asset


# ─── 7. Cash Register Logs ──────────────────────────────────────────────────

def get_all_cash_logs() -> List[CashRegister]:
    """جلب حركات الخزينة بالكامل مرتبة من الأحدث إلى الأقدم."""
    with get_session() as session:
        results = session.query(CashRegister).order_by(CashRegister.created_at.desc(), CashRegister.id.desc()).all()
        for r in results:
            session.expunge(r)
        return results


# ─── 8. Critical Actions (الاعتماد والشحن) ──────────────────────────────────

def approve_proposal(proposal_id: int) -> Optional[Invoice]:
    """اعتماد عرض السعر وتحويله لفاتورة نهائية وتوليد قيد الخزينة/المصرف."""
    with get_session() as session:
        proposal = session.query(FinancialProposal).options(
            joinedload(FinancialProposal.line_items)
        ).filter(FinancialProposal.id == proposal_id).first()
        
        if not proposal or proposal.status == ProposalStatus.APPROVED:
            return None
            
        proposal.status = ProposalStatus.APPROVED
        proposal.approved_by = "المدير المالي"
        proposal.approved_at = dt.datetime.now()
        
        # Generate Invoice
        year = dt.datetime.now().year
        count = session.query(Invoice).count() + 1
        invoice_number = f"INV-{year}-{count:04d}"
        
        invoice = Invoice(
            invoice_number=invoice_number,
            proposal_id=proposal.id,
            client_id=proposal.client_id,
            total_value=proposal.total_value,
            created_at=dt.datetime.now()
        )
        session.add(invoice)
        session.flush()
        
        # Copy line items
        for item in proposal.line_items:
            new_item = ServiceLineItem(
                invoice_id=invoice.id,
                service_type=item.service_type,
                unit_description=item.unit_description,
                quantity=item.quantity,
                unit_price=item.unit_price,
                currency=item.currency,
                discount=item.discount,
                total=item.total
            )
            session.add(new_item)
            
        # Determine payment register (Default to Bank)
        reg_type = RegisterType.BANK
        latest = session.query(CashRegister).filter(
            CashRegister.register_type == reg_type
        ).order_by(CashRegister.created_at.desc(), CashRegister.id.desc()).first()
        
        prev_bal = latest.balance_after if latest else Decimal("0.00")
        new_bal = prev_bal + Decimal(str(proposal.total_value))
        
        tx = CashRegister(
            register_type=reg_type,
            transaction_type=TransactionType.IN,
            amount=proposal.total_value,
            description=f"إيراد اعتماد الفاتورة {invoice.invoice_number} التابعة للعرض {proposal.proposal_number}",
            related_invoice_id=invoice.id,
            balance_after=new_bal
        )
        session.add(tx)
        
        # Update project actual budget if linked
        if hasattr(proposal, "project_id") and proposal.project_id:
            proj = session.query(Project).filter(Project.id == proposal.project_id).first()
            if proj and hasattr(proj, "budget_spent"):
                proj.budget_spent = (proj.budget_spent or 0) + proposal.total_value
                
        session.flush()
        session.refresh(invoice)
        
        result = session.query(Invoice).options(
            joinedload(Invoice.line_items)
        ).filter(Invoice.id == invoice.id).first()
        
        if result in session:
            session.expunge(result)
            for item in result.line_items:
                if item in session:
                    session.expunge(item)
        return result


def charge_employee_to_project(employee_id: int, project_id: int, work_days: int) -> Expense:
    """تحميل أجر موظف على ميزانية مشروع وتوليد مصروف وحركة الخزينة."""
    with get_session() as session:
        employee = session.query(Employee).filter(Employee.id == employee_id).first()
        project = session.query(Project).filter(Project.id == project_id).first()
        
        if not employee or not project:
            raise ValueError("الموظف أو المشروع غير موجود")
            
        daily_rate = employee.daily_wage_rate or Decimal("0.00")
        charge_amount = daily_rate * Decimal(work_days)
        
        if charge_amount <= 0:
            raise ValueError("قيمة الشحن يجب أن تكون أكبر من الصفر")
            
        # Deduct or increase spent
        if hasattr(project, 'budget_spent') and project.budget_spent is not None:
            project.budget_spent += charge_amount
        elif project.budget is not None:
            project.budget = max(Decimal("0.00"), project.budget - charge_amount)
            
        # Create Expense
        expense = Expense(
            name=f"تحميل أجر الموظف: {employee.name} لعدد {work_days} أيام عمل",
            quantity=Decimal(work_days),
            unit="يوم",
            unit_price=daily_rate,
            total=charge_amount,
            project_id=project.id,
            payment_method=PaymentMethod.CASH,
            notes=f"راتب محمل تلقائياً للمشروع {project.name}"
        )
        session.add(expense)
        session.flush()
        
        # Deduct from CashRegister (CASH)
        latest = session.query(CashRegister).filter(
            CashRegister.register_type == RegisterType.CASH
        ).order_by(CashRegister.created_at.desc(), CashRegister.id.desc()).first()
        prev_bal = latest.balance_after if latest else Decimal("0.00")
        new_bal = prev_bal - charge_amount
        
        tx = CashRegister(
            register_type=RegisterType.CASH,
            transaction_type=TransactionType.OUT,
            amount=charge_amount,
            description=f"مصروف تحميل راتب {employee.name} على مشروع {project.name}",
            related_expense_id=expense.id,
            balance_after=new_bal
        )
        session.add(tx)
        
        session.flush()
        session.refresh(expense)
        session.expunge(expense)
        return expense


# ─── 9. Additional CRUD for Invoices, Vouchers, Expenses, Assets ────────────

def update_invoice(invoice_id: int, data: dict) -> Optional[Invoice]:
    """تحديث بيانات فاتورة."""
    with get_session() as session:
        inv = session.query(Invoice).filter(Invoice.id == invoice_id).first()
        if not inv:
            return None
        for key, value in data.items():
            if hasattr(inv, key):
                setattr(inv, key, value)
        session.flush()
        session.refresh(inv)
        session.expunge(inv)
        return inv


def delete_invoice(invoice_id: int) -> bool:
    """حذف فاتورة وإرجاع عرض السعر المرتبط لحالة الانتظار."""
    with get_session() as session:
        inv = session.query(Invoice).filter(Invoice.id == invoice_id).first()
        if not inv:
            return False
            
        if inv.proposal_id:
            prop = session.query(FinancialProposal).filter(FinancialProposal.id == inv.proposal_id).first()
            if prop:
                prop.status = ProposalStatus.PENDING
                prop.approved_by = None
                prop.approved_at = None
                
        # Get register types of logs we're about to delete
        logs = session.query(CashRegister).filter(CashRegister.related_invoice_id == invoice_id).all()
        reg_types = {log.register_type for log in logs}
        
        # Delete related cash log using foreign key
        session.query(CashRegister).filter(CashRegister.related_invoice_id == invoice_id).delete()

        session.delete(inv)
        
        # Recalculate balances
        for rt in reg_types:
            recalculate_balances(session, rt)
            
        return True


def update_voucher(voucher_id: int, data: dict) -> Optional[Voucher]:
    """تحديث بيانات سند مالي وتفقيطه."""
    with get_session() as session:
        v = session.query(Voucher).filter(Voucher.id == voucher_id).first()
        if not v:
            return None
        for key, value in data.items():
            if hasattr(v, key):
                setattr(v, key, value)
        v.amount_in_words = amount_to_arabic_words(v.amount)
        session.flush()
        session.refresh(v)
        session.expunge(v)
        return v


def delete_voucher(voucher_id: int) -> bool:
    """حذف سند مالي وعكس حركته من الخزينة وميزانية المشاريع."""
    with get_session() as session:
        v = session.query(Voucher).filter(Voucher.id == voucher_id).first()
        if not v:
            return False
            
        if v.voucher_type == VoucherType.DISBURSEMENT and v.project_id:
            proj = session.query(Project).filter(Project.id == v.project_id).first()
            if proj and hasattr(proj, "budget_spent") and proj.budget_spent is not None:
                proj.budget_spent = max(Decimal("0.00"), proj.budget_spent - v.amount)
                
        # Get register types of logs we're about to delete
        logs = session.query(CashRegister).filter(CashRegister.related_voucher_id == voucher_id).all()
        reg_types = {log.register_type for log in logs}
        
        session.query(CashRegister).filter(CashRegister.related_voucher_id == voucher_id).delete()
        session.delete(v)
        
        # Recalculate balances
        for rt in reg_types:
            recalculate_balances(session, rt)
            
        return True


def update_expense(expense_id: int, data: dict) -> Optional[Expense]:
    """تحديث مصروف مالي وإعادة احتساب المجموع."""
    with get_session() as session:
        ex = session.query(Expense).filter(Expense.id == expense_id).first()
        if not ex:
            return None
        for key, value in data.items():
            if hasattr(ex, key):
                setattr(ex, key, value)
        ex.total = Decimal(str(ex.unit_price)) * Decimal(str(ex.quantity))
        session.flush()
        session.refresh(ex)
        session.expunge(ex)
        return ex


def delete_expense(expense_id: int) -> bool:
    """حذف مصروف وإلغاء تحميله من ميزانية المشاريع وحركات الخزينة."""
    with get_session() as session:
        ex = session.query(Expense).filter(Expense.id == expense_id).first()
        if not ex:
            return False
            
        if ex.project_id:
            proj = session.query(Project).filter(Project.id == ex.project_id).first()
            if proj and hasattr(proj, "budget_spent") and proj.budget_spent is not None:
                proj.budget_spent = max(Decimal("0.00"), proj.budget_spent - ex.total)
                
        # Get register types of logs we're about to delete
        logs = session.query(CashRegister).filter(CashRegister.related_expense_id == expense_id).all()
        reg_types = {log.register_type for log in logs}
        
        # Delete related cash log using foreign key
        session.query(CashRegister).filter(CashRegister.related_expense_id == expense_id).delete()
        
        session.delete(ex)
        
        # Recalculate balances
        for rt in reg_types:
            recalculate_balances(session, rt)
            
        return True


def update_asset(asset_id: int, data: dict) -> Optional[Asset]:
    """تحديث بيانات أصل ثابت."""
    with get_session() as session:
        ast = session.query(Asset).filter(Asset.id == asset_id).first()
        if not ast:
            return None
        for key, value in data.items():
            if hasattr(ast, key):
                setattr(ast, key, value)
        session.flush()
        session.refresh(ast)
        session.expunge(ast)
        return ast


def delete_asset(asset_id: int) -> bool:
    """حذف أصل ثابت."""
    with get_session() as session:
        ast = session.query(Asset).filter(Asset.id == asset_id).first()
        if not ast:
            return False
        session.delete(ast)
        return True
