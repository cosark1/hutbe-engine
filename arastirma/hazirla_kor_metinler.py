# -*- coding: utf-8 -*-
"""
İP-2 kör etiketleme paketi üretimi.
Girdi: guvenilirlik_orneklem_kor.csv + site/data/metinler/{yıl}.json
Çıktı: guvenilirlik_kor_metinler.json  → {sira: {tarih, baslik, metin}}
Metinler dosyalarındaki kategori/özet/anahtar kelime alanları BİLİNÇLİ olarak
dışarıda bırakılır (körlük kuralı, guvenilirlik_protokolu.md §3).
Ayrıca pilot alt-kümesi (sıra 1,11,...,191) pilot_kor_metinler.json'a yazılır.
"""
import json, csv
from pathlib import Path

kok = Path(__file__).resolve().parent
site_metin = kok.parent / "site" / "data" / "metinler"

ornek = list(csv.DictReader(open(kok / "guvenilirlik_orneklem_kor.csv", encoding="utf-8-sig")))

yil_cache = {}
def metin_getir(tarih, yil, baslik):
    if yil not in yil_cache:
        yil_cache[yil] = json.loads((site_metin / f"{yil}.json").read_text(encoding="utf-8"))
    kayit = yil_cache[yil].get(tarih)
    if kayit is None:
        return None
    return kayit.get("text")

paket, eksik = {}, []
for satir in ornek:
    metin = metin_getir(satir["tarih"], satir["yil"], satir["baslik"])
    if not metin:
        eksik.append(satir["sira"])
        continue
    paket[satir["sira"]] = {"tarih": satir["tarih"], "baslik": satir["baslik"], "metin": metin}

(kok / "guvenilirlik_kor_metinler.json").write_text(
    json.dumps(paket, ensure_ascii=False, indent=1), encoding="utf-8")

pilot_siralar = [str(i) for i in range(1, 200, 10)]
pilot = {s: paket[s] for s in pilot_siralar if s in paket}
(kok / "pilot_kor_metinler.json").write_text(
    json.dumps(pilot, ensure_ascii=False, indent=1), encoding="utf-8")

print(f"Paket: {len(paket)} hutbe | Pilot: {len(pilot)} | Eksik metin: {eksik or 'yok'}")
ort = sum(len(v["metin"]) for v in paket.values()) // max(len(paket), 1)
print(f"Ortalama metin uzunluğu: {ort} karakter")
