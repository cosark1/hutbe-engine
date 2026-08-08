# -*- coding: utf-8 -*-
"""site/data/{ayetler,hadisler}.json'ı tek doğruluk kaynağı sayıp ayet_tam_metin.csv,
hadis_tam_metin.csv ve türev sıralama/tema tablolarını yeniden üretir.

Girdi : site/data/{ayetler,hadisler}.json  (denetlenmiş + 20 eksik hutbeyle
        genişletilmiş tam atıf kümesi; her kaydın kendi `category` alanı zaten
        15'li ana kategori şemasını kullanıyor — 08_integrate_new_hutbe.py bunu
        korpus_v2/all.csv'deki ana_kategori'den doğrudan yazıyor)
Çıktı : ayet_tam_metin.csv, hadis_tam_metin.csv (JSON'dan birebir yeniden
        üretilir; İP-7b öncesi ayrı bir "tema" sözlüğü kullanan eski sürüm
        artık yok), ayet_atif_siralamasi.csv, sure_atif_siralamasi.csv,
        ayet_x_tema.csv, hadis_siralamasi.csv, hadis_kaynak_siralamasi.csv,
        hadis_x_tema.csv, hadis_kaynak_x_tema.csv

Not (İP-7b, 03.08.2026): Önceki sürüm tema sütununu ayrı bir
hutbe_kategori_analizi.csv dosyasından (eski, 645 satırlık, güncellenmeyen
ince şema) türetiyordu; bu sütun site JSON'larındaki 15'li şemadan
sistematik olarak farklıydı. Artık `tema` doğrudan ayetler.json/hadisler.json
kayıtlarının `category` alanından alınır -- tek şema, tek kaynak.
"""
import csv, json, os, shutil
from collections import Counter, defaultdict

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, 'site', 'data')

TEMALAR = [
    'Toplumsal Dayanışma, Merhamet ve Kardeşlik', 'İbadet ve Kulluk', 'Aile, Çocuk ve Nesil',
    'İman, Tevhid ve Ahiret', 'Ahlak, Erdem ve Söz', 'Ramazan, Oruç ve Bayramlar',
    'Vatan, Millet ve Tarih', 'Sabır, Tevekkül ve Manevi Olgunluk',
    'Ekonomik Hayat: Kazanç, Zekat ve İsraf', 'Kandiller, Muharrem ve Mübarek Geceler',
    'Peygamberimiz ve Ashab', 'İslam Coğrafyası ve Küresel Meseleler',
    'Eğitim, Teknoloji, Çevre ve Toplumsal Değişim', 'Afet, Kriz ve Sağlık', 'Kur\'an-ı Kerim',
]


def yaz(ad, basliklar, satirlar):
    yol = os.path.join(BASE, ad)
    if os.path.exists(yol) and not os.path.exists(yol + '.bak-preAtifDenetimi'):
        shutil.copy2(yol, yol + '.bak-preAtifDenetimi')
    with open(yol, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f)
        w.writerow(basliklar)
        w.writerows(satirlar)
    print(f'  {ad}: {len(satirlar)} satır')


def capraz(rows, anahtar):
    """anahtar(row) -> {tema: sayı} çapraz tablosu; tema doğrudan row['category']."""
    tab = defaultdict(Counter)
    for r in rows:
        tab[anahtar(r)][r.get('category') or ''] += 1
    out = []
    for k, c in sorted(tab.items(), key=lambda kv: -sum(kv[1].values())):
        out.append([k, sum(c.values())] + [c.get(t, 0) for t in TEMALAR])
    return out


def yaz_tam_metin(ad, rows, json_keycols, csv_keycols, meal_kolonu):
    """ayet_tam_metin.csv / hadis_tam_metin.csv'yi JSON kayıtlarından üretir.

    Şema, denetim öncesi elle üretilen dosyayla birebir aynı: her satır bir
    KULLANIM (hutbe × atıf) örneğidir, kac_kez o (sure,ayet_no)/(kaynak,bolum)
    çiftinin toplam kullanım sayısıdır (her satırda tekrarlanır). json_keycols
    JSON'daki alan adları (ayetler.json'da ayet no. alanı 'ayet'), csv_keycols
    çıktı CSV başlıkları (tarihsel uyum için 'ayet_no').
    """
    jka, jkb = json_keycols
    say = Counter((r[jka], r[jkb]) for r in rows)
    out = []
    for r in rows:
        out.append([r[jka], r[jkb], say[(r[jka], r[jkb])], r['quote'], r.get('category', ''),
                    r['date'], r['title']])
    out.sort(key=lambda x: (-x[2], x[0], str(x[1]), x[5]))
    yaz(ad, list(csv_keycols) + ['kac_kez', meal_kolonu, 'tema', 'tarih', 'hutbe_basligi'], out)


