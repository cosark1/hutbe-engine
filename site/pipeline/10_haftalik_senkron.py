# -*- coding: utf-8 -*-
"""Haftalık hutbe senkronu — mekanik adımlar. (Yargı gerektiren adımlar — korpus
etiketlemesi ve Kahutbe soruları — ajanın işi; bkz. HAFTALIK_RUTIN.md.)

KAYNAK NEDEN diyanethaber.com.tr (dinhizmetleri.diyanet.gov.tr değil):
  dinhizmetleri.diyanet.gov.tr/robots.txt `Disallow: /kategoriler/` diyor ve hutbe
  listesi tam o yolun altında. Proje kuralı gereği (hafıza: feedback_robots_txt_gate)
  bu eleyici bir bulgu, etrafından dolaşılmaz. Diyanet'in resmî haber ajansı
  diyanethaber.com.tr aynı hutbeleri RSS'le yayımlıyor, robots.txt'i /hutbeler ve
  /rss yollarına izin veriyor, PDF'ler teimg.com CDN'inde (robots: Allow /).
  25.09.2026'da doğrulandı: CDN'deki Kardeşlik PDF'i resmî PDF'le sha256 düzeyinde AYNI.

ALT KOMUTLAR
  durum                  RSS'i okur; korpusta ve Kahutbe'de eksik olanları listeler.
  indir                  Korpusta eksik hutbelerin PDF'ini {yıl}/ klasörüne indirir,
                         PDF içindeki "Tarih:" satırını RSS tarihiyle doğrular; bir kopyasını
                         ~/.kahutbe/is/pdf/'e koyar.
  cikar                  ~/.kahutbe/is/pdf/'tekileri ~/.kahutbe/is/extracted.json'a çıkarır.
  korpus-yaz EXT LABELS  Etiketleri kapalı listelere karşı denetler, korpusa yazar.
  alinti-denetle DOSYA   Soru JSON'undaki alıntıları hutbe metninde arar (yazmaz).
  kahutbe-yaz DOSYA.json Hutbe + 5 soruyu Supabase'e yazar (idempotent). Önce biçimi ve
                         açıklamalardaki “…” alıntılarının korpustaki hutbe metninde birebir
                         geçtiğini denetler; tek hata varsa HİÇBİR ŞEY yazmaz (soru onayı
                         otomatik olduğu için editörün yerini bu denetim tutuyor).
  vakit [YYYY-MM-DD]     quiz/supabase/vakit_guncelle.py'yi çalıştırır (varsayılan: önümüzdeki Cuma).

SERVİS ANAHTARI: ortam değişkeni SUPABASE_SERVICE_ROLE_KEY ya da
  %USERPROFILE%\\.kahutbe\\supabase.env (SUPABASE_SERVICE_ROLE_KEY=... satırı).
  Bilinçli olarak Drive'ın ve git'in DIŞINDA tutuluyor. Yalnızca kahutbe-yaz ve vakit ister.
"""
import html, io, json, os, re, subprocess, sys, urllib.request
from datetime import date

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

BASE = r"G:\Drive'ım\kamuran\hutbe"
DATA = os.path.join(BASE, "site", "data")
QUIZ = os.path.join(BASE, "quiz")
RSS_URL = "https://www.diyanethaber.com.tr/rss/hutbeler"
UA = {"User-Agent": "Mozilla/5.0 (kahutbe haftalik senkron)"}

# Kahutbe'ye eklenecek en eski tarih. Kullanıcı kararı (25.09.2026): eksik haftalar
# 24.07.2026'dan itibaren tamamlanır; daha eskileri yalnızca korpusta kalır.
KAHUTBE_TABAN = "2026-07-24"

# Haftalık rutinin geçici çalışma klasörü (PDF kopyaları, extracted/labels/soru JSON'ları).
# Drive dışında: yarım kalmış bir çalıştırmanın ara dosyaları senkronlanmasın.
IS = os.path.join(os.path.expanduser("~"), ".kahutbe", "is")

