# Hutbe Analiz Sitesi — Yenileme Planı

> **Devamı:** Site yenilemesi (Faz 1–3) tamamlandı. Araştırma programı (Faz 4+: kod kitabı, güvenilirlik, karşılaştırmalı korpus, etki analizleri) ayrı dosyada izleniyor → [arastirma_programi.md](arastirma_programi.md)

> **Uygulama durumu: Faz 1, Faz 2 ve Faz 3'ün tamamı uygulandı.** Yeni site `hutbe/site/` klasöründe (`index.html + css/ + js/ + data/ + pipeline/`). Eski tek dosyalık `hutbe_dashboard.html` yedek olarak korunuyor.
>
> **Önemli — nasıl açılır:** Yeni site artık veri dosyalarını `fetch()` ile ayrı ayrı yüklediği için tarayıcılar güvenlik nedeniyle dosyayı doğrudan çift tıklayarak (`file://`) açmaya izin vermez. İki seçenek:
> 1. **Yerel önizleme:** `hutbe/site` klasöründe bir terminal açıp `python3 -m http.server 8000` çalıştırın, sonra tarayıcıda `http://localhost:8000` adresine gidin.
> 2. **Barındırma:** Klasörü olduğu gibi GitHub Pages veya Netlify'a yükleyin (Faz 1.5'te planlandığı gibi) — statik dosyalar oldukları için ek bir sunucu kurulumu gerekmez.

Mevcut durum (yenileme öncesi): 2011–2025 Diyanet hutbelerini kapsayan, tüm verinin içine gömülü olduğu ~4.9 MB'lık tek dosyalık HTML dashboard (`hutbe_dashboard.html`). İçerik ve analizler güçlü; mimari, tasarım ve içerik derinliği açısından yenilendi (aşağıdaki plan uygulandı).

Plan üç fazdan oluşur: **Faz 1 — Mimari**, **Faz 2 — Tasarım**, **Faz 3 — Yeni İçerik**. Fazlar sıralı ilerler çünkü yeni içerik ve tasarım, ayrıştırılmış veri katmanının üzerine çok daha kolay inşa edilir.

---

## Faz 1 — Mimari Yeniden Yapılandırma

### 1.1 Veri katmanının ayrıştırılması
- Gömülü `const DATA` nesnesi parçalanır ve ayrı JSON dosyalarına taşınır:
  - `data/hutbeler.json` — tarih, başlık, kategori, özet, anahtar kelimeler, atıf sayıları (tam metin HARİÇ)
  - `data/metinler/{yil}.json` — hutbe tam metinleri, yıl bazında bölünmüş; yalnızca detay sayfası açılınca yüklenir (lazy load)
  - `data/ayetler.json`, `data/hadisler.json`, `data/sahabeler.json`, `data/kelimeler.json` — mevcut CSV'lerdeki analiz tablolarının JSON karşılıkları
- Hedef: ilk sayfa yüklemesi 4.9 MB → ~250 KB.

### 1.2 Veri boru hattı (pipeline)
Yeni yıl PDF'i geldiğinde tek komutla güncellenebilir, tekrarlanabilir bir zincir:

1. `01_extract.py` — PDF → ham metin (pdfplumber)
2. `02_parse.py` — ham metin → hutbe kayıtları (tarih, başlık, gövde ayrıştırma)
3. `03_annotate.py` — LLM ile özet, kategori, anahtar kelime, ayet/hadis/sahabe tespiti
4. `04_validate.py` — tarih formatı, kategori sözlüğü, atıf tutarlılığı kontrolleri; hatalı kayıtları rapor eder
5. `05_build.py` — doğrulanmış kayıtlardan `data/` JSON'larını üretir

Mevcut `hutbe_work/` scriptleri bu yapıya taşınır ve klasör `pipeline/` olarak yeniden düzenlenir.

### 1.3 Ön yüz modülerleştirme
Framework yok, vanilla JS korunur; tek dev script şu modüllere bölünür:

- `js/state.js` — aktif filtreler (yıl aralığı, kategori, arama) tek merkezde; her değişiklik tek `render()` çağrısını tetikler
- `js/data.js` — fetch, önbellekleme, lazy load
- `js/charts.js` — Chart.js kurulum ve güncelleme
- `js/tables.js` — **tek** `createDataTable(config)` fabrikası; ayet/hadis/sahabe/kelime tablolarındaki kopya arama+sayfalama+filtre kodu buradan üretilir
- `js/modal.js`, `js/heatmap.js`, `js/tagcloud.js`
- `css/style.css` — stiller HTML'den ayrılır

### 1.4 Paylaşım ve dışa aktarma
- URL hash ile durum kodlama (`#yil=2015-2020&kategori=aile`) → filtreli görünüm link olarak paylaşılabilir
- Her tablo ve grafiğe "CSV indir" butonu

### 1.5 Barındırma
- Statik site: GitHub Pages veya Netlify
- Yıllık güncelleme = pipeline çalıştır + yeni JSON'ları push et

**Faz 1 çıktısı:** `index.html + css/ + js/ + data/ + pipeline/` yapısında, aynı işlevselliğe sahip ama hızlı ve bakımı kolay site.

---

## Faz 2 — Görsel Tasarım Yenilemesi

