// suramap.js — Faz 3.3: 114 surelik kapsam haritası
window.App = window.App || {};
App.suramap = (function(){
  async function render(rootId, ayetler){
    const suralar = await App.data.loadJSON('data/suralar.json');
    const counts = {};
    ayetler.forEach(r => { counts[r.sure] = (counts[r.sure]||0) + 1; });
    const maxC = Math.max(1, ...Object.values(counts));
    const root = document.getElementById(rootId);
    root.innerHTML = `<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(96px,1fr));gap:6px;">` +
      suralar.map(s => {
        const c = counts[s.name] || 0;
        const alpha = c === 0 ? 0 : 0.2 + 0.8*(c/maxC);
        const bg = c === 0 ? 'var(--border)' : `rgba(184,134,58,${alpha.toFixed(2)})`;
        const fg = c === 0 ? 'var(--ink-soft)' : (alpha > 0.55 ? '#fff' : 'var(--ink)');
        return `<div title="${s.no}. ${App.util.esc(s.name)} — ${c} atıf" style="background:${bg};color:${fg};border-radius:8px;padding:8px 6px;text-align:center;font-size:11px;">
          <div style="font-size:9px;opacity:.7;">${s.no}</div>${App.util.esc(s.name)}<div style="font-weight:700;font-size:12px;">${c}</div>
        </div>`;
      }).join('') + `</div>`;
    const used = Object.keys(counts).length;
    document.getElementById(rootId + '-summary').textContent = `${used} / 114 surede en az bir atıf var (${suralar.length - used} sureye hiç atıfta bulunulmamış).`;
  }
  return { render };
})();
