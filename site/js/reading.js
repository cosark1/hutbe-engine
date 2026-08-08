// reading.js — Faz 3.6: modal yerine kalıcı hutbe okuma sayfası (hash ile bağlantı verilebilir)
window.App = window.App || {};
App.reading = (function(){
  let hutbeByDate = {};
  function index(hutbeler){ hutbeler.forEach(h => hutbeByDate[h.date] = h); }

  function computeSimilar(date, keywords){
    const kwIndex = App.kwModal.getIndex();
    const scores = {};
    (keywords||[]).forEach(kw => {
      (kwIndex[kw]||[]).forEach(e => { if (e.date !== date) scores[e.date] = (scores[e.date]||0)+1; });
    });
    return Object.entries(scores).sort((a,b)=>b[1]-a[1]).slice(0,6)
      .map(([d,c]) => ({ date:d, count:c, title:(hutbeByDate[d]||{}).title||'' }));
  }

  async function open(date){
    location.hash = '#/oku/' + date;
    await renderCurrent();
    window.scrollTo(0,0);
  }

  async function renderCurrent(){
    const m = location.hash.match(/^#\/oku\/(.+)$/);
    if (!m) return false;
    const date = m[1];
    const light = hutbeByDate[date];
    if (!light) return false;
    const page = document.getElementById('reading-page');
    document.querySelectorAll('.section, #reading-page').forEach(el => el.style.display = 'none');
    page.style.display = 'block';
    page.innerHTML = `<span class="back-link">‹ Panele dön</span><h1>${App.util.esc(light.title)}</h1>
      <div class="rp-meta">${date} · <span class="badge">${App.util.esc(light.primary_category)}</span> ${ (light.secondary_categories||[]).map(c=>`<span class="badge sec">${App.util.esc(c)}</span>`).join('') }</div>
      <div class="rp-summary">${App.util.esc(light.summary)}</div>
      <div style="margin-bottom:18px;display:flex;gap:6px;flex-wrap:wrap;">${(light.keywords||[]).map(k=>`<span class="badge kw-link" data-kw="${App.util.esc(k)}" style="cursor:pointer;">${App.util.esc(k)}</span>`).join('')}</div>
      <div class="rp-text">Yükleniyor…</div>
      <div class="rp-similar"><h4 style="font-size:12px;text-transform:uppercase;color:var(--ink-soft);margin-bottom:10px;">Benzer Hutbeler (ortak anahtar kelime)</h4><div class="rp-similar-list"></div></div>`;
    page.querySelector('.back-link').addEventListener('click', () => { history.replaceState(null,'',location.pathname); showDashboard(); });
    page.querySelectorAll('.kw-link').forEach(el => el.addEventListener('click', () => App.kwModal.open(el.dataset.kw)));

    const full = await App.data.getHutbeText(date);
    const highlighted = App.util.esc(full.text).replace(/[“"]([^“”"]{8,400})[”"]/g, (m0, inner) => `“<mark class="hl">${inner}</mark>”`);
    page.querySelector('.rp-text').innerHTML = highlighted;

    const similar = computeSimilar(date, light.keywords);
    const simWrap = page.querySelector('.rp-similar-list');
    if (similar.length){
      simWrap.innerHTML = similar.map(s => `<div class="similar-item" data-date="${s.date}">${App.util.esc(s.title)} <span style="color:var(--ink-soft);">(${s.date} · ${s.count} ortak kelime)</span></div>`).join('');
      simWrap.querySelectorAll('.similar-item').forEach(el => el.addEventListener('click', () => open(el.dataset.date)));
    } else {
      simWrap.innerHTML = '<span style="color:var(--ink-soft);font-size:13px;">Ortak anahtar kelimeli başka hutbe bulunamadı.</span>';
    }
    return true;
  }

  function showDashboard(){
    document.getElementById('reading-page').style.display = 'none';
    if (App.nav) App.nav.showActive();
    else document.querySelectorAll('.section').forEach(el => el.style.display = 'block');
  }

  window.addEventListener('hashchange', () => {
    if (location.hash.startsWith('#/oku/')) renderCurrent();
    else showDashboard();
  });

  return { init: index, open, renderCurrent, showDashboard };
})();
