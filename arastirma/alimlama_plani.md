# İP-9 · Alımlama Araştırması Tasarımı

**Durum:** Tasarım tamamlandı (03.08.2026, 03.08.2026'da AS4/odak grup
kaldırılarak revize edildi — bkz. §9). **Saha uygulaması bu programın kapsamı
dışındadır** — bu belge yalnızca yöntem, örneklem, enstrüman ve etik çerçeveyi
üretir; uygulanıp uygulanmayacağı, ne zaman ve kim tarafından yürütüleceği ayrı
bir karardır.

**İlgili:** `quiz_plani.md` (dijital enstrüman, Faz 1 yayında — [kahutbe.com](https://kahutbe.com))
bu planın bir bileşenidir ve burada özetlenir, tekrar edilmez.

---

## 1. Alımlama araştırması neyi soruyor, korpus analizinden farkı ne?

Bu programın diğer iş paketleri (İP-1–8) **üretim tarafını** inceliyor: hangi
temalar ne sıklıkla işleniyor, devlet iletişimiyle zamanlama ilişkisi nasıl.
Hiçbiri **alımlama tarafına** — cemaatin hutbeyi gerçekte nasıl duyduğuna,
anladığına, hatırladığına ve (varsa) davranışına yansıttığına — dokunmuyor.
Üretim analizi "ne söyleniyor" sorusuna, alımlama araştırması "ne duyuluyor"
sorusuna cevap arar.

## 2. Araştırma soruları

Korpus analizinin (İP-3) somut bulgularından türetildi — her soru, alımlama
verisiyle sınanabilecek belirli bir korpus gözlemine bağlanıyor:

| # | Soru | Korpus dayanağı | Birincil yöntem |
|---|---|---|---|
| **AS1** | Cemaat, dinlediği hutbenin ana mesajını (ana kategori düzeyinde) doğru özetleyebiliyor mu? | 15 kategorili şema (`kod_kitabi.md` §3) — "doğru özet" için referans etiket zaten var | Cami çıkışı anketi + dijital quiz |
| **AS2** | Ayet/hadis atıf yoğunluğu, hutbenin akılda kalıcılığını öngörüyor mu? | `ayet_tam_metin.csv`/`hadis_tam_metin.csv`'deki hutbe başına atıf sayısı | Dijital quiz (Faz 4 rastgeleleştirmesiyle — bkz. §3) |
| **AS3** | Hutbenin çerçevesi (`cerceve`: birey/aile/cemaat-toplum/devlet-otorite) cemaatin "bu sorunu kim çözmeli" algısını şekillendiriyor mu? | `korpus_v2` çerçeve etiketi — % dağılımı zaten bilinen bir bağımsız değişken | Cami çıkışı anketi (deneysel değil, gözlemsel eşleştirme) |
| **AS4** | Alımlama, demografik değişkenlere (yaş, cinsiyet, bölge/il büyüklüğü) göre sistematik farklılaşıyor mu? | — (korpusta demografik veri yok, bu soru saf alan verisi gerektiriyor) | Anket (tabakalı örneklem) |

AS1-AS3 **doğrulayıcı** (korpustaki bir örüntünün alan karşılığı var mı),
AS4 **keşifsel**dir (saf alan verisi, korpusta karşılığı yok).

## 3. Yöntem seçimi ve gerekçe

Tek yöntem yeterli değil — her biri farklı bir soruyu, farklı bir hata
profiliyle cevaplıyor:

### 3.1 Dijital quiz (Kahutbe) — geniş ölçek, kendiliğinden örneklem

Tasarımı tamamlanmış, Faz 1 yayında (`quiz_plani.md`). AS2 için **biricik**
uygun araç: yalnızca dijital ortamda oturum düzeyinde rastgeleleştirme
(soru-önce/soru-sonra kolu, `oturumlar.kol` alanı zaten şemada ayrılmış,
`quiz_plani.md` §3 ve §9.1) mümkün. **Sınırlılık:** katılımcılar kendiliğinden
seçilir (uygulamayı bilen, telefonu olan, quiz'e ilgi duyan) — bu, AS1/AS3/AS4
gibi temsili örneklem gerektiren sorular için **tek başına yeterli değildir**,
yalnızca AS2 için (atıf yoğunluğu × hatırlama, içsel geçerliliği önemli olan
bir soru, dış geçerlilik daha az kritik) kabul edilebilir bir tasarım.

### 3.2 Cami çıkışı kısa anket — temsili örneklem, düşük derinlik

AS1, AS3, AS4 için birincil araç. Cuma namazı sonrası cami çıkışında, 2-3
dakikada tamamlanan kısa bir kağıt/tablet anket. Kendiliğinden örneklem
sorunu quiz'e göre daha azdır (namaza gelen herkes potansiyel katılımcıdır)
ama **hâlâ mevcuttur**: ankete cevap vermeyi kabul edenler muhtemelen daha
ilgili/hatırlayan kişilerdir (yanıt yanlılığı — nonresponse bias). Örneklem
stratejisi (§4) bunu kısmen telafi eder.

### 3.3 Yarı yapılandırılmış mülakat — anket bulgularının derinleştirilmesi

Anket/quiz'den çıkan uç veya ilginç örüntülerin ("neden bu kişi ana mesajı
yanlış hatırladı", "neden sorumluluk algısı hutbenin çerçevesiyle
uyuşmuyor") nitel olarak derinleştirilmesi için 8-10 cemaat üyesiyle
derinlemesine mülakat. Amaçlı (purposive) örneklem — anket/quiz
sonuçlarında öne çıkan uç görüşlerin peşinden gidilir, rastgele seçilmez.

## 4. Örneklem stratejisi

| Yöntem | Örneklem türü | Hedef büyüklük | Tabakalama |
|---|---|---|---|
| Anket | Kolayda + tabakalı hedef | ~300-400 (n≈30-40 kişi × 8-10 cami) | Cami büyüklüğü (küçük mahalle / orta / büyük merkez camii) × il tipi (büyükşehir / il / ilçe merkezi) |
| Mülakat | Amaçlı, aşırı-örnekleme | 8-10 kişi | Anket/quiz'den çıkan uç görüşlerin derinleştirilmesi |
| Dijital quiz | Kendiliğinden | (mevcut kullanıcı tabanı) | Yok — tasarım gereği |

**Bilinen kısıt:** hiçbir yöntem gerçek rastgele örneklem değildir (camiye
gelen kişiler zaten Cuma namazı kılan bir alt küme — genel nüfusa
genellenemez, yalnızca "Cuma namazı kılan cemaat" evrenine genellenebilir).
Bu, alan çalışmasının doğasında olan bir sınır, tasarımla giderilemez;
bulgu raporlanırken evren tanımı açıkça belirtilmelidir.

## 5. Soru formu taslağı — cami çıkışı anketi

6 soru, 2-3 dakika. Tamamı kapalı uçlu (AS1/AS3/AS4); mülakat (§3.3) açık
uçlu derinleştirmeyi üstleniyor.

1. **[AS1]** Bugünkü hutbenin ana konusu sizce aşağıdakilerden hangisiydi?
   *(o günün gerçek `ana_kategori` etiketi + 3 makul çeldirici + "hatırlamıyorum" — çoktan seçmeli, tek doğru)*
2. **[AS1]** Hutbede geçen bir ayet veya hadisi hatırlıyor musunuz? *(evet/hayır; evetse serbest metin — kelimesi kelimesine değil, "ne anlattığını" hatırlama testi)*
3. **[AS3]** Bugün anlatılan konudaki asıl sorumluluğun kimde olduğunu düşünüyorsunuz? *(birey / aile / toplum-cemaat / devlet-kurumlar / birden fazlası — hutbenin kendi `cerceve` etiketiyle karşılaştırılacak)*
4. **[AS3]** Bu hutbeyi dinledikten sonra bugün/bu hafta yapmayı düşündüğünüz somut bir şey var mı? *(evet/hayır; evetse serbest metin — `eylem_cagrisi` etiketiyle karşılaştırma)*
5. **[AS4]** Yaş grubu / Cinsiyet *(demografik, isteğe bağlı bırakılabilir)*
6. **[AS4]** Bu camiye ne sıklıkla gelirsiniz? *(her hafta / ayda birkaç kez / nadiren — düzenli dinleyici vs. tesadüfi dinleyici ayrımı, AS1/AS2 yorumlanmasında karıştırıcı değişken)*

**Tasarım notu:** Soru 1 ve 3, o haftaki hutbenin gerçek etiketiyle (`korpus_v2`
alanları) doğrudan karşılaştırılacak şekilde kurgulandı — bu, anketi
korpusa **bağlayan** kritik tasarım kararı, quiz'deki `korpus_hutbe_id`
alanının (`quiz_plani.md` §9.1) kağıt-anket karşılığıdır.

## 6. Etik ve izin gereklilikleri

Quiz için zaten belirlenen ilkeler (`quiz_plani.md` §8) burada da geçerli,
ayrıca alan yöntemlerine özgü ek gereklilikler var:

- **Dini inanç, KVKK m.6'da özel nitelikli kişisel veridir** — anket/mülakat
  verisi kimlikten arındırılmış (anonim) toplanmalı; anket formunda isim/
  iletişim bilgisi **istenmemeli**.
- **Gönüllü katılım ve aydınlatılmış onay** — anket formunun başında kısa bir
  açıklama ("bu bir akademik araştırmadır, katılım gönüllüdür, hutbe içeriği
  hakkındadır, dini inancınızı değerlendirmez"); mülakatta yazılı onam formu
  ve ses kaydı için ayrı, açık rıza.
- **Cami/Diyanet izni** — cami çıkışında anket dağıtımı için ilgili
  müftülük/cami yönetiminden önceden izin alınmalı; kurumsal izin süreci bu
  belgenin kapsamı dışında, saha aşamasının ilk adımı olmalı.
- **Çocuk katılımcı olmaması** — 18 yaş altı bilinçli olarak dışlanmalı,
  cami çıkışında yaş görünürlüğü belirsiz olduğundan anket formunda "18 yaş
  ve üzeri" ibaresi + soru 5'te yaş teyidi.
- **Etik kurul onayı** — akademik yayın hedefleniyorsa (bu programın nihai
  amacı, bkz. İP-10/İP-11), saha öncesi üniversite etik kurulundan onay
  **zorunludur**. Bu belge etik kurul başvurusunun metodoloji ekini
  karşılayacak ayrıntıdadır ama başvurunun kendisi değildir.
- **Araştırmacı-hatip ayrımı** — anket dağıtımının hutbeyi okuyan hatip
  tarafından değil, bağımsız bir araştırmacı/gönüllü tarafından yapılması
  önerilir (aksi hâlde cevaplarda otorite baskısı/sosyal beğenirlik yanlılığı
  riski artar).

## 7. quiz_plani.md ile ilişki ve Faz 4 bağlantısı

`quiz_plani.md` §11'deki Faz 4 ("*isteğe bağlı* ön/son soru rastgeleleştirmesi
+ korpus etiketleriyle birleştirilmiş anonim araştırma dışa aktarımı") bu
planın AS2'sini karşılayacak şekilde tasarlanmıştı; bu belge o bağlantıyı
teyit eder ve AS1/AS3/AS4 için **quiz'in kapsamadığı** iki ek yöntemi
(anket, mülakat) ekler. Kahutbe'nin veri modelindeki
`hutbeler.korpus_hutbe_id` (`quiz_plani.md` §9.1) ile bu belgedeki anket
sorularının korpus etiketine bağlanma mantığı (§5 tasarım notu) **aynı
ilkeye** dayanır: alan verisi, doğrudan korpus etiketleriyle eşleştirilebilir
olmalı ki alımlama bulguları üretim bulgularına (İP-1-8) bağlanabilsin.

## 8. Sınırlılıklar

- **Genellenebilirlik evreni "Cuma namazı kılan cemaat"tir**, genel nüfus
  değil — bkz. §4.
- **Hiçbir yöntem gerçek rastgele örneklem üretmiyor**; kendiliğinden seçilim
  (quiz), yanıt yanlılığı (anket), küçük N (mülakat) her birinde farklı
  biçimde mevcut.
- **AS2 dışında deneysel/nedensel iddia yok** — AS1/AS3/AS4 gözlemsel/
  betimsel tasarımlardır, "hutbe bu algıyı yarattı" değil "hutbe etiketiyle
  bu algı arasında bir ilişki var" düzeyinde yorumlanmalıdır.
- **Saha uygulaması, örneklem gerçekleşmesi, etik kurul süreci ve zamanlama
  bu belgenin kapsamı dışındadır** — yalnızca tasarım üretilmiştir (WP
  tanımı gereği).

## 9. Revizyon notu (03.08.2026)

İlk sürümde beşinci bir araştırma sorusu (AS4: korpusta sistematik olarak
işlenmeyen konuların — enflasyon, iklim krizi — cemaat tarafından bir
"boşluk" olarak fark edilip edilmediği) ve buna özel bir odak grup yöntemi
vardı; bu sorunun ampirik dayanağı, kullanıcı isteğiyle projeden kaldırılan
Sessizlikler analiziydi (bkz. `arastirma_programi.md` İP-5 kaydı,
`arastirma/kaldirilan_sessizlikler/`). Analiz kaldırılınca bu sorunun
korpus dayanağı da ortadan kalktığından, soru ve ona özel odak grup yöntemi
bu belgeden çıkarıldı; kalan dört soru (AS1-4, eskiden AS1/AS2/AS3/AS5)
yeniden numaralandırıldı. Sessizlikler analizi ileride farklı bir biçimde
yeniden ele alınırsa, bu tür bir keşifsel alımlama sorusu tekrar
eklenebilir.
