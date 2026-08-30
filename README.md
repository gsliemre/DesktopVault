# 🔐 Desktop Vault - Güvenli Şifre ve Veri Yöneticisi

Desktop Vault, kişisel hesap bilgilerinizi, şifrelerinizi ve hassas verilerinizi yerel veritabanında güçlü şifreleme algoritmalarıyla saklayan modern bir masaüstü uygulamasıdır.

## 🚀 Özellikler

* **Master Password Güvenliği:** PBKDF2 ve SHA-256 türetme algoritmaları ile korunan tek ana şifre ile erişim.
* **AES-256 (Fernet) Şifreleme:** Veritabanına kaydedilen tüm parolalar uçtan uca şifrelenir; düz metin (plain-text) olarak saklanmaz.
* **Modern Kullanıcı Arayüzü:** CustomTkinter ile tasarlanmış koyu tema (Dark Mode) odaklı responsive arayüz.
* **Kategori Yönetimi:** Sosyal Medya, İş, Finans ve Genel kategorileri altında düzenli veri takibi.
* **Dinamik Arama:** Kayıtlı hesaplar arasında anlık filtreleme ve arama.
* **Rastgele Şifre Oluşturucu:** Güçlü ve karmaşık parolalar üreten entegre araç.
* **Hızlı Kopyalama:** Şifreleri ve kullanıcı adlarını tek tıkla panoya kopyalama.

## 🛠️ Teknolojiler ve Kütüphaneler

* **Dil:** Python 3.x
* **GUI Framework:** CustomTkinter
* **Şifreleme:** Cryptography (Fernet / PBKDF2)
* **Veritabanı:** SQLite3
* **Yardımcı Araçlar:** Pyperclip

## 📦 Kurulum ve Çalıştırma

1. **Projeyi Klonlayın:**
   ```bash
   git clone [https://github.com/kullaniciadi/DesktopVault.git](https://github.com/kullaniciadi/DesktopVault.git)
   cd DesktopVault