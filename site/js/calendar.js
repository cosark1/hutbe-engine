// calendar.js — Faz 3.1: Takvim-gündem bağlantısı
window.App = window.App || {};
App.calendar = (function(){
  function nearestHutbeler(hutbeler, eventDate, windowDays){
    const ed = App.util.parseTrDate(eventDate);
    return hutbeler
      .map(h => ({ h, diff: (App.util.parseTrDate(h.date) - ed) / 86400000 }))
      .filter(x => Math.abs(x.diff) <= windowDays)
      .sort((a,b) => Math.abs(a.diff) - Math.abs(b.diff));
  }
  async function render(rootId, hutbeler){
    const events = await App.data.loadJSON('data/events.json');
    const root = document.getElementById(rootId);
    const rows = events.map(ev => {
      const near = nearestHutbeler(hutbeler, ev.date, 10);
      const first = near[0];
      let hutbeHtml;
      if (first){
        const yon = first.diff >= 0 ? `${Math.round(first.diff)} gün sonra` : `${Math.round(-first.diff)} gün önce`;
        hutbeHtml = `<div class="similar-item" data-date="${first.h.date}">${App.util.esc(first.h.title)}</div><div style="font-size:11.5px;color:var(--ink-soft);">${first.h.date} · ${yon} · <span class="badge">${App.util.esc(first.h.primary_category)}</span></div>`;
      } else {
        hutbeHtml = `<div style="font-size:12.5px;color:var(--ink-soft);">±10 gün içinde eşleşen hutbe bulunamadı</div>`;
      }
      return `<div style="display:grid;grid-template-columns:170px 1fr;gap:14px;padding:12px 0;border-bottom:1px solid var(--border);">
        <div><div style="font-weight:600;font-size:13px;">${ev.date}</div><span class="badge sec" style="font-size:10.5px;">${App.util.esc(ev.tip)}</span></div>
        <div><div style="font-size:13.5px;margin-bottom:4px;">${App.util.esc(ev.title)}</div>${hutbeHtml}</div>
      </div>`;
    }).join('');
    root.innerHTML = rows;
    root.querySelectorAll('.similar-item[data-date]').forEach(el => el.addEventListener('click', () => App.reading.open(el.dataset.date)));
  }
  return { render };
})();
