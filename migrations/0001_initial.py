"""
Migration 0001: Initial schema.
إنشاء الجداول الأساسية — Phase A.

Tables created:
    - partnerships
    - projects
    - halls
    - employees
    - clients
    - training_programs
    - trainees
    - trainers
"""
from sqlalchemy import text


def upgrade(engine):
    """Apply migration — create all Phase A tables."""
    with engine.begin() as conn:
        # ── partnerships ──
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS partnerships (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(200) NOT NULL,
                partner_entity VARCHAR(200),
                start_date DATE,
                end_date DATE,
                agreement_value NUMERIC(15, 2),
                status VARCHAR(20) DEFAULT 'قائم',
                notes TEXT,
                is_deleted BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP
            )
        """))

        # ── projects ──
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(300) NOT NULL,
                description TEXT,
                start_date DATE,
                end_date DATE,
                status VARCHAR(20) DEFAULT 'نشط',
                budget NUMERIC(15, 2),
                is_deleted BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP
            )
        """))

        # ── halls ──
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS halls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(200) NOT NULL,
                capacity INTEGER,
                daily_rate NUMERIC(10, 2),
                hourly_rate NUMERIC(10, 2),
                location VARCHAR(200),
                notes TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))

        # ── employees ──
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(200) NOT NULL,
                email VARCHAR(200),
                phone VARCHAR(50),
                position VARCHAR(200),
                hire_date DATE,
                address TEXT,
                id_number VARCHAR(50),
                contract_start_date DATE,
                contract_end_date DATE,
                daily_wage_rate NUMERIC(10, 2),
                employment_type VARCHAR(20),
                payment_method VARCHAR(20),
                current_project_id INTEGER REFERENCES projects(id),
                is_deleted BOOLEAN NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP
            )
        """))

        # ── clients ──
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP,
                is_deleted BOOLEAN DEFAULT 0,
                client_type VARCHAR(20) NOT NULL,
                name VARCHAR(200) NOT NULL,
                email VARCHAR(200),
                phone VARCHAR(50),
                address TEXT,
                payment_method VARCHAR(20),
                partnership_status VARCHAR(20),
                sector VARCHAR(20),
                project_name VARCHAR(300),
                project_summary TEXT,
                contract_value NUMERIC(15, 2),
                roles_distribution TEXT,
                partnership_id INTEGER REFERENCES partnerships(id)
            )
        """))

        # ── training_programs ──
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS training_programs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(300) NOT NULL,
                description TEXT,
                start_date DATE,
                end_date DATE,
                duration_hours INTEGER,
                status VARCHAR(20) DEFAULT 'مخطط',
                notes TEXT,
                is_deleted BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP
            )
        """))

        # ── trainees ──
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS trainees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(200) NOT NULL,
                email VARCHAR(200),
                phone VARCHAR(50),
                id_number VARCHAR(50),
                organization VARCHAR(200),
                address TEXT,
                date_of_birth DATE,
                gender VARCHAR(10),
                notes TEXT,
                is_deleted BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP
            )
        """))

        # ── trainers ──
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS trainers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(200) NOT NULL,
                email VARCHAR(200),
                phone VARCHAR(50),
                specialization VARCHAR(300),
                bio TEXT,
                is_active BOOLEAN DEFAULT 1,
                is_deleted BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP
            )
        """))

        print("[migration 0001] All Phase A tables created")