AYLAR = {"ocak":1,"şubat":2,"mart":3,"nisan":4,"mayıs":5,"haziran":6,"temmuz":7,
         "ağustos":8,"eylül":9,"ekim":10,"kasım":11,"aralık":12}


def _get(url, headers=None, data=None, method=None):
    h = dict(UA); h.update(headers or {})
    r = urllib.request.Request(url, headers=h, data=data, method=method)
    with urllib.request.urlopen(r, timeout=30) as resp:
        return resp.read()


def kahutbe_config():
    """Supabase adresi + anon anahtar: tek kaynak quiz/config.js."""
    t = open(os.path.join(QUIZ, "config.js"), encoding="utf-8").read()
    url = re.search(r"url:\s*'([^']+)'", t).group(1).rstrip("/")
    anon = re.search(r"anonKey:\s*'([^']+)'", t).group(1)
    return url, anon


def servis_anahtari():
    k = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if k:
        return k
    p = os.path.join(os.path.expanduser("~"), ".kahutbe", "supabase.env")
    if os.path.exists(p):
        for line in open(p, encoding="utf-8"):
            if line.strip().startswith("SUPABASE_SERVICE_ROLE_KEY="):
                return line.split("=", 1)[1].strip()
    sys.exit(f"Servis anahtarı yok: SUPABASE_SERVICE_ROLE_KEY ortam değişkeni ya da {p}")


def tarih_ayikla(s):
    """'25 Eylül 2026 - Cuma Hutbesi' / 'Kurban Bayramı Hutbesi - 27 Mayıs 2026' -> date."""
    m = re.search(r"(\d{1,2})\s+([A-Za-zÇĞİÖŞÜçğıöşü]+)\s+(\d{4})", s)
    if not m:
        return None
    ay = AYLAR.get(m.group(2).replace("I", "ı").replace("İ", "i").lower())
    return date(int(m.group(3)), ay, int(m.group(1))) if ay else None


def rss_oku():
    x = _get(RSS_URL).decode("utf-8", "replace")
    out = []
    for it in re.findall(r"<item>(.*?)</item>", x, re.S):
        baslik = re.sub(r"<!\[CDATA\[|\]\]>", "", re.search(r"<title>(.*?)</title>", it, re.S).group(1)).strip()
        link = re.search(r"<link>(.*?)</link>", it, re.S).group(1).strip()
        t = tarih_ayikla(baslik)
        if not t:
            print(f"UYARI: RSS başlığından tarih çıkmadı, atlandı: {baslik!r}")
            continue
        out.append({"tarih": t, "tur": "bayram" if "bayram" in baslik.lower() else "cuma",
                    "rss_baslik": baslik, "link": link})
    return out


def korpus_anahtarlari():
    h = json.load(open(os.path.join(DATA, "hutbeler.json"), encoding="utf-8"))
    anahtar = set()
    for x in h:
        d, m, y = x["date"].split(".")
        tur = "bayram" if "BAYRAM" in x["title"].upper() else "cuma"
        anahtar.add((date(int(y), int(m), int(d)), tur))
    return anahtar


def kahutbe_tarihleri():
    url, anon = kahutbe_config()
    try:
        rows = json.loads(_get(f"{url}/rest/v1/hutbeler?select=tarih", {"apikey": anon}))
    except Exception as e:
        print(f"UYARI: Kahutbe'ye ulaşılamadı ({e}) — Supabase projesi duraklatılmış olabilir.")
        return None
    return {date.fromisoformat(r["tarih"]) for r in rows}


