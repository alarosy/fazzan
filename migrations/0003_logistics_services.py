"""
Migration 0003: Logistics services.
إنشاء جداول الخدمات اللوجستية — Phase C.
"""
from sqlalchemy import text


def upgrade(engine):
    """Apply migration."""
    with engine.begin() as conn:
        # consultants
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS consultants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(200) NOT NULL,
                email VARCHAR(200),
                phone VARCHAR(50),
                address TEXT,
                specialization VARCHAR(50) NOT NULL,
                service_detail TEXT,
                contract_start DATE,
                contract_end DATE,
                gross_value NUMERIC(10,2),
                center_share NUMERIC(10,2),
                consultant_share NUMERIC(10,2),
                payment_method VARCHAR(20),
                is_deleted BOOLEAN DEFAULT 0
            )
        """))
        # financial_proposals (stub for FK)
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS financial_proposals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                proposal_number VARCHAR(50) UNIQUE,
                client_id INTEGER,
                service_type VARCHAR(50),
                status VARCHAR(50) DEFAULT 'قيد الانتظار',
                approved_by VARCHAR(100),
                approved_at TIMESTAMP,
                total_value NUMERIC(15,2),
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        # catering_orders
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS catering_orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                proposal_id INTEGER REFERENCES financial_proposals(id),
                meal_type VARCHAR(50) NOT NULL,
                service_level VARCHAR(50) NOT NULL,
                pricing_mode VARCHAR(20) DEFAULT 'per_person',
                num_persons INTEGER,
                num_days INTEGER,
                unit_price NUMERIC(10,2) NOT NULL,
                details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))

        # catering_extras
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS catering_extras (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL REFERENCES catering_orders(id) ON DELETE CASCADE,
                service_name VARCHAR(200) NOT NULL,
                price NUMERIC(10,2) NOT NULL
            )
        """))

        # accommodation_bookings
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS accommodation_bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                proposal_id INTEGER REFERENCES financial_proposals(id),
                apartment_type VARCHAR(5) NOT NULL,
                check_in_date DATE NOT NULL,
                check_out_date DATE NOT NULL
            )
        """))

        # accommodation_extras
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS accommodation_extras (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                booking_id INTEGER NOT NULL REFERENCES accommodation_bookings(id) ON DELETE CASCADE,
                service_name VARCHAR(200) NOT NULL,
                price NUMERIC(10,2) NOT NULL
            )
        """))

        # market_research
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS market_research (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                collection_method VARCHAR(20) NOT NULL,
                collection_type VARCHAR(200) NOT NULL,
                min_samples INTEGER NOT NULL,
                min_price NUMERIC(10,2) NOT NULL,
                max_samples INTEGER NOT NULL,
                max_price NUMERIC(10,2) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))

        print("[migration 0003] Logistics services tables created successfully")
