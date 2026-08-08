# -*- coding: utf-8 -*-
"""Fill missing ayet/hadis citations in site/data/{ayetler,hadisler}.json
for hutbeler that currently have none, by replicating the extraction logic
of site/pipeline/01_extract.py (quote+footnote matching) and
02_citations.py (sure/hadith-source resolution) against the full text
already stored in site/data/metinler/{yil}.json. Also does a best-effort
whitelist scan for sahabe mentions.

Only ADDS rows for dates that currently have zero ayet (resp. hadis)
rows -- existing correctly-extracted data is left untouched.

Usage: python 07_fill_missing_citations.py [--dry-run]
(run from anywhere; paths below are absolute to this project)
"""
import json, re, glob, os, unicodedata, shutil
from collections import Counter

BASE = r"G:\Drive'ım\kamuran\hutbe"
DATA = os.path.join(BASE, "site", "data")
METINLER_DIR = os.path.join(DATA, "metinler")

# ---------- v2 (20.07.2026, İP-5): robust footnote-block parser ----------
# 01_extract.py'nin orijinal get_footnotes() satır-bazlı ayrıştırıcısı yalnızca
# "her dipnot kendi satırında" düzenine sahip PDF'lerde çalışıyordu; korpusun
# önemli bir kısmında dipnot bloğu tek satır/paragraf halinde ("1 Kaynak. 2
# Kaynak2. ...") geliyor. Bu sürüm paragraf-başlangıcı çapası + ardışık
# numara taraması kullanıyor, her iki düzeni de kapsıyor.
# v3 (İP-5 kök-neden düzeltmesi #1): [A-ZÇĞİÖŞÜ] sınıfı Â/Î/Û (Arapça kökenli
# kelimelerdeki düzeltme işaretli büyük harfler: "Âl-i İmran", "Nisâ", "İsrâ",
# "Furkân" vb.) içermiyordu. Bu, dipnot numarası tarayıcısının "3 Âl-i İmran"
# gibi işaretleri tanımamasına, dolayısıyla ardışık numaralamanın kırılıp
# sonraki tüm dipnotların önceki dipnota yutulmasına yol açıyordu.
#
# v4 (İP-5 kök-neden düzeltmesi #2 ve #3): iki ek kök neden bulundu ve
# giderildi:
#  (a) Dipnot bloğunun "\n\n1 " ile başladığı varsayımı yanlıştı -- korpusun
#      önemli bir kısmında dipnot bloğu, önceki cümlenin hemen ardından, satır
#      sonu/paragraf boşluğu OLMADAN başlıyor. Çözüm: metnin kuyruğunda (son
#      3000 karakter) TÜM "N [Büyük harf]" adaylarını tara, "1"den başlayan
#      olası her diziyi dene, en UZUN ardışık (1,2,3,...) diziyi seç -- sahte
#      / kopuk eşleşmeler kısa dizilerde kalır. Ayrıca gerçek dipnotlar birbirine
#      yakın konumlarda olduğundan (MAX_GAP) uzak sıçramalı sahte zincirler elenir.
#  (b) FOOTER_RE orijinali "Diyanet İşleri Başkanlığı" / "Din Hizmetleri Genel
#      Müdürlüğü" ifadesinin METİN GÖVDESİNDE (dipnot bloğundan ÖNCE, konu
#      bağlamında -- örn. "...camilerde Diyanet İşleri Başkanlığı'nca
#      hazırlanan...") geçtiği hutbelerde, "son geçtiği yerden kes" yaklaşımı
#      bile yanlış yerden kesebiliyordu (gövdedeki geçiş gerçek dipnot
#      bloğundan sonra ama asıl ALL-CAPS altbilgiden önce olabiliyor).
#      Çözüm: kuyruğu HİÇ kesme -- re.match() zaten yalnızca segmentin
#      BAŞINDAN eşleştiği için sondaki altbilgi çöpü sure/hadis regex'lerini
#      bozmuyor. Altbilgi metni yalnızca her dipnot segmenti çıkarıldıktan
#      SONRA, o segmentin kendi içinde varsa kırpılıyor (kozmetik amaçlı).
CAP = "A-ZÇĞİÖŞÜÂÎÛ"
LOW = "a-zçğıöşüâîû"
FOOTER_TRIGGER_RE = re.compile(r'Hazırlayan(?:\s+ve\s+Redaksiyon)?:?|Din Hizmetleri Genel Müdürlüğü|D[İI]YANET İŞLERİ BAŞKANLIĞI|Diyanet İşleri Başkanlığı')
MARKER_RE = re.compile(r'(?:^|(?<=[\s.\)”’]))(\d{1,2})\s+(?=(?:el-)?[' + CAP + r'])')
FOOTNOTE_MAX_GAP = 250  # dipnot girdileri kısa metinlerdir; gerçek ardışık dipnotlar birbirine yakın olur