def main():
    ayet = json.load(open(os.path.join(DATA, 'ayetler.json'), encoding='utf-8'))
    hadis = json.load(open(os.path.join(DATA, 'hadisler.json'), encoding='utf-8'))
    sahabe = json.load(open(os.path.join(DATA, 'sahabeler.json'), encoding='utf-8'))
    print(f'girdi: {len(ayet)} ayet atfı, {len(hadis)} hadis atfı, {len(sahabe)} sahabe anımı')

    yaz_tam_metin('ayet_tam_metin.csv', ayet, ('sure', 'ayet'), ('sure', 'ayet_no'),
                  'ayet_meali_hutbede_gecen')
    yaz_tam_metin('hadis_tam_metin.csv', hadis, ('kaynak', 'bolum'), ('kaynak', 'bolum'),
                  'hadis_meali_hutbede_gecen')

    # sahabe_tam_liste.csv: sahabeler.json'daki isim alanı zaten tek anahtar
    # (bolum yok), bu yüzden yaz_tam_metin() kalıbı yerine ayrı, basit bir
    # üretim mantığı kullanılır.
    say_s = Counter(r['isim'] for r in sahabe)
    out_s = sorted(
        ([r['isim'], say_s[r['isim']], r.get('category', ''), r['date'], r['title']] for r in sahabe),
        key=lambda x: (-x[1], x[0], x[3]))
    yaz('sahabe_tam_liste.csv', ['isim', 'kac_kez', 'tema', 'tarih', 'hutbe_basligi'], out_s)
    yaz('sahabe_siralamasi.csv', ['isim', 'kac_kez'],
        [[isim, n] for isim, n in say_s.most_common()])
    yaz('sahabe_x_tema.csv', ['isim', 'toplam'] + TEMALAR, capraz(sahabe, lambda r: r['isim']))

    c = Counter((r['sure'], r['ayet']) for r in ayet)
    yaz('ayet_atif_siralamasi.csv', ['sure', 'ayet', 'atif_sayisi'],
        [[s, a, n] for (s, a), n in c.most_common()])

    cs = Counter(r['sure'] for r in ayet)
    yaz('sure_atif_siralamasi.csv', ['sure', 'atif_sayisi'],
        [[s, n] for s, n in cs.most_common()])

    yaz('ayet_x_tema.csv', ['ayet', 'toplam'] + TEMALAR,
        capraz(ayet, lambda r: f"{r['sure']} {r['ayet']}"))

    ch = Counter((r['kaynak'], r['bolum']) for r in hadis)
    yaz('hadis_siralamasi.csv', ['kaynak', 'bolum', 'atif_sayisi'],
        [[k, b, n] for (k, b), n in ch.most_common()])

    ck = Counter(r['kaynak'] for r in hadis)
    yaz('hadis_kaynak_siralamasi.csv', ['kaynak', 'atif_sayisi'],
        [[k, n] for k, n in ck.most_common()])

    yaz('hadis_x_tema.csv', ['hadis_kaynagi_bolumu', 'toplam'] + TEMALAR,
        capraz(hadis, lambda r: f"{r['kaynak']} {r['bolum']}".strip()))

    yaz('hadis_kaynak_x_tema.csv', ['kaynak', 'toplam'] + TEMALAR,
        capraz(hadis, lambda r: r['kaynak']))

    guncelle_meta(ayet, hadis, c, cs, ck)


def guncelle_meta(ayet, hadis, ayet_c, sure_c, kaynak_c):
    """site/data/meta.json içindeki atıf toplamlarını ve ilk-N listelerini tazeler."""
    yol = os.path.join(DATA, 'meta.json')
    m = json.load(open(yol, encoding='utf-8'))
    if not os.path.exists(yol + '.bak-preAtifDenetimi'):
        shutil.copy2(yol, yol + '.bak-preAtifDenetimi')

    ornek = {}
    for r in ayet:
        ornek.setdefault((r['sure'], r['ayet']), r['quote'])

    m['total_ayet'] = len(ayet)
    m['total_hadis'] = len(hadis)
    m['total_citations'] = len(ayet) + len(hadis) + m.get('total_sahabe_isim', 0)
    m['top_suras'] = [{'name': s, 'count': n} for s, n in sure_c.most_common(15)]
    m['top_verses'] = [{'label': f'{s} {a}', 'count': n, 'quote': ornek[(s, a)]}
                       for (s, a), n in ayet_c.most_common(20)]
    m['top_hadis_kaynak'] = [{'name': k, 'count': n} for k, n in kaynak_c.most_common(15)]
    json.dump(m, open(yol, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f"  site/data/meta.json: total_ayet={m['total_ayet']}, total_hadis={m['total_hadis']}, "
          f"total_citations={m['total_citations']}")


if __name__ == '__main__':
    main()
