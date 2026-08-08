// tccb_reading.js — İP-6: TCCB (Cumhurbaşkanlığı) konuşması için site-içi okuma sayfası
// reading.js'teki hutbe okuma sayfasının aynısı, kaynak kendi arşivimizden (yerel, tccb.gov.tr'ye gitmeden)
window.App = window.App || {};
App.tccbReading = (function(){
  function open(yil, id){
    location.hash = `#/tccb/${yil}/${id}`;
    renderCurrent();
    window.scrollTo(0,0);
  }

  async function renderCurrent(){
    const m = location.hash.match(/^#\/tccb\/(\d+)\/(\d+)$/);
    if (!m) return false;
    const [, yil, id] = m;
    const page = document.getElementById('tccb-reading-page');
    document.querySelectorAll('.section, #reading-page, #tccb-reading-page').forEach(el => el.style.display = 'none');
    page.style.display = 'block';
    page.innerHTML = `<span class="back-link">‹ Panele dön</span><div class="rp-text">Yükleniyor…</div>`;
    page.querySelector('.back-link').addEventListener('click', () => { history.replaceState(null,'',location.pathname); showDashboard(); });

    const kayit = await App.data.getTccbText(yil, id);
    if (!kayit){
      page.querySelector('.rp-text').innerHTML = 'Konuşma bulunamadı.';
      return true;
    }
    page.innerHTML = `<span class="back-link">‹ Panele dön</span><h1>${App.util.esc(kayit.baslik)}</h1>
      <div class="rp-meta">${kayit.tarih} · <span class="badge sec">T.C. Cumhurbaşkanlığı — Konuşma</span></div>
      <div class="rp-text">${App.util.esc(kayit.metin).replace(/\n\n/g, '</p><p>').replace(/^/, '<p>').replace(/$/, '</p>')}</div>
      <div style="margin-top:18px;font-size:12px;color:var(--ink-soft);">Kaynak: <a href="${kayit.url}" target="_blank" rel="noopener">tccb.gov.tr</a></div>`;
    page.querySelector('.back-link').addEventListener('click', () => { history.replaceState(null,'',location.pathname); showDashboard(); });
    return true;
  }

  function showDashboard(){
    document.getElementById('tccb-reading-page').style.display = 'none';
    if (App.nav) App.nav.showActive();
    else document.querySelectorAll('.section').forEach(el => el.style.display = 'block');
  }

  window.addEventListener('hashchange', () => {
    if (location.hash.startsWith('#/tccb/')) renderCurrent();
    else if (!location.hash.startsWith('#/oku/')) showDashboard();
  });

  return { open, renderCurrent, showDashboard };
})();
