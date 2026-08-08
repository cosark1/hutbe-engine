// karsilastirmali_arama.js — İP-7: Diyanet (Türkçe) ile BAE (İngilizce) korpuslarında
// aynı anda serbest kelime arama, sonuçları yan yana karşılaştırmalı okuma için.
window.App = window.App || {};

App.karsilastirmaliArama = (function(){
  let bae_cache = null;

  async function loadBaeAll(){
    if (bae_cache) return bae_cache;
    const yillar = [2009, 2016, 2017, 2022, 2023, 2024, 2025, 2026];
    const parcalar = await Promise.all(yillar.map(y => App.data.loadJSON(`data/uae_metinler/${y}.json`).catch(() => ({}))));
    bae_cache = Object.assign({}, ...parcalar);
    return bae_cache;
  }

  function diyanetCumleler(text, qLower){
    const trLower = App.util.trLower;
    const sentences = text.split(/(?<=[.!?])\s+/);
    return sentences.filter(s => App.util.wordMatch(trLower(s), qLower)).slice(0, 2);
  }
  function baeCumleler(text, qLower){
    const sentences = text.split(/(?<=[.!?])\s+/);
    return sentences.filter(s => s.toLowerCase().includes(qLower)).slice(0, 2);
  }
  function vurgula(sentence, q){
    const esc = App.util.esc(sentence);
    const safeQ = q.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    return esc.replace(new RegExp('(' + safeQ + ')', 'gi'), '<mark class="hl">$1</mark>');
  }

  async function run(query, years, hutbeByDate, opts){
    const { diyanetElId, baeElId, statusElId } = opts;
    const statusEl = document.getElementById(statusElId);
    const diyanetEl = document.getElementById(diyanetElId);
    const baeEl = document.getElementById(baeElId);
    const q = query.trim();
    if (!q){ diyanetEl.innerHTML = ''; baeEl.innerHTML = ''; statusEl.textContent = ''; return; }
    statusEl.textContent = 'Aranıyor…';

    const trLower = App.util.trLower;
    const qLowerTr = trLower(q);
    const qLowerEn = q.toLowerCase();

    const diyanetAll = {};
    for (const y of years){
      Object.assign(diyanetAll, await App.data.loadYearText(y));
    }
    const dHits = [];
    Object.entries(diyanetAll).forEach(([date, rec]) => {
      const matches = diyanetCumleler(rec.text, qLowerTr);
      if (matches.length) dHits.push({ date, title: rec.title, category: rec.category, matches });
    });
    dHits.sort((a,b) => App.util.parseTrDate(b.date) - App.util.parseTrDate(a.date));

    const baeAll = await loadBaeAll();
    const bHits = [];
    Object.entries(baeAll).forEach(([id, rec]) => {
      if (!rec.en_metin) return;
      const matches = baeCumleler(rec.en_metin, qLowerEn);
      if (matches.length) bHits.push({ id, yil: rec.tarih.split('-')[0], tarih: rec.tarih, baslik: rec.baslik, matches });
    });
    bHits.sort((a,b) => b.tarih.localeCompare(a.tarih));

    statusEl.textContent = `Diyanet: ${dHits.length} hutbe · BAE: ${bHits.length} hutbe`;

    diyanetEl.innerHTML = dHits.slice(0, 40).map(h => `
      <div class="card" style="padding:12px 16px;margin-bottom:8px;">
        <div style="display:flex;justify-content:space-between;gap:8px;flex-wrap:wrap;">
          <a class="ka-diyanet-link" data-date="${h.date}" style="font-weight:600;cursor:pointer;color:var(--accent);">${App.util.esc(h.title)}</a>
          <span style="font-size:11px;color:var(--ink-soft);">${h.date}</span>
        </div>
        ${h.matches.map(m => `<div style="font-size:12.5px;margin-top:6px;font-family:var(--serif);color:var(--ink-soft);">…${vurgula(m, q)}…</div>`).join('')}
      </div>`).join('') || '<p style="color:var(--ink-soft);font-size:13px;">Eşleşme yok.</p>';
    diyanetEl.querySelectorAll('.ka-diyanet-link[data-date]').forEach(el => el.addEventListener('click', () => App.reading.open(el.dataset.date)));

    baeEl.innerHTML = bHits.slice(0, 40).map(h => `
      <div class="card" style="padding:12px 16px;margin-bottom:8px;">
        <div style="display:flex;justify-content:space-between;gap:8px;flex-wrap:wrap;">
          <a class="ka-bae-link" data-yil="${h.yil}" data-id="${h.id}" style="font-weight:600;cursor:pointer;color:var(--warm-2);">${App.util.esc(h.baslik)}</a>
          <span style="font-size:11px;color:var(--ink-soft);">${h.tarih}</span>
        </div>
        ${h.matches.map(m => `<div style="font-size:12.5px;margin-top:6px;font-family:var(--serif);color:var(--ink-soft);">…${vurgula(m, q)}…</div>`).join('')}
      </div>`).join('') || '<p style="color:var(--ink-soft);font-size:13px;">Eşleşme yok.</p>';
    baeEl.querySelectorAll('.ka-bae-link[data-id]').forEach(el => el.addEventListener('click', () => App.uaeReading.open(el.dataset.yil, el.dataset.id)));
  }
  return { run };
})();
