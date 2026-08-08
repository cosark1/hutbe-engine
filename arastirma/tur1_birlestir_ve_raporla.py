# -*- coding: utf-8 -*-
"""
İP-2 Tur 1: paket CSV'lerini birleştirir, anahtarla karşılaştırır, metrikleri basar.
Çıktılar: tur1/tur1_etiketler.csv (birleşik) + konsola metrik dökümü.
Metrikler: ham uyum, Cohen kappa + %95 bootstrap GA (1000 örnek, SEED=42),
kategori bazında uyum, en sık karışan çiftler, ikincil Jaccard.
"""
import csv, random
from collections import Counter, defaultdict
from pathlib import Path

kok = Path(__file__).resolve().parent
tur1 = kok / "tur1"

birlesik = {}
for p in sorted(tur1.glob("etiketler_paket_*.csv")):
    for r in csv.DictReader(open(p, encoding="utf-8-sig")):
        birlesik[r["sira"].strip()] = {
            "ana": r["ana_kategori"].strip(),
            "ikincil": r.get("ikincil_kategoriler", "").strip(),
        }
print(f"Birleşik etiket: {len(birlesik)} kayıt ({len(list(tur1.glob('etiketler_paket_*.csv')))} paket)")

anahtar = {r["sira"]: r for r in csv.DictReader(open(kok / "guvenilirlik_orneklem_anahtar.csv", encoding="utf-8-sig"))}

with open(tur1 / "tur1_etiketler.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(["sira", "ana_kategori", "ikincil_kategoriler"])
    for s in sorted(birlesik, key=int):
        w.writerow([s, birlesik[s]["ana"], birlesik[s]["ikincil"]])

ortak = sorted(set(anahtar) & set(birlesik), key=int)
a_list = [anahtar[s]["ana_kategori"] for s in ortak]
b_list = [birlesik[s]["ana"] for s in ortak]
n = len(ortak)

def kappa_hesapla(a, b):
    m = len(a)
    po = sum(x == y for x, y in zip(a, b)) / m
    ca, cb = Counter(a), Counter(b)
    pe = sum(ca[k] * cb.get(k, 0) for k in ca) / (m * m)
    return (po - pe) / (1 - pe) if pe < 1 else float("nan"), po

kappa, po = kappa_hesapla(a_list, b_list)

rng = random.Random(42)
boot = []
for _ in range(1000):
    idx = [rng.randrange(n) for _ in range(n)]
    k, _ = kappa_hesapla([a_list[i] for i in idx], [b_list[i] for i in idx])
    boot.append(k)
boot.sort()
alt, ust = boot[24], boot[974]

print(f"\nANA KATEGORİ (n={n})")
print(f"  ham uyum: {po:.2%} | Cohen kappa: {kappa:.3f} [%95 GA: {alt:.3f}–{ust:.3f}]")

print("\nKATEGORİ BAZINDA UYUM (anahtar kategorisine göre):")
kat_toplam, kat_uyum = Counter(a_list), Counter()
for a, b in zip(a_list, b_list):
    if a == b:
        kat_uyum[a] += 1
for kat, t in kat_toplam.most_common():
    print(f"  {kat_uyum[kat]:3d}/{t:<3d} ({kat_uyum[kat]/t:.0%})  {kat}")

print("\nEN SIK KARIŞAN ÇİFTLER (anahtar → etiketçi):")
kariskl = Counter((a, b) for a, b in zip(a_list, b_list) if a != b)
for (a, b), adet in kariskl.most_common(10):
    print(f"  {adet:2d}  {a}  →  {b}")

def kume(s):
    return frozenset(x.strip() for x in (s or "").split(";") if x.strip())

jac_toplam, tam = 0.0, 0
for s in ortak:
    ka, kb = kume(anahtar[s]["ikincil_kategoriler"]), kume(birlesik[s]["ikincil"])
    jac = 1.0 if not ka and not kb else len(ka & kb) / len(ka | kb)
    jac_toplam += jac
    tam += ka == kb
print(f"\nİKİNCİL — ortalama Jaccard: {jac_toplam/n:.3f} | tam eşleşme: {tam}/{n}")

gecersiz = [s for s in ortak if birlesik[s]["ana"] not in set(a_list)]
if gecersiz:
    print(f"\n⚠️ Şema dışı ana kategori içeren kayıtlar: {gecersiz}")
