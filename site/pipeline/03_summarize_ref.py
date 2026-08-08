import json, re

SALUT_PAT = re.compile(r'^\s*((?:Aziz|Muhterem|Kıymetli|Değerli|Sevgili)\s+(?:Müslümanlar|Müminler|Kardeşlerim|Mü’minler|Müminlerim)\s*!)\s*')
SENT_SPLIT = re.compile(r'(?<!\bHz)(?<!\bs\.a\.s)(?<=[.!?…”"\'])\s+(?=[A-ZÇĞİÖŞÜ“"\'])')

def split_sentences(paragraph):
    p = SALUT_PAT.sub('', paragraph).strip()
    if not p:
        return []
    sents = SENT_SPLIT.split(p)
    return [s.strip() for s in sents if s.strip()]

def strip_footnote_num(s):
    return re.sub(r'(?<=[.!?…”"\'])\d{1,2}\b\s*$', '', s).strip()

def trim(s, maxlen=230):
    s = strip_footnote_num(s.strip())
    if len(s) <= maxlen:
        return s
    cut = s[:maxlen]
    last_space = cut.rfind(' ')
    if last_space > 100:
        cut = cut[:last_space]
    return cut + "…"

FOOTER_PAT = re.compile(r'(Din Hizmetleri Genel Müdürlüğü|Hazırlayan\b|D\.İ\.B\.|Diyanet İşleri Başkanlığı|Hutbe Komisyonu)', re.I)

def summarize(text):
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    FOOTNOTE_SEQ = re.compile(r'(?:^|\s)[1-9]\d?\s+[A-ZÇĞİÖŞÜ]')
    def is_footnote_block(p):
        return len(FOOTNOTE_SEQ.findall(p)) >= 2
    # drop trailing footer / footnote-list paragraphs
    while paragraphs and (FOOTER_PAT.search(paragraphs[-1]) or is_footnote_block(paragraphs[-1])):
        paragraphs.pop()
    if not paragraphs:
        return ""
    # sentence1: thesis - first sentence of 2nd paragraph if available, else 1st paragraph's 2nd sentence, else 1st sentence
    sent1 = None
    if len(paragraphs) >= 2:
        s = split_sentences(paragraphs[1])
        if s:
            sent1 = s[0]
    if not sent1:
        s = split_sentences(paragraphs[0])
        sent1 = s[1] if len(s) > 1 else (s[0] if s else "")

    # sent3: closing - last sentence of last paragraph
    last_sents = split_sentences(paragraphs[-1])
    sent3 = last_sents[-1] if last_sents else ""

    # sent2: development - first sentence of a middle paragraph, avoiding duplicate of sent1/sent3
    sent2 = ""
    if len(paragraphs) >= 3:
        mid_idx = min(len(paragraphs)-2, max(2, len(paragraphs)//2))
        for idx in [mid_idx] + list(range(2, len(paragraphs)-1)):
            s = split_sentences(paragraphs[idx])
            if s and s[0] not in (sent1, sent3):
                sent2 = s[0]
                break

    parts = [trim(s) for s in [sent1, sent2, sent3] if s]
    # dedupe while preserving order
    seen = set()
    final = []
    for p in parts:
        if p not in seen:
            seen.add(p)
            final.append(p)
    return " ".join(final)

if __name__ == "__main__":
    d = json.load(open("dashboard_data7.json"))
    for date in ["22.08.2025", "15.04.2011"]:
        rec = d["full_texts"].get(date)
        if rec:
            print("===", date, rec["title"], "===")
            print(summarize(rec["text"]))
            print()
