# -*- coding: utf-8 -*-
"""
06_build_data.py — Birleşik dashboard_dataN.json dosyasından, sitenin
data/ klasöründeki modüler JSON dosyalarını üretir.

Girdi : dashboard_dataN.json (01-05 adımlarının çıktısı birleştirilmiş hali)
Çıktı : data/hutbeler.json, data/metinler/{yil}.json, data/ayetler.json,
        data/hadisler.json, data/sahabeler.json, data/kelimeler.json, data/meta.json

Kullanım:
    python3 06_build_data.py /yol/dashboard_dataN.json /yol/site/data/
"""
import json, sys, collections, os

def build(src_path, out_dir):
    d = json.load(open(src_path, encoding='utf-8'))
    os.makedirs(os.path.join(out_dir, 'metinler'), exist_ok=True)

    fset = set(d['full_texts'].keys())
    seen = {}
    for row in d['hutbeler']:
        if row['date'] not in fset:
            continue
        seen[row['date']] = row  # aynı tarihte birden fazla kayıt varsa sonuncusunu al
    hutbeler_light = []
    for date, row in seen.items():
        hutbeler_light.append({
            "date": row['date'], "year": row['year'], "title": row['title'],
            "summary": row.get('summary', ''), "keywords": row.get('keywords', []),
            "primary_category": row['primary_category'],
            "secondary_categories": row.get('secondary_categories', []),
            "citation_count": row.get('citation_count', 0),
        })
    hutbeler_light.sort(key=lambda r: tuple(reversed(r['date'].split('.'))))
    json.dump(hutbeler_light, open(os.path.join(out_dir, 'hutbeler.json'), 'w', encoding='utf-8'), ensure_ascii=False)

    by_year = collections.defaultdict(dict)
    for date, rec in d['full_texts'].items():
        year = int(date.split('.')[-1])
        by_year[year][date] = {
            "title": rec['title'], "category": rec['category'],
            "secondary_categories": rec.get('secondary_categories', []),
            "summary": rec.get('summary', ''), "keywords": rec.get('keywords', []),
            "text": rec['text'],
        }
    for year, recs in by_year.items():
        json.dump(recs, open(os.path.join(out_dir, 'metinler', f'{year}.json'), 'w', encoding='utf-8'), ensure_ascii=False)

    json.dump(d['ayet_list'], open(os.path.join(out_dir, 'ayetler.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    json.dump(d['hadis_list'], open(os.path.join(out_dir, 'hadisler.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    json.dump(d['sahabe_list'], open(os.path.join(out_dir, 'sahabeler.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    json.dump(d['keyword_list'], open(os.path.join(out_dir, 'kelimeler.json'), 'w', encoding='utf-8'), ensure_ascii=False)

    meta = {
        "overall_category": d['overall_category'], "yearly": d['yearly'], "weekly_grid": d['weekly_grid'],
        "top_suras": d['top_suras'], "top_verses": d['top_verses'], "top_hadis_kaynak": d['top_hadis_kaynak'],
        "keyword_category_matrix": d['keyword_category_matrix'], "top_keywords": d['top_keywords'],
        "total_hutbe": len(hutbeler_light), "total_citations": d['total_citations'],
        "total_ayet": d['total_ayet'], "total_hadis": d['total_hadis'], "total_sahabe_isim": d['total_sahabe_isim'],
        "total_keywords": d['total_keywords'], "total_keyword_mentions": d['total_keyword_mentions'],
        "year_min": d['year_min'], "year_max": d['year_max'], "top_category": d['top_category'],
    }
    json.dump(meta, open(os.path.join(out_dir, 'meta.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    print(f"Tamamlandı: {len(hutbeler_light)} hutbe, {len(by_year)} yıl dosyası.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Kullanım: python3 06_build_data.py <dashboard_dataN.json> <data_cikti_klasoru>")
        sys.exit(1)
    build(sys.argv[1], sys.argv[2])
