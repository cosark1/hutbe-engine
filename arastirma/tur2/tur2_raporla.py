# -*- coding: utf-8 -*-
"""
İP-2 Tur 2 (insan etiketçi) uyum raporu — tur1_birlestir_ve_raporla.py ile aynı
metrik seti (ham uyum, Cohen kappa + %95 bootstrap GA, kategori bazında uyum,
en sık karışan çiftler, ikincil Jaccard), Tur 2'nin 50 hutbelik tek CSV'sine
uygulanmış hâli.
"""
import csv, random
from collections import Counter
from pathlib import Path

kok = Path(__file__).resolve().parent
gen_kok = kok.parent  # arastirma/

etiketci = {r["sira"].strip(): r for r in csv.DictReader(open(kok / "tur2_etiketler.csv", encoding="utf-8-sig"))}
anahtar = {r["sira"]: r for r in csv.DictReader(open(gen_kok / "guvenilirlik_orneklem_anahtar.csv", encoding="utf-8-sig"))}

ortak = sorted(set(anahtar) & set(etiketci), key=int)
a_list = [anahtar[s]["ana_kategori"] for s in ortak]
b_list = [etiketci[s]["ana_kategori"] for s in ortak]
n = len(ortak)
print(f"Karşılaştırılan kayıt: {n} (CSV'de {len(etiketci)} satır var)")

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
print(f"  ham uyum: {po:.2%} | Cohen kappa: {kappa:.3f} [%95 GA: {alt:.3f}-{ust:.3f}]")

print("\nKATEGORİ BAZINDA UYUM (anahtar kategorisine göre):")
kat_toplam, kat_uyum = Counter(a_list), Counter()
for a, b in zip(a_list, b_list):
    if a == b:
        kat_uyum[a] += 1
for kat, t in kat_toplam.most_common():
    print(f"  {kat_uyum[kat]:3d}/{t:<3d} ({kat_uyum[kat]/t:.0%})  {kat}")

print("\nEN SIK KARIŞAN ÇİFTLER (anahtar -> Tur 2 etiketçisi):")
kariskl = Counter((a, b) for a, b in zip(a_list, b_list) if a != b)
for (a, b), adet in kariskl.most_common(10):
    print(f"  {adet:2d}  {a}  ->  {b}")

def kume(s):
    return frozenset(x.strip() for x in (s or "").split(";") if x.strip())

jac_toplam, tam = 0.0, 0
for s in ortak:
    ka, kb = kume(anahtar[s]["ikincil_kategoriler"]), kume(etiketci[s]["ikincil_kategoriler"])
    jac = 1.0 if not ka and not kb else len(ka & kb) / len(ka | kb)
    jac_toplam += jac
    tam += ka == kb
print(f"\nİKİNCİL -- ortalama Jaccard: {jac_toplam/n:.3f} | tam eşleşme: {tam}/{n}")

gecersiz = [s for s in ortak if etiketci[s]["ana_kategori"] not in set(a_list) | set(b_list)]
sema = set(a_list)
disari = [s for s in ortak if etiketci[s]["ana_kategori"] not in sema]
if disari:
    print(f"\n⚠️ Şema dışı ana kategori içeren kayıtlar: {disari}")

print("\nUYUŞMAYAN ANA KATEGORİLER (detay):")
for s in ortak:
    a, b = anahtar[s]["ana_kategori"], etiketci[s]["ana_kategori"]
    if a != b:
        print(f"  sıra {s} ({anahtar[s]['tarih']} {anahtar[s]['baslik'][:45]})")
        print(f"    anahtar: {a}")
        print(f"    Tur 2  : {b}")

print("\nUYUŞMAYAN İKİNCİL KATEGORİLER (detay):")
for s in ortak:
    ka, kb = kume(anahtar[s]["ikincil_kategoriler"]), kume(etiketci[s]["ikincil_kategoriler"])
    if ka != kb:
        print(f"  sıra {s} ({anahtar[s]['tarih']} {anahtar[s]['baslik'][:45]})")
        print(f"    anahtar: {sorted(ka) or '(yok)'}")
        print(f"    Tur 2  : {sorted(kb) or '(yok)'}")
