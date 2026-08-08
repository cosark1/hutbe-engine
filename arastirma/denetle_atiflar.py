# -*- coding: utf-8 -*-
"""Ayet ve hadis atıflarını hutbe dipnotlarına karşı denetler ve düzeltir.

Kök neden
---------
ayet_tam_metin.csv / hadis_tam_metin.csv'deki atıfların bir kısmı, hutbe
metnindeki alıntının KENDİ dipnot numarasına değil, yakınındaki başka bir
dipnota bağlanmış. Dört ayrı arıza biçimi tespit edildi:

  1) Birleşik hutbe bloğu — eski metin çıkarımında birden çok hutbe tek kayıtta
     birleşmiş; dipnot numarası YANLIŞ hutbenin dipnot listesinde aranmış.
     (23.03.2018 "Ancak sana ibadet eder..." → Fâtiha 1/5 yerine Zümer 39/9;
      Zümer 39/9 bir sonraki hutbenin 3 numaralı dipnotu.)
  2) Dipnotsuz alıntı — hutbede dipnotu olmayan alıntıya (genelde kapanış
     duası) en yakın dipnot atanmış.
     (20.11.2015 "Rabbimiz! İlmimizi... artır" → İbrahim 14/3 diye etiketlenmiş;
      doğrusu Tâhâ 20/114, hutbede dipnotu yok.)
  3) Tür karışması — ayet dosyasında hadis dipnotlu satır (ve tersi).
  4) Kırpılmış bölüm adı — eski regex â/î/û harflerini tanımadığından
     "Rikâk" → "Rik", "Sıfatü'l-kıyâme" → "Sıfatü'l-kıy" gibi yarım kalmış.

Doğruluk kaynağı
----------------
Birincil: site/data/metinler/YYYY.json — doğru bölünmüş hutbe metinleri, her
birinin sonunda kendi dipnot listesi ("1 Buhârî, Cihâd, 128.  2 İsrâ, 17/53.").
İkincil: hutbeler_veriseti.csv — metinler'de bulunmayan (çoğu bayram) hutbeler
için; kayıtlar alt-hutbelere bölünüp her birinin kendi dipnot bloğu okunur.

Dipnot ayrıştırma ve sure/hadis kaynağı çözümleme mantığı
site/pipeline/07_fill_missing_citations.py'den aynen kullanılır; böylece
düzeltilmiş satırlar mevcut korpusla aynı kanonik biçimi korur.

Çalıştırma
----------
  python arastirma/denetle_atiflar.py            # denetle + rapor (yazmaz)
  python arastirma/denetle_atiflar.py --uygula   # düzeltilmiş CSV'leri yerine yaz
"""
import csv, difflib, importlib.util, json, os, re, shutil, sys, unicodedata
from collections import Counter, defaultdict

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MET = os.path.join(BASE, 'site', 'data', 'metinler')
OUT = os.path.join(BASE, 'arastirma', 'atif_denetimi')
csv.field_size_limit(10 ** 7)

# --- boru hattının kendi çözümleyicilerini yeniden kullan ---------------------
_spec = importlib.util.spec_from_file_location(
    'fillcit', os.path.join(BASE, 'site', 'pipeline', '07_fill_missing_citations.py'))
P = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(P)

get_footnotes, norm = P.get_footnotes, P.norm
NORM2CANON, NORM2HADITH = P.NORM2CANON, P.NORM2HADITH
SURE_REF_PAT, SURE_REF_PAT_NOSLASH = P.SURE_REF_PAT, P.SURE_REF_PAT_NOSLASH

# Boru hattındaki HADITH_LEAD_PAT üç durumu kaçırıyor:
#   (a) kaynak ile bölüm arasında virgül yok  -> "Tirmizi Birr, 15."
#   (b) eser adı "el-" ile başlıyor           -> "Taberânî, el-Mu'cemü'l-evsat, VII, 56."
#   (c) bölüm yerine cilt numarası var        -> "İbn Hanbel, II, 400."  (bölüm boş kalmalı)
# Ayrıca iki büyük harfli kelimeyle sınırlı olduğundan "Gusül ve Teyemmüm" gibi
# bağlaç içeren bölüm adlarını "Gusül"e kırpıyor. Bu yüzden denetimde regex
# yerine "en uzun bilinen kaynak adı + kalanın ilk öğesi" yaklaşımı kullanılır.
ROMAN = re.compile(r'^[IVXLC]+$')


def split_source(ref):
    """Dipnotun başındaki hadis kaynağını tanı; (kanonik_ad, kalan) döndür."""
    toks = [t for t in re.split(r'[\s,]+', ref) if t]
    for n in (3, 2, 1):
        if len(toks) < n:
            continue
        canon = NORM2HADITH.get(norm(' '.join(toks[:n])))
        if canon:
            rest = ref
            for t in toks[:n]:
                rest = rest.split(t, 1)[1] if t in rest else rest
            return canon, rest.lstrip(' ,.')
    return None, ''


