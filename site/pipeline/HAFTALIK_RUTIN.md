# Haftalık hutbe rutini — korpus + site + Kahutbe

Her **Perşembe 20:00**'de bu bilgisayardaki yerel zamanlanmış görev (Claude Code) bu belgeyi
baştan sona uygular. Elle çalıştırmak için de aynı adımlar geçerli.

Kullanıcı kararları (25.09.2026):
- Kaynak Diyanet'in yayımladığı yeni Cuma hutbesi; Perşembe öğleden sonra RSS'e düşüyor.
- Kahutbe soruları **tamamen otomatik**: inceleme ve bildirim yok, yazıldığı anda yayında
  (`arastirma/quiz_plani.md` §10). Editörün yerini aşağıdaki denetimler tutuyor — hiçbirini atlama.
- Rutin bu bilgisayarda çalışır; servis anahtarı ve git kimliği burada.

Mekanik adımlar `10_haftalik_senkron.py`'de. Yargı gerektiren iki adım (korpus etiketleri,
Kahutbe soruları) senin işin. Çalışma klasörü: `%USERPROFILE%\.kahutbe\is\` (Drive dışı).

```
cd "G:\Drive'ım\kamuran\hutbe\site\pipeline"
python 10_haftalik_senkron.py durum
```

`durum` üç şey söyler: RSS'teki hutbeler, **korpusta eksik** olanlar, **Kahutbe'de eksik**
olanlar (yalnız Cuma, ≥ 2026-07-24). İkisi de 0 ise 8. adıma (vakit) geç, sonra bitir.

> **Kaynak kuralı:** dinhizmetleri.diyanet.gov.tr `robots.txt` ile `/kategoriler/`'i yasaklıyor.
> Proje kuralı gereği bu eleyici; oraya istek atma, etrafından dolaşma. Kaynak
> diyanethaber.com.tr RSS'i (resmî PDF'le byte-aynı dosyalar). RSS'e ulaşılamazsa dur, raporla.

## 1. İndir ve çıkar

```
python 10_haftalik_senkron.py indir     # PDF -> {yıl}/ + kopyası is\pdf\ ; PDF tarihini RSS'le doğrular
python 10_haftalik_senkron.py cikar     # is\pdf\ -> is\extracted.json
```

`indir` "HATA: PDF tarihi …" derse o hutbeyi atla ve raporla (yanlış dosya korpusa girmesin).

## 2. Korpus etiketleri (yargı adımı)

`is\extracted.json`'daki her kayıt için metni **baştan sona oku** ve `is\labels.json` yaz:

```json
[{"date": "02.10.2026", "title": "BAŞLIK (extracted'daki gibi)",
  "primary": "ahlak", "secondary": ["peygamber"],
  "cerceve": "birey", "ton": ["teşvik", "uyarı"], "muhatap": "genel",
  "eylem_cagrisi": ["ahlaki"],
  "summary": "2-3 cümle, yorumsuz, 'anlatılıyor / vurgulanıyor' diliyle.",
  "keywords": ["4-5", "tematik", "ifade", "..."]}]
