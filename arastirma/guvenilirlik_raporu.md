# İP-2 Tur 1 Güvenilirlik Raporu

**Tarih:** 20.07.2026 · Etiketçi: LLM (bağımsız oturum, protokol §7 körlük kuralına uyularak) · Kapsam: 200 hutbe (5 paket × 40) · Kod kitabı: v1.1

## Sonuçlar

| Metrik | Değer | Yorum |
|---|---|---|
| Ana kategori ham uyum | 134/200 (%67) | — |
| Ana kategori Cohen κ | **0.643** [%95 GA: 0.571–0.710] | "Orta" bant (0.41–0.60) ile pilotun "kabul edilebilir" bandı (0.67–0.80) arasında; pilotun 0.713'ünün altında |
| İkincil ortalama Jaccard | **0.335** | Zayıf-orta; pilotun 0.208'inden yüksek ama hâlâ güvensiz |
| İkincil tam eşleşme | 55/200 (%28) | — |

Bootstrap (1000 örnek, SEED=42) güven aralığı 0.571–0.710 arasında; alt sınır bile "orta" bandın üzerinde kalıyor, yani sonuç rastgele düşük çıkmış değil.

## Veri kalitesi düzeltmesi (raporlama öncesi)

Birleştirme sırasında 4 kayıt (sıra 42, 70, 107, 117) "şema dışı kategori" olarak işaretlendi. Kök neden: paket 2 ve 5'i etiketleyen oturumlar "Kur'an-ı Kerim" kategori adında kıvrık kesme işareti (') kullanmış, kod kitabı ve anahtar dosya ise düz kesme işareti (') kullanıyor. Metinler doğru kategoriyi seçmişti, yalnızca karakter farkı vardı. `etiketler_paket_2.csv` ve `etiketler_paket_5.csv`'de düzeltildi (7 satır etkilendi). Düzeltme öncesi/sonrası: ham uyum %66→%67, κ 0.632→0.643. **Not:** Bu tür Unicode kesme işareti tutarsızlığı, ileride pipeline'a (03_annotate/04_validate) otomatik kontrol olarak eklenmeli (İP-3).

## Kategori bazında uyum (anahtar kategorisine göre, n≥5 olanlar)

| Uyum | Kategori |
|---|---|
| 16/16 (%100) | Vatan, Millet ve Tarih |
| 16/17 (%94) | Ramazan, Oruç ve Bayramlar |
| 9/10 (%90) | Kandiller, Muharrem ve Mübarek Geceler |
| 14/18 (%78) | Aile, Çocuk ve Nesil |
| 4/5 (%80) | Kur'an-ı Kerim |
| 4/6 (%67) | Eğitim, Teknoloji, Çevre ve Toplumsal Değişim |
| 12/18 (%67) | İman, Tevhid ve Ahiret |
| 13/20 (%65) | İbadet ve Kulluk |
| 3/5 (%60) | Afet, Kriz ve Sağlık |
| 10/17 (%59) | Ahlak, Erdem ve Söz |
| 8/14 (%57) | Ekonomik Hayat: Kazanç, Zekat ve İsraf |
| 5/9 (%56) | Peygamberimiz ve Ashab |
| 10/24 (%42) | Toplumsal Dayanışma, Merhamet ve Kardeşlik |
| 3/7 (%43) | İslam Coğrafyası ve Küresel Meseleler |
| 7/14 (%50) | Sabır, Tevekkül ve Manevi Olgunluk |

Takvim/tarih vesilesiyle ana kategorisi büyük ölçüde kendiliğinden belirlenen kategoriler (Vatan/Millet, Ramazan, Kandiller) neredeyse mükemmel uyum gösteriyor. En zayıf bölge, tanımı gereği geniş ve komşularıyla örtüşen "genel ahlak/toplum" kümesi: Toplumsal Dayanışma, Sabır/Tevekkül, İslam Coğrafyası.

## En sık karışan çiftler (anahtar → Tur 1 etiketçisi)

| Adet | Anahtar | Tur 1 |
|---|---|---|
| 4 | Sabır, Tevekkül ve Manevi Olgunluk | İman, Tevhid ve Ahiret |
| 3 | Ahlak, Erdem ve Söz | Toplumsal Dayanışma, Merhamet ve Kardeşlik |
| 3 | Toplumsal Dayanışma, Merhamet ve Kardeşlik | Ahlak, Erdem ve Söz |
| 3 | Toplumsal Dayanışma, Merhamet ve Kardeşlik | Ramazan, Oruç ve Bayramlar |
| 3 | İman, Tevhid ve Ahiret | İbadet ve Kulluk |
| 2 | Sabır, Tevekkül ve Manevi Olgunluk | İbadet ve Kulluk |
| 2 | İbadet ve Kulluk | İman, Tevhid ve Ahiret |
| 2 | İbadet ve Kulluk | Kur'an-ı Kerim |
| 2 | Ahlak, Erdem ve Söz | İman, Tevhid ve Ahiret |
| 2 | Aile, Çocuk ve Nesil | Kur'an-ı Kerim |

