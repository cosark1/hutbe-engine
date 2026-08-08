// heatmap.js — haftalık tema yoğunluğu (her tema kendi rengiyle)
window.App = window.App || {};
App.heatmap = {
  render(wg, monthsElId, heatmapElId, legendElId, tooltipElId){
    const catOrder = wg.category_order || [];
    const colors = App.charts.palette(catOrder.length);
    const monthsRow = document.getElementById(monthsElId);
    const monthNamesShort = ["Oca","Şub","Mar","Nis","May","Haz","Tem","Ağu","Eyl","Eki","Kas","Ara"];
    let monthHtml = '';
    for (let w = 1; w <= wg.weeks; w++){
      const approxMonth = Math.floor((w-1)/4.345);
      const isFirst = w === 1 || Math.floor((w-2)/4.345) !== approxMonth;
      monthHtml += `<span>${isFirst ? monthNamesShort[approxMonth % 12] : ''}</span>`;
    }
    monthsRow.innerHTML = monthHtml;
    const tooltip = document.getElementById(tooltipElId);
    const heatmap = document.getElementById(heatmapElId);
    let html = '';
    wg.years.forEach(y => {
      const row = wg.grid[y];
      html += `<div class="heatmap-row"><span class="year-label">${y}</span>`;
      for (let w = 0; w < wg.weeks; w++){
        const cell = row[w];
        if (cell){
          const color = colors[cell.ci % colors.length] || '#adb5bd';
          html += `<div class="week-cell filled" style="background:${color}" data-date="${cell.date}" data-title="${App.util.esc(cell.title)}" data-cat="${App.util.esc(cell.cat)}"></div>`;
        } else { html += `<div class="week-cell"></div>`; }
      }
      html += `</div>`;
    });
    heatmap.innerHTML = html;
    heatmap.querySelectorAll('.week-cell.filled').forEach(el => {
      el.addEventListener('mouseenter', () => {
        tooltip.style.display = 'block';
        tooltip.innerHTML = `<b>${el.dataset.date}</b><br>${el.dataset.title}<br><span style="opacity:.75">${el.dataset.cat}</span>`;
      });
      el.addEventListener('mousemove', (e) => { tooltip.style.left = (e.clientX+14)+'px'; tooltip.style.top = (e.clientY+14)+'px'; });
      el.addEventListener('mouseleave', () => { tooltip.style.display = 'none'; });
      el.addEventListener('click', () => { if (App.reading) App.reading.open(el.dataset.date); });
    });
    if (legendElId){
      document.getElementById(legendElId).innerHTML = catOrder.map((c,i) =>
        `<span class="sw" style="display:inline-flex;align-items:center;gap:5px;margin-right:12px;"><span class="dot" style="background:${colors[i % colors.length]};width:11px;height:11px;border-radius:3px;display:inline-block;"></span>${App.util.esc(c)}</span>`
      ).join('');
    }
  }
};
