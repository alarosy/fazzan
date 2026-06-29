"""
Migration 0005: Advanced features.
توسعة المشاريع، وإنشاء جداول العقود والشركاء — Phase E.
"""
from sqlalchemy import text


def upgrade(engine):
    """Apply migration."""
    with engine.begin() as conn:
        # Alter projects table to add columns (using try-except for robustness in SQLite)
        try:
            conn.execute(text("ALTER TABLE projects ADD COLUMN project_number VARCHAR(50)"))
        except Exception:
            pass

        try:
            conn.execute(text("ALTER TABLE projects ADD COLUMN geographic_scope VARCHAR(100)"))
        except Exception:
            pass

        try:
            conn.execute(text("ALTER TABLE projects ADD COLUMN budget_allocated NUMERIC(15,2)"))
        except Exception:
            pass

        try:
            conn.execute(text("ALTER TABLE projects ADD COLUMN budget_spent NUMERIC(15,2) DEFAULT 0.00"))
        except Exception:
            pass

        # Create contracts table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS contracts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER NOT NULL REFERENCES clients(id),
                project_id INTEGER REFERENCES projects(id),
                title VARCHAR(200) NOT NULL,
                status VARCHAR(50) NOT NULL,
                value NUMERIC(15,2) NOT NULL,
                start_date DATE,
                end_date DATE,
                scope TEXT,
                clauses TEXT,
                is_deleted BOOLEAN DEFAULT 0
            )
        """))

        # Create partners table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS partners (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(200) NOT NULL,
                type VARCHAR(50) NOT NULL,
                email VARCHAR(200),
                phone VARCHAR(50),
                contribution_details TEXT,
                is_deleted BOOLEAN DEFAULT 0
            )
        """))

        print("[migration 0005] Advanced features columns and tables created successfully")
