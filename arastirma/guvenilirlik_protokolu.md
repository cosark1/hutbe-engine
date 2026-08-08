# İP-2 · Güvenilirlik Ölçümü Protokolü

**Sürüm:** v1.0 · 19.07.2026 · Bağlı belge: [kod_kitabi.md](kod_kitabi.md) v1.0

## 1. Amaç
Kod kitabı v1.0'ın, birbirinden bağımsız etiketçiler elinde aynı sonucu üretip üretmediğini ölçmek. Eşikler:
- Krippendorff α (veya Cohen κ) **≥ 0.80** → şema güvenilir, korpus yayımlanabilir
- **0.67 – 0.80** → kabul edilebilir; sorunlu kategoriler için kod kitabına revizyon notu
- **< 0.67** → ilgili kategori tanımları revize edilir (v1.1), ölçüm o kategorilerde tekrarlanır

## 2. Örneklem
- `sec_orneklem.py` (SEED=42) ile seçilen **200 hutbe**; ana kategoriye orantılı tabakalı, tabaka başına ≥5, tabaka içinde tarihe göre sistematik seçim (yıl yayılımı).
- Dosyalar: `guvenilirlik_orneklem_kor.csv` (etiketçi sürümü — etiket yok), `guvenilirlik_orneklem_anahtar.csv` (orijinal etiketler; **etiketleme bitmeden etiketçiyle paylaşılmaz**).

## 3. Körlük kuralları
1. Etiketçiye verilecek girdi **yalnızca**: sıra no, tarih, başlık, tam metin. `hazirla_kor_metinler.py` bu paketi üretir (`guvenilirlik_kor_metinler.json`).
2. ⚠️ `site/data/metinler/{yıl}.json` dosyaları kategori/özet/anahtar kelime alanlarını da içerir — etiketçi bu dosyaları **doğrudan açmaz**, yalnızca kör paketi kullanır.
3. Etiketçi kod kitabı v1.0'ın tamamına erişir; başka hiçbir korpus istatistiğine (kategori dağılımı vb.) bakmaz.
4. LLM etiketçi kullanılıyorsa **taze oturum/bağlam** açılır: bağlamda yalnız kod kitabı + kör paket bulunur. Aynı oturumda korpusun orijinal etiketleri görülmüşse o oturum etiketçi olamaz.

## 4. Etiketleme görevi
Her hutbe için, kod kitabı §3 kurallarıyla:
- `ana_kategori` (15 kategoriden tam olarak 1)
- `ikincil_kategoriler` (0–2; §3.1/2 paragraf kuralına göre)
Çıktı formatı: `sira, ana_kategori, ikincil_kategoriler` ("; " ile ayrık) CSV.

## 5. Karşılaştırma ve metrikler
`hesapla_uyum.py` ile:
- **Ana kategori:** ham uyum yüzdesi + Cohen κ (nominal). 200 birim, 15 kategori için κ güven aralığı bootstrap (1000 örnek) ile raporlanır.
- **İkincil kategoriler:** küme karşılaştırması — Jaccard ortalaması; ayrıca "tam eşleşme" oranı. (MASI mesafeli Krippendorff α, İP-3'te çok-etiketli şemaya geçilirse eklenir.)
- **Kategori bazında:** her kategori için ayrı uyum/karışıklık satırı; en çok karışan çiftler kod kitabı sınır kurallarına geri beslenir.

## 6. Turlar
| Tur | Etiketçi | Kapsam | Amaç |
|---|---|---|---|
| Pilot | LLM (bu proje oturumu) | 20 hutbe (sıra 1, 11, 21, … 191) | Süreç testi + ilk sinyal |
| Tur 1 | Bağımsız LLM (taze oturum) | 200 | Asıl ölçüm |
| Tur 2 (önerilen) | İnsan (alan bilgisi olan) | 200'den alt-örneklem ≥50 | İnsan–LLM uyumu |

## 7. Bilinen sınırlılıklar
- **Pilot kontaminasyonu:** Pilot etiketçisi (bu oturumdaki model) kod kitabını korpusun kendisinden türettiği için tam bağımsız değildir; korpus kategori dağılımını ve bazı örnek başlıkların etiketlerini görmüştür. Pilot sonuçları **yalnızca süreç testi** sayılır, raporlanacak asıl metrik Tur 1'den gelir.
- Orijinal etiketler de LLM üretimidir; Tur 1 "LLM–LLM tutarlılığı" ölçer. İnsan doğrulaması (Tur 2) yayın için gereklidir.
