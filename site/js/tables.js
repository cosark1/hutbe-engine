// tables.js — tek fabrika: arama + sıralama + "daha fazla yükle" + CSV indirme
window.App = window.App || {};

App.util = App.util || {};
App.util.esc = function(s){ return (s||'').toString().replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); };
App.util.parseTrDate = function(d){ const [dd,mm,yy] = d.split('.'); return new Date(parseInt(yy), parseInt(mm)-1, parseInt(dd)); };
App.util.fmtNum = function(v){ return (v||0).toLocaleString('tr-TR'); };

// Türkçe küçük harfe çevirir ve şapkalı (circumflex) ünlüleri düzler:
// "zekât" ile "zekat" aynı arama sorgusuyla eşleşsin diye â/î/û → a/i/u
// (ç/ğ/ı/ö/ş/ü'ye DOKUNMAZ -- onlar ayrı harflerdir, şapka yalnızca uzun
// ünlü/incelme işaretidir ve yazımda sıkça atlanır).
// NFC normalize() ÖNCE yapılır: korpusun küçük bir kısmında (ör. 24.07.2020)
// harfler "önceden-birleşik" (â = U+00E2) değil "ayrışık" (a + ayrı bir
// BİRLEŞTİRİCİ ŞAPKA/CEDİLLA/UMLAUT işareti) olarak kayıtlı -- görsel olarak
// aynı görünür ama karakter dizisi farklı olduğundan aşağıdaki .replace()
// bunları yakalayamaz. normalize('NFC') ikisini de tek, öngörülebilir forma
// indirger (yalnızca â/î/û değil ç/ğ/ö/ş/ü için de aynı sorunu önler).
App.util.trLower = function(s){
  return (s||'').normalize('NFC').replace(/İ/g,'i').replace(/I/g,'ı').toLocaleLowerCase('tr')
    .replace(/â/g,'a').replace(/î/g,'i').replace(/û/g,'u');
};

// Kelime-sınırı farkında arama: "emek" araması "demektir" içindeki tesadüfi
// alt-dizeyle eşleşmesin (d+emek), ama Türkçe eklerle devam eden "kardeşlik",
// "kardeşlerim" gibi köke ekli biçimlere hâlâ eşleşsin (yalnızca kelime BAŞI
// sınırı aranır, sonu serbest bırakılır -- eklemeli dil yapısına uygun).
const TR_WORD_LOOKBEHIND = '(?<![a-zçğıöşüâîûA-ZÇĞİÖŞÜÂÎÛ0-9])';
App.util.wordBoundaryRegex = function(needleLower, flags){
  const esc = needleLower.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  return new RegExp(TR_WORD_LOOKBEHIND + '(' + esc + ')', flags || '');
};
App.util.wordMatch = function(haystackLower, needleLower){
  if (!needleLower) return true;
  return App.util.wordBoundaryRegex(needleLower).test(haystackLower);
};
App.util.wordMatchCount = function(haystackLower, needleLower){
  if (!needleLower) return 0;
  const re = App.util.wordBoundaryRegex(needleLower, 'g');
  return (haystackLower.match(re) || []).length;
};
// highlight() gibi ORİJİNAL (şapka düzleştirilmemiş) metne karşı eşleştirme
// gerektiğinde: sorgudaki düz a/i/u harflerini [aâ]/[iî]/[uû] karakter
// sınıflarına çevirir, böylece "zekat" sorgusu metindeki "zekât"ı da bulur.
App.util.wordBoundaryRegexRaw = function(needleLowerFolded, flags){
  const esc = needleLowerFolded.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const pat = esc.replace(/a/g,'[aâ]').replace(/i/g,'[iî]').replace(/u/g,'[uû]');
  return new RegExp(TR_WORD_LOOKBEHIND + '(' + pat + ')', flags || '');
};

