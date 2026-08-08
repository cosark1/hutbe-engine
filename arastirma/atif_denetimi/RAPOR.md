# Ayet ve Hadis Atıf Denetimi — Rapor

**Tarih:** 03.08.2026
**Kapsam:** `ayet_tam_metin.csv` (243 satır), `hadis_tam_metin.csv` (640 satır),
`site/data/ayetler.json` (648), `site/data/hadisler.json` (819)
**Doğruluk ölçütü:** Hutbelerin kendi dipnotları (703 hutbe metni)
**Betikler:** `arastirma/denetle_atiflar.py`, `arastirma/normalize_bolum_adlari.py`,
`arastirma/uret_turev_dosyalar.py`

---

## 1. Kök neden

Bildirilen iki hata da doğrulandı ve **tek bir ortak arıza değil, dört ayrı arıza**
olduğu ortaya çıktı. Ortak nokta: alıntının kendi dipnot numarası yerine yakınındaki
başka bir dipnotun kullanılması.

### (1) Birleşik hutbe bloğu — bildirilen 1. hata

Eski metin çıkarımında **birden çok hutbe tek kayıtta birleşmişti**. Dipnot numarası
o kaydın *sonundaki* listede arandığı için, birleşik bloğun ilk hutbesindeki alıntılar
**ikinci hutbenin dipnot listesinden** numara aldı.

23.03.2018 "İBADET HAYATIMIZ VE GÖNÜL DÜNYAMIZ" hutbesi 30.03.2018 hutbesiyle birleşmişti:

| | 23.03.2018 dipnotları (doğru) | 30.03.2018 dipnotları (kullanılan) |
|---|---|---|
| 3 | **Fâtiha, 1/5** | Zümer, 39/9 |

Alıntı `"Ancak sana ibadet eder ve ancak senden yardım dileriz"³` → dipnot 3 →
yanlış listeden **Zümer 39/9** okundu. Doğrusu **Fâtiha 1/5**. ✔ düzeltildi

### (2) Dipnotsuz alıntı — bildirilen 2. hata

Kapanış duaları çoğu hutbede dipnotsuzdur. Eski çıkarım bunlara **en yakın dipnotu**
atadı. 20.11.2015 hutbesinde yalnızca 2 dipnot var (1 İbrahim 14/3, 2 Tirmizî İmân 12);
kapanış duası `"Rabbimiz! İlmimizi, anlayışımızı artır..."` dipnotsuz olduğu hâlde
**İbrahim 14/3** etiketi aldı. Doğrusu **Tâhâ 20/114** ("Rabbi zidnî ilmen"). ✔ düzeltildi

> Denetim betiğinin ilk sürümü bu satırı yanlışlıkla "doğru" saydı: kapanış tırnağından
> sonraki boşluk serbest bırakılınca **dipnot listesinin kendi "1" numarası** alıntının
> işaretçisi sanılıyordu. Düzeltildi — işaretçi ile tırnak arasında satır sonu olamaz ve
> alıntı dipnot bloğundan önce bitmelidir.

### (3) Tür karışması

13 satırda ayet dosyasında hadis, hadis dosyasında ayet vardı. Örnek: `Necm, 1` diye
etiketlenen `"İyilik güzel ahlâktır..."` aslında **Müslim, Birr, 14**; `İbn Mâce, Sunne`
diye etiketlenen `"Ey Rabbimiz! Bizim günahlarımızı... bağışla"` aslında **Âl-i İmrân 3/147**.

### (4) Kırpılmış bölüm adları

Eski `02_citations.py` bölüm adı deseni `â/î/û` harflerini tanımıyordu; ad ilk aksanlı
harfte kesiliyordu: `Rikâk→Rik`, `Sıfatü'l-kıyâme→Sıfatü'l-kıy`, `Sıyâm→Sıy`, `Îmân→İm`.
Bu bir yanlış atıf değil ama paylaşım kartında "Buhârî, Rik" gibi bozuk görünüyordu.

---

## 2. Sonuçlar

### ayet_tam_metin.csv — 243 satır

| Durum | Satır |
|---|---|
| doğru | 232 |
| **HATALI** (gerçek yanlış atıf) | **4** |
| tür hatası (aslında hadis) | 3 |
| dipnotsuz (elle karara bırakıldı) | 3 |
| alıntı bulunamadı | 1 |

Gerçek yanlış atıflar:

| Satır | Eski | Doğru | Dipnot |
|---|---|---|---|
| 24 | Zümer 9 | **Fâtiha 5** | `Fâtiha, 1/5.` |
| 101 | Haşr 18 | **Mâide 48** | `Mâide, 5/48.` |
| 211 | Mâide 105 | **Hicr 99** | `Hicr, 15/99.` |
| 221 | Nasr 1 | **Mutaffifîn 1** | `Mutaffifîn, 83/1-6.` |

