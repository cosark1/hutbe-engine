# İP-2 Pilot Turu Raporu

**Tarih:** 19.07.2026 · Etiketçi: LLM (proje oturumu — bkz. protokol §7 kontaminasyon notu) · Kapsam: 20 hutbe (sıra 1, 11, …, 191) · Kod kitabı: v1.0

> Protokol gereği bu pilot yalnızca **süreç testi**dir; raporlanabilir asıl metrik Tur 1'den (bağımsız etiketçi, 200 hutbe) gelecektir.

## Sonuçlar

| Metrik | Değer | Yorum |
|---|---|---|
| Ana kategori ham uyum | 15/20 (%75) | — |
| Ana kategori Cohen κ | **0.713** | "Kabul edilebilir" bandı (0.67–0.80); 20 birimde geniş belirsizlik payıyla |
| İkincil ortalama Jaccard | **0.208** | Zayıf — ikincil atama kuralı orijinal etiketlemeyle örtüşmüyor |
| İkincil tam eşleşme | 1/20 | — |

## Uyuşmazlık analizi (5 vaka)

Uyuşmazlıklar iki ayrı kaynağa işaret ediyor: (A) kod kitabı kuralının netleştirilmesi gereken yerler, (B) **orijinal etiketin kendisinin şüpheli olduğu** yerler.

1. **Sıra 21 · RAMAZAN BAYRAMI (2014)** — anahtar: Toplumsal Dayanışma; pilot: Ramazan. Bayram hutbesine vesile önceliği kuralı (kod kitabı §3.1/3) uygulanırsa Ramazan doğrudur. **Tür B:** orijinal etiket kurala aykırı görünüyor.
2. **Sıra 131 · İBADET: ALLAH İLE KUL ARASINDAKİ KUTLU BAĞ (2021)** — anahtar: İman; pilot: İbadet. Hutbe kulluk/ibadet çağrısı ama tevhid-davet gövdesi geniş. **Tür A:** İbadet↔İman sınır kuralı yeterince keskin değil; "başlıkta ve kapanış çağrısında ibadet pratiği varsa İbadet" gibi ek işaret gerekiyor.
3. **Sıra 141 · HAYDİ KOŞ GEL, CAMİLER SENİNLE GÜZEL (2022)** — anahtar: Aile; pilot: Kur'an. Yaz Kur'an kursu kampanya hutbesi ama gövdenin çoğu çocuk terbiyesi. **Tür A:** "kampanya/duyuru vesilesi" ile "gövde teması" çatışması için kural yok; Kur'an kursu duyurusu tek paragrafsa gövde teması kazanmalı.
4. **Sıra 151 · ÜÇ AYLAR (2023)** — anahtar: Ramazan; pilot: Kandiller. Üç aylar + Regaib hutbesi kod kitabına göre açıkça Kandiller kapsamında ("üç aylar (Ramazan hariç)"). **Tür B:** orijinal etiket şüpheli.
5. **Sıra 171 · ORUÇ, BEDENİMİZE SIHHAT (2024)** — anahtar: İslam Coğrafyası; pilot: Ramazan. Ramazan oruç hutbesi; Gazze tek paragraf. **Tür B:** orijinal etiket kuralla bağdaşmıyor (ikincil olmalıydı).

**Ara değerlendirme:** 5 uyuşmazlığın 3'ü (21, 151, 171) kod kitabı kurallarının orijinal etiketten *daha tutarlı* sonuç verdiği vakalar. Bu, İP-3'teki yeniden etiketlemenin (korpus v2) yalnız yeni katman eklemek için değil, mevcut ana kategori etiketlerini düzeltmek için de gerekli olduğunu gösteriyor.

## İkincil kategori sorunu

Jaccard 0.208: "en az bir tam paragraf" kuralı, orijinal etiketlemenin davranışından daha cömert. Orijinal veride hutbelerin %39'unda hiç ikincil yok. İki seçenek:
- (a) Kuralı sıkılaştır: "hutbenin ana argümanını destekleyen, en az iki paragraflık ikinci tema" — ATLANACAK karar İP-3 öncesi.
- (b) Orijinal ikincilleri güvenilir sayma; v2'de ikinciller kod kitabı kuralıyla sıfırdan atanır. **Öneri: (b)** — ana kategorilerde bile Tür B hatalar varken ikincillere güven zaten düşük.

## Sonraki adımlar

1. Kod kitabı v1.1 revizyon adayları: İbadet↔İman ek işareti, kampanya/duyuru-vesile kuralı (Tür A bulguları). Revizyon Tur 1'den ÖNCE yapılmalı ki asıl ölçüm güncel kuralla koşulsun.
2. Tur 1: bağımsız etiketçi (taze LLM oturumu), 200 hutbe, `guvenilirlik_kor_metinler.json` + kod kitabı v1.1.
3. Tur 1 çıktısı üzerinde `hesapla_uyum.py` + bootstrap güven aralığı (script'e eklenecek).
