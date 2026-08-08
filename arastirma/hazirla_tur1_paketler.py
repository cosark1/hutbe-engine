# -*- coding: utf-8 -*-
"""
İP-2 Tur 1: kör metin paketini 5 alt-pakete böler (etiketçi ajan başına 40 hutbe).
Girdi: guvenilirlik_kor_metinler.json
Çıktı: tur1/tur1_paket_{1..5}.json
"""
import json
from pathlib import Path

kok = Path(__file__).resolve().parent
paket = json.loads((kok / "guvenilirlik_kor_metinler.json").read_text(encoding="utf-8"))
hedef = kok / "tur1"
hedef.mkdir(exist_ok=True)

siralar = sorted(paket, key=int)
N = 5
for i in range(N):
    dilim = {s: paket[s] for s in siralar[i::N]}  # serpiştirilmiş dilim: her pakette tüm yıllar
    (hedef / f"tur1_paket_{i+1}.json").write_text(
        json.dumps(dilim, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"paket {i+1}: {len(dilim)} hutbe")