### hadis_tam_metin.csv — 640 satır

| Durum | Satır |
|---|---|
| doğru | 253 |
| kırpılmış bölüm adı tamamlandı | 299 |
| eksik bölüm adı ("-") dolduruldu | 47 |
| **HATALI** (gerçek yanlış atıf) | **13** |
| tür hatası (aslında ayet) | 10 |
| cilt numarası bölüm sanılmış ("II") | 8 |
| yazım farkı ("el-" öneki) | 6 |
| dipnotsuz / alıntı bulunamadı | 4 |

Gerçek yanlış atıflara örnek: `Tirmizî, Kıraat` → **İbn Mâce, Nikah** ("En hayırlınız
ailesine en güzel davranandır"), `Müslim, Sal` → **Buhârî, Mezâlim** ("Zulüm, kıyâmet
günü karanlıklardır"), `Buhârî, Zekat` → **İbn Mâce, Ticaret**.

### Özet

- **Gerçek yanlış atıf: 17** (ayet 4 + hadis 13) — hepsi düzeltildi
- **Tür karışması: 13** — satırlar doğru dosyaya taşındı
- **Biçim kusuru: 360** (kırpılma 299 + eksik 47 + cilt 8 + yazım 6) — düzeltildi
- **Kutsal metin olmayan 2 satır silindi:**
  - `"Ey velâdeti yeryüzünün baharı..."` — hutbe yazarının Peygamber'e kendi hitabı,
    ayet olarak etiketlenmişti (03.02.2012)
  - `"Eline, diline, beline sahip ol!"` — hutbede açıkça "Ahilik Müessesesi'nin
    öğütleri" diye tanıtılan Ahi nasihati, hadis olarak etiketlenmişti (17.09.2021)
- **21 satırın tarihi/başlığı/teması** düzeltildi (birleşik blok yan etkisi)

### site/data

| Dosya | Önce | Sonra | Değişiklik |
|---|---|---|---|
| `ayetler.json` | 648 | 654 | 15 |
| `hadisler.json` | 819 | 811 | 433 |

Bu dosyalar CSV'lerin üst kümesidir (`07_fill_missing_citations.py` atfı olmayan
hutbeler için satır eklemişti), bu yüzden CSV'den yeniden üretilmedi; aynı denetimden
geçirildi.

---

## 3. Yan bulgular

**a) Korpus eksiği — 12 hutbe.** `site/data/metinler/` bayram hutbelerinin bir kısmını
içermiyor: aynı güne hem cuma hem bayram hutbesi düştüğünde yalnızca biri saklanmış
(17.07.2015, 15.06.2018, 21.04.2023 …). Bu hutbeler `hutbeler_veriseti.csv` içinde
duruyor; denetimde oradan alt-hutbelere bölünüp kullanıldı. **Korpus 691 değil, en az
703 hutbe olmalı** — ayrı bir düzeltme turu gerektirir.

**b) Türev dosyalar zaten bayattı.** `ayet_atif_siralamasi.csv`, `sure_atif_siralamasi.csv`
ve tema çaprazları 3 Temmuz tarihliydi; 20-21 Temmuz'daki atıf tamamlama ve 2026
genişletmesinden sonra hiç yeniden üretilmemişti. Atıf hatasından bağımsız olarak
sayılar sapmıştı (Bakara 160 → 83, Âl-i İmrân 20 → 66). Hepsi yeniden üretildi.

**c) Bölüm adı yazım varyantları.** Aynı bölüm 9 farklı yazılabiliyordu
(`Sıfatu'l Kıyâme`, `Sıfatü'l- Kıyâme`, `Sıfâtü'l-kıyâme` …). 46 varyant tek biçime
indirgendi; benzersiz hadis bölümü sayısı **209 → 159**. Ahmed b. Hanbel atıflarında
boş kalan bölüm alanı `Müsned` yapıldı.

**d) `02_citations.py` ve `07_fill_missing_citations.py` hâlâ eski desenleri kullanıyor.**
Yeni yıl eklendiğinde aynı kırpılma tekrar oluşur. Bu denetimdeki `split_source()` /
`clean_bolum()` mantığının boru hattına taşınması gerekir. **Yapılmadı — ayrı iş.**

**e) `tema` sütunu iki sözlük karışımı.** Satır CSV'lerindeki `tema` eski ince şemayı
("Namaz ve İbadet"), türev dosyalar 15'li şemayı kullanıyor. Tarihi düzeltilen 21 satır
15'li şemadan değer aldı; sütun artık karışık. Tamamının normalize edilmesi ayrı bir
karar gerektirir. **Yapılmadı.**

---

## 4. Elle verilen kararlar