App.util.toCSV = function(rows, columns){
  const esc = v => { v = (v===undefined||v===null) ? '' : String(v); if (/[",\n;]/.test(v)) return '"' + v.replace(/"/g,'""') + '"'; return v; };
  const header = columns.map(c => esc(c.label)).join(',');
  const lines = rows.map(r => columns.map(c => esc(typeof c.value === 'function' ? c.value(r) : r[c.value])).join(','));
  return header + '\n' + lines.join('\n');
};
App.util.downloadCSV = function(filename, rows, columns){
  const csv = App.util.toCSV(rows, columns);
  const blob = new Blob(['﻿' + csv], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = filename; a.click();
  URL.revokeObjectURL(url);
};

/**
 * createDataTable(opts)
 * opts: { root(HTMLElement), columns:[{field,label,sortable}], defaultSort, dateField,
 *         rowHtml(rows), getRows(), pageSize, onRowClick(date), csv:{filename, columns} }
 */
App.createDataTable = function(opts){
  let sortField = opts.defaultSort, sortDir = 'desc', visibleCount = opts.pageSize || 30;
  const root = opts.root;
  root.innerHTML = `
    <div class="table-toolbar">
      ${opts.searchPlaceholder ? `<input type="text" class="dt-search" placeholder="${opts.searchPlaceholder}">` : ''}
      ${opts.filterOptions ? `<select class="dt-filter"><option value="all">Tüm temalar</option>${opts.filterOptions.map(c=>`<option value="${App.util.esc(c)}">${App.util.esc(c)}</option>`).join('')}</select>` : ''}
      <span class="dt-count" style="font-size:12px;color:var(--ink-soft);"></span>
      ${opts.csv ? '<button class="csv-btn">CSV indir</button>' : ''}
    </div>
    <div class="table-scroll">
      <table class="data-table">
        <thead><tr>${opts.columns.map(c=>`<th data-field="${c.field}">${c.label}</th>`).join('')}</tr></thead>
        <tbody></tbody>
      </table>
    </div>
    <div class="load-more-row"><button class="load-more-btn">Daha fazla yükle</button></div>
  `;
  const tbody = root.querySelector('tbody');
  const countEl = root.querySelector('.dt-count');
  const loadMoreBtn = root.querySelector('.load-more-btn');
  const searchInput = root.querySelector('.dt-search');
  const filterSelect = root.querySelector('.dt-filter');

  function currentRows(){
    let rows = opts.getRows();
    if (searchInput && searchInput.value.trim()){
      const q = searchInput.value.trim().toLocaleLowerCase('tr');
      rows = rows.filter(r => opts.searchMatch(r, q));
    }
    if (filterSelect && filterSelect.value !== 'all'){
      rows = rows.filter(r => r.category === filterSelect.value);
    }
    return rows;
  }
  function render(){
    const rows = currentRows();
    const sorted = [...rows].sort((a,b) => {
      let av = a[sortField], bv = b[sortField];
      if (sortField === opts.dateField){ av = App.util.parseTrDate(av); bv = App.util.parseTrDate(bv); }
      const cmp = av < bv ? -1 : av > bv ? 1 : 0;
      return sortDir === 'asc' ? cmp : -cmp;
    });
    countEl.textContent = `${sorted.length} kayıt`;
    const visRows = sorted.slice(0, visibleCount);
    tbody.innerHTML = opts.rowHtml(visRows);
    loadMoreBtn.disabled = visibleCount >= sorted.length;
    loadMoreBtn.textContent = visibleCount >= sorted.length ? 'Tümü yüklendi' : 'Daha fazla yükle';
    if (opts.onRowClick){
      tbody.querySelectorAll('tr[data-date]').forEach(tr => {
        tr.addEventListener('click', (e) => {
          if (e.target.closest('.kw-link')) return;
          opts.onRowClick(tr.dataset.date);
        });
      });
    }
  }
  root.querySelectorAll('th[data-field]').forEach(th => {
    th.addEventListener('click', () => {
      const f = th.dataset.field;
      if (sortField === f) sortDir = sortDir === 'asc' ? 'desc' : 'asc';
      else { sortField = f; sortDir = 'desc'; }
      render();
    });
  });
  loadMoreBtn.addEventListener('click', () => { visibleCount += (opts.pageSize||30); render(); });
  if (searchInput) searchInput.addEventListener('input', () => { visibleCount = opts.pageSize||30; render(); });
  if (filterSelect) filterSelect.addEventListener('change', () => { visibleCount = opts.pageSize||30; render(); });
  if (opts.csv){
    root.querySelector('.csv-btn').addEventListener('click', () => {
      App.util.downloadCSV(opts.csv.filename, currentRows(), opts.csv.columns);
    });
  }
  render();
  return { render, refresh: render };
};
