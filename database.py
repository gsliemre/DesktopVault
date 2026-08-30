import sqlite3
import hashlib
import os

DB_NAME = "vault.db"

class DatabaseManager:
    """SQLite veritabanı işlemlerini yürüten ve Master Password 
    doğrulamasını sağlayan veri katmanı."""
    
    def __init__(self, db_name=DB_NAME):
        self.db_name = db_name
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_name)

    def _init_db(self):
        """Veritabanı tablolarını oluşturur."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Sistem ayarları / Master password doğrulama tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS system_config (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    master_hash TEXT NOT NULL,
                    salt BLOB NOT NULL
                )
            """)

            # Vault hesap kayıtları tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS vault_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    username TEXT NOT NULL,
                    encrypted_password TEXT NOT NULL,
                    category TEXT DEFAULT 'Genel',
                    url TEXT,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def is_master_set(self) -> bool:
        """Kullanıcının daha önce Master Password belirleyip belirlemediğini kontrol eder."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM system_config WHERE id = 1")
            return cursor.fetchone()[0] > 0

    def setup_master_password(self, master_password: str, salt: bytes):
        """İlk kurulumda Master Password hash'ini ve salt değerini kaydeder."""
        master_hash = hashlib.sha256(master_password.encode('utf-8') + salt).hexdigest()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO system_config (id, master_hash, salt)
                VALUES (1, ?, ?)
            """, (master_hash, salt))
            conn.commit()

    def verify_master_password(self, master_password: str) -> tuple[bool, bytes]:
        """Girilen Master Password'ü doğrular. Doğruysa (True, salt) döner."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT master_hash, salt FROM system_config WHERE id = 1")
            row = cursor.fetchone()
            if not row:
                return False, None
            
            stored_hash, salt = row
            input_hash = hashlib.sha256(master_password.encode('utf-8') + salt).hexdigest()
            
            if input_hash == stored_hash:
                return True, salt
            return False, None

    def add_entry(self, title, username, encrypted_password, category="Genel", url="", notes=""):
        """Yeni bir şifrelenmiş hesap kaydı ekler."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO vault_entries (title, username, encrypted_password, category, url, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (title, username, encrypted_password, category, url, notes))
            conn.commit()

    def get_all_entries(self, category_filter=None, search_query=None):
        """Kayıtlı hesapları getirir (kategori veya arama filtresine göre)."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT id, title, username, encrypted_password, category, url, notes FROM vault_entries WHERE 1=1"
            params = []

            if category_filter and category_filter != "Tümü":
                query += " AND category = ?"
                params.append(category_filter)

            if search_query:
                query += " AND (title LIKE ? OR username LIKE ?)"
                params.append(f"%{search_query}%")
                params.append(f"%{search_query}%")

            query += " ORDER BY id DESC"
            cursor.execute(query, params)
            return cursor.fetchall()

    def delete_entry(self, entry_id):
        """Belirtilen kaydı siler."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM vault_entries WHERE id = ?", (entry_id,))
            conn.commit()