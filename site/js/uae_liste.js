// uae_liste.js — İP-7: BAE'nin 232 hutbesinin gezilebilir tam listesi.
// Diyanet tarafında kullanılan App.createDataTable bileşenini yeniden kullanır
// (arama + tema filtresi + sıralama + sayfalama + CSV indirme hazır gelir).
window.App = window.App || {};

App.uaeListe = (function(){
  async function render(opts){
    const { rootElId } = opts;
    const rows = await App.data.loadJSON('data/uae_hutbeler.json');
    const byId = {};
    rows.forEach(r => byId[r.id] = r);
    const kategoriler = [...new Set(rows.map(r => r.category))].sort((a, b) => a.localeCompare(b, 'tr'));

    App.createDataTable({
      root: document.getElementById(rootElId),
      columns: [
        { field: 'tarih', label: 'Tarih' },
        { field: 'baslik', label: 'Başlık (Arapça)' },
        { field: 'category', label: 'Ana Tema' },
        { field: 'cerceve', label: 'Çerçeve' },
        { field: 'ton', label: 'Ton' },
        { field: 'muhatap', label: 'Muhatap' },
        { field: 'eylem', label: 'Eylem Çağrısı' },
      ],
      defaultSort: 'tarih',
      // dateField VERİLMEDİ: BAE tarihleri ISO (yyyy-mm-dd) olduğu için düz metin
      // sıralaması zaten kronolojik doğru; parseTrDate (dd.mm.yyyy) uygulanmamalı.
      pageSize: 30,
      searchPlaceholder: 'Başlıkta ara (Arapça)…',
      filterOptions: kategoriler,
      searchMatch: (r, q) => (r.baslik || '').toLocaleLowerCase('tr').includes(q) || (r.category || '').toLocaleLowerCase('tr').includes(q),
      getRows: () => rows,
      rowHtml: (visRows) => visRows.map(r => `
        <tr data-date="${r.id}" class="clickable">
          <td style="white-space:nowrap;">${r.tarih}</td>
          <td dir="rtl" style="text-align:right;max-width:280px;">${App.util.esc(r.baslik)}${r.en_var ? '' : ' <span class="badge sec" title="Bu kayıtta resmi İngilizce çeviri yok, yalnızca Arapça metin var">yalnızca AR</span>'}</td>
          <td><span class="badge">${App.util.esc(r.category)}</span></td>
          <td style="color:var(--ink-soft);font-size:12px;">${App.util.esc(r.cerceve)}</td>
          <td style="color:var(--ink-soft);font-size:12px;">${App.util.esc(r.ton)}</td>
          <td style="color:var(--ink-soft);font-size:12px;">${App.util.esc(r.muhatap)}</td>
          <td style="color:var(--ink-soft);font-size:12px;">${App.util.esc(r.eylem)}</td>
        </tr>`).join(''),
      onRowClick: (id) => { const r = byId[id]; if (r) App.uaeReading.open(r.yil, r.id); },
      csv: {
        filename: 'bae_awqaf_hutbeler.csv',
        columns: [
          { label: 'tarih', value: 'tarih' }, { label: 'baslik', value: 'baslik' },
          { label: 'ana_kategori', value: 'category' }, { label: 'ikincil', value: 'ikincil' },
          { label: 'cerceve', value: 'cerceve' }, { label: 'ton', value: 'ton' },
          { label: 'muhatap', value: 'muhatap' }, { label: 'eylem_cagrisi', value: 'eylem' },
          { label: 'url', value: (r) => `https://www.awqaf.ae/friday-khutba-details/${r.id}` },
        ],
      },
    });
  }
  return { render };
})();
