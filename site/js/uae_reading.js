// uae_reading.js — İP-7: BAE (Awqaf.ae) hutbesi için site-içi okuma sayfası
// tccb_reading.js ile aynı desen; kayıt hem Arapça orijinali hem resmi İngilizce çeviriyi içeriyor
window.App = window.App || {};
App.uaeReading = (function(){
  function open(yil, id){
    location.hash = `#/uae/${yil}/${id}`;
    renderCurrent();
    window.scrollTo(0,0);
  }

  async function renderCurrent(){
    const m = location.hash.match(/^#\/uae\/(\d+)\/(\d+)$/);
    if (!m) return false;
    const [, yil, id] = m;
    const page = document.getElementById('uae-reading-page');
    document.querySelectorAll('.section, #reading-page, #tccb-reading-page, #uae-reading-page').forEach(el => el.style.display = 'none');
    page.style.display = 'block';
    page.innerHTML = `<span class="back-link">‹ Panele dön</span><div class="rp-text">Yükleniyor…</div>`;
    page.querySelector('.back-link').addEventListener('click', () => { history.replaceState(null,'',location.pathname); showDashboard(); });

    const kayit = await App.data.getUaeText(yil, id);
    if (!kayit){
      page.querySelector('.rp-text').innerHTML = 'Hutbe bulunamadı.';
      return true;
    }
    const enPar = kayit.en_metin ? App.util.esc(kayit.en_metin).replace(/\n\n/g, '</p><p>').replace(/^/, '<p>').replace(/$/, '</p>') : '<p style="color:var(--ink-soft);">Bu kayıt için resmi İngilizce çeviri mevcut değil.</p>';
    const arPar = kayit.ar_metin ? App.util.esc(kayit.ar_metin).replace(/\n\n/g, '</p><p>').replace(/^/, '<p>').replace(/$/, '</p>') : '';
    page.innerHTML = `<span class="back-link">‹ Panele dön</span><h1>${App.util.esc(kayit.baslik)}</h1>
      <div class="rp-meta">${kayit.tarih} · <span class="badge sec">BAE Awqaf — Cuma Hutbesi</span></div>
      <div class="rp-summary" style="font-size:12.5px;">Bu hutbe, Türkiye Diyanet korpusuna değil, İP-7 karşılaştırma çalışması kapsamında kazınan Birleşik Arap Emirlikleri (Awqaf) arşivine ait. Aşağıda kurumun kendi resmi İngilizce çevirisi (esas okunan metin), altında Arapça orijinali yer alıyor.</div>
      <h4 style="font-size:12px;text-transform:uppercase;color:var(--ink-soft);margin:22px 0 10px;">Resmi İngilizce Çeviri</h4>
      <div class="rp-text" style="font-size:15px;">${enPar}</div>
      ${arPar ? `<h4 style="font-size:12px;text-transform:uppercase;color:var(--ink-soft);margin:28px 0 10px;">Arapça Orijinal</h4><div class="rp-text" dir="rtl" style="font-size:15px;">${arPar}</div>` : ''}
      <div style="margin-top:18px;font-size:12px;color:var(--ink-soft);">Kaynak: <a href="${kayit.url}" target="_blank" rel="noopener">awqaf.ae</a></div>`;
    page.querySelector('.back-link').addEventListener('click', () => { history.replaceState(null,'',location.pathname); showDashboard(); });
    return true;
  }

  function showDashboard(){
    document.getElementById('uae-reading-page').style.display = 'none';
    if (App.nav) App.nav.showActive();
    else document.querySelectorAll('.section').forEach(el => el.style.display = 'block');
  }

  window.addEventListener('hashchange', () => {
    if (location.hash.startsWith('#/uae/')) renderCurrent();
    else if (!location.hash.startsWith('#/oku/') && !location.hash.startsWith('#/tccb/')) showDashboard();
  });

  return { open, renderCurrent, showDashboard };
})();