def get_footnotes(text):
    tail = text[max(0, len(text) - 3000):]
    candidates = [(m.start(1), int(m.group(1))) for m in MARKER_RE.finditer(tail)]
    ones = [i for i, (pos, num) in enumerate(candidates) if num == 1]
    best_run = []
    for start_i in ones:
        run = [candidates[start_i]]
        expected, last_pos = 2, candidates[start_i][0]
        for pos, num in candidates[start_i+1:]:
            if num == expected and pos - last_pos <= FOOTNOTE_MAX_GAP:
                run.append((pos, num))
                expected += 1
                last_pos = pos
        if len(run) > len(best_run):
            best_run = run
    if not best_run:
        return {}
    positions = [p for p, n in best_run] + [len(tail)]
    footnotes = {}
    for idx in range(len(positions) - 1):
        seg = tail[positions[idx]:positions[idx+1]]
        mm = re.match(r'\d{1,2}\s+(.*)', seg, re.DOTALL)
        if mm:
            ref_text = mm.group(1).strip()
            ftrig = FOOTER_TRIGGER_RE.search(ref_text)
            if ftrig:
                ref_text = ref_text[:ftrig.start()].strip()
            if len(ref_text) > 200:
                continue  # sanity cap: a real footnote reference is short; longer = misparse
            footnotes[idx+1] = ref_text
    return footnotes

# v2 (08.08.2026, İP-7b takip kök-neden düzeltmesi): bkz. 08_integrate_new_hutbe.py
# aynı isimli değişkenin yorumu -- eski desen tırnak içindeki Türkçe kesme
# işaretlerini (’) de sınır sayıp o alıntıyı baştan kaçırıyordu.
QUOTE_PAT = re.compile(r'“([^“”]{3,700})”\s*(\d{1,2})\b|‘([^‘’]{3,700})’\s*(\d{1,2})\b')

def extract_quotes(text):
    out = []
    for m in QUOTE_PAT.finditer(text):
        g_quote, g_num = (m.group(1), m.group(2)) if m.group(1) is not None else (m.group(3), m.group(4))
        quote = re.sub(r'\s+', ' ', g_quote).strip()
        num = int(g_num)
        out.append((quote, num))
    return out

# ---------- ported from 02_citations.py ----------
def norm(s):
    s = s.replace('İ','i').replace('I','ı').replace('Ü','ü').replace('Ö','ö').replace('Ç','ç').replace('Ş','ş').replace('Ğ','ğ')
    s = s.lower().replace('’',"'").replace("‘","'").replace("`","'").replace("'", "")
    s = unicodedata.normalize('NFKD', s)
    s = ''.join(c for c in s if not unicodedata.combining(c)).strip()
    # v5 (İP-5): nokta/tire/boşluk de normalize edilir -- "Ahmed b. Hanbel" /
    # "Ahmed b Hanbel" / "Al-i İmran" / "Aliimran" hepsi aynı anahtara düşsün.
    return re.sub(r'[-.\s]', '', s)

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