def clean_bolum(rest):
    """Kalan metinden bölüm/eser adını al (cilt numarası bölüm sayılmaz)."""
    seg = re.split(r'[,;]', rest)[0].strip(' ,.:"“”')
    seg = re.sub(r'\s*\d[\d\s/\-]*$', '', seg).strip(' ,.:"“”')
    return '' if (not seg or ROMAN.match(seg)) else seg


def resolve_ref(ref):
    """Dipnot metnini ('ayet', sure, no) / ('hadis', kaynak, bolum) yapar."""
    if not ref:
        return None
    ref = ref.strip()
    m = SURE_REF_PAT.match(ref) or SURE_REF_PAT_NOSLASH.match(ref)
    if m:
        canon = NORM2CANON.get(norm(m.group(1)))
        if canon:
            try:
                return ('ayet', canon[1], str(int(m.group(m.lastindex))))
            except ValueError:
                pass
    first = re.split(r'\s*;\s*', ref)[0]
    canon, rest = split_source(first)
    if canon:
        return ('hadis', canon, clean_bolum(rest))
    return None


# --- alıntı çıkarımı ----------------------------------------------------------
# DİKKAT: kapanış tırnağından sonraki boşluğu serbest bırakmak, metnin son
# alıntısında dipnot LİSTESİNİN kendi "1" numarasını o alıntının işaretçisi
# sanmaya yol açar (20.11.2015 hutbesi tam olarak böyle yanlış "doğrulanıyordu").
# Bu yüzden işaretçi ile tırnak arasında satır sonu olamaz ve alıntı dipnot
# bloğunun başlangıcından önce bitmelidir.
# v2 (08.08.2026, İP-7b takip kök-neden düzeltmesi -- bkz. site/pipeline/
# 08_integrate_new_hutbe.py'deki aynı isimli yorum): eski desenin ortak içerik
# dışlama sınıfı ([^“”‘’"]) tırnak İÇİNDEKİ Türkçe kesme işaretlerini (’, ör.
# "Allah’ın") de sınır sayıp o alıntıyı baştan kaçırıyordu (07.08.2026
# "KARDEŞLİK" hutbesinde 3 ayet böyle kaçmıştı). Üç tırnak stili artık
# birbirinden bağımsız gruplarla eşleştiriliyor.
QUOTE_ANY = re.compile(
    r'“([^“”]{3,700})”[ \t]{0,3}(\d{0,2})'
    r'|‘([^‘’]{3,700})’[ \t]{0,3}(\d{0,2})'
    r'|"([^"]{3,700})"[ \t]{0,3}(\d{0,2})'
)


def get_footnotes_lenient(text):
    """1'den başlamayan dipnot blokları için toleranslı tarayıcı.

    Bazı hutbelerde (ör. 05.06.2015) dipnot bloğu altbilgiden SONRA geliyor ve
    ilk birkaç dipnot metin çıkarımında düşmüş: liste "6 Müslim, İmare, 57"
    ile başlıyor. Boru hattının tarayıcısı diziyi 1'den aramak zorunda olduğu
    için hiçbir dipnot bulamıyor. Burada dizinin herhangi bir sayıdan
    başlamasına izin verilir; katı tarayıcının sonucu her zaman önceliklidir.
    """
    tail = text[max(0, len(text) - 3000):]
    cands = [(m.start(1), int(m.group(1))) for m in P.MARKER_RE.finditer(tail)]
    best = []
    for i, (pos, num) in enumerate(cands):
        run, expected, last = [(pos, num)], num + 1, pos
        for p2, n2 in cands[i + 1:]:
            if n2 == expected and p2 - last <= P.FOOTNOTE_MAX_GAP:
                run.append((p2, n2)); expected += 1; last = p2
        if len(run) > len(best):
            best = run
    if len(best) < 2:
        return {}
    pos_list = [p for p, n in best] + [len(tail)]
    out = {}
    for i, (p, n) in enumerate(best):
        seg = tail[pos_list[i]:pos_list[i + 1]]
        mm = re.match(r'\d{1,2}\s+(.*)', seg, re.DOTALL)
        if not mm:
            continue
        ref = mm.group(1).strip()
        ft = P.FOOTER_TRIGGER_RE.search(ref)
        if ft:
            ref = ref[:ft.start()].strip()
        if len(ref) <= 200:
            out[n] = ref
    return out


def footnote_block_start(text):
    """Dipnot listesinin metindeki başlangıç konumu (yoksa len(text))."""
    off = max(0, len(text) - 3000)
    tail = text[off:]
    cands = [(m.start(1), int(m.group(1))) for m in P.MARKER_RE.finditer(tail)]
    best = []
    for i, (pos, num) in enumerate(cands):
        if num != 1:
            continue
        run, expected, last = [(pos, num)], 2, pos
        for p2, n2 in cands[i + 1:]:
            if n2 == expected and p2 - last <= P.FOOTNOTE_MAX_GAP:
                run.append((p2, n2)); expected += 1; last = p2
        if len(run) > len(best):
            best = run
    return off + best[0][0] if best else len(text)


