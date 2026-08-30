import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class CryptoManager:
    """
    Kullanıcının Master Password'ünü temel alarak verileri AES-256 (Fernet) 
    ile şifreleyen ve çözen güvenlik sınıfı.
    """
    def __init__(self, master_password: str, salt: bytes = None):
        self.master_password = master_password.encode('utf-8')
        
        # Salt yoksa yeni bir 16 baytlık rastgele salt üretilir
        if salt is None:
            self.salt = os.urandom(16)
        else:
            self.salt = salt

        self.key = self._generate_key()
        self.fernet = Fernet(self.key)

    def _generate_key(self) -> bytes:
        """Master password ve salt kullanarak 32 baytlık Fernet anahtarı türetir."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100_000,
        )
        return base64.urlsafe_b64encode(kdf.derive(self.master_password))

    def encrypt(self, plain_text: str) -> str:
        """Düz metin şifreyi/veriyi şifreler (string döner)."""
        if not plain_text:
            return ""
        encrypted_bytes = self.fernet.encrypt(plain_text.encode('utf-8'))
        return encrypted_bytes.decode('utf-8')

    def decrypt(self, encrypted_text: str) -> str:
        """Şifrelenmiş veriyi ana şifre ile çözer."""
        if not encrypted_text:
            return ""
        try:
            decrypted_bytes = self.fernet.decrypt(encrypted_text.encode('utf-8'))
            return decrypted_bytes.decode('utf-8')
        except Exception:
            raise ValueError("Hatalı Master Password veya bozuk veri!")

    def get_salt(self) -> bytes:
        """Veritabanında saklamak için üretilen salt değerini döndürür."""
        return self.salt