SURE_REF_PAT = re.compile(r"^(?:el-)?([" + CAP + r"][" + LOW + r"'’\-]+(?:\s[" + CAP + r"][" + LOW + r"'’\-]+)?)\s*,?\s*(\d{1,3})\s*/\s*(\d{1,3})")
# v5 (İP-5): bazı ayet dipnotları "sure/ayet" değil yalnızca "Sure, ayetNo."
# biçiminde (sure numarası zaten bilindiği için atlanmış). Tek koşul: virgülden
# sonra TEK bir sayı olmalı (aksi halde "Buhârî, İman, 39." gibi hadis
# referanslarıyla karışır -- onlarda sayıdan önce bir bölüm adı daha var).
SURE_REF_PAT_NOSLASH = re.compile(r"^(?:el-)?([" + CAP + r"][" + LOW + r"'’\-]+(?:\s[" + CAP + r"][" + LOW + r"'’\-]+)?)\s*,\s*(\d{1,3})\s*\.?\s*$")

# v5 (İP-5 kök-neden düzeltmesi #4): hadis kaynağı eşleştirmesi eskiden büyük
# bir literal-varyant listesine (Buhârî/Buhari/Buhâri/Buharî...) dayanıyordu;
# bu yaklaşım her yeni yazım biçimini elle eklemeyi gerektiriyordu. norm()
# zaten NFKD ile TÜM aksan işaretlerini (â/î/û fark etmeksizin) siliyor, yani
# "Buhârî", "Buhari", "Buhâri", "Buharî" hepsi norm() sonrası "buhari" olur.
# Bu yüzden artık suralarla aynı norm()-tabanlı sözlük yaklaşımını kullanıyoruz;
# yalnızca GERÇEKTEN farklı harf içeren yazım varyantları (t/d, î/û gibi taban
# harf farkları -- bunlar norm() ile birleşmez) ayrıca ekleniyor.
CANON_HADITH_BASE = {
 "buhari": "Buhârî", "muslim": "Müslim", "tirmizi": "Tirmizî", "ibn mace": "İbn Mâce",
 "ebu davud": "Ebû Dâvûd", "nesai": "Nesâi", "taberani": "Taberânî", "darimi": "Dârimî",
 "beyhaki": "Beyhakî", "muvatta": "Muvatta", "hakim": "Hakim", "heysemi": "Heysemî",
 "ibn hanbel": "Ahmed b. Hanbel", "ahmed b hanbel": "Ahmed b. Hanbel", "ahmet b hanbel": "Ahmed b. Hanbel",
 "musned": "Ahmed b. Hanbel (Müsned)", "mustedrek": "Hakim (Müstedrek)",
 "ibn hibban": "İbn Hibbân", "kudai": "Kudâî", "suyuti": "Süyûtî", "deylemi": "Deylemî",
 "bezzar": "Bezzâr", "munziri": "Münzirî", "ibn hisam": "İbn Hişâm", "belazuri": "Belâzurî",
 "ibn ebi seybe": "İbn Ebî Şeybe", "ibn ebu seybe": "İbn Ebî Şeybe",
}
NORM2HADITH = {norm(k): v for k, v in CANON_HADITH_BASE.items()}

# v6 (03.08.2026, İP-7b atıf denetimi kök-neden düzeltmesi): eski HADITH_LEAD_PAT
# regex'i üç durumu kaçırıyordu ve bu, korpusta 300+ satırlık kırpılmış/eksik
# bölüm adına yol açmıştı (bkz. arastirma/atif_denetimi/RAPOR.md):
#   (a) kaynak ile bölüm arasında virgül/nokta olmaması: "Tirmizi Birr, 15."
#   (b) bölüm adının "el-" ile başlaması: "Taberânî, el-Mu'cemü'l-evsat, VII, 56."
#   (c) bölüm yerine cilt/sayfa numarası olması: "İbn Hanbel, II, 400." (burada
#       bölüm boş kalmalı, "II" bir bölüm adı değildir)
# Ayrıca regex iki büyük-harfli kelimeyle sınırlıydı, "Gusül ve Teyemmüm" gibi
# bağlaçlı çok kelimeli bölüm adlarını "Gusül"e kırpıyordu. split_hadith_ref()
# regex yerine kelime-kelime tarama yapar: bilinen en uzun kaynak adını NORM2HADITH
# sözlüğünde arar, kalan metinden (varsa) bölüm adını çıkarır.
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

