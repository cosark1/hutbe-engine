// modal.js — anahtar kelime detay paneli (hutbe görünümü artık reading.js'de, modal değil)
window.App = window.App || {};
App.kwModal = (function(){
  let kwIndex = null, catChart = null, yearChart = null;
  function buildIndex(kelimeler){
    kwIndex = {};
    kelimeler.forEach(r => { (kwIndex[r.keyword] = kwIndex[r.keyword] || []).push({date:r.date, title:r.title, category:r.category}); });
  }
  function overlay(){ return document.getElementById('kw-modal'); }
  function open(keyword){
    const entries = kwIndex[keyword] || [];
    const uniq = []; const seen = new Set();
    entries.forEach(e => { if (!seen.has(e.date)){ seen.add(e.date); uniq.push(e); } });
    document.getElementById('kw-modal-title').textContent = keyword;
    document.getElementById('kw-modal-count').textContent = entries.length;
    document.getElementById('kw-modal-hutbecount').textContent = uniq.length;

    const catCounts = {}; entries.forEach(e => catCounts[e.category] = (catCounts[e.category]||0)+1);
    const catLabels = Object.keys(catCounts).sort((a,b)=>catCounts[b]-catCounts[a]).slice(0,8);
    const catData = catLabels.map(c => catCounts[c]);
    const yearCounts = {}; entries.forEach(e => { const y = e.date.split('.')[2]; yearCounts[y] = (yearCounts[y]||0)+1; });
    const yearLabels = Object.keys(yearCounts).sort();
    const yearData = yearLabels.map(y => yearCounts[y]);

    if (catChart) catChart.destroy();
    if (yearChart) yearChart.destroy();
    catChart = new Chart(document.getElementById('kw-modal-cat-chart').getContext('2d'), { type:'bar', data:{labels:catLabels, datasets:[{data:catData, backgroundColor:'#b8863acc', borderRadius:4}]}, options:{indexAxis:'y', responsive:true, maintainAspectRatio:false, plugins:{legend:{display:false}}, scales:{x:{beginAtZero:true,ticks:{stepSize:1}}, y:{ticks:{font:{size:10}}}}} });
    yearChart = new Chart(document.getElementById('kw-modal-year-chart').getContext('2d'), { type:'bar', data:{labels:yearLabels, datasets:[{data:yearData, backgroundColor:'#3f7d6bcc', borderRadius:4}]}, options:{responsive:true, maintainAspectRatio:false, plugins:{legend:{display:false}}, scales:{y:{beginAtZero:true,ticks:{stepSize:1}}}} });

    uniq.sort((a,b) => App.util.parseTrDate(b.date) - App.util.parseTrDate(a.date));
    document.getElementById('kw-modal-hutbe-list').innerHTML = uniq.map(e => `<div class="kw-hutbe-item" data-date="${e.date}"><span>${App.util.esc(e.title)}</span> <span style="color:var(--ink-soft);font-size:11px;">${e.date}</span></div>`).join('');
    document.getElementById('kw-modal-hutbe-list').querySelectorAll('.kw-hutbe-item').forEach(el => {
      el.addEventListener('click', () => { close(); App.reading.open(el.dataset.date); });
    });
    overlay().classList.add('open');
  }
  function close(){ overlay().classList.remove('open'); }
  function init(kelimeler){
    buildIndex(kelimeler);
    document.getElementById('kw-modal-close-btn').addEventListener('click', close);
    overlay().addEventListener('click', (e) => { if (e.target === overlay()) close(); });
    document.addEventListener('keydown', (e) => { if (e.key === 'Escape') close(); });
  }
  function getIndex(){ return kwIndex; }
  return { init, open, close, getIndex };
})();