def durum(yazdir=True):
    rss = rss_oku()
    korpus = korpus_anahtarlari()
    kahutbe = kahutbe_tarihleri()
    taban = date.fromisoformat(KAHUTBE_TABAN)
    eksik_korpus = [r for r in rss if (r["tarih"], r["tur"]) not in korpus]
    eksik_kahutbe = None if kahutbe is None else [
        r for r in rss if r["tur"] == "cuma" and r["tarih"] >= taban and r["tarih"] not in kahutbe]
    if yazdir:
        print(f"RSS: {len(rss)} hutbe ({min(r['tarih'] for r in rss)} → {max(r['tarih'] for r in rss)})")
        print(f"\nKorpusta eksik: {len(eksik_korpus)}")
        for r in sorted(eksik_korpus, key=lambda r: r["tarih"]):
            print(f"  {r['tarih']}  {r['tur']:6}  {r['rss_baslik']}")
        if eksik_kahutbe is None:
            print("\nKahutbe: ULAŞILAMADI — Kahutbe adımları bu çalıştırmada atlanmalı.")
        else:
            print(f"\nKahutbe'de eksik (Cuma, ≥{KAHUTBE_TABAN}): {len(eksik_kahutbe)}")
            for r in sorted(eksik_kahutbe, key=lambda r: r["tarih"]):
                print(f"  {r['tarih']}  {r['rss_baslik']}")
    return rss, eksik_korpus, eksik_kahutbe


BAGLACLAR = {"ve", "ile", "ya", "da", "de", "ki", "mi"}

def tr_baslik(s):
    kucuk = s.replace("İ", "i").replace("I", "ı").lower()
    def buyut(i, w):
        if not w or (i > 0 and w in BAGLACLAR): return w
        return {"i": "İ", "ı": "I"}.get(w[0], w[0].upper()) + w[1:]
    return " ".join(buyut(i, w) for i, w in enumerate(kucuk.split(" ")))


def pdf_indir(r):
    """Detay sayfasından PDF bağlantısını bulur, indirir, PDF'teki tarihi doğrular."""
    import fitz
    sys.path.insert(0, os.path.join(BASE, "site", "pipeline"))
    from importlib import import_module
    entegre = import_module("08_integrate_new_hutbe")

    sayfa = _get(r["link"]).decode("utf-8", "replace")
    pdfler = re.findall(r"https?://[^\"'\s>]+\.pdf", sayfa, re.I)
    if not pdfler:
        print(f"  HATA: {r['tarih']} detay sayfasında PDF yok: {r['link']}")
        return None
    icerik = _get(pdfler[0])
    doc = fitz.open(stream=icerik, filetype="pdf")
    metin = "\n".join(p.get_text("text") for p in doc)
    m = entegre.date_re.search(metin)
    pdf_tarih = f"{m.group(2)}.{m.group(3)}.{m.group(4)}" if m else None
    beklenen = r["tarih"].strftime("%d.%m.%Y")
    if pdf_tarih != beklenen:
        print(f"  HATA: {r['link']} — PDF tarihi {pdf_tarih!r}, RSS tarihi {beklenen!r}. İndirilmedi.")
        return None
    baslik, _ = entegre.extract_title_and_body_start(metin)
    # Dosya adı PDF METNİNDEKİ başlıktan. Meta verideki "title" GÜVENİLMEZ: Diyanet Word
    # şablonlarını yeniden kullanıyor, meta veri eski kalıyor (25.09.2026 Tebliğ Sorumluluğumuz
    # hutbesinin meta başlığı "Peygamberimiz (s.a.s), Cami ve Namaz", 11 ve 18.09'unki "İLİ" idi).
    ad = tr_baslik(baslik) if baslik else beklenen
    ad = re.sub(r'[\\/:*?"<>|]', "", ad).strip()
    klasor = os.path.join(BASE, str(r["tarih"].year))
    os.makedirs(klasor, exist_ok=True)
    yol = os.path.join(klasor, f"{ad}.pdf")
    if os.path.exists(yol) and open(yol, "rb").read() != icerik:
        yol = os.path.join(klasor, f"{ad} ({beklenen}).pdf")
    open(yol, "wb").write(icerik)
    print(f"  indirildi: {beklenen}  {baslik}  -> {os.path.relpath(yol, BASE)}")
    return yol