UNRESOLVED_SAMPLES = []

def extract_citations_for(text):
    fn = get_footnotes(text)
    quotes = extract_quotes(text)
    ayet_rows, hadis_rows, unresolved = [], [], 0
    for quote, num in quotes:
        ref = fn.get(num)
        if not ref:
            unresolved += 1
            continue
        ref_clean = ref.strip()
        m = SURE_REF_PAT.match(ref_clean) or SURE_REF_PAT_NOSLASH.match(ref_clean)
        matched = False
        if m:
            key = norm(m.group(1))
            canon = NORM2CANON.get(key)
            if canon:
                cnum, cname = canon
                try:
                    ayet_no = int(m.group(m.lastindex))
                except ValueError:
                    ayet_no = None
                if ayet_no is not None:
                    ayet_rows.append({"sure": cname, "sure_no": cnum, "ayet": ayet_no, "quote": quote, "ref_raw": ref_clean})
                    matched = True
        if not matched:
            canon, bolum = split_hadith_ref(ref_clean)
            if canon:
                hadis_rows.append({"kaynak": canon, "bolum": bolum, "quote": quote, "ref_raw": ref_clean})
                matched = True
        if not matched:
            unresolved += 1
            if "--dry-run" in __import__("sys").argv:
                UNRESOLVED_SAMPLES.append(ref_clean)
    return ayet_rows, hadis_rows, unresolved

# ---------- sahabe: best-effort whitelist scan (not footnote-based) ----------
SAHABE_WHITELIST = [
    "Hz. Ebu Bekir", "Hz. Ömer", "Hz. Osman", "Hz. Ali", "Hz. Aişe", "Hz. Fatıma",
    "Hz. Hatice", "Hz. Hasan", "Hz. Hüseyin", "Hz. Hamza", "Hz. Zeynep",
    "Abdullah bin Mesud", "Abdullah b. Mesud", "Bilal-i Habeşi", "Bilâl-i Habeşî",
    "Ebu Zer el-Gıffari", "Ebû Zer", "Enes bin Malik", "Enes b. Mâlik",
    "Muaz bin Cebel", "Muâz b. Cebel", "Selman-ı Farisi", "Selmân-ı Fârisî",
    "Ümmü Seleme", "Ebu Hureyre", "Ebû Hüreyre", "Abdullah b. Abbas", "İbn Abbas",
    "Abdullah b. Ömer", "İbn Ömer", "Câbir b. Abdullah", "Muâviye", "Zeyd b. Sabit",
    "Ka'b b. Mâlik", "Ebu Katade", "Ebû Katâde", "Nevvâs", "Übey b. Ka'b",
    "Ammâr b. Yâsir", "Sa'd b. Ebî Vakkas", "Huzeyfe b. Yemân", "Talha b. Ubeydullah",
    "Zübeyr b. Avvâm", "Abdurrahman b. Avf", "Ebû Ubeyde b. Cerrâh", "Süheyb-i Rûmî",
]

def norm_name_key(name):
    # canonicalize "Hz. X" and diacritic variants roughly to one bucket per person
    n = name.replace("Hz. ", "").replace("Hz.", "").strip()
    n = norm(n)
    return n

CANON_SAHABE = {}
for full in SAHABE_WHITELIST:
    key = norm_name_key(full)
    CANON_SAHABE.setdefault(key, full)
