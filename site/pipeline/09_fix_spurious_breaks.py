# -*- coding: utf-8 -*-
"""
07.11.2014'te kullanıcının bulduğu "O halde Müslüman,\n\nzulmü..." hatasının
kapsamını tüm korpusta tarayıp düzeltir (kaynak-PDF'lerden miras kalan, bu
projenin pipeline'ından bağımsız, ÖNCEDEN VAR olan bir metin kusuru — 2011-2020
arasına dağılmış 45 hutbede 50 örnek, tek seferlik keşif). İki desen:
  (a) \n\n hemen ardından küçük harf -- cümle ortasında yanlışlıkla açılmış
      paragraf sınırı (49 örnek) -> tek boşlukla birleştirilir.
  (b) \n\n RAKAM \n\n -- muhtemel sayfa numarası artığı (yalnız 22.08.2014,
      1 örnek) -> rakam silinip tek boşlukla birleştirilir.
Yalnızca site/data/metinler/{yıl}.json'daki "text" alanı düzeltilir (tam metnin
tek kaynağı burası; korpus_v2 CSV'leri metni tutmuyor, yalnız etiketleri).
Kalıcı olarak saklanıyor: ileride benzer bir kusur bulunursa aynı tarama
mantığı (regex'ler) yeniden kullanılabilir.
"""
import json, re, glob, shutil
from pathlib import Path

kok = Path(__file__).resolve().parent.parent / "data" / "metinler"

def tara(kok=kok):
    """Şüpheli bölünmeleri (uygulamadan) listeler — doğrulama/keşif amaçlı."""
    bulgular = []
    for yol in sorted(glob.glob(str(kok / "*.json"))):
        yil = Path(yol).stem
        d = json.loads(Path(yol).read_text(encoding="utf-8"))
        for tarih, kayit in d.items():
            t = kayit.get("text", "")
            for m in re.finditer(r"\n\n", t):
                after = t[m.end():m.end()+1]
                if after and after.islower():
                    bulgular.append((yil, tarih, kayit.get("title") or kayit.get("baslik")))
    return bulgular

def uygula(kok=kok):
    toplam_a, toplam_b, degisen_dosya, degisen_hutbe = 0, 0, 0, []
    for yol in sorted(glob.glob(str(kok / "*.json"))):
        yol = Path(yol)
        d = json.loads(yol.read_text(encoding="utf-8"))
        dosya_degisti = False
        for tarih, kayit in d.items():
            t = kayit.get("text", "")
            if not t:
                continue
            yeni = t
            yeni, n_b = re.subn(r"\n\n\d{1,3}\n\n", " ", yeni)
            yeni, n_a = re.subn(r"\n\n(?=[a-zçğıöşüâîû])", " ", yeni)
            if n_a or n_b:
                kayit["text"] = re.sub(r"  +", " ", yeni)
                toplam_a += n_a
                toplam_b += n_b
                dosya_degisti = True
                degisen_hutbe.append((yol.stem, tarih, kayit.get("title") or kayit.get("baslik"), n_a, n_b))
        if dosya_degisti:
            bak = yol.with_suffix(yol.suffix + ".bak-preSpuriousBreakFix")
            if not bak.exists():
                shutil.copy2(yol, bak)
            yol.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
            degisen_dosya += 1
    return toplam_a, toplam_b, degisen_dosya, degisen_hutbe

if __name__ == "__main__":
    a, b, dosya, hutbe = uygula()
    print(f"Degisen dosya: {dosya} | duzeltilen hutbe: {len(hutbe)}")
    print(f"Tip (a) cumle-ortasi birlesme: {a} | Tip (b) izole rakam: {b}")
    for yil, tarih, baslik, na, nb in hutbe:
        print(f"  {tarih} ({yil}) {baslik} -- a:{na} b:{nb}")
    kalan = tara()
    print(f"Dogrulama: kalan supheli bolunme = {len(kalan)}")