def indir():
    _, eksik, _ = durum(yazdir=False)
    # Bu çalıştırmanın PDF'leri ayrıca IS/pdf'e kopyalanır: extract_batch bir klasörün tamamını
    # okuyor, {yıl}/ klasöründe ise korpustaki eski PDF'ler de var.
    import shutil
    shutil.rmtree(os.path.join(IS, "pdf"), ignore_errors=True)
    os.makedirs(os.path.join(IS, "pdf"))
    if not eksik:
        print("Korpusta eksik hutbe yok — indirilecek bir şey yok.")
        return
    print(f"{len(eksik)} PDF indiriliyor:")
    for r in sorted(eksik, key=lambda r: r["tarih"]):
        yol = pdf_indir(r)
        if yol:
            shutil.copy2(yol, os.path.join(IS, "pdf", os.path.basename(yol)))


def cikar():
    """IS/pdf'teki PDF'leri 08.extract_batch ile IS/extracted.json'a çıkarır."""
    sys.path.insert(0, os.path.join(BASE, "site", "pipeline"))
    from importlib import import_module
    entegre = import_module("08_integrate_new_hutbe")
    hedef = os.path.join(IS, "extracted.json")
    entegre.extract_batch(os.path.join(IS, "pdf"), hedef)
    for r in json.load(open(hedef, encoding="utf-8")):
        print(f"  {r['date']}  {r['title']}  ({len(r['text'])} karakter)")
    print(f"-> {hedef}")


def _alinti_norm(s):
    """Karşılaştırma için: tırnak türleri (iç içe alıntıda ‘ ’ / “ ” farkı), dipnot rakamları,
    büyük-küçük harf ve boşluk farkları yok sayılır."""
    s = re.sub(r"[“”\"‘’'`]", "", s)
    s = re.sub(r"(?<=[^\W\d])\d+\b", "", s)          # kelimeye yapışık dipnot işaretçisi
    s = s.replace("İ", "i").replace("I", "ı").lower()
    return re.sub(r"\s+", " ", s).strip()


def alinti_denetle(k):
    """Açıklamalardaki “…” alıntılarını hutbe metninde arar; bulunamayanları döndürür."""
    gun, ay, yil = k["korpus_hutbe_id"].split(".")
    metinler = json.load(open(os.path.join(DATA, "metinler", f"{yil}.json"), encoding="utf-8"))
    assert k["korpus_hutbe_id"] in metinler, f"{k['korpus_hutbe_id']} korpusta yok — önce korpus-yaz"
    metin = _alinti_norm(metinler[k["korpus_hutbe_id"]]["text"])
    eksik = []
    for s in k["sorular"]:
        for alinti in re.findall(r"“(.*?)”(?![’\w])", s["aciklama"]):
            for parca in re.split(r"…|\.\.\.", alinti):
                p = _alinti_norm(parca).strip(" ,;.:!?")
                if len(p) > 8 and p not in metin:
                    eksik.append(f"soru {s['sira']}: {parca.strip()[:80]}")
    return eksik


def kahutbe_yaz(dosya):
    """dosya: {"tarih":"YYYY-MM-DD","baslik":"...","korpus_hutbe_id":"GG.AA.YYYY",
               "sorular":[{"sira":1,"metin":"...","secenekler":[4 şık],"dogru_idx":0-3,"aciklama":"..."}]}"""
    k = json.load(open(dosya, encoding="utf-8"))
    sor = k["sorular"]
    assert len(sor) == 5, f"5 soru olmalı, {len(sor)} var"
    for s in sor:
        assert len(s["secenekler"]) == 4 and 0 <= s["dogru_idx"] <= 3, f"soru {s['sira']} geçersiz"
        assert len(set(s["secenekler"])) == 4, f"soru {s['sira']}: şıklar tekrar ediyor"
        assert s["aciklama"].strip(), f"soru {s['sira']}: açıklama boş"
    assert sorted(s["sira"] for s in sor) == [1, 2, 3, 4, 5], "sıra 1-5 olmalı"
    eksik = alinti_denetle(k)
    if eksik:
        sys.exit("Alıntı denetimi BAŞARISIZ — hiçbir şey yazılmadı:\n  " + "\n  ".join(eksik))
    url, _ = kahutbe_config()
    key = servis_anahtari()
    H = {"apikey": key, "Authorization": f"Bearer {key}", "Content-Type": "application/json"}

    mevcut = json.loads(_get(f"{url}/rest/v1/hutbeler?tarih=eq.{k['tarih']}&select=id", H))
    if mevcut:
        hid = mevcut[0]["id"]
        n = len(json.loads(_get(f"{url}/rest/v1/sorular?hutbe_id=eq.{hid}&select=id", H)))
        if n:
            print(f"{k['tarih']} zaten var ({n} soru) — dokunulmadı.")
            return
    else:
        hid = json.loads(_get(f"{url}/rest/v1/hutbeler", {**H, "Prefer": "return=representation"},
                              json.dumps({"tarih": k["tarih"], "baslik": k["baslik"],
                                          "korpus_hutbe_id": k["korpus_hutbe_id"]}).encode(), "POST"))[0]["id"]
    satirlar = [{"hutbe_id": hid, "sira": s["sira"], "metin": s["metin"], "secenekler": s["secenekler"],
                 "dogru_idx": s["dogru_idx"], "aciklama": s.get("aciklama", ""), "tur": "kavrayis"} for s in sor]
    _get(f"{url}/rest/v1/sorular", {**H, "Prefer": "return=minimal"}, json.dumps(satirlar).encode(), "POST")
    print(f"{k['tarih']} {k['baslik']}: hutbe + 5 soru yazıldı.")


