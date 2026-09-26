"""
vardiya_modeli.py
-------------------
Vardiya çizelgeleme problemini İkili (Binary) Tam Sayılı Programlama olarak
kurar ve scipy.optimize.milp (HiGHS çözücüsü, harici kurulum gerektirmez)
ile çözer.

Karar Değişkeni
---------------
x[e, d, s] ∈ {0, 1} : e çalışanı, d gününde, s vardiyasında çalışıyorsa 1

Amaç Fonksiyonu
----------------
minimize  Σ maliyet[s] * x[e,d,s]     (toplam işçilik maliyetini minimize et)

Kısıtlar
--------
1) Talep karşılama   : Σ_e x[e,d,s] ≥ talep[d,s]              (her gün-vardiya için)
2) Günde tek vardiya  : Σ_s x[e,d,s] ≤ 1                       (her çalışan-gün için)
3) Haftalık tavan     : Σ_d,s x[e,d,s] ≤ MAKS_HAFTALIK_VARDIYA (her çalışan için)
4) Haftalık taban     : Σ_d,s x[e,d,s] ≥ MIN_HAFTALIK_VARDIYA  (her çalışan için)
5) Minimum dinlenme   : x[e,d,s1] + x[e,d+1,s2] ≤ 1            (yasaklı ardışık çiftler için)
"""

import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds

from veri import (
    GUNLER, VARDIYALAR, VARDIYA_MALIYETI, TALEP, CALISANLAR,
    MIN_HAFTALIK_VARDIYA, MAKS_HAFTALIK_VARDIYA, YASAKLI_ARDISIK_CIFTLER,
)


def _degisken_indeksi(e, d, s, n_gun, n_vardiya):
    """(çalışan, gün, vardiya) üçlüsünü tek boyutlu değişken indeksine çevirir."""
    return e * (n_gun * n_vardiya) + d * n_vardiya + s


def modeli_kur_ve_coz():
    """
    Vardiya çizelgeleme MILP modelini kurar, çözer ve sonucu okunabilir bir
    çizelgeye dönüştürür.

    Dönüş
    ------
    (cizelge, toplam_maliyet, basarili_mi)
      cizelge: {calisan: {gun: vardiya_ya_da_None}}
    """
    n_calisan = len(CALISANLAR)
    n_gun = len(GUNLER)
    n_vardiya = len(VARDIYALAR)
    n_degisken = n_calisan * n_gun * n_vardiya

    vardiya_idx = {v: i for i, v in enumerate(VARDIYALAR)}

    # --- Amaç fonksiyonu katsayıları (maliyet) ---
    c = np.zeros(n_degisken)
    for e in range(n_calisan):
        for d in range(n_gun):
            for s, vardiya_adi in enumerate(VARDIYALAR):
                c[_degisken_indeksi(e, d, s, n_gun, n_vardiya)] = VARDIYA_MALIYETI[vardiya_adi]

    kisit_satirlari = []   # her biri n_degisken uzunluğunda katsayı listesi
    alt_sinirlar = []
    ust_sinirlar = []

    def kisit_ekle(katsayilar_sozlugu, alt, ust):
        satir = np.zeros(n_degisken)
        for idx, katsayi in katsayilar_sozlugu.items():
            satir[idx] = katsayi
        kisit_satirlari.append(satir)
        alt_sinirlar.append(alt)
        ust_sinirlar.append(ust)

    # --- 1) Talep karşılama: her gün-vardiya için en az istenen kişi sayısı ---
    for d in range(n_gun):
        for s, vardiya_adi in enumerate(VARDIYALAR):
            katsayilar = {
                _degisken_indeksi(e, d, s, n_gun, n_vardiya): 1 for e in range(n_calisan)
            }
            kisit_ekle(katsayilar, TALEP[d][vardiya_adi], np.inf)

    # --- 2) Bir çalışan günde en fazla bir vardiyada çalışabilir ---
    for e in range(n_calisan):
        for d in range(n_gun):
            katsayilar = {
                _degisken_indeksi(e, d, s, n_gun, n_vardiya): 1 for s in range(n_vardiya)
            }
            kisit_ekle(katsayilar, 0, 1)

    # --- 3) & 4) Haftalık minimum / maksimum vardiya sayısı ---
    for e in range(n_calisan):
        katsayilar = {
            _degisken_indeksi(e, d, s, n_gun, n_vardiya): 1
            for d in range(n_gun) for s in range(n_vardiya)
        }
        kisit_ekle(katsayilar, MIN_HAFTALIK_VARDIYA, MAKS_HAFTALIK_VARDIYA)

    # --- 5) Minimum dinlenme süresi: yasaklı ardışık gün-vardiya çiftleri ---
    for e in range(n_calisan):
        for d in range(n_gun - 1):  # yalnızca hafta içi ardışık günler (Pazar->Pzt döngüsü hariç)
            for vardiya1, vardiya2 in YASAKLI_ARDISIK_CIFTLER:
                idx1 = _degisken_indeksi(e, d, vardiya_idx[vardiya1], n_gun, n_vardiya)
                idx2 = _degisken_indeksi(e, d + 1, vardiya_idx[vardiya2], n_gun, n_vardiya)
                kisit_ekle({idx1: 1, idx2: 1}, 0, 1)

    A = np.vstack(kisit_satirlari)
    kisitlar = LinearConstraint(A, alt_sinirlar, ust_sinirlar)
    sinirlar = Bounds(0, 1)
    tam_sayililik = np.ones(n_degisken)  # tüm değişkenler ikili (0/1)

    sonuc = milp(c, constraints=kisitlar, integrality=tam_sayililik, bounds=sinirlar)

    if not sonuc.success:
        return None, None, False

    x = np.round(sonuc.x).astype(int)

    cizelge = {calisan: {gun: None for gun in GUNLER} for calisan in CALISANLAR}
    for e, calisan in enumerate(CALISANLAR):
        for d, gun in enumerate(GUNLER):
            for s, vardiya_adi in enumerate(VARDIYALAR):
                if x[_degisken_indeksi(e, d, s, n_gun, n_vardiya)] == 1:
                    cizelge[calisan][gun] = vardiya_adi

    toplam_maliyet = sonuc.fun
    return cizelge, toplam_maliyet, True


def kapsama_tablosu_hesapla(cizelge):
    """Çizelgeden, her gün-vardiya için fiilen atanan çalışan sayısını hesaplar."""
    kapsama = {gun: {vardiya: 0 for vardiya in VARDIYALAR} for gun in GUNLER}
    for calisan, gunler in cizelge.items():
        for gun, vardiya in gunler.items():
            if vardiya is not None:
                kapsama[gun][vardiya] += 1
    return kapsama


if __name__ == "__main__":
    cizelge, maliyet, basarili = modeli_kur_ve_coz()
    if not basarili:
        print("Model çözülemedi (infeasible). Kısıtları veya çalışan sayısını gözden geçirin.")
    else:
        print(f"Optimum toplam haftalık maliyet: {maliyet:,.0f} TL\n")
        for calisan, gunler in cizelge.items():
            print(f"{calisan:<14}: " + " | ".join(
                f"{gun[:3]}:{(gunler[gun] or '-'):<5}" for gun in GUNLER
            ))
