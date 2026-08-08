import json, re, unicodedata, csv
from collections import Counter, defaultdict

def norm(s):
    s = s.replace('İ','i').replace('I','ı').replace('Ü','ü').replace('Ö','ö').replace('Ç','ç').replace('Ş','ş').replace('Ğ','ğ')
    s = s.lower().replace('’',"'").replace("‘","'").replace("`","'").replace("'", "")
    s = unicodedata.normalize('NFKD', s)
    return ''.join(c for c in s if not unicodedata.combining(c)).strip()

SURAS = [
 (1,"Fatiha"),(2,"Bakara"),(3,"Al-i İmran"),(4,"Nisa"),(5,"Maide"),(6,"En'am"),(7,"A'raf"),(8,"Enfal"),
 (9,"Tevbe"),(10,"Yunus"),(11,"Hud"),(12,"Yusuf"),(13,"Ra'd"),(14,"İbrahim"),(15,"Hicr"),(16,"Nahl"),
 (17,"İsra"),(18,"Kehf"),(19,"Meryem"),(20,"Taha"),(21,"Enbiya"),(22,"Hac"),(23,"Mü'minun"),(24,"Nur"),
 (25,"Furkan"),(26,"Şuara"),(27,"Neml"),(28,"Kasas"),(29,"Ankebut"),(30,"Rum"),(31,"Lokman"),(32,"Secde"),
 (33,"Ahzab"),(34,"Sebe"),(35,"Fatır"),(36,"Yasin"),(37,"Saffat"),(38,"Sad"),(39,"Zümer"),(40,"Mü'min"),
 (41,"Fussilet"),(42,"Şura"),(43,"Zuhruf"),(44,"Duhan"),(45,"Casiye"),(46,"Ahkaf"),(47,"Muhammed"),(48,"Fetih"),
 (49,"Hucurat"),(50,"Kaf"),(51,"Zariyat"),(52,"Tur"),(53,"Necm"),(54,"Kamer"),(55,"Rahman"),(56,"Vakıa"),
 (57,"Hadid"),(58,"Mücadele"),(59,"Haşr"),(60,"Mümtehine"),(61,"Saff"),(62,"Cuma"),(63,"Münafikun"),(64,"Tegabun"),
 (65,"Talak"),(66,"Tahrim"),(67,"Mülk"),(68,"Kalem"),(69,"Hakka"),(70,"Mearic"),(71,"Nuh"),(72,"Cin"),
 (73,"Müzzemmil"),(74,"Müddessir"),(75,"Kıyamet"),(76,"İnsan"),(77,"Mürselat"),(78,"Nebe"),(79,"Naziat"),(80,"Abese"),
 (81,"Tekvir"),(82,"İnfitar"),(83,"Mutaffifin"),(84,"İnşikak"),(85,"Buruc"),(86,"Tarık"),(87,"Ala"),(88,"Gaşiye"),
 (89,"Fecr"),(90,"Beled"),(91,"Şems"),(92,"Leyl"),(93,"Duha"),(94,"İnşirah"),(95,"Tin"),(96,"Alak"),
 (97,"Kadir"),(98,"Beyyine"),(99,"Zilzal"),(100,"Adiyat"),(101,"Karia"),(102,"Tekasür"),(103,"Asr"),(104,"Hümeze"),
 (105,"Fil"),(106,"Kureyş"),(107,"Maun"),(108,"Kevser"),(109,"Kafirun"),(110,"Nasr"),(111,"Tebbet"),(112,"İhlas"),
 (113,"Felak"),(114,"Nas"),
]
VARIANTS = {
 "imran":"Al-i İmran","aliimran":"Al-i İmran","enam":"En'am","araf":"A'raf","rad":"Ra'd",
 "muminun":"Mü'minun","mumin":"Mü'min","gafir":"Mü'min","hacc":"Hac","yasin":"Yasin","yasiin":"Yasin",
 "kadr":"Kadir","insirah":"İnşirah","serh":"İnşirah","dehr":"İnsan","mesed":"Tebbet","cuma":"Cuma",
 "tovbe":"Tevbe","furkaan":"Furkan","fussilet":"Fussilet","fussılet":"Fussilet","kıyame":"Kıyamet",
}
NORM2CANON = {}
for num, name in SURAS:
    NORM2CANON[norm(name)] = (num, name)
for variant, canon in VARIANTS.items():
    for num, name in SURAS:
        if name == canon:
            NORM2CANON[variant] = (num, name)

SURE_REF_PAT = re.compile(r"^([A-ZÇĞİÖŞÜ][a-zçğıöşü'’\-]+(?:\s[A-ZÇĞİÖŞÜ][a-zçğıöşü'’\-]+)?)\s*,?\s*(\d{1,3})\s*/\s*(\d{1,3})")

CANON_HADITH = {
 "Buhârî":"Buhârî","Buhari":"Buhârî","Müslim":"Müslim","Tirmizî":"Tirmizî","Tirmizi":"Tirmizî",
 "İbn Mâce":"İbn Mâce","İbn Mace":"İbn Mâce","Ebû Dâvûd":"Ebû Dâvûd","Ebu Davud":"Ebû Dâvûd",
 "Nesâi":"Nesâi","Nesai":"Nesâi","Taberânî":"Taberânî","Taberani":"Taberânî","Dârimî":"Dârimî","Darimi":"Dârimî",
 "Beyhakî":"Beyhakî","Beyhaki":"Beyhakî","Muvatta":"Muvatta","Ahmed b. Hanbel":"Ahmed b. Hanbel",
 "Müsned":"Ahmed b. Hanbel (Müsned)","Hakim":"Hakim","Müstedrek":"Hakim (Müstedrek)","Heysemî":"Heysemî","Heysemi":"Heysemî",
}
NORM2HADITH = {norm(k): v for k, v in CANON_HADITH.items()}