CERCEVE = {"birey", "aile", "cemaat-toplum", "devlet-otorite", "karma"}
TON = {"teşvik", "uyarı", "teselli", "kınama", "bilgilendirme"}
MUHATAP = {"genel", "aileler", "gençler", "kadınlar", "esnaf-işveren", "millet", "ümmet"}
EYLEM = {"yok", "ritüel", "ahlaki", "maddi", "katılım"}


def tr_buyuk(s):
    """Türkçe büyük harf ('i'->'İ'). PDF başlıkları bazen 've' gibi küçük bağlaç içeriyor
    ('EĞİTİM ve ÖĞRETİM'); korpustaki tüm başlıklar büyük harf."""
    return s.replace("i", "İ").replace("ı", "I").upper()


def etiket_denetle(extracted, labels, CATS):
    """Kod kitabı §3-§4'ün kapalı değer listelerine karşı denetim. Hata listesi döndürür."""
    hata = []
    anahtar = {(r["date"], r["title"]) for r in extracted}
    for L in labels:
        k = f"{L.get('date')} {L.get('title')}"
        if (L.get("date"), L.get("title")) not in anahtar:
            hata.append(f"{k}: çıkarılan kayıtlarda bu tarih+başlık yok")
        if L.get("primary") not in CATS:
            hata.append(f"{k}: ana kategori geçersiz: {L.get('primary')!r}")
        sec = L.get("secondary", [])
        if len(sec) > 2 or any(s not in CATS for s in sec) or L.get("primary") in sec:
            hata.append(f"{k}: ikincil kategoriler geçersiz: {sec!r}")
        if L.get("cerceve") not in CERCEVE:
            hata.append(f"{k}: çerçeve geçersiz: {L.get('cerceve')!r}")
        if L.get("muhatap") not in MUHATAP:
            hata.append(f"{k}: muhatap geçersiz: {L.get('muhatap')!r}")
        for alan, izinli in (("ton", TON), ("eylem_cagrisi", EYLEM)):
            v = L.get(alan, [])
            if not (1 <= len(v) <= 2) or any(x not in izinli for x in v) or len(set(v)) != len(v):
                hata.append(f"{k}: {alan} geçersiz: {v!r}")
        if "yok" in L.get("eylem_cagrisi", []) and len(L["eylem_cagrisi"]) > 1:
            hata.append(f"{k}: eylem_cagrisi 'yok' başka değerle birlikte olamaz")
        if not L.get("summary", "").strip():
            hata.append(f"{k}: özet boş")
        if not (4 <= len(L.get("keywords", [])) <= 5):
            hata.append(f"{k}: 4-5 anahtar kelime olmalı")
    return hata


