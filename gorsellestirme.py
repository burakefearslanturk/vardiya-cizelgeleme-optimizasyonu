"""
gorsellestirme.py
-------------------
Üç görsel üretir:

  1) talep_kapsama.png     — Gün-vardiya bazında istenen vs atanan personel sayısı
  2) calisan_cizelgesi.png — Çalışan x Gün ısı haritası (hangi çalışan hangi gün
                               hangi vardiyada), renk = vardiya türü
  3) maliyet_dagilimi.png  — Toplam maliyetin vardiya türüne ve güne göre dağılımı
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import ListedColormap

from veri import GUNLER, VARDIYALAR, VARDIYA_MALIYETI, CALISANLAR, GUN_KISA

_VARDIYA_RENK = {"Sabah": "#f1c40f", "Akşam": "#e67e22", "Gece": "#2c3e50", None: "#ecf0f1"}


# ---------------------------------------------------------------------------
# 1) TALEP vs KAPSAMA
# ---------------------------------------------------------------------------
def talep_kapsama_ciz(talep, kapsama, cikti_yolu="talep_kapsama.png"):
    n_gun = len(GUNLER)
    x = np.arange(n_gun)
    genislik = 0.13

    fig, ax = plt.subplots(figsize=(13, 6))
    for i, vardiya in enumerate(VARDIYALAR):
        istenen = [talep[d][vardiya] for d in range(n_gun)]
        atanan = [kapsama[GUNLER[d]][vardiya] for d in range(n_gun)]

        ofset = (i - 1) * (genislik * 2.3)
        ax.bar(x + ofset - genislik / 2, istenen, genislik, label=f"{vardiya} (Talep)",
                color=_VARDIYA_RENK[vardiya], alpha=0.45, edgecolor="black", linewidth=0.6)
        ax.bar(x + ofset + genislik / 2, atanan, genislik, label=f"{vardiya} (Atanan)",
                color=_VARDIYA_RENK[vardiya], alpha=0.95, edgecolor="black", linewidth=0.6)

    ax.set_xticks(x)
    ax.set_xticklabels(GUNLER, rotation=20)
    ax.set_ylabel("Personel Sayısı")
    # (GUNLER tam adlarla gösterilir; kısaltma çakışması yalnızca ısı haritasında söz konusu)
    ax.set_title("Vardiya Bazında Talep ile Optimum Çizelgenin Karşılaştırılması\n"
                  "(soluk = talep edilen, koyu = fiilen atanan)", fontsize=12, fontweight="bold")
    ax.legend(ncol=3, fontsize=8.5, loc="upper left")
    ax.grid(axis="y", alpha=0.3)

    if os.path.dirname(cikti_yolu):
        os.makedirs(os.path.dirname(cikti_yolu), exist_ok=True)
    plt.tight_layout()
    plt.savefig(cikti_yolu, dpi=150)
    plt.close()


# ---------------------------------------------------------------------------
# 2) ÇALIŞAN ÇİZELGESİ (ısı haritası / grid görünümü)
# ---------------------------------------------------------------------------
def calisan_cizelgesi_ciz(cizelge, cikti_yolu="calisan_cizelgesi.png"):
    vardiya_kodu = {None: 0, "Sabah": 1, "Akşam": 2, "Gece": 3}
    renk_listesi = [_VARDIYA_RENK[None], _VARDIYA_RENK["Sabah"], _VARDIYA_RENK["Akşam"], _VARDIYA_RENK["Gece"]]
    cmap = ListedColormap(renk_listesi)

    matris = np.array([
        [vardiya_kodu[cizelge[calisan][gun]] for gun in GUNLER]
        for calisan in CALISANLAR
    ])

    fig, ax = plt.subplots(figsize=(10, 0.55 * len(CALISANLAR) + 1.5))
    ax.imshow(matris, cmap=cmap, vmin=0, vmax=3, aspect="auto")

    for i, calisan in enumerate(CALISANLAR):
        for j, gun in enumerate(GUNLER):
            vardiya = cizelge[calisan][gun]
            if vardiya is not None:
                metin_rengi = "white" if vardiya == "Gece" else "black"
                ax.text(j, i, vardiya[:3], ha="center", va="center",
                         fontsize=8, color=metin_rengi, fontweight="bold")

    ax.set_xticks(range(len(GUNLER)))
    ax.set_xticklabels([GUN_KISA[g] for g in GUNLER])
    ax.set_yticks(range(len(CALISANLAR)))
    ax.set_yticklabels(CALISANLAR, fontsize=9)
    ax.set_title("Optimum Haftalık Çalışan Çizelgesi", fontsize=12, fontweight="bold")

    for kenar in ["top", "right", "left", "bottom"]:
        ax.spines[kenar].set_visible(False)
    ax.set_xticks(np.arange(-0.5, len(GUNLER), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(CALISANLAR), 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=2)
    ax.tick_params(which="minor", size=0)

    etiketler = [mpatches.Patch(color=_VARDIYA_RENK["Sabah"], label="Sabah (08-16)"),
                 mpatches.Patch(color=_VARDIYA_RENK["Akşam"], label="Akşam (16-24)"),
                 mpatches.Patch(color=_VARDIYA_RENK["Gece"], label="Gece (00-08)"),
                 mpatches.Patch(color=_VARDIYA_RENK[None], label="İzin günü")]
    ax.legend(handles=etiketler, loc="upper center", bbox_to_anchor=(0.5, -0.08),
               ncol=4, fontsize=9)

    if os.path.dirname(cikti_yolu):
        os.makedirs(os.path.dirname(cikti_yolu), exist_ok=True)
    plt.tight_layout()
    plt.savefig(cikti_yolu, dpi=150, bbox_inches="tight")
    plt.close()


# ---------------------------------------------------------------------------
# 3) MALİYET DAĞILIMI
# ---------------------------------------------------------------------------
def maliyet_dagilimi_ciz(kapsama, cikti_yolu="maliyet_dagilimi.png"):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

    # --- Sol: vardiya türüne göre toplam maliyet ---
    vardiya_maliyeti_toplam = {
        vardiya: sum(kapsama[gun][vardiya] for gun in GUNLER) * VARDIYA_MALIYETI[vardiya]
        for vardiya in VARDIYALAR
    }
    renkler = [_VARDIYA_RENK[v] for v in VARDIYALAR]
    ax1.pie(vardiya_maliyeti_toplam.values(),
             labels=[f"{v}\n{m:,.0f} TL" for v, m in vardiya_maliyeti_toplam.items()],
             colors=renkler, autopct="%1.1f%%", startangle=90,
             wedgeprops=dict(edgecolor="white", linewidth=1.5))
    ax1.set_title("Vardiya Türüne Göre Maliyet Dağılımı", fontsize=11, fontweight="bold")

    # --- Sağ: güne göre toplam maliyet ---
    gunluk_maliyet = [
        sum(kapsama[gun][v] * VARDIYA_MALIYETI[v] for v in VARDIYALAR) for gun in GUNLER
    ]
    ax2.bar(GUNLER, gunluk_maliyet, color="#3498db", edgecolor="black", linewidth=0.6)
    for i, deger in enumerate(gunluk_maliyet):
        ax2.text(i, deger + max(gunluk_maliyet) * 0.02, f"{deger:,.0f}",
                  ha="center", fontsize=8.5)
    ax2.set_ylabel("Maliyet (TL)")
    ax2.set_title("Güne Göre Toplam İşçilik Maliyeti", fontsize=11, fontweight="bold")
    ax2.tick_params(axis="x", rotation=25)
    ax2.grid(axis="y", alpha=0.3)

    if os.path.dirname(cikti_yolu):
        os.makedirs(os.path.dirname(cikti_yolu), exist_ok=True)
    plt.tight_layout()
    plt.savefig(cikti_yolu, dpi=150)
    plt.close()


def tum_gorselleri_uret(cizelge, talep, kapsama, cikti_klasoru="."):
    """
    Varsayılan olarak görselleri proje KÖK dizinine (README.md ile aynı yere)
    kaydeder — ayrı bir alt klasör kullanılmaz, böylece README'deki
    ![...](talep_kapsama.png) gibi göreli bağlantılar hiçbir yol/klasör
    karışıklığı olmadan doğrudan çalışır.
    """
    talep_kapsama_ciz(talep, kapsama, os.path.join(cikti_klasoru, "talep_kapsama.png"))
    calisan_cizelgesi_ciz(cizelge, os.path.join(cikti_klasoru, "calisan_cizelgesi.png"))
    maliyet_dagilimi_ciz(kapsama, os.path.join(cikti_klasoru, "maliyet_dagilimi.png"))