def extract_quotes_all(text):
    limit = footnote_block_start(text)
    out = []
    for m in QUOTE_ANY.finditer(text):
        if m.start() >= limit:
            break
        for gi in (1, 3, 5):
            if m.group(gi) is not None:
                g_txt, g_mk = m.group(gi), m.group(gi + 1)
                break
        q = re.sub(r'\s+', ' ', g_txt).strip()
        mk = g_mk
        if mk and m.end() > limit:
            mk = None
        out.append((q, int(mk) if mk else None))
    return out


def gun(tarih):
    """gg.aa.yyyy -> sıralanabilir gün sayısı (tarih yakınlığı karşılaştırması için)."""
    try:
        g, a, y = (int(x) for x in tarih.split('-')[0].split('.'))
        return y * 372 + a * 31 + g
    except Exception:
        return 0


def qnorm(s):
    s = s.replace('’', "'").replace('‘', "'")
    s = re.sub(r'[^\w\s]', ' ', s, flags=re.UNICODE)
    return ' '.join(s.lower().split())


def tnorm(s):
    s = (s or '').lower().replace('İ', 'i')
    s = unicodedata.normalize('NFKD', s)
    s = ''.join(c for c in s if not unicodedata.combining(c))
    return re.sub(r'[^a-z0-9]', '', s)


# --- korpus: metinler (birincil) + veriseti alt-hutbeleri (ikincil) -----------
HDR = re.compile(r'(?:İL[İI]\s*\n?\s*:?\s*[^\n]{0,20}\n\s*)?TAR[İI]H[İI]?\s*\n?\s*:?\s*\n?\s*(\d{2}[./]\d{2}[./]\d{4})')
HDR_LINE = re.compile(r'TAR[İI]H|İL[İI]\b|^\s*:|GENEL|^\s*\d|HAZIRLAYAN|D[İI]N H[İI]ZMETLER[İI]|BAŞKANLI', re.I)


def title_after(seg):
    """Başlık PDF'te iki satıra bölünmüş olabilir; ardışık büyük harfli satırları birleştir."""
    parts = []
    for line in seg.split('\n')[:22]:
        t = ' '.join(line.split())
        if not t:
            if parts:
                break
            continue
        if HDR_LINE.search(t) or len(t) > 130:
            if parts:
                break
            continue
        letters = [c for c in t if c.isalpha()]
        if letters and sum(1 for c in letters if c.isupper()) / len(letters) > 0.75:
            parts.append(t)
        elif parts:
            break
    return ' '.join(parts)


def split_record(text, fallback_date):
    hs = [m.start() for m in HDR.finditer(text)]
    if not hs:
        return [(fallback_date, text)]
    hs.append(len(text))
    out = []
    for i in range(len(hs) - 1):
        seg = text[hs[i]:hs[i + 1]]
        d = HDR.search(seg)
        out.append((d.group(1).replace('/', '.') if d else fallback_date, seg))
    return out


def load_corpus():
    """{(tarih, baslik_norm): {tarih, baslik, text, kaynak}} ve tarih->kayıt listesi."""
    hutbe = []
    for fn in sorted(os.listdir(MET)):
        if not re.fullmatch(r'\d{4}\.json', fn):
            continue
        for key, rec in json.load(open(os.path.join(MET, fn), encoding='utf-8')).items():
            hutbe.append(dict(anahtar=key, tarih=key.split('-')[0], baslik=rec['title'],
                              text=rec['text'], kaynak='metinler'))
    have = {(h['tarih'], tnorm(h['baslik'])) for h in hutbe}
    have_date = {h['tarih'] for h in hutbe}

    # Bu dört (tarih, kırpık-başlık) çifti split_record()/title_after()'ın metin
    # ortasından yanlışlıkla yakaladığı sahte parçalardır -- gerçek ikinci hutbe
    # değil, metinler'de zaten var olan TEK hutbenin bir fragmanı (İP-7b PDF
    # sayfa-bazlı doğrulamasıyla 03.08.2026'da elendi, bkz. RAPOR.md §6).
    SAHTE_EK = {('13.04.2018', 'olmacabasi'), ('20.09.2019', 'a'),
                ('15.07.2022', 'birlikveberaberliginzaferi'), ('12.07.2024', 'zaferi')}

    ek = 0
    for r in csv.DictReader(open(os.path.join(BASE, 'hutbeler_veriseti.csv'), encoding='utf-8-sig')):
        for d, seg in split_record(r['text'], r['date']):
            t = title_after(seg)
            if not t or len(seg) < 1200:
                continue
            tn = tnorm(t)
            if (d, tn) in have or (d, tn) in SAHTE_EK:
                continue
            # metinler'deki aynı tarihli başlıklardan biriyle önek ilişkisi varsa
            # bu, PDF'te satıra bölünmüş aynı başlıktır -> yeni hutbe değildir
            if any(hd == d and (tn.startswith(hn) or hn.startswith(tn)) and min(len(tn), len(hn)) >= 10
                   for hd, hn in have):
                continue
            hutbe.append(dict(anahtar=f'{d}~ek', tarih=d, baslik=t, text=seg, kaynak='veriseti'))
            ek += 1
    return hutbe, ek


