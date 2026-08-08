// lag_analizi.js — İP-6: Hutbe ile TCCB (Cumhurbaşkanlığı) resmi söylem karşılaştırması
window.App = window.App || {};

App.lagAnalizi = (function(){
  function durumEtiket(durum){
    if (durum === 'ONCU_TCCB') return 'TCCB önce';
    if (durum === 'ONCU_HUTBE') return 'Hutbe önce';
    if (durum === 'AYNI_GUN') return 'Aynı gün';
    return '—';
  }
  function durumRenk(durum){
    if (durum === 'ONCU_TCCB') return 'var(--warm-2)';
    if (durum === 'ONCU_HUTBE') return 'var(--warm-1)';
    return 'var(--ink-soft)';
  }

  async function render(opts){
    const { statElId, caveatElId, tableElId } = opts;
    const data = await App.data.loadJSON('data/lag_analizi.json');
    const o = data.ozet;

    const statEl = document.getElementById(statElId);
    statEl.innerHTML = `
      <div class="kpi-card">
        <div class="kpi-label">Kapsam</div>
        <div class="kpi-value" style="font-size:17px;">${o.hutbe_sayisi} hutbe</div>
        <div class="kpi-sub">${o.kapsam.baslangic}–${o.kapsam.bitis} · ${o.tccb_konusma_sayisi} TCCB konuşmasıyla karşılaştırıldı</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Hutbe Bazında — TCCB Önce Konuşmuş</div>
        <div class="kpi-value" style="color:var(--warm-2);">${o.hutbe_bazinda.TCCB_ONCE_EN_AZ_BIR} / ${o.hutbe_sayisi}</div>
        <div class="kpi-sub">hutbenin en az bir anahtar kelimesi, ±30 gün içinde TCCB'de daha önce (ya da aynı gün) geçmiş</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Ortalama Gecikme</div>
        <div class="kpi-value">${o.ortalama_gecikme_gun} gün</div>
        <div class="kpi-sub">negatif = TCCB önce konuşmuş (tüm eşleşen kelime-çiftleri, ham/düzeltilmemiş)</div>
      </div>`;

    const jenerikListesi = data.jenerik_ornekler.map(j => `${App.util.esc(j.kelime)} (${j.adet})`).join(', ');
    const caveatEl = document.getElementById(caveatElId);
    caveatEl.innerHTML = `<b>Dikkat — ham sayı yanıltıcı olabilir:</b> "TCCB önce" olarak işaretlenen kelime-çiftlerinin en sık örnekleri ${jenerikListesi} gibi <b>kronik/jenerik</b> kelimeler — bunlar hemen her siyasi konuşmada geçer, hutbeyle gerçek bir tema örtüşmesinden değil, TCCB'nin ~3 kat daha sık konuşmasından kaynaklanan istatistiksel bir yapaylık. Aşağıdaki tablo yalnızca açıkça <b>olay-özgü</b> kelime kümelerini (Gazze, terör, deprem, salgın, mülteci, 15 Temmuz, orman yangınları) gösteriyor — buradaki örüntü daha güvenilir.`;

    const tEl = document.getElementById(tableElId);
    let html = '<table class="data-table" style="width:100%;border-collapse:collapse;font-size:12.5px;"><thead><tr>' +
      '<th style="text-align:left;padding:6px 8px;">Olay/Tema</th>' +
      '<th style="text-align:right;padding:6px 8px;">n</th>' +
      '<th style="text-align:right;padding:6px 8px;">TCCB önce</th>' +
      '<th style="text-align:right;padding:6px 8px;">Ort. gecikme</th>' +
      '<th style="text-align:left;padding:6px 8px;">Örnek</th></tr></thead><tbody>';
    data.olay_ozel.forEach(g => {
      const ornek = g.ornekler[0];
      const tccbYil = ornek && ornek.tccb_tarih ? ornek.tccb_tarih.split('.').pop() : null;
      const ornekHtml = ornek ? `<span class="kw-hutbe-item lag-hutbe-link" data-date="${ornek.hutbe_tarih}" style="color:var(--accent);cursor:pointer;">${ornek.hutbe_tarih} "${App.util.esc(ornek.hutbe_baslik)}"</span>` +
        (ornek.tccb_id ? ` <span class="lag-tccb-link" data-yil="${tccbYil}" data-id="${ornek.tccb_id}" style="color:var(--ink-soft);font-size:11px;cursor:pointer;text-decoration:underline;">↔ TCCB ${ornek.tccb_tarih}</span>` : '') : '—';
      html += `<tr style="border-bottom:1px solid var(--border);vertical-align:top;">` +
        `<td style="padding:6px 8px;font-weight:600;">${App.util.esc(g.grup)}</td>` +
        `<td style="padding:6px 8px;text-align:right;">${g.n}</td>` +
        `<td style="padding:6px 8px;text-align:right;color:${durumRenk('ONCU_TCCB')};">%${g.tccb_once_yuzde}</td>` +
        `<td style="padding:6px 8px;text-align:right;">${g.ortalama_gecikme_gun !== null ? g.ortalama_gecikme_gun + ' gün' : '—'}</td>` +
        `<td style="padding:6px 8px;">${ornekHtml}</td></tr>`;
    });
    html += '</tbody></table>';
    tEl.innerHTML = html;
    tEl.querySelectorAll('.lag-hutbe-link[data-date]').forEach(el => el.addEventListener('click', () => App.reading.open(el.dataset.date)));
    tEl.querySelectorAll('.lag-tccb-link[data-id]').forEach(el => el.addEventListener('click', () => App.tccbReading.open(el.dataset.yil, el.dataset.id)));
  }
  return { render };
})();
