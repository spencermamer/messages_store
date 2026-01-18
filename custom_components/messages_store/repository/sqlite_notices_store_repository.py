import sqlite3
from typing import Optional, List
from .notices_store import NoticesStore

class SQLiteNoticeStoreRepository(NoticesStore):
    def __init__(self, db_path: str):
        self.db_path = db_path

    def create_table(self):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute('''
                CREATE TABLE IF NOT EXISTS notices_store (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    slug TEXT NOT NULL UNIQUE,
                    notice TEXT NOT NULL,
                    priority INTEGER NOT NULL DEFAULT 3,
                    audience TEXT NOT NULL DEFAULT 'all',
                    expiration_date TEXT,
                    acknowledged INTEGER NOT NULL DEFAULT 0
                )
            ''')
            c.execute('''
                CREATE INDEX IF NOT EXISTS idx_priority ON notices_store (priority)
            ''')
            c.execute('''
                CREATE INDEX IF NOT EXISTS idx_audience ON notices_store (audience)
            ''')
            c.execute('''
                CREATE INDEX IF NOT EXISTS idx_acknowledged ON notices_store (acknowledged)
            ''')
            conn.commit()

    def insert_notice(self, slug: str, notice: str, priority: int = 3, audience: str = 'all', expiration_date: Optional[str] = None, acknowledged: int = 0):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            # Note: acknowledged is included in the table definition with a default, 
            # but we also include it here for explicit control if needed in the future.
            c.execute("INSERT INTO notices_store (slug, notice, priority, audience, expiration_date, acknowledged) VALUES (?, ?, ?, ?, ?, ?)", 
                      (slug, notice, priority, audience, expiration_date, acknowledged))
            conn.commit()

    def slug_exists(self, slug: str) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute("SELECT 1 FROM notices_store WHERE slug = ?", (slug,))
            return c.fetchone() is not None

    def retrieve_notice(self, slug: str) -> Optional[str]:
        """Return the notice content for the provided slug."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            c.execute(
                "SELECT notice FROM notices_store WHERE slug = ?",
                (slug,),
            )
            result = c.fetchone()
            return result["notice"] if result else None

    def delete_notice(self, slug: str) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            # Check if the notice exists before deleting
            c.execute("SELECT 1 FROM notices_store WHERE slug = ?", (slug,))
            if c.fetchone() is None:
                return False
            c.execute("DELETE FROM notices_store WHERE slug = ?", (slug,))
            conn.commit()
            return True

    def update_notice(self, slug: str, notice: Optional[str] = None, priority: Optional[int] = None, audience: Optional[str] = None, expiration_date: Optional[str] = None, acknowledged: Optional[int] = None) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            
            # Check if the notice exists
            c.execute("SELECT 1 FROM notices_store WHERE slug = ?", (slug,))
            if c.fetchone() is None:
                return False

            fields_to_update = []
            params = []

            if notice is not None:
                fields_to_update.append("notice = ?")
                params.append(notice)
            if priority is not None:
                fields_to_update.append("priority = ?")
                params.append(priority)
            if audience is not None:
                fields_to_update.append("audience = ?")
                params.append(audience)
            if expiration_date is not None: # This needs careful handling if you want to set it to NULL
                fields_to_update.append("expiration_date = ?")
                params.append(expiration_date)
            if acknowledged is not None:
                fields_to_update.append("acknowledged = ?")
                params.append(acknowledged)

            if not fields_to_update:
                return True # Or False, depending on desired behavior if no fields are updated

            sql = f"UPDATE notices_store SET {', '.join(fields_to_update)} WHERE slug = ?"
            params.append(slug)
            
            c.execute(sql, tuple(params))
            conn.commit()
            return True

    def retrieve_all_notices(self) -> List[dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            c.execute("SELECT slug, notice, priority, audience, expiration_date, acknowledged FROM notices_store")
            results = c.fetchall()
            return [dict(row) for row in results]

    def set_acknowledged_status(self, slug: str, acknowledged: int) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            
            # Check if the notice exists
            c.execute("SELECT 1 FROM notices_store WHERE slug = ?", (slug,))
            if c.fetchone() is None:
                return False
            
            c.execute("UPDATE notices_store SET acknowledged = ? WHERE slug = ?", (acknowledged, slug))
            conn.commit()
            return c.rowcount > 0 # Ensure a row was actually updated