class Corpus:
    def __init__(self):
        self.hutbe, self.ek_sayisi = load_corpus()
        for h in self.hutbe:
            h['quotes'] = extract_quotes_all(h['text'])
            fn = dict(get_footnotes_lenient(h['text']))
            fn.update(get_footnotes(h['text']))   # katı tarayıcı önceliklidir
            h['fn'] = fn
        self.by_date = defaultdict(list)
        for h in self.hutbe:
            self.by_date[h['tarih']].append(h)
        self.inv = defaultdict(set)
        for hi, h in enumerate(self.hutbe):
            for qi, (txt, _) in enumerate(h['quotes']):
                for w in {w for w in qnorm(txt).split() if len(w) > 4}:
                    self.inv[w].add((hi, qi))

    def pick_hutbe(self, tarih, baslik):
        """CSV satırının ait olduğu hutbeyi (tarih, başlık) ile bul."""
        cands = self.by_date.get(tarih, [])
        if not cands:
            return None, 'tarih_korpusta_yok'
        tn = tnorm(baslik)
        for h in cands:                                    # tam başlık eşleşmesi
            if tnorm(h['baslik']) == tn:
                return h, 'baslik_eslesti'
        for h in cands:                                    # satıra bölünmüş başlık
            hn = tnorm(h['baslik'])
            if min(len(tn), len(hn)) >= 10 and (tn.startswith(hn) or hn.startswith(tn)):
                return h, 'baslik_onek'
        if len(cands) == 1:
            return cands[0], 'baslik_uyusmadi_tek_aday'
        return None, 'baslik_uyusmadi'

    def find_quote(self, h, q):
        qn = qnorm(q)
        best, bestr = None, 0.0
        for txt, mk in h['quotes']:
            r = difflib.SequenceMatcher(None, qnorm(txt), qn).ratio()
            if r > bestr:
                bestr, best = r, (txt, mk)
        return best, bestr

    def find_global(self, q, ref_date=None):
        """Alıntıyı tüm korpusta ara.

        Yaygın hadis/ayetler onlarca hutbede geçtiğinden en yüksek benzerlik
        tek başına yeterli ölçüt değil. Bu arıza birleşik PDF kaydından doğduğu
        için gerçek hutbe, kaydedilen tarihe yakın olur; bu yüzden benzerlikçe
        yarışan adaylar arasında tarihe en yakın olan seçilir.
        """
        qn = qnorm(q)
        cand = Counter()
        for w in {w for w in qn.split() if len(w) > 4}:
            for key in self.inv.get(w, ()):
                cand[key] += 1
        scored = []
        for (hi, qi), _ in cand.most_common(120):
            txt, mk = self.hutbe[hi]['quotes'][qi]
            r = difflib.SequenceMatcher(None, qnorm(txt), qn).ratio()
            scored.append((r, hi, (txt, mk)))
        if not scored:
            return None, 0.0, None
        top = max(s[0] for s in scored)
        yakin = [s for s in scored if s[0] >= max(top - 0.10, GLOBAL_ESIK)]
        if ref_date and yakin:
            yakin.sort(key=lambda s: (abs(gun(self.hutbe[s[1]]['tarih']) - gun(ref_date)), -s[0]))
            r, hi, best = yakin[0]
            return best, r, self.hutbe[hi]
        r, hi, best = max(scored, key=lambda s: s[0])
        return best, r, self.hutbe[hi]


# --- denetim ------------------------------------------------------------------
SPEC = {
    'ayet': dict(path='ayet_tam_metin.csv', qcol='ayet_meali_hutbede_gecen',
                 keys=('sure', 'ayet_no'), tur='ayet'),
    'hadis': dict(path='hadis_tam_metin.csv', qcol='hadis_meali_hutbede_gecen',
                  keys=('kaynak', 'bolum'), tur='hadis'),
}
ESIK = 0.60
# Alıntı kendi hutbesinde bulunamazsa korpus geneli aranır. Bu eşik kasten
# yüksek: yaygın hadisler (ör. "amellerin en sevimlisi az da olsa devamlı
# olanıdır") onlarca hutbede geçtiğinden, zayıf bir benzerlik satırı yanlış
# hutbeye taşıyıp onun dipnotunu yapıştırabilir.
GLOBAL_ESIK = 0.75


def canon_old(kind, a, b):
    if kind == 'ayet':
        c = NORM2CANON.get(norm(a or ''))
        return ((c[1] if c else (a or '').strip()), re.sub(r'\D', '', b or ''))
    c = NORM2HADITH.get(norm(a or ''))
    return ((c if c else (a or '').strip()), (b or '').strip())


