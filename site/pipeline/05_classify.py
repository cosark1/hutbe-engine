# -*- coding: utf-8 -*-
import json, collections

AXES = json.load(open("/sessions/happy-trusting-turing/mnt/outputs/hutbe_work/axes.json", encoding="utf-8"))
d = json.load(open("/sessions/happy-trusting-turing/mnt/outputs/hutbe_work/dashboard_data10.json", encoding="utf-8"))

FALLBACK = {
 "Ahlak ve Erdemler":"Ahlak, Erdem ve Söz","Dil ve Söz Ahlakı":"Ahlak, Erdem ve Söz","Sahih Din Anlayışı":"Ahlak, Erdem ve Söz",
 "Peygamberimiz: Siyer ve Sünnet":"Peygamberimiz ve Ashab","Sahabe ve Ehl-i Beyt":"Peygamberimiz ve Ashab",
 "İman Esasları ve Tevhid":"İman, Tevhid ve Ahiret","Ahiret, Ölüm ve Kıyamet":"İman, Tevhid ve Ahiret","Tevbe ve İstiğfar":"İman, Tevhid ve Ahiret",
 "Ramazan ve Oruç":"Ramazan, Oruç ve Bayramlar","Ramazan Bayramı":"Ramazan, Oruç ve Bayramlar","Kurban ve Kurban Bayramı":"Ramazan, Oruç ve Bayramlar",
 "Aile ve Evlilik":"Aile, Çocuk ve Nesil","Çocuk ve Gençlik":"Aile, Çocuk ve Nesil","Kadın":"Aile, Çocuk ve Nesil","Yaşlılar ve Vefa":"Aile, Çocuk ve Nesil",
 "Namaz ve İbadet":"İbadet ve Kulluk","Hac ve Umre":"İbadet ve Kulluk","Cami ve Cemaat":"İbadet ve Kulluk","Dua":"İbadet ve Kulluk",
 "Kandiller (Miraç/Berat/Kadir/Mevlid)":"Kandiller, Muharrem ve Mübarek Geceler","Muharrem, Aşure ve Kerbela":"Kandiller, Muharrem ve Mübarek Geceler",
 "Kur'an-ı Kerim":"Kur'an-ı Kerim",
 "İslam Coğrafyası ve Mazlumlar":"İslam Coğrafyası ve Küresel Meseleler",
 "Şehitlik, Vatan ve 15 Temmuz":"Vatan, Millet ve Tarih","Milli ve Tarihi Günler":"Vatan, Millet ve Tarih",
 "Merhamet ve Sevgi":"Toplumsal Dayanışma, Merhamet ve Kardeşlik","Birlik, Kardeşlik ve Hoşgörü":"Toplumsal Dayanışma, Merhamet ve Kardeşlik",
 "Komşuluk ve Toplumsal Dayanışma":"Toplumsal Dayanışma, Merhamet ve Kardeşlik","Engellilik":"Toplumsal Dayanışma, Merhamet ve Kardeşlik",
 "Helal Kazanç, Ticaret ve Ekonomi":"Ekonomik Hayat: Kazanç, Zekat ve İsraf","Zekat, Sadaka ve İnfak":"Ekonomik Hayat: Kazanç, Zekat ve İsraf","Çalışma ve İsraf":"Ekonomik Hayat: Kazanç, Zekat ve İsraf",
 "Afet ve Kriz":"Afet, Kriz ve Sağlık","Sağlık ve Salgın":"Afet, Kriz ve Sağlık",
 "İlim ve Eğitim":"Eğitim, Teknoloji, Çevre ve Toplumsal Değişim","Dijital Dünya ve Bağımlılık":"Eğitim, Teknoloji, Çevre ve Toplumsal Değişim","Çevre ve Hayvan Hakları":"Eğitim, Teknoloji, Çevre ve Toplumsal Değişim",
 "Diğer / Sınıflandırılamadı":"Sabır, Tevekkül ve Manevi Olgunluk",
}

def matches(term, kw):
    return term == kw or term in kw or kw in term

def score_hutbe(kw_list, title, summary):
    text_extra = (title + " " + summary).lower()
    kw_lower = list(dict.fromkeys(k.lower() for k in kw_list))  # dedupe, preserve order
    scores = {}
    for axis, terms in AXES.items():
        s = 0
        matched_kw = set()
        for kw in kw_lower:
            if kw in matched_kw:
                continue
            if any(matches(t.lower(), kw) for t in terms):
                s += 3
                matched_kw.add(kw)
        # small text-level signal (capped contribution, doesn't dominate keyword signal)
        text_hits = sum(1 for t in terms if t.lower() in text_extra)
        s += min(text_hits, 3)
        scores[axis] = s
    return scores

results = {}
for date, rec in d['full_texts'].items():
    scores = score_hutbe(rec.get('keywords', []), rec.get('title',''), rec.get('summary',''))
    ranked = sorted(scores.items(), key=lambda x: -x[1])
    top_score = ranked[0][1]
    if top_score == 0:
        old_cat = rec.get('category','')
        primary = FALLBACK.get(old_cat, "Sabır, Tevekkül ve Manevi Olgunluk")
        secondary = []
    else:
        primary = ranked[0][0]
        secondary = [a for a,s in ranked[1:] if s >= max(3, top_score*0.5)][:2]
    results[date] = {"primary": primary, "secondary": secondary, "scores": dict(ranked[:5])}

json.dump(results, open("/sessions/happy-trusting-turing/mnt/outputs/hutbe_work/new_theme_assignment.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)

dist = collections.Counter(r['primary'] for r in results.values())
print("=== Ana tema dağılımı ===")
for cat, cnt in dist.most_common():
    print(f"{cnt:4d}  {cat}")
print("\nToplam:", sum(dist.values()))
print("İkincil tema ortalama:", sum(len(r['secondary']) for r in results.values())/len(results))
print("İkincil teması olmayan:", sum(1 for r in results.values() if not r['secondary']))
