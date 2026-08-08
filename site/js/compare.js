// compare.js — Faz 3.5: iki yıl veya iki tema karşılaştırma modu
window.App = window.App || {};
App.compare = (function(){
  let hutbeler = [], kelimeler = [], categories = [];

  function init(data){
    hutbeler = data.hutbeler; kelimeler = data.kelimeler; categories = data.meta.overall_category.labels;
  }

  function optionsHtml(){
    const years = [...new Set(hutbeler.map(h=>h.year))].sort();
    const yearOpts = years.map(y => `<option value="year:${y}">Yıl: ${y}</option>`).join('');
    const catOpts = categories.map(c => `<option value="cat:${App.util.esc(c)}">Tema: ${App.util.esc(c)}</option>`).join('');
    return `<optgroup label="Yıllar">${yearOpts}</optgroup><optgroup label="Temalar">${catOpts}</optgroup>`;
  }

  function selectHutbeler(sel){
    const [type, value] = sel.split(':');
    if (type === 'year') return hutbeler.filter(h => String(h.year) === value);
    return hutbeler.filter(h => h.primary_category === value || (h.secondary_categories||[]).includes(value));
  }

  function statsFor(sel){
    const rows = selectHutbeler(sel);
    const dateSet = new Set(rows.map(r=>r.date));
    const kws = kelimeler.filter(k => dateSet.has(k.date));
    const kwCount = {};
    kws.forEach(k => kwCount[k.keyword] = (kwCount[k.keyword]||0)+1);
    const topKw = Object.entries(kwCount).sort((a,b)=>b[1]-a[1]).slice(0,10);
    const avgCitation = rows.length ? (rows.reduce((a,r)=>a+(r.citation_count||0),0)/rows.length) : 0;
    const catDist = {};
    rows.forEach(r => catDist[r.primary_category] = (catDist[r.primary_category]||0)+1);
    return { count: rows.length, topKw, avgCitation, catDist, kwSet: new Set(Object.keys(kwCount)) };
  }

  function render(selectAId, selectBId, outAId, outBId, commonId){
    const selA = document.getElementById(selectAId), selB = document.getElementById(selectBId);
    selA.innerHTML = optionsHtml(); selB.innerHTML = optionsHtml();
    selA.value = selA.querySelector('option').value;
    const opts = selA.querySelectorAll('option');
    if (opts[5]) selB.value = opts[5].value; else selB.value = opts[0].value;

    function renderSide(sel, outId){
      const s = statsFor(sel.value);
      const topCats = Object.entries(s.catDist).sort((a,b)=>b[1]-a[1]).slice(0,5);
      document.getElementById(outId).innerHTML = `
        <div class="compare-stat-row"><span>Hutbe sayısı</span><b>${s.count}</b></div>
        <div class="compare-stat-row"><span>Ort. atıf/hutbe</span><b>${s.avgCitation.toFixed(1)}</b></div>
        <div style="margin-top:10px;font-size:11.5px;color:var(--ink-soft);text-transform:uppercase;">Öne çıkan temalar</div>
        ${topCats.map(([c,n])=>`<div class="compare-stat-row"><span>${App.util.esc(c)}</span><span>${n}</span></div>`).join('')}
        <div style="margin-top:10px;font-size:11.5px;color:var(--ink-soft);text-transform:uppercase;">En sık anahtar kelimeler</div>
        ${s.topKw.map(([k,n])=>`<div class="compare-stat-row"><span>${App.util.esc(k)}</span><span>${n}</span></div>`).join('')}
      `;
      return s;
    }
    function renderAll(){
      const sA = renderSide(selA, outAId);
      const sB = renderSide(selB, outBId);
      const common = [...sA.kwSet].filter(k => sB.kwSet.has(k));
      document.getElementById(commonId).textContent = common.length ? common.slice(0,20).join(', ') : 'Ortak anahtar kelime bulunamadı.';
    }
    selA.addEventListener('change', renderAll);
    selB.addEventListener('change', renderAll);
    renderAll();
  }
  return { init, render };
})();
