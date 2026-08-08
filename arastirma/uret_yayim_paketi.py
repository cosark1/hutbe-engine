# -*- coding: utf-8 -*-
"""İP-10: Zenodo/OSF'ye yüklenecek açık veri paketini arastirma/yayim_paketi/
altında derler. Etiket verisi (korpus_v2/all.csv) ile tam metni (metinler/*.json)
tek bir hutbe_korpusu.{csv,json} dosyasında birleştirir; ayet/hadis/sahabe atıf
tablolarını, kod kitabını ve güvenilirlik raporunu aynı klasöre kopyalar.

DİKKAT: Bu betik yalnızca YEREL dosyaları hazırlar. Zenodo/OSF'ye yükleme ve
DOI alma adımı kasıtlı olarak burada YOKTUR -- hesap açma ve kalıcı kamuya açık
yayın gerektirdiği için bu adım kullanıcı tarafından yapılmalıdır.
"""
import csv, json, os, shutil

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, 'site', 'data')
OUT = os.path.join(BASE, 'arastirma', 'yayim_paketi')
csv.field_size_limit(10 ** 7)


def load_metinler():
    met = {}
    d = os.path.join(DATA, 'metinler')
    for fn in sorted(os.listdir(d)):
        if fn.endswith('.json') and fn[:4].isdigit():
            for k, r in json.load(open(os.path.join(d, fn), encoding='utf-8')).items():
                met[k] = r
    return met


def main():
    os.makedirs(OUT, exist_ok=True)
    metinler = load_metinler()
    etiketler = list(csv.DictReader(open(os.path.join(BASE, 'arastirma', 'korpus_v2', 'all.csv'),
                                          encoding='utf-8-sig')))
    print(f'korpus_v2/all.csv: {len(etiketler)} etiketli hutbe | metinler: {len(metinler)} tam metin')

    birlesik = []
    eksik_metin = 0
    # id alanı korpus_v2'de "YYYY-MM-DD[-b]" biçiminde, metinler ise "DD.MM.YYYY[-b]" anahtarlı.
    for r in etiketler:
        yyyy, mm, dd_suf = r['id'].split('-', 2)
        dd = dd_suf[:2]
        suf = dd_suf[2:]  # "" veya "-b"
        anahtar = f'{dd}.{mm}.{yyyy}{suf}'
        m = metinler.get(anahtar)
        if not m:
            eksik_metin += 1
            ozet, kw, metin = '', [], ''
        else:
            ozet, kw, metin = m.get('summary', ''), m.get('keywords', []), m.get('text', '')
        birlesik.append({
            'id': r['id'], 'tarih': r['tarih'], 'baslik': r['baslik'],
            'ana_kategori': r['ana_kategori'], 'ikincil_kategoriler': r['ikincil_kategoriler'],
            'cerceve': r['cerceve'], 'ton': r['ton'], 'muhatap': r['muhatap'],
            'eylem_cagrisi': r['eylem_cagrisi'], 'ozet': ozet,
            'anahtar_kelimeler': '; '.join(kw), 'tam_metin': metin,
        })
    if eksik_metin:
        print(f'UYARI: {eksik_metin} etiketli kayıt için tam metin bulunamadı')

    cols = ['id', 'tarih', 'baslik', 'ana_kategori', 'ikincil_kategoriler', 'cerceve', 'ton',
            'muhatap', 'eylem_cagrisi', 'ozet', 'anahtar_kelimeler', 'tam_metin']
    with open(os.path.join(OUT, 'hutbe_korpusu.csv'), 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(birlesik)
    json.dump(birlesik, open(os.path.join(OUT, 'hutbe_korpusu.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print(f'yazıldı: hutbe_korpusu.csv/json ({len(birlesik)} hutbe)')

    # atıf tabloları ve kod kitabı/güvenilirlik raporu paketin içine kopyalanır
    kopyala = [
        ('ayet_tam_metin.csv', 'ayet_atiflari.csv'),
        ('hadis_tam_metin.csv', 'hadis_atiflari.csv'),
        ('sahabe_tam_liste.csv', 'sahabe_animlari.csv'),
        (os.path.join('arastirma', 'kod_kitabi.md'), 'kod_kitabi.md'),
        (os.path.join('arastirma', 'guvenilirlik_raporu.md'), 'guvenilirlik_raporu.md'),
        (os.path.join('arastirma', 'pilot_raporu.md'), 'pilot_raporu.md'),
    ]
    for src, dst in kopyala:
        s = os.path.join(BASE, src)
        if os.path.exists(s):
            shutil.copy2(s, os.path.join(OUT, dst))
            print(f'kopyalandı: {dst}')
        else:
            print(f'UYARI: bulunamadı, kopyalanmadı: {src}')


if __name__ == '__main__':
    main()