Dipnotu olmayan veya alıntısı bulunamayan 8 satır otomatik çözülemedi; kararlar
gerekçeleriyle `elle_kararlar.csv` dosyasında tutuluyor ve betik tarafından uygulanıyor.
Bunlardan biri (`hadis` 501, Berat gecesi hadisi) korpusta birden çok hutbede geçtiği
için otomatik eşleştirmeye bırakılmadı; kaynağı 29.05.2015 "TEVBEMİZ BERATIMIZ OLSUN"
hutbesinin 2 nolu dipnotudur: `İbn Mâce, İkâmetü's-Salavât, 191`.

---

## 5. Üretilen dosyalar

**Denetim izi** (`arastirma/atif_denetimi/`)
`ayet_denetim.csv`, `hadis_denetim.csv` — satır satır karar, skor, dipnot, kaynak hutbe
`degisiklik_gunlugu.csv`, `site_ayet_degisiklik.csv`, `site_hadis_degisiklik.csv`
`elle_kararlar.csv`, `ozet.json`

**Düzeltilen** (yedekleri `.bak-preAtifDenetimi` / `.bak-preBolumNorm` ile duruyor)
`ayet_tam_metin.csv` (249), `hadis_tam_metin.csv` (632)
`site/data/ayetler.json` (654), `site/data/hadisler.json` (811), `site/data/meta.json`

**Yeniden üretilen türevler**
`ayet_atif_siralamasi.csv`, `sure_atif_siralamasi.csv`, `ayet_x_tema.csv`,
`hadis_siralamasi.csv`, `hadis_kaynak_siralamasi.csv`, `hadis_x_tema.csv`,
`hadis_kaynak_x_tema.csv`

---

## 6. Doğrulama — düzeltilmiş korpusun yeniden denetimi

Betik düzeltilmiş dosyalar üzerinde yeniden çalıştırıldığında:

| Dosya | Sonuç |
|---|---|
| `ayet_tam_metin.csv` (249) | 246 doğru + 3 dipnotsuz/bulunamayan (elle karar verilmiş satırlar) |
| `hadis_tam_metin.csv` (632) | 550 doğru + 79 bilinçli normalizasyon + 3 elle karar |

Hadisteki 79 fark **hata değil, kasıtlı normalizasyondur** ve yeniden çalıştırmada
tekrar "farklı" görünür:

- **67 + 11** — bölüm adı kanonik yazıma çekildi; ilgili dipnot başka bir varyantı
  yazıyor (`Bedʾü'l-vahy` → `Bed'ü'l-vahy`, `Cihad` → `Cihâd` …)
- **11** — Ahmed b. Hanbel atıflarında dipnot cilt/sayfa verdiği için bölüm alanı boştu;
  görüntüleme için `Müsned` yazıldı

Bu farkların dipnot metniyle *bilinçli* olarak ayrıştığı unutulmamalı; ileride betik
tekrar çalıştırılırsa bu satırlar yeni hata sanılmamalıdır.

---

## 7. Takip — açık uçların kapatılması (03.08.2026, aynı gün ikinci tur)

Bölüm 2'de listelenen üç açık uç kapatıldı:

**a) Boru hattı regex düzeltmesi.** `site/pipeline/{02_citations,07_fill_missing_citations,
08_integrate_new_hutbe}.py`'deki hadis kaynağı/bölüm ayrıştırıcısı `split_hadith_ref()`
ile değiştirildi. Eski desen üç durumu kaçırıyordu: kaynak-bölüm arasında virgül
olmaması ("Tirmizi Birr, 15."), "el-" önekli eser adları ("el-Mu'cemü'l-evsat"),
cilt/sayfa numarasının bölüm sanılması ("İbn Hanbel, II, 400."). Ayrıca
`extract_title_and_body_start()`/`extract_title()`'daki üstbilgi-sınırı deseni
yalnız nokta ayraçlı tarihleri ("31.07.2015") tanıyordu, eğik çizgili
("31/07/2015") tarihlerde üstbilginin kendisini başlık sanıyordu — düzeltildi.

**b) Eksik hutbeler.** "12 eksik" tahmini yanlış çıktı. Tüm 15 yıllık PDF
sayfa-bazlı sistematik tarandı (`sistematik_tarama.py`): adayların **4'ü yanlış
pozitifti** (hutbeler_veriseti.csv'nin kaba metin bölmesinin aynı hutbenin ortasından
yanlışlıkla ikinci "başlık" çıkardığı fragmanlar — 13.04.2018, 20.09.2019,
15.07.2022, 12.07.2024), ama **2015'in 02.01–06.03 arası 10 haftası tamamen
korpustan eksikti** (gizli birleşim değil, düpedüz kayıp veri). Gerçek eksik: **20
hutbe** (2015: 15, 2017/2018/2020/2023/2025: birer). Her biri `01_extract.py`/
`08_integrate_new_hutbe.py` mantığıyla (paragraf yeniden inşası + dipnot/atıf
çıkarımı) PDF'lerden temiz çıkarıldı, tam metin okunarak kod kitabına göre
etiketlendi (kategori, çerçeve, ton, muhatap, eylem çağrısı, özet, anahtar
kelimeler) ve `08_integrate_new_hutbe.py`'nin `integrate()`/`recompute_meta()`
fonksiyonlarıyla `site/data/*.json`, `arastirma/korpus_v2/*` ve `hutbe_kategori_analizi.csv`
soyundan gelen her yere işlendi. **Korpus artık 691 değil 711 hutbe.**
Entegrasyon sırasında 20 hutbenin tamamının atıfları sıfır çözümlenemeyen
sonuçla eklendi.

