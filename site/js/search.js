// search.js — Faz 3.4: serbest metin arama (concordance), Türkçe karakter normalizasyonu ile
window.App = window.App || {};
App.search = (function(){
  const trLower = App.util.trLower;
  async function loadAllYears(years){
    const all = {};
    for (const y of years){
      const data = await App.data.loadYearText(y);
      Object.assign(all, data);
    }
    return all;
  }
  function findSentences(text, qLower){
    const sentences = text.split(/(?<=[.!?])\s+/);
    return sentences.filter(s => App.util.wordMatch(trLower(s), qLower)).slice(0,3);
  }
  function highlight(sentence, q){
    // normalize('NFC'): metnin ayrışık (decomposed) Unicode formunda saklanan
    // nadir harfleri de (bkz. trLower notu) tek biçime indirger, yoksa
    // aşağıdaki [aâ]/[iî]/[uû] karakter-sınıfı deseni onları yakalayamaz.
    const re = App.util.wordBoundaryRegexRaw(trLower(q), 'gi');
    return App.util.esc(sentence.normalize('NFC')).replace(re, '<mark class="hl">$1</mark>');
  }
  async function run(query, years, hutbeByDate, resultsElId, statusElId){
    const statusEl = document.getElementById(statusElId);
    const resultsEl = document.getElementById(resultsElId);
    if (!query.trim()){ resultsEl.innerHTML=''; statusEl.textContent=''; return; }
    statusEl.textContent = 'Aranıyor…';
    const all = await loadAllYears(years);
    const qLower = trLower(query.trim());
    const hits = [];
    Object.entries(all).forEach(([date, rec]) => {
      const matches = findSentences(rec.text, qLower);
      if (matches.length) hits.push({ date, title: rec.title, category: rec.category, matches });
    });
    hits.sort((a,b) => App.util.parseTrDate(b.date) - App.util.parseTrDate(a.date));
    statusEl.textContent = `${hits.length} hutbede eşleşme bulundu`;
    resultsEl.innerHTML = hits.slice(0,60).map(h => `
      <div class="card" style="padding:14px 18px;margin-bottom:10px;">
        <div style="display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap;">
          <a class="similar-item" data-date="${h.date}" style="font-weight:600;">${App.util.esc(h.title)}</a>
          <span style="font-size:11.5px;color:var(--ink-soft);">${h.date} · <span class="badge">${App.util.esc(h.category)}</span></span>
        </div>
        ${h.matches.map(m => `<div style="font-size:13px;margin-top:8px;font-family:var(--serif);color:var(--ink-soft);">…${highlight(m, query.trim())}…</div>`).join('')}
      </div>`).join('') || '<p style="color:var(--ink-soft);font-size:13px;">Sonuç bulunamadı.</p>';
    resultsEl.querySelectorAll('[data-date]').forEach(el => el.addEventListener('click', () => App.reading.open(el.dataset.date)));
  }
  return { run };
})();
