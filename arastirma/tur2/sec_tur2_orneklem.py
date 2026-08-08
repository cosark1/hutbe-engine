# -*- coding: utf-8 -*-
"""
İP-2 Tur 2 (insan etiketçi) alt-örneklem seçimi.
Tur 1'in 200'lük kör örnekleminden sistematik olarak her 4. sırayı (1,5,9,...,197)
alıp 50 hutbelik bir alt-küme çıkarır — orijinal tabakalı seçimin (yıl/kategori
yayılımı) yapısını korur. Kör metinler zaten guvenilirlik_kor_metinler.json'da
kategori/özet içermeden hazır (körlük kuralı guvenilirlik_protokolu.md §3).
Çıktı: tur2_veri.json → [{sira, tarih, baslik, metin}, ...] (50 kayıt, sira'ya göre sıralı)
"""
import json
from pathlib import Path

kok = Path(__file__).resolve().parent.parent  # arastirma/

kor = json.loads((kok / "guvenilirlik_kor_metinler.json").read_text(encoding="utf-8"))

secilen_siralar = [str(i) for i in range(1, 200, 4)]  # 1,5,...,197 -> 50 sira
eksik = [s for s in secilen_siralar if s not in kor]
if eksik:
    print("UYARI eksik sira:", eksik)

veri = []
for s in secilen_siralar:
    if s in kor:
        kayit = kor[s]
        veri.append({"sira": s, "tarih": kayit["tarih"], "baslik": kayit["baslik"], "metin": kayit["metin"]})

(kok / "tur2" / "tur2_veri.json").write_text(json.dumps(veri, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"{len(veri)} hutbe secildi -> tur2_veri.json")
ort = sum(len(v["metin"]) for v in veri) // max(len(veri), 1)
print(f"Ortalama metin uzunlugu: {ort} karakter")
