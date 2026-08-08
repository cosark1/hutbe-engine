// archive.js — Faz "Hutbe Ara": kart görünümlü arşiv sayfası
window.App = window.App || {};
App.archive = (function(){
  const PERIOD_TERMS = {
    'ramazan': 'ramazan',
    'ramazan-bayrami': 'ramazan bayram',
    'kurban': 'kurban',
    'kandil': 'kandil',
    'mevlid': 'mevlid'
  };
  let hutbeler, themeLabels, ayetDates, hadisDates, years, hutbeByDate;
  let activeThemes = new Set();
  let activePeriod = null;
  const pageSize = 24;
  let shown = pageSize;
  let deepTimer = null;

  const trLower = App.util.trLower;
  function esc(s){ return App.util.esc(s); }

  function matchesQuery(h, q){
    if (!q) return true;
    const hay = trLower(h.title + ' ' + h.summary + ' ' + (h.keywords||[]).join(' '));
    return App.util.wordMatch(hay, q);
  }
  function relevanceScore(h, q){
    const t = trLower(h.title), s = trLower(h.summary);
    let score = App.util.wordMatchCount(t,q)*5 + App.util.wordMatchCount(s,q)*2;
    (h.keywords||[]).forEach(k => { if (App.util.wordMatch(trLower(k), q)) score += 3; });
    return score;
  }

  function getFiltered(){
    const q = trLower(document.getElementById('arch-search').value.trim());
    const yMin = parseInt(document.getElementById('arch-year-min').value);
    const yMax = parseInt(document.getElementById('arch-year-max').value);
    const wantAyet = document.getElementById('arch-has-ayet').checked;
    const wantHadis = document.getElementById('arch-has-hadis').checked;
    const sortMode = document.getElementById('arch-sort').value;
    let rows = hutbeler.filter(h => {
      if (h.year < yMin || h.year > yMax) return false;
      if (activeThemes.size && !(activeThemes.has(h.primary_category) || (h.secondary_categories||[]).some(c=>activeThemes.has(c)))) return false;
      if (activePeriod){
        const term = PERIOD_TERMS[activePeriod];
        const hay = trLower(h.title + ' ' + h.summary + ' ' + (h.keywords||[]).join(' '));
        if (!App.util.wordMatch(hay, term)) return false;
      }
      if (wantAyet && !ayetDates.has(h.date)) return false;
      if (wantHadis && !hadisDates.has(h.date)) return false;
      if (!matchesQuery(h, q)) return false;
      return true;
    });
    if (sortMode === 'date-asc') rows.sort((a,b) => App.util.parseTrDate(a.date) - App.util.parseTrDate(b.date));
    else if (sortMode === 'citation-desc') rows.sort((a,b) => b.citation_count - a.citation_count);
    else if (sortMode === 'relevance' && q) rows.sort((a,b) => relevanceScore(b,q) - relevanceScore(a,q));
    else rows.sort((a,b) => App.util.parseTrDate(b.date) - App.util.parseTrDate(a.date));
    return { rows, q };
  }

  function cardHtml(h){
    const kwChips = (h.keywords||[]).slice(0,6).map(k => `<span class="kw-chip" data-kw="${esc(k)}">${esc(k)}</span>`).join('');
    const secBadges = (h.secondary_categories||[]).map(c => `<span class="badge sec">${esc(c)}</span>`).join('');
    return `<div class="hutbe-card" data-date="${h.date}">
      <div class="hutbe-card-top"><span class="hutbe-date-badge">${h.date}</span><span class="hutbe-citation-badge" title="Atıf sayısı">${h.citation_count} atıf</span></div>
      <h4 class="hutbe-card-title">${esc(h.title)}</h4>
      <p class="hutbe-card-summary">${esc(h.summary)}</p>
      <div class="hutbe-card-themes"><span class="badge">${esc(h.primary_category)}</span>${secBadges}</div>
      <div class="hutbe-card-keywords">${kwChips}</div>
      <div class="hutbe-card-footer"><span class="btn-read">Oku →</span></div>
    </div>`;
  }

  function render(){
    const { rows } = getFiltered();
    document.getElementById('arch-status').textContent = `${rows.length} hutbe bulundu (toplam ${hutbeler.length})`;
    const visible = rows.slice(0, shown);
    document.getElementById('hutbe-grid').innerHTML = visible.map(cardHtml).join('') || '<p style="color:var(--ink-soft);font-size:13px;padding:20px;">Bu filtrelerle eşleşen hutbe bulunamadı.</p>';
    const lm = document.getElementById('arch-loadmore');
    lm.style.display = rows.length > shown ? 'inline-block' : 'none';
  }

  function resetAndRender(){ shown = pageSize; render(); }

  function renderThemeMulti(){
    const el = document.getElementById('arch-theme-multi');
    el.innerHTML = themeLabels.map(t => `<button type="button" class="theme-chip" data-theme="${esc(t)}">${esc(t)}</button>`).join('');
    el.querySelectorAll('.theme-chip').forEach(btn => {
      btn.addEventListener('click', () => {
        const t = btn.dataset.theme;
        if (activeThemes.has(t)){ activeThemes.delete(t); btn.classList.remove('active'); }
        else { activeThemes.add(t); btn.classList.add('active'); }
        resetAndRender();
      });
    });
  }

  function wirePeriodChips(){
    document.querySelectorAll('#arch-period-chips .chip').forEach(btn => {
      btn.addEventListener('click', () => {
        const p = btn.dataset.period;
        if (activePeriod === p){
          activePeriod = null; btn.classList.remove('active');
        } else {
          document.querySelectorAll('#arch-period-chips .chip').forEach(b => b.classList.remove('active'));
          activePeriod = p; btn.classList.add('active');
        }
        resetAndRender();
      });
    });
  }

  function runDeep(){
    const q = document.getElementById('arch-search').value;
    App.search.run(q, years, hutbeByDate, 'arch-deep-results', 'arch-deep-status');
  }

  function wireDeepSearch(){
    const deepChk = document.getElementById('arch-deep');
    const deepWrap = document.getElementById('arch-deep-results-wrap');
    deepChk.addEventListener('change', () => {
      const on = deepChk.checked;
      deepWrap.style.display = on ? 'block' : 'none';
      document.getElementById('hutbe-grid').style.display = on ? 'none' : '';
      if (on) runDeep(); else render();
    });
  }

  function wireGridClicks(){
    document.getElementById('hutbe-grid').addEventListener('click', (e) => {
      const kwEl = e.target.closest('.kw-chip');
      if (kwEl){ e.stopPropagation(); App.kwModal.open(kwEl.dataset.kw); return; }
      const card = e.target.closest('.hutbe-card');
      if (card) App.reading.open(card.dataset.date);
    });
  }

  function init(data){
    hutbeler = data.hutbeler;
    themeLabels = data.meta.overall_category.labels;
    ayetDates = new Set(data.ayetler.map(a => a.date));
    hadisDates = new Set(data.hadisler.map(h => h.date));
    years = [...new Set(hutbeler.map(h => h.year))].sort((a,b) => a-b);
    hutbeByDate = {}; hutbeler.forEach(h => hutbeByDate[h.date] = h);

    const yMinSel = document.getElementById('arch-year-min'), yMaxSel = document.getElementById('arch-year-max');
    years.forEach(y => { yMinSel.appendChild(new Option(y,y)); yMaxSel.appendChild(new Option(y,y)); });
    yMinSel.value = years[0]; yMaxSel.value = years[years.length-1];

    renderThemeMulti();
    wirePeriodChips();
    wireDeepSearch();
    wireGridClicks();

    document.getElementById('arch-search').addEventListener('input', () => {
      clearTimeout(deepTimer);
      deepTimer = setTimeout(() => {
        resetAndRender();
        if (document.getElementById('arch-deep').checked) runDeep();
      }, 250);
    });
    [yMinSel, yMaxSel].forEach(el => el.addEventListener('change', resetAndRender));
    document.getElementById('arch-has-ayet').addEventListener('change', resetAndRender);
    document.getElementById('arch-has-hadis').addEventListener('change', resetAndRender);
    document.getElementById('arch-sort').addEventListener('change', resetAndRender);
    document.getElementById('arch-loadmore').addEventListener('click', () => { shown += pageSize; render(); });
    document.getElementById('arch-reset').addEventListener('click', () => {
      document.getElementById('arch-search').value = '';
      yMinSel.value = years[0]; yMaxSel.value = years[years.length-1];
      document.getElementById('arch-has-ayet').checked = false;
      document.getElementById('arch-has-hadis').checked = false;
      document.getElementById('arch-sort').value = 'date-desc';
      document.getElementById('arch-deep').checked = false;
      document.getElementById('arch-deep-results-wrap').style.display = 'none';
      document.getElementById('hutbe-grid').style.display = '';
      activeThemes.clear();
      document.querySelectorAll('#arch-theme-multi .theme-chip').forEach(b => b.classList.remove('active'));
      activePeriod = null;
      document.querySelectorAll('#arch-period-chips .chip').forEach(b => b.classList.remove('active'));
      resetAndRender();
    });

    resetAndRender();
  }

  return { init, refresh: resetAndRender };
})();