# force a stable preferred display form per known cluster (matches existing sahabeler.json style)
DISPLAY_OVERRIDE = {
    "ebubekir": "Hz. Ebu Bekir", "omer": "Hz. Ömer", "osman": "Hz. Osman", "ali": "Hz. Ali",
    "aise": "Hz. Aişe", "fatima": "Hz. Fatıma", "hatice": "Hz. Hatice", "hasan": "Hz. Hasan",
    "huseyin": "Hz. Hüseyin", "hamza": "Hz. Hamza", "zeynep": "Hz. Zeynep",
    "abdullahbinmesud": "Abdullah bin Mesud", "abdullahbmesud": "Abdullah bin Mesud",
    "bilalihabesi": "Bilal-i Habeşi", "bilalihabesii": "Bilal-i Habeşi",
    "ebuzerelgiffari": "Ebu Zer el-Gıffari", "ebuzer": "Ebu Zer el-Gıffari",
    "enesbinmalik": "Enes bin Malik", "enesbmalik": "Enes bin Malik",
    "muazbincebel": "Muaz bin Cebel", "muazbcebel": "Muaz bin Cebel",
    "selmanifarisi": "Selman-ı Farisi", "ummuseleme": "Ümmü Seleme",
    "ebuhureyre": "Ebu Hureyre", "abdullahbabbas": "Abdullah b. Abbas", "ibnabbas": "Abdullah b. Abbas",
    "abdullahbomer": "Abdullah b. Ömer", "ibnomer": "Abdullah b. Ömer",
    "caberbabdullah": "Câbir b. Abdullah", "muaviye": "Muâviye", "zeydbsabit": "Zeyd b. Sabit",
    "kabbmalik": "Ka'b b. Mâlik", "ebukatade": "Ebu Katade", "nevvas": "Nevvâs",
    "ubeybkab": "Übey b. Ka'b", "ammarbyasir": "Ammâr b. Yâsir", "sadbebivakkas": "Sa'd b. Ebî Vakkas",
    "huzeyfebyeman": "Huzeyfe b. Yemân", "talhabubeydullah": "Talha b. Ubeydullah",
    "zubeyrbavvam": "Zübeyr b. Avvâm", "abdurrahmanbavf": "Abdurrahman b. Avf",
    "ebuubeydebcerrah": "Ebû Ubeyde b. Cerrâh", "suheybirumi": "Süheyb-i Rûmî",
}

def scan_sahabe(text):
    found = Counter()
    for full in SAHABE_WHITELIST:
        n = re.escape(full)
        cnt = len(re.findall(n, text))
        if cnt:
            key = norm_name_key(full)
            disp = DISPLAY_OVERRIDE.get(key, full)
            found[disp] += cnt
    return found

