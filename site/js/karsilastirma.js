// karsilastirma.js — İP-7: Diyanet (Türkiye) ile BAE (Awqaf) hutbe kategorisi karşılaştırması
// Gösterim: kategori başına TEK satır, ortadan ayrılan karşıt (butterfly) çubuk —
// solda Diyanet, sağda BAE. İki ayrı çubuk satırına göre yarı yer kaplıyor ve
// hangi tarafın baskın olduğu tek bakışta görünüyor.
window.App = window.App || {};

App.karsilastirma = (function(){
  let dataCache = null;
  async function loadData(){
    if (!dataCache) dataCache = await App.data.loadJSON('data/karsilastirma_diyanet_bae.json');
    return dataCache;
  }

  // BAE sekmesinin üst KPI satırı + öne çıkan bulgular
  async function renderOzet(opts){
    const { statElId, bulgularElId } = opts;
    const [kat, atif, sahabe, liste] = await Promise.all([
      loadData(),
      App.data.loadJSON('data/atif_karsilastirma_diyanet_bae.json'),
      App.data.loadJSON('data/sahabe_karsilastirma_diyanet_bae.json'),
      App.data.loadJSON('data/uae_hutbeler.json'),
    ]);

    const yillar = [...new Set(liste.map(r => r.yil))].sort();
    const enBuyukFark = kat.kategoriler.reduce((a, b) => Math.abs(b.delta) > Math.abs(a.delta) ? b : a);

    document.getElementById(statElId).innerHTML = `
      <div class="kpi-card">
        <div class="kpi-label">BAE Korpusu</div>
        <div class="kpi-value">${kat.bae_toplam}</div>
        <div class="kpi-sub">hutbe · ${yillar[0]}, ${yillar[1]}–${yillar[yillar.length-1]} · ${atif.bae.toplam_hutbe}'inde resmi İngilizce çeviri var</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Karşılaştırma Tabanı</div>
        <div class="kpi-value">${kat.diyanet_toplam}</div>
        <div class="kpi-sub">Diyanet hutbesi · her iki korpus da aynı kod kitabı (v1.4) ile elle etiketlendi</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Atıf Yoğunluğu (hutbe başına)</div>
        <div class="kpi-value" style="font-size:19px;"><span style="color:var(--warm-2);">${atif.bae.ayet_ortalama}</span> / ${atif.diyanet.ayet_ortalama} ayet</div>
        <div class="kpi-sub">BAE / Diyanet · hadis: ${atif.bae.hadis_ortalama} / ${atif.diyanet.hadis_ortalama}</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">En Büyük Tema Farkı</div>
        <div class="kpi-value" style="font-size:15px;">${App.util.esc(enBuyukFark.kategori)}</div>
        <div class="kpi-sub">Diyanet %${enBuyukFark.diyanet_yuzde} · BAE %${enBuyukFark.bae_yuzde} (${enBuyukFark.delta > 0 ? '+' : ''}${enBuyukFark.delta} puan)</div>
      </div>`;

    // Öne çıkan bulgular — her biri ilgili karta/bölüme götüren bir kısayolla
    const cografya = kat.kategoriler.find(k => k.kategori.startsWith('İslam Coğrafyası'));
    const vatan = kat.kategoriler.find(k => k.kategori.startsWith('Vatan'));
    const huseyin = sahabe.sahabeler.find(s => s.isim === 'Hz. Hüseyin');

    const bulgular = [
      {
        baslik: 'İslam Coğrafyası teması BAE\'de hiç yok',
        metin: `Diyanet'in ${cografya ? cografya.diyanet_sayi : 24} hutbesi (%${cografya ? cografya.diyanet_yuzde : 3.5}) bu kategoride; BAE'de <b>0/${kat.bae_toplam}</b>. Kelime düzeyinde de doğrulandı: aşağıdaki aramada "Gaza" BAE'de hiç geçmiyor, Diyanet'te "Gazze" 55 hutbede geçiyor.`,
        hedef: 'bae-arama-karti',
      },
      {
        baslik: 'Vatan/Millet teması iki devlet kurumunda da güçlü',
        metin: `Diyanet %${vatan ? vatan.diyanet_yuzde : 7.5} · BAE %${vatan ? vatan.bae_yuzde : 8.6} — neredeyse eşit. Aynı şema DİTİB'e (Almanya, devlet-dışı diaspora kurumu) uygulandığında bu kategori <b>hiç çıkmamıştı</b>; fark kurumun devlet kimliğiyle ilişkili görünüyor.`,
        hedef: 'bae-kategori-karti',
      },
      {
        baslik: 'Hz. Hüseyin BAE\'de anılmıyor',
        metin: `Diyanet'te ${huseyin ? huseyin.diyanet_hutbe : 18} hutbede (çoğunlukla Kerbela/Muharrem bağlamında) geçiyor, BAE'de <b>hiç</b> geçmiyor — Körfez Sünni geleneğinin Kerbela-merkezli anmayı öne çıkarmadığına işaret ediyor.`,
        hedef: 'bae-sahabe-karti',
      },
    ];

    document.getElementById(bulgularElId).innerHTML = bulgular.map(b => `
      <div class="bae-bulgu" data-hedef="${b.hedef}">
        <div class="bae-bulgu-baslik">${b.baslik}</div>
        <div class="bae-bulgu-metin">${b.metin}</div>
      </div>`).join('');
    document.getElementById(bulgularElId).querySelectorAll('.bae-bulgu[data-hedef]').forEach(el => {
      el.addEventListener('click', () => {
        const t = document.getElementById(el.dataset.hedef);
        if (t) t.scrollIntoView({ behavior: 'smooth', block: 'start' });
      });
    });
  }

  async function render(opts){
    const { listElId } = opts;
    const data = await loadData();
    const maxYuzde = Math.max(...data.kategoriler.map(k => Math.max(k.diyanet_yuzde, k.bae_yuzde)));

    const listEl = document.getElementById(listElId);
    listEl.innerHTML = `
      <div class="bae-cmp-head">
        <div>Kategori</div>
        <div class="bae-cmp-legend"><span class="bae-cmp-swatch" style="background:var(--accent);"></span>Diyanet &nbsp;·&nbsp; BAE<span class="bae-cmp-swatch" style="background:var(--warm-2);margin-left:6px;"></span></div>
        <div style="text-align:right;">Fark</div>
      </div>` + data.kategoriler.map((k, i) => {
      const dW = (k.diyanet_yuzde / maxYuzde * 100).toFixed(1);
      const bW = (k.bae_yuzde / maxYuzde * 100).toFixed(1);
      const deltaColor = k.delta > 0 ? 'var(--warm-2)' : (k.delta < 0 ? 'var(--accent)' : 'var(--ink-soft)');
      const dOrnek = k.diyanet_ornekler.map(o => `<div class="cmp-ex-item cmp-ex-diyanet" data-date="${o.tarih}">${o.tarih} — ${App.util.esc(o.baslik)}</div>`).join('') || '<div class="cmp-ex-item" style="color:var(--ink-soft);cursor:default;">bu kategoride hutbe yok</div>';
      const bOrnek = k.bae_ornekler.map(o => `<div class="cmp-ex-item cmp-ex-bae" data-yil="${o.yil}" data-id="${o.id}">${o.tarih} — ${App.util.esc(o.baslik)}</div>`).join('') || '<div class="cmp-ex-item" style="color:var(--ink-soft);cursor:default;">bu kategoride hutbe yok</div>';
      return `<div class="bae-cmp-row" data-idx="${i}">
        <div class="bae-cmp-main">
          <div class="bae-cmp-kat">${App.util.esc(k.kategori)}</div>
          <div class="bae-cmp-bars">
            <div class="bae-cmp-side bae-cmp-left">
              <span class="bae-cmp-val">%${k.diyanet_yuzde}</span>
              <div class="bae-cmp-track"><div class="bae-cmp-bar" style="width:${dW}%;background:var(--accent);"></div></div>
            </div>
            <div class="bae-cmp-side bae-cmp-right">
              <div class="bae-cmp-track"><div class="bae-cmp-bar" style="width:${bW}%;background:var(--warm-2);"></div></div>
              <span class="bae-cmp-val">%${k.bae_yuzde}</span>
            </div>
          </div>
          <div class="bae-cmp-delta" style="color:${deltaColor};">${k.delta > 0 ? '+' : ''}${k.delta}</div>
        </div>
        <div class="cmp-examples" style="display:none;">
          <div class="cmp-ex-col"><b>Diyanet (${k.diyanet_sayi} hutbe)</b>${dOrnek}</div>
          <div class="cmp-ex-col"><b>BAE (${k.bae_sayi} hutbe)</b>${bOrnek}</div>
        </div>
      </div>`;
    }).join('');

    listEl.querySelectorAll('.bae-cmp-main').forEach(el => el.addEventListener('click', () => {
      const ex = el.closest('.bae-cmp-row').querySelector('.cmp-examples');
      ex.style.display = ex.style.display === 'none' ? 'flex' : 'none';
    }));
    listEl.querySelectorAll('.cmp-ex-diyanet[data-date]').forEach(el => el.addEventListener('click', (e) => { e.stopPropagation(); App.reading.open(el.dataset.date); }));
    listEl.querySelectorAll('.cmp-ex-bae[data-id]').forEach(el => el.addEventListener('click', (e) => { e.stopPropagation(); App.uaeReading.open(el.dataset.yil, el.dataset.id); }));
  }
  return { render, renderOzet };
})();