### 2.1 Tipografi
- Başlıklar: karakterli bir serif (Lora veya Playfair Display, Google Fonts)
- Gövde ve arayüz: Inter
- Ayet/hadis metinleri: ayrı alıntı stili — hafif italik, sol kenar çizgisi, krem zemin
- Hutbe okuma görünümünde satır genişliği ~65 karakterle sınırlanır

### 2.2 Renk kimliği
- Ana palet: koyu petrol yeşili veya gece mavisi zemin vurguları + altın/kehribar aksan + kırık beyaz kartlar
- Kategori renkleri rastgele palet yerine anlamlı skala: ibadet temaları sıcak tonlar, toplumsal temalar soğuk tonlar
- Karanlık mod (CSS değişkenleriyle, tek geçiş düğmesi)

### 2.3 Sayfa yapısı ve hiyerarşi
- Bölümlere ayrılmış tek sayfa + yapışkan (sticky) bölüm menüsü: **Genel Bakış / Temalar / Kaynaklar / Arşiv**
- KPI kartlarına mini sparkline'lar (sayı + 15 yıllık eğilim tek bakışta)
- Mobilde filtre çubuğu açılır panele taşınır

### 2.4 Bileşen iyileştirmeleri
- Heatmap: çok renkli yerine tek renkli yoğunluk skalası; mobilde yatay kaydırma
- Tablolar: zebra çizgileri, satır hover, sayfalama yerine "daha fazla yükle"
- Grafikler: animasyon azaltılır, tooltip'ler zenginleştirilir (yüzde + örnek hutbe başlığı)
- Arama: Türkçe karakter normalizasyonu (İ/i, ı/I sorunlarının çözümü)

**Faz 2 çıktısı:** Kimlikli, okunaklı, mobil uyumlu arayüz.

---

## Faz 3 — Yeni İçerik ve Analizler

Öncelik sırasına göre (etki/emek oranı en yüksekten):

### 3.1 Takvim–gündem bağlantısı ⭐ öncelikli
- Dini günler takvimi (Ramazan, Kandiller, Kurban, Mevlid) hutbe tarihleriyle eşleştirilir
- Büyük olaylarla ilişkilendirme: pandemi (2020–21), 2023 depremi, ekonomik dönemler
- Görünüm: yatay zaman çizelgesi; olay işaretleri + o dönemin tema dağılımı
- Örnek sorular: "Ramazan haftalarında hangi temalar öne çıkıyor?", "Deprem sonrası söylem nasıl değişti?"
- Yeni etiketleme gerektirmez; tarih verisi + hazır dini takvim yeter

### 3.2 Yükselen–düşen kelimeler ⭐ öncelikli
- Yıllara göre kelime frekans trendi; "son 3 yılda 5 kat arttı" / "2018'den beri hiç geçmiyor" listeleri
- Seçilmiş kavramlar için trend çizgileri: aile, gençlik, israf, sabır, birlik...
- Mevcut anahtar kelime verisinden hesaplanır

### 3.3 Ayet–hadis kullanım derinliği
- **Sure kapsam haritası:** 114 surelik grid; hiç atıf yapılmayanlar, en yoğun kullanılanlar
- Aynı ayetin farklı temalardaki bağlamları
- En sık birlikte geçen ayet–hadis ikilileri

### 3.4 Serbest metin arama (concordance)
- Hutbe tam metinlerinde arama; sonuçta kelimenin geçtiği cümle vurgulu gösterilir
- Faz 1'deki lazy-load metin dosyaları üzerinde istemci tarafı indeks (ör. basit ters indeks veya FlexSearch)

### 3.5 Karşılaştırma modu
- İki yıl veya iki kategori yan yana: tema dağılımı, ortak/farklı anahtar kelimeler, atıf profilleri

### 3.6 Hutbe okuma sayfası
- Modal yerine her hutbeye kalıcı görünüm: tam metin, ayet/hadis vurgulama, benzer hutbeler, haftanın bağlamı (dini gün/olay)
- URL hash ile doğrudan bağlantı verilebilir

### 3.7 Söylem/dil metrikleri (opsiyonel, son sırada)
- Yıllara göre ortalama hutbe uzunluğu, cümle uzunluğu
- Kelime çeşitliliği (type-token oranı) trendi

---

## Uygulama Sırası ve Kilometre Taşları

| Adım | İş | Bağımlılık |
|---|---|---|
| 1 | Veri ayrıştırma + JSON üretimi (1.1, 1.2) | — |
| 2 | Modüler ön yüz iskeleti, mevcut işlevlerin taşınması (1.3) | 1 |
| 3 | URL hash + CSV indirme (1.4) | 2 |
| 4 | Tipografi + renk + karanlık mod (2.1–2.2) | 2 |
| 5 | Sayfa yapısı + bileşen iyileştirmeleri (2.3–2.4) | 4 |
| 6 | Takvim–gündem + yükselen-düşen kelimeler (3.1–3.2) | 2 |
| 7 | Sure haritası + ayet-hadis derinliği (3.3) | 2 |
| 8 | Metin arama + okuma sayfası (3.4, 3.6) | 1 (metin JSON'ları) |
| 9 | Karşılaştırma modu + dil metrikleri (3.5, 3.7) | 6 |
| 10 | Yayınlama (GitHub Pages/Netlify) + son test | hepsi |

Her kilometre taşında site çalışır durumda kalır; mevcut `hutbe_dashboard.html` yedek olarak korunur.
