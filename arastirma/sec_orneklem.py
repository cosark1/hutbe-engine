# -*- coding: utf-8 -*-
"""
İP-2 güvenilirlik örneklemi seçimi.
Tabakalı (ana kategoriye orantılı, kategori başına en az 5) + tabaka içinde
tarihe göre sıralayıp rastgele başlangıçlı sistematik seçim (yıl yayılımı için).
Tekrarlanabilirlik: SEED sabit. Çıktılar:
  - guvenilirlik_orneklem_kor.csv     → etiketçiye verilen kör dosya (etiket YOK)
  - guvenilirlik_orneklem_anahtar.csv → orijinal etiketli anahtar (karşılaştırma için)
"""
import json, csv, random, math
from pathlib import Path

SEED = 42
N_HEDEF = 200
MIN_TABAKA = 5

kok = Path(__file__).resolve().parent.parent
hutbeler = json.loads((kok / "site" / "data" / "hutbeler.json").read_text(encoding="utf-8"))

def tarih_anahtari(h):
    g, a, y = h["date"].split(".")
    return (int(y), int(a), int(g))

tabakalar = {}
for h in hutbeler:
    tabakalar.setdefault(h["primary_category"], []).append(h)

toplam = len(hutbeler)
rng = random.Random(SEED)

# Orantılı tahsis + minimum taban; yuvarlama farkını en büyük tabakalardan düzelt
tahsis = {k: max(MIN_TABAKA, round(N_HEDEF * len(v) / toplam)) for k, v in tabakalar.items()}
fark = sum(tahsis.values()) - N_HEDEF
for k in sorted(tahsis, key=lambda k: -tahsis[k]):
    if fark == 0:
        break
    adim = 1 if fark > 0 else -1
    if tahsis[k] - adim >= MIN_TABAKA:
        tahsis[k] -= adim
        fark -= adim

secim = []
for kat, grup in sorted(tabakalar.items()):
    grup = sorted(grup, key=tarih_anahtari)
    n = min(tahsis[kat], len(grup))
    adim = len(grup) / n
    baslangic = rng.uniform(0, adim)
    indeksler = sorted({min(int(baslangic + i * adim), len(grup) - 1) for i in range(n)})
    # küme tekrarı yüzünden eksik kalırsa rastgele tamamla
    kalan = [i for i in range(len(grup)) if i not in indeksler]
    rng.shuffle(kalan)
    while len(indeksler) < n and kalan:
        indeksler.append(kalan.pop())
    secim.extend(grup[i] for i in sorted(indeksler))

secim.sort(key=tarih_anahtari)

kor_yol = kok / "arastirma" / "guvenilirlik_orneklem_kor.csv"
anahtar_yol = kok / "arastirma" / "guvenilirlik_orneklem_anahtar.csv"

with open(kor_yol, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(["sira", "tarih", "yil", "baslik"])
    for i, h in enumerate(secim, 1):
        w.writerow([i, h["date"], h["year"], h["title"]])

with open(anahtar_yol, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(["sira", "tarih", "yil", "baslik", "ana_kategori", "ikincil_kategoriler"])
    for i, h in enumerate(secim, 1):
        w.writerow([i, h["date"], h["year"], h["title"],
                    h["primary_category"], "; ".join(h.get("secondary_categories") or [])])

print(f"Toplam korpus: {toplam} | Örneklem: {len(secim)} | SEED={SEED}")
print("Kategoriye göre örneklem dağılımı:")
from collections import Counter
for kat, adet in Counter(h["primary_category"] for h in secim).most_common():
    print(f"  {adet:3d}  {kat}")
print("Yıla göre:")
for yil, adet in sorted(Counter(h["year"] for h in secim).items()):
    print(f"  {yil}: {adet}")
