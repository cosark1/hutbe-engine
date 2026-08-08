# Hutbe Korpusu Kod Kitabı (Codebook)

**Sürüm:** v1.4 · 21.07.2026
**Durum:** Yürürlükte — İP-3 (korpus v2) tamamlandı, kod kitabı kararlarıyla korpus artık tutarlı.

Sürüm geçmişi:
- v1.4 (21.07.2026) — İP-2 Tur 2 bulguları (50 hutbe, insan etiketçi, κ=0.540) işlendi: Toplumsal Dayanışma↔Ahlak ve İman↔Sabır/Tevekkül, v1.2'nin "somut alıcı testi"ne rağmen hem Tur 1'de (LLM-LLM) hem Tur 2'de (insan-LLM) en sık karışan çiftler olmaya devam etti — iki bağımsız ölçümün aynı sonuca varması, sorunun kural belirsizliğinden çok bu iki çiftin teolojik olarak iç içe geçmiş olmasından kaynaklandığını gösterdi (bkz. `guvenilirlik_raporu.md` Tur 2 bölümü). Her iki sınıra kesin bir **nihai tie-break kuralı** eklendi (kategori 1 ve 4) — kategorileri birleştirmek/azaltmak yerine, gerçekten 50-50 kalan durumlarda sabit bir varsayılana düşülüyor; bu, ayrımı/bilgiyi korur, yalnızca kararsızlığı ortadan kaldırır. Kategorileri birleştirmek κ'yı "sahte" yükseltirdi (ayrımı ortadan kaldırarak); tie-break bunu yapmıyor.
- v1.2 (20.07.2026) — Tur 1 bulguları (200 hutbe, κ=0.643) işlendi: en sık karışan iki çifte karar işareti eklendi — İman↔Sabır/Tevekkül (kategori 4) ve Toplumsal Dayanışma↔Ahlak (kategori 1/5, "somut alıcı testi"). Bkz. `guvenilirlik_raporu.md` — bu iki sınırdaki uyuşmazlıkların çoğunluğu kural belirsizliğinden (Tür A) değil, orijinal (v1) etiketlerin mevcut kuralla tutarsız olmasından (Tür B) kaynaklanıyor; eklenen işaretler kuralın mekanik uygulanabilirliğini artırmak için.
- v1.1 (19.07.2026) — Pilot bulguları işlendi: vesile kuralı takvim vesileleriyle sınırlandı ve kampanya/duyuru kuralı eklendi (§3.1/3a), İbadet↔İman sınırına karar işareti eklendi (kategori 2), ikincil kategori kuralı sıkılaştırıldı ve orijinal ikincillerin güvenilmezliği not edildi (§3.1/2).
- v1.0 (19.07.2026) — Açık sorular karara bağlandı (§6), şema kesinleşti.
- v0.1 (19.07.2026) — Mevcut etiketlemeden geriye dönük çıkarılan şema + yeni katman tanımları (taslak).

---

## 1. Amaç ve kapsam

Bu belge, 2011–2025 Diyanet Cuma hutbeleri korpusunun etiketleme şemasını tanımlar: her etiketin tanımı, tipik ve sınır örnekleri, karar kuralları. Amaç, etiketlemenin **kim (veya hangi model) yaparsa yapsın aynı sonucu verecek** kadar açık olması; güvenilirlik ölçümü (İP-2) bu belgeye körü körüne bağlı kalınarak yapılır.

## 2. Analiz birimi ve korpus

- **Analiz birimi:** Tek bir Cuma hutbesi metni (başlık + gövde). Kaynak: DİB yıllık hutbe PDF'leri.
- **Korpus (v1):** 637 hutbe, 15.04.2011 – 2025 sonu. Canlı veri: `site/data/hutbeler.json` + `site/data/metinler/{yıl}.json`.
- ⚠️ **Veri notu:** Eski analiz dosyası `genel_kategori_dagilimi.csv` 644 kayıt ve **farklı (20 kategorili) bir şema** içerir; bu şema **kullanımdan kaldırılmıştır**. Geçerli şema aşağıdaki 15 kategoridir. 644↔637 kayıt farkı İP-3'te (korpus v2, kalıcı ID'ler) izlenip açıklanacak.

