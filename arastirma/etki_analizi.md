# İP-8 · Etki Tasarımları (Doğal Deney) — Yöntem, Aday Vakalar ve Veri Erişilebilirliği

**Durum:** Metodoloji ve aday vaka seçimi tamamlandı; ampirik ITS analizi **veri
erişilebilirliği engeliyle** durduruldu (03.08.2026). Bu belge, İP-8'in
"sınırlılıklar bölümü zorunlu" şartını karşılayan bir ara rapor niteliğindedir.

---

## 1. Tasarımın mantığı

Türkiye'deki cuma hutbeleri Diyanet İşleri Başkanlığı tarafından merkezi olarak
yazılır ve aynı hafta, ülke genelindeki ~90.000 camide **eşzamanlı** okunur. Bu,
sosyal bilimlerde nadir bulunan bir yapı sunar: tek bir metnin, tek bir tarihte,
milyonlarca kişiye eşzamanlı ulaştığı bir **doğal deney**. Eğer hutbenin konusu
ölçülebilir, tarihli bir davranışa karşılık geliyorsa (ör. bir bağımlılık
karşıtı hutbe → sigara bırakma danışma hattı aramaları), hutbe öncesi ve
sonrası dönemi karşılaştıran bir **kesikli zaman serisi (interrupted time
series, ITS)** tasarımı kurulabilir:

- **Müdahale noktası (t₀):** hutbenin okunduğu cuma günü
- **Öncesi pencere:** t₀'dan önceki 4-8 hafta (temel eğilim/mevsimsellik)
- **Sonrası pencere:** t₀'dan sonraki 4-8 hafta (seviye/eğim kırılması var mı?)
- **Kontrol değişkenleri:** mevsimsellik (ör. Ocak ayı "yeni yıl kararları"
  etkisi sigara bırakma aramalarını zaten yükseltir), eşzamanlı haberler/
  kampanyalar (confound riski)

Bu tasarımın **iddia edebileceği en güçlü sonuç nedensellik değil,
korelasyondur** — tek bir olayın çevresinde onlarca başka şey de olur
(mevsim, haberler, diğer kurumların kampanyaları). ITS, "hutbe sonrası
seviyede/eğimde anlamlı bir kırılma var mı" sorusuna cevap verir; "bu kırılmayı
hutbe mi yaptı" sorusuna kesin cevap vermez. Kod kitabının `eylem_cagrisi`
alanındaki `maddi` ve `katılım` değerleri (bkz. `kod_kitabi.md` §4.4) bu
tasarımın girdisi olarak düşünülmüştü — bağış/katılım verisiyle eşleşen
hutbeler en güçlü adaylardır.

## 2. Aday vakalar (korpustan seçildi)

Korpus (711 hutbe) tam metin taranarak "tek bir tarihte, tek bir davranışa
adanmış" nitelikte 5 hutbe belirlendi. Seçim ölçütü: hutbenin **tamamının**
(vesile paragrafı değil, gövdenin bütünü) tek bir ölçülebilir davranışa
ayrılmış olması — dağınık, çok-temalı hutbeler ITS için zayıf adaydır çünkü
"tedavi" (treatment) net değildir.

| # | Tarih | Başlık | Davranışsal odak | Beklenen aday gösterge |
|---|---|---|---|---|
| 1 | 23.02.2018 | BAĞIMLILIK BİR TUZAKTIR | sigara, alkol, uyuşturucu, kumar, internet/telefon bağımlılığı | Yeşilay ALO 191 danışma hattı arama hacmi; "bağımlılık", "sigara bırakma" Google Trends |
| 2 | 01.03.2024 | ZARARLI ALIŞKANLIKLARIN ESİRİ OLMAYALIM | alkol, uyuşturucu (2018'in güncel tekrarı) | Aynı göstergeler, 2024 penceresi |
| 3 | 25.12.2020 | İÇKİ: KÖTÜLÜĞÜN ZEHİRLİ ARKADAŞI | yalnızca alkol (dar, tek-konulu) | Alkollü içecek satış/vergi verisi (TAPDK), "içki bırakma" Trends |
| 4 | 25.01.2013 | ALLAH'IN SEVMEDİĞİ DAVRANIŞ: İSRAF | genel tüketim/israf ahlakı | Zayıf aday — davranış çok genel, tek gösterge yok |
| 5 | 18.07.2025 | SUYUMUZU İSRAF ETMEYELİM | su tüketimi/tasarrufu (dar, tek-konulu, güncel) | Belediye su tüketim istatistikleri (varsa il bazlı) |

**En güçlü iki aday: #1 ve #3.** #1 çok-bağımlılık odaklı olduğu için birden
çok Trends terimiyle çapraz doğrulama imkânı sunar; #3 tek konuya (alkol)
odaklandığı için "tedavi" en netidir. #4 kapsam olarak fazla geniş (israf
hemen her hutbede yan tema olarak geçer, "tek olay" sayılamaz) — aday
listesinden düşürüldü, yalnızca kayıt için tabloda bırakıldı.

