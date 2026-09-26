"""
ana_program.py
----------------
Vardiya çizelgeleme MILP modelini çözer, sonuçları konsola yazdırır ve üç
görseli üretir.

Kullanım:
    python ana_program.py
"""

from veri import GUNLER, VARDIYALAR, TALEP, CALISANLAR, GUN_KISA
from vardiya_modeli import modeli_kur_ve_coz, kapsama_tablosu_hesapla
from gorsellestirme import tum_gorselleri_uret


def cizelge_yazdir(cizelge):
    print("=" * 100)
    print("OPTİMUM HAFTALIK ÇALIŞAN ÇİZELGESİ")
    print("=" * 100)
    baslik = f"{'Çalışan':<14}" + "".join(f"{GUN_KISA[g]:>9}" for g in GUNLER) + f"{'Toplam':>9}"
    print(baslik)
    for calisan in CALISANLAR:
        satir = f"{calisan:<14}"
        toplam = 0
        for gun in GUNLER:
            vardiya = cizelge[calisan][gun]
            satir += f"{(vardiya or '-'):>9}"
            if vardiya:
                toplam += 1
        satir += f"{toplam:>9}"
        print(satir)


def kapsama_yazdir(kapsama):
    print("\n" + "=" * 100)
    print("GÜN-VARDİYA BAZINDA TALEP KARŞILAMA")
    print("=" * 100)
    for d, gun in enumerate(GUNLER):
        satir = f"{gun:<12}"
        for vardiya in VARDIYALAR:
            satir += f"  {vardiya}: {kapsama[gun][vardiya]}/{TALEP[d][vardiya]}"
        print(satir)


if __name__ == "__main__":
    cizelge, maliyet, basarili = modeli_kur_ve_coz()

    if not basarili:
        print("⚠ Model çözülemedi (infeasible). Çalışan sayısını artırın veya kısıtları gevşetin.")
    else:
        cizelge_yazdir(cizelge)
        kapsama = kapsama_tablosu_hesapla(cizelge)
        kapsama_yazdir(kapsama)

        print(f"\nOPTİMUM TOPLAM HAFTALIK İŞÇİLİK MALİYETİ: {maliyet:,.0f} TL")

        print("\nGörseller üretiliyor...")
        tum_gorselleri_uret(cizelge, TALEP, kapsama, cikti_klasoru=".")
        print("Tamamlandı. Proje kök dizinine kaydedildi (README.md ile aynı yer):")
        print("  - talep_kapsama.png")
        print("  - calisan_cizelgesi.png")
        print("  - maliyet_dagilimi.png")
