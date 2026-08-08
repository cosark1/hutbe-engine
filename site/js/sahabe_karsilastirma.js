// sahabe_karsilastirma.js — İP-7: Diyanet ile BAE'de geçen sahabe isimleri karşılaştırması
window.App = window.App || {};

App.sahabeKarsilastirma = (function(){
  async function render(opts){
    const { tableElId, noteElId } = opts;
    const data = await App.data.loadJSON('data/sahabe_karsilastirma_diyanet_bae.json');

    const noteEl = document.getElementById(noteElId);
    noteEl.innerHTML = `<b>Not:</b> Sayımlar, hutbe kapanışındaki sabit "Hulefâ-yi Râşidîn" (Abu Bakr, Ömer, Osman, Ali) dua formülünü hariç tutuyor — yalnızca gövde içinde bir anekdot/örneklik bağlamında anılan sahabeler sayıldı. Değerler, o ismin geçtiği <b>benzersiz hutbe sayısının</b> yüzdesi (Diyanet ${data.diyanet_toplam}, BAE ${data.bae_toplam} hutbe üzerinden).`;

    const tEl = document.getElementById(tableElId);
    let html = '<table class="data-table" style="width:100%;"><thead><tr><th>Sahabe</th><th style="text-align:right;">Diyanet</th><th style="text-align:right;">BAE</th><th>Örnek (BAE)</th></tr></thead><tbody>';
    data.sahabeler.forEach(s => {
      const ornek = s.bae_ornekler[0];
      const ornekHtml = ornek ? `<span class="cmp-ex-item sahabe-bae-link" data-yil="${ornek.yil}" data-id="${ornek.id}" style="color:var(--accent);cursor:pointer;">${ornek.tarih} — ${App.util.esc(ornek.baslik)}</span>` : '—';
      html += `<tr><td>${App.util.esc(s.isim)}</td>` +
        `<td style="text-align:right;">${s.diyanet_hutbe} <span style="color:var(--ink-soft);">(%${s.diyanet_yuzde})</span></td>` +
        `<td style="text-align:right;color:var(--warm-2);">${s.bae_hutbe} <span style="color:var(--ink-soft);">(%${s.bae_yuzde})</span></td>` +
        `<td>${ornekHtml}</td></tr>`;
    });
    html += '</tbody></table>';
    tEl.innerHTML = html;
    tEl.querySelectorAll('.sahabe-bae-link[data-id]').forEach(el => el.addEventListener('click', () => App.uaeReading.open(el.dataset.yil, el.dataset.id)));
  }
  return { render };
})();