**İncelenip elenen adaylar:** organ/kan bağışı (07.11.2025 "VEFA İMANDANDIR")
— yalnızca tek cümlelik bir örnek, adanmış bir kampanya çağrısı değil,
"tedavi" olarak fazla zayıf. Trafik güvenliği (8 hutbede geçiyor, çoğu bayram
vesilesiyle) — tekrarlayan/mevsimsel olduğu için tek-olay ITS mantığına
uymuyor, kendi başına ayrı bir (muhtemelen panel-veri) tasarım gerektirir.

## 3. Veri erişilebilirliği bulguları (03.08.2026)

Üç aday kaynak kategorisi araştırıldı; **üçü de bu ortamda programatik/serbest
erişime kapalı** çıktı:

**a) Google Trends.** Resmi API (`developers.google.com/search/blog/2025/07/
trends-api`) Temmuz 2025'te duyuruldu ama hâlâ başvuru gerektiren kapalı alfa
aşamasında. Toplulukça bakımı yapılan `pytrends` kütüphanesi 17.04.2025'te
arşivlendi/terk edildi. Herkese açık web arayüzü (`trends.google.com`) tarayıcı
üzerinden erişilebilir durumda (test edildi, sayfa açıldı) ama:
  - varsayılan pencere "son 12 ay" — 2018/2020/2024 gibi geçmiş tarih
    aralıklarını URL parametreleriyle ayarlamak ek deneme gerektiriyor,
  - ilk deneme bir istekte `429 Too Many Requests` döndürdü (olası bot-tespiti),
  - veri interaktif bir grafikten geliyor, sayısal değerlerin güvenilir
    çıkarımı (CSV indirme UI akışı veya ağ isteği yakalama) ayrı bir
    mühendislik işi.
  Bu, üç kaynak arasında **en gerçekçi olanı** ama hazır değil.

**b) Organ/doku bağışı istatistikleri.** Sağlık Bakanlığı'nın resmi paneli
(`organkds.saglik.gov.tr/dss/`) incelendi — yalnızca **güncel toplam
sayıları** (kayıtlı gönüllü bağışçı, bekleyen hasta sayısı vb.) gösteren bir
pano; haftalık/aylık **geçmiş** zaman serisi veya indirme özelliği
bulunamadı.

**c) Kan bağışı istatistikleri (Kızılay).** Aynı örüntü — yalnızca dönemsel
basın açıklamalarında (ör. "2025'te 3 milyon ünite hedefi") toplu rakamlar
var; tarihli/indirilebilir bir veri seti bulunamadı.

**Genel örüntü:** Türkiye'deki kamu/STK panoları büyük ölçüde "anlık durum"
gösterge tablosu (dashboard) mantığıyla kurulu, geçmişe dönük zaman serisi
yayımlama alışkanlığı yaygın değil. Bu, yalnızca bu üç kaynağa özgü değil,
muhtemelen İP-8'in aday göstereceği başka kaynaklarda da (TAPDK satış verisi,
belediye su tüketim istatistikleri) karşılaşılacak yapısal bir kısıt.

## 4. Önerilen ileri adımlar (yapılmadı, karar kullanıcıda)

1. **Google Trends'i tarayıcı otomasyonuyla zorlamak** — özel tarih aralığı
   ayarlanıp CSV indirme akışının çalıştırılması; başarılı olursa aday #1/#3
   için gerçek ITS analizi mümkün olur. En düşük maliyetli, en yüksek olası
   getirili seçenek.
2. **Doğrudan kurumsal veri talebi** — Kızılay/Sağlık Bakanlığı'na araştırma
   amaçlı geçmiş veri talebiyle başvurmak (bürokratik süre, akademik ortaklık
   gerektirebilir; bu oturumun kapsamı dışında).
3. **Google Trends resmi API'sine başvuru** — alfa erişim listesine
   girmek (bekleme süresi belirsiz).
4. **Vazgeçilecek göstergeler için vekil (proxy) veri** — ör. haber
   arşivlerinde "sigara bırakma hattı başvuruları arttı" gibi dönemsel
   haberlerin sayımı (zayıf, gürültülü, ama tamamen kapalı değil).

## 5. Sınırlılıklar

- **Nedensellik iddia edilemez.** En iyi ihtimalle bir ITS tasarımı korelasyon/
  zamanlama uyumu gösterir; hutbenin tek başına nedensel etken olduğu
  kanıtlanamaz (eşzamanlı haberler, mevsimsellik, diğer kurumların
  kampanyaları kontrol edilemeyen karıştırıcılardır).
- **Vaka sayısı azlığı.** 5 aday arasından yalnızca 2'si (bkz. §2) gerçekten
  güçlü; bu, bulguların genellenebilirliğini baştan sınırlar.
- **Veri erişilebilirliği, tasarımın kendisinden önce gelen bir engel
  oldu** — bu belge bu yüzden bulgu değil, bir **fizibilite raporu**dur.
- **"Google Trends arama ilgisi" davranış değişikliğinin zayıf bir vekilidir**
  — arama yapmak, gerçekten bırakmak/değiştirmek değildir; en iyi ihtimalle
  "farkındalık" ölçer, "davranış" değil.

---

*Bağımlılık: İP-4 (bağlam eşleştirme tablosu, tamamlandı). Kullanılan araçlar:
korpus tam metin taraması (bu oturumda ad-hoc), WebSearch, tarayıcı testi
(`trends.google.com`).*
