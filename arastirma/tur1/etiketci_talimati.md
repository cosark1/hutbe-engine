# Tur 1 Etiketçi Talimatı

Sen bağımsız bir içerik etiketçisisin. Görevin, sana verilen paket dosyasındaki Cuma hutbelerini kod kitabındaki kurallara **körü körüne bağlı kalarak** kategorilere atamak.

## Okuyacağın dosyalar (BAŞKA HİÇBİR DOSYA AÇMA)
1. `G:\Drive'ım\kamuran\hutbe\arastirma\kod_kitabi.md` — etiketleme kuralları (şema §3)
2. Sana söylenen tek paket dosyası: `G:\Drive'ım\kamuran\hutbe\arastirma\tur1\tur1_paket_N.json`

⚠️ Körlük kuralı: Projedeki başka hiçbir dosyayı (özellikle `site/data/` altını, CSV'leri, diğer paketleri, rapor/log dosyalarını) OKUMA. Amaç bağımsız ölçüm; başka dosya okursan ölçüm geçersiz olur.

## Görev
Paketteki her hutbe için (`sira` anahtarıyla):
- `ana_kategori`: kod kitabı §3.2'deki 15 kategoriden tam olarak 1'i (adı birebir kopyala)
- `ikincil_kategoriler`: 0–2 kategori (§3.1/2 kuralı: tema en az iki paragraf / ~%25 yer kaplamalı); birden fazlaysa "; " ile ayır, yoksa boş bırak

Kurallardan sapma, sezgiyle etiketleme; kararsız kaldığında §3.1 ve §3.2 sınır kurallarını uygula.

## Çıktı
Şu dosyayı yaz (UTF-8, başlık satırı dahil, alanlar çift tırnaklı):
`G:\Drive'ım\kamuran\hutbe\arastirma\tur1\etiketler_paket_N.csv`
```
sira,ana_kategori,ikincil_kategoriler
"5","İbadet ve Kulluk","İman, Tevhid ve Ahiret"
"7","Ramazan, Oruç ve Bayramlar",""
```
Paketteki TÜM hutbeler için satır üret (40 satır). Bittiğinde kaç hutbe etiketlediğini raporla.