```

- Kategoriler ve sınır kuralları: `arastirma/kod_kitabi.md` §3 (gövde belirler; ikincil ≥ 2
  paragraf; vesile önceliği; 3a: kampanya/hafta vesile değildir; somut olay önceliği; Mevlid
  istisnası: Peygamber ana + Kandil ikincil). Kapalı listeler: §4.
- **Tutarlılık:** aynı ya da yakın başlıklı geçmiş hutbelerin etiketlerine bak
  (`site/data/hutbeler.json`'da başlıkta ara) ve sapma varsa gerekçesi olsun.

```
python 10_haftalik_senkron.py korpus-yaz %USERPROFILE%\.kahutbe\is\extracted.json %USERPROFILE%\.kahutbe\is\labels.json
```

Denetçi tek hata bulursa hiçbir şey yazmaz → düzelt, tekrar çalıştır. Çıktıda
"çözümlenemeyen atıf" > 0 ise dipnotu incele (`08_integrate_new_hutbe.py` `split_hadith_ref`);
Diyanet'in PDF'indeki eksik kaynak adını **tahmin etme**. `korpus-yaz` sonunda
`arastirma/uret_turev_dosyalar.py`'yi kendisi çalıştırır (kök dizindeki türev atıf CSV'leri +
`meta.json`'ın atıf alanları); `meta.json` girintili kalmalı ve `total_citations` =
ayet + hadis + sahabe ismi olmalı.

Atıf denetimi (isteğe bağlı ama önerilir):

```
python ..\..\arastirma\denetle_atiflar.py
git -C ..\.. checkout -- arastirma/atif_denetimi/
```

Denetçi, deneme modunda bile `arastirma/atif_denetimi/` altındaki **tarihsel** rapor ve
değişiklik günlüğünün üzerine yazar; bu yüzden ikinci satırla hemen geri al. Yalnız yeni
hutbelerin tarihli satırlarına bak: `HATALI` varsa commit'leme, raporla. `ref_cozulemedi`
denetçinin eski çözümleyicisinden olabilir (ör. `;` ile ayrılmış çok kaynaklı dipnot).
Korpustaki kayıt doğruysa sorun değildir.

## 3. Siteyi üret

```
python ..\yayina_hazirla.py
```

## 4. Kahutbe soruları (yargı adımı)

**Yalnız Cuma hutbeleri** (bayram hutbeleri öğle vakti mantığına uymaz — yalnız korpusa girer).
Her eksik Cuma için `quiz\supabase\sorular\YYYY-MM-DD.json` yaz:

```json
{"tarih": "2026-10-02", "baslik": "Başlık Türkçe Yazımla", "korpus_hutbe_id": "02.10.2026",
 "sorular": [{"sira": 1, "metin": "...", "secenekler": ["a","b","c","d"], "dogru_idx": 2,
              "aciklama": "“Hutbeden birebir alıntı.” (Kaynak, varsa)"}]}