Karışan çiftlerin neredeyse tamamı, kod kitabının kendisinin "en sık karışan çift" olarak zaten işaretlediği sınırlarla örtüşüyor (İman↔Sabır/Tevekkül, İbadet↔İman, Toplumsal Dayanışma↔Ahlak). Bu, sınır kurallarının kâğıt üzerinde tanımlanmış olsa da pratikte hâlâ yetersiz ayırt edici olduğunu gösteriyor.

## Pilot ile çapraz doğrulama

Pilot raporundaki (bkz. [pilot_raporu.md](pilot_raporu.md)) 5 uyuşmazlık vakasından 4'ü (sıra 21, 141, 151, 171) bu 200'lük örneklemde de yer alıyor. Tur 1'in bağımsız etiketlemesi, kod kitabı v1.1 kurallarını uygulayarak pilotla **aynı** kararlara ulaştı (21→Ramazan, 141→Aile [kod kitabındaki §3.1/3a örneğiyle birebir aynı vaka], 151→Kandiller, 171→Ramazan+ikincil İslam Coğrafyası). Bu, kuralların en azından tekrarlanabilir şekilde uygulanabildiğini, sorunun kural belirsizliğinden çok kategori tanımlarının doğal örtüşmesinden kaynaklandığını destekliyor.

## Değerlendirme ve sonraki adımlar

κ=0.643, pilotun 0.713'ünün altında kaldı; bunun büyük bölümü örneklem büyümesiyle (20→200) nadir/geniş kategorilerdeki gerçek belirsizliğin daha fazla yakalanmasından kaynaklanıyor — pilotta hiç görülmeyen düşük uyumlu kategoriler (Toplumsal Dayanışma %42, Sabır/Tevekkül %50, İslam Coğrafyası %43) burada ortaya çıktı.

1. **İnsan etiketçi turu (Tur 2, opsiyonel ama önerilir):** ≥50 hutbelik alt örneklem, özellikle düşük uyumlu 4 kategoriden ağırlıklı seçilerek — LLM-LLM uyumunun insan yargısıyla ne kadar örtüştüğünü test etmek için. **→ 21.07.2026'da yapıldı, bkz. aşağıdaki Tur 2 bölümü.**
2. **Kod kitabı v1.2 adayı:** Toplumsal Dayanışma↔Ahlak ve İman↔Sabır/Tevekkül sınırlarına, pilotta olduğu gibi ek "karar işareti" eklenmesi (ör. kapanış eylem çağrısı testi, kategori 2'de zaten uygulanan yönteme benzer şekilde). **→ v1.2'de yapıldı ("somut alıcı testi"); Tur 2 sonucuna göre yetersiz kaldı, v1.3 gerekiyor.**
3. **İP-3'e geçiş:** Mevcut uyum düzeyi (κ=0.64, orta-iyi bant), tam korpus yeniden etiketlemesi (v2) için yeterli bir temel sayılabilir; ancak yukarıdaki 3 kategori çiftinin netleştirilmesi önce yapılmalı ki v2 etiketlemesi aynı belirsizlikleri tekrar üretmesin. **→ İP-3 zaten tamamlandı (20.07.2026), bu öneri geride kaldı.**
4. Unicode/karakter normalizasyonu `04_validate.py`'ye kural olarak eklenmeli. (Tur 2'de bu tür bir hata çıkmadı — bkz. aşağı.)

---

## Tur 2 — İnsan etiketçi

**Tarih:** 21.07.2026 · Etiketçi: proje sahibi (insan, körlük kuralına uyularak — bkz. `tur2_etiketleme_araci.html`) · Kapsam: 50 hutbe (Tur 1'in 200'lük kör örrekleminden sistematik alt-örneklem, sıra 1-197 arası her 4.) · Kod kitabı: v1.2

### Sonuçlar

| Metrik | Değer | Yorum |
|---|---|---|
| Ana kategori ham uyum | 29/50 (%58) | Tur 1'in %67'sinin altında |
| Ana kategori Cohen κ | **0.540** [%95 GA: 0.390–0.689] | Protokolün 0.67 eşiğinin ALTINDA (bkz. `guvenilirlik_protokolu.md` §1) — "orta" bant, revizyon tetikleyen sonuç |
| İkincil ortalama Jaccard | **0.297** | Tur 1'in 0.335'inin biraz altında |
| İkincil tam eşleşme | 12/50 (%24) | — |

n=50 olduğundan güven aralığı geniş (0.390–0.689) — alt sınır Tur 1'in nokta tahmininin (0.643) bile altına iniyor, üst sınır ise Tur 1'e yakın. Yani bu tek örneklemle "insan-LLM uyumu LLM-LLM uyumundan kesinlikle daha düşük" iddiası güçlü değil, ama nokta tahmini (0.540) yönü açık: **insan etiketçi, orijinal (LLM üretimi) etiketlerle Tur 1'in bağımsız LLM'inden daha az örtüşüyor.**

