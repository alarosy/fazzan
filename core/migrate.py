"""
Sequential migration runner.
نظام تشغيل الترحيلات التسلسلية — يتتبع الإصدارات عبر جدول _migrations.
"""
import importlib
import os

from sqlalchemy import text

from core.database import engine


def _ensure_migrations_table():
    """Create the _migrations tracking table if it doesn't exist."""
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS _migrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                version TEXT NOT NULL UNIQUE,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))


def _get_applied_versions():
    """Return set of already-applied migration version strings."""
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version FROM _migrations ORDER BY version"))
        return {row[0] for row in result}


def _discover_migrations():
    """
    Scan the migrations/ folder for numbered migration scripts.
    يبحث في مجلد migrations/ عن سكربتات الترحيل المرقّمة (مثل 0001_initial.py).
    Returns sorted list of (version_string, module_name).
    """
    migrations_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "migrations"
    )
    
    migrations = []
    if not os.path.isdir(migrations_dir):
        return migrations
    
    for filename in sorted(os.listdir(migrations_dir)):
        if filename.endswith(".py") and not filename.startswith("_"):
            version = filename.replace(".py", "")
            module_name = f"migrations.{version}"
            migrations.append((version, module_name))
    
    return migrations


def run_migrations():
    """
    Execute all pending migrations in order.
    تنفيذ جميع الترحيلات المعلّقة بالترتيب التسلسلي.
    """
    _ensure_migrations_table()
    applied = _get_applied_versions()
    pending = _discover_migrations()
    
    for version, module_name in pending:
        if version in applied:
            continue
        
        print(f"[migrate] Applying {version}...")
        module = importlib.import_module(module_name)
        
        if hasattr(module, "upgrade"):
            module.upgrade(engine)
        
        with engine.begin() as conn:
            conn.execute(
                text("INSERT INTO _migrations (version) VALUES (:v)"),
                {"v": version}
            )
        
        print(f"[migrate] Applied {version}")
    
    if not any(v not in applied for v, _ in pending):
        print("[migrate] Database is up to date.")
