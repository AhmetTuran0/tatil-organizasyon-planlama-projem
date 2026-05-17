import io
import sqlite3
import sys
from PyQt5.QtCore import QDate, Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QApplication,
    QComboBox,
    QDateEdit,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

# --- ÇIKTI KODLAMA HATASINI ÖNLEME ---
if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")


# --- GLOBAL GALAXY STİL TANIMI ---
GALAXY_STYLE = """
    QWidget { background-color: #0f0c29; color: white; font-family: 'Segoe UI'; }
    QTabWidget::pane { border: 1px solid #00d2ff; background: #0f0c29; border-radius: 5px; }
    QTabBar::tab { background: #1a1a2e; color: #888; padding: 12px 30px; font-weight: bold; border-top-left-radius: 6px; border-top-right-radius: 6px; }
    QTabBar::tab:selected { background: #9d50bb; color: white; border: 1px solid #00d2ff; border-bottom: none; }
    QLabel { color: #00d2ff; font-weight: bold; }
    QLineEdit, QComboBox, QDateEdit { background-color: #24243e; color: white; border: 1px solid #00d2ff; padding: 8px; border-radius: 4px; }
    QListWidget { background-color: #1a1a2e; border: 1px solid #302b63; border-radius: 8px; padding: 5px; }
    QListWidget::item { padding: 10px; border-bottom: 1px solid #24243e; }
    QListWidget::item:selected { background-color: #9d50bb; color: white; }
    QPushButton { background-color: #9d50bb; color: white; padding: 10px 20px; font-weight: bold; border-radius: 4px; border: none; }
    QPushButton:hover { background-color: #00d2ff; color: #0f0c29; }
"""