def siniflandir(kind, old, new):
    """Gerçek yanlış atıf mı, yoksa eski regex'in bıraktığı biçim kusuru mu?

    Kaynak/sure farklıysa gerçek yanlış atıftır. Aynı kaynağın bölüm adındaki
    kırpılma, eksiklik veya yazım farkı ayrı sayılır ki gerçek hata sayısı
    şişmesin.
    """
    if old[0] != new[0] or kind == 'ayet':
        return 'HATALI'
    ob, nb = old[1], new[1]
    on, nn = norm(ob), norm(nb)
    if not ob or ob == '-':
        return 'eksik_tamamlandi'
    # normalize_bolum_adlari.py, Ahmed b. Hanbel'in cilt/sayfa referanslı
    # (bölümsüz) dipnotlarında görüntü kolaylığı için bölümü "Müsned" yazar;
    # dipnottan çıkan boş bölümle eşleşmemesi beklenir, hata değildir.
    if old[0].startswith('Ahmed b. Hanbel') and ob == 'Müsned' and not nb:
        return 'dogru'
    if ROMAN.match(ob) and not nb:
        return 'cilt_temizlendi'      # "II" bir bölüm adı değil, cilt numarası
    if nn and on and nn.startswith(on):
        return 'kirpilmis_duzeltildi'  # "Rik" -> "Rikâk"
    if nn and on and (on in nn or nn in on):
        return 'yazim_farki'           # "Mu'cemü'l-evsat" -> "el-Mu'cemü'l-evsat"
    return 'HATALI'


def audit(kind, C):
    sp = SPEC[kind]
    ka, kb = sp['keys']
    rows = list(csv.DictReader(open(os.path.join(BASE, sp['path']), encoding='utf-8-sig')))
    out = []
    for r in rows:
        rec = dict(durum='', skor='', dipnot_no='', dipnot_ref='', yeni_a='', yeni_b='',
                   hutbe='', esleme='', kaynak='')
        h, how = C.pick_hutbe(r['tarih'], r['hutbe_basligi'])
        rec['esleme'] = how

        if h is None:
            best, ratio, h2 = C.find_global(r[sp['qcol']])
            if h2 is None or ratio < ESIK:
                rec['durum'] = 'hutbe_bulunamadi'
                out.append((r, rec)); continue
            h, best_pair, ratio = h2, best, ratio
            rec['esleme'] = how + '+korpus_taramasi'
        else:
            best_pair, ratio = C.find_quote(h, r[sp['qcol']])
            if ratio < ESIK:
                # Alıntı atandığı hutbede yok: eski çıkarım birleşik kayıtta
                # sonraki hutbenin alıntısını ilkinin tarihi altına yazmış.
                gbest, gratio, gh = C.find_global(r[sp['qcol']], r['tarih'])
                if gh is not None and gratio >= GLOBAL_ESIK:
                    h, best_pair, ratio = gh, gbest, gratio
                    rec['esleme'] = how + '+tarih_duzeltildi'

        rec['hutbe'] = f"{h['tarih']} {h['baslik'][:40]}"
        rec['kaynak'] = h['kaynak']
        rec['skor'] = round(ratio, 3)
        if best_pair is None or ratio < ESIK:
            rec['durum'] = 'alinti_bulunamadi'
            out.append((r, rec)); continue

        mk = best_pair[1]
        if mk is None:
            rec['durum'] = 'dipnotsuz'
            out.append((r, rec)); continue

        ref = h['fn'].get(mk)
        rec['dipnot_no'], rec['dipnot_ref'] = mk, ref or ''
        res = resolve_ref(ref)
        if res is None:
            rec['durum'] = 'dipnot_bulunamadi' if not ref else 'ref_cozulemedi'
            out.append((r, rec)); continue

        rec['yeni_a'], rec['yeni_b'] = res[1], res[2]
        if res[0] != sp['tur']:
            rec['durum'] = 'tur_hatasi'
            out.append((r, rec)); continue

        old = canon_old(kind, r[ka], r[kb])
        new = (res[1], re.sub(r'\D', '', res[2]) if kind == 'ayet' else res[2])
        rec['durum'] = 'dogru' if old == new else siniflandir(kind, old, new)
        out.append((r, rec))
    return rows, out


# --- düzeltilmiş CSV üretimi --------------------------------------------------
DUZELTEN = {'HATALI', 'kirpilmis_duzeltildi', 'eksik_tamamlandi', 'cilt_temizlendi', 'yazim_farki'}


def elle_kararlar():
    yol = os.path.join(OUT, 'elle_kararlar.csv')
    if not os.path.exists(yol):
        return {}
    out = {}
    for r in csv.DictReader(open(yol, encoding='utf-8-sig')):
        out[(r['dosya'], int(r['satir']))] = r
    return out


def temalar():
    """tarih -> ana_tema (hutbe_kategori_analizi.csv, 15'li şema)."""
    yol = os.path.join(BASE, 'hutbe_kategori_analizi.csv')
    if not os.path.exists(yol):
        return {}
    return {r['tarih']: r['ana_tema'] for r in csv.DictReader(open(yol, encoding='utf-8-sig'))}


