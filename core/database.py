"""
Database engine and session management.
محرك قاعدة البيانات وإدارة الجلسات.
"""
import os
from contextlib import contextmanager

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

# Database file path — relative to project root
_DB_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(_DB_DIR, "center.db")
DB_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    DB_URL,
    echo=False,
    connect_args={"check_same_thread": False},
)

# Enable SQLite foreign key enforcement
@event.listens_for(engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


SessionLocal = sessionmaker(bind=engine, autoflush=True, autocommit=False)


@contextmanager
def get_session():
    """
    Context manager for database sessions.
    مدير سياق لجلسات قاعدة البيانات — يضمن commit عند النجاح و rollback عند الخطأ.
    
    Usage:
        with get_session() as session:
            session.add(obj)
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_db():
    """
    Create all tables defined by SQLAlchemy models.
    إنشاء جميع الجداول المعرّفة في النماذج — يُستدعى عند أول تشغيل.
    """
    from models import Base
    Base.metadata.create_all(bind=engine)
