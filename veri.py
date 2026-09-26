"""
veri.py
--------
Örnek işletme: 7/24 açık bir mağaza/restoran için haftalık vardiya
çizelgeleme problemi verileri.

3 vardiya x 7 gün için, güne göre değişen personel talebi tanımlanır.
Gece vardiyası, gece çalışma zammı nedeniyle daha maliyetlidir.
"""

GUNLER = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
VARDIYALAR = ["Sabah", "Akşam", "Gece"]  # Sabah: 08-16, Akşam: 16-24, Gece: 00-08

# "Cuma" ve "Cumartesi" ilk 3 harfte çakıştığı (ikisi de "Cum") için tablo/grafik
# başlıklarında kullanılacak benzersiz kısa günler ayrıca tanımlanır.
GUN_KISA = {"Pazartesi": "Pzt", "Salı": "Sal", "Çarşamba": "Çar", "Perşembe": "Per",
            "Cuma": "Cum", "Cumartesi": "Cts", "Pazar": "Paz"}

# Vardiya başına saatlik/vardiya maliyeti (TL) — gece vardiyasında %50 zam
VARDIYA_MALIYETI = {"Sabah": 800, "Akşam": 880, "Gece": 1200}

# Personel talebi: TALEP[gün_indeksi][vardiya] = gereken çalışan sayısı
# (Hafta sonu talebi daha yüksek — tipik perakende/restoran deseni)
TALEP = {
    0: {"Sabah": 2, "Akşam": 2, "Gece": 1},   # Pazartesi
    1: {"Sabah": 2, "Akşam": 2, "Gece": 1},   # Salı
    2: {"Sabah": 2, "Akşam": 2, "Gece": 1},   # Çarşamba
    3: {"Sabah": 2, "Akşam": 3, "Gece": 1},   # Perşembe
    4: {"Sabah": 3, "Akşam": 3, "Gece": 2},   # Cuma
    5: {"Sabah": 3, "Akşam": 4, "Gece": 2},   # Cumartesi
    6: {"Sabah": 2, "Akşam": 3, "Gece": 1},   # Pazar
}

CALISAN_SAYISI = 10
CALISANLAR = [f"Personel_{i+1}" for i in range(CALISAN_SAYISI)]

# İş Kanunu / işletme politikası kısıtları
MIN_HAFTALIK_VARDIYA = 3   # her çalışana en az garanti edilen vardiya sayısı
MAKS_HAFTALIK_VARDIYA = 6  # haftada en az 1 gün izin zorunluluğu (6 vardiya x 8 saat = 48 saat tavan)

# Vardiyalar arası minimum dinlenme süresi 11 saattir (4857 sayılı İş Kanunu Md. 69).
# Bu nedenle bazı ardışık gün/vardiya kombinasyonları YASAKTIR:
#   Akşam (16-24) biter 24:00  -> ertesi gün Sabah (08:00 başlar) = 8 saat dinlenme (YETERSİZ)
#   Akşam (16-24) biter 24:00  -> ertesi gün Gece (00:00 başlar) = 0 saat dinlenme (YETERSİZ)
#   Sabah (08-16) biter 16:00  -> ertesi gün Gece (00:00 başlar) = 8 saat dinlenme (YETERSİZ)
YASAKLI_ARDISIK_CIFTLER = [
    ("Akşam", "Sabah"),
    ("Akşam", "Gece"),
    ("Sabah", "Gece"),
]
