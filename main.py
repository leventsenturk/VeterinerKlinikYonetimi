import tkinter as tk
from tkinter import messagebox, ttk
import mysql.connector
from datetime import datetime, timedelta
from PIL import Image, ImageTk

# --- Veritabanı Ayarları ---
DB_CONFIG = {
    "host": "localhost",
    "user": "levent", # Kendi MySQL kullanıcı adınızı girin
    "password": "1234", # Kendi MySQL şifrenizi girin
    "database": "veteriner_klinik"
}

# --- Renk Paleti (Yeşil Tonları) ---
COLORS = {
    "primary": "#2E8B57",    # Deniz Yeşili (Daha koyu, ana vurgu)
    "secondary": "#66CDAA",  # Orta Deniz Yeşili (Daha açık, ikincil vurgu)
    "background": "#F0FFF0", # Honeydew (çok açık yeşil/beyaz)
    "frame_bg": "#E0FFE0",   # Açık Mint Yeşili (çerçeve arka planı)
    "button_bg": "#98FB98",  # Soluk Yeşil (düğme arka planı)
    "text_dark": "#2F4F4F",  # Koyu Gri/Mavi (yazı rengi)
    "text_light": "#FFFFFF", # Beyaz
    "heading_bg": "#66CDAA", # Açık Turkuaz (tablo başlığı)
    "treeview_selected": "#3CB371", # Orta Deniz Yeşili (seçili satır)
    "error": "#DC143C"       # Crimson Kırmızısı (hata mesajları)
}

# --- Veritabanı Sınıfı ---
class Veritabani:
    def __init__(self, config):
        self.config = config
        self.baglanti = None

    def baglan(self):
        """MySQL veritabanına bağlantı kurar ve bağlantı nesnesini döndürür."""
        try:
            if self.baglanti is None or not self.baglanti.is_connected():
                self.baglanti = mysql.connector.connect(**self.config)
            return self.baglanti
        except mysql.connector.Error as err:
            messagebox.showerror(
                "Veritabanı Bağlantı Hatası",
                f"Veritabanına bağlanılamadı:\n{err}\\n\\n"
                "Lütfen MySQL sunucunuzun çalıştığından, kullanıcı adı ve şifrenin doğru olduğundan "
                "ve 'veteriner_klinik' veritabanının mevcut olduğundan emin olun.",
                icon="error" 
            )
            self.baglanti = None
            return None

    def kapat(self):
        """Veritabanı bağlantısını kapatır."""
        if self.baglanti and self.baglanti.is_connected():
            self.baglanti.close()
            self.baglanti = None

    def sorgu_calistir(self, sorgu, veri=None, commit=False, fetch_results=False):
        """
        Veritabanı sorgusunu çalıştırır.
        :param sorgu: Çalıştırılacak SQL sorgusu.
        :param veri: Sorguya geçirilecek veriler (tuple).
        :param commit: True ise değişiklikleri commit eder.
        :param fetch_results: True ise tüm sonuçları (SELECT için) fetch eder ve döndürür.
        :return: Sorgu sonuçları (list of tuples) SELECT için, aksi halde True/False başarılı/başarısız.
        """
        db = self.baglan()
        if db is None:
            return None 

        cursor = db.cursor()
        try:
            cursor.execute(sorgu, veri)
            
            if commit:
                db.commit()
                return True 
            
            if fetch_results:
                results = cursor.fetchall() 
                return results 
            else:
                return True 

        except mysql.connector.Error as err:
            messagebox.showerror("Veritabanı Hatası", f"Sorgu çalıştırılırken bir hata oluştu:\n{err}\nSorgu: {sorgu}", icon="error") 
            if commit: 
                db.rollback() 
            return None 
        finally:
            if cursor:
                cursor.close()
            self.kapat() 


