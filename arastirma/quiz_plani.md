# Cuma Hutbesi Quiz Platformu — Tasarım Belgesi

**Tarih:** 07.08.2026 (v6) · **Durum:** **Faz 1 yayında** → [kahutbe.com](https://kahutbe.com) (kendi alan adı, Cloudflare'e bağlandı — barındırma hâlâ Cloudflare Workers, `kmrn06.workers.dev` alt adresi de aynı siteye açık) · kod: [github.com/cosark1/race](https://github.com/cosark1/race) · **İlgili iş paketi:** İP-9

> **Ürün adı: Kahutbe.** "Kahoot" tınısı kasıtlı — ne olduğunu ilk duyuşta anlatıyor, bu da dağıtımı tamamen organik olan bir ürün için (§7) doğrudan bir avantaj.

Cuma namazında, o hafta okunan hutbe üzerine kısa bir quiz sunan mobil uyumlu **web sitesi** (uygulama indirme yok). İlçe düzeyinde sıralama, anonim katılım.

> **v1'den farklar (kullanıcı kararı):** ① Quiz ezanla birlikte açılır, sorular hutbeden **önce** görülür. ② QR yok — kurumsal izin/tanınırlık gerektirdiği için elendi. ③ Öncelik sırası netleşti: **eğlence birincil, araştırma ikincil ve koşullu.**

---

## 1. Amaç ve öncelik sırası

| Öncelik | Hedef |
|---|---|
| **1 (birincil)** | İnsanların hutbeyi **eğlenerek ve dikkatle** dinlemesi |
| 2 (ikincil, koşullu) | Akademik çalışma yapılırsa alımlama verisi toplanmış olması |

Bu sıralama tasarımın tamamını belirliyor. Çatışma çıktığında **eğlence lehine karar verilir**; araştırma tasarımı buna uyum sağlar, tersi değil. (v1'de bu ters kurgulanmıştı.)

## 2. Akış: soru önce, cevap sonra

Kullanıcı kararı (v3): quiz **ezanla birlikte açılır; sorular hem görünür hem anında cevaplanabilir.** Aşama kilidi yok.

Sorular ezanda görülebildiği için hutbe yine bir **arama görevine** dönüşür — kişi cevapları *dinleyerek arar* (ön-soru / advance organizer tekniği). Fark: kilit kaldırıldığı için ne zaman cevaplayacağına kişi karar verir.

| Aşama | Zaman | Ekranda ne var |
|---|---|---|
| **Sorular açık** | Ezan (T+0) → gün sonu | 5 soru liste hâlinde okunabilir + *"Cevaplamaya başla"* butonu. Tek sürekli pencere. |
| **Cevaplama** | Kullanıcı ne zaman isterse | Soru başına 20 sn, hız bonuslu; **sorular arasında otomatik geçiş yok** |

**Tasarım gerekçesi:** kilit paternalistti — erken cevaplayan zaten bilemez, bu kendi tercihi; uygulama polislik yapmıyor. Giriş metni beklentiyi kuruyor: *"Cevaplar bu haftanın hutbesinde."*

### 2.1 Süre, kilidin yerini alan doğal teşvik

Kilit kaldırıldı ama **süre baskısı erken cevaplamayı kendiliğinden caydırıyor**: hutbeyi dinlemeden başlayan hem cevabı bilemez hem de sayaç işlediği için puan kaybeder. Bu, yasaklamadan aynı sonucu veren bir teşvik. Giriş ekranında vurgulu biçimde belirtilir.

### 2.2 "Hutbe akışına eşlik" — otomatik geçiş yok

Sorular **hutbenin anlatım sırasıyla aynı sırada** dizilir. Hatip bir konuya geldikçe cemaat cevabı yakalar ve o sorunun şıklarını görmek ister. Bu yüzden bir soru cevaplandıktan sonra **otomatik olarak sonrakine geçilmez**; *"Sonraki soru →"* butonu vardır ve pas kullanıcıdadır.

**Kritik teknik sonuç:** süre sayacı ancak sonraki soru **açıldığında** başlar. Kişi hatip o konuya gelene kadar bekleyebilir ve bu bekleme puanını düşürmez. (Prototipte doğrulandı: 6 sn bekleyip açılan soru yine tam puan verdi.)

Bu, quiz'i "hutbeden sonra çözülen test" olmaktan çıkarıp **hutbeye eşlik eden canlı bir refakatçiye** dönüştürüyor.

> **v2'den kaldırılan:** "Önizleme (cevaplanamaz)" ve "Sessizlik" ekranları. Sessizlik ekranı (*"Hutbe başladı — telefonu bırak, dinle"*) ürünün camide telefon kullanımını teşvik etmediğini göstermesi açısından tasarlanmıştı; tek sürekli pencere modeline uymadığı için çıkarıldı. **Kabul edilen bedel:** kişi hutbe sırasında cevaplamaya başlayabilir. İstenirse zorlayıcı olmayan bir uyarı (kapatılabilir şerit) geri eklenebilir.

**Zamanlama teknik notu:** T = ilçenin öğle vakti (Diyanet vakit API'si). Quiz'in açık olup olmadığına **sunucu** karar verir — istemci saatine güvenilmez.

### 2.3 Cuma dışındaki günler: alıştırma modu ve geri sayım

Quiz haftada bir kez, birkaç saatliğine açık. Geriye kalan ~6,5 günde giriş sayfası boş duruyordu — dağıtımı tamamen organik olan bir ürün için (§7) ölü zaman. İki ekleme:

**① Alıştırma (canlı değil).** Geçmiş hutbelerin soruları istendiği zaman oynanabilir. Kasıtlı sınırlar:

| Karar | Gerekçe |
|---|---|
| Oturum/cevap **kaydedilmez** | Sıralamayı ve araştırma verisini kirletmez (§3, §9.1) |
| Puan **istemcide** hesaplanır | Sıralamaya girmediği için manipülasyonun anlamı yok; sunucu-taraflı zaman çapasına gerek kalmıyor |
| Doğru cevaplar istemciye açıkça gönderilir | Yalnızca `tarih < bugün` olan hutbeler için (`alistirma_sorulari` RPC'si). **Canlı quizin cevapları bu yoldan sızamaz** — deneysel olarak doğrulandı: canlı akışta `dogru_idx` istemciye hiç ulaşmıyor |

**② İlçeye göre geri sayım.** Seçilen ilçenin bir sonraki öğle vaktine kalan süre. Uyarlanabilir biçim (*"5 gün 11 saat"* → *"3 saat 20 dk"* → *"12:34"*), son 1 saatte renk vurgusu, sıfırlanınca **sayfa yenilemeden** kendiliğinden açılır.

**Kritik teknik sonuç:** sayaç istemci saatine göre işlemez. `sonraki_kahutbe` RPC'si sunucu zamanını da döndürür, istemci aradaki **farkı bir kez ölçüp** sayacı ona göre işletir. Böylece telefonun saati yanlış olsa bile açılış anı kaymaz. (Ölçülen fark testte ~3,3 sn idi.)

Ayrıca `quiz_durumu` artık canlı quiz için **tam olarak bugünün tarihli hutbesini** şart koşuyor. Önceden "tarih ≤ bugün olan en güncel hutbe" alınıyordu; bu, yeni hutbe eklenmediğinde geçen haftanınkini canlı sanma hatasına yol açıyordu. Hutbe yoksa kullanıcıya bu **açıkça söyleniyor** ("Bu haftanın hutbesi henüz yayımlanmadı"), böylece neden geçmiş hutbelerin sunulduğu anlaşılıyor.

## 3. Ön-soru tasarımının bedeli (dürüst not)

Sorular önceden görülünce ölçülen şey değişir:

| Tasarım | Ölçtüğü şey |
|---|---|
| Sorular **sonra** | Doğal/kendiliğinden akılda kalıcılık |
| Sorular **önce** (bizim seçim) | **Yönlendirilmiş dikkat** — "cevabı aradı mı" |

Yani AS3 ("ayet/hadis yoğunluğu akılda kalıcılığı öngörür mü?") ön-soru düzeninde **saf biçimde yanıtlanamaz**, çünkü dikkat yapay olarak yönlendirilmiştir.

**Çözüm (Faz 4'te, isteğe bağlı):** oturum düzeyinde rastgeleleştirme — katılımcıların bir kısmı soruları önce, bir kısmı sonra görür. Bu:
- Herkese aynı eğlenceyi verir (kimse mağdur olmaz),
- "Sonra" grubundan temiz doğal-hatırlama verisi üretir,
- Üstelik kendi başına yayımlanabilir bir bulgu doğurur: **"Ön-soru vermek hutbe hatırlanmasını artırıyor mu?"** — din eğitimi alanında özgün bir soru.

Faz 1-3'te gerek yok; not olarak duruyor.

## 4. Soru kalitesi — ön-soru düzeninde daha da kritik

İki kural:

1. **Genel dini bilgiyle cevaplanmamalı.** Aksi hâlde ölçülen şey hutbe değil kişinin mevcut bilgisi olur.
   - ❌ *"Zekât kaç şartla farzdır?"*
   - ✅ *"Hatip israfı hangi somut örnekle anlattı?"*
2. **Ezber değil kavrayış aramalı.** Ön-soru düzeninde "hangi sure okundu" tipi sorular hutbeyi bir kelime avına indirger. Sorular hutbenin **mesajını** hedeflerse dinleme derinleşir.

İkinci kural birincil hedefe (eğlenerek *anlayarak* dinleme) doğrudan bağlı; editör onayında her iki kontrol de zorunlu adım.

## 5. Konum ve sıralama — QR olmadan

QR elendi (cami düzeyinde izin/tanınırlık gerektiriyordu). Bu, cami düzeyindeki sıralamayı da beraberinde götürüyor: kurumsal işbirliği olmadan güvenilir bir cami kimliği elde etmenin yolu yok — GPS kapalı mekânda ve 80 m arayla iki caminin bulunduğu merkezlerde yanlış atama yapar, ve doğrulanmış bir cami listesi de elde değil.

**Karar: v1'de sıralama ilçe düzeyinde.**

| Neden ilçe işe yarıyor |
|---|
| GPS **ilçe** ölçeğinde güvenilir (kilometrelerce alan; caminin aksine) |
| Namaz vakti zaten ilçe bazında hesaplanıyor → aynı veri ikisini birden çözüyor |
| Yeterince yerel: *"Kadıköy'de 3. sıradasın"* motive edici |
| Sıfır kurulum, sıfır izin |

**Konum alma — açılır menü kullanılmaz.** ~973 ilçe bir `<select>` içine sığmaz; iki yol sunulur:

1. **"Konumumu kullan"** — tarayıcının kendi izin penceresi çıkar (hukuken sağlam: açık rıza tarayıcı düzeyinde alınır). Koordinat **yalnızca bellekte** en yakın ilçeye çevrilir, ardından atılır; **hiçbir yere yazılmaz**. Kullanıcıya bu açıkça söylenir.
2. **Aramalı alan** — izin verilmezse/çalışmazsa. Yazdıkça filtreleyen bir metin kutusu; Türkçe büyük/küçük harf dönüşümüne duyarlı (`İ→i`, `I→ı`) ve il adıyla da arama yapılabilir ("izmir" → Konak, Bornova, Karşıyaka).

> **Not:** İzin *istemek* ile koordinatı *saklamak* farklı şeyler. Yasal risk ikincisindedir; bu tasarımda koordinat hiç saklanmadığı için sorun doğmaz.

**Uygulamada çıkan sorun — büyükşehir merkez ilçeleri.** Diyanet'in vakit hiyerarşisi Kadıköy, Üsküdar, Beşiktaş, Çankaya, Konak gibi merkez ilçeleri **ayrı ayrı listelemiyor** (büyükşehir öncesi müftülük sınırları); İstanbul için 39 yerine yalnızca 19 kayıt dönüyor. Bu, tasarımın can alıcı vaadini (*"Kadıköy'de 3. sıradasın"*) en kalabalık şehirlerde kırıyordu.

**Çözüm:** ilçe listesi Diyanet'ten değil, tam idari listeden (972 ilçe, koordinatlı) alınır; `diyanet_ilce_kodu` mümkün olduğunda doğrudan eşleşmeden (784 ilçe), yoksa **il merkezinin kodundan** (188 ilçe) türetilir. Namaz vakti bir il merkezinde saniyeler mertebesinde değiştiği için bu, vakit doğruluğunu bozmaz — yalnızca o 188 ilçe il merkeziyle **aynı** öğle vaktini paylaşır. Arama ve sıralama gerçek ilçe düzeyinde kalır. (`diyanet_ilce_kodu` bu yüzden benzersiz değildir.)

**Cami düzeyi ileride:** kullanıcıların cami adını serbest metin girmesiyle kalabalıklaştırma (crowdsourcing) yoluyla eklenebilir. Kullanıcı tabanı oluşmadan anlamsız; v1 kapsamı dışında.

## 6. Takma ad ve puanlama

- **Takma ad:** küratörlü Türkçe sıfat+isim listesinden, cihaz jetonundan **deterministik** üretilir → kişi haftalarca aynı adı görür ("Sabırlı Ceylan"), kendi ilerlemesini izler, kimliği yoktur. Liste elle küratörlü olduğu için istenmeyen çağrışım sorunu doğmaz.
- **Puanlama:** Kahoot mantığı — doğruda taban 1000 puan + kalan süreye orantılı hız bonusu, yanlışta 0. Soru başına ~20 sn.
- **Sıralamalar:** ilçe içi (haftalık) · il içi (ilçe ortalamaları, **min. 5 katılımcı eşiği** — yoksa tek kişilik ilçe tepeye çıkar) · Türkiye · kişisel geçmiş.

## 7. Dağıtım — QR gidince en kritik başlık

Kurumsal işbirliği ve fiziksel QR yoksa büyüme tamamen **organik**. Bu, ürün tasarımına doğrudan yansımalı:

1. **Paylaşılabilir sonuç (Wordle modeli).** Quiz sonunda metin/görsel kart: *"Bu haftanın hutbesi: 6/8 · Kadıköy'de 12. · Sabırlı Ceylan"*. Wordle'ın tüm büyümesi bu mekanizmadandı; kurumsal desteği olmayan bir ürün için en gerçekçi kanal.
2. **Web push hatırlatma.** Android/masaüstü Chrome'da normal web sayfasından çalışır. **iOS'ta yalnızca "ana ekrana ekle" yapılmışsa** (iOS 16.4+) — yani iPhone kullanıcılarının bir kısmına ulaşılamaz. Bu, uygulama indirmeme kararının kabul edilen bedeli.
3. **WhatsApp/Telegram grupları** — her cuma link paylaşımı; en düşük sürtünmeli manuel kanal.

**Dürüst değerlendirme:** teknik risk düşük, **benimsenme riski yüksek**. Ürün gerçekten eğlenceli ve paylaşılabilir değilse organik büyüme olmaz. Faz 0'ın asıl amacı bunu ölçmek.

## 8. Etik ve KVKK

Dini inanç KVKK m.6'da **özel nitelikli kişisel veri**. Tasarım ilkeleri (pazarlık konusu değil):

- Hesap yok, e-posta yok, telefon numarası yok.
- **Ham GPS koordinatı saklanmaz** — yalnızca ilçe kodu.
- Kimlik yerine cihazda duran rastgele jeton; sunucuda yalnızca **hash'i**.
- Araştırma dışa aktarımında jeton hash'i de düşürülür → veri **anonim** hâle gelir (anonim veri KVKK kapsamı dışı).
- İlk girişte aydınlatma metni + araştırma kullanımına rıza.
- Camide çocuk da bulunur; hiçbir durumda kimliklendirici veri toplanmaması bu yüzden ayrıca önemli.
- Akademik yayın hedeflenirse **etik kurul onayı** gerekir (saha öncesi).

## 9. Teknik mimari

Mevcut analiz sitesiyle aynı felsefe: **statik ön yüz + yönetilen arka uç**, sunucu bakımı sıfır. Kullanıcı kararı gereği **native uygulama yok** — kurulabilir web sitesi (PWA).

| Katman | Seçim | Gerekçe |
|---|---|---|
| Ön yüz | Statik PWA (GitHub Pages / Cloudflare Pages) | İndirme gerektirmez; "ana ekrana ekle" isteğe bağlı |
| Arka uç | **Supabase** (Postgres + otomatik REST + realtime) | Canlı sıralama hazır; anonim oturum yerleşik; **veri Postgres'te → araştırma için doğrudan SQL** |
| Namaz vakti | Diyanet vakit API'si, ilçe bazlı haftalık önbellek | ~973 ilçe, haftada bir çekilir |

Supabase tercihi bilinçli: Firebase gibi alternatifler veriyi araştırma amaçlı çekmeyi zorlaştırır.

### 9.1 Veri modeli (taslak)

```
iller      (plaka, ad)
ilceler    (id, il_plaka, ad, diyanet_ilce_kodu)
vakitler   (ilce_id, tarih, ogle)                  -- haftalık önbellek
hutbeler   (id, tarih, baslik, korpus_hutbe_id)    -- ← korpus v2'ye bağlanır
sorular    (id, hutbe_id, sira, metin, secenekler, dogru_idx, tur, sure_sn=20)
oturumlar  (id, jeton_hash, ilce_id, hutbe_id, takma_ad, baslangic, mod, kol)
cevaplar   (id, oturum_id, soru_id, secilen_idx, dogru_mu, yanit_ms, puan)
```

- `hutbeler.korpus_hutbe_id` → araştırma değerinin tamamı bu bağlantıdan geliyor; **zorunlu tutulmalı.**
- `oturumlar.kol` → Faz 4'teki ön/son soru rastgeleleştirmesi için (v1'de hep `"on"`).
- `camiler` tablosu v1'de **yok** (§5).

### 9.2 Kötüye kullanıma karşı

- Cihaz jetonu → `(jeton, hutbe)` başına tek oturum
- Sorular cevaplama aşamasında **tek tek** sunulur; her biri sunucu zaman damgası + son tarihiyle gelir
- IP bazlı hız limiti
- Asıl savunma tasarımda: bireysel zirve yerine **ilçe ortalaması + katılım sayısı** öne çıkar

Sertifika sınavı değil; hedef "istatistiği bozacak ölçekte manipülasyonu zorlaştırmak".

## 10. Soru üretimi ve editoryal süreç

Diyanet hutbeyi birkaç gün önceden yayımlıyor → sorular cumadan önce hazırlanıp gözden geçirilebilir.

| Gün | Adım |
|---|---|
| Perşembe | Hutbe metnini çek (**mevcut boru hattı zaten yapıyor**) |
| Perşembe | LLM ile 5-8 soru taslağı |
| Perşembe | **Editör paneli: elle onay** — §4'teki iki kontrol zorunlu |
| Cuma | Yayımla |

Elle onay adımı pazarlık konusu değil: dini içerikte hatalı veya yanlış anlaşılmaya açık bir soru, teknik arızadan çok daha maliyetlidir.

## 11. Yol haritası

| Faz | Kapsam | Tahmini |
|---|---|---|
| **0** ✅ | Backend'siz prototip: tek ilçe, elle yazılmış 5 soru, tek sürekli pencere (sorular açık → cevaplama → sonuç), sıralama yok → **`quiz/index.html` (26.07.2026)** | tamamlandı |
| **1** ✅ **yayında** | Supabase şeması + RLS + sunucu-taraflı puanlama/zaman çapası (`schema.sql`), **972 ilçe** + Diyanet kodu + koordinat seed'i (`seed_ilceler.sql`), haftalık vakit önbelleği (`vakit_guncelle.py` — 971/972 ilçe için 07.08 öğle vakti yazıldı), ilçe sıralaması, paylaşılabilir kart, **alıştırma modu + geri sayım** (`02_alistirma_modu.sql`). Cloudflare Workers'ta yayında. | tamamlandı (02.08.2026) |
| **2** | PWA (ana ekrana ekle, web push) + kişisel geçmiş | 1-2 gün |
| **3** 🔶 | Mobil yönetim paneli ✅ (`admin.html` — Supabase Auth ile korumalı, RLS'de tek e-postaya kilitli; hutbe/soru ekle-düzenle-sil). Kalan: LLM ile soru taslağı üretimi + onay akışı | 1 gün |
| **4** | *(isteğe bağlı)* Ön/son soru rastgeleleştirmesi + korpus etiketleriyle birleştirilmiş anonim araştırma dışa aktarımı | 1-2 gün |

Faz 0'ın amacı kod değil **karar**: bu şey gerçekten eğlenceli mi, sonuç kartı paylaşılacak kadar tatmin edici mi?

## 12. Maliyet

Supabase ücretsiz katmanı (500 MB, 50k aylık aktif kullanıcı) binlerce eşzamanlı katılımcıya yeter; aşılırsa ~25 USD/ay. Ön yüz barındırma ücretsiz. Yük profili avantajlı: namaz vakitleri illere göre farklı olduğundan trafik ~1-1,5 saate yayılır.

## 13. Riskler

| Risk | Değerlendirme |
|---|---|
| **Benimsenme (en büyük)** | QR ve kurumsal destek olmadan büyüme tamamen organik. Paylaşılabilir sonuç kartı en gerçekçi kanal. |
| iOS bildirim kısıtı | "Ana ekrana ekle" yapılmadan push yok — indirme gerektirmeme kararının bedeli |
| Soru kalitesi | §4 — ön-soru düzeninde ölçüm *ve* deneyim doğrudan buna bağlı |
| Camide telefon algısı | v3'te kilit kaldırıldığı için kişi hutbe sırasında cevaplayabilir. Zorlayıcı olmayan bir uyarı şeridi gerekirse eklenir (bkz. §2) |
| Araştırma yorumlanabilirliği | §3 — ön-soru düzeni doğal hatırlamayı ölçmez; Faz 4 rastgeleleştirmesi çözer |

**Karar bekleyen:** pilot ölçeği (tek ilçe mi, tek il mi?) ve akademik yayın hedefi (etik kurul gerekliliğini belirler).
