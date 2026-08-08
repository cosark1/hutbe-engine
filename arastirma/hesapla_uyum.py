# -*- coding: utf-8 -*-
"""
İP-2 uyum hesabı: etiketçi CSV'si ile anahtar dosyayı karşılaştırır.
Kullanım: python hesapla_uyum.py <etiketci.csv>
Metrikler: ana kategori ham uyum + Cohen kappa; ikincil kategoriler Jaccard.
"""
import csv, sys
from collections import Counter
from pathlib import Path

kok = Path(__file__).resolve().parent
etiketci_yol = Path(sys.argv[1]) if len(sys.argv) > 1 else kok / "pilot_etiketler_llm.csv"

def kume(s):
    return frozenset(x.strip() for x in (s or "").split(";") if x.strip())

anahtar = {r["sira"]: r for r in csv.DictReader(open(kok / "guvenilirlik_orneklem_anahtar.csv", encoding="utf-8-sig"))}
etiketci = {r["sira"]: r for r in csv.DictReader(open(etiketci_yol, encoding="utf-8-sig"))}

ortak = sorted(set(anahtar) & set(etiketci), key=int)
if not ortak:
    sys.exit("Ortak kayıt yok.")

a_list = [anahtar[s]["ana_kategori"] for s in ortak]
b_list = [etiketci[s]["ana_kategori"] for s in ortak]
n = len(ortak)

uyum = sum(a == b for a, b in zip(a_list, b_list))
po = uyum / n
ca, cb = Counter(a_list), Counter(b_list)
pe = sum(ca[k] * cb.get(k, 0) for k in ca) / (n * n)
kappa = (po - pe) / (1 - pe) if pe < 1 else float("nan")

print(f"Karşılaştırılan kayıt: {n}")
print(f"ANA KATEGORİ  — ham uyum: {uyum}/{n} = {po:.2%} | Cohen kappa: {kappa:.3f}")

jac_toplam, tam = 0.0, 0
for s in ortak:
    ka, kb = kume(anahtar[s]["ikincil_kategoriler"]), kume(etiketci[s]["ikincil_kategoriler"])
    if not ka and not kb:
        jac = 1.0
    else:
        jac = len(ka & kb) / len(ka | kb)
    jac_toplam += jac
    tam += ka == kb
print(f"İKİNCİL       — ortalama Jaccard: {jac_toplam / n:.3f} | tam eşleşme: {tam}/{n}")

print("\nUYUŞMAYAN ANA KATEGORİLER:")
farksiz = True
for s in ortak:
    a, b = anahtar[s]["ana_kategori"], etiketci[s]["ana_kategori"]
    if a != b:
        farksiz = False
        print(f"  sıra {s} ({anahtar[s]['tarih']} {anahtar[s]['baslik'][:45]})")
        print(f"    anahtar : {a}")
        print(f"    etiketçi: {b}")
if farksiz:
    print("  yok")