# --- MODERN ÖZEL UYARI PENCERESİ ---
class GalaxyMessageBox(QDialog):
    def __init__(self, baslik, mesaj, tip="info", parent=None):
        super().__init__(parent)
        self.setWindowTitle(baslik)
        self.setFixedSize(380, 180)
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.Dialog)
        
        renk = "#00d2ff"
        if tip == "hata":
            renk = "#e74c3c"
        elif tip == "basari":
            renk = "#2ecc71"

        self.setStyleSheet(f"""
            QDialog {{ background-color: #1a1a2e; border: 2px solid {renk}; border-radius: 10px; }}
            QLabel {{ color: white; font-family: 'Segoe UI'; }}
            QPushButton {{ background-color: {renk}; color: #0f0c29; font-weight: bold; padding: 8px 20px; border-radius: 4px; }}
            QPushButton:hover {{ background-color: white; color: #0f0c29; }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        ust_layout = QHBoxLayout()
        ikonlar = {"info": "ℹ️", "hata": "❌", "basari": "✅"}
        
        lbl_ikon = QLabel(ikonlar.get(tip, "ℹ️"))
        lbl_ikon.setStyleSheet("font-size: 24px; margin-right: 10px;")
        
        lbl_baslik = QLabel(baslik.upper())
        lbl_baslik.setStyleSheet(f"color: {renk}; font-size: 16px; font-weight: bold;")
        
        ust_layout.addWidget(lbl_ikon)
        ust_layout.addWidget(lbl_baslik)
        ust_layout.addStretch()
        layout.addLayout(ust_layout)

        lbl_mesaj = QLabel(mesaj)
        lbl_mesaj.setWordWrap(True)
        lbl_mesaj.setStyleSheet("font-size: 12px; margin-top: 10px; margin-bottom: 15px;")
        layout.addWidget(lbl_mesaj)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_ok = QPushButton("KAPAT")
        btn_ok.clicked.connect(self.accept)
        btn_layout.addWidget(btn_ok)
        layout.addLayout(btn_layout)


# --- POP-UP TATİL DÜZENLEME PENCERESİ ---
class GalaxyDuzenlemeDialog(QDialog):
    def __init__(self, plan_id, parent=None):
        super().__init__(parent)
        self.plan_id = plan_id
        self.setWindowTitle("Tatil Planını Düzenle")
        self.setFixedSize(450, 350)
        self.setStyleSheet(GALAXY_STYLE + """
            QDialog { background-color: #1a1a2e; border: 2px solid #9d50bb; border-radius: 10px; }
        """)
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.Dialog)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)

        # Üst Başlık
        lbl_baslik = QLabel("⚙️ TATİL PLANI DÜZENLEME")
        lbl_baslik.setStyleSheet("color: #9d50bb; font-size: 18px; font-weight: bold; margin-bottom: 15px;")
        layout.addWidget(lbl_baslik)

        # Form Alanları
        layout.addWidget(QLabel("Tatil Konumu / Bölgesi:"))
        self.ed_konum = QLineEdit()
        layout.addWidget(self.ed_konum)

        layout.addWidget(QLabel("Hizmet Sınıfı Paket:"))
        self.ed_sinif = QComboBox()
        self.ed_sinif.addItems(["Ekonomik Sınıf", "Standart Paket", "VIP Ultra Plus"])
        layout.addWidget(self.ed_sinif)

        tarih_lay = QHBoxLayout()
        vbox1 = QVBoxLayout()
        vbox1.addWidget(QLabel("Giriş Tarihi:"))
        self.ed_baslangic = QDateEdit(calendarPopup=True)
        vbox1.addWidget(self.ed_baslangic)

        vbox2 = QVBoxLayout()
        vbox2.addWidget(QLabel("Çıkış Tarihi:"))
        self.ed_bitis = QDateEdit(calendarPopup=True)
        vbox2.addWidget(self.ed_bitis)

        tarih_lay.addLayout(vbox1)
        tarih_lay.addLayout(vbox2)
        layout.addLayout(tarih_lay)

        layout.addSpacing(15)

        # Butonlar
        btn_lay = QHBoxLayout()
        btn_iptal = QPushButton("İPTAL")
        btn_iptal.setStyleSheet("background-color: #3a3a52; color: white;")
        btn_iptal.clicked.connect(self.reject)

        btn_kaydet = QPushButton("DEĞİŞİKLİKLERİ KAYDET")
        btn_kaydet.setStyleSheet("background-color: #9d50bb; color: white;")
        btn_kaydet.clicked.connect(self.verileri_guncelle)

        btn_lay.addWidget(btn_iptal)
        btn_lay.addWidget(btn_kaydet)
        layout.addLayout(btn_lay)

        self.verileri_yukle()

    def verileri_yukle(self):
        conn = sqlite3.connect("galaxy_travel_v3.db")
        cursor = conn.cursor()
        cursor.execute("SELECT konum, sinif, baslangic, bitis FROM planlar WHERE id = ?", (self.plan_id,))
        veri = cursor.fetchone()
        conn.close()

        if veri:
            konum, sinif, baslangic, bitis = veri
            self.ed_konum.setText(konum)
            self.ed_sinif.setCurrentText(sinif)
            self.ed_baslangic.setDate(QDate.fromString(baslangic, "dd.MM.yyyy"))
            self.ed_bitis.setDate(QDate.fromString(bitis, "dd.MM.yyyy"))

    def verileri_guncelle(self):
        konum = self.ed_konum.text().strip().upper()
        sinif = self.ed_sinif.currentText()
        bas = self.ed_baslangic.date().toString("dd.MM.yyyy")
        bit = self.ed_bitis.date().toString("dd.MM.yyyy")

        if not konum:
            GalaxyMessageBox("Hata", "Konum alanı boş bırakılamaz.", "hata", self).exec_()
            return

        conn = sqlite3.connect("galaxy_travel_v3.db")
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE planlar 
            SET konum = ?, sinif = ?, baslangic = ?, bitis = ? 
            WHERE id = ?
        """, (konum, sinif, bas, bit, self.plan_id))
        conn.commit()
        conn.close()
        self.accept()


def veritabani_hazirla():
    conn = sqlite3.connect("galaxy_travel_v3.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS uyeler (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ad_soyad TEXT UNIQUE
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS planlar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            uye_ad TEXT,
            konum TEXT,
            baslangic TEXT,
            bitis TEXT,
            sinif TEXT,
            durum TEXT DEFAULT 'Beklemede'
        )
    """)
    conn.commit()
    conn.close()


# --- GİRİŞ EKRANI ---
class GirisEkrani(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Galaxy Access")
        self.setFixedSize(400, 450)
        self.setStyleSheet("background-color: #0f0c29;")
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)

        self.lbl_title = QLabel("GALAXY\nTRAVEL")
        self.lbl_title.setStyleSheet("color: #00d2ff; font-size: 32px; font-weight: bold; margin-bottom: 20px;")
        self.lbl_title.setAlignment(Qt.AlignCenter)

        input_style = "padding: 12px; background-color: #24243e; color: white; border: 1px solid #00d2ff; border-radius: 5px; margin-bottom: 10px;"
        self.username = QLineEdit(placeholderText="Yönetici Adı (admin)")
        self.password = QLineEdit(placeholderText="Şifre (admin)")
        self.password.setEchoMode(QLineEdit.Password)
        self.username.setStyleSheet(input_style)
        self.password.setStyleSheet(input_style)

        btn_style = """
            QPushButton { background-color: #9d50bb; color: white; padding: 15px; border-radius: 5px; font-weight: bold; margin-top: 10px;}
            QPushButton:hover { background-color: #00d2ff; color: #0f0c29; }
        """
        self.btn_login = QPushButton("SİSTEME BAĞLAN")
        self.btn_login.clicked.connect(self.auth_check)
        self.btn_login.setStyleSheet(btn_style)

        layout.addWidget(self.lbl_title)
        layout.addWidget(self.username)
        layout.addWidget(self.password)
        layout.addWidget(self.btn_login)
        layout.addStretch()

    def auth_check(self):
        if self.username.text() == "admin" and self.password.text() == "admin":
            self.accept()
        else:
            GalaxyMessageBox("Erişim Reddedildi", "Hatalı yönetici adı veya şifre girdiniz!", "hata", self).exec_()


# --- ANA UYGULAMA PENCERESİ ---
class GalaxyYonetimSistemi(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Galaxy Travel Hub")
        self.resize(1300, 750)
        self.setStyleSheet(GALAXY_STYLE)

        main_layout = QVBoxLayout(self)

        header = QLabel("GALAXY TRAVEL")
        header.setStyleSheet("font-size: 20px; font-weight: bold; color: #00d2ff; letter-spacing: 2px; margin: 10px 0;")
        header.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header)

        self.tabs = QTabWidget()
        self.tab_planlama = QWidget()
        self.tab_yonetici = QWidget()

        self.tabs.addTab(self.tab_planlama, "✈️ TATİL PLANLAMA EKRANI")
        self.tabs.addTab(self.tab_yonetici, "👑 YÖNETİCİ KONTROL PANELİ")

        self.tasarla_planlama_sekmesi()
        self.tasarla_yonetici_sekmesi()

        main_layout.addWidget(self.tabs)
        self.yenile_tum_listeler()

    # --- 1. SEKME: TATİL PLANLAMA EKRANI ---
    def tasarla_planlama_sekmesi(self):
        layout = QHBoxLayout(self.tab_planlama)
        layout.setContentsMargins(20, 20, 20, 20)

        sol_panel = QFrame()
        sol_panel.setFixedWidth(400)
        sol_layout = QVBoxLayout(sol_panel)

        sol_layout.addWidget(QLabel("<h3>YENİ TATİL TALEBİ OLUŞTUR</h3>"))

        sol_layout.addWidget(QLabel("Uçuş/Seyahat Edecek Üye:"))
        self.cmb_plan_uye = QComboBox()
        sol_layout.addWidget(self.cmb_plan_uye)

        sol_layout.addWidget(QLabel("Gidilecek Destinasyon / Tatil Yeri:"))
        self.in_plan_konum = QLineEdit(placeholderText="Örn: İbiza, Maldivler, Mars...")
        sol_layout.addWidget(self.in_plan_konum)

        tarih_box = QHBoxLayout()
        vbox1 = QVBoxLayout()
        vbox1.addWidget(QLabel("Başlangıç Tarihi:"))
        self.date_baslangic = QDateEdit(calendarPopup=True)
        self.date_baslangic.setDate(QDate.currentDate())
        vbox1.addWidget(self.date_baslangic)

        vbox2 = QVBoxLayout()
        vbox2.addWidget(QLabel("Bitiş Tarihi:"))
        self.date_bitis = QDateEdit(calendarPopup=True)
        self.date_bitis.setDate(QDate.currentDate().addDays(7))
        vbox2.addWidget(self.date_bitis)

        tarih_box.addLayout(vbox1)
        tarih_box.addLayout(vbox2)
        sol_layout.addLayout(tarih_box)

        sol_layout.addWidget(QLabel("Konsept / Hizmet Sınıfı:"))
        self.cmb_plan_sinif = QComboBox()
        self.cmb_plan_sinif.addItems(["Ekonomik Sınıf", "Standart Paket", "VIP Ultra Plus"])
        sol_layout.addWidget(self.cmb_plan_sinif)

        self.btn_plan_kaydet = QPushButton("📝 TATİL PLANINI ÖN KAYDET")
        self.btn_plan_kaydet.setStyleSheet("background-color: #00d2ff; color: #0f0c29;")
        self.btn_plan_kaydet.clicked.connect(self.tatil_plani_ekle)
        sol_layout.addWidget(self.btn_plan_kaydet)

        sol_layout.addStretch()
        layout.addWidget(sol_panel)

        sag_panel = QFrame()
        sag_layout = QVBoxLayout(sag_panel)
        sag_layout.addWidget(QLabel("<h3>AKTİF VEYA BEKLEYEN TATİL PLANLARI</h3>"))
        self.list_genel_planlar = QListWidget()
        sag_layout.addWidget(self.list_genel_planlar)

        layout.addWidget(sag_panel)

    # --- 2. SEKME: YÖNETİCİ KONTROL PANELİ ---
    def tasarla_yonetici_sekmesi(self):
        layout = QHBoxLayout(self.tab_yonetici)
        layout.setContentsMargins(20, 20, 20, 20)

        sol_panel = QFrame()
        sol_panel.setFixedWidth(320)
        sol_layout = QVBoxLayout(sol_panel)

        sol_layout.addWidget(QLabel("<h3>SİSTEM ÜYE YÖNETİMİ</h3>"))
        self.in_yeni_uye = QLineEdit(placeholderText="Yeni Üye Adı Soyadı...")
        btn_yeni_uye = QPushButton("👤 Üye Ekle")
        btn_yeni_uye.clicked.connect(self.yeni_uye_ekle)
        sol_layout.addWidget(self.in_yeni_uye)
        sol_layout.addWidget(btn_yeni_uye)

        sol_layout.addWidget(QLabel("\nKayıtlı Üye Listesi:"))
        self.list_yonetici_uyeler = QListWidget()
        sol_layout.addWidget(self.list_yonetici_uyeler)
        layout.addWidget(sol_panel)

        sag_panel = QFrame()
        sag_layout = QVBoxLayout(sag_panel)

        sag_layout.addWidget(QLabel("<h3>YÖNETİCİ ONAY, ATAMA VE DÜZENLEME PANELİ</h3>"))
        self.list_yonetici_talepler = QListWidget()
        sag_layout.addWidget(self.list_yonetici_talepler)

        # Onaylama, Düzenleme ve Silme Buton Yan Yana Düzeni
        btn_box = QHBoxLayout()
        
        self.btn_onayla = QPushButton("✅ Seçili Planı Onayla")
        self.btn_onayla.setStyleSheet("background-color: #2ecc71; color: white;")
        self.btn_onayla.clicked.connect(self.plani_onayla)

        self.btn_duzenle = QPushButton("⚙️ Seçili Planı Düzenle")
        self.btn_duzenle.setStyleSheet("background-color: #9d50bb; color: white;")
        self.btn_duzenle.clicked.connect(self.plani_duzenle_penceresi_ac)

        self.btn_sil = QPushButton("🗑️ Planı İptal Et/Sil")
        self.btn_sil.setStyleSheet("background-color: #e74c3c; color: white;")
        self.btn_sil.clicked.connect(self.plani_sil)

        btn_box.addWidget(self.btn_onayla)
        btn_box.addWidget(self.btn_duzenle)
        btn_box.addWidget(self.btn_sil)
        sag_layout.addLayout(btn_box)

        layout.addWidget(sag_panel)

    # --- LOGIC METOTLARI ---

    def yeni_uye_ekle(self):
        ad = self.in_yeni_uye.text().strip()
        if ad:
            try:
                conn = sqlite3.connect("galaxy_travel_v3.db")
                cursor = conn.cursor()
                cursor.execute("INSERT INTO uyeler (ad_soyad) VALUES (?)", (ad,))
                conn.commit()
                conn.close()
                self.in_yeni_uye.clear()
                self.yenile_tum_listeler()
                GalaxyMessageBox("Başarılı", f"'{ad}' sisteme başarıyla eklendi.", "basari", self).exec_()
            except sqlite3.IntegrityError:
                GalaxyMessageBox("Hata", "Bu isimde bir üye zaten mevcut!", "hata", self).exec_()
        else:
            GalaxyMessageBox("Uyarı", "Lütfen geçerli bir üye adı girin!", "info", self).exec_()

    def tatil_plani_ekle(self):
        uye = self.cmb_plan_uye.currentText()
        konum = self.in_plan_konum.text().strip().upper()
        baslangic = self.date_baslangic.date().toString("dd.MM.yyyy")
        bitis = self.date_bitis.date().toString("dd.MM.yyyy")
        sinif = self.cmb_plan_sinif.currentText()

        if not uye:
            GalaxyMessageBox("Eksik Bilgi", "Sistemde kayıtlı üye bulunamadı.", "hata", self).exec_()
            return

        if konum:
            conn = sqlite3.connect("galaxy_travel_v3.db")
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO planlar (uye_ad, konum, baslangic, bitis, sinif) 
                VALUES (?, ?, ?, ?, ?)
            """, (uye, konum, baslangic, bitis, sinif))
            conn.commit()
            conn.close()

            self.in_plan_konum.clear()
            self.yenile_tum_listeler()
            GalaxyMessageBox("Talep Alındı", "Plan başarıyla oluşturulup onay listesine aktarıldı.", "basari", self).exec_()
        else:
            GalaxyMessageBox("Uyarı", "Lütfen tatil bölgesini/konumu boş bırakmayın!", "info", self).exec_()

    def plani_duzenle_penceresi_ac(self):
        """Aşağıdaki paneli iptal edip, verileri bağımsız pop-up pencerede açar."""
        secili_item = self.list_yonetici_talepler.currentItem()
        if secili_item:
            plan_id = secili_item.data(Qt.UserRole)
            # Pop-up formu çağırıyoruz
            dialog = GalaxyDuzenlemeDialog(plan_id, self)
            if dialog.exec_() == QDialog.Accepted:
                self.yenile_tum_listeler()
                GalaxyMessageBox("Güncellendi", "Tatil detayları başarıyla revize edildi.", "basari", self).exec_()
        else:
            GalaxyMessageBox("Seçim Yapılmadı", "Lütfen düzenlemek istediğiniz planı listeden seçin.", "info", self).exec_()

    def plani_onayla(self):
        secili_item = self.list_yonetici_talepler.currentItem()
        if secili_item:
            plan_id = secili_item.data(Qt.UserRole)
            conn = sqlite3.connect("galaxy_travel_v3.db")
            cursor = conn.cursor()
            cursor.execute("UPDATE planlar SET durum = 'Onaylandı' WHERE id = ?", (plan_id,))
            conn.commit()
            conn.close()
            self.yenile_tum_listeler()
            GalaxyMessageBox("Onaylandı", "Tatil planı onaylandı ve üye tatile gönderildi!", "basari", self).exec_()
        else:
            GalaxyMessageBox("Seçim Yapılmadı", "Lütfen onaylamak için listeden bir plan seçin.", "info", self).exec_()

    def plani_sil(self):
        secili_item = self.list_yonetici_talepler.currentItem()
        if secili_item:
            plan_id = secili_item.data(Qt.UserRole)
            conn = sqlite3.connect("galaxy_travel_v3.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM planlar WHERE id = ?", (plan_id,))
            conn.commit()
            conn.close()
            self.yenile_tum_listeler()
            GalaxyMessageBox("Silindi", "Plan sistemden tamamen kaldırıldı.", "basari", self).exec_()
        else:
            GalaxyMessageBox("Seçim Yapılmadı", "Lütfen silmek istediğiniz tatil planını seçin.", "info", self).exec_()

    def yenile_tum_listeler(self):
        conn = sqlite3.connect("galaxy_travel_v3.db")
        cursor = conn.cursor()

        cursor.execute("SELECT ad_soyad FROM uyeler")
        tum_uyeler = [row[0] for row in cursor.fetchall()]

        self.cmb_plan_uye.clear()
        self.cmb_plan_uye.addItems(tum_uyeler)

        self.list_yonetici_uyeler.clear()
        for uye in tum_uyeler:
            self.list_yonetici_uyeler.addItem(f"👤 {uye}")

        cursor.execute("SELECT id, uye_ad, konum, baslangic, bitis, sinif, durum FROM planlar")
        tum_planlar = cursor.fetchall()

        self.list_genel_planlar.clear()
        self.list_yonetici_talepler.clear()

        for pid, uye_ad, konum, bas, bit, sinif, durum in tum_planlar:
            durum_icon = "🟢" if durum == "Onaylandı" else "🟡"
            gosterim_metni = (
                f"{durum_icon} [{durum.upper()}] - {uye_ad}\n"
                f"📍 Konum: {konum} | Paket: {sinif}\n"
                f"📅 Tarih: {bas} - {bit}"
            )

            self.list_genel_planlar.addItem(gosterim_metni)

            yonetici_item = QListWidgetItem(gosterim_metni)
            yonetici_item.setData(Qt.UserRole, pid)
            self.list_yonetici_talepler.addItem(yonetici_item)

        conn.close()


def main():
    veritabani_hazirla()
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))

    login = GirisEkrani()
    if login.exec_() == QDialog.Accepted:
        pencere = GalaxyYonetimSistemi()
        pencere.show()
        sys.exit(app.exec_())


if __name__ == "__main__":
    main()