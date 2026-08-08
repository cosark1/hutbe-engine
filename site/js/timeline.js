// timeline.js — Faz 3.1: Bağlam zaman çizelgesi (İP-4)
// Yatay zaman çizelgesi: dini/siyasi/kriz bağlam etiketleri + seçilen
// bağlamın hutbe teması dağılımı. Kaynak: arastirma/baglam_takvimi.csv
window.App = window.App || {};
App.timeline = (function(){
  const TYPE_META = {
    dini_gun:    { renk: '#b8863a', ad: 'Dini gün / kandil' },
    siyasi_olay: { renk: '#446b9e', ad: 'Seçim / referandum' },
    kriz_olayi:  { renk: '#a8552f', ad: 'Kriz / afet' },
  };

  function baseLabel(s){
    let out = s;
    if (out.includes(' öncesi')) out = out.split(' öncesi')[0];
    else if (out.includes(' sonrası')) out = out.split(' sonrası')[0];
    if (out.includes('(+')) out = out.split('(+')[0].trim();
    return out.trim();
  }

  function build(baglam, hutbeler){
    const byDate = {};
    baglam.forEach(r => { byDate[r.tarih] = r; });
    const hutbeByDate = {};
    hutbeler.forEach(h => { hutbeByDate[h.date] = h; });

    const labelSet = new Set();
    baglam.forEach(r => {
      ['dini_gun','siyasi_olay','kriz_olayi'].forEach(k => r[k].forEach(s => labelSet.add(baseLabel(s))));
    });
    const labels = [...labelSet].sort((a,b) => a.localeCompare(b, 'tr'));

    return { byDate, hutbeByDate, labels };
  }

  function renderGrid(gridElId, monthsElId, legendElId, baglam, hutbeler, onCellClick){
    const years = [...new Set(hutbeler.map(h => h.year))].sort((a,b)=>a-b);
    const weeksPerYear = 53;
    const monthsRow = document.getElementById(monthsElId);
    if (monthsRow){
      const monthNamesShort = ["Oca","Şub","Mar","Nis","May","Haz","Tem","Ağu","Eyl","Eki","Kas","Ara"];
      let mh = '';
      for (let w = 1; w <= weeksPerYear; w++){
        const approxMonth = Math.floor((w-1)/4.345);
        const isFirst = w === 1 || Math.floor((w-2)/4.345) !== approxMonth;
        mh += `<span>${isFirst ? monthNamesShort[approxMonth % 12] : ''}</span>`;
      }
      monthsRow.innerHTML = mh;
    }

    // hafta_id -> baglam row, tarih -> hafta index within its year
    const byYear = {};
    years.forEach(y => byYear[y] = new Array(weeksPerYear).fill(null));
    baglam.forEach(r => {
      const d = App.util.parseTrDate(r.tarih);
      const y = d.getFullYear();
      if (!byYear[y]) return;
      const jan1 = new Date(y,0,1);
      const w = Math.min(weeksPerYear-1, Math.floor((d - jan1) / 604800000));
      byYear[y][w] = r;
    });

    const root = document.getElementById(gridElId);
    let html = '';
    years.forEach(y => {
      html += `<div class="heatmap-row"><span class="year-label">${y}</span>`;
      byYear[y].forEach(cell => {
        if (!cell || (!cell.dini_gun.length && !cell.siyasi_olay.length && !cell.kriz_olayi.length)){
          html += `<div class="week-cell"></div>`;
          return;
        }
        const type = cell.dini_gun.length ? 'dini_gun' : (cell.kriz_olayi.length ? 'kriz_olayi' : 'siyasi_olay');
        const color = TYPE_META[type].renk;
        const allTags = [...cell.dini_gun, ...cell.siyasi_olay, ...cell.kriz_olayi].join(' · ');
        html += `<div class="week-cell filled" style="background:${color}" data-tarih="${cell.tarih}" data-tags="${App.util.esc(allTags)}"></div>`;
      });
      html += `</div>`;
    });
    root.innerHTML = html;

    const tooltip = document.getElementById('timeline-tooltip');
    root.querySelectorAll('.week-cell.filled').forEach(el => {
      el.addEventListener('mouseenter', () => {
        if (!tooltip) return;
        tooltip.style.display = 'block';
        tooltip.innerHTML = `<b>${el.dataset.tarih}</b><br>${el.dataset.tags}`;
      });
      el.addEventListener('mousemove', (e) => { if (tooltip){ tooltip.style.left = (e.clientX+14)+'px'; tooltip.style.top = (e.clientY+14)+'px'; } });
      el.addEventListener('mouseleave', () => { if (tooltip) tooltip.style.display = 'none'; });
      el.addEventListener('click', () => onCellClick(el.dataset.tarih));
    });

    if (legendElId){
      document.getElementById(legendElId).innerHTML = Object.entries(TYPE_META).map(([k,v]) =>
        `<span style="display:inline-flex;align-items:center;gap:5px;margin-right:16px;"><span style="background:${v.renk};width:11px;height:11px;border-radius:3px;display:inline-block;"></span>${v.ad}</span>`
      ).join('');
    }
  }

  function highlightLabel(gridElId, label){
    const root = document.getElementById(gridElId);
    root.querySelectorAll('.week-cell.filled').forEach(el => {
      const on = label && el.dataset.tags && el.dataset.tags.split(' · ').some(t => baseLabel(t) === label);
      el.classList.toggle('week-cell-dim', !!label && !on);
      el.classList.toggle('week-cell-hit', !!on);
    });
  }

  function renderDistribution(chartId, sumElId, ctx, label){
    const dates = [];
    ctx.baglam.forEach(r => {
      const hit = [...r.dini_gun, ...r.siyasi_olay, ...r.kriz_olayi].some(s => baseLabel(s) === label);
      if (hit) dates.push(r.tarih);
    });
    const rows = dates.map(d => ctx.hutbeByDate[d]).filter(Boolean);
    const counts = {};
    rows.forEach(h => { counts[h.primary_category] = (counts[h.primary_category]||0) + 1; });
    const entries = Object.entries(counts).sort((a,b) => b[1]-a[1]);
    App.charts.renderHBar(chartId, entries.map(e=>e[0]), entries.map(e=>e[1]), '#b8863acc');
    if (sumElId){
      document.getElementById(sumElId).textContent = rows.length
        ? `"${label}" bağlamındaki ${rows.length} hutbe içinde en sık tema: ${entries[0] ? entries[0][0] : '-'} (${entries[0] ? entries[0][1] : 0} hutbe)`
        : `"${label}" bağlamında eşleşen hutbe bulunamadı`;
    }
  }

  async function render(opts){
    const { gridElId, monthsElId, legendElId, selectElId, chartId, sumElId, hutbeler } = opts;
    const baglam = await App.data.loadJSON('data/baglam_takvimi.json');
    const ctx = build(baglam, hutbeler);
    ctx.baglam = baglam;

    renderGrid(gridElId, monthsElId, legendElId, baglam, hutbeler, (date) => App.reading.open(date));

    const sel = document.getElementById(selectElId);
    sel.innerHTML = '<option value="">— bağlam seçin —</option>' + ctx.labels.map(l => `<option value="${App.util.esc(l)}">${App.util.esc(l)}</option>`).join('');
    sel.addEventListener('change', () => {
      const label = sel.value;
      highlightLabel(gridElId, label);
      if (label) renderDistribution(chartId, sumElId, ctx, label);
      else { App.charts.destroy(chartId); if (sumElId) document.getElementById(sumElId).textContent = 'Bir bağlam seçtiğinizde, o dönemdeki hutbelerin tema dağılımı burada görünür.'; }
    });
  }

  return { render };
})();
