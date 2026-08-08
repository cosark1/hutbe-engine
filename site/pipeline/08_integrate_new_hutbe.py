# -*- coding: utf-8 -*-
"""Yeni bir hutbe PDF partisini (ör. site/pipeline/../<YIL>/ klasörüne bırakılan
tek-sayfalık, "Tarih: DD.MM.YYYY" başlıklı Diyanet hutbe PDF'leri) korpusa ve
site JSON'larına entegre eder. 21.07.2026'da 2026/ klasöründeki 29 hutbe ile
geliştirilip doğrulanmıştır (bkz. arastirma_programi.md aynı tarihli günlük).

KULLANIM (iki adım):
  1) Bu dosyadaki extract_batch() çağrısıyla PDF'lerden (tarih, başlık, tam
     metin) çıkar, bir JSON dosyasına yaz.
  2) O JSON'daki her kayıt için LABELS listesine elle (LLM okuyarak) şu
     alanları doldur: primary/secondary kategori (CATS anahtarlarından),
     cerceve/ton/muhatap/eylem_cagrisi (kod_kitabi.md §4), summary (2-3
     cümle), keywords (4-5 tematik ifade). Bu adım OTOMATİKLEŞTİRİLEMEZ --
     05_classify.py bile zaten var olan keywords/summary'yi yeniden ağırlıklandırıyor,
     sıfırdan üretmiyor (bkz. İP-5/2026 entegrasyonu günlüğü).
  3) integrate() çağrısıyla EXTRACTED + LABELS'i işleyip:
     - metinler/{yıl}.json (yeni dosya veya var olana ekleme)
     - hutbeler.json, ayetler.json, hadisler.json, sahabeler.json, kelimeler.json (ekleme)
     - meta.json (SATIR SAYISI yöntemiyle top_suras/top_hadis_kaynak/top_keywords
       yeniden hesaplanır -- count alanı ASLA toplanmaz, bkz. İP-5 oturum notları)
     - arastirma/korpus_v2/{yıl}.csv + all.csv + all.json
     dosyalarına yazar. Her JSON dosyası ilk çalıştırmada .bak-pre<YIL> yedeği alır.

Aynı tarihte iki ayrı hutbe varsa (ör. bayram + Cuma çakışması) id_suffix="-b"
kullanılır (bkz. 25.08.2017 ve 20.03.2026 örnekleri).
"""
import json, os, re, glob, shutil, unicodedata, csv
from collections import Counter

BASE = r"G:\Drive'ım\kamuran\hutbe"
DATA = os.path.join(BASE, "site", "data")

CATS = {
 "dayanisma": "Toplumsal Dayanışma, Merhamet ve Kardeşlik", "iman": "İman, Tevhid ve Ahiret",
 "ramazan": "Ramazan, Oruç ve Bayramlar", "ahlak": "Ahlak, Erdem ve Söz",
 "ibadet": "İbadet ve Kulluk", "aile": "Aile, Çocuk ve Nesil",
 "kandil": "Kandiller, Muharrem ve Mübarek Geceler", "vatan": "Vatan, Millet ve Tarih",
 "ekonomi": "Ekonomik Hayat: Kazanç, Zekat ve İsraf", "sabir": "Sabır, Tevekkül ve Manevi Olgunluk",
 "cografya": "İslam Coğrafyası ve Küresel Meseleler", "afet": "Afet, Kriz ve Sağlık",
 "peygamber": "Peygamberimiz ve Ashab", "egitim": "Eğitim, Teknoloji, Çevre ve Toplumsal Değişim",
 "kuran": "Kur'an-ı Kerim",
}

date_re = re.compile(r'(TARİH|Tarih)İ?\s*:\s*(\d{2})[./](\d{2})[./](\d{4})')
CITELIKE = re.compile(r"^[A-ZÇĞİÖŞÜ][a-zçğıöşüâîû'’.\- ]*,?\s*\d")

def is_arabic(line):
    arabic_chars = sum(1 for c in line if '؀' <= c <= 'ۿ')
    return arabic_chars > len(line.strip()) * 0.3 if line.strip() else False

def is_title_line(s):
    if len(s) < 4 or len(s) > 90: return False
    if is_arabic(s): return False
    if CITELIKE.match(s): return False
    letters = [c for c in s if c.isalpha() and c != '﷽']
    if not letters: return False
    upper_ratio = sum(1 for c in letters if c.isupper()) / len(letters)
    return upper_ratio > 0.85

