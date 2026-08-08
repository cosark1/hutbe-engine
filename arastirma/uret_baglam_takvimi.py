# -*- coding: utf-8 -*-
"""
İP-4: Bağlam eşleştirme tablosu üretimi.
Her hutbe haftasına (Cuma tarihi) dini takvim, siyasi takvim ve kriz olaylarını bağlar.
Çıktı: baglam_takvimi.csv
Şema: hafta_id, tarih, dini_gun, siyasi_olay, kriz_olayi, olay_notu

Pencere kuralları:
- dini_gun: olay hutbe Cumasının ±6 gün penceresindeyse yazılır (o haftanın vesilesi)
- siyasi_olay: seçim/referandum tarihi Cumadan sonraki 14 gün içindeyse "öncesi",
  önceki 14 gün içindeyse "sonrası" olarak işaretlenir
- kriz_olayi: olay Cumadan önceki 28 gün içinde başladıysa işaretlenir (tepki penceresi);
  pandemi gibi süreli olaylar aralık boyunca işaretlenir
Kandillerden Kadir Gecesi (Ramazan+26) kesindir; Berat (Ramazan-15) YAKLAŞIKTIR (hicri ay
uzunluğu ±1 gün) ve nota "yaklaşık" düşülür. Regaib, Miraç ve Mevlid kandilleri v2'de eklendi
(20.07.2026, İP-4) — sabit çapa tarihleri, web taraması + korpus çapraz doğrulamasıyla.
"""
import json, csv
from datetime import date, timedelta
from pathlib import Path

kok = Path(__file__).resolve().parent

def t(s):  # "dd.mm.yyyy" -> date
    g, a, y = s.split(".")
    return date(int(y), int(a), int(g))

# --- Dini takvim çapaları (Diyanet takvimi, gregoryen) ---
ramazan_baslangic = {
    2011: date(2011, 8, 1),  2012: date(2012, 7, 20), 2013: date(2013, 7, 9),
    2014: date(2014, 6, 28), 2015: date(2015, 6, 18), 2016: date(2016, 6, 6),
    2017: date(2017, 5, 27), 2018: date(2018, 5, 16), 2019: date(2019, 5, 6),
    2020: date(2020, 4, 24), 2021: date(2021, 4, 13), 2022: date(2022, 4, 2),
    2023: date(2023, 3, 23), 2024: date(2024, 3, 11), 2025: date(2025, 3, 1),
    2026: date(2026, 2, 19),
}
ramazan_bayrami = {
    2011: date(2011, 8, 30),  2012: date(2012, 8, 19), 2013: date(2013, 8, 8),
    2014: date(2014, 7, 28),  2015: date(2015, 7, 17), 2016: date(2016, 7, 5),
    2017: date(2017, 6, 25),  2018: date(2018, 6, 15), 2019: date(2019, 6, 4),
    2020: date(2020, 5, 24),  2021: date(2021, 5, 13), 2022: date(2022, 5, 2),
    2023: date(2023, 4, 21),  2024: date(2024, 4, 10), 2025: date(2025, 3, 30),
    2026: date(2026, 3, 20),
}
kurban_bayrami = {
    2011: date(2011, 11, 6),  2012: date(2012, 10, 25), 2013: date(2013, 10, 15),
    2014: date(2014, 10, 4),  2015: date(2015, 9, 24),  2016: date(2016, 9, 12),
    2017: date(2017, 9, 1),   2018: date(2018, 8, 21),  2019: date(2019, 8, 11),
    2020: date(2020, 7, 31),  2021: date(2021, 7, 20),  2022: date(2022, 7, 9),
    2023: date(2023, 6, 28),  2024: date(2024, 6, 16),  2025: date(2025, 6, 6),
    2026: date(2026, 5, 27),
}