# --- Ana Uygulama Sınıfı ---
class VeterinerUygulamasi:
    def __init__(self, root):
        self.root = root
        self.root.title("Vefa Veteriner Klinik Sistemi")
        self.db = Veritabani(DB_CONFIG) 

        # --- İkonları Yükle ---
        self.icons = self._load_icons()

        # --- Stil Ayarları ---
        self.style = ttk.Style()
        self.style.theme_use("clam") 

        # Genel arka plan rengi
        self.root.configure(bg=COLORS["background"])
        self.style.configure("TFrame", background=COLORS["background"])
        self.style.configure("TLabelframe", background=COLORS["frame_bg"])
        self.style.configure("TLabelframe.Label", background=COLORS["frame_bg"], foreground=COLORS["text_dark"])


        # Genel fontlar
        self.style.configure(".", font=("Segoe UI", 10), background=COLORS["background"], foreground=COLORS["text_dark"]) 
        self.style.configure("TLabel", font=("Segoe UI", 10), background=COLORS["background"], foreground=COLORS["text_dark"])
        self.style.configure("TEntry", font=("Segoe UI", 10), fieldbackground=COLORS["text_light"], foreground=COLORS["text_dark"])
        self.style.configure("TCombobox", font=("Segoe UI", 10), fieldbackground=COLORS["text_light"], foreground=COLORS["text_dark"])
        self.style.configure("TNotebook.Tab", font=("Segoe UI", 10, "bold"), background=COLORS["secondary"], foreground=COLORS["text_light"])
        self.style.map("TNotebook.Tab", background=[("selected", COLORS["primary"])], foreground=[("selected", COLORS["text_light"])])


        # Buton stilleri
        self.style.configure("TButton", 
                            font=("Segoe UI", 11, "bold"), 
                            padding=10, 
                            background=COLORS["button_bg"], 
                            foreground=COLORS["text_dark"],
                            relief="flat") 
        self.style.map("TButton", 
                       background=[("active", COLORS["primary"]), ("!disabled", COLORS["button_bg"])],
                       foreground=[("active", COLORS["text_light"]), ("!disabled", COLORS["text_dark"])])
        
        self.style.configure("MainMenu.TButton", 
                            font=("Segoe UI", 13, "bold"), 
                            padding=[15, 12], # Yatay, Dikey
                            background=COLORS["primary"],
                            foreground=COLORS["text_light"])
        self.style.map("MainMenu.TButton", 
                       background=[("active", COLORS["secondary"])],
                       foreground=[("active", COLORS["text_dark"])])


        # Treeview için özel stil
        self.style.configure("Treeview.Heading", 
                             font=("Segoe UI", 11, "bold"), 
                             background=COLORS["heading_bg"], 
                             foreground=COLORS["text_dark"])
        self.style.configure("Treeview", 
                             font=("Segoe UI", 9), 
                             rowheight=25,
                             background=COLORS["text_light"], 
                             foreground=COLORS["text_dark"], 
                             fieldbackground=COLORS["text_light"]) 
        self.style.map("Treeview", 
                       background=[("selected", COLORS["treeview_selected"])],
                       foreground=[("selected", COLORS["text_light"])]) 

        self._ana_menu_olustur()

    def _load_icons(self):
        icons = {}
        icon_path = "icons/"
        
        # Hata yönetimi için try-except bloğu
        def get_icon(name, size=(24, 24)):
            try:
                img = Image.open(f"{icon_path}{name}.png")
                img = img.resize(size, Image.Resampling.LANCZOS)
                return ImageTk.PhotoImage(img)
            except FileNotFoundError:
                print(f"Uyarı: '{icon_path}{name}.png' ikonu bulunamadı. Lütfen ikon dosyasının var olduğundan emin olun.")
                return None
            except Exception as e:
                print(f"Hata: '{icon_path}{name}.png' ikonu yüklenirken bir sorun oluştu: {e}")
                return None

        # Menü ikonları
        icons["paw_print"] = get_icon("paw_print", size=(64, 64)) 
        icons["add_animal"] = get_icon("add_animal", size=(32, 32))
        icons["list_animals"] = get_icon("list_animals", size=(32, 32))
        icons["add_owner"] = get_icon("add_owner", size=(32, 32))
        icons["vaccine"] = get_icon("vaccine", size=(32, 32))
        icons["upcoming_vaccine"] = get_icon("upcoming_vaccine", size=(32, 32))
        icons["appointment"] = get_icon("appointment", size=(32, 32))
        icons["examination"] = get_icon("examination", size=(32, 32))
        icons["exit"] = get_icon("exit", size=(32, 32))

        icons["save"] = get_icon("save", size=(24, 24))
        icons["delete"] = get_icon("delete", size=(24, 24))
        icons["update"] = get_icon("update", size=(24, 24))
        icons["details"] = get_icon("details", size=(24, 24))
        icons["refresh"] = get_icon("refresh", size=(24, 24))
        icons["filter"] = get_icon("filter", size=(24, 24))
        icons["add"] = get_icon("add", size=(24, 24)) 

        return icons

    def _ana_menu_olustur(self):
        # Eğer mevcut bir frame varsa temizle
        for widget in self.root.winfo_children():
            widget.destroy()

        main_frame = ttk.Frame(self.root, padding="30 40 30 40", style="TFrame") 
        main_frame.pack(expand=True, fill="both")
        
        # Başlık etiketi ve ikon
        header_frame = ttk.Frame(main_frame, style="TFrame")
        header_frame.pack(pady=20, anchor="w", fill="x") # Sola hizala ve yatayda doldur
        
        if self.icons["paw_print"]:
            ttk.Label(header_frame, image=self.icons["paw_print"], background=COLORS["background"]).pack(side="left", padx=10)
        ttk.Label(header_frame, text="Veteriner Klinik Yönetim Sistemi", font=("Segoe UI", 20, "bold"), 
                  foreground=COLORS["primary"], background=COLORS["background"]).pack(side="left")

        # Butonlar için bir çerçeve
        button_container = ttk.Frame(main_frame, style="TFrame")
        button_container.pack(pady=10)

        
        button_width = 30
        button_pady = 10

        # Menü düğmeleri
        self._create_main_menu_button(button_container, "Hayvan Ekle", self._hayvan_ekle_penceresi, "add_animal", button_width, button_pady)
        self._create_main_menu_button(button_container, "Hayvanları Listele/Yönet", self._hayvanlari_listele_penceresi, "list_animals", button_width, button_pady)
        self._create_main_menu_button(button_container, "Sahipleri Listele/Yönet", self._sahipleri_listele_penceresi, "add_owner", button_width, button_pady) 
        self._create_main_menu_button(button_container, "Aşı Takip Sistemi", self._asi_ekle_penceresi, "vaccine", button_width, button_pady)
        self._create_main_menu_button(button_container, "Yaklaşan Aşılar", self._yaklasan_asilar_penceresi, "upcoming_vaccine", button_width, button_pady)
        self._create_main_menu_button(button_container, "Randevu Yönetimi", self._randevulari_listele_penceresi, "appointment", button_width, button_pady)
        self._create_main_menu_button(button_container, "Muayene ve Tedavi Kayıtları", self._muayene_listele_penceresi, "examination", button_width, button_pady)
        self._create_main_menu_button(button_container, "Çıkış", self.root.quit, "exit", button_width, button_pady)
   
    def _create_main_menu_button(self, parent, text, command, icon_name, width, pady):
        """Ana menü düğmelerini ikonlarla oluşturur."""
        btn = ttk.Button(parent, text=text, command=command, style="MainMenu.TButton")
        if self.icons.get(icon_name):
            btn.config(image=self.icons[icon_name], compound="left") 
        btn.pack(pady=pady, fill="x", ipadx=width) 

    def _create_button_with_icon(self, parent, text, command, icon_name):
        """Küçük düğmeleri ikonlarla oluşturur."""
        btn = ttk.Button(parent, text=text, command=command)
        if self.icons.get(icon_name):
            btn.config(image=self.icons[icon_name], compound="left")
        return btn

    def _yaklasan_asilar_penceresi(self):
        top = tk.Toplevel(self.root, bg=COLORS["background"])
        top.title("Yaklaşan Aşılar")
        top.grab_set()
        top.geometry("800x500") # Pencere boyutu

        # Başlık sola hizalandı
        ttk.Label(top, text="Yaklaşan Aşı Kayıtları", font=("Segoe UI", 14, "bold"), 
                  background=COLORS["background"], foreground=COLORS["primary"]).pack(pady=10, anchor="w", padx=10)

        # Arama ve Filtreleme alanı
        filter_frame = ttk.LabelFrame(top, text="Filtreleme", padding="10", style="TLabelframe")
        filter_frame.pack(padx=10, pady=5, fill="x")

        ttk.Label(filter_frame, text="Sonraki Aşılar (gün):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.gun_sayisi_var = tk.StringVar(value="30")
        gun_entry = ttk.Entry(filter_frame, textvariable=self.gun_sayisi_var, width=5)
        gun_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        self._create_button_with_icon(filter_frame, "Filtrele", lambda: yukle_yaklasan_asilar(int(self.gun_sayisi_var.get())), "filter").grid(row=0, column=2, padx=5, pady=5)
        
        filter_frame.columnconfigure(1, weight=1) 

        tree_frame = ttk.Frame(top, style="TFrame")
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

        tree = ttk.Treeview(tree_frame, columns=("Hayvan", "Aşı Adı", "Aşı Tarihi", "Sonraki Aşı Tarihi", "Kalan Gün"), show="headings")
        tree.pack(side="left", fill="both", expand=True)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        vsb.pack(side="right", fill="y")
        tree.configure(yscrollcommand=vsb.set)

        tree.heading("Hayvan", text="Hayvan")
        tree.heading("Aşı Adı", text="Aşı Adı")
        tree.heading("Aşı Tarihi", text="Aşı Tarihi")
        tree.heading("Sonraki Aşı Tarihi", text="Sonraki Aşı Tarihi")
        tree.heading("Kalan Gün", text="Kalan Gün")

        tree.column("Hayvan", width=150, anchor="w")
        tree.column("Aşı Adı", width=120, anchor="w")
        tree.column("Aşı Tarihi", width=120, anchor="center")
        tree.column("Sonraki Aşı Tarihi", width=120, anchor="center")
        tree.column("Kalan Gün", width=80, anchor="center")

        def yukle_yaklasan_asilar(gun_sayisi=30):
            for item in tree.get_children():
                tree.delete(item)
            
            bugun = datetime.now().date()
            gecerli_tarih = bugun + timedelta(days=gun_sayisi)

            sorgu = """
                SELECT h.isim, at.asi_adi, at.asi_tarihi, at.sonraki_asi_tarihi
                FROM asi_takip at
                JOIN hayvanlar h ON at.hayvan_id = h.id
                WHERE at.sonraki_asi_tarihi IS NOT NULL
                AND at.sonraki_asi_tarihi BETWEEN %s AND %s
                ORDER BY at.id ASC  -- ID'ye göre küçükten büyüğe sırala
            """
            kayitlar = self.db.sorgu_calistir(sorgu, (bugun.strftime("%Y-%m-%d"), gecerli_tarih.strftime("%Y-%m-%d")), fetch_results=True)

            if kayitlar:
                for kayit in kayitlar:
                    hayvan_adi, asi_adi, asi_tarihi, sonraki_asi_tarihi = kayit
                    
                    asi_tarihi_str = asi_tarihi.strftime("%Y-%m-%d") if asi_tarihi else ""
                    sonraki_asi_str = sonraki_asi_tarihi.strftime("%Y-%m-%d") if sonraki_asi_tarihi else ""
                    
                    # Düzeltme: sonraki_asi_tarihi zaten bir datetime.date objesi olduğu için .date() metodunu çağırmaya gerek yok.
                    # Eğer sonraki_asi_tarihi bir datetime.datetime objesi olsaydı, .date() kullanmak doğru olurdu.
                    # MySQL'den gelen 'DATE' tipi sütunlar genellikle Python'da datetime.date objesi olarak eşlenir.
                    kalan_gun = (sonraki_asi_tarihi - bugun).days
                    
                    tree.insert("", "end", values=(hayvan_adi, asi_adi, asi_tarihi_str, sonraki_asi_str, kalan_gun))
            else:
                messagebox.showinfo("Bilgi", "Yaklaşan aşı kaydı bulunamadı.", icon="info")
        
        yukle_yaklasan_asilar(int(self.gun_sayisi_var.get())) # Load on open

    def _get_hayvanlar_ve_sahipler(self):
        """Hayvan ve sahip bilgilerini veritabanından çeker."""
        hayvanlar = {}
        sahipler = {}
        
        hayvan_data = self.db.sorgu_calistir("SELECT id, isim FROM hayvanlar", fetch_results=True)
        if hayvan_data:
            hayvanlar = {f"{isim} (ID:{id})": id for id, isim in hayvan_data}

        sahip_data = self.db.sorgu_calistir("SELECT id, isim FROM sahipler", fetch_results=True)
        if sahip_data:
            sahipler = {f"{isim} (ID: {id})": id for id, isim in sahip_data}
            
        return hayvanlar, sahipler

    # --- Hayvan Ekleme Penceresi ---
    def _hayvan_ekle_penceresi(self):
        top = tk.Toplevel(self.root, bg=COLORS["background"])
        top.title("Hayvan Ekle")
        top.grab_set()
        top.geometry("450x450") # Sabit pencere boyutu
        top.resizable(False, False) # Boyut değiştirmeyi kapat

        form_frame = ttk.LabelFrame(top, text="Yeni Hayvan Bilgileri", padding="20", style="TLabelframe")
        form_frame.pack(padx=20, pady=20, fill="both", expand=True)

        hayvan_dict, sahip_dict = self._get_hayvanlar_ve_sahipler()


        fields = [
            ("Hayvan Adı:", "isim"),
            ("Tür:", "tur"),
            ("Cins:", "cins"),
            ("Doğum Tarihi (YYYY-AA-GG):", "dogum_tarihi"),
            ("Geliş Sebebi:", "gelis_sebebi"),
            ("Sahip:", "sahip"),
        ]
        entries = {}

        for i, (label_text, key_name) in enumerate(fields):
            ttk.Label(form_frame, text=label_text).grid(row=i, column=0, padx=10, pady=8, sticky="w")
            if key_name == "gelis_sebebi":
                gelis_var = tk.StringVar(form_frame)
                gelis_options = ["Aşı", "Yaralanma", "Parazit", "Kontrol", "Diğer"]
                entries[key_name] = ttk.Combobox(form_frame, textvariable=gelis_var, values=gelis_options, state="readonly")
                entries[key_name].set("Kontrol")
                entries[key_name].grid(row=i, column=1, padx=10, pady=8, sticky="ew")
            elif key_name == "sahip":
                sahip_var = tk.StringVar(form_frame)
                entries[key_name] = ttk.Combobox(form_frame, textvariable=sahip_var, values=list(sahip_dict.keys()), state="readonly")
                if sahip_dict: # Sahipler varsa ilkini seç
                    entries[key_name].set(next(iter(sahip_dict)))
                entries[key_name].grid(row=i, column=1, padx=10, pady=8, sticky="ew")
            else:
                entry = ttk.Entry(form_frame)
                entries[key_name] = entry
                entry.grid(row=i, column=1, padx=10, pady=8, sticky="ew")
                if key_name == "dogum_tarihi":
                    entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        form_frame.columnconfigure(1, weight=1) # İkinci sütunun (girişler) genişlemesini sağlar

        def kaydet():
            # Use the consistent keys defined above
            isim = entries['isim'].get().strip()
            tur = entries['tur'].get().strip()
            cins = entries['cins'].get().strip()
            dogum = entries['dogum_tarihi'].get().strip()
            gelis = entries['gelis_sebebi'].get().strip()
            secilen_sahip_str = entries['sahip'].get()
            sahip_id = sahip_dict.get(secilen_sahip_str)

            # Boş alan kontrolü güçlendirildi
            if not isim:
                messagebox.showerror("Hata", "Hayvan Adı boş bırakılamaz.", icon="warning")
                return
            if not tur:
                messagebox.showerror("Hata", "Tür boş bırakılamaz.", icon="warning")
                return
            if not cins:
                messagebox.showerror("Hata", "Cins boş bırakılamaz.", icon="warning")
                return
            if not dogum:
                messagebox.showerror("Hata", "Doğum Tarihi boş bırakılamaz.", icon="warning")
                return
            if not gelis:
                messagebox.showerror("Hata", "Geliş Sebebi boş bırakılamaz.", icon="warning")
                return
            if not secilen_sahip_str or sahip_id is None: 
                messagebox.showerror("Hata", "Lütfen geçerli bir Sahip seçin.", icon="warning")
                return

            try:
                datetime.strptime(dogum, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Hata", "Doğum tarihi formatı yanlış. Lütfen YYYY-AA-GG formatını kullanın.", icon="warning")
                return

            sorgu = "INSERT INTO hayvanlar (isim, tur, cins, dogum_tarihi, gelis_sebebi, sahip_id) VALUES (%s, %s, %s, %s, %s, %s)"
            veri = (isim, tur, cins, dogum, gelis, sahip_id)
            if self.db.sorgu_calistir(sorgu, veri, commit=True):
                messagebox.showinfo("Başarılı", "Hayvan kaydı eklendi.", icon="info")
                top.destroy()

        self._create_button_with_icon(top, "Kaydet", kaydet, "save").pack(pady=15, padx=20, fill="x")

    # --- Aşı Ekleme Penceresi ---
    def _asi_ekle_penceresi(self):
        top = tk.Toplevel(self.root, bg=COLORS["background"])
        top.title("Aşı Takip Sistemi ")
        top.grab_set()
        top.geometry("500x550")
        top.resizable(False, False)

        form_frame = ttk.LabelFrame(top, text="Yeni Aşı Kaydı", padding="20", style="TLabelframe")
        form_frame.pack(padx=20, pady=20, fill="both", expand=True)

        hayvan_dict, _ = self._get_hayvanlar_ve_sahipler()

        ttk.Label(form_frame, text="Hayvan:").grid(row=0, column=0, padx=10, pady=8, sticky="w")
        hayvan_combo = ttk.Combobox(form_frame, width=30, values=list(hayvan_dict.keys()), state="readonly")
        if hayvan_dict:
            hayvan_combo.set(next(iter(hayvan_dict)))
        hayvan_combo.grid(row=0, column=1, padx=10, pady=8, sticky="ew")

        ttk.Label(form_frame, text="Aşı Adı:").grid(row=1, column=0, padx=10, pady=8, sticky="w")
        asi_adi_entry = ttk.Entry(form_frame)
        asi_adi_entry.grid(row=1, column=1, padx=10, pady=8, sticky="ew")

        ttk.Label(form_frame, text="Aşı Tarihi (YYYY-AA-GG):").grid(row=2, column=0, padx=10, pady=8, sticky="w")
        asi_tarihi_entry = ttk.Entry(form_frame)
        asi_tarihi_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        asi_tarihi_entry.grid(row=2, column=1, padx=10, pady=8, sticky="ew")

        ttk.Label(form_frame, text="Sonraki Aşı Tarihi (YYYY-AA-GG):").grid(row=3, column=0, padx=10, pady=8, sticky="w")
        sonraki_asi_entry = ttk.Entry(form_frame)
        sonraki_asi_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        sonraki_asi_entry.grid(row=3, column=1, padx=10, pady=8, sticky="ew")

        ttk.Label(form_frame, text="Notlar:").grid(row=4, column=0, padx=10, pady=8, sticky="nw")
        notlar_entry = tk.Text(form_frame, height=5, width=40, font=("Segoe UI", 10))
        notlar_entry.grid(row=4, column=1, padx=10, pady=8, sticky="ew")

        form_frame.columnconfigure(1, weight=1)

        def kaydet():
            secilen_hayvan_str = hayvan_combo.get().strip()
            asi_adi = asi_adi_entry.get().strip()
            asi_tarihi_str = asi_tarihi_entry.get().strip()
            sonraki_asi_str = sonraki_asi_entry.get().strip()
            notlar = notlar_entry.get("1.0", "end-1c").strip() # "-1c" son newline karakterini siler

            if not (secilen_hayvan_str and asi_adi and asi_tarihi_str):
                messagebox.showerror("Hata", "Lütfen Hayvan, Aşı Adı ve Aşı Tarihini doldurun.", icon="warning")
                return
            
            hayvan_id = hayvan_dict.get(secilen_hayvan_str)
            if not hayvan_id:
                messagebox.showerror("Hata", "Lütfen geçerli bir hayvan seçin.", icon="warning")
                return
            
            try:
                datetime.strptime(asi_tarihi_str, "%Y-%m-%d")
                if sonraki_asi_str:
                    datetime.strptime(sonraki_asi_str, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Hata", "Tarih formatları yanlış. Lütfen YYYY-AA-GG formatını kullanın.", icon="warning")
                return

            sql = """
                INSERT INTO asi_takip (hayvan_id, asi_adi, asi_tarihi, sonraki_asi_tarihi, notlar)
                VALUES (%s, %s, %s, %s, %s)
            """
            veri = (hayvan_id, asi_adi, asi_tarihi_str, sonraki_asi_str if sonraki_asi_str else None, notlar if notlar else None)
            if self.db.sorgu_calistir(sql, veri, commit=True):
                messagebox.showinfo("Başarılı", "Aşı kaydı eklendi.", icon="info")
                top.destroy()

        self._create_button_with_icon(top, "Kaydet", kaydet, "save").pack(pady=15, padx=20, fill="x")

    # --- Sahip Ekleme Penceresi ---
    def _sahip_ekle_penceresi(self):
        top = tk.Toplevel(self.root, bg=COLORS["background"])
        top.title("Sahip Ekle")
        top.grab_set()
        top.geometry("450x350")
        top.resizable(False, False)

        form_frame = ttk.LabelFrame(top, text="Yeni Sahip Bilgileri", padding="20", style="TLabelframe")
        form_frame.pack(padx=20, pady=20, fill="both", expand=True) # expand=True kalabilir, buton grid içinde olacak

        ttk.Label(form_frame, text="Adı Soyadı:").grid(row=0, column=0, padx=10, pady=8, sticky="w")
        isim_entry = ttk.Entry(form_frame)
        isim_entry.grid(row=0, column=1, padx=10, pady=8, sticky="ew")

        ttk.Label(form_frame, text="Telefon:").grid(row=1, column=0, padx=10, pady=8, sticky="w")
        telefon_entry = ttk.Entry(form_frame)
        telefon_entry.grid(row=1, column=1, padx=10, pady=8, sticky="ew")

        ttk.Label(form_frame, text="Adres:").grid(row=2, column=0, padx=10, pady=8, sticky="nw")
        adres_text = tk.Text(form_frame, height=4, width=40, font=("Segoe UI", 10))
        adres_text.grid(row=2, column=1, padx=10, pady=8, sticky="ew")

        form_frame.columnconfigure(1, weight=1)

        def kaydet():
            isim = isim_entry.get().strip()
            telefon = telefon_entry.get().strip()
            adres = adres_text.get("1.0", "end-1c").strip()

            if not (isim and telefon):
                messagebox.showerror("Hata", "Lütfen Adı Soyadı ve Telefon alanlarını doldurun.", icon="warning")
                return

            sorgu = "INSERT INTO sahipler (isim, telefon, adres) VALUES (%s, %s, %s)"
            veri = (isim, telefon, adres if adres else None)
            if self.db.sorgu_calistir(sorgu, veri, commit=True):
                messagebox.showinfo("Başarılı", "Sahip kaydı eklendi.", icon="info")
                top.destroy()
        
        # Butonu doğrudan form_frame'in içine grid ile yerleştir
        # En son satır (adres) 2. satırda, bu yüzden buton 3. satıra gelecek
        self._create_button_with_icon(form_frame, "Kaydet", kaydet, "save").grid(row=3, column=0, columnspan=2, pady=15, padx=20, sticky="e")
        
    # --- Sahip Listeleme ve Yönetimi Penceresi ---
    def _sahipleri_listele_penceresi(self):
        top = tk.Toplevel(self.root, bg=COLORS["background"])
        top.title("Sahipleri Listele")
        top.grab_set()
        top.geometry("800x500") 

        # Başlık sola hizalandı
        ttk.Label(top, text="Kayıtlı Sahipler", font=("Segoe UI", 14, "bold"), 
                  background=COLORS["background"], foreground=COLORS["primary"]).pack(pady=10, anchor="w", padx=10)

        tree_frame = ttk.Frame(top, style="TFrame")
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

        tree = ttk.Treeview(tree_frame, columns=("ID", "Adı Soyadı", "Telefon", "Adres"), show="headings")
        tree.pack(side="left", fill="both", expand=True)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        vsb.pack(side="right", fill="y")
        tree.configure(yscrollcommand=vsb.set)

        tree.heading("ID", text="ID")
        tree.heading("Adı Soyadı", text="Adı Soyadı")
        tree.heading("Telefon", text="Telefon")
        tree.heading("Adres", text="Adres")

        tree.column("ID", width=50, anchor="center")
        tree.column("Adı Soyadı", width=150, anchor="w")
        tree.column("Telefon", width=120, anchor="w")
        tree.column("Adres", width=250, anchor="w")

        def verileri_yukle():
            for item in tree.get_children():
                tree.delete(item)
            # Sorguyu ID'ye göre sıralayacak şekilde güncellendi
            kayitlar = self.db.sorgu_calistir("SELECT id, isim, telefon, adres FROM sahipler ORDER BY id ASC", fetch_results=True)
            if kayitlar:
                for kayit in kayitlar:
                    tree.insert("", "end", values=kayit)
            else:
                messagebox.showinfo("Bilgi", "Kayıtlı sahip bulunamadı.", icon="info")
        
        def sahip_sil():
            secilen_item = tree.selection()
            if not secilen_item:
                messagebox.showwarning("Uyarı", "Lütfen silmek istediğiniz sahibi seçin.", icon="warning")
                return

            sahip_id = tree.item(secilen_item, "values")[0]
            sahip_adi = tree.item(secilen_item, "values")[1]

            # Sahibe bağlı hayvan var mı kontrol et
            hayvan_sayisi_sorgu = "SELECT COUNT(*) FROM hayvanlar WHERE sahip_id = %s"
            hayvan_sayisi_result = self.db.sorgu_calistir(hayvan_sayisi_sorgu, (sahip_id,), fetch_results=True)
            
            if hayvan_sayisi_result and hayvan_sayisi_result[0][0] > 0:
                messagebox.showerror("Hata", f"'{sahip_adi}' adlı sahibe bağlı hayvanlar bulunmaktadır. "
                                              "Sahibi silmek için önce bu hayvanları başka bir sahibe atamalı veya silmelisiniz.", icon="error")
                return

            if messagebox.askyesno("Onay", f"'{sahip_adi}' adlı sahibi silmek istediğinize emin misiniz? Bu işlem geri alınamaz.", icon="question"):
                sorgu = "DELETE FROM sahipler WHERE id=%s"
                if self.db.sorgu_calistir(sorgu, (sahip_id,), commit=True):
                    messagebox.showinfo("Silindi", "Sahip başarıyla silindi.", icon="info")
                    verileri_yukle()
                else:
                    messagebox.showerror("Hata", "Sahip silinirken bir hata oluştu.", icon="error")

        def sahip_guncelle():
            secilen_item = tree.selection()
            if not secilen_item:
                messagebox.showwarning("Uyarı", "Lütfen güncellemek istediğiniz sahibi seçin.", icon="warning")
                return
            kayit_id = tree.item(secilen_item, "values")[0]
            self._sahip_guncelle_penceresi(kayit_id, verileri_yukle) # Güncelleme sonrası listeyi yenilemek için callback

        verileri_yukle()

        button_frame = ttk.Frame(top, style="TFrame")
        button_frame.pack(pady=10)

        self._create_button_with_icon(button_frame, "Sahip Ekle", self._sahip_ekle_penceresi, "add").pack(side="left", padx=7)
        self._create_button_with_icon(button_frame, "Sahip Sil", sahip_sil, "delete").pack(side="left", padx=7)
        self._create_button_with_icon(button_frame, "Sahip Güncelle", sahip_guncelle, "update").pack(side="left", padx=7)
        self._create_button_with_icon(button_frame, "Listeyi Yenile", verileri_yukle, "refresh").pack(side="left", padx=7)


    # --- Sahip Güncelleme Penceresi ---
    def _sahip_guncelle_penceresi(self, kayit_id, callback=None):
        top = tk.Toplevel(self.root, bg=COLORS["background"])
        top.title("Sahip Güncelle")
        top.grab_set()
        top.geometry("450x350")
        top.resizable(False, False)

        form_frame = ttk.LabelFrame(top, text=f"Sahip Bilgilerini Güncelle (ID: {kayit_id})", padding="20", style="TLabelframe")
        form_frame.pack(padx=20, pady=20, fill="both", expand=True)

        sahip_data_list = self.db.sorgu_calistir("SELECT isim, telefon, adres FROM sahipler WHERE id=%s", (kayit_id,), fetch_results=True)
        if not sahip_data_list:
            messagebox.showerror("Hata", "Sahip kaydı bulunamadı veya veritabanı hatası.", icon="error")
            top.destroy()
            return
        kayit = sahip_data_list[0]

        ttk.Label(form_frame, text="Adı Soyadı:").grid(row=0, column=0, padx=10, pady=8, sticky="w")
        isim_entry = ttk.Entry(form_frame)
        isim_entry.insert(0, kayit[0])
        isim_entry.grid(row=0, column=1, padx=10, pady=8, sticky="ew")

        ttk.Label(form_frame, text="Telefon:").grid(row=1, column=0, padx=10, pady=8, sticky="w")
        telefon_entry = ttk.Entry(form_frame)
        telefon_entry.insert(0, kayit[1])
        telefon_entry.grid(row=1, column=1, padx=10, pady=8, sticky="ew")

        ttk.Label(form_frame, text="Adres:").grid(row=2, column=0, padx=10, pady=8, sticky="nw")
        adres_text = tk.Text(form_frame, height=4, width=40, font=("Segoe UI", 10))
        adres_text.insert("1.0", kayit[2] if kayit[2] else "")
        adres_text.grid(row=2, column=1, padx=10, pady=8, sticky="ew")

        form_frame.columnconfigure(1, weight=1)

        def guncelle():
            yeni_isim = isim_entry.get().strip()
            yeni_telefon = telefon_entry.get().strip()
            yeni_adres = adres_text.get("1.0", "end-1c").strip()

            if not (yeni_isim and yeni_telefon):
                messagebox.showerror("Hata", "Lütfen Adı Soyadı ve Telefon alanlarını doldurun.", icon="warning")
                return

            sorgu = "UPDATE sahipler SET isim=%s, telefon=%s, adres=%s WHERE id=%s"
            veri = (yeni_isim, yeni_telefon, yeni_adres if yeni_adres else None, kayit_id)
            if self.db.sorgu_calistir(sorgu, veri, commit=True):
                messagebox.showinfo("Başarılı", "Sahip kaydı güncellendi.", icon="info")
                top.destroy()
                if callback:
                    callback() # Listeyi yenile

        self._create_button_with_icon(top, "Güncelle", guncelle, "update").pack(pady=15, padx=20, fill="x")


    # --- Hayvan Güncelleme Penceresi ---
    def _hayvan_guncelle_penceresi(self, kayit_id, callback=None):
        top = tk.Toplevel(self.root, bg=COLORS["background"])
        top.title("Hayvan Güncelle")
        top.grab_set()
        top.geometry("450x550")
        top.resizable(False, False)

        form_frame = ttk.LabelFrame(top, text=f"Hayvan Bilgilerini Güncelle (ID: {kayit_id})", padding="20", style="TLabelframe")
        form_frame.pack(padx=20, pady=20, fill="both", expand=True)

        hayvan_data_list = self.db.sorgu_calistir("SELECT isim, tur, cins, dogum_tarihi, gelis_sebebi, sahip_id, notlar FROM hayvanlar WHERE id=%s", (kayit_id,), fetch_results=True)
        if not hayvan_data_list:
            messagebox.showerror("Hata", "Hayvan kaydı bulunamadı veya veritabanı hatası.", icon="error")
            top.destroy()
            return
        kayit = hayvan_data_list[0]

        sahip_liste = self.db.sorgu_calistir("SELECT id, isim FROM sahipler", fetch_results=True)
        if not sahip_liste:
            messagebox.showerror("Hata", "Sahip bilgileri yüklenemedi.", icon="error")
            top.destroy()
            return

        sahip_dict = {f"{isim} (ID: {id})": id for id, isim in sahip_liste}
        ters_sahip_dict = {id: f"{isim} (ID: {id})" for id, isim in sahip_liste}

        # Define fields and their corresponding keys for consistency
        fields = [
            ("İsim:", "isim"),
            ("Tür:", "tur"),
            ("Cins:", "cins"),
            ("Doğum Tarihi (YYYY-AA-GG):", "dogum_tarihi"),
            ("Geliş Sebebi:", "gelis_sebebi"),
            ("Sahip:", "sahip"),
            ("Notlar:", "notlar")
        ]
        entries = {} # This dictionary will store the widget references

        for i, (label_text, key_name) in enumerate(fields):
            ttk.Label(form_frame, text=label_text).grid(row=i, column=0, padx=10, pady=8, sticky="w")
            if key_name == "gelis_sebebi":
                entries[key_name] = ttk.Combobox(form_frame, values=["Aşı", "Yaralanma", "Parazit", "Kontrol", "Diğer"], state="readonly")
                entries[key_name].set(kayit[4])
                entries[key_name].grid(row=i, column=1, padx=10, pady=8, sticky="ew")
            elif key_name == "sahip":
                sahip_var = tk.StringVar(form_frame)
                entries[key_name] = ttk.Combobox(form_frame, textvariable=sahip_var, values=list(sahip_dict.keys()), state="readonly")
                entries[key_name].set(ters_sahip_dict.get(kayit[5], ""))
                entries[key_name].grid(row=i, column=1, padx=10, pady=8, sticky="ew")
            elif key_name == "notlar":
                notlar_text = tk.Text(form_frame, height=5, width=40, font=("Segoe UI", 10))
                notlar_text.insert("1.0", kayit[6] if kayit[6] else "")
                entries[key_name] = notlar_text
                notlar_text.grid(row=i, column=1, padx=10, pady=8, sticky="ew")
            else:
                entry = ttk.Entry(form_frame)
                entries[key_name] = entry
                entry.grid(row=i, column=1, padx=10, pady=8, sticky="ew")
                
                # Populate entry fields with existing data based on their key_name
                if key_name == "isim": entry.insert(0, kayit[0])
                elif key_name == "tur": entry.insert(0, kayit[1])
                elif key_name == "cins": entry.insert(0, kayit[2])
                elif key_name == "dogum_tarihi": entry.insert(0, kayit[3].strftime("%Y-%m-%d") if kayit[3] else "")


        form_frame.columnconfigure(1, weight=1)

        def guncelle():
            # Access entries using the consistent keys
            yeni_isim = entries['isim'].get().strip()
            yeni_tur = entries['tur'].get().strip()
            yeni_cins = entries['cins'].get().strip()
            yeni_dogum = entries['dogum_tarihi'].get().strip()
            yeni_gelis = entries['gelis_sebebi'].get().strip()
            yeni_sahip_id = sahip_dict.get(entries['sahip'].get())
            yeni_notlar = entries['notlar'].get("1.0", "end-1c").strip()

            if not all([yeni_isim, yeni_tur, yeni_cins, yeni_dogum, yeni_gelis, yeni_sahip_id]):
                messagebox.showerror("Hata", "Tüm gerekli alanları doldurun.", icon="warning")
                return

            try:
                datetime.strptime(yeni_dogum, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Hata", "Doğum tarihi formatı yanlış. Lütfen YYYY-AA-GG formatını kullanın.", icon="warning")
                return

            sorgu = """
                UPDATE hayvanlar SET isim=%s, tur=%s, cins=%s, dogum_tarihi=%s, gelis_sebebi=%s, sahip_id=%s, notlar=%s WHERE id=%s
            """
            veri = (yeni_isim, yeni_tur, yeni_cins, yeni_dogum, yeni_gelis, yeni_sahip_id, yeni_notlar if yeni_notlar else None, kayit_id)
            if self.db.sorgu_calistir(sorgu, veri, commit=True):
                messagebox.showinfo("Başarılı", "Kayıt güncellendi.", icon="info")
                top.destroy()
                if callback:
                    callback() 

        self._create_button_with_icon(top, "Güncelle", guncelle, "update").pack(pady=15, padx=20, fill="x")

    # --- Hayvan Listeleme Penceresi ---
    def _hayvanlari_listele_penceresi(self):
        top = tk.Toplevel(self.root, bg=COLORS["background"])
        top.title("Hayvanları Listele")
        top.grab_set()
        top.geometry("1000x600") # Daha büyük pencere

        # Başlık sola hizalandı
        ttk.Label(top, text="Kayıtlı Hayvanlar", font=("Segoe UI", 14, "bold"), 
                  background=COLORS["background"], foreground=COLORS["primary"]).pack(pady=10, anchor="w", padx=10)

        tree_frame = ttk.Frame(top, style="TFrame")
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Sütunları güncelle: "Doğum Tarihi" yerine "Yaş"
        tree = ttk.Treeview(tree_frame, columns=("ID", "İsim", "Tür", "Cins", "Yaş", "Geliş Sebebi", "Sahip"), show="headings")
        tree.pack(side="left", fill="both", expand=True)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        vsb.pack(side="right", fill="y")
        tree.configure(yscrollcommand=vsb.set)

        tree.heading("ID", text="ID")
        tree.heading("İsim", text="İsim")
        tree.heading("Tür", text="Tür")
        tree.heading("Cins", text="Cins")
        tree.heading("Yaş", text="Yaş")  # Sütun başlığını "Yaş" olarak değiştir
        tree.heading("Geliş Sebebi", text="Geliş Sebebi")
        tree.heading("Sahip", text="Sahip")

        tree.column("ID", width=40, anchor="center")
        tree.column("İsim", width=120, anchor="w")
        tree.column("Tür", width=90, anchor="w")
        tree.column("Cins", width=90, anchor="w")
        tree.column("Yaş", width=80, anchor="center") # Yaş sütunu için genişlik ayarı
        tree.column("Geliş Sebebi", width=120, anchor="w")
        tree.column("Sahip", width=150, anchor="w")

        def verileri_yukle():
            for item in tree.get_children():
                tree.delete(item)
            # Sorguyu ID'ye göre sıralayacak şekilde güncellendi
            kayitlar = self.db.sorgu_calistir("""
                SELECT h.id, h.isim, h.tur, h.cins, h.dogum_tarihi, h.gelis_sebebi, s.isim
                FROM hayvanlar h JOIN sahipler s ON h.sahip_id = s.id
                ORDER BY h.id ASC 
            """, fetch_results=True)
            if kayitlar:
                bugun = datetime.now().date()
                for kayit in kayitlar:
                    hayvan_id, isim, tur, cins, dogum_tarihi, gelis_sebebi, sahip_isim = kayit
                    
                    yas_str = "Bilinmiyor"
                    if dogum_tarihi:
                        # Yaş hesaplama
                        age = bugun.year - dogum_tarihi.year - ((bugun.month, bugun.day) < (dogum_tarihi.month, dogum_tarihi.day))
                        if age > 0:
                            yas_str = f"{age} yıl"
                        else:
                            # 1 yaşından küçükse ayları veya günleri hesapla
                            delta = bugun - dogum_tarihi
                            if delta.days < 30:
                                yas_str = f"{delta.days} gün"
                            elif delta.days < 365:
                                months = delta.days // 30 # Yaklaşık ay hesabı
                                yas_str = f"{months} ay"
                            else:
                                yas_str = "1 yaşından küçük" # Nadir durum, ama kapsayıcı olsun

                    tree.insert("", "end", values=(hayvan_id, isim, tur, cins, yas_str, gelis_sebebi, sahip_isim))
            else:
                messagebox.showinfo("Bilgi", "Kayıtlı hayvan bulunamadı.", icon="info")
        
        def kayit_sil():
            secilen_item = tree.selection()
            if not secilen_item:
                messagebox.showwarning("Uyarı", "Lütfen silmek istediğiniz kaydı seçin.", icon="warning")
                return

            kayit_id = tree.item(secilen_item, "values")[0]

            if messagebox.askyesno("Onay", f"ID {kayit_id} olan kaydı silmek istediğinize emin misiniz? Bu işlem bağlantılı tüm kayıtları da silebilir!", icon="question"):
                sorgu = "DELETE FROM hayvanlar WHERE id=%s"
                if self.db.sorgu_calistir(sorgu, (kayit_id,), commit=True):
                    messagebox.showinfo("Silindi", "Kayıt başarıyla silindi.", icon="info")
                    verileri_yukle()

        def kayit_guncelle():
            secilen_item = tree.selection()
            if not secilen_item:
                messagebox.showwarning("Uyarı", "Lütfen güncellemek istediğiniz kaydı seçin.", icon="warning")
                return
            kayit_id = tree.item(secilen_item, "values")[0]
            self._hayvan_guncelle_penceresi(kayit_id, verileri_yukle)

        def hayvan_detay_goster():
            secilen_item = tree.selection()
            if not secilen_item:
                messagebox.showwarning("Uyarı", "Lütfen detaylarını görmek istediğiniz hayvanı seçin.", icon="warning")
                return
            kayit_id = tree.item(secilen_item, "values")[0]
            self._hayvan_detay_penceresi(kayit_id)

        verileri_yukle()

        button_frame = ttk.Frame(top, style="TFrame")
        button_frame.pack(pady=10)

        self._create_button_with_icon(button_frame, "Sil", kayit_sil, "delete").pack(side="left", padx=7)
        self._create_button_with_icon(button_frame, "Güncelle", kayit_guncelle, "update").pack(side="left", padx=7)
        self._create_button_with_icon(button_frame, "Detay Gör", hayvan_detay_goster, "details").pack(side="left", padx=7)
        self._create_button_with_icon(button_frame, "Yenile", verileri_yukle, "refresh").pack(side="left", padx=7)

    def _hayvan_detay_penceresi(self, hayvan_id):
        top = tk.Toplevel(self.root, bg=COLORS["background"])
        top.title(f"Hayvan Detayı (ID: {hayvan_id})")
        top.grab_set()
        top.geometry("800x650") 

        # Hayvan temel bilgilerini gösteren çerçeve
        info_frame = ttk.LabelFrame(top, text="Hayvan Bilgileri", padding=15, style="TLabelframe")
        info_frame.pack(fill="x", padx=15, pady=10)
        
        # Grid sistemi için daha fazla boşluk ve hizalama
        info_frame.columnconfigure(1, weight=1) # İkinci sütun genişlesin
        info_frame.columnconfigure(3, weight=1) # Dördüncü sütun genişlesin

        hayvan_bilgi = self.db.sorgu_calistir(
            """
            SELECT h.isim, h.tur, h.cins, h.dogum_tarihi, h.gelis_sebebi, s.isim, h.notlar
            FROM hayvanlar h JOIN sahipler s ON h.sahip_id = s.id
            WHERE h.id = %s
            """, (hayvan_id,), fetch_results=True
        )
        if not hayvan_bilgi:
            messagebox.showerror("Hata", "Hayvan bilgileri bulunamadı veya veritabanı hatası.", icon="error")
            top.destroy()
            return
        
        hayvan_bilgi = hayvan_bilgi[0] 

        ttk.Label(info_frame, text="Adı:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        ttk.Label(info_frame, text=hayvan_bilgi[0], font=("Segoe UI", 10, "bold"), 
                  foreground=COLORS["primary"]).grid(row=0, column=1, sticky="w", padx=5, pady=2)
        
        ttk.Label(info_frame, text="Tür:").grid(row=0, column=2, sticky="w", padx=15, pady=2)
        ttk.Label(info_frame, text=hayvan_bilgi[1]).grid(row=0, column=3, sticky="w", padx=5, pady=2)

        ttk.Label(info_frame, text="Cins:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        ttk.Label(info_frame, text=hayvan_bilgi[2]).grid(row=1, column=1, sticky="w", padx=5, pady=2)
        
        dogum_tarihi_str = hayvan_bilgi[3].strftime("%Y-%m-%d") if hayvan_bilgi[3] else "Belirtilmemiş"
        ttk.Label(info_frame, text="Doğum Tarihi:").grid(row=1, column=2, sticky="w", padx=15, pady=2)
        ttk.Label(info_frame, text=dogum_tarihi_str).grid(row=1, column=3, sticky="w", padx=5, pady=2)

        ttk.Label(info_frame, text="Geliş Sebebi:").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        ttk.Label(info_frame, text=hayvan_bilgi[4]).grid(row=2, column=1, sticky="w", padx=5, pady=2)
        
        ttk.Label(info_frame, text="Sahibi:").grid(row=2, column=2, sticky="w", padx=15, pady=2)
        ttk.Label(info_frame, text=hayvan_bilgi[5], font=("Segoe UI", 10, "bold"),
                  foreground=COLORS["primary"]).grid(row=2, column=3, sticky="w", padx=5, pady=2)

        ttk.Label(info_frame, text="Notlar/Uyarılar:").grid(row=3, column=0, sticky="nw", padx=5, pady=5)
        notlar_text = tk.Text(info_frame, height=4, width=60, font=("Segoe UI", 9), wrap="word", 
                              bg=COLORS["text_light"], fg=COLORS["text_dark"])
        notlar_text.insert("1.0", hayvan_bilgi[6] if hayvan_bilgi[6] else "")
        notlar_text.grid(row=3, column=1, columnspan=3, sticky="ew", padx=5, pady=5)
        
        def notlari_kaydet():
            yeni_notlar = notlar_text.get("1.0", "end-1c").strip()
            sorgu = "UPDATE hayvanlar SET notlar = %s WHERE id = %s"
            if self.db.sorgu_calistir(sorgu, (yeni_notlar if yeni_notlar else None, hayvan_id), commit=True):
                messagebox.showinfo("Başarılı", "Notlar güncellendi.", icon="info")
            else:
                messagebox.showerror("Hata", "Notlar güncellenirken bir hata oluştu.", icon="error")

        self._create_button_with_icon(info_frame, "Notları Kaydet", notlari_kaydet, "save").grid(row=4, column=3, sticky="e", padx=5, pady=5)


        # Sekmeli Görünüm (Notebook)
        notebook = ttk.Notebook(top)
        notebook.pack(fill="both", expand=True, padx=15, pady=10)

        # --- Aşı Geçmişi Tabı ---
        asi_frame = ttk.Frame(notebook, style="TFrame")
        notebook.add(asi_frame, text="Aşı Geçmişi")
        self._asi_gecmisi_tab_olustur(asi_frame, hayvan_id) # Fonksiyonu ayrı çağıralım

        # --- Randevu Geçmişi Tabı ---
        randevu_frame = ttk.Frame(notebook, style="TFrame")
        notebook.add(randevu_frame, text="Randevu Geçmişi")
        self._randevu_gecmisi_tab_olustur(randevu_frame, hayvan_id)

        # --- Muayene ve Tedavi Geçmişi Tabı ---
        muayene_frame = ttk.Frame(notebook, style="TFrame")
        notebook.add(muayene_frame, text="Muayene/Tedavi")
        self._muayene_gecmisi_tab_olustur(muayene_frame, hayvan_id)

    # Aşı Geçmişi Tabı için yardımcı fonksiyon
    def _asi_gecmisi_tab_olustur(self, parent_frame, hayvan_id):
        tree = ttk.Treeview(parent_frame, columns=("Aşı Adı", "Aşı Tarihi", "Sonraki Aşı", "Notlar"), show="headings")
        tree.pack(fill="both", expand=True, padx=5, pady=5)

        vsb = ttk.Scrollbar(tree, orient="vertical", command=tree.yview)
        vsb.pack(side="right", fill="y")
        tree.configure(yscrollcommand=vsb.set)

        tree.heading("Aşı Adı", text="Aşı Adı")
        tree.heading("Aşı Tarihi", text="Aşı Tarihi")
        tree.heading("Sonraki Aşı", text="Sonraki Aşı")
        tree.heading("Notlar", text="Notlar")

        tree.column("Aşı Adı", width=120, anchor="w")
        tree.column("Aşı Tarihi", width=120, anchor="center")
        tree.column("Sonraki Aşı", width=120, anchor="center")
        tree.column("Notlar", width=200, anchor="w")

        asi_kayitlar = self.db.sorgu_calistir(
            "SELECT asi_adi, asi_tarihi, sonraki_asi_tarihi, notlar FROM asi_takip WHERE hayvan_id = %s ORDER BY id ASC", # ID'ye göre sırala
            (hayvan_id,), fetch_results=True
        )
        if asi_kayitlar:
            for kayit in asi_kayitlar:
                asi_tarihi_str = kayit[1].strftime("%Y-%m-%d") if kayit[1] else ""
                sonraki_asi_str = kayit[2].strftime("%Y-%m-%d") if kayit[2] else "Yok"
                tree.insert("", "end", values=(kayit[0], asi_tarihi_str, sonraki_asi_str, kayit[3]))
        else:
            # Başlık sola hizalandı
            ttk.Label(parent_frame, text="Bu hayvana ait aşı kaydı bulunmamaktadır.", background=COLORS["frame_bg"]).pack(pady=20, anchor="center")


    # Randevu Geçmişi Tabı için yardımcı fonksiyon
    def _randevu_gecmisi_tab_olustur(self, parent_frame, hayvan_id):
        tree = ttk.Treeview(parent_frame, columns=("Tarih", "Açıklama", "Durum"), show="headings")
        tree.pack(fill="both", expand=True, padx=5, pady=5)
        
        vsb = ttk.Scrollbar(tree, orient="vertical", command=tree.yview)
        vsb.pack(side="right", fill="y")
        tree.configure(yscrollcommand=vsb.set)

        tree.heading("Tarih", text="Tarih")
        tree.heading("Açıklama", text="Açıklama")
        tree.heading("Durum", text="Durum")

        tree.column("Tarih", width=150, anchor="center")
        tree.column("Açıklama", width=300, anchor="w")
        tree.column("Durum", width=100, anchor="center")

        randevu_kayitlar = self.db.sorgu_calistir(
            "SELECT randevu_tarihi, aciklama, durum FROM randevular WHERE hayvan_id = %s ORDER BY id ASC", # ID'ye göre sırala
            (hayvan_id,), fetch_results=True
        )
        if randevu_kayitlar:
            for kayit in randevu_kayitlar:
                randevu_tarihi_str = kayit[0].strftime("%Y-%m-%d %H:%M") if kayit[0] else ""
                tree.insert("", "end", values=(randevu_tarihi_str, kayit[1], kayit[2]))
        else:
            # Başlık sola hizalandı
            ttk.Label(parent_frame, text="Bu hayvana ait randevu kaydı bulunmamaktadır.", background=COLORS["frame_bg"]).pack(pady=20, anchor="center")

    # Muayene Geçmişi Tabı için yardımcı fonksiyon
    def _muayene_gecmisi_tab_olustur(self, parent_frame, hayvan_id):
        tree = ttk.Treeview(parent_frame, columns=("Tarih", "Şikayet", "Teşhis", "Tedavi Planı"), show="headings")
        tree.pack(fill="both", expand=True, padx=5, pady=5)

        vsb = ttk.Scrollbar(tree, orient="vertical", command=tree.yview)
        vsb.pack(side="right", fill="y")
        tree.configure(yscrollcommand=vsb.set)

        tree.heading("Tarih", text="Tarih")
        tree.heading("Şikayet", text="Şikayet")
        tree.heading("Teşhis", text="Teşhis")
        tree.heading("Tedavi Planı", text="Tedavi Planı")

        tree.column("Tarih", width=120, anchor="center")
        tree.column("Şikayet", width=150, anchor="w")
        tree.column("Teşhis", width=150, anchor="w")
        tree.column("Tedavi Planı", width=180, anchor="w")

        muayene_kayitlar = self.db.sorgu_calistir(
            "SELECT muayene_tarihi, sikayet, teshis, tedavi_plani FROM muayeneler WHERE hayvan_id = %s ORDER BY id ASC", # ID'ye göre sırala
            (hayvan_id,), fetch_results=True
        )
        if muayene_kayitlar:
            for kayit in muayene_kayitlar:
                muayene_tarihi_str = kayit[0].strftime("%Y-%m-%d %H:%M") if kayit[0] else ""
                tree.insert("", "end", values=(kayit[0], kayit[1], kayit[2], kayit[3]))
        else:
            # Başlık sola hizalandı
            ttk.Label(parent_frame, text="Bu hayvana ait muayene kaydı bulunmamaktadır.", background=COLORS["frame_bg"]).pack(pady=20, anchor="center")


    # --- Randevu Yönetimi ---
    def _randevu_ekle_penceresi(self):
        top = tk.Toplevel(self.root, bg=COLORS["background"])
        top.title("Randevu Ekle")
        top.grab_set()
        top.geometry("500x480")
        top.resizable(False, False)

        form_frame = ttk.LabelFrame(top, text="Yeni Randevu Bilgileri", padding="20", style="TLabelframe")
        form_frame.pack(padx=20, pady=20, fill="both", expand=True)

        hayvan_dict, _ = self._get_hayvanlar_ve_sahipler()

        ttk.Label(form_frame, text="Hayvan:").grid(row=0, column=0, padx=10, pady=8, sticky="w")
        hayvan_combo = ttk.Combobox(form_frame, width=30, values=list(hayvan_dict.keys()), state="readonly")
        if hayvan_dict:
            hayvan_combo.set(next(iter(hayvan_dict)))
        hayvan_combo.grid(row=0, column=1, padx=10, pady=8, sticky="ew")

        ttk.Label(form_frame, text="Randevu Tarihi (YYYY-AA-GG HH:MM):").grid(row=1, column=0, padx=10, pady=8, sticky="w")
        randevu_tarihi_entry = ttk.Entry(form_frame)
        randevu_tarihi_entry.insert(0, datetime.now().strftime("%Y-%m-%d %H:%M"))
        randevu_tarihi_entry.grid(row=1, column=1, padx=10, pady=8, sticky="ew")

        ttk.Label(form_frame, text="Açıklama:").grid(row=2, column=0, padx=10, pady=8, sticky="nw")
        aciklama_text = tk.Text(form_frame, height=5, width=40, font=("Segoe UI", 10))
        aciklama_text.grid(row=2, column=1, padx=10, pady=8, sticky="ew")
        
        ttk.Label(form_frame, text="Durum:").grid(row=3, column=0, padx=10, pady=8, sticky="w")
        durum_var = tk.StringVar(form_frame)
        durum_options = ["Planlandı", "Tamamlandı", "İptal Edildi", "Gelmedi"]
        durum_combo = ttk.Combobox(form_frame, textvariable=durum_var, values=durum_options, state="readonly")
        durum_combo.set("Planlandı")
        durum_combo.grid(row=3, column=1, padx=10, pady=8, sticky="ew")

        form_frame.columnconfigure(1, weight=1)

        def kaydet():
            secilen_hayvan = hayvan_combo.get().strip()
            randevu_tarihi_str = randevu_tarihi_entry.get().strip()
            aciklama = aciklama_text.get("1.0", "end-1c").strip()
            durum = durum_var.get()

            if not (secilen_hayvan and randevu_tarihi_str):
                messagebox.showerror("Hata", "Lütfen hayvan ve randevu tarihini doldurun.", icon="warning")
                return

            hayvan_id = hayvan_dict.get(secilen_hayvan)
            if not hayvan_id:
                messagebox.showerror("Hata", "Lütfen geçerli bir hayvan seçin.", icon="warning")
                return
            
            try:
                randevu_tarihi = datetime.strptime(randevu_tarihi_str, "%Y-%m-%d %H:%M")
            except ValueError:
                messagebox.showerror("Hata", "Randevu tarihi formatı yanlış. Lütfen YYYY-AA-GG HH:MM formatını kullanın.", icon="warning")
                return

            # Çakışma kontrolü
            collision_check_sql = "SELECT COUNT(*) FROM randevular WHERE randevu_tarihi = %s AND durum != 'İptal Edildi'"
            existing_appointments_data = self.db.sorgu_calistir(collision_check_sql, (randevu_tarihi,), fetch_results=True)
            
            if existing_appointments_data and existing_appointments_data[0][0] > 0:
                if not messagebox.askyesno("Randevu Çakışması", 
                                          f"Bu tarihte ({randevu_tarihi_str}) zaten bir randevu var. Yine de eklemek istiyor musunuz?", icon="question"):
                    return
            
            sql = "INSERT INTO randevular (hayvan_id, randevu_tarihi, aciklama, durum) VALUES (%s, %s, %s, %s)"
            veri = (hayvan_id, randevu_tarihi, aciklama if aciklama else None, durum)
            if self.db.sorgu_calistir(sql, veri, commit=True):
                messagebox.showinfo("Başarılı", "Randevu başarıyla eklendi.", icon="info")
                top.destroy()

        self._create_button_with_icon(top, "Kaydet", kaydet, "save").pack(pady=15, padx=20, fill="x")

    # --- Randevu Listeleme ve Takvim Görünümü ---
    def _randevulari_listele_penceresi(self):
        top = tk.Toplevel(self.root, bg=COLORS["background"])
        top.title("Randevular")
        top.grab_set()
        top.geometry("1000x600")

        # Başlık sola hizalandı
        ttk.Label(top, text="Randevu Kayıtları", font=("Segoe UI", 14, "bold"), 
                  background=COLORS["background"], foreground=COLORS["primary"]).pack(pady=10, anchor="w", padx=10)

        tree_frame = ttk.Frame(top, style="TFrame")
        tree_frame.pack(pady=10, padx=10, fill="both", expand=True)

        tree = ttk.Treeview(tree_frame, columns=("ID", "Hayvan", "Randevu Tarihi", "Açıklama", "Durum"), show="headings")
        tree.pack(side="left", fill="both", expand=True)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        vsb.pack(side="right", fill="y")
        tree.configure(yscrollcommand=vsb.set)

        tree.heading("ID", text="ID")
        tree.heading("Hayvan", text="Hayvan")
        tree.heading("Randevu Tarihi", text="Randevu Tarihi")
        tree.heading("Açıklama", text="Açıklama")
        tree.heading("Durum", text="Durum")

        tree.column("ID", width=40, anchor="center")
        tree.column("Hayvan", width=120, anchor="w")
        tree.column("Randevu Tarihi", width=150, anchor="center")
        tree.column("Açıklama", width=250, anchor="w")
        tree.column("Durum", width=100, anchor="center")

        def randevulari_yukle():
            for item in tree.get_children():
                tree.delete(item)
            # Sorguyu ID'ye göre sıralayacak şekilde güncellendi
            randevular = self.db.sorgu_calistir("""
                SELECT r.id, h.isim, r.randevu_tarihi, r.aciklama, r.durum
                FROM randevular r
                JOIN hayvanlar h ON r.hayvan_id = h.id
                ORDER BY r.id ASC 
            """, fetch_results=True)
            if randevular:
                for randevu in randevular:
                    randevu_tarihi_str = randevu[2].strftime("%Y-%m-%d %H:%M")
                    tree.insert("", "end", values=(randevu[0], randevu[1], randevu_tarihi_str, randevu[3], randevu[4]))
            else:
                messagebox.showinfo("Bilgi", "Kayıtlı randevu bulunamadı.", icon="info")

        def randevu_sil():
            secilen_item = tree.selection()
            if not secilen_item:
                messagebox.showwarning("Uyarı", "Lütfen silmek istediğiniz randevuyu seçin.", icon="warning")
                return

            randevu_id = tree.item(secilen_item, "values")[0]

            if messagebox.askyesno("Onay", f"ID {randevu_id} olan randevuyu silmek istediğinize emin misiniz?", icon="question"):
                sorgu = "DELETE FROM randevular WHERE id=%s"
                if self.db.sorgu_calistir(sorgu, (randevu_id,), commit=True):
                    messagebox.showinfo("Başarılı", "Randevu başarıyla silindi.", icon="info")
                    randevulari_yukle()

        def randevu_guncelle():
            secilen_item = tree.selection()
            if not secilen_item:
                messagebox.showwarning("Uyarı", "Lütfen güncellemek istediğiniz randevuyu seçin.", icon="warning")
                return
            
            randevu_id = tree.item(secilen_item, "values")[0]
            
            top_guncelle = tk.Toplevel(self.root, bg=COLORS["background"])
            top_guncelle.title("Randevu Güncelle")
            top_guncelle.grab_set()
            top_guncelle.geometry("500x480")
            top_guncelle.resizable(False, False)

            form_frame = ttk.LabelFrame(top_guncelle, text=f"Randevu Bilgilerini Güncelle (ID: {randevu_id})", padding="20", style="TLabelframe")
            form_frame.pack(padx=20, pady=20, fill="both", expand=True)

            randevu_data_list = self.db.sorgu_calistir("SELECT hayvan_id, randevu_tarihi, aciklama, durum FROM randevular WHERE id=%s", (randevu_id,), fetch_results=True)
            if not randevu_data_list:
                messagebox.showerror("Hata", "Randevu kaydı bulunamadı veya veritabanı hatası.", icon="error")
                top_guncelle.destroy()
                return
            randevu_data = randevu_data_list[0]
            
            hayvan_dict, _ = self._get_hayvanlar_ve_sahipler()
            ters_hayvan_dict = {v: k for k, v in hayvan_dict.items()} 

            ttk.Label(form_frame, text="Hayvan:").grid(row=0, column=0, padx=10, pady=8, sticky="w")
            hayvan_combo_guncelle = ttk.Combobox(form_frame, width=30, values=list(hayvan_dict.keys()), state="readonly")
            hayvan_combo_guncelle.set(ters_hayvan_dict.get(randevu_data[0], ""))
            hayvan_combo_guncelle.grid(row=0, column=1, padx=10, pady=8, sticky="ew")

            ttk.Label(form_frame, text="Randevu Tarihi (YYYY-AA-GG HH:MM):").grid(row=1, column=0, padx=10, pady=8, sticky="w")
            randevu_tarihi_entry_guncelle = ttk.Entry(form_frame)
            randevu_tarihi_entry_guncelle.insert(0, randevu_data[1].strftime("%Y-%m-%d %H:%M"))
            randevu_tarihi_entry_guncelle.grid(row=1, column=1, padx=10, pady=8, sticky="ew")

            ttk.Label(form_frame, text="Açıklama:").grid(row=2, column=0, padx=10, pady=8, sticky="nw")
            aciklama_text_guncelle = tk.Text(form_frame, height=5, width=40, font=("Segoe UI", 10))
            aciklama_text_guncelle.insert("1.0", randevu_data[2] if randevu_data[2] else "")
            aciklama_text_guncelle.grid(row=2, column=1, padx=10, pady=8, sticky="ew")

            ttk.Label(form_frame, text="Durum:").grid(row=3, column=0, padx=10, pady=8, sticky="w")
            durum_var_guncelle = tk.StringVar(form_frame)
            durum_options_guncelle = ["Planlandı", "Tamamlandı", "İptal Edildi", "Gelmedi"]
            durum_combo_guncelle = ttk.Combobox(form_frame, textvariable=durum_var_guncelle, values=durum_options_guncelle, state="readonly")
            durum_combo_guncelle.set(randevu_data[3])
            durum_combo_guncelle.grid(row=3, column=1, padx=10, pady=8, sticky="ew")

            form_frame.columnconfigure(1, weight=1)

            def guncelle_kaydet():
                yeni_secilen_hayvan = hayvan_combo_guncelle.get().strip()
                yeni_randevu_tarihi_str = randevu_tarihi_entry_guncelle.get().strip()
                yeni_aciklama = aciklama_text_guncelle.get("1.0", "end-1c").strip()
                yeni_durum = durum_var_guncelle.get()

                if not (yeni_secilen_hayvan and yeni_randevu_tarihi_str):
                    messagebox.showerror("Hata", "Lütfen hayvan ve randevu tarihini doldurun.", icon="warning")
                    return
                
                yeni_hayvan_id = hayvan_dict.get(yeni_secilen_hayvan)
                if not yeni_hayvan_id:
                    messagebox.showerror("Hata", "Lütfen geçerli bir hayvan seçin.", icon="warning")
                    return

                try:
                    yeni_randevu_tarihi = datetime.strptime(yeni_randevu_tarihi_str, "%Y-%m-%d %H:%M")
                except ValueError:
                    messagebox.showerror("Hata", "Randevu tarihi formatı yanlış. Lütfen YYYY-AA-GG HH:MM formatını kullanın.", icon="warning")
                    return

                # Çakışma kontrolü
                collision_check_sql = "SELECT COUNT(*) FROM randevular WHERE randevu_tarihi = %s AND id != %s AND durum != 'İptal Edildi'"
                existing_appointments_data = self.db.sorgu_calistir(collision_check_sql, (yeni_randevu_tarihi, randevu_id), fetch_results=True)
                
                if existing_appointments_data and existing_appointments_data[0][0] > 0:
                    if not messagebox.askyesno("Randevu Çakışması", 
                                              f"Bu tarihte ({yeni_randevu_tarihi_str}) zaten başka bir randevu var. Yine de güncellemek istiyor musunuz?", icon="question"):
                        return

                sql = """
                    UPDATE randevular SET hayvan_id=%s, randevu_tarihi=%s, aciklama=%s, durum=%s WHERE id=%s
                """
                veri = (yeni_hayvan_id, yeni_randevu_tarihi, yeni_aciklama if yeni_aciklama else None, yeni_durum, randevu_id)
                if self.db.sorgu_calistir(sql, veri, commit=True):
                    messagebox.showinfo("Başarılı", "Randevu başarıyla güncellendi.", icon="info")
                    top_guncelle.destroy()
                    randevulari_yukle()

            self._create_button_with_icon(top_guncelle, "Güncelle", guncelle_kaydet, "update").pack(pady=15, padx=20, fill="x")

        randevulari_yukle()

        button_frame = ttk.Frame(top, style="TFrame")
        button_frame.pack(pady=10)

        self._create_button_with_icon(button_frame, "Randevu Ekle", self._randevu_ekle_penceresi, "add").pack(side="left", padx=7)
        self._create_button_with_icon(button_frame, "Randevu Sil", randevu_sil, "delete").pack(side="left", padx=7)
        self._create_button_with_icon(button_frame, "Randevu Güncelle", randevu_guncelle, "update").pack(side="left", padx=7)
        self._create_button_with_icon(button_frame, "Listeyi Yenile", randevulari_yukle, "refresh").pack(side="left", padx=7)

    # --- Muayene ve Tedavi Kayıtları ---
    def _muayene_ekle_penceresi(self):
        top = tk.Toplevel(self.root, bg=COLORS["background"])
        top.title("Muayene Kaydı Ekle")
        top.grab_set()
        top.geometry("550x650")
        top.resizable(False, False)

        form_frame = ttk.LabelFrame(top, text="Yeni Muayene Kaydı", padding="20", style="TLabelframe")
        form_frame.pack(padx=20, pady=20, fill="both", expand=True)

        hayvan_dict, _ = self._get_hayvanlar_ve_sahipler()

        ttk.Label(form_frame, text="Hayvan:").grid(row=0, column=0, padx=10, pady=8, sticky="w")
        hayvan_combo = ttk.Combobox(form_frame, width=30, values=list(hayvan_dict.keys()), state="readonly")
        if hayvan_dict:
            hayvan_combo.set(next(iter(hayvan_dict)))
        hayvan_combo.grid(row=0, column=1, padx=10, pady=8, sticky="ew")

        ttk.Label(form_frame, text="Muayene Tarihi (YYYY-AA-GG HH:MM):").grid(row=1, column=0, padx=10, pady=8, sticky="w")
        muayene_tarihi_entry = ttk.Entry(form_frame)
        muayene_tarihi_entry.insert(0, datetime.now().strftime("%Y-%m-%d %H:%M"))
        muayene_tarihi_entry.grid(row=1, column=1, padx=10, pady=8, sticky="ew")

        ttk.Label(form_frame, text="Şikayet:").grid(row=2, column=0, padx=10, pady=8, sticky="nw")
        sikayet_text = tk.Text(form_frame, height=4, width=40, font=("Segoe UI", 10))
        sikayet_text.grid(row=2, column=1, padx=10, pady=8, sticky="ew")

        ttk.Label(form_frame, text="Bulgular:").grid(row=3, column=0, padx=10, pady=8, sticky="nw")
        bulgular_text = tk.Text(form_frame, height=4, width=40, font=("Segoe UI", 10))
        bulgular_text.grid(row=3, column=1, padx=10, pady=8, sticky="ew")

        ttk.Label(form_frame, text="Teşhis:").grid(row=4, column=0, padx=10, pady=8, sticky="nw")
        teshis_text = tk.Text(form_frame, height=4, width=40, font=("Segoe UI", 10))
        teshis_text.grid(row=4, column=1, padx=10, pady=8, sticky="ew")

        ttk.Label(form_frame, text="Tedavi Planı:").grid(row=5, column=0, padx=10, pady=8, sticky="nw")
        tedavi_text = tk.Text(form_frame, height=4, width=40, font=("Segoe UI", 10))
        tedavi_text.grid(row=5, column=1, padx=10, pady=8, sticky="ew")

        form_frame.columnconfigure(1, weight=1)

        def kaydet():
            secilen_hayvan = hayvan_combo.get().strip()
            muayene_tarihi_str = muayene_tarihi_entry.get().strip()
            sikayet = sikayet_text.get("1.0", "end-1c").strip()
            bulgular = bulgular_text.get("1.0", "end-1c").strip()
            teshis = teshis_text.get("1.0", "end-1c").strip()
            tedavi_plani = tedavi_text.get("1.0", "end-1c").strip()

            if not (secilen_hayvan and muayene_tarihi_str):
                messagebox.showerror("Hata", "Lütfen hayvan ve muayene tarihini doldurun.", icon="warning")
                return

            hayvan_id = hayvan_dict.get(secilen_hayvan)
            if not hayvan_id:
                messagebox.showerror("Hata", "Lütfen geçerli bir hayvan seçin.", icon="warning")
                return
            
            try:
                muayene_tarihi = datetime.strptime(muayene_tarihi_str, "%Y-%m-%d %H:%M")
            except ValueError:
                messagebox.showerror("Hata", "Muayene tarihi formatı yanlış. Lütfen YYYY-AA-GG HH:MM formatını kullanın.", icon="warning")
                return

            sql = """
                INSERT INTO muayeneler (hayvan_id, muayene_tarihi, sikayet, bulgular, teshis, tedavi_plani)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            veri = (hayvan_id, muayene_tarihi, sikayet if sikayet else None, bulgular if bulgular else None, teshis if teshis else None, tedavi_plani if tedavi_plani else None)
            if self.db.sorgu_calistir(sql, veri, commit=True):
                messagebox.showinfo("Başarılı", "Muayene kaydı eklendi.", icon="info")
                top.destroy()

        self._create_button_with_icon(top, "Kaydet", kaydet, "save").pack(pady=15, padx=20, fill="x")

    def _muayene_listele_penceresi(self):
        top = tk.Toplevel(self.root, bg=COLORS["background"])
        top.title("Muayene ve Tedavi Kayıtları")
        top.grab_set()
        top.geometry("1100x600")

        # Başlık sola hizalandı
        ttk.Label(top, text="Muayene ve Tedavi Kayıtları", font=("Segoe UI", 14, "bold"), 
                  background=COLORS["background"], foreground=COLORS["primary"]).pack(pady=10, anchor="w", padx=10)

        tree_frame = ttk.Frame(top, style="TFrame")
        tree_frame.pack(pady=10, padx=10, fill="both", expand=True)

        tree = ttk.Treeview(tree_frame, columns=("ID", "Hayvan", "Tarih", "Şikayet", "Bulgular", "Teşhis", "Tedavi Planı"), show="headings")
        tree.pack(side="left", fill="both", expand=True)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        vsb.pack(side="right", fill="y")
        tree.configure(yscrollcommand=vsb.set)

        tree.heading("ID", text="ID")
        tree.heading("Hayvan", text="Hayvan")
        tree.heading("Tarih", text="Tarih")
        tree.heading("Şikayet", text="Şikayet")
        tree.heading("Bulgular", text="Bulgular")
        tree.heading("Teşhis", text="Teşhis")
        tree.heading("Tedavi Planı", text="Tedavi Planı")

        tree.column("ID", width=40, anchor="center")
        tree.column("Hayvan", width=100, anchor="w")
        tree.column("Tarih", width=120, anchor="center")
        tree.column("Şikayet", width=150, anchor="w")
        tree.column("Bulgular", width=150, anchor="w")
        tree.column("Teşhis", width=150, anchor="w")
        tree.column("Tedavi Planı", width=180, anchor="w")

        def muayeneleri_yukle():
            for item in tree.get_children():
                tree.delete(item)
            # Sorguyu ID'ye göre sıralayacak şekilde güncellendi
            kayitlar = self.db.sorgu_calistir("""
                SELECT m.id, h.isim, m.muayene_tarihi, m.sikayet, m.bulgular, m.teshis, m.tedavi_plani
                FROM muayeneler m
                JOIN hayvanlar h ON m.hayvan_id = h.id
                ORDER BY m.id ASC
            """, fetch_results=True)
            if kayitlar:
                for kayit in kayitlar:
                    muayene_tarihi_str = kayit[2].strftime("%Y-%m-%d %H:%M") if kayit[2] else ""
                    tree.insert("", "end", values=(kayit[0], kayit[1], muayene_tarihi_str, kayit[3], kayit[4], kayit[5], kayit[6]))
            else:
                messagebox.showinfo("Bilgi", "Kayıtlı muayene bulunamadı.", icon="info")

        def muayene_sil():
            secilen_item = tree.selection()
            if not secilen_item:
                messagebox.showwarning("Uyarı", "Lütfen silmek istediğiniz kaydı seçin.", icon="warning")
                return

            kayit_id = tree.item(secilen_item, "values")[0]

            if messagebox.askyesno("Onay", f"ID {kayit_id} olan muayene kaydını silmek istediğinize emin misiniz?", icon="question"):
                sorgu = "DELETE FROM muayeneler WHERE id=%s"
                if self.db.sorgu_calistir(sorgu, (kayit_id,), commit=True):
                    messagebox.showinfo("Silindi", "Muayene kaydı başarıyla silindi.", icon="info")
                    muayeneleri_yukle()

        def muayene_guncelle():
            secilen_item = tree.selection()
            if not secilen_item:
                messagebox.showwarning("Uyarı", "Lütfen güncellemek istediğiniz muayene kaydını seçin.", icon="warning")
                return
            kayit_id = tree.item(secilen_item, "values")[0]
            
            top_guncelle = tk.Toplevel(self.root, bg=COLORS["background"])
            top_guncelle.title("Muayene Kaydı Güncelle")
            top_guncelle.grab_set()
            top_guncelle.geometry("550x650")
            top_guncelle.resizable(False, False)

            form_frame = ttk.LabelFrame(top_guncelle, text=f"Muayene Kaydını Güncelle (ID: {kayit_id})", padding="20", style="TLabelframe")
            form_frame.pack(padx=20, pady=20, fill="both", expand=True)

            muayene_data_list = self.db.sorgu_calistir(
                "SELECT hayvan_id, muayene_tarihi, sikayet, bulgular, teshis, tedavi_plani FROM muayeneler WHERE id=%s", (kayit_id,), fetch_results=True)
            if not muayene_data_list:
                messagebox.showerror("Hata", "Muayene kaydı bulunamadı veya veritabanı hatası.", icon="error")
                top_guncelle.destroy()
                return
            muayene_data = muayene_data_list[0]
            
            hayvan_dict, _ = self._get_hayvanlar_ve_sahipler()
            ters_hayvan_dict = {v: k for k, v in hayvan_dict.items()}

            ttk.Label(form_frame, text="Hayvan:").grid(row=0, column=0, padx=10, pady=8, sticky="w")
            hayvan_combo_guncelle = ttk.Combobox(form_frame, width=30, values=list(hayvan_dict.keys()), state="readonly")
            hayvan_combo_guncelle.set(ters_hayvan_dict.get(muayene_data[0], ""))
            hayvan_combo_guncelle.grid(row=0, column=1, padx=10, pady=8, sticky="ew")

            ttk.Label(form_frame, text="Muayene Tarihi (YYYY-AA-GG HH:MM):").grid(row=1, column=0, padx=10, pady=8, sticky="w")
            muayene_tarihi_entry_guncelle = ttk.Entry(form_frame)
            muayene_tarihi_entry_guncelle.insert(0, muayene_data[1].strftime("%Y-%m-%d %H:%M"))
            muayene_tarihi_entry_guncelle.grid(row=1, column=1, padx=10, pady=8, sticky="ew")

            ttk.Label(form_frame, text="Şikayet:").grid(row=2, column=0, padx=10, pady=8, sticky="nw")
            sikayet_text_guncelle = tk.Text(form_frame, height=4, width=40, font=("Segoe UI", 10))
            sikayet_text_guncelle.insert("1.0", muayene_data[2] if muayene_data[2] else "")
            sikayet_text_guncelle.grid(row=2, column=1, padx=10, pady=8, sticky="ew")

            ttk.Label(form_frame, text="Bulgular:").grid(row=3, column=0, padx=10, pady=8, sticky="nw")
            bulgular_text_guncelle = tk.Text(form_frame, height=4, width=40, font=("Segoe UI", 10))
            bulgular_text_guncelle.insert("1.0", muayene_data[3] if muayene_data[3] else "")
            bulgular_text_guncelle.grid(row=3, column=1, padx=10, pady=8, sticky="ew")

            ttk.Label(form_frame, text="Teşhis:").grid(row=4, column=0, padx=10, pady=8, sticky="nw")
            teshis_text_guncelle = tk.Text(form_frame, height=4, width=40, font=("Segoe UI", 10))
            teshis_text_guncelle.insert("1.0", muayene_data[4] if muayene_data[4] else "")
            teshis_text_guncelle.grid(row=4, column=1, padx=10, pady=8, sticky="ew")

            ttk.Label(form_frame, text="Tedavi Planı:").grid(row=5, column=0, padx=10, pady=8, sticky="nw")
            tedavi_text_guncelle = tk.Text(form_frame, height=4, width=40, font=("Segoe UI", 10))
            tedavi_text_guncelle.insert("1.0", muayene_data[5] if muayene_data[5] else "")
            tedavi_text_guncelle.grid(row=5, column=1, padx=10, pady=8, sticky="ew")

            form_frame.columnconfigure(1, weight=1)

            def guncelle_kaydet():
                yeni_secilen_hayvan = hayvan_combo_guncelle.get().strip()
                yeni_muayene_tarihi_str = muayene_tarihi_entry_guncelle.get().strip()
                yeni_sikayet = sikayet_text_guncelle.get("1.0", "end-1c").strip()
                yeni_bulgular = bulgular_text_guncelle.get("1.0", "end-1c").strip()
                yeni_teshis = teshis_text_guncelle.get("1.0", "end-1c").strip()
                yeni_tedavi_plani = tedavi_text_guncelle.get("1.0", "end-1c").strip()

                if not (yeni_secilen_hayvan and yeni_muayene_tarihi_str):
                    messagebox.showerror("Hata", "Lütfen hayvan ve muayene tarihini doldurun.", icon="warning")
                    return
                
                yeni_hayvan_id = hayvan_dict.get(yeni_secilen_hayvan)
                if not yeni_hayvan_id:
                    messagebox.showerror("Hata", "Lütfen geçerli bir hayvan seçin.", icon="warning")
                    return

                try:
                    yeni_muayene_tarihi = datetime.strptime(yeni_muayene_tarihi_str, "%Y-%m-%d %H:%M")
                except ValueError:
                    messagebox.showerror("Hata", "Muayene tarihi formatı yanlış. Lütfen YYYY-AA-GG HH:MM formatını kullanın.", icon="warning")
                    return

                sql = """
                    UPDATE muayeneler SET hayvan_id=%s, muayene_tarihi=%s, sikayet=%s, bulgular=%s, teshis=%s, tedavi_plani=%s WHERE id=%s
                """
                veri = (yeni_hayvan_id, yeni_muayene_tarihi, yeni_sikayet if yeni_sikayet else None, yeni_bulgular if yeni_bulgular else None, yeni_teshis if yeni_teshis else None, yeni_tedavi_plani if yeni_tedavi_plani else None, kayit_id)
                if self.db.sorgu_calistir(sql, veri, commit=True):
                    messagebox.showinfo("Başarılı", "Muayene kaydı başarıyla güncellendi.", icon="info")
                    top_guncelle.destroy()
                    muayeneleri_yukle()

            self._create_button_with_icon(top_guncelle, "Güncelle", guncelle_kaydet, "update").pack(pady=15, padx=20, fill="x")

        muayeneleri_yukle()

        button_frame = ttk.Frame(top, style="TFrame")
        button_frame.pack(pady=10)

        self._create_button_with_icon(button_frame, "Muayene Ekle", self._muayene_ekle_penceresi, "add").pack(side="left", padx=7)
        self._create_button_with_icon(button_frame, "Muayene Sil", muayene_sil, "delete").pack(side="left", padx=7)
        self._create_button_with_icon(button_frame, "Muayene Güncelle", muayene_guncelle, "update").pack(side="left", padx=7)
        self._create_button_with_icon(button_frame, "Listeyi Yenile", muayeneleri_yukle, "refresh").pack(side="left", padx=7)


# --- Ana Program Başlatma ---
if __name__ == "__main__":
    root = tk.Tk()
    app = VeterinerUygulamasi(root)
    root.mainloop()