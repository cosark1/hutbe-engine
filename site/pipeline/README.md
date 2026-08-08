# Pipeline — Hutbe Verisi Güncelleme Zinciri

Yeni bir yıl hutbe PDF'i eklendiğinde bu adımları sırayla çalıştırın:

1. **`01_extract.py`** — PDF → ham metin + başlık + tarih + dipnot çıkarımı (PyMuPDF).
2. **`02_citations.py`** — Ayet/hadis/sahabe tespiti; dipnot numaralarını tam alıntı metnine bağlar (114 sure + ~15 hadis kaynağı + ~28 sahabi whitelist'i içerir).
3. **`03_summarize_ref.py`** — Referans: eski extractive özetleme mantığı. Güncel süreçte özetler tam metin okunarak (abstractive) elle/yarı-otomatik üretiliyor; bu dosya sadece footnote/footer temizleme mantığı için referans olarak tutulur.
4. **`04_axes.py`** — 15 ana tema sözlüğünü (`axes.json`) tanımlar. Yeni içerik mevcut temalara düşük skorla eşleşiyorsa önce bu dosyadaki terim listeleri genişletilir.
5. **`05_classify.py`** — Her hutbeye `axes.json` sözlüğünü kullanarak 1 ana + en fazla 2 ikincil tema atar. **Tüm veri setinde** (yalnızca yeni hutbelerde değil) yeniden çalıştırılmalı.
6. **`06_build_data.py`** — Birleşik `dashboard_dataN.json`'dan sitenin `data/` klasöründeki modüler JSON dosyalarını üretir:
   ```
   python3 06_build_data.py dashboard_dataN.json ../data/
   ```

## Yeni yıl eklerken kontrol listesi

- [ ] PDF `01_extract.py` ile işlendi, başlık yakalama oranı %100'e yakın mı?
- [ ] `02_citations.py` çıktısı bir örnek üzerinden manuel doğrulandı mı?
- [ ] Yeni hutbeler için özet + anahtar kelime üretildi mi?
- [ ] `05_classify.py` **tüm** veri seti üzerinde yeniden çalıştırıldı mı?
- [ ] `06_build_data.py` ile `data/` yeniden üretildi mi?
- [ ] Site yerelde (`python3 -m http.server`) açılıp kontrol edildi mi?