# İP-4 (20.07.2026): Kalan üç kandil eklendi. Kaynak: web taraması (Diyanet
# takvimine dayalı haber siteleri) + korpusun kendisiyle çapraz doğrulama.
# 2023-2025 Regaib/Miraç/Mevlid, korpustaki ilgili hutbelerin metniyle
# (ör. "Önümüzdeki Salı'yı Çarşamba'ya bağlayan gece..." gibi göreli tarih
# ifadeleri) birebir doğrulandı. 2015 Miraç Kandili ilk taramada "3 Mayıs"
# (aslında 2016 değeriyle karışmış bir hata) çıkmıştı; korpustaki
# "15.05.2015 | MİRAÇ KANDİLİ" hutbesiyle 15 Mayıs olarak düzeltildi —
# ardışık yıllar arası gün farkı (~354-355 gün) kontrolüyle bu hata
# yakalandı. Regaib, sabit bir hicri güne değil "Receb ayının ilk cuma
# gecesi"ne denk geldiğinden yıllar arası fark 350-357 gün arasında
# gezinir (bu normaldir, hata değildir).
regaib_kandili = {
    2011: date(2011, 6, 2),   2012: date(2012, 5, 24),  2013: date(2013, 5, 16),
    2014: date(2014, 5, 1),   2015: date(2015, 4, 23),  2016: date(2016, 4, 7),
    2017: date(2017, 3, 30),  2018: date(2018, 3, 22),  2019: date(2019, 3, 7),
    2020: date(2020, 2, 27),  2021: date(2021, 2, 18),  2022: date(2022, 2, 3),
    2023: date(2023, 1, 26),  2024: date(2024, 1, 11),  2025: date(2025, 1, 2),
    # 2026 receb ayının regaib'i miladi olarak 2025 Aralık'ına düşüyor (Diyanet
    # takvimi: 25.12.2025) -- 2025 hutbeleri (İP-4'te ayrı doğrulanmış) için
    # kafa karışıklığı yaratmaması adına burada eklenmedi, ayrı not: bkz.
    # arastirma_programi.md 21.07.2026 günlüğü.
}
mirac_kandili = {
    2011: date(2011, 6, 28),  2012: date(2012, 6, 16),  2013: date(2013, 6, 5),
    2014: date(2014, 5, 25),  2015: date(2015, 5, 15),  2016: date(2016, 5, 3),
    2017: date(2017, 4, 23),  2018: date(2018, 4, 13),  2019: date(2019, 4, 2),
    2020: date(2020, 3, 21),  2021: date(2021, 3, 10),  2022: date(2022, 2, 27),
    2023: date(2023, 2, 17),  2024: date(2024, 2, 6),   2025: date(2025, 1, 26),
    2026: date(2026, 1, 15),
}
berat_kandili_kesin = {
    # Diyanet takvimine göre doğrulanmış kesin Berat tarihleri (var olduğunda
    # ramazan_baslangic-15 yaklaşık formülünün yerine kullanılır). Yalnızca
    # 2026 için eklendi (09.01.2026/30.01.2026 hutbe metinleriyle çapraz
    # doğrulandı: "Pazartesi'yi Salı'ya bağlayan gece" = 02.02.2026 Pazartesi).
    2026: date(2026, 2, 2),
}
# Diyanet takvimiyle doğrulanmış, korpus hutbe metinlerindeki göreli tarih
# ifadeleriyle çapraz kontrol edilmiş yeni olay türleri (2026, İP-4'ün
# orijinal kapsamında yoktu -- yalnızca bu batch için eklendi, 2011-2025
# için geriye dönük araştırılmadı, bkz. arastirma_programi.md).
hicri_yilbasi = {2026: date(2026, 6, 16)}
asure_gunu = {2026: date(2026, 6, 25)}
mevlid_kandili = {
    2011: date(2011, 2, 14),  2012: date(2012, 2, 3),   2013: date(2013, 1, 23),
    2014: date(2014, 1, 12),  2015: date(2015, 12, 22),
    2016: date(2016, 12, 11), 2017: date(2017, 11, 30), 2018: date(2018, 11, 19),
    2019: date(2019, 11, 8),  2020: date(2020, 10, 28), 2021: date(2021, 10, 17),
    2022: date(2022, 10, 7),  2023: date(2023, 9, 26),  2024: date(2024, 9, 14),
    2025: date(2025, 9, 3),
}

dini_olaylar = []  # (tarih, ad, yaklasik_mi)
for y, d in ramazan_baslangic.items():
    dini_olaylar.append((d, "Ramazan başlangıcı", False))
    dini_olaylar.append((d + timedelta(days=26), "Kadir Gecesi", False))
    if y in berat_kandili_kesin:
        dini_olaylar.append((berat_kandili_kesin[y], "Berat Kandili", False))
    else:
        dini_olaylar.append((d - timedelta(days=15), "Berat Kandili", True))
for y, d in ramazan_bayrami.items():
    dini_olaylar.append((d, "Ramazan Bayramı", False))
for y, d in hicri_yilbasi.items():
    dini_olaylar.append((d, "Hicri Yılbaşı", False))
for y, d in asure_gunu.items():
    dini_olaylar.append((d, "Aşure Günü", False))
for y, d in regaib_kandili.items():
    dini_olaylar.append((d, "Regaib Kandili", False))
for y, d in mirac_kandili.items():
    dini_olaylar.append((d, "Miraç Kandili", False))
for y, d in mevlid_kandili.items():
    dini_olaylar.append((d, "Mevlid Kandili", False))
for y, d in kurban_bayrami.items():
    dini_olaylar.append((d, "Kurban Bayramı", False))

def ramazan_icinde(g):
    for y, bas in ramazan_baslangic.items():
        if bas <= g < ramazan_bayrami[y]:
            return True
    return False

# --- Siyasi takvim: seçimler ve referandumlar ---
secimler = [
    (date(2011, 6, 12), "Genel seçim"),
    (date(2014, 3, 30), "Yerel seçim"),
    (date(2014, 8, 10), "Cumhurbaşkanlığı seçimi"),
    (date(2015, 6, 7),  "Genel seçim (Haziran)"),
    (date(2015, 11, 1), "Genel seçim (Kasım, yenileme)"),
    (date(2017, 4, 16), "Anayasa referandumu"),
    (date(2018, 6, 24), "Genel + CB seçimi"),
    (date(2019, 3, 31), "Yerel seçim"),
    (date(2019, 6, 23), "İstanbul seçim yenilemesi"),
    (date(2023, 5, 14), "Genel + CB seçimi 1. tur"),
    (date(2023, 5, 28), "CB seçimi 2. tur"),
    (date(2024, 3, 31), "Yerel seçim"),
]

# --- Kriz olayları: (başlangıç, bitiş|None, ad) — nokta olaylar bitiş None ---
krizler = [
    (date(2011, 10, 23), None, "Van depremi"),
    (date(2014, 5, 13),  None, "Soma maden faciası"),
    (date(2015, 7, 20),  None, "Suruç saldırısı"),
    (date(2015, 10, 10), None, "Ankara Gar saldırısı"),
    (date(2016, 7, 15),  None, "15 Temmuz darbe girişimi"),
    (date(2016, 11, 29), None, "Aladağ yurt yangını"),
    (date(2020, 1, 24),  None, "Elazığ depremi"),
    (date(2020, 3, 11),  date(2021, 7, 1), "COVID-19 pandemisi (yoğun dönem)"),
    (date(2020, 10, 30), None, "İzmir depremi"),
    (date(2021, 7, 28),  date(2021, 8, 12), "Orman yangınları (Akdeniz-Ege)"),
    (date(2021, 12, 17), date(2022, 1, 15), "Kur şoku (Aralık 2021)"),
    (date(2023, 2, 6),   date(2023, 5, 6), "6 Şubat Kahramanmaraş depremleri"),
]

hutbeler = json.loads((kok.parent / "site" / "data" / "hutbeler.json").read_text(encoding="utf-8"))
tarihler = sorted({h["date"] for h in hutbeler}, key=t)

satirlar = []
for ts in tarihler:
    g = t(ts)
    dini, siyasi, kriz, not_ = [], [], [], []

    for d, ad, yaklasik in dini_olaylar:
        if abs((g - d).days) <= 6:
            dini.append(ad)
            if yaklasik:
                not_.append(f"{ad} tarihi yaklaşık (±1 gün)")
    if ramazan_icinde(g) and "Ramazan başlangıcı" not in dini and "Kadir Gecesi" not in dini:
        dini.append("Ramazan içi")

    for d, ad in secimler:
        fark = (d - g).days
        if 0 < fark <= 14:
            siyasi.append(f"{ad} öncesi ({fark} gün)")
        elif 0 <= -fark <= 14:
            siyasi.append(f"{ad} sonrası ({-fark} gün)")

    for bas, bit, ad in krizler:
        if bit is None:
            fark = (g - bas).days
            if 0 <= fark <= 28:
                kriz.append(f"{ad} (+{fark} gün)")
        else:
            if bas <= g <= bit:
                kriz.append(ad)

    satirlar.append([ts.replace(".", "")[4:] + "-" + ts[:5].replace(".", ""),  # hafta_id: yyyy-ddmm
                     ts, "; ".join(dini), "; ".join(siyasi), "; ".join(kriz), "; ".join(not_)])

cikti = kok / "baglam_takvimi.csv"
with open(cikti, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(["hafta_id", "tarih", "dini_gun", "siyasi_olay", "kriz_olayi", "olay_notu"])
    w.writerows(satirlar)

dolu = sum(1 for s in satirlar if s[2] or s[3] or s[4])
print(f"{len(satirlar)} hafta yazıldı → {cikti.name} | en az bir bağlam etiketi olan hafta: {dolu}")
for kolon, ad in [(2, "dini_gun"), (3, "siyasi_olay"), (4, "kriz_olayi")]:
    print(f"  {ad}: {sum(1 for s in satirlar if s[kolon])} hafta")
