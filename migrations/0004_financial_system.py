"""
Migration 0004: Financial system.
إنشاء الجداول والتركيبة المالية للمنظومة — Phase D.
"""
from sqlalchemy import text


def upgrade(engine):
    """Apply migration."""
    with engine.begin() as conn:
        # invoices
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_number VARCHAR(50) UNIQUE NOT NULL,
                proposal_id INTEGER REFERENCES financial_proposals(id),
                client_id INTEGER NOT NULL REFERENCES clients(id),
                total_value NUMERIC(15,2) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))

        # service_line_items
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS service_line_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                proposal_id INTEGER REFERENCES financial_proposals(id) ON DELETE CASCADE,
                invoice_id INTEGER REFERENCES invoices(id) ON DELETE CASCADE,
                service_type VARCHAR(50) NOT NULL,
                unit_description VARCHAR(100) NOT NULL,
                quantity NUMERIC(10,2) NOT NULL DEFAULT 1.00,
                unit_price NUMERIC(10,2) NOT NULL,
                currency VARCHAR(10) DEFAULT 'LYD',
                discount NUMERIC(10,2) DEFAULT 0.00,
                total NUMERIC(10,2) NOT NULL
            )
        """))

        # vouchers
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS vouchers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                voucher_type VARCHAR(20) NOT NULL,
                voucher_number VARCHAR(50) UNIQUE NOT NULL,
                party_name VARCHAR(200) NOT NULL,
                amount NUMERIC(12,2) NOT NULL,
                amount_in_words VARCHAR(300) NOT NULL,
                payment_method VARCHAR(20) NOT NULL,
                revenue_source VARCHAR(50),
                project_id INTEGER REFERENCES projects(id),
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))

        # expenses
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(200) NOT NULL,
                quantity NUMERIC(10,2) NOT NULL DEFAULT 1.00,
                unit VARCHAR(50),
                unit_price NUMERIC(12,2) NOT NULL,
                total NUMERIC(12,2) NOT NULL,
                notes TEXT,
                invoice_image_path TEXT,
                project_id INTEGER REFERENCES projects(id),
                payment_method VARCHAR(20) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))

        # assets
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS assets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(200) NOT NULL,
                category VARCHAR(50) NOT NULL,
                acquisition_date DATE NOT NULL,
                depreciation_months INTEGER NOT NULL DEFAULT 12,
                ownership VARCHAR(20) NOT NULL,
                lender_name VARCHAR(200),
                notes TEXT
            )
        """))

        # cash_register
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS cash_register (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                register_type VARCHAR(20) NOT NULL,
                transaction_type VARCHAR(5) NOT NULL,
                amount NUMERIC(12,2) NOT NULL,
                description TEXT NOT NULL,
                related_voucher_id INTEGER REFERENCES vouchers(id) ON DELETE SET NULL,
                balance_after NUMERIC(15,2) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))

        print("[migration 0004] Financial system tables created successfully")