## 3. Kategori şeması (15 kategori)

### 3.1 Genel atama kuralları

1. **Gövde belirler, başlık değil.** Kategori kararı hutbenin ana argümanına göre verilir; başlık yalnız ipucudur.
2. **Bir ana kategori zorunlu, en fazla iki ikincil kategori.** İkincil kategori ancak o tema hutbenin **en az iki paragrafını veya yaklaşık dörtte birini** kaplıyorsa atanır; tek paragraflık değini (ör. kapanıştaki Gazze duası, tek paragraflık duyuru) yeterli değildir. ⚠️ Orijinal (v1) verideki ikincil etiketler bu kuralla üretilmemiştir ve güvenilir sayılmaz; v2'de ikinciller sıfırdan atanır (pilot bulgusu, `pilot_raporu.md`).
3. **Vesile önceliği kuralı (yalnız takvim vesileleri):** Hutbe belirli bir **takvim** vesilesine (bayram, kandil, üç aylar, milli gün/hafta) bağlı yazılmışsa **vesile kategorisi ana kategori olur**, işlenen tema ikincile düşer. Örnek: Ramazan'da kardeşliği anlatan hutbe → ana: *Ramazan, Oruç ve Bayramlar*; ikincil: *Toplumsal Dayanışma*. Vesileye yalnızca girişte değinilip gövde bağımsız bir temaya ayrılmışsa kural uygulanmaz.
   **3a. Kampanya/duyuru vesile sayılmaz:** DİB kampanyaları, kurs kayıtları, yardım çağrıları ve hafta duyuruları (Kutlu Doğum, Camiler Haftası teması, yaz Kur'an kursu vb.) takvim vesilesi değildir; duyuru hutbenin bir-iki paragrafıyla sınırlıysa ana kategoriyi **gövde teması** belirler. Örnek (pilot, sıra 141): yaz Kur'an kursu çağrısıyla biten ama gövdesi çocuk terbiyesi olan hutbe → ana: *Aile, Çocuk ve Nesil*.
4. **Somut olay önceliği:** Hutbe güncel somut bir olaya (afet, salgın, saldırı, savaş) tepki olarak yazılmışsa ilgili olay kategorisi (*Afet, Kriz ve Sağlık* veya *İslam Coğrafyası* veya *Vatan, Millet ve Tarih*) ana kategori olur.
5. Kararsız kalınan durumda: aşağıdaki sınır kurallarına bak; hâlâ kararsızsa daha **spesifik** kategori kazanır (ör. *Kur'an-ı Kerim* > *İbadet ve Kulluk*).

### 3.2 Kategori tanımları

Her kategori: tanım → tipik örnekler (korpustan) → sınır kuralları.

**1. Toplumsal Dayanışma, Merhamet ve Kardeşlik** (79 hutbe)
Toplum geneline dönük ilişki ahlakı: kardeşlik, merhamet, yardımlaşma, komşuluk, birlik-beraberlik, barış dili.
- Tipik: "MERHAMET EĞİTİMİ" (2011), "KARDEŞLİK ÇAĞRISI" (2012), "SEVGİ VE BARIŞ DİLİ: SELÂM" (2012)
- Sınır — *Aile* ile: ilişkinin sahnesi hane içiyse (eş, çocuk, ebeveyn) → Aile; toplum geneliyse → burası.
- Sınır — *Ahlak* ile: kolektif pratik ve toplumsal bağ vurgusu → burası; bireysel erdem/karakter vurgusu → Ahlak. **Karar işareti (v1.2) — somut alıcı testi:** Hutbe, adı/durumu belirli bir muhtaç kesime (yetim, mülteci, komşu, mazlum, hasta, kardeş...) yönelik somut yardım eylemlerini bir liste hâlinde anlatıyorsa (elini uzatmak, kucak açmak, kusurunu örtmek, ihtiyacını gidermek) → burası, başlıkta "ahlak" kelimesi geçse bile (ör. "KARDEŞLİK AHLAKI VE HUKUKU", Tur 1 sıra 3). Hutbe bir erdemi (doğruluk, güven, hürriyet, iffet, sabır) alıcısı belirtilmeden soyut bir iç nitelik/karakter tanımı olarak işliyorsa → Ahlak, sonucu toplumsal olarak zikredilse bile (ör. "insan emin oldukça ülkeler emin olur" gibi bir sonuç cümlesi kategoriyi değiştirmez; Tur 1 sıra 57 "MÜMİN GÜVENEN VE GÜVENİLEN İNSANDIR"). (Bkz. `guvenilirlik_raporu.md` — Tur 1'de bu çift 6/200 kayıtta karıştı, çoğu Tür B; Tur 2'de 3/50, oransal olarak daha yüksek.) **Nihai tie-break (v1.4):** Yukarıdaki alıcı testi de sonuç vermiyorsa (hutbe hem soyut bir erdemi hem somut bir alıcıya yönelik eylemi dengeli işliyorsa) → ana kategori **Toplumsal Dayanışma**, Ahlak ikincil olarak eklenir. Gerekçe: klasik ahlâk literatüründe güzel ahlakın tarifi zaten ilişkiseldir ("mümin, elinden ve dilinden insanların emin olduğu kişidir" hadisi) — teolojik olarak temel eksen ilişkisel/toplumsaldır, Ahlak onun bireysel görünümüdür, tersi değil.
- Sınır — *Ekonomik Hayat* ile: yardımlaşma zekât/infak/sadaka ekseninde kurgulanmışsa → Ekonomik Hayat.

**2. İbadet ve Kulluk** (66)
Ritüel ibadetler (namaz, dua, hac, kurban) ve genel kulluk bilinci; cami-cemaat teşviki.
- Tipik: "DAVET HEPİMİZE, HEP BİRLİKTE CAMİYE!" (2013), "DUA, İBADETİN ÖZÜDÜR" (2014)
- Sınır — *Ramazan* ile: oruç/teravih/fıtır Ramazan-bayram bağlamında → Ramazan; ibadet genel/takvimden bağımsız anlatılıyorsa → burası.
- Sınır — *İman* ile: ibadetin pratiği/teşviki → burası; ibadetin itikadi temeli (niçin kulluk) → İman. **Karar işareti (v1.1):** hutbenin **kapanış eylem çağrısına** bak — çağrı somut ibadet pratiğine ("namazı aksatmayalım", "ibadetlerimizi eda edelim") dönükse gövdede tevhid/itikat anlatımı geniş yer tutsa bile → İbadet; çağrı inancın kendisine ("imanımızı tazeleyelim", "ahireti unutmayalım") dönükse → İman. (Pilot, sıra 131.)

**3. Aile, Çocuk ve Nesil** (57)
Evlilik, eş ilişkisi, çocuk terbiyesi, kadın (aile bağlamında), nesil endişesi, mahremiyet-aile kesişimi.
- Tipik: "EŞİMİZ, EVLADIMIZ, ANNEMİZ: KADIN" (2011), "SOKAĞIN YETİMLERİ: ÇOCUKLARIMIZ" (2013)
- Sınır — *Eğitim/Teknoloji* ile: teknoloji/medya tehdidi aile-çocuk üzerinden işleniyorsa → burası; toplumsal değişim genel düzeydeyse → Eğitim/Teknoloji.
- Not: Kadın konulu hutbeler bu şemada ayrı kategori değildir; kadın teması İP-3'te ayrıca anahtar kelime katmanından izlenir (eski 20'li şemada "Kadın" ayrı kategoriydi).

**4. İman, Tevhid ve Ahiret** (57)
İnanç esasları: tevhid, ahiret, ölüm bilinci, dünya-ahiret dengesi, kalp temizliği (itikadi çerçevede).
- Tipik: "TEKBİR: ALLÂHU EKBER" (2013), "DÜNYADA YOLCU OLABİLMEK!" (2013), "KALB-İ SELİM" (2014)
- Sınır — *Sabır/Tevekkül* ile (en sık karışan çift, 31 eş-geçiş; Tur 1'de de en sık karışan çift, 4/200): mesaj **neye inanılacağı** (itikat, ahiret gerçekliği) → burası; **inançla nasıl dayanılacağı** (imtihan karşısında hâl: sabır, şükür, tevekkül) → Sabır/Tevekkül. **Karar işareti (v1.2):** "Dünya-ahiret dengesi", "dünyevileşme", itidal, Allah'ın isim/sıfatlarını (Esma-i Hüsna) tanıma temalı hutbeler → burası (kategori tanımı bu temaları zaten kapsıyor), sabır/tevekkül/kanaat kelimeleri metinde geçse bile (ör. Tur 1 sıra 33 "DÜNYA-AHİRET DENGESİ", sıra 35 "EN GÜZEL İSİMLER O'NUNDUR", sıra 98 "DÜNYEVİLEŞMEK"). Sabır/Tevekkül kategorisi yalnızca hutbe **somut bir imtihan/musibet/zorluk anına** odaklanıp o anda nasıl davranılacağını (dayanma, rıza, şükür) işliyorsa uygulanır; test sorusu: hutbenin gövdesi bir "dert/zorluk hâli" mi anlatıyor, yoksa "inanç dengesi/Allah'ı tanıma" mı? Birincisi Sabır/Tevekkül, ikincisi İman. **Nihai tie-break (v1.4):** Yukarıdaki test de sonuç vermiyorsa (hutbe hem itikadi çerçeveyi hem somut bir dert/zorluk hâlini dengeli işliyorsa) → ana kategori **İman, Tevhid ve Ahiret**, Sabır/Tevekkül ikincil olarak eklenir. Gerekçe: hadis literatüründe sabır iman'ın bir *şubesi* sayılır (bkz. "imanın yetmiş küsür şubesi vardır… hayâ da imandan bir şubedir" hadisi, Buhârî/Müslim; korpusta 22.08.2014 "HAYÂ HAYATTIR!" hutbesinde birebir geçiyor) — teolojik olarak İman kapsayıcı/kök kategori, Sabır/Tevekkül onun bir dalı/tezahürüdür, kardeş bir kategori değil.

**5. Ahlak, Erdem ve Söz** (55)
Bireysel karakter ve dil ahlakı: doğruluk, edep, samimiyet, gıybet/yalan, öfke kontrolü.
- Tipik: "İSLÂMÎ BİR DEĞERİMİZ: EDEB" (2013), "DİN SAMİMİYETTİR" (2014)
- Sınır — *Toplumsal Dayanışma* ile: bkz. kategori 1.

**6. Ramazan, Oruç ve Bayramlar** (53)
Ramazan ayı, oruç, iki bayram, kurban (bayram bağlamında).
- Tipik: "KURBAN BAYRAMI" (2011), "'BEN ORUÇLUYUM' DİYEBİLMEK" (2012)
- Vesile önceliği kuralının (3.1/3) en sık uygulandığı kategori.

**7. Vatan, Millet ve Tarih** (50)
Şehitlik, milli günler (Çanakkale, 15 Temmuz), tarih ve millet söylemi.
- Tipik: "AZÎZ ŞEHİTLERİMİZE…" (2011), "ŞEHİTLİK VE ÇANAKKALE" (2013)
- Sınır — *İslam Coğrafyası* ile: konu Türkiye'nin milleti/tarihi/şehidi → burası; ülke dışı Müslüman toplumlar/mazlumlar → İslam Coğrafyası.
- Araştırma notu: devlet-iletişimi analizinde (İP-6) kritik kategori; atamalar özellikle titiz olmalı.

**8. Sabır, Tevekkül ve Manevi Olgunluk** (46)
İmtihan karşısında bireysel manevi hâl: sabır, şükür, tevekkül, zaman bilinci, istikamet.
- Tipik: "ZAMAN BİLİNCİ" (2011), "İMTİHAN DÜNYASI" (2014)
- Sınır — *İman* ile: bkz. kategori 4. — *Afet* ile: sabır somut bir felaket vesilesiyle işleniyorsa → Afet (somut olay önceliği).

**9. Ekonomik Hayat: Kazanç, Zekat ve İsraf** (45)
Helal kazanç, ticaret ahlakı, zekât-infak, israf, borç, faiz.
- Tipik: "ALLAH'IN SEVMEDİĞİ DAVRANIŞ: İSRAF" (2013), "HELAL KAZANÇ HELAL LOKMA" (2013)
- Araştırma notu: kamu politikası bağlantısı en güçlü kategorilerden (ekonomik dönemlerle eşleşme, İP-4/İP-8).

**10. Kandiller, Muharrem ve Mübarek Geceler** (31)
Kandiller, üç aylar (Ramazan hariç), Muharrem-Aşure-Kerbela, hicri yılbaşı.
- Tipik: "KERBELA'YI ANLAMAK" (2011), "BERÂT'A YOL ARAMAK" (2012)
- Sınır — *Peygamberimiz* ile: Mevlid kandili hutbesi gövdede Peygamber'in hayatını işliyorsa → Peygamberimiz ana, kandil ikincil (vesile kuralının istisnası; gerekçe: Mevlid hutbelerinin asıl konusu kişidir, gece değil). Aksi durumda → burası.

**11. Peygamberimiz ve Ashab** (30)
Hz. Peygamber'in hayatı, örnekliği, sünnet; sahabe ve hicret.
- Tipik: "MEVLİD-İ NEBİ" (2012), "MEDENİYET YOLCULUĞU: HİCRET" (2012)

**12. İslam Coğrafyası ve Küresel Meseleler** (21)
Ülke dışı Müslüman toplumlar, mazlumlar, Kudüs/Mescid-i Aksâ, küresel zulüm-adalet söylemi.
- Tipik: "MESCİD-İ AKSÂ KAN AĞLIYOR" (2014), "ZULÜM EBEDİ DEĞİLDİR" (2017)
- Sınır — *Vatan* ile: bkz. kategori 7.

**13. Eğitim, Teknoloji, Çevre ve Toplumsal Değişim** (18)
İlim-eğitim teşviki, dijital dünya/bağımlılık, mahremiyet, çevre, toplumsal değişim eleştirisi.
- Tipik: "YARATAN RABBİNİN ADIYLA OKU!" (2015), "MAHREMİYETİ YİTİRMEK MAHRUMİYETTİR" (2016)
- ⚠️ Şema notu: dört ayrı alt temayı barındıran en heterojen kategori; İP-3'te alt-etiketle (eğitim / teknoloji / çevre) ayrıştırılması değerlendirilecek. Eski 20'li şemada bunlar ayrıydı ("Çevre ve Hayvan Hakları", "Dijital Dünya/Bağımlılık", "İlim ve Eğitim").

**14. Afet, Kriz ve Sağlık** (17)
Somut afet/salgın/kaza vesileli hutbeler + sağlık, bağımlılıkla mücadele.
- Tipik: "MÜMİNLER TEK BİR VÜCUT GİBİDİR" (2011, Van depremi), "İMAN, ÖZGÜRLÜK VE BAĞIMLILIK" (2014)
- Somut olay önceliği kuralı (3.1/4) bu kategoriyi güçlendirir: felaket vesilesi varsa tema ne olursa olsun ana kategori burasıdır.

**15. Kur'an-ı Kerim** (12)
Kur'an'ın kendisinin konu olduğu hutbeler: okuma teşviki, Kur'an kursları, Kur'an-insan ilişkisi.
- Tipik: "YAZ KUR'AN KURSLARI" (2013), "KUR'AN AYINDA KUR'AN'LA BULUŞALIM!" (2015)
- Sınır: Kur'an'dan yalnızca delil getirilmesi yeterli değildir (her hutbe yapar); Kur'an'ın **konunun kendisi** olması gerekir.

## 4. Yeni etiket katmanları (v2 — İP-3'te uygulanacak, taslak)

Aşağıdaki dört katman hutbe düzeyinde atanır. Değer listeleri kapalıdır (serbest metin yok).

### 4.1 Çerçeve — sorumluluk/çözüm atfı
Hutbenin işaret ettiği sorunun çözümü kimden bekleniyor?
- `birey` — kişisel takva, tövbe, bireysel davranış değişikliği
- `aile` — ebeveyn/eş sorumluluğu
- `cemaat-toplum` — kolektif dayanışma, sivil yardımlaşma
- `devlet-otorite` — açıkça kurumlara/devlete atıf (nadir; varlığı başlı başına bulgu)
- `karma` — birden çok düzey dengeli biçimde (baskın olan ayrıca not edilir)

Karar kuralı: hutbenin **eylem çağrısı cümlelerine** bak (genelde son 2 paragraf); çağrının öznesi kimse çerçeve odur.

### 4.2 Ton (baskın + varsa ikincil, en çok 2)
- `teşvik` — özendirme, müjde, fazilet anlatımı
- `uyarı` — sakındırma, tehdit (dünyevi/uhrevi sonuç uyarısı)
- `teselli` — acı/musibet karşısında avutma, umut
- `kınama` — mevcut bir davranışın/durumun açıkça ayıplanması
- `bilgilendirme` — nötr anlatım, tarihçe, ilmihal bilgisi

### 4.3 Muhatap (açıkça seslenilen kesim; yoksa `genel`)
- `genel` · `aileler` · `gençler` · `kadınlar` · `esnaf-işveren` · `millet` (ulusal kolektife sesleniş: "aziz milletimiz") · `ümmet` (sınır-ötesi kolektif)

Karar kuralı: hitap cümleleri ("Kıymetli kardeşlerim" standart hitabı sayılmaz) + içerikte özel kesime dönük en az bir paragraf.

### 4.4 Eylem çağrısı (var/yok; varsa türü, en çok 2)
- `yok` · `ritüel` (namaz kıl, dua et, oruç tut) · `ahlaki` (davranış değiştir) · `maddi` (bağış, zekât, kampanya) · `katılım` (camiye gel, kursa kaydol, etkinliğe katıl)

Araştırma notu: `maddi` ve `katılım` çağrıları İP-8 etki analizlerinin (bağış/davranış verisiyle eşleşme) ana girdisidir.

## 5. Atıf sayım kuralları

Mevcut veri: `ayetler.json` (243 benzersiz ayet kaydı), `hadisler.json` (640), `sahabeler.json`; kayıt = ayet/hadis × hutbe, `count` alanı tekrar sayısı.

1. **Ayet:** Sure adı + ayet numarası tespit edilebilen meal alıntıları sayılır. Aynı ayet aynı hutbede birden çok geçerse tek kayıt, `count` artar.
2. **Hutbe açılış ayeti:** Minberde okunan standart Arapça açılış metni **sayılmaz**; yalnızca gövde içinde mealen kullanılan ayetler sayılır.
3. **Hadis:** Kaynak (Buhari, Müslim, ...) + bölüm ile kayıt edilir. Kaynağı metinde belirtilmemiş "Peygamberimiz buyurur ki" alıntıları hadis sayılır, kaynak alanı `belirtilmemiş` olur.
4. **Sahabe:** İsmen anılan sahabe sayılır; "ashab-ı kiram" genel ifadesi sayılmaz.
5. **Telmih/ima** (referanssız gönderme): v1'de sayılmaz. (Açık soru, bkz. §6.)

## 6. Kararlar (v1.0'da kapatılan sorular)

| # | Soru | Karar (19.07.2026) |
|---|---|---|
| 1 | 644 (eski CSV) ↔ 637 (canlı) kayıt farkı | **Kapandı (20.07.2026, İP-3 sonu).** Üç ayrı rakam, üç ayrı şeyi ölçüyordu: **644** = kullanımdan kaldırılmış eski 20 kategorili şema (`genel_kategori_dagilimi.csv`, kapsam dışı, mutabakat aranmadı). **637** = gizli birleşik kayıtlar keşfedilmeden önceki canlı `site/data/` kaydı sayısı. **662** = v2'nin nihai, doğru hutbe sayısı (637 + İP-3 boyunca tam metin okunarak tespit edilen 25 gizli birleşik kayıt: 2013×3, 2014×3, 2015×11, 2016×2, 2017×1, 2018×3, 2019×1, 2020×1 — bkz. §7). 662 artık tek doğru sayıdır; `site/data/metinler/*.json` ve `hutbeler.json` bu sayıya göre düzeltildi. |
| 2 | Kategori 13 (Eğitim/Teknoloji/Çevre) bölünsün mü? | Bölünmeyecek; v2'de alt-etiket (`eğitim`/`teknoloji`/`çevre`) eklenecek — 15'li şemanın zaman serisi kırılmaz |
| 3 | İkincil kategori sınırı | 2 olarak kesinleşti; mevcut veri zaten uyumlu (0 ikincil: 250, 1: 197, 2: 190 hutbe) |
| 4 | Telmihler sayılmalı mı? | v1 sayımına girmez; v2'de ayrı `telmih_sayisi` alanı olarak eklenir |
| 5 | Ton/çerçeve atama düzeyi | Hutbe düzeyi; İP-3 pilotunda 20 hutbede paragraf düzeyiyle karşılaştırılıp gerekirse revize edilir |

## 7. İP-3 sonuç notu (20.07.2026)

İP-3, 2011–2025 arası tüm korpusun (662 hutbe) tam metin okunarak elle etiketlenmesi ve siteye bağlanmasıyla kapandı. Özet:

- **Kalıcı ID şeması:** `YYYY-MM-DD`; aynı tarihte birden fazla hutbe varsa (korpusta yalnızca tek örnek: 25.08.2017 — hem "Zaferler Allah'tandır" Malazgirt Zaferi hutbesi hem "Allah'a Yakın Olma Arayışı: Kurban" genel hutbesi) ikinci kayıt `-b` soneki alır. ID, `site/data/metinler/{yıl}.json` içindeki gerçek JSON anahtarıyla birebir eşleşecek şekilde atanmıştır.
- **Gizli birleşik kayıtlar:** 25 kayıt (§6/1'de listelendi) `site/data/metinler/*.json` içinde tespit edilip ayrıştırıldı; her biri `korpus_v2/{yıl}.csv`'deki elle doğrulanmış (tarih, başlık) çiftiyle çapraz kontrol edildi (23/25 otomatik desen eşleşmesiyle, 2/25 — 2019 ve 2020 — işaretsiz/farklı biçimli olduğu için elle bulunup yamalanarak). Kök neden `site/pipeline/01_extract.py`'deki `date_re`'nin yalnızca `TARİH:` + nokta-ayraçlı tarihi tanıyıp `TARİHİ :` yazım varyasyonunu ve `DD/MM/YYYY` slash-ayraçlı tarihi kaçırmasıydı; regex düzeltildi (yalnız gelecekteki PDF çalıştırmaları için — kaynak PDF'ler bu ortamda erişilebilir olmadığından pipeline yeniden çalıştırılamadı, düzeltme doğrudan `site/data/` çıktılarına uygulandı).
- **Yan bulgu:** `hutbeler.json` ile `metinler/*.json` arasında 7 tarihte (21.02.2014, 17.07.2015, 01.09.2017, 15.06.2018, 31.07.2020, 21.04.2023, 06.06.2025) başlık/özet tutarsızlığı vardı (muhtemelen eski bir manuel düzenlemenin iki dosyaya da yansımaması) — `metinler/*.json` ground truth kabul edilerek düzeltildi; aynı tutarsızlık `ayetler.json`/`hadisler.json`/`sahabeler.json`'da da 11 kayıtta bulunup aynı şekilde giderildi.
- **Siteye bağlama:** `hutbeler.json` ve `metinler/{yıl}.json`'a `id`, düzeltilmiş `primary_category`/`secondary_categories`, `cerceve`, `ton`, `muhatap`, `eylem_cagrisi` alanları eklendi (tarih+başlık eşleşmesiyle, %100 eşleşme). `ayetler.json`/`hadisler.json`/`sahabeler.json`/`kelimeler.json`'daki `category` alanı da v2 değerleriyle güncellendi. `meta.json`'da `total_hutbe`, `overall_category`, `yearly` matrisi ve `top_category` v2 verisinden yeniden hesaplandı.
- **Bilinen sınırlamalar (kapsam dışı bırakıldı):** (1) 25 yeni ayrıştırılan kayıt için ayet/hadis/sahabe atıfları çıkarılmadı (`02_citations.py` mantığı bu betikte yeniden üretilmedi) — bu 25 kayıt `ayetler.json`/`hadisler.json`/`sahabeler.json`'da yer almıyor, `citation_count` alanları 0. (2) `meta.json`'daki `weekly_grid`, `keyword_category_matrix`, `top_keywords`, `top_suras`/`top_verses`/`top_hadis_kaynak` ve toplam sayaçlar (`total_ayet` vb.) v1 verisinden hesaplanmış haliyle kaldı — bunlar yalnızca `category` alanına dolaylı bağımlı olduğundan hafif tutarsızlık taşıyabilir, tam yeniden hesaplama ayrı bir iş.
