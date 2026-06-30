"""
Migration 0006: Add related_expense_id and related_invoice_id to CashRegister.
ربط حركات الخزينة بالمصروفات والفواتير عبر مفاتيح خارجية.
"""
from sqlalchemy import text


def upgrade(engine):
    """Apply migration."""
    with engine.begin() as conn:
        try:
            conn.execute(text("ALTER TABLE cash_register ADD COLUMN related_expense_id INTEGER REFERENCES expenses(id) ON DELETE CASCADE"))
        except Exception:
            pass

        try:
            conn.execute(text("ALTER TABLE cash_register ADD COLUMN related_invoice_id INTEGER REFERENCES invoices(id) ON DELETE CASCADE"))
        except Exception:
            pass

        try:
            conn.execute(text("ALTER TABLE financial_proposals ADD COLUMN project_id INTEGER REFERENCES projects(id)"))
        except Exception:
            pass
