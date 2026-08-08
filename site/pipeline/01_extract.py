import fitz, re, json, glob, os
from collections import Counter

SRC_DIR = "/sessions/happy-trusting-turing/mnt/hutbe"
# Not (20.07.2026, İP-3 bulgusu): bazı sayfa başlıkları "TARİHİ :" yazım
# varyasyonunu veya "DD/MM/YYYY" slash-ayraçlı tarih biçimini kullanıyor
# (ör. "İLİ : GENEL TARİH : 09/03/2018", "İLİ : MUŞ TARİHİ : 25.08.2017").
# Eski desen (yalnız "TARİH" + nokta-ayraçlı tarih) bunları atlayıp art arda
# gelen haftaları tek kayıtta birleştiriyordu — bkz. arastirma_programi.md
# TaskList #16-18. Buradaki genişletme yalnız gelecekteki 01_extract.py
# çalıştırmaları içindir; mevcut site/data/metinler/*.json dosyaları ayrı
# bir betikle (07_fix_hidden_merges.py) doğrudan yamalanmıştır.
date_re = re.compile(r'(TARİH|Tarih)İ?\s*:\s*(\d{2})[./](\d{2})[./](\d{4})')

def get_entries(path):
    doc = fitz.open(path)
    entries = []
    current = None
    for page in doc:
        t = page.get_text("text")
        m = date_re.search(t)
        if m:
            if current:
                entries.append(current)
            current = {"date": f"{m.group(2)}.{m.group(3)}.{m.group(4)}", "pages": [t]}
        else:
            if current is not None:
                current["pages"].append(t)
    if current:
        entries.append(current)
    for e in entries:
        e["text"] = "\n".join(e["pages"])
        del e["pages"]
    return entries

def is_arabic(line):
    arabic_chars = sum(1 for c in line if '؀' <= c <= 'ۿ')
    return arabic_chars > len(line.strip()) * 0.3 if line.strip() else False

CITELIKE = re.compile(r"^[A-ZÇĞİÖŞÜ][a-zçğıöşüâîû'’.\- ]*,?\s*\d")

def is_title_line(s):
    if len(s) < 4 or len(s) > 90:
        return False
    if is_arabic(s):
        return False
    if CITELIKE.match(s):
        return False
    letters = [c for c in s if c.isalpha() and c != '﷽']
    if not letters:
        return False
    upper_ratio = sum(1 for c in letters if c.isupper()) / len(letters)
    return upper_ratio > 0.85

def extract_title(text):
    # v2 (03.08.2026, İP-7b): eğik çizgi ayraçlı tarihler ("31/07/2015") de
    # üstbilgi sınırı sayılmalı, yalnız nokta değil (bkz. 08_integrate_new_hutbe.py
    # extract_title_and_body_start aynı düzeltme).
    lines = text.split("\n")
    start_idx = 0
    for i, l in enumerate(lines[:12]):
        if re.search(r'\d{2}[./]\d{2}[./]\d{4}', l):
            start_idx = i + 1
    candidates = lines[start_idx:start_idx+80]
    for idx, l in enumerate(candidates):
        s = l.strip()
        if not s:
            continue
        if is_title_line(s):
            title_parts = [s]
            for j in range(idx+1, min(idx+3, len(candidates))):
                nxt = candidates[j].strip()
                if not nxt:
                    break
                if is_title_line(nxt) and len(nxt) < 60:
                    title_parts.append(nxt)
                else:
                    break
            return " ".join(title_parts)
    return ""

def get_footnotes(text):
    lines = text.split("\n")
    candidates = []
    for i, line in enumerate(lines):
        m = re.match(r'^\s*(\d{1,2})\s+([A-ZÇĞİÖŞÜ].{2,160})$', line.strip())
        if m:
            candidates.append((i, int(m.group(1)), m.group(2).strip()))
    footnotes = {}
    expected = 1
    for i, num, txt in candidates:
        if num == expected:
            footnotes[num] = txt
            expected += 1
        elif num == 1:
            footnotes = {1: txt}
            expected = 2
    return footnotes

# v2 (08.08.2026, İP-7b takip kök-neden düzeltmesi): bkz. 08_integrate_new_hutbe.py
# aynı isimli değişkenin yorumu -- eski desen tırnak içindeki Türkçe kesme
# işaretlerini (’) de sınır sayıp o alıntıyı baştan kaçırıyordu.
QUOTE_PAT = re.compile(r'“([^“”]{3,700})”\s*(\d{1,2})\b|‘([^‘’]{3,700})’\s*(\d{1,2})\b')

def extract_quotes(text):
    out = []
    for m in QUOTE_PAT.finditer(text):
        g_quote = m.group(1) if m.group(1) is not None else m.group(3)
        g_num = m.group(2) if m.group(1) is not None else m.group(4)
        quote = re.sub(r'\s+', ' ', g_quote).strip()
        num = int(g_num)
        out.append((quote, num))
    return out

all_entries = []
files = sorted(glob.glob(os.path.join(SRC_DIR, "*.pdf")))
for path in files:
    fname = os.path.basename(path)
    entries = get_entries(path)
    for e in entries:
        title = extract_title(e["text"])
        fn = get_footnotes(e["text"])
        quotes = extract_quotes(e["text"])
        cited = []
        for q, n in quotes:
            ref = fn.get(n)
            cited.append({"num": n, "quote": q, "ref": ref})
        all_entries.append({
            "source_file": fname,
            "date": e["date"],
            "title": title,
            "text": e["text"],
            "footnotes": fn,
            "citations": cited,
        })
    print(f"{fname}: {len(entries)} entries")

print("TOTAL:", len(all_entries))
titled = sum(1 for e in all_entries if e["title"])
print("Başlık bulunan:", titled, "/", len(all_entries))

with open("hutbeler_v2.json", "w", encoding="utf-8") as f:
    json.dump(all_entries, f, ensure_ascii=False, indent=1)
