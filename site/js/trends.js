// trends.js — Faz 3.2: Yükselen-düşen anahtar kelimeler
window.App = window.App || {};
App.trends = (function(){
  let byKeywordYear = {}; // keyword -> {year: count}
  let allYears = [];

  function build(kelimeler, yearMin, yearMax){
    byKeywordYear = {};
    kelimeler.forEach(r => {
      const y = parseInt(r.date.split('.')[2]);
      byKeywordYear[r.keyword] = byKeywordYear[r.keyword] || {};
      byKeywordYear[r.keyword][y] = (byKeywordYear[r.keyword][y]||0) + 1;
    });
    allYears = [];
    for (let y = yearMin; y <= yearMax; y++) allYears.push(y);
  }

  function seriesFor(keyword){ return allYears.map(y => (byKeywordYear[keyword]||{})[y] || 0); }

  function computeRisingFalling(){
    const mid = allYears[Math.floor(allYears.length/2)];
    const results = [];
    Object.keys(byKeywordYear).forEach(kw => {
      const total = Object.values(byKeywordYear[kw]).reduce((a,b)=>a+b,0);
      if (total < 5) return;
      let early = 0, late = 0, earlyYears = 0, lateYears = 0;
      allYears.forEach(y => {
        const c = (byKeywordYear[kw][y]||0);
        if (y < mid){ early += c; earlyYears++; } else { late += c; lateYears++; }
      });
      const earlyRate = early / Math.max(1, earlyYears);
      const lateRate = late / Math.max(1, lateYears);
      const change = lateRate - earlyRate;
      results.push({ keyword: kw, total, earlyRate, lateRate, change });
    });
    const rising = [...results].sort((a,b) => b.change - a.change).slice(0, 10);
    const falling = [...results].sort((a,b) => a.change - b.change).slice(0, 10);
    return { rising, falling };
  }

  function renderLists(risingId, fallingId){
    const { rising, falling } = computeRisingFalling();
    const rowHtml = (r, arrow) => `<div class="compare-stat-row"><span>${App.util.esc(r.keyword)}</span><span>${arrow} ${r.earlyRate.toFixed(1)} → ${r.lateRate.toFixed(1)} / yıl</span></div>`;
    document.getElementById(risingId).innerHTML = rising.map(r => rowHtml(r, '↑')).join('') || '<span style="color:var(--ink-soft);font-size:13px;">Yeterli veri yok</span>';
    document.getElementById(fallingId).innerHTML = falling.map(r => rowHtml(r, '↓')).join('') || '<span style="color:var(--ink-soft);font-size:13px;">Yeterli veri yok</span>';
  }

  function renderKeywordChart(canvasId, keyword){
    App.charts.make(canvasId, {
      type: 'line',
      data: { labels: allYears, datasets: [{ label: keyword, data: seriesFor(keyword), borderColor:'#b8863a', backgroundColor:'#b8863a33', fill:true, tension:.3 }] },
      options: { responsive:true, maintainAspectRatio:false, plugins:{legend:{display:false}}, scales:{ y:{beginAtZero:true, ticks:{stepSize:1}} } }
    });
  }

  function initSelector(selectId, canvasId, defaultKeywords){
    const sel = document.getElementById(selectId);
    const all = Object.keys(byKeywordYear).filter(k => Object.values(byKeywordYear[k]).reduce((a,b)=>a+b,0) >= 4).sort();
    sel.innerHTML = all.map(k => `<option value="${App.util.esc(k)}">${App.util.esc(k)}</option>`).join('');
    const def = defaultKeywords.find(k => all.includes(k)) || all[0];
    sel.value = def;
    renderKeywordChart(canvasId, def);
    sel.addEventListener('change', () => renderKeywordChart(canvasId, sel.value));
  }

  return { build, renderLists, initSelector, renderKeywordChart };
})();