```

Kurallar (quiz_plani §4 + Kardeşlik revizyonunda kullanıcıyla netleşenler):
1. **Genel dini bilgiyle cevaplanamaz** — yalnız bu hutbeyi dinleyen bilir. Çok bilinen bir
   ayet/hadisi tamamlatmak yerine hutbeye özgü cümleleri, eşleştirmeleri, sayımları sor.
2. **Ezber değil kavrayış.** Sayı/yıl ezberi sorma.
3. 5 soru, **hutbenin anlatım sırasıyla**; genellikle 5. soru kapanış ayeti/hadisi.
4. Şıklar **aynı kategoride ve biçimce paralel**, birbirine yakın. Çeldiriciler "mantıklı"
   olsun: en iyisi, konuyu bilen ama hutbeyi dinlemeyenin seçeceği ders kitabı cevabı
   (ör. Ahîlik → "usta ile çırak"; doğru: "esnaf ile müşteri").
5. "Hangisi geçmedi/sayılmadı" sorusunda **doğru (geçmeyen) şık diğerleriyle aynı temada**
   olmalı (Kardeşlik'te "Siyasi görüşlerimiz" fazla kolaydı → "Hayallerimiz"). Hutbede sayılan
   ama başka bağlamda geçen bir öğeyi şık yapma — iki doğru cevap doğar.
6. Hadis soruluyorsa son kısım hariç tamamını ver; şiirde şairi, ayette sure ve ayet
   numarasını soru metninde belirt.
7. `dogru_idx` sorular arasında değişsin (hep aynı konum olmasın).
8. `aciklama`: hutbedeki cümleyi “…” içinde **birebir** alıntıla (kısaltma için "…"), varsa
   dipnottaki kaynağı parantezde ver. Soru "geçmeyen"i soruyorsa bunu açıklamada söyle.
9. Hiçbir şık dini açıdan yanlış bir iddia içermesin (yanlış şık "hutbede geçmeyen" olmalı,
   "İslam'a aykırı" değil). Tarihsel olarak doğru ama hutbede olmayan bir olay şık yapılacaksa,
   soru "Hutbeye göre…" diye kurulmalı ve doğru şıkla çelişmemeli.

Önce denetle, sonra yaz:

```
python 10_haftalik_senkron.py alinti-denetle ..\..\quiz\supabase\sorular\2026-10-02.json
python 10_haftalik_senkron.py kahutbe-yaz   ..\..\quiz\supabase\sorular\2026-10-02.json
```

`kahutbe-yaz` biçimi ve alıntıları kendisi de denetler, hata varsa hiçbir şey yazmaz.
Alıntı bulunamazsa alıntıyı düzelt — denetimi gevşetme. İdempotenttir: o tarihte soru varsa
dokunmaz (düzeltme gerekiyorsa `admin.html`'den ya da REST ile tek tek).

Kayıt için aynı soruları `quiz\supabase\` altında sıradaki numaralı SQL dosyasına da yaz
(`09_hutbeler_agustos_eylul2026.sql` biçiminde; veritabanı sıfırdan kurulursa kullanılır).

## 5. Vakit önbelleği

```
python 10_haftalik_senkron.py vakit          # önümüzdeki Cuma
```

~5 dk sürer. 972 ilçeden 1'i (Eskişehir/Mihalgazi, kod 33292) ayna API'de kalıcı 502 veriyor
— bilinen durum, rapora yaz, rutini durdurma. Başka hatalar çoksa (ör. 429 fırtınası) bir kez
tekrar çalıştır.

## 6. Commit ve push

Üç ayrı depo; **yalnız bu çalıştırmanın dosyalarını** ekle (`git add -A` yok):

| Depo | Klasör | Eklenecekler |
|---|---|---|
| cosark1/hutbe-engine | `hutbe\` | `{yıl}\*.pdf` (yeni), `site\data\`, `arastirma\korpus_v2\`, kök dizindeki `*_siralamasi.csv`, `*_tam_metin.csv`, `*_x_tema.csv`, `sahabe_tam_liste.csv` |
| cosark1/hutbe (GitHub Pages) | `hutbe\site-build\` | `git add -A` burada güvenli (üretilmiş kopya) |
| cosark1/race (Kahutbe) | `hutbe\quiz\` | `supabase\sorular\*.json` (yeni), yeni SQL kaydı |

Kullanıcının commit'lenmemiş başka değişiklikleri olabilir (ör. `arastirma_programi.md`,
`.claude/launch.json`) — onlara **dokunma**. Git kimliği depo-özel `cosark1`; `--global` kullanma.
Commit mesajı Türkçe, ne eklendiğini söylesin; sonuna oturumun kendi atıf satırını
(`Co-Authored-By: …`) ekle.

Push'u **bir kez** dene. İzin sistemi engellerse aşmaya çalışma: commit'ler diskte kalır,
raporda hangi depoda hangi commit'in beklediğini ve `git push` komutunu yaz. (Kahutbe soruları
Supabase'e zaten yazıldığı için quiz deposunun push'u yalnız kayıttır; site-build push'u
edilmezse site bir hafta eski kalır.)

## 7. Supabase'e ulaşılamazsa

`durum` "Kahutbe: ULAŞILAMADI" derse proje büyük olasılıkla ücretsiz planın hareketsizlik
duraklatmasına girmiştir. Korpus ve site adımlarını yine yap; 4-5. adımları atla, soru
JSON'unu yine yaz ve commit'le (kayıt), raporda "Supabase panelinden projeyi yeniden başlatın,
sonra `kahutbe-yaz` + `vakit`i çalıştırın" de.

## 8. Rapor

Kısa, Türkçe: hangi hutbe(ler) eklendi, etiketleri (ana + ikincil), 5 sorunun metni ve doğru
cevabı, vakit sonucu, commit/push durumu, varsa hatalar. Her şey yolundaysa da raporla.