def korpus_yaz(extracted_json, labels_json):
    """Çıkarılmış kayıtlar + ajanın yazdığı etiketler -> korpus. Önce denetler; tek hata
    varsa HİÇBİR ŞEY yazmaz."""
    sys.path.insert(0, os.path.join(BASE, "site", "pipeline"))
    from importlib import import_module
    entegre = import_module("08_integrate_new_hutbe")

    extracted = json.load(open(extracted_json, encoding="utf-8"))
    for r in extracted:
        r["title"] = tr_buyuk(r["title"])
    labels = json.load(open(labels_json, encoding="utf-8"))

    hata = etiket_denetle(extracted, labels, entegre.CATS)
    if hata:
        print("ETİKET DENETİMİ BAŞARISIZ — korpusa hiçbir şey yazılmadı:")
        for h in hata:
            print("  -", h)
        sys.exit(1)

    mevcut = korpus_anahtarlari()
    for L in labels:
        d, m, y = L["date"].split(".")
        tur = "bayram" if "BAYRAM" in L["title"] else "cuma"
        if (date(int(y), int(m), int(d)), tur) in mevcut:
            sys.exit(f"{L['date']} {L['title']} korpusta ZATEN var — çift kayıt önlendi, hiçbir şey yazılmadı.")

    yillar = {L["date"][-4:] for L in labels}
    # Her çalıştırmaya AYRI yedek eki: varsayılan ".bak-pre{yıl}" o yılın ilk entegrasyonunda
    # zaten oluştuğu için sonraki entegrasyonlarda yeni bir geri dönüş noktası üretmiyordu.
    ek = f".bak-pre{date.today():%Y%m%d}"
    for yil in sorted(yillar):
        e = [r for r in extracted if r["date"].endswith(yil)]
        l = [L for L in labels if L["date"].endswith(yil)]
        entegre.integrate(e, l, int(yil), backup_suffix=ek)
    entegre.recompute_meta(ek)
    # Kök dizindeki türev atıf tablolarını yeniden üretir VE meta.json'ın atıf alanlarını
    # (total_citations, top_verses, top_suras, top_hadis_kaynak) yerleşik tanımıyla yazar.
    # recompute_meta total_citations'ı hutbe başına citation_count toplamı olarak hesaplıyor;
    # sitenin baştan beri kullandığı tanım ayet + hadis + sahabe ismi. Bu adım atlanınca
    # 25.09.2026 backfill'inde sayı 1546 yerine 1783 olarak yayına çıktı.
    subprocess.run([sys.executable, os.path.join(BASE, "arastirma", "uret_turev_dosyalar.py")],
                   check=True, cwd=BASE, env=dict(os.environ, PYTHONIOENCODING="utf-8"))
    print(f"\nKorpusa {len(labels)} hutbe eklendi (yedek eki: {ek}).")


def vakit(tarih=None):
    url, _ = kahutbe_config()
    env = dict(os.environ, SUPABASE_URL=url, SUPABASE_SERVICE_ROLE_KEY=servis_anahtari(),
               PYTHONIOENCODING="utf-8")
    subprocess.run([sys.executable, os.path.join(QUIZ, "supabase", "vakit_guncelle.py")] + ([tarih] if tarih else []),
                   env=env, check=True)


if __name__ == "__main__":
    komut = sys.argv[1] if len(sys.argv) > 1 else "durum"
    if komut == "durum":
        durum()
    elif komut == "indir":
        indir()
    elif komut == "cikar":
        cikar()
    elif komut == "korpus-yaz":
        korpus_yaz(sys.argv[2], sys.argv[3])
    elif komut == "kahutbe-yaz":
        kahutbe_yaz(sys.argv[2])
    elif komut == "alinti-denetle":  # yalnızca denetim, yazma yok
        e = alinti_denetle(json.load(open(sys.argv[2], encoding="utf-8")))
        print("\n".join(e) if e else "tüm alıntılar hutbe metninde bulundu")
        sys.exit(1 if e else 0)
    elif komut == "vakit":
        vakit(sys.argv[2] if len(sys.argv) > 2 else None)
    else:
        sys.exit(__doc__)