def duzelt(kind, res, kararlar, tema_map):
    """Denetim sonucundan düzeltilmiş satır listesi + taşınacak satırlar üretir."""
    sp = SPEC[kind]
    ka, kb = sp['keys']
    tutulan, tasinan, log = [], [], []
    for i, (r, rec) in enumerate(res, start=2):
        yeni = dict(r)
        k = kararlar.get((kind, i))
        eylem = ''

        if k and k['karar'] == 'sil':
            log.append((i, 'sil', f"{r[ka]},{r[kb]}", '', k['gerekce']))
            continue
        if k and k['karar'] in ('duzelt', 'koru'):
            if k['karar'] == 'duzelt':
                yeni[ka], yeni[kb] = k['yeni_a'], k['yeni_b']
                eylem = 'elle_duzeltildi'
            if k.get('yeni_tarih'):
                yeni['tarih'] = k['yeni_tarih']
                h = next(iter(C_GLOBAL.by_date.get(k['yeni_tarih'], [])), None)
                if h:
                    yeni['hutbe_basligi'] = h['baslik']
                yeni['tema'] = tema_map.get(k['yeni_tarih'], yeni['tema'])
        elif rec['durum'] == 'tur_hatasi':
            tasinan.append((rec, r))
            log.append((i, 'tasindi', f"{r[ka]},{r[kb]}",
                        f"{rec['yeni_a']},{rec['yeni_b']}", 'tür karışması: diğer dosyaya taşındı'))
            continue
        elif rec['durum'] in DUZELTEN:
            yeni[ka], yeni[kb] = rec['yeni_a'], rec['yeni_b']
            eylem = rec['durum']

        # Alıntı başka hutbeye aitse tarih/başlık/tema da düzeltilir. Elle karar
        # verilmiş satırlarda otomatik taşıma uygulanmaz: bu satırların doğru
        # hutbesi zaten insan tarafından belirlenmiştir (ör. s501 Berat hadisi
        # korpusta birden çok hutbede geçtiği için otomatik eşleşme güvenilmez).
        if not k and rec.get('esleme', '').endswith('tarih_duzeltildi') and rec['hutbe']:
            gt = rec['hutbe'].split(' ', 1)[0]
            if gt != r['tarih']:
                yeni['tarih'] = gt
                h = next((x for x in C_GLOBAL.by_date.get(gt, [])), None)
                if h:
                    yeni['hutbe_basligi'] = h['baslik']
                if gt in tema_map:
                    yeni['tema'] = tema_map[gt]
                eylem = (eylem + '+' if eylem else '') + 'tarih_duzeltildi'

        if eylem:
            log.append((i, eylem, f"{r[ka]},{r[kb]}", f"{yeni[ka]},{yeni[kb]}",
                        (k or {}).get('gerekce', '') or rec['dipnot_ref']))
        tutulan.append(yeni)
    return tutulan, tasinan, log


def yaz_csv(kind, rows, gelen, tema_map):
    """Düzeltilmiş CSV'yi kac_kez yeniden hesaplayarak yaz."""
    sp = SPEC[kind]
    ka, kb = sp['keys']
    oteki = SPEC['ayet' if kind == 'hadis' else 'hadis']['qcol']
    for rec, src in gelen:                       # diğer dosyadan taşınan satırlar
        gt = rec['hutbe'].split(' ', 1)[0] if rec['hutbe'] else src['tarih']
        h = next(iter(C_GLOBAL.by_date.get(gt, [])), None)
        rows.append({ka: rec['yeni_a'], kb: rec['yeni_b'], 'kac_kez': '',
                     sp['qcol']: src[oteki],
                     'tema': tema_map.get(gt, src['tema']), 'tarih': gt,
                     'hutbe_basligi': h['baslik'] if h else src['hutbe_basligi']})

    say = Counter((r[ka], r[kb]) for r in rows)
    for r in rows:
        r['kac_kez'] = say[(r[ka], r[kb])]
    rows.sort(key=lambda r: (-say[(r[ka], r[kb])], r[ka], str(r[kb]), r['tarih']))

    yol = os.path.join(BASE, sp['path'])
    yedek = yol + '.bak-preAtifDenetimi'
    if not os.path.exists(yedek):
        shutil.copy2(yol, yedek)
    cols = [ka, kb, 'kac_kez', sp['qcol'], 'tema', 'tarih', 'hutbe_basligi']
    with open(yol, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction='ignore')
        w.writeheader()
        w.writerows(rows)
    return len(rows)


# --- site/data/{ayetler,hadisler}.json denetimi -------------------------------
# Bu dosyalar CSV'lerin üst kümesi: 07_fill_missing_citations.py, atfı hiç
# olmayan hutbeler için satır EKLEMİŞ ama mevcut (hatalı) satırlara dokunmamış.
# Bu yüzden CSV'den yeniden üretilemezler; aynı denetimden geçirilirler.
JSPEC = {
    'ayet': dict(path='ayetler.json', keys=('sure', 'ayet'), tur='ayet'),
    'hadis': dict(path='hadisler.json', keys=('kaynak', 'bolum'), tur='hadis'),
}


