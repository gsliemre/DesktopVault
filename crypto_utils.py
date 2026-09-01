import base64
import os
from typing import Union

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class Salt:
    """Güvenli ve kullanılabilir salt değeri taşıyan yardımcı sınıf."""

    def __init__(self, value: Union[bytes, str, None] = None, length: int = 16):
        if value is None:
            self._value = os.urandom(length)
        elif isinstance(value, str):
            self._value = value.encode('utf-8')
        elif isinstance(value, (bytes, bytearray)):
            self._value = bytes(value)
        else:
            raise TypeError('Salt değeri bytes, str veya None olmalıdır.')

    @classmethod
    def generate(cls, length: int = 16) -> 'Salt':
        """Yeni rastgele bir salt üretir."""
        return cls(length=length)

    @classmethod
    def from_value(cls, value: Union[bytes, str, None]) -> 'Salt':
        """Mevcut salt değerinden nesne oluşturur."""
        return cls(value=value)

    def to_bytes(self) -> bytes:
        """Salt değerini bayt dizisine çevirir."""
        return self._value

    def to_string(self) -> str:
        """Salt değerini metin olarak döndürür."""
        return self._value.decode('utf-8', errors='strict')

    def __bytes__(self) -> bytes:
        return self._value

    def __str__(self) -> str:
        return self.to_string()


class CryptoManager:
    """
    Kullanıcının Master Password'ünü temel alarak verileri AES-256 (Fernet) 
    ile şifreleyen ve çözen güvenlik sınıfı.
    """
    def __init__(self, master_password: str, salt: bytes = None):
        self.master_password = master_password.encode('utf-8')

        # Salt kontrolü ve tip doğrulaması
        if salt is None:
            self.salt = Salt.generate().to_bytes()
        elif isinstance(salt, Salt):
            self.salt = salt.to_bytes()
        elif isinstance(salt, str):
            self.salt = Salt.from_value(salt).to_bytes()
        else:
            self.salt = bytes(salt)

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