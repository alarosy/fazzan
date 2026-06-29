"""
Migration 0002: Training program extensions and course enrollments.
توسعة البرامج التدريبية وإنشاء جدول التسجيل — Phase B.
"""
from sqlalchemy import text


def upgrade(engine):
    """Apply migration."""
    with engine.begin() as conn:
        # 1. Add columns to training_programs one by one for SQLite compatibility
        try:
            conn.execute(text("ALTER TABLE training_programs ADD COLUMN course_category VARCHAR(20)"))
        except Exception:
            pass

        try:
            conn.execute(text("ALTER TABLE training_programs ADD COLUMN hall_id INTEGER REFERENCES halls(id)"))
        except Exception:
            pass

        try:
            conn.execute(text("ALTER TABLE training_programs ADD COLUMN min_trainees INTEGER"))
        except Exception:
            pass

        try:
            conn.execute(text("ALTER TABLE training_programs ADD COLUMN max_trainees INTEGER"))
        except Exception:
            pass

        try:
            conn.execute(text("ALTER TABLE training_programs ADD COLUMN fee_per_trainee NUMERIC(10,2)"))
        except Exception:
            pass

        try:
            conn.execute(text("ALTER TABLE training_programs ADD COLUMN trainer_pay_type VARCHAR(20)"))
        except Exception:
            pass

        try:
            conn.execute(text("ALTER TABLE training_programs ADD COLUMN trainer_pay_value NUMERIC(10,2)"))
        except Exception:
            pass

        try:
            conn.execute(text("ALTER TABLE training_programs ADD COLUMN project_id INTEGER REFERENCES projects(id)"))
        except Exception:
            pass

        try:
            conn.execute(text("ALTER TABLE training_programs ADD COLUMN schedule_days VARCHAR(100)"))
        except Exception:
            pass

        try:
            conn.execute(text("ALTER TABLE training_programs ADD COLUMN schedule_time VARCHAR(50)"))
        except Exception:
            pass

        # 2. Create course_enrollments
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS course_enrollments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_id INTEGER NOT NULL REFERENCES training_programs(id) ON DELETE CASCADE,
                trainee_id INTEGER NOT NULL REFERENCES trainees(id) ON DELETE CASCADE,
                enrollment_status VARCHAR(20) DEFAULT 'مبدئي',
                payment_method VARCHAR(20),
                amount_paid NUMERIC(10,2),
                refund_requested BOOLEAN DEFAULT 0,
                refund_amount NUMERIC(10,2),
                refund_date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))

        print("[migration 0002] Training extensions applied successfully")