def elle_kararlar_json(kind, kararlar):
    """Elle kararları JSON satırlarına bağlamak için alıntı metnine göre indeksle.

    CSV'de kararlar satır numarasıyla tutuluyor; JSON'da satır numarası yok, bu
    yüzden ilgili CSV satırının alıntı metni anahtar olarak kullanılır.
    """
    yedek = os.path.join(BASE, SPEC[kind]['path'] + '.bak-preAtifDenetimi')
    kaynak = yedek if os.path.exists(yedek) else os.path.join(BASE, SPEC[kind]['path'])
    satirlar = list(csv.DictReader(open(kaynak, encoding='utf-8-sig')))
    out = []
    for (dosya, satir), k in kararlar.items():
        if dosya != kind or satir - 2 >= len(satirlar):
            continue
        out.append((qnorm(satirlar[satir - 2][SPEC[kind]['qcol']]), k))
    return out


def audit_json(kind, C, tema_map, kararlar):
    sp = JSPEC[kind]
    ka, kb = sp['keys']
    yol = os.path.join(BASE, 'site', 'data', sp['path'])
    data = json.load(open(yol, encoding='utf-8'))
    elle = elle_kararlar_json(kind, kararlar)
    sonuc, log, tasinan = [], [], []
    for i, r in enumerate(data):
        # elle karara bağlanmış satırlar otomatik çözümlemeyi ezer
        qn = qnorm(r['quote'])
        k = next((k for eq, k in elle
                  if difflib.SequenceMatcher(None, eq, qn).ratio() >= 0.90), None)
        if k is not None:
            if k['karar'] == 'sil':
                log.append((i, 'sil', f"{r.get(ka)},{r.get(kb)}", '', k['gerekce']))
                continue
            if k['karar'] == 'duzelt':
                yeni = dict(r)
                yeni[ka] = int(re.sub(r'\D', '', k['yeni_b']) or 0) if kind == 'ayet' else k['yeni_a']
                if kind == 'ayet':
                    yeni['sure'], yeni['ayet'] = k['yeni_a'], int(re.sub(r'\D', '', k['yeni_b']) or 0)
                else:
                    yeni['kaynak'], yeni['bolum'] = k['yeni_a'], k['yeni_b']
                if k.get('yeni_tarih'):
                    h2 = next(iter(C.by_date.get(k['yeni_tarih'], [])), None)
                    yeni['date'] = k['yeni_tarih']
                    if h2:
                        yeni['title'] = h2['baslik']
                    yeni['category'] = tema_map.get(k['yeni_tarih'], yeni.get('category', ''))
                log.append((i, 'elle_duzeltildi', f"{r.get(ka)},{r.get(kb)}",
                            f"{k['yeni_a']},{k['yeni_b']}", k['gerekce']))
                sonuc.append(yeni)
            else:
                sonuc.append(r)
            continue
        h, how = C.pick_hutbe(r['date'], r.get('title', ''))
        best, ratio = (None, 0.0)
        if h is not None:
            best, ratio = C.find_quote(h, r['quote'])
            if ratio < ESIK:
                gb, gr, gh = C.find_global(r['quote'], r['date'])
                if gh is not None and gr >= GLOBAL_ESIK:
                    h, best, ratio, how = gh, gb, gr, how + '+tarih_duzeltildi'
        if h is None or best is None or ratio < ESIK or best[1] is None:
            sonuc.append(r); continue

        res = resolve_ref(h['fn'].get(best[1]))
        if res is None:
            sonuc.append(r); continue

        yeni = dict(r)
        eski = (str(r.get(ka, '')), str(r.get(kb, '')))
        if res[0] != sp['tur']:
            tasinan.append((res, r, h))
            log.append((i, 'tasindi', f'{eski[0]},{eski[1]}', f'{res[1]},{res[2]}', 'tür karışması'))
            continue
        yeni[ka] = res[1]
        yeni[kb] = int(re.sub(r'\D', '', res[2]) or 0) if kind == 'ayet' else res[2]
        if how.endswith('tarih_duzeltildi'):
            yeni['date'], yeni['title'] = h['tarih'], h['baslik']
            yeni['category'] = tema_map.get(h['tarih'], r.get('category', ''))
        if (str(yeni[ka]), str(yeni[kb])) != eski or yeni.get('date') != r['date']:
            log.append((i, 'duzeltildi', f'{eski[0]},{eski[1]}',
                        f'{yeni[ka]},{yeni[kb]}', h['fn'].get(best[1], '')))
        sonuc.append(yeni)
    return data, sonuc, tasinan, log