Bilinen kalan sınırlama — **2011-2014 PDF'lerinde sayfa-bazlı tarayıcı yalnız
7/10/27/42 kayıt buluyor** (beklenenin çok altında); bu ya farklı bir PDF
yapısından (sayfa başına birden çok hutbe) ya da gerçek bir arşiv boşluğundan
kaynaklanıyor, ayrı bir teşhis gerektiriyor. Kullanıcı onayıyla bu turun
kapsamı dışında bırakıldı.

**c) Tema şeması birleştirmesi.** `ayet_tam_metin.csv`/`hadis_tam_metin.csv`
artık ayrı, bayat bir `hutbe_kategori_analizi.csv` sözlüğünden değil, doğrudan
`site/data/{ayetler,hadisler}.json` kayıtlarının `category` alanından (15'li
şema, tek kaynak) üretiliyor (`uret_turev_dosyalar.py` yeniden yazıldı). Bu
aynı zamanda CSV'lerin JSON'dan **tarihsel olarak sürüklenmiş** olmasını da
düzeltti: `ayet_tam_metin.csv` uzun süredir `ayetler.json`'dan çok daha küçüktü
(243'e karşı 648) çünkü `07_fill_missing_citations.py` yalnız JSON'lara yazıyordu,
CSV'lere hiç dokunmuyordu. Artık tek doğruluk kaynağı var: 668 ayet + 814 hadis
atfı (20 yeni hutbe dahil, aşağıdaki tekilleştirmeden sonra).

**Yan bulgu — 26 tam yinelenen kayıt.** Tarih düzeltmesi uygulanan atıflar
bazen hedef hutbede zaten doğru şekilde var olan bir kaydın birebir kopyasını
oluşturdu (ör. Berat gecesi hadisi hem düzeltilmiş eski kayıtta hem
29.05.2015'in kendi çıkarımında). Genel bir tekilleştirme geçişiyle giderildi
(`sure/kaynak+ayet/bölüm+tarih+alıntı` birebir eşleşmesi); 677→668 ayet,
831→814 hadis.

**Doğrulama.** Düzeltilmiş+genişletilmiş korpus üzerinde denetim yeniden
çalıştırıldı: 711 hutbe, sıfır sahte "ek" kayıt, ayet 665/668 doğru (3 satır
önceden elle karara bağlanmış sınır durumu), hadis 737/814 doğru + 73 bilinçli
bölüm-adı normalizasyonu (2 satır bulunamadı, 1 kozmetik Unicode apostrof
varyantı, 1 zaten doğrulanmış Berat hadisi).

---

## 8. Kalan risk

Denetim **hutbelerin kendi dipnotlarını** ölçüt alır. Dipnotun kendisi yanlışsa
korpus da yanlış kalır. Örnek: 15.07.2016 hutbesinde `"Allah katında amellerin en
sevimlisi, az da olsa devamlı olanıdır"` için Diyanet'in verdiği dipnot
`Buhârî, Libâs, 43` — bu hadisin bilinen yeri Buhârî, Rikâk 18 / Müslim, Müsâfirîn 215.
Korpus kaynağa sadık kalarak dipnottaki değeri taşır. Bu tür sapmaların ayrı bir
"kaynak dipnotu şüpheli" taraması akademik yayın için değerli olabilir — **yapılmadı.**

**Yeni 20 hutbe `weekly_grid`/`baglam_takvimi`'ye işlenmedi.** 2026 partisi
entegrasyonunda da aynı sınırlama yaşanmıştı (bkz. `arastirma_programi.md`
21.07.2026 günlüğü): `recompute_meta()` bu iki yapıyı kasıtlı olarak
genişletmiyor. Isı haritası ve bağlam zaman çizelgesi kartlarında 2015'in
Ocak-Mart haftaları ve diğer 5 yeni hutbe tarihi boş hücre olarak görünecektir
— site fonksiyonel kalır, yalnızca bu iki görselleştirme eksik kalır. Ayrı bir
iş.

**2011-2014 kapsam şüphesi teşhis edilmedi.** Bkz. §7 — kullanıcı onayıyla bu
turun dışında bırakıldı.