Şema dışı kategori kontrolünde 3 kayıt (sıra 117, 141, 189) ilk bakışta işaretlendi, ancak incelemede bunların gerçek bir yazım/encoding hatası olmadığı görüldü — bu 3 hutbe, bu 50'lik alt-örneklemin ANAHTARINDA hiç "Kur'an-ı Kerim" veya "Ekonomik Hayat" kategorili kayıt bulunmamasından kaynaklanan bir kontrol yanlış-pozitifi (kategori adlarının kendisi kod kitabıyla birebir eşleşiyor). Tur 1'deki gibi bir Unicode/kesme işareti sorunu bu turda çıkmadı.

### Kategori bazında uyum (n küçük, temkinli okunmalı)

| Uyum | Kategori |
|---|---|
| 3/3 (%100) | Ahlak, Erdem ve Söz |
| 2/2 (%100) | Afet, Kriz ve Sağlık |
| 3/4 (%75) | Ramazan, Oruç ve Bayramlar |
| 4/6 (%67) | İbadet ve Kulluk |
| 2/3 (%67) | Peygamberimiz ve Ashab |
| 2/3 (%67) | Kandiller, Muharrem ve Mübarek Geceler |
| 2/3 (%67) | Vatan, Millet ve Tarih |
| 3/5 (%60) | İman, Tevhid ve Ahiret |
| 3/5 (%60) | Aile, Çocuk ve Nesil |
| 1/2 (%50) | İslam Coğrafyası ve Küresel Meseleler |
| 3/9 (%33) | Toplumsal Dayanışma, Merhamet ve Kardeşlik |
| 1/5 (%20) | Sabır, Tevekkül ve Manevi Olgunluk |

### En sık karışan çiftler (anahtar → Tur 2 etiketçisi)

| Adet | Anahtar | Tur 2 |
|---|---|---|
| 3 | Toplumsal Dayanışma, Merhamet ve Kardeşlik | Ahlak, Erdem ve Söz |
| 2 | Toplumsal Dayanışma, Merhamet ve Kardeşlik | Ramazan, Oruç ve Bayramlar |
| 2 | Sabır, Tevekkül ve Manevi Olgunluk | İman, Tevhid ve Ahiret |

### Değerlendirme

**Toplumsal Dayanışma ↔ Ahlak, Erdem ve Söz, kod kitabının v1.2'de eklediği "somut alıcı testi"ne (§3.2 kategori 1) rağmen hem Tur 1'de (LLM-LLM, 3+3=6/200) hem Tur 2'de (insan-LLM, 3/50 — oransal olarak daha da yüksek) en sık karışan çift olmaya devam ediyor.** Bu, tek bir turda rastlantısal görülen bir gürültü değil — iki bağımsız ölçümde de aynı sınırın en zayıf nokta olarak çıkması, kuralın kâğıt üzerinde mantıklı olsa da pratikte ayırt edici gücünün hâlâ yetersiz olduğunu gösteriyor. **Sabır/Tevekkül ↔ İman** ikinci en sık karışan çift olarak da her iki turda tekrar ediyor (Tur 1'de #1, Tur 2'de #2).

Kategori bazında en düşük uyum yine aynı iki kategoride: Toplumsal Dayanışma (%33) ve Sabır/Tevekkül (%20) — Tur 1'de de en zayıf kategoriler arasındaydı (%42, %50). Küçük n (9 ve 5) nedeniyle tek tek yüzdelere aşırı anlam yüklenmemeli, ama yön tutarlı.

### Sonraki adımlar

1. **Kod kitabı v1.3:** Toplumsal Dayanışma↔Ahlak sınırına "somut alıcı testi"nden daha keskin bir ayırt edici kural gerekiyor — iki turda da yetersiz kaldığı kanıtlandı. Sabır/Tevekkül↔İman sınırı da benzer şekilde gözden geçirilmeli.
2. Bu 50 kaydın **UYUŞMAYAN ANA/İKİNCİL KATEGORİLER** dökümü (bkz. `tur2/tur2_raporla.py` çıktısı) doğrudan v1.3 taslağı için vaka listesi olarak kullanılabilir.
3. Protokolün kendi eşiğine göre (κ<0.67 → "ilgili kategori tanımları revize edilir, ölçüm o kategorilerde tekrarlanır"): v1.3 revizyonundan sonra en az Toplumsal Dayanışma/Ahlak/Sabır-Tevekkül/İman dörtlüsünde küçük bir tekrar ölçümü (Tur 3?) önerilir — tam 200'lük yeniden ölçüm şart değil.
4. **Not:** İP-3 (tam korpus v2 yeniden etiketleme) bu bulgulardan ÖNCE tamamlanmıştı (20.07.2026); yani mevcut 691 hutbelik korpus, bu iki zayıf sınırdaki belirsizlikleri muhtemelen içeriyor. v1.3 kararlaşırsa, korpusun bu dört kategoriye giren alt-kümesinin (yaklaşık 24+46=70 hutbe) yeniden gözden geçirilmesi düşünülebilir — ancak bu, kullanıcı önceliğine bağlı ayrı bir karar.
