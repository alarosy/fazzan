"""
Migration to add image_path column to trainers and consultants.
"""
from sqlalchemy import text

def upgrade(engine):
    """Apply migration."""
    with engine.begin() as conn:
        try:
            conn.execute(text("ALTER TABLE trainers ADD COLUMN image_path VARCHAR(500)"))
        except Exception:
            pass

        try:
            conn.execute(text("ALTER TABLE consultants ADD COLUMN image_path VARCHAR(500)"))
        except Exception:
            pass