# ================= main =================
if __name__ == "__main__":
    ayetler_path = os.path.join(DATA, "ayetler.json")
    hadisler_path = os.path.join(DATA, "hadisler.json")
    sahabeler_path = os.path.join(DATA, "sahabeler.json")

    ayetler = json.load(open(ayetler_path, encoding="utf-8"))
    hadisler = json.load(open(hadisler_path, encoding="utf-8"))
    sahabeler = json.load(open(sahabeler_path, encoding="utf-8"))

    ayet_dates_have = set(a["date"] for a in ayetler)
    hadis_dates_have = set(h["date"] for h in hadisler)
    sahabe_dates_have = set(s["date"] for s in sahabeler)

    hutbeler = json.load(open(os.path.join(DATA, "hutbeler.json"), encoding="utf-8"))
    by_date_meta = {h["date"]: h for h in hutbeler}

    new_ayet, new_hadis, new_sahabe = [], [], []
    total_unresolved = 0
    processed = 0

    for path in sorted(glob.glob(os.path.join(METINLER_DIR, "*.json"))):
        year = os.path.basename(path).replace(".json", "")
        if not year.isdigit():
            continue
        d = json.load(open(path, encoding="utf-8"))
        for jkey, rec in d.items():
            date = re.sub(r"-[a-h]$", "", jkey)
            meta = by_date_meta.get(date)
            if not meta:
                continue  # shouldn't happen, but guard
            title = rec["title"]
            cat = meta.get("primary_category", rec.get("category", ""))
            text = rec["text"]

            if date not in ayet_dates_have or date not in hadis_dates_have:
                ay, ha, unres = extract_citations_for(text)
                total_unresolved += unres
                if date not in ayet_dates_have and ay:
                    cnt = Counter((r["sure"], r["ayet"]) for r in ay)
                    seen = set()
                    for r in ay:
                        k = (r["sure"], r["ayet"])
                        if k in seen:
                            continue
                        seen.add(k)
                        new_ayet.append({"sure": r["sure"], "ayet": r["ayet"], "quote": r["quote"], "category": cat, "date": date, "title": title, "count": cnt[k]})
                if date not in hadis_dates_have and ha:
                    cnt = Counter((r["kaynak"], r["bolum"]) for r in ha)
                    seen = set()
                    for r in ha:
                        k = (r["kaynak"], r["bolum"])
                        if k in seen:
                            continue
                        seen.add(k)
                        new_hadis.append({"kaynak": r["kaynak"], "bolum": r["bolum"], "quote": r["quote"], "category": cat, "date": date, "title": title, "count": cnt[k]})
                processed += 1

            if date not in sahabe_dates_have:
                found = scan_sahabe(text)
                for isim, cnt in found.items():
                    new_sahabe.append({"isim": isim, "date": date, "category": cat, "title": title, "count": cnt})

    print(f"İşlenen (eksik atıflı) hutbe sayısı: {processed}")
    print(f"Yeni ayet kaydı: {len(new_ayet)}")
    print(f"Yeni hadis kaydı: {len(new_hadis)}")
    print(f"Yeni sahabe kaydı: {len(new_sahabe)}")
    print(f"Çözümlenemeyen atıf (footnote var ama sure/hadis eşleşmedi): {total_unresolved}")

    new_ayet_dates = set(r["date"] for r in new_ayet)
    new_hadis_dates = set(r["date"] for r in new_hadis)
    missing_ayet_dates = [h["date"] for h in hutbeler if h["date"] not in ayet_dates_have and h["date"] not in new_ayet_dates]
    missing_both_dates = [h["date"] for h in hutbeler if h["date"] not in ayet_dates_have and h["date"] not in hadis_dates_have
                           and h["date"] not in new_ayet_dates and h["date"] not in new_hadis_dates]
    print(f"\nHâlâ ayet ataması olmayan hutbe: {len(missing_ayet_dates)}")
    print(f"Hâlâ ayet VE hadis ataması olmayan hutbe: {len(missing_both_dates)}")

    import sys
    if "--dry-run" in sys.argv:
        print("\n[DRY RUN] Dosyalar yazılmadı.")
        print(f"\nÇözümlenemeyen örnekler ({len(UNRESOLVED_SAMPLES)} toplam, ilk 40):")
        for s in UNRESOLVED_SAMPLES[:40]:
            print(" -", repr(s))
        raise SystemExit(0)

    # backup + write
    for p in [ayetler_path, hadisler_path, sahabeler_path]:
        bak = p + ".bak-preCitationFill"
        if not os.path.exists(bak):
            shutil.copy2(p, bak)

    ayetler_out = ayetler + new_ayet
    hadisler_out = hadisler + new_hadis
    sahabeler_out = sahabeler + new_sahabe

    json.dump(ayetler_out, open(ayetler_path, "w", encoding="utf-8"), ensure_ascii=False)
    json.dump(hadisler_out, open(hadisler_path, "w", encoding="utf-8"), ensure_ascii=False)
    json.dump(sahabeler_out, open(sahabeler_path, "w", encoding="utf-8"), ensure_ascii=False)

    print(f"\nayetler.json: {len(ayetler)} -> {len(ayetler_out)}")
    print(f"hadisler.json: {len(hadisler)} -> {len(hadisler_out)}")
    print(f"sahabeler.json: {len(sahabeler)} -> {len(sahabeler_out)}")
