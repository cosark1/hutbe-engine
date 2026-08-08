# -*- coding: utf-8 -*-
"""
site/'ı GitHub Pages'e yayınlamak için "yayına hazır" bir kopya üretir.
Yerel çalışma kopyasına DOKUNMAZ -- ayrı bir build klasörüne kopyalar.

Neler DIŞARIDA bırakılıyor:
  - *.bak* yedek dosyaları (18MB+, kamuya açık yayında gereksiz).
  - pipeline/, serve.py, yayina_hazirla.py, desktop.ini (geliştirme/altyapı
    dosyaları, canlı sitenin çalışması için gerekmiyor).

Not (03.08.2026): Sessizlikler (İP-5) analizi kaynağından tamamen kaldırıldı
(bkz. arastirma/kaldirilan_sessizlikler/); bu script'in önceki sürümündeki
o analize özel çıkarma adımları artık gereksiz, kaldırıldı.

Not (08.08.2026, kök neden düzeltmesi): Önceki sürüm her çalıştırmada
`shutil.rmtree(BUILD)` ile TÜM site-build/ klasörünü (içindeki `.git` git
deposu dahil) silip sıfırdan oluşturuyordu. Bu, bir dosya kilidi (muhtemelen
Google Drive senkronu) yüzünden silme işlemi yarıda kaldığında `.git`
geçmişini ve remote bağlantısını kalıcı olarak kaybettirebiliyordu (gerçekte
oldu, `git clone` ile kurtarıldı). Artık `.git` klasörüne HİÇ dokunulmuyor --
yalnızca içindeki takip edilen içerik dosyaları silinip yeniden kopyalanıyor.

Kullanım:  python3 yayina_hazirla.py
Çıktı:     ../site-build/  (git deposu; ilk seferde elle `git init` +
           `git remote add origin ...` gerekir, sonraki her çalıştırma
           mevcut git geçmişini korur)
"""
import shutil
from pathlib import Path

KOK = Path(__file__).resolve().parent
BUILD = KOK.parent / "site-build"

HARIC_DOSYALAR = {"pipeline", "serve.py", "yayina_hazirla.py", "desktop.ini"}
KORUNACAK = {".git", ".gitignore"}  # bunlar asla silinmez/üzerine yazılmaz; .gitignore site/'da değil, ilk yayında site-build/'a elle eklenmişti


def kopyala():
    BUILD.mkdir(parents=True, exist_ok=True)

    # BUILD içindeki her şeyi `.git` HARİÇ temizle -- git geçmişi asla silinmez.
    for item in BUILD.iterdir():
        if item.name in KORUNACAK:
            continue
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()

    def ignore(dirpath, names):
        atlanacak = set()
        for n in names:
            if n in HARIC_DOSYALAR:
                atlanacak.add(n)
            elif ".bak" in n:
                atlanacak.add(n)
            elif n == "desktop.ini":  # Windows/Drive senkron artığı, hiçbir alt klasörde istenmiyor
                atlanacak.add(n)
        return atlanacak

    for item in KOK.iterdir():
        if item.name in HARIC_DOSYALAR:
            continue
        if item.is_dir():
            shutil.copytree(item, BUILD / item.name, ignore=ignore)
        else:
            shutil.copy2(item, BUILD / item.name)
    print(f"Kopyalandı: {KOK} -> {BUILD} (.git korunarak)")


if __name__ == "__main__":
    kopyala()
    if (BUILD / ".git").exists():
        print(f"\nHazır: {BUILD}\nSıradaki adım: git add -A && git commit && git push")
    else:
        print(f"\nHazır: {BUILD}\nSıradaki adım: git init + remote add origin + commit + push (ilk yayın)")
