# -*- coding: utf-8 -*-
"""Hadis bölüm adlarındaki yazım varyantlarını tek biçime indirger.

Dipnotlar aynı bölümü farklı yazıyor: Tirmizî'nin "Sıfatü'l-kıyâme" bölümü
korpusta 9 ayrı biçimde geçiyor ("Sıfatu'l Kıyâme", "Sıfatü'l- Kıyâme",
"Sıfâtü'l-kıyâme", ...). Bu, "en çok atıf yapılan bölüm" gibi toplamları
böldüğü için hem İP-3 analizini hem de paylaşım kartlarındaki kaynak
gösterimini bozuyor.

Kural: aksan/kesme/boşluk/büyük-küçük harf farkı dışında AYNI olan adlar tek
grupta toplanır; grubun kanonik biçimi en sık geçen yazımdır (eşitlikte en uzun
olan, yani aksanı korunmuş biçim seçilir). Farklı sözcük içeren adlar
(ör. "Birr" ile "Birr ve Sıla") BİRLEŞTİRİLMEZ -- bu bir yazım değil kısaltma
farkıdır ve konu bilgisi gerektirir.

Ayrıca: Ahmed b. Hanbel atıfları cilt/sayfa biçiminde olduğundan bölüm alanı
boş kalıyor; görüntülemede "Ahmed b. Hanbel, " gibi eksik görünmemesi için
bu satırlarda bölüm "Müsned" olarak yazılır.
"""
import csv, json, os, re, shutil, unicodedata
from collections import Counter, defaultdict

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, 'site', 'data')


def key(s):
    s = (s or '').lower().replace('İ', 'i')
    s = unicodedata.normalize('NFKD', s)
    s = ''.join(c for c in s if not unicodedata.combining(c))
    return re.sub(r'[^a-z0-9]', '', s)


def kanonik_harita(kayitlar):
    grup = defaultdict(Counter)
    for kaynak, bolum in kayitlar:
        if bolum:
            grup[(kaynak, key(bolum))][bolum] += 1
    harita = {}
    for (kaynak, k), c in grup.items():
        en_iyi = sorted(c.items(), key=lambda kv: (-kv[1], -len(kv[0])))[0][0]
        for varyant in c:
            if varyant != en_iyi:
                harita[(kaynak, varyant)] = en_iyi
    return harita


def main():
    hadis = json.load(open(os.path.join(DATA, 'hadisler.json'), encoding='utf-8'))
    csv_yolu = os.path.join(BASE, 'hadis_tam_metin.csv')
    satirlar = list(csv.DictReader(open(csv_yolu, encoding='utf-8-sig')))

    harita = kanonik_harita([(r['kaynak'], r['bolum']) for r in hadis]
                            + [(r['kaynak'], r['bolum']) for r in satirlar])
    print(f'{len(harita)} yazım varyantı tek biçime indirgeniyor')
    for (kay, var), kan in sorted(harita.items())[:10]:
        print(f'  {kay}: {var!r} -> {kan!r}')

    n = m = 0
    for r in hadis:
        yeni = harita.get((r['kaynak'], r['bolum']), r['bolum'])
        if not yeni and r['kaynak'].startswith('Ahmed b. Hanbel'):
            yeni = 'Müsned'
        if yeni != r['bolum']:
            r['bolum'] = yeni; n += 1
    for r in satirlar:
        yeni = harita.get((r['kaynak'], r['bolum']), r['bolum'])
        if not yeni and r['kaynak'].startswith('Ahmed b. Hanbel'):
            yeni = 'Müsned'
        if yeni != r['bolum']:
            r['bolum'] = yeni; m += 1

    say = Counter((r['kaynak'], r['bolum']) for r in hadis)
    for r in hadis:
        r['count'] = say[(r['kaynak'], r['bolum'])]
    say = Counter((r['kaynak'], r['bolum']) for r in satirlar)
    for r in satirlar:
        r['kac_kez'] = say[(r['kaynak'], r['bolum'])]

    for yol, yaz in ((os.path.join(DATA, 'hadisler.json'), None), (csv_yolu, None)):
        if not os.path.exists(yol + '.bak-preBolumNorm'):
            shutil.copy2(yol, yol + '.bak-preBolumNorm')
    json.dump(hadis, open(os.path.join(DATA, 'hadisler.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    with open(csv_yolu, 'w', encoding='utf-8-sig', newline='') as f:
        cols = ['kaynak', 'bolum', 'kac_kez', 'hadis_meali_hutbede_gecen', 'tema', 'tarih', 'hutbe_basligi']
        w = csv.DictWriter(f, fieldnames=cols, extrasaction='ignore')
        w.writeheader()
        w.writerows(sorted(satirlar, key=lambda r: (-int(r['kac_kez']), r['kaynak'], r['bolum'], r['tarih'])))
    print(f'hadisler.json: {n} satır güncellendi | hadis_tam_metin.csv: {m} satır güncellendi')


if __name__ == '__main__':
    main()
