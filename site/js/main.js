// main.js — bootstrap ve orkestrasyon
(async function(){
  const root = document.documentElement;
  const savedTheme = localStorage.getItem('hutbe-theme');
  if (savedTheme === 'dark') root.setAttribute('data-theme','dark');
  document.getElementById('theme-toggle').addEventListener('click', () => {
    const isDark = root.getAttribute('data-theme') === 'dark';
    if (isDark){ root.removeAttribute('data-theme'); localStorage.setItem('hutbe-theme','light'); document.getElementById('theme-toggle').textContent = '🌙 Karanlık mod'; }
    else { root.setAttribute('data-theme','dark'); localStorage.setItem('hutbe-theme','dark'); document.getElementById('theme-toggle').textContent = '☀️ Aydınlık mod'; }
  });
  if (savedTheme === 'dark') document.getElementById('theme-toggle').textContent = '☀️ Aydınlık mod';

  // section nav
  // BAE sekmesi kendi korpusunu gösterdiği için Diyanet'e özgü üst KPI satırı ve
  // yıl/tema filtre çubuğu o sekmede gizlenir (yoksa oradaki sayılar BAE verisine
  // aitmiş gibi okunuyor ve filtreler hiçbir şeyi etkilemediği hâlde etkin görünüyor).
  function showSection(target){
    document.querySelectorAll('.section-nav button').forEach(b => b.classList.toggle('active', b.dataset.target === target));
    ['reading-page','tccb-reading-page','uae-reading-page'].forEach(id => {
      const el = document.getElementById(id); if (el) el.style.display = 'none';
    });
    document.querySelectorAll('.section').forEach(s => s.style.display = (s.id === target ? 'block' : 'none'));
    const diyanetOnly = target !== 'sec-bae';
    document.getElementById('kpi-row').style.display = diyanetOnly ? '' : 'none';
    document.getElementById('filters-bar').style.display = diyanetOnly ? '' : 'none';
    document.getElementById('mobile-filter-toggle').style.display = diyanetOnly ? '' : 'none';
  }
  document.querySelectorAll('.section-nav button').forEach(btn => {
    btn.addEventListener('click', () => showSection(btn.dataset.target));
  });
  // Okuma sayfalarının "Panele dön" bağlantıları buradan geçer: eskiden TÜM
  // bölümleri birden gösteriyorlardı, artık kullanıcının bulunduğu sekmeye döner.
  App.nav = {
    show: showSection,
    showActive(){
      const btn = document.querySelector('.section-nav button.active');
      showSection(btn ? btn.dataset.target : 'sec-overview');
    },
  };
  document.getElementById('goto-bae-tab').addEventListener('click', () => {
    showSection('sec-bae');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });
  document.getElementById('mobile-filter-toggle').addEventListener('click', () => {
    document.getElementById('filters-bar').classList.toggle('open');
  });

  const data = await App.data.loadAll();
  const { hutbeler, meta, ayetler, hadisler, sahabeler, kelimeler } = data;

  App.kwModal.init(kelimeler);
  App.reading.init(hutbeler);
  App.compare.init(data);

  // ---- Filters ----
  const years = [...new Set(hutbeler.map(h=>h.year))].sort((a,b)=>a-b);
  const yMinSel = document.getElementById('f-year-min'), yMaxSel = document.getElementById('f-year-max'), catSel = document.getElementById('f-category');
  years.forEach(y => { yMinSel.appendChild(new Option(y,y)); yMaxSel.appendChild(new Option(y,y)); });
  yMinSel.value = years[0]; yMaxSel.value = years[years.length-1];
  meta.overall_category.labels.forEach(c => catSel.appendChild(new Option(c,c)));

  const st = App.state.get();
  if (st.yearMin) yMinSel.value = st.yearMin;
  if (st.yearMax) yMaxSel.value = st.yearMax;
  if (st.category) catSel.value = st.category;

  function filteredHutbeler(){
    const yMin = parseInt(yMinSel.value), yMax = parseInt(yMaxSel.value), cat = catSel.value;
    return hutbeler.filter(h => {
      if (h.year < yMin || h.year > yMax) return false;
      if (cat !== 'all' && h.primary_category !== cat && !(h.secondary_categories||[]).includes(cat)) return false;
      return true;
    });
  }

  function computeKPIs(rows){
    document.getElementById('kpi-total').textContent = App.util.fmtNum(rows.length);
    document.getElementById('kpi-total-sub').textContent = `Toplam ${meta.total_hutbe} kayıttan filtrelendi`;
    const counts = {}; rows.forEach(r => counts[r.primary_category] = (counts[r.primary_category]||0)+1);
    const top = Object.entries(counts).sort((a,b)=>b[1]-a[1])[0];
    document.getElementById('kpi-topcat').textContent = top ? top[0] : '-';
    document.getElementById('kpi-topcat-sub').textContent = top ? `${top[1]} hutbe` : '';
    document.getElementById('kpi-ayet').textContent = App.util.fmtNum(meta.total_ayet);
    document.getElementById('kpi-hadis').textContent = App.util.fmtNum(meta.total_hadis);
    document.getElementById('kpi-keywords').textContent = App.util.fmtNum(meta.total_keywords);
    document.getElementById('kpi-keywords-sub').textContent = `${App.util.fmtNum(meta.total_keyword_mentions)} toplam etiketleme`;
  }

  function applyFilters(){
    App.state.set({ yearMin: parseInt(yMinSel.value), yearMax: parseInt(yMaxSel.value), category: catSel.value });
    const rows = filteredHutbeler();
    computeKPIs(rows);
    App.charts.renderYearly('chart-yearly', meta.yearly);
    App.charts.renderDoughnut('chart-doughnut', meta.overall_category);
  }
  [yMinSel, yMaxSel, catSel].forEach(el => el.addEventListener('change', applyFilters));

  // ---- Heatmap ----
  App.heatmap.render(meta.weekly_grid, 'heatmap-months', 'heatmap', 'heatmap-legend', 'heatmap-tooltip');

  // ---- Static charts (suras/verses/hadis kaynak) ----
  App.charts.renderHBar('chart-suras', meta.top_suras.map(s=>s.name), meta.top_suras.map(s=>s.count), '#b8863acc');
  App.charts.renderHBar('chart-verses', meta.top_verses.map(v=>v.label), meta.top_verses.map(v=>v.count), '#c96a4acc',
    (ctx) => meta.top_verses[ctx.dataIndex].quote.slice(0,80)+'...');
  App.charts.renderHBar('chart-hadis-kaynak', meta.top_hadis_kaynak.map(s=>s.name), meta.top_hadis_kaynak.map(s=>s.count), '#3f7d6bcc');

  // ---- Ayet table ----
  App.createDataTable({
    root: document.getElementById('ayet-table-root'),
    columns: [ {field:'sure',label:'Sure'}, {field:'ayet',label:'Ayet'}, {field:'count',label:'Kaç Kez'}, {field:'quote',label:'Meal'}, {field:'category',label:'Tema'}, {field:'date',label:'Tarih'} ],
    defaultSort:'count', dateField:'date', pageSize:30, searchPlaceholder:'Sure adı veya metin ara...', filterOptions: meta.overall_category.labels,
    searchMatch: (r,q) => r.sure.toLocaleLowerCase('tr').includes(q) || r.quote.toLocaleLowerCase('tr').includes(q),
    getRows: () => ayetler,
    rowHtml: (rows) => rows.map(r => `<tr class="clickable" data-date="${r.date}"><td class="ref-cell" style="font-weight:600;">${App.util.esc(r.sure)}</td><td>${r.ayet}</td><td style="font-weight:700;text-align:center;">${r.count}</td><td class="quote-cell">"${App.util.esc(r.quote)}"</td><td><span class="badge">${App.util.esc(r.category)}</span></td><td>${r.date}</td></tr>`).join(''),
    onRowClick: (date) => App.reading.open(date),
    csv: { filename:'ayet_listesi.csv', columns:[ {label:'Sure',value:'sure'},{label:'Ayet',value:'ayet'},{label:'Kaç Kez',value:'count'},{label:'Meal',value:'quote'},{label:'Tema',value:'category'},{label:'Tarih',value:'date'} ] }
  });

  // ---- Hadis table ----
  App.createDataTable({
    root: document.getElementById('hadis-table-root'),
    columns: [ {field:'kaynak',label:'Kaynak'}, {field:'bolum',label:'Bölüm'}, {field:'count',label:'Kaç Kez'}, {field:'quote',label:'Metin'}, {field:'category',label:'Tema'}, {field:'date',label:'Tarih'} ],
    defaultSort:'count', dateField:'date', pageSize:30, searchPlaceholder:'Kaynak veya metin ara...', filterOptions: meta.overall_category.labels,
    searchMatch: (r,q) => r.kaynak.toLocaleLowerCase('tr').includes(q) || r.quote.toLocaleLowerCase('tr').includes(q),
    getRows: () => hadisler,
    rowHtml: (rows) => rows.map(r => `<tr class="clickable" data-date="${r.date}"><td class="ref-cell" style="font-weight:600;">${App.util.esc(r.kaynak)}</td><td>${App.util.esc(r.bolum)}</td><td style="font-weight:700;text-align:center;">${r.count}</td><td class="quote-cell">"${App.util.esc(r.quote)}"</td><td><span class="badge">${App.util.esc(r.category)}</span></td><td>${r.date}</td></tr>`).join(''),
    onRowClick: (date) => App.reading.open(date),
    csv: { filename:'hadis_listesi.csv', columns:[ {label:'Kaynak',value:'kaynak'},{label:'Bölüm',value:'bolum'},{label:'Kaç Kez',value:'count'},{label:'Metin',value:'quote'},{label:'Tema',value:'category'},{label:'Tarih',value:'date'} ] }
  });

  // ---- Sahabe table ----
  App.createDataTable({
    root: document.getElementById('sahabe-table-root'),
    columns: [ {field:'isim',label:'İsim'}, {field:'count',label:'Kaç Kez'}, {field:'category',label:'Tema'}, {field:'date',label:'Tarih'}, {field:'title',label:'Hutbe Başlığı'} ],
    defaultSort:'count', dateField:'date', pageSize:30, searchPlaceholder:'İsim ara...', filterOptions: meta.overall_category.labels,
    searchMatch: (r,q) => r.isim.toLocaleLowerCase('tr').includes(q),
    getRows: () => sahabeler,
    rowHtml: (rows) => rows.map(r => `<tr class="clickable" data-date="${r.date}"><td class="ref-cell" style="font-weight:600;">${App.util.esc(r.isim)}</td><td style="font-weight:700;text-align:center;">${r.count}</td><td><span class="badge">${App.util.esc(r.category)}</span></td><td>${r.date}</td><td>${App.util.esc(r.title)}</td></tr>`).join(''),
    onRowClick: (date) => App.reading.open(date),
    csv: { filename:'sahabe_listesi.csv', columns:[ {label:'İsim',value:'isim'},{label:'Kaç Kez',value:'count'},{label:'Tema',value:'category'},{label:'Tarih',value:'date'},{label:'Başlık',value:'title'} ] }
  });

  // ---- Keyword table ----
  App.createDataTable({
    root: document.getElementById('keyword-table-root'),
    columns: [ {field:'keyword',label:'Anahtar Kelime'}, {field:'count',label:'Kaç Kez'}, {field:'category',label:'Tema'}, {field:'date',label:'Tarih'}, {field:'title',label:'Hutbe Başlığı'} ],
    defaultSort:'count', dateField:'date', pageSize:30, searchPlaceholder:'Anahtar kelime ara...', filterOptions: meta.overall_category.labels,
    searchMatch: (r,q) => r.keyword.toLocaleLowerCase('tr').includes(q),
    getRows: () => kelimeler,
    rowHtml: (rows) => rows.map(r => `<tr data-date="${r.date}"><td class="ref-cell kw-link" data-kw="${App.util.esc(r.keyword)}" style="cursor:pointer;text-decoration:underline dotted;">${App.util.esc(r.keyword)}</td><td style="font-weight:700;text-align:center;">${r.count}</td><td><span class="badge">${App.util.esc(r.category)}</span></td><td>${r.date}</td><td>${App.util.esc(r.title)}</td></tr>`).join(''),
    onRowClick: (date) => App.reading.open(date),
    csv: { filename:'anahtar_kelimeler.csv', columns:[ {label:'Anahtar Kelime',value:'keyword'},{label:'Kaç Kez',value:'count'},{label:'Tema',value:'category'},{label:'Tarih',value:'date'},{label:'Başlık',value:'title'} ] }
  });
  document.getElementById('keyword-table-root').addEventListener('click', (e) => {
    const kwCell = e.target.closest('.kw-link');
    if (kwCell) App.kwModal.open(kwCell.dataset.kw);
  });
  document.getElementById('keyword-count-label').textContent = `${meta.total_keyword_mentions} kayıt · ${meta.total_keywords} benzersiz kelime`;

  // ---- Tag cloud ----
  App.tagcloud.render('tagcloud', meta.top_keywords, (kw) => App.kwModal.open(kw));

  // ---- Keyword × theme heatmap ----
  (function renderKwHeatmap(){
    const matrix = meta.keyword_category_matrix, cats = meta.overall_category.labels;
    let maxVal = 1;
    matrix.forEach(row => cats.forEach(c => { if ((row[c]||0) > maxVal) maxVal = row[c]; }));
    let html = '<thead><tr><th style="text-align:right;padding-right:10px;position:sticky;left:0;background:var(--bg-card);">Kelime</th>' + cats.map(c=>`<th style="font-size:9px;max-width:56px;padding:3px;">${App.util.esc(c)}</th>`).join('') + '</tr></thead><tbody>';
    matrix.forEach(row => {
      html += `<tr><th class="kw-link" data-kw="${App.util.esc(row.keyword)}" style="text-align:right;padding-right:10px;cursor:pointer;position:sticky;left:0;background:var(--bg-card);">${App.util.esc(row.keyword)}</th>`;
      cats.forEach(c => {
        const v = row[c] || 0;
        const bg = v === 0 ? 'var(--border)' : `rgba(184,134,58,${(0.15+0.85*(v/maxVal)).toFixed(2)})`;
        html += `<td style="padding:3px;"><div style="width:16px;height:16px;border-radius:3px;background:${bg};margin:0 auto;" title="${App.util.esc(row.keyword)} × ${App.util.esc(c)}: ${v}"></div></td>`;
      });
      html += '</tr>';
    });
    html += '</tbody>';
    const el = document.getElementById('kw-heatmap');
    el.innerHTML = html;
    el.querySelectorAll('.kw-link').forEach(th => th.addEventListener('click', () => App.kwModal.open(th.dataset.kw)));
  })();

  // ---- Trends (rising/falling keywords) ----
  App.trends.build(kelimeler, meta.year_min, meta.year_max);
  App.trends.renderLists('trend-rising', 'trend-falling');
  App.trends.initSelector('trend-select', 'trend-chart', ['aile','gençlik','israf','sabır','birlik ve beraberlik']);

  // ---- Sure map ----
  App.suramap.render('suramap', ayetler);

  // ---- Calendar ----
  await App.calendar.render('calendar-list', hutbeler);

  // ---- Bağlam zaman çizelgesi (İP-4) ----
  await App.timeline.render({
    gridElId: 'timeline-grid', monthsElId: 'timeline-months', legendElId: 'timeline-legend',
    selectElId: 'timeline-select', chartId: 'timeline-chart', sumElId: 'timeline-summary',
    hutbeler,
  });

  // ---- Hutbe-TCCB gecikme (lag) analizi (İP-6) ----
  await App.lagAnalizi.render({
    statElId: 'lag-stats', caveatElId: 'lag-caveat', tableElId: 'lag-olay-table',
  });

  // ---- BAE Karşılaştırma sekmesi (İP-7) ----
  App.karsilastirma.renderOzet({ statElId: 'bae-ozet-stats', bulgularElId: 'bae-bulgular' });
  App.karsilastirma.render({ listElId: 'cmp-kategori-list' });
  App.atifKarsilastirma.render({
    statElId: 'atif-stats', noteElId: 'atif-not',
    ayetTableElId: 'atif-ayet-table', hadisTableElId: 'atif-hadis-table',
  });
  App.sahabeKarsilastirma.render({ tableElId: 'sahabe-table', noteElId: 'sahabe-not' });
  App.uaeListe.render({ rootElId: 'bae-liste-root' });

  // ---- Karşılaştırmalı kelime arama (İP-7) ----
  const kaInput = document.getElementById('ka-input');
  function kaAra(q){
    App.karsilastirmaliArama.run(q, years, null, {
      diyanetElId: 'ka-diyanet-results', baeElId: 'ka-bae-results', statusElId: 'ka-status',
    });
  }
  let kaTimer = null;
  kaInput.addEventListener('input', (e) => {
    clearTimeout(kaTimer);
    const q = e.target.value;
    kaTimer = setTimeout(() => kaAra(q), 350);
  });
  document.querySelectorAll('.ka-preset[data-q]').forEach(btn => {
    btn.addEventListener('click', () => { kaInput.value = btn.dataset.q; kaAra(btn.dataset.q); });
  });

  // ---- Compare ----
  App.compare.render('compare-a','compare-b','compare-out-a','compare-out-b','compare-common');

  // ---- Discourse metrics ----
  App.metrics.render('chart-metrics-len', 'chart-metrics-ttr', years);

  // ---- Hutbe Ara (kart arşivi) ----
  App.archive.init(data);

  // ---- Initial render ----
  applyFilters();

  // ---- Hash routing on load ----
  if (location.hash.startsWith('#/oku/')) App.reading.renderCurrent();
  else if (location.hash.startsWith('#/tccb/')) App.tccbReading.renderCurrent();
  else if (location.hash.startsWith('#/uae/')) App.uaeReading.renderCurrent();
})();
