import customtkinter as ctk
from tkinter import messagebox
import random
import string
import subprocess

from database import DatabaseManager
from crypto_utils import CryptoManager

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class DesktopVaultApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Desktop Vault - Güvenli Şifre Yöneticisi")
        self.geometry("950x650")
        self.resizable(False, False)

        self.db = DatabaseManager()
        self.crypto = None

        if not self.db.is_master_set():
            self._show_master_setup_screen()
        else:
            self._show_login_screen()

    def _clear_window(self):
        for widget in self.winfo_children():
            widget.destroy()

    # --- PANO YÖNETİMİ (WINDOWS CLIPBOARD) ---
    def _copy_to_clipboard(self, text: str):
        """Windows'un yerel 'clip' komutunu kullanarak metni kesin olarak panoya aktarır."""
        try:
            process = subprocess.Popen('clip', stdin=subprocess.PIPE, shell=True)
            process.communicate(input=text.encode('utf-8'))
            return True
        except Exception as e:
            messagebox.showerror("Pano Hatası", f"Kopyalama yapılamadı: {e}")
            return False

    def _show_toast(self, message):
        """Üst kısımdaki etikete 2.5 saniyeliğine bilgi mesajı yazdırır."""
        self.status_label.configure(text=message)
        self.after(2500, lambda: self.status_label.configure(text=""))

    # --- KURULUM & GİRİŞ EKRANLARI ---
    def _show_master_setup_screen(self):
        self._clear_window()
        frame = ctk.CTkFrame(self, width=400, height=350, corner_radius=15)
        frame.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(frame, text="🔐 İlk Kurulum", font=("Arial", 22, "bold")).pack(pady=(25, 10))
        ctk.CTkLabel(frame, text="Lütfen tüm şifrelerinizi koruyacak olan\nMaster Password'ünüzü belirleyin.", font=("Arial", 12), text_color="gray").pack(pady=(0, 20))

        self.pass_entry = ctk.CTkEntry(frame, placeholder_text="Master Password", show="*", width=280)
        self.pass_entry.pack(pady=10)

        self.pass_confirm_entry = ctk.CTkEntry(frame, placeholder_text="Master Password (Tekrar)", show="*", width=280)
        self.pass_confirm_entry.pack(pady=10)

        ctk.CTkButton(frame, text="Kaydet ve Başla", width=280, command=self._save_initial_master).pack(pady=20)

    def _save_initial_master(self):
        pwd1, pwd2 = self.pass_entry.get(), self.pass_confirm_entry.get()
        if not pwd1 or not pwd2:
            messagebox.showerror("Hata", "Lütfen şifre alanlarını boş bırakmayın.")
            return
        if pwd1 != pwd2:
            messagebox.showerror("Hata", "Şifreler eşleşmiyor!")
            return
        if len(pwd1) < 4:
            messagebox.showwarning("Uyarı", "Master Password en az 4 karakter olmalıdır.")
            return

        self.crypto = CryptoManager(pwd1)
        self.db.setup_master_password(pwd1, self.crypto.get_salt())
        self._show_main_dashboard()

    def _show_login_screen(self):
        self._clear_window()
        frame = ctk.CTkFrame(self, width=380, height=300, corner_radius=15)
        frame.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(frame, text="🔑 Desktop Vault", font=("Arial", 22, "bold")).pack(pady=(30, 10))
        ctk.CTkLabel(frame, text="Erişim için Master Password girin.", font=("Arial", 12), text_color="gray").pack(pady=(0, 20))

        self.login_pass_entry = ctk.CTkEntry(frame, placeholder_text="Master Password", show="*", width=260)
        self.login_pass_entry.pack(pady=10)
        self.login_pass_entry.bind("<Return>", lambda e: self._login_verify())

        ctk.CTkButton(frame, text="Giriş Yap", width=260, command=self._login_verify).pack(pady=15)

    def _login_verify(self):
        pwd = self.login_pass_entry.get()
        is_valid, salt = self.db.verify_master_password(pwd)
        if is_valid:
            self.crypto = CryptoManager(pwd, salt)
            self._show_main_dashboard()
        else:
            messagebox.showerror("Hata", "Yanlış Master Password!")

    # --- ANA PANEL ---
    def _show_main_dashboard(self):
        self._clear_window()

        # Sol Menü
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")

        ctk.CTkLabel(self.sidebar, text="🛡️ Vault Dashboard", font=("Arial", 16, "bold")).pack(pady=20, padx=10)

        self.cat_var = ctk.StringVar(value="Tümü")
        categories = ["Tümü", "Genel", "Sosyal Medya", "İş", "Finans"]

        for cat in categories:
            btn = ctk.CTkRadioButton(self.sidebar, text=cat, value=cat, variable=self.cat_var, command=self._load_vault_entries)
            btn.pack(pady=10, padx=20, anchor="w")

        ctk.CTkButton(self.sidebar, text="⚡ Şifre Üretici", command=self._open_generator_dialog).pack(side="bottom", pady=20, padx=15)

        # Üst Arama & Bilgi Barı
        top_frame = ctk.CTkFrame(self, height=60)
        top_frame.pack(side="top", fill="x", padx=15, pady=15)

        self.search_entry = ctk.CTkEntry(top_frame, placeholder_text="Hesap veya Kullanıcı Adı Arayın...", width=350)
        self.search_entry.pack(side="left", padx=15, pady=10)
        self.search_entry.bind("<KeyRelease>", lambda e: self._load_vault_entries())

        self.status_label = ctk.CTkLabel(top_frame, text="", font=("Arial", 11, "bold"), text_color="#2ed573")
        self.status_label.pack(side="left", padx=10)

        ctk.CTkButton(top_frame, text="+ Yeni Hesap Ekle", command=self._open_add_entry_dialog).pack(side="right", padx=15, pady=10)

        # Liste Alanı
        self.scroll_frame = ctk.CTkScrollableFrame(self, label_text="Kayıtlı Hesaplar")
        self.scroll_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        self._load_vault_entries()

    def _load_vault_entries(self):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        cat = self.cat_var.get()
        query = self.search_entry.get()
        entries = self.db.get_all_entries(category_filter=cat, search_query=query)

        if not entries:
            ctk.CTkLabel(self.scroll_frame, text="Kayıtlı veri bulunamadı.", text_color="gray").pack(pady=20)
            return

        for entry in entries:
            e_id, title, username, enc_pass, category, url, notes = entry
            
            card = ctk.CTkFrame(self.scroll_frame)
            card.pack(fill="x", pady=5, padx=5)

            info_label = ctk.CTkLabel(card, text=f"📌 {title} ({category})\n👤 Kullanıcı: {username}", justify="left", font=("Arial", 12, "bold"))
            info_label.pack(side="left", padx=15, pady=10)

            ctk.CTkButton(card, text="Sil", fg_color="red", hover_color="darkred", width=60, command=lambda idx=e_id: self._delete_entry(idx)).pack(side="right", padx=10)
            ctk.CTkButton(card, text="Şifreyi Kopyala", width=110, command=lambda ep=enc_pass, t=title: self._copy_password(ep, t)).pack(side="right", padx=5)
            ctk.CTkButton(card, text="Kullanıcı Kopyala", width=120, fg_color="gray", command=lambda u=username: self._copy_text(u, "Kullanıcı adı")).pack(side="right", padx=5)

    def _copy_password(self, encrypted_pass, title):
        try:
            plain_pass = self.crypto.decrypt(encrypted_pass)
            if self._copy_to_clipboard(plain_pass):
                self._show_toast(f"✓ {title} şifresi kopyalandı!")
        except Exception as e:
            messagebox.showerror("Hata", f"Şifre çözülemedi: {e}")

    def _copy_text(self, text, label_name="Metin"):
        if self._copy_to_clipboard(str(text)):
            self._show_toast(f"✓ {label_name} kopyalandı!")

    def _delete_entry(self, entry_id):
        if messagebox.askyesno("Onay", "Bu kaydı silmek istediğinizden emin misiniz?"):
            self.db.delete_entry(entry_id)
            self._load_vault_entries()

    # --- DIALOG PENCERELERİ ---
    def _open_add_entry_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Yeni Hesap Ekle")
        dialog.geometry("400x480")
        dialog.attributes("-topmost", True)

        ctk.CTkLabel(dialog, text="Hesap Bilgileri", font=("Arial", 16, "bold")).pack(pady=15)

        title_e = ctk.CTkEntry(dialog, placeholder_text="Başlık (ör: GitHub, Gmail)", width=300)
        title_e.pack(pady=8)

        user_e = ctk.CTkEntry(dialog, placeholder_text="Kullanıcı Adı / E-posta", width=300)
        user_e.pack(pady=8)

        pass_e = ctk.CTkEntry(dialog, placeholder_text="Şifre", width=300)
        pass_e.pack(pady=8)

        cat_combo = ctk.CTkComboBox(dialog, values=["Genel", "Sosyal Medya", "İş", "Finans"], width=300)
        cat_combo.pack(pady=8)

        url_e = ctk.CTkEntry(dialog, placeholder_text="URL / Web Sitesi (İsteğe Bağlı)", width=300)
        url_e.pack(pady=8)

        def save():
            t, u, p, c, link = title_e.get(), user_e.get(), pass_e.get(), cat_combo.get(), url_e.get()
            if not t or not u or not p:
                messagebox.showerror("Hata", "Başlık, Kullanıcı Adı ve Şifre zorunludur!", parent=dialog)
                return
            
            enc_p = self.crypto.encrypt(p)
            self.db.add_entry(title=t, username=u, encrypted_password=enc_p, category=c, url=link)
            dialog.destroy()
            self._load_vault_entries()

        ctk.CTkButton(dialog, text="Kaydet", command=save, width=300).pack(pady=20)

    def _open_generator_dialog(self):
        gen_window = ctk.CTkToplevel(self)
        gen_window.title("Güçlü Şifre Üretici")
        gen_window.geometry("350x250")
        gen_window.attributes("-topmost", True)

        ctk.CTkLabel(gen_window, text="🎲 Rastgele Şifre Üret", font=("Arial", 16, "bold")).pack(pady=15)

        result_e = ctk.CTkEntry(gen_window, width=250, font=("Consolas", 14))
        result_e.pack(pady=10)

        def generate():
            chars = string.ascii_letters + string.digits + "!@#$%^&*()"
            pwd = "".join(random.choice(chars) for _ in range(16))
            result_e.delete(0, "end")
            result_e.insert(0, pwd)
            self._copy_to_clipboard(pwd)
            self._show_toast("✓ Yeni şifre üretildi ve kopyalandı!")

        ctk.CTkButton(gen_window, text="Şifre Üret & Kopyala", command=generate, width=250).pack(pady=15)
        generate()

if __name__ == "__main__":
    app = DesktopVaultApp()
    app.mainloop()