# v2 (03.08.2026, İP-7b atıf denetimi kök-neden düzeltmesi -- bu betik şu an
# hutbeler_v3_categorized.json bulunmadığı için çalıştırılamıyor, ancak
# tutarlılık için 07/08'deki düzeltme buraya da taşındı): eski HADITH_PAT
# regex'i kaynak-bölüm arasında virgül olmayan durumları ve cilt/sayfa
# numarasının bölüm sanılmasını kaçırıyordu; iki büyük-harfli kelimeyle
# sınırlı olduğundan "Gusül ve Teyemmüm" gibi bağlaçlı bölüm adlarını kırpıyordu.
ROMAN_RE = re.compile(r'^[IVXLC]+$')

def split_hadith_ref(ref_clean):
    """Dipnot metninden (kaynak, bölüm) döndürür; kaynak tanınmazsa (None, '')."""
    first = re.split(r'\s*;\s*', ref_clean)[0]
    toks = [t for t in re.split(r'[\s,]+', first) if t]
    canon, rest = None, ''
    for n in (3, 2, 1):
        if len(toks) < n:
            continue
        c = NORM2HADITH.get(norm(' '.join(toks[:n])))
        if c:
            canon = c
            rest = first
            for t in toks[:n]:
                rest = rest.split(t, 1)[1] if t in rest else rest
            rest = rest.lstrip(' ,.')
            break
    if not canon:
        return None, ''
    seg = re.split(r'[,;]', rest)[0].strip(' ,.:"“”')
    seg = re.sub(r'\s*\d[\d\s/\-]*$', '', seg).strip(' ,.:"“”')
    bolum = '' if (not seg or ROMAN_RE.match(seg)) else seg
    return canon, bolum

data = json.load(open("hutbeler_v3_categorized.json"))

ayet_rows = []
hadis_rows = []
unresolved = 0

for e in data:
    date, cat, title = e["date"], e["primary_category"], e["title"]
    for c in e["citations"]:
        ref = c.get("ref")
        quote = c["quote"]
        if not ref:
            unresolved += 1
            continue
        ref_clean = ref.strip()
        m = SURE_REF_PAT.match(ref_clean)
        matched = False
        if m:
            key = norm(m.group(1))
            canon = NORM2CANON.get(key)
            if canon:
                cnum, cname = canon
                ayet_rows.append({
                    "sure": cname, "sure_no": cnum, "ayet_no": int(m.group(3)),
                    "quote": quote, "ref_raw": ref_clean, "date": date, "title": title, "category": cat
                })
                matched = True
        if not matched:
            canon, bolum = split_hadith_ref(ref_clean)
            if canon:
                hadis_rows.append({
                    "kaynak": canon, "bolum": bolum,
                    "quote": quote, "ref_raw": ref_clean, "date": date, "title": title, "category": cat
                })
                matched = True
        if not matched:
            unresolved += 1

print(f"Ayet: {len(ayet_rows)}, Hadis: {len(hadis_rows)}, çözümlenemeyen: {unresolved}")

with open("ayet_tam_metin.json", "w", encoding="utf-8") as f:
    json.dump(ayet_rows, f, ensure_ascii=False, indent=1)
with open("hadis_tam_metin.json", "w", encoding="utf-8") as f:
    json.dump(hadis_rows, f, ensure_ascii=False, indent=1)

with open("ayet_tam_metin.csv", "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f); w.writerow(["sure","ayet_no","ayet_meali_hutbede_gecen","tema","tarih","hutbe_basligi"])
    for r in sorted(ayet_rows, key=lambda x:(x["sure_no"], x["ayet_no"])):
        w.writerow([r["sure"], r["ayet_no"], r["quote"], r["category"], r["date"], r["title"]])

with open("hadis_tam_metin.csv", "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f); w.writerow(["kaynak","bolum","hadis_meali_hutbede_gecen","tema","tarih","hutbe_basligi"])
    for r in sorted(hadis_rows, key=lambda x:(x["kaynak"], x["bolum"])):
        w.writerow([r["kaynak"], r["bolum"], r["quote"], r["category"], r["date"], r["title"]])

# aggregated rankings with sample quote text
ayet_counter = Counter((r["sure"], r["ayet_no"]) for r in ayet_rows)
ayet_quote_sample = {}
for r in ayet_rows:
    k = (r["sure"], r["ayet_no"])
    ayet_quote_sample.setdefault(k, r["quote"])

print("\nEn çok tekrarlanan 15 ayet (tam metinle):")
for (sure, no), cnt in ayet_counter.most_common(15):
    print(f"  {sure} {no} ({cnt}x): \"{ayet_quote_sample[(sure,no)]}\"")

hadis_counter = Counter((r["kaynak"], r["bolum"]) for r in hadis_rows)
hadis_quote_sample = {}
for r in hadis_rows:
    k = (r["kaynak"], r["bolum"])
    hadis_quote_sample.setdefault(k, r["quote"])
print("\nEn çok tekrarlanan 15 hadis (tam metinle):")
for (kaynak, bolum), cnt in hadis_counter.most_common(15):
    print(f"  {kaynak} - {bolum} ({cnt}x): \"{hadis_quote_sample[(kaynak,bolum)]}\"")