def extract_title_and_body_start(text):
    """Başlığı ve gövdenin karakter ofsetini döndürür. Başlık birden çok
    satıra bölünmüş olabileceğinden (naif find() başarısız olur), satır
    indeksinden ofset hesaplanır."""
    # v2 (03.08.2026, İP-7b eksik hutbe kurtarma): bazı yıllık PDF'lerde tarih
    # eğik çizgi ayraçlıdır ("TARİH : 31/07/2015"); yalnız nokta arayan eski
    # desen bu satırı üstbilgi olarak tanımıyor, sonucunda üstbilginin kendisi
    # başlık sanılıyordu (bkz. 31.07.2015 kurtarma günlüğü).
    lines = text.split("\n")
    start_idx = 0
    for i, l in enumerate(lines[:12]):
        if re.search(r'\d{2}[./]\d{2}[./]\d{4}', l):
            start_idx = i + 1
    candidates = lines[start_idx:start_idx+80]
    for idx, l in enumerate(candidates):
        s = l.strip()
        if not s: continue
        if is_title_line(s):
            title_parts = [s]; last_j = idx
            for j in range(idx+1, min(idx+3, len(candidates))):
                nxt = candidates[j].strip()
                if not nxt: break
                if is_title_line(nxt) and len(nxt) < 60:
                    title_parts.append(nxt); last_j = j
                else: break
            title = " ".join(title_parts)
            body_line_idx = start_idx + last_j + 1
            body_char_offset = len("\n".join(lines[:body_line_idx])) + 1
            return title, body_char_offset
    return "", 0

# PyMuPDF "text" modu her GÖRSEL satırı ayrı \n ile döndürür (kelime-sarma dahil).
# Korpus kuralı (2011-2025 örneklerinden doğrulandı): paragraf geçişleri
# yalnızca bilinen hitap ifadeleriyle ("Aziz Müminler!" vb.) başlayan
# satırlardan önce \n\n olur; PDF'nin ürettiği ARADAKİ tüm satır-sarma \n'leri
# boşluğa dönmelidir. Bu adım atlanırsa metin "text" alanında cümle ortasında
# gereksiz enter'larla kayar (21.07.2026'da 2026 partisinde fark edilen ve
# düzeltilen bir hata -- bkz. arastirma_programi.md).
VOCATIVE_RE = re.compile(r'^(?:Muhterem|Aziz|Kıymetli|Değerli)\s+[A-ZÇĞİÖŞÜ][a-zA-ZçğıöşüÇĞİÖŞÜ ]*!\s*$')
FOOTNOTE_START_RE = re.compile(r'^1\s+[A-ZÇĞİÖŞÜÂÎÛ]')

def reconstruct_paragraphs(body_text):
    lines = [l.rstrip() for l in body_text.split("\n")]
    out_lines = []
    for i, line in enumerate(lines):
        s = line.strip()
        is_para_start = bool(VOCATIVE_RE.match(s)) or bool(FOOTNOTE_START_RE.match(s))
        if i == 0:
            out_lines.append(s)
        elif is_para_start:
            out_lines.append("\n\n" + s)
        else:
            out_lines.append(" " + s if s else "")
    text = "".join(out_lines)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r' *\n\n *', '\n\n', text)
    return text.strip()