def yaz_json(kind, sonuc, gelen, tema_map):
    sp = JSPEC[kind]
    ka, kb = sp['keys']
    for res, src, h in gelen:
        yeni = dict(src)
        yeni.pop('sure', None); yeni.pop('ayet', None)
        yeni.pop('kaynak', None); yeni.pop('bolum', None)
        yeni[ka] = res[1]
        yeni[kb] = int(re.sub(r'\D', '', res[2]) or 0) if kind == 'ayet' else res[2]
        sonuc.append(yeni)
    say = Counter((str(r.get(ka)), str(r.get(kb))) for r in sonuc)
    for r in sonuc:
        r['count'] = say[(str(r.get(ka)), str(r.get(kb)))]
    yol = os.path.join(BASE, 'site', 'data', sp['path'])
    yedek = yol + '.bak-preAtifDenetimi'
    if not os.path.exists(yedek):
        shutil.copy2(yol, yedek)
    json.dump(sonuc, open(yol, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    return len(sonuc)


C_GLOBAL = None


def main():
    global C_GLOBAL
    os.makedirs(OUT, exist_ok=True)
    C = Corpus()
    C_GLOBAL = C
    print(f"hutbe: {len(C.hutbe)} (metinler + {C.ek_sayisi} ek) | "
          f"dipnotu okunan: {sum(1 for h in C.hutbe if h['fn'])}")

    kararlar, tema_map = elle_kararlar(), temalar()
    ozet, duzeltilmis = {}, {}
    for kind in ('ayet', 'hadis'):
        sp = SPEC[kind]
        ka, kb = sp['keys']
        rows, res = audit(kind, C)
        c = Counter(rec['durum'] for _, rec in res)
        ozet[kind] = dict(toplam=len(rows), dagilim=dict(c))
        duzeltilmis[kind] = duzelt(kind, res, kararlar, tema_map)
        print(f'\n=== {kind} ({len(rows)} satır) ===')
        for k, v in c.most_common():
            print(f'  {k:24s} {v}')

        with open(os.path.join(OUT, f'{kind}_denetim.csv'), 'w', encoding='utf-8-sig', newline='') as f:
            w = csv.writer(f)
            w.writerow(['satir', 'durum', 'skor', f'eski_{ka}', f'eski_{kb}', f'yeni_{ka}', f'yeni_{kb}',
                        'dipnot_no', 'dipnot_ref', 'csv_tarih', 'hutbe', 'metin_kaynagi', 'esleme', 'alinti'])
            for i, (r, rec) in enumerate(res, start=2):
                w.writerow([i, rec['durum'], rec['skor'], r[ka], r[kb], rec['yeni_a'], rec['yeni_b'],
                            rec['dipnot_no'], rec['dipnot_ref'], r['tarih'], rec['hutbe'],
                            rec['kaynak'], rec['esleme'], r[sp['qcol']]])
        print(f'  -> arastirma/atif_denetimi/{kind}_denetim.csv')

    # değişiklik günlüğü
    with open(os.path.join(OUT, 'degisiklik_gunlugu.csv'), 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f)
        w.writerow(['dosya', 'satir', 'eylem', 'eski', 'yeni', 'gerekce'])
        for kind in ('ayet', 'hadis'):
            for satir, eylem, eski, yeni, ger in duzeltilmis[kind][2]:
                w.writerow([kind, satir, eylem, eski, yeni, ger])

    print('\n=== düzeltme özeti ===')
    for kind in ('ayet', 'hadis'):
        tut, tas, log = duzeltilmis[kind]
        e = Counter(x[1] for x in log)
        print(f'  {kind}: {len(log)} satır değişti  ' + ', '.join(f'{k}={v}' for k, v in e.most_common()))
    json.dump(ozet, open(os.path.join(OUT, 'ozet.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)

    # site/data JSON denetimi
    jres = {k: audit_json(k, C, tema_map, kararlar) for k in ('ayet', 'hadis')}
    print('\n=== site/data JSON ===')
    for kind in ('ayet', 'hadis'):
        data, sonuc, tas, log = jres[kind]
        e = Counter(x[1] for x in log)
        print(f'  {JSPEC[kind]["path"]}: {len(data)} satır, {len(log)} değişiklik  '
              + ', '.join(f'{k}={v}' for k, v in e.most_common()))
        with open(os.path.join(OUT, f'site_{kind}_degisiklik.csv'), 'w',
                  encoding='utf-8-sig', newline='') as f:
            w = csv.writer(f)
            w.writerow(['indeks', 'eylem', 'eski', 'yeni', 'dipnot_ref'])
            w.writerows(log)

    if '--uygula' not in sys.argv:
        print('\n(deneme çalışması — dosya yazılmadı; yazmak için --uygula)')
        return
    for kind in ('ayet', 'hadis'):
        gelen = duzeltilmis['hadis' if kind == 'ayet' else 'ayet'][1]
        n = yaz_csv(kind, duzeltilmis[kind][0], gelen, tema_map)
        print(f'  yazıldı: {SPEC[kind]["path"]} ({n} satır)')
    for kind in ('ayet', 'hadis'):
        n = yaz_json(kind, jres[kind][1], jres['hadis' if kind == 'ayet' else 'ayet'][2], tema_map)
        print(f'  yazıldı: site/data/{JSPEC[kind]["path"]} ({n} satır)')


if __name__ == '__main__':
    main()