def extract_batch(pdf_dir, out_json_path):
    """pdf_dir içindeki tüm *.pdf dosyalarını (date, title, text) olarak
    çıkarır ve out_json_path'e yazar. fitz (PyMuPDF) gerektirir."""
    import fitz
    files = sorted(glob.glob(os.path.join(pdf_dir, "*.pdf")))
    records = []
    for path in files:
        fname = os.path.basename(path)
        doc = fitz.open(path)
        full_text = "\n".join(page.get_text("text") for page in doc)
        m = date_re.search(full_text)
        date = f"{m.group(2)}.{m.group(3)}.{m.group(4)}" if m else None
        title, body_offset = extract_title_and_body_start(full_text)
        raw_body = full_text[body_offset:].strip() if title else full_text.strip()
        body = reconstruct_paragraphs(raw_body)
        if not date:
            print(f"UYARI: {fname} içinde 'Tarih:' bulunamadı, elle kontrol edin")
        records.append({"file": fname, "date": date, "title": title, "text": body})
    records.sort(key=lambda r: tuple(reversed(r["date"].split("."))) if r["date"] else ("",))
    json.dump(records, open(out_json_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"{len(records)} kayıt çıkarıldı -> {out_json_path}")
    for r in records:
        print(f"  {r['date']} | {r['title']} | ({r['file']})")
    return records

# ---------- atıf çıkarımı: 07_fill_missing_citations.py v5 mantığı ----------
CAP = "A-ZÇĞİÖŞÜÂÎÛ"
LOW = "a-zçğıöşüâîû"
FOOTER_TRIGGER_RE = re.compile(r'Hazırlayan(?:\s+ve\s+Redaksiyon)?:?|Din Hizmetleri Genel Müdürlüğü|D[İI]YANET İŞLERİ BAŞKANLIĞI|Diyanet İşleri Başkanlığı')
MARKER_RE = re.compile(r'(?:^|(?<=[\s.\)”’]))(\d{1,2})\s+(?=(?:el-)?[' + CAP + r'])')
FOOTNOTE_MAX_GAP = 250

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
                run.append((pos, num)); expected += 1; last_pos = pos
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
                continue
            footnotes[idx+1] = ref_text
    return footnotes

# v2 (08.08.2026, İP-7b takip kök-neden düzeltmesi): eski desen `[^“”‘’]` içerik
# sınıfının tırnak İÇİNDEKİ Türkçe iyelik/kesme işaretlerini (’, ör. "Allah’ın",
# "İslam’ı") de dışlaması, aralarında böyle bir kesme işareti geçen HER alıntıyı
# baştan sona kaçırıyordu (07.08.2026 "KARDEŞLİK" hutbesinde 6 dipnottan hiçbiri
# eşleşmedi). Artık “ ” ve ‘ ’ çiftleri birbirinden bağımsız işleniyor; her çift
# yalnızca KENDİ sınırlayıcısını içerik dışı sayıyor, kesme işaretleri serbest.
QUOTE_PAT = re.compile(r'“([^“”]{3,700})”\s*(\d{1,2})\b|‘([^‘’]{3,700})’\s*(\d{1,2})\b')
def extract_quotes(text):
    out = []
    for m in QUOTE_PAT.finditer(text):
        q, n = (m.group(1), m.group(2)) if m.group(1) is not None else (m.group(3), m.group(4))
        out.append((re.sub(r'\s+', ' ', q).strip(), int(n)))
    return out

def norm(s):
    s = s.replace('İ','i').replace('I','ı').replace('Ü','ü').replace('Ö','ö').replace('Ç','ç').replace('Ş','ş').replace('Ğ','ğ')
    s = s.lower().replace('’',"'").replace("‘","'").replace("`","'").replace("'", "")
    s = unicodedata.normalize('NFKD', s)
    s = ''.join(c for c in s if not unicodedata.combining(c)).strip()
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
for num, name in SURAS: NORM2CANON[norm(name)] = (num, name)
for variant, canon in VARIANTS.items():
    for num, name in SURAS:
        if name == canon: NORM2CANON[variant] = (num, name)

SURE_REF_PAT = re.compile(r"^(?:el-)?([" + CAP + r"][" + LOW + r"'’\-]+(?:\s[" + CAP + r"][" + LOW + r"'’\-]+)?)\s*,?\s*(\d{1,3})\s*/\s*(\d{1,3})")
SURE_REF_PAT_NOSLASH = re.compile(r"^(?:el-)?([" + CAP + r"][" + LOW + r"'’\-]+(?:\s[" + CAP + r"][" + LOW + r"'’\-]+)?)\s*,\s*(\d{1,3})\s*\.?\s*$")

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

# v6 (03.08.2026, İP-7b atıf denetimi kök-neden düzeltmesi -- ayrıntı için
# 07_fill_missing_citations.py'deki aynı isimli fonksiyonun yorumuna bkz.):
# eski HADITH_LEAD_PAT regex/virgül-öncesi-1-3-kelime yaklaşımı virgülsüz
# kaynak-bölüm ayrımını, "el-" önekli eser adlarını ve cilt/sayfa numarasının
# bölüm sanılmasını kaçırıyordu.
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

def extract_citations_for(text):
    fn = get_footnotes(text)
    quotes = extract_quotes(text)
    ayet_rows, hadis_rows, unresolved = [], [], []
    for quote, num in quotes:
        ref = fn.get(num)
        if not ref:
            unresolved.append((num, None)); continue
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
                    ayet_rows.append({"sure": cname, "ayet": ayet_no, "quote": quote})
                    matched = True
        if not matched:
            canon, bolum = split_hadith_ref(ref_clean)
            if canon:
                hadis_rows.append({"kaynak": canon, "bolum": bolum, "quote": quote})
                matched = True
        if not matched:
            unresolved.append((num, ref_clean))
    return ayet_rows, hadis_rows, unresolved

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
    return norm(name.replace("Hz. ", "").replace("Hz.", "").strip())
DISPLAY_OVERRIDE = {
    "ebubekir": "Hz. Ebu Bekir", "omer": "Hz. Ömer", "osman": "Hz. Osman", "ali": "Hz. Ali",
    "aise": "Hz. Aişe", "fatima": "Hz. Fatıma", "hatice": "Hz. Hatice", "hasan": "Hz. Hasan",
    "huseyin": "Hz. Hüseyin", "hamza": "Hz. Hamza", "zeynep": "Hz. Zeynep",
}
def scan_sahabe(text):
    found = Counter()
    for full in SAHABE_WHITELIST:
        cnt = len(re.findall(re.escape(full), text))
        if cnt:
            key = norm_name_key(full)
            found[DISPLAY_OVERRIDE.get(key, full)] += cnt
    return found

# ---------- entegrasyon ----------
def backup(path, suffix):
    if not os.path.exists(path + suffix):
        shutil.copy2(path, path + suffix)

def integrate(extracted_records, labels, year, backup_suffix=None):
    """extracted_records: extract_batch() çıktısı. labels: her kayıt için
    {date,title,id_suffix,primary,secondary,cerceve,ton,muhatap,eylem_cagrisi,
    summary,keywords} sözlükleri listesi (bkz. dosya başı KULLANIM notu)."""
    backup_suffix = backup_suffix or f".bak-pre{year}"
    ext_by_key = {(r["date"], r["title"]): r for r in extracted_records}

    new_metinler, new_hutbeler = {}, []
    new_ayet, new_hadis, new_sahabe, new_kelime = [], [], [], []
    csv_rows, unresolved_report = [], []

    for lab in labels:
        ext = ext_by_key[(lab["date"], lab["title"])]
        text = ext["text"]
        dd, mm, yyyy = lab["date"].split(".")
        hid = f"{yyyy}-{mm}-{dd}{lab.get('id_suffix','')}"
        jkey = f"{lab['date']}{lab.get('id_suffix','')}"
        primary = CATS[lab["primary"]]
        secondary = [CATS[s] for s in lab["secondary"]]

        ay, ha, unresolved = extract_citations_for(text)
        for num, ref in unresolved:
            unresolved_report.append((lab["date"], lab["title"], num, ref))
        sahabe_found = scan_sahabe(text)

        new_metinler[jkey] = {
            "title": lab["title"], "category": primary, "secondary_categories": secondary,
            "summary": lab["summary"], "keywords": lab["keywords"], "text": text,
            "id": hid, "cerceve": lab["cerceve"], "ton": lab["ton"], "muhatap": lab["muhatap"],
            "eylem_cagrisi": lab["eylem_cagrisi"],
        }
        new_hutbeler.append({
            "date": lab["date"], "year": int(yyyy), "title": lab["title"], "summary": lab["summary"],
            "keywords": lab["keywords"], "primary_category": primary, "secondary_categories": secondary,
            "citation_count": len(ay) + len(ha), "id": hid, "cerceve": lab["cerceve"], "ton": lab["ton"],
            "muhatap": lab["muhatap"], "eylem_cagrisi": lab["eylem_cagrisi"],
        })
        ay_cnt = Counter((r["sure"], r["ayet"]) for r in ay); seen = set()
        for r in ay:
            k = (r["sure"], r["ayet"])
            if k in seen: continue
            seen.add(k)
            new_ayet.append({"sure": r["sure"], "ayet": r["ayet"], "quote": r["quote"], "category": primary,
                              "date": lab["date"], "title": lab["title"], "count": ay_cnt[k]})
        ha_cnt = Counter((r["kaynak"], r["bolum"]) for r in ha); seen = set()
        for r in ha:
            k = (r["kaynak"], r["bolum"])
            if k in seen: continue
            seen.add(k)
            new_hadis.append({"kaynak": r["kaynak"], "bolum": r["bolum"], "quote": r["quote"], "category": primary,
                               "date": lab["date"], "title": lab["title"], "count": ha_cnt[k]})
        for isim, cnt in sahabe_found.items():
            new_sahabe.append({"isim": isim, "date": lab["date"], "category": primary, "title": lab["title"], "count": cnt})
        text_lower = text.lower()
        for kw in lab["keywords"]:
            cnt = text_lower.count(kw.lower()) or 1
            new_kelime.append({"keyword": kw, "date": lab["date"], "title": lab["title"], "category": primary, "count": cnt})
        csv_rows.append({
            "id": hid, "tarih": lab["date"], "baslik": lab["title"], "ana_kategori": primary,
            "ikincil_kategoriler": "; ".join(secondary), "cerceve": lab["cerceve"],
            "ton": "; ".join(lab["ton"]), "muhatap": lab["muhatap"], "eylem_cagrisi": "; ".join(lab["eylem_cagrisi"]),
        })

    print(f"İşlenen hutbe: {len(new_hutbeler)}; yeni ayet {len(new_ayet)}, hadis {len(new_hadis)}, "
          f"sahabe {len(new_sahabe)}, kelime {len(new_kelime)}; çözümlenemeyen atıf {len(unresolved_report)}")
    for u in unresolved_report:
        print("  çözümlenemedi:", u)

    metinler_path = os.path.join(DATA, "metinler", f"{year}.json")
    if os.path.exists(metinler_path):
        existing = json.load(open(metinler_path, encoding="utf-8"))
        existing.update(new_metinler)
        new_metinler = existing
    json.dump(new_metinler, open(metinler_path, "w", encoding="utf-8"), ensure_ascii=False)
    print(f"yazıldı: {metinler_path} ({len(new_metinler)} kayıt)")

    hutbeler_path = os.path.join(DATA, "hutbeler.json")
    backup(hutbeler_path, backup_suffix)
    hutbeler = json.load(open(hutbeler_path, encoding="utf-8"))
    hutbeler_out = hutbeler + new_hutbeler
    json.dump(hutbeler_out, open(hutbeler_path, "w", encoding="utf-8"), ensure_ascii=False)
    print(f"hutbeler.json: {len(hutbeler)} -> {len(hutbeler_out)}")

    for name, new_rows in [("ayetler.json", new_ayet), ("hadisler.json", new_hadis),
                            ("sahabeler.json", new_sahabe), ("kelimeler.json", new_kelime)]:
        p = os.path.join(DATA, name)
        backup(p, backup_suffix)
        old = json.load(open(p, encoding="utf-8"))
        out = old + new_rows
        json.dump(out, open(p, "w", encoding="utf-8"), ensure_ascii=False)
        print(f"{name}: {len(old)} -> {len(out)}")

    csv_path = os.path.join(BASE, "arastirma", "korpus_v2", f"{year}.csv")
    mode, write_header = ("a", False) if os.path.exists(csv_path) else ("w", True)
    with open(csv_path, mode, encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["tarih","baslik","ana_kategori","ikincil_kategoriler","cerceve","ton","muhatap","eylem_cagrisi"], quoting=csv.QUOTE_ALL)
        if write_header: w.writeheader()
        for r in csv_rows:
            w.writerow({k: v for k, v in r.items() if k != "id"})
    print(f"yazıldı: {csv_path}")

    all_csv_path = os.path.join(BASE, "arastirma", "korpus_v2", "all.csv")
    backup(all_csv_path, backup_suffix)
    existing_all = list(csv.DictReader(open(all_csv_path, encoding="utf-8")))
    existing_all_out = existing_all + csv_rows
    with open(all_csv_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["id","tarih","baslik","ana_kategori","ikincil_kategoriler","cerceve","ton","muhatap","eylem_cagrisi"], quoting=csv.QUOTE_ALL)
        w.writeheader()
        for r in existing_all_out: w.writerow(r)
    print(f"all.csv: {len(existing_all)} -> {len(existing_all_out)}")

    all_json_path = os.path.join(BASE, "arastirma", "korpus_v2", "all.json")
    backup(all_json_path, backup_suffix)
    all_json = json.load(open(all_json_path, encoding="utf-8"))
    all_json_out = all_json + [
        {"id": r["id"], "tarih": r["tarih"], "baslik": r["baslik"], "ana_kategori": r["ana_kategori"],
         "ikincil_kategoriler": r["ikincil_kategoriler"], "cerceve": r["cerceve"], "ton": r["ton"],
         "muhatap": r["muhatap"], "eylem_cagrisi": r["eylem_cagrisi"]}
        for r in csv_rows
    ]
    json.dump(all_json_out, open(all_json_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"all.json: {len(all_json)} -> {len(all_json_out)}")

def recompute_meta(backup_suffix):
    """total_hutbe/overall_category/yearly/top_*/keyword_category_matrix'i
    SATIR SAYISI yöntemiyle (count alanı toplanmadan) yeniden hesaplar.
    NOT: weekly_grid ve baglam_takvimi.csv/timeline bu fonksiyonla genişletilmez
    (bilinen, kabul edilmiş bir sınırlama -- ayrı bir iş, bkz. arastirma_programi.md)."""
    meta_path = os.path.join(DATA, "meta.json")
    backup(meta_path, backup_suffix)
    meta = json.load(open(meta_path, encoding="utf-8"))
    hutbeler = json.load(open(os.path.join(DATA, "hutbeler.json"), encoding="utf-8"))
    ayetler = json.load(open(os.path.join(DATA, "ayetler.json"), encoding="utf-8"))
    hadisler = json.load(open(os.path.join(DATA, "hadisler.json"), encoding="utf-8"))
    sahabeler = json.load(open(os.path.join(DATA, "sahabeler.json"), encoding="utf-8"))
    kelimeler = json.load(open(os.path.join(DATA, "kelimeler.json"), encoding="utf-8"))
    CATS15 = meta["overall_category"]["labels"]

    meta["total_hutbe"] = len(hutbeler)
    meta["total_ayet"] = len(ayetler)
    meta["total_hadis"] = len(hadisler)
    meta["total_sahabe_isim"] = len(set(s["isim"] for s in sahabeler))
    meta["total_citations"] = sum(h.get("citation_count", 0) for h in hutbeler)
    meta["total_keyword_mentions"] = len(kelimeler)
    meta["total_keywords"] = len(set(k["keyword"] for k in kelimeler))
    meta["year_max"] = max(h["year"] for h in hutbeler)
    meta["year_min"] = min(h["year"] for h in hutbeler)

    cat_count = Counter(h["primary_category"] for h in hutbeler)
    meta["overall_category"] = {"labels": CATS15, "values": [cat_count.get(c, 0) for c in CATS15]}
    meta["top_category"] = cat_count.most_common(1)[0][0]

    years = sorted(set(h["year"] for h in hutbeler))
    matrix = []
    for y in years:
        row_counts = Counter(h["primary_category"] for h in hutbeler if h["year"] == y)
        matrix.append([row_counts.get(c, 0) for c in CATS15])
    meta["yearly"] = {"years": years, "categories": CATS15, "matrix": matrix}

    sure_row_cnt = Counter(a["sure"] for a in ayetler)
    meta["top_suras"] = [{"name": s, "count": c} for s, c in sure_row_cnt.most_common(15)]
    verse_row_cnt = Counter((a["sure"], a["ayet"]) for a in ayetler)
    verse_quote = {(a["sure"], a["ayet"]): a["quote"] for a in ayetler}
    meta["top_verses"] = [{"label": f"{s} {v}", "count": c, "quote": verse_quote[(s, v)]} for (s, v), c in verse_row_cnt.most_common(20)]
    kaynak_row_cnt = Counter(h["kaynak"] for h in hadisler)
    meta["top_hadis_kaynak"] = [{"name": k, "count": c} for k, c in kaynak_row_cnt.most_common(15)]
    kw_row_cnt = Counter(k["keyword"] for k in kelimeler)
    meta["top_keywords"] = [{"keyword": kw, "count": c} for kw, c in kw_row_cnt.most_common(60)]
    top40 = [kw for kw, c in kw_row_cnt.most_common(40)]
    matrix_kw = []
    for kw in top40:
        row = {"keyword": kw, "total": kw_row_cnt[kw]}
        per_cat = Counter()
        for k in kelimeler:
            if k["keyword"] == kw: per_cat[k["category"]] += 1
        for c in CATS15: row[c] = per_cat.get(c, 0)
        matrix_kw.append(row)
    meta["keyword_category_matrix"] = matrix_kw

    json.dump(meta, open(meta_path, "w", encoding="utf-8"), ensure_ascii=False)
    print(f"meta.json güncellendi: total_hutbe={meta['total_hutbe']}, "
          f"total_ayet={meta['total_ayet']}, total_hadis={meta['total_hadis']}, "
          f"yıl aralığı {meta['year_min']}-{meta['year_max']}")

if __name__ == "__main__":
    print(__doc__)
