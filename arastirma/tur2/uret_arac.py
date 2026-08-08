# -*- coding: utf-8 -*-
"""
Tur 2 etiketleme aracını (tek dosyalık, sunucusuz HTML) üretir.
Girdi: tur2_veri.json (50 kör hutbe) + bu dosyada gömülü kod kitabı v1.2 kategori özetleri.
Çıktı: tur2_etiketleme_araci.html — çift tıklayıp tarayıcıda açılabilir, veri/kategoriler
gömülü, hiçbir sunucu/ağ bağlantısı gerektirmez. İlerleme tarayıcının localStorage'ında
otomatik kaydedilir; "CSV indir" tur1 ile aynı şemada (sira,ana_kategori,ikincil_kategoriler)
bir dosya üretir.
"""
import json
from pathlib import Path

kok = Path(__file__).resolve().parent

veri = json.loads((kok / "tur2_veri.json").read_text(encoding="utf-8"))

# kod_kitabi.md v1.2 §3.2'den kısaltılmış: (ad, kısa tanım, sınır notu)
KATEGORILER = [
    ("Toplumsal Dayanışma, Merhamet ve Kardeşlik",
     "Toplum geneline dönük ilişki ahlakı: kardeşlik, merhamet, yardımlaşma, komşuluk, birlik-beraberlik, barış dili.",
     "Aile ile: ilişki hane içiyse → Aile. Ahlak ile: somut alıcıya (yetim, mülteci, komşu...) yönelik yardım eylemleri listesi → burası; alıcısı belirtilmeden soyut erdem tanımı → Ahlak. Ekonomik Hayat ile: yardımlaşma zekât/infak eksenliyse → Ekonomik Hayat."),
    ("İbadet ve Kulluk",
     "Ritüel ibadetler (namaz, dua, hac, kurban) ve genel kulluk bilinci; cami-cemaat teşviki.",
     "Ramazan ile: oruç/teravih Ramazan-bayram bağlamındaysa → Ramazan. İman ile: kapanış çağrısı somut ibadet pratiğineyse → burası; inancın kendisine (iman/ahiret) dönükse → İman."),
    ("Aile, Çocuk ve Nesil",
     "Evlilik, eş ilişkisi, çocuk terbiyesi, kadın (aile bağlamında), nesil endişesi, mahremiyet-aile kesişimi.",
     "Eğitim/Teknoloji ile: tehdit aile-çocuk üzerinden işleniyorsa → burası; toplumsal düzeyde genel ise → Eğitim/Teknoloji."),
    ("İman, Tevhid ve Ahiret",
     "İnanç esasları: tevhid, ahiret, ölüm bilinci, dünya-ahiret dengesi, kalp temizliği (itikadi çerçevede).",
     "Sabır/Tevekkül ile (en sık karışan çift): neye inanılacağı (itikat) → burası; imtihan karşısında nasıl dayanılacağı (sabır/şükür) → Sabır/Tevekkül. Dünya-ahiret dengesi/dünyevileşme/Esma-i Hüsna temaları hep burası, sabır kelimesi geçse bile — test: gövde bir 'dert/zorluk hâli' mi (→Sabır), yoksa 'inanç dengesi' mi (→İman)?"),
    ("Ahlak, Erdem ve Söz",
     "Bireysel karakter ve dil ahlakı: doğruluk, edep, samimiyet, gıybet/yalan, öfke kontrolü.",
     "Toplumsal Dayanışma ile: bkz. o kategori."),
    ("Ramazan, Oruç ve Bayramlar",
     "Ramazan ayı, oruç, iki bayram, kurban (bayram bağlamında).",
     "Vesile önceliği kuralının en sık uygulandığı kategori: Ramazan'da başka temayı işleyen hutbe bile ana kategoride burası olur, işlenen tema ikincile düşer."),
    ("Vatan, Millet ve Tarih",
     "Şehitlik, milli günler (Çanakkale, 15 Temmuz), tarih ve millet söylemi.",
     "İslam Coğrafyası ile: Türkiye'nin milleti/tarihi/şehidi → burası; ülke dışı Müslüman toplumlar/mazlumlar → İslam Coğrafyası."),
    ("Sabır, Tevekkül ve Manevi Olgunluk",
     "İmtihan karşısında bireysel manevi hâl: sabır, şükür, tevekkül, zaman bilinci, istikamet.",
     "İman ile: bkz. o kategori. Afet ile: sabır somut bir felaket vesilesiyle işleniyorsa → Afet (somut olay önceliği)."),
    ("Ekonomik Hayat: Kazanç, Zekat ve İsraf",
     "Helal kazanç, ticaret ahlakı, zekât-infak, israf, borç, faiz.",
     ""),
    ("Kandiller, Muharrem ve Mübarek Geceler",
     "Kandiller, üç aylar (Ramazan hariç), Muharrem-Aşure-Kerbela, hicri yılbaşı.",
     "Peygamberimiz ile: Mevlid kandili hutbesi gövdede Peygamber'in hayatını işliyorsa → Peygamberimiz ana, kandil ikincil. Aksi hâlde → burası."),
    ("Peygamberimiz ve Ashab",
     "Hz. Peygamber'in hayatı, örnekliği, sünnet; sahabe ve hicret.",
     ""),
    ("İslam Coğrafyası ve Küresel Meseleler",
     "Ülke dışı Müslüman toplumlar, mazlumlar, Kudüs/Mescid-i Aksâ, küresel zulüm-adalet söylemi.",
     "Vatan ile: bkz. o kategori."),
    ("Eğitim, Teknoloji, Çevre ve Toplumsal Değişim",
     "İlim-eğitim teşviki, dijital dünya/bağımlılık, mahremiyet, çevre, toplumsal değişim eleştirisi.",
     "En heterojen kategori: eğitim / teknoloji / çevre alt temalarını birlikte barındırır."),
    ("Afet, Kriz ve Sağlık",
     "Somut afet/salgın/kaza vesileli hutbeler + sağlık, bağımlılıkla mücadele.",
     "Somut olay önceliği: felaket vesilesi varsa tema ne olursa olsun ana kategori burasıdır."),
    ("Kur'an-ı Kerim",
     "Kur'an'ın kendisinin konu olduğu hutbeler: okuma teşviki, Kur'an kursları, Kur'an-insan ilişkisi.",
     "Kur'an'dan yalnızca delil getirilmesi yeterli değildir (her hutbe yapar); Kur'an'ın konunun kendisi olması gerekir."),
]

GENEL_KURALLAR = [
    "Gövde belirler, başlık değil — karar hutbenin ana argümanına göre verilir.",
    "Bir ana kategori zorunlu, en fazla iki ikincil. İkincil ancak o tema en az iki paragrafı / ~%25'i kaplıyorsa atanır (tek paragraflık değini yetmez).",
    "Vesile önceliği: hutbe bir takvim vesilesine (bayram, kandil, üç aylar, milli gün) bağlıysa vesile kategorisi ana olur, işlenen tema ikincile düşer. (Kampanya/duyuru — Kutlu Doğum, kurs kayıtları vb. — vesile sayılmaz; 1-2 paragrafla sınırlıysa gövde teması belirler.)",
    "Somut olay önceliği: afet/salgın/saldırı/savaşa tepkiyse ilgili olay kategorisi (Afet-Kriz-Sağlık / İslam Coğrafyası / Vatan-Millet-Tarih) ana kategori olur.",
    "Kararsızsanız daha spesifik kategori kazanır (ör. Kur'an-ı Kerim > İbadet ve Kulluk).",
]

html = r"""<!doctype html>
<html lang="tr">
<head>
<meta charset="utf-8">
<title>İP-2 Tur 2 — İnsan Etiketleme Aracı</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
  :root {
    --bg: #faf7f0; --panel: #fff; --ink: #2a231c; --muted: #75695a;
    --accent: #8a5a2b; --accent-ink: #fff; --border: #e4dbc9;
    --chip: #f1ead9; --chip-on: #8a5a2b; --chip-on-ink: #fff;
    --danger: #a33;
  }
  @media (prefers-color-scheme: dark) {
    :root { --bg:#1b1712; --panel:#241f18; --ink:#ecdfc9; --muted:#a99a80;
      --accent:#c98a4b; --accent-ink:#1b1712; --border:#3a3123; --chip:#332a1d;
      --chip-on:#c98a4b; --chip-on-ink:#1b1712; --danger:#e07a7a; }
  }
  * { box-sizing: border-box; }
  body { margin:0; background:var(--bg); color:var(--ink); font-family: -apple-system,Segoe UI,Roboto,sans-serif; }
  header { padding:16px 20px; border-bottom:1px solid var(--border); background:var(--panel); position:sticky; top:0; z-index:5; }
  h1 { font-size:17px; margin:0 0 4px; }
  .sub { color:var(--muted); font-size:13px; }
  .kural-kutu { background:#fff3d6; color:#5a4210; border:1px solid #d9b96b; border-radius:8px; padding:10px 14px; margin-top:10px; font-size:13px; }
  @media (prefers-color-scheme: dark) { .kural-kutu { background:#3a2e12; color:#f0d99a; border-color:#6b5626; } }
  .wrap { max-width: 900px; margin: 0 auto; padding: 18px 20px 80px; }
  .strip { display:flex; flex-wrap:wrap; gap:4px; margin-bottom:16px; }
  .dot { width:16px; height:16px; border-radius:4px; background:var(--chip); border:1px solid var(--border); cursor:pointer; font-size:0; }
  .dot.done { background: #4f8a5b; border-color:#4f8a5b; }
  .dot.current { outline:2px solid var(--accent); outline-offset:1px; }
  .card { background:var(--panel); border:1px solid var(--border); border-radius:12px; padding:20px; margin-bottom:16px; }
  .meta { display:flex; justify-content:space-between; align-items:baseline; margin-bottom:10px; }
  .meta .tarih { color:var(--muted); font-size:13px; }
  .baslik { font-size:19px; font-weight:700; margin:2px 0 14px; }
  .metin { font-family: Georgia, 'Times New Roman', serif; font-size:16px; line-height:1.75; max-height:52vh; overflow-y:auto; padding-right:6px; }
  .metin p { margin:0 0 1em; }
  .metin .dipnot { font-size:13px; color:var(--muted); border-top:1px solid var(--border); padding-top:8px; margin-top:16px; }
  .sec-title { font-size:12px; text-transform:uppercase; letter-spacing:.04em; color:var(--muted); margin:18px 0 8px; }
  .chips { display:flex; flex-wrap:wrap; gap:8px; }
  .chip { background:var(--chip); border:1px solid var(--border); border-radius:20px; padding:7px 13px; font-size:13.5px; cursor:pointer; color:var(--ink); position:relative; }
  .chip.on { background:var(--chip-on); color:var(--chip-on-ink); border-color:var(--chip-on); }
  .chip.disabled { opacity:.35; cursor:not-allowed; }
  .chip .info { margin-left:6px; opacity:.6; }
  #global-tooltip { display:none; position:fixed; z-index:9999; width:280px; background:var(--panel); border:1px solid var(--border); border-radius:8px; padding:10px 12px; font-size:12.5px; line-height:1.5; color:var(--ink); box-shadow:0 8px 28px rgba(0,0,0,.35); text-align:left; pointer-events:none; }
  #global-tooltip b { display:block; margin-bottom:4px; }
  .nav { display:flex; gap:10px; margin-top:18px; align-items:center; flex-wrap:wrap; }
  button { font:inherit; border:none; border-radius:8px; padding:10px 16px; cursor:pointer; font-size:14px; }
  .btn-primary { background:var(--accent); color:var(--accent-ink); font-weight:600; }
  .btn-secondary { background:var(--chip); color:var(--ink); }
  .btn-secondary:disabled { opacity:.4; cursor:not-allowed; }
  .spacer { flex:1; }
  .progress { font-size:13px; color:var(--muted); }
  details.rehber { background:var(--panel); border:1px solid var(--border); border-radius:10px; padding:10px 14px; margin-bottom:16px; }
  details.rehber summary { cursor:pointer; font-weight:600; font-size:13.5px; }
  details.rehber ul { margin:10px 0 0; padding-left:18px; font-size:13px; line-height:1.6; color:var(--muted); }
  .foot { display:flex; gap:10px; margin-top:26px; border-top:1px solid var(--border); padding-top:16px; flex-wrap:wrap; align-items:center; }
  .warn { color:var(--danger); font-size:13px; }
</style>
</head>
<body>
<header>
  <h1>İP-2 Tur 2 — İnsan Etiketleme Aracı</h1>
  <div class="sub">50 hutbe · kod kitabı v1.2 · ilerleme bu tarayıcıda otomatik kaydedilir</div>
  <div class="kural-kutu">
    ⚠️ <b>Körlük kuralı:</b> Bu etiketleme geçerli sayılması için bağımsız olmalı. Bitirene kadar
    sitedeki hutbe sayfalarını, <code>guvenilirlik_orneklem_anahtar.csv</code>'yi veya bu hutbelerin
    orijinal kategorisini gösteren başka hiçbir dosyayı açmayın — yalnızca aşağıdaki metne ve
    kategori tanımlarına bakarak karar verin.
  </div>
</header>
<div class="wrap">
  <details class="rehber">
    <summary>Genel atama kuralları (kod kitabı §3.1) — açmak için tıklayın</summary>
    <ul id="genel-kurallar"></ul>
  </details>

  <div class="strip" id="strip"></div>

  <div class="card">
    <div class="meta">
      <div class="baslik-wrap"><span class="tarih" id="tarih"></span></div>
      <div class="progress" id="progress"></div>
    </div>
    <div class="baslik" id="baslik"></div>
    <div class="metin" id="metin"></div>

    <div class="sec-title">Ana kategori (tam olarak 1)</div>
    <div class="chips" id="ana-chips"></div>

    <div class="sec-title">İkincil kategoriler (0–2, isteğe bağlı)</div>
    <div class="chips" id="ikincil-chips"></div>
  </div>

  <div class="nav">
    <button class="btn-secondary" id="prev">← Önceki</button>
    <button class="btn-secondary" id="next">Sonraki →</button>
    <div class="spacer"></div>
    <button class="btn-secondary" id="reset">Bu hutbenin etiketini temizle</button>
  </div>

  <div class="foot">
    <button class="btn-primary" id="indir">CSV indir</button>
    <span class="warn" id="uyari"></span>
  </div>
</div>

<div id="global-tooltip"></div>

<script>
const DATA = __VERI__;
const KATEGORILER = __KATEGORILER__;
const GENEL_KURALLAR = __GENEL_KURALLAR__;

const LS_KEY = 'tur2_etiketler_v1';
const LS_IDX = 'tur2_index_v1';

let labels = JSON.parse(localStorage.getItem(LS_KEY) || '{}');
let idx = parseInt(localStorage.getItem(LS_IDX) || '0', 10);
if (isNaN(idx) || idx < 0 || idx >= DATA.length) idx = 0;

function save() {
  localStorage.setItem(LS_KEY, JSON.stringify(labels));
  localStorage.setItem(LS_IDX, String(idx));
}

function getLabel(sira) {
  return labels[sira] || { ana: null, ikincil: [] };
}

function renderGenelKurallar() {
  const ul = document.getElementById('genel-kurallar');
  ul.innerHTML = GENEL_KURALLAR.map(k => `<li>${k}</li>`).join('');
}

function renderStrip() {
  const strip = document.getElementById('strip');
  strip.innerHTML = '';
  DATA.forEach((h, i) => {
    const d = document.createElement('div');
    const done = !!getLabel(h.sira).ana;
    d.className = 'dot' + (done ? ' done' : '') + (i === idx ? ' current' : '');
    d.title = `#${i+1} — ${h.tarih} ${h.baslik}`;
    d.onclick = () => { idx = i; save(); render(); };
    strip.appendChild(d);
  });
}

function paragraflar(metin) {
  return metin.split(/\n\n+/).map(p => p.trim()).filter(Boolean)
    .map(p => `<p>${p.replace(/\n/g,' ')}</p>`).join('');
}

function esc(s) {
  return String(s).replace(/&/g,'&amp;').replace(/"/g,'&quot;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

function chipHtml(cat, secili, devreDisi) {
  return `<span class="chip${secili?' on':''}${devreDisi?' disabled':''}" data-cat="${esc(cat)}">${cat}<span class="info">ⓘ</span></span>`;
}

const gt = document.getElementById('global-tooltip');
function showTooltip(el) {
  const def = KATEGORILER.find(k => k.ad === el.dataset.cat);
  if (!def) return;
  gt.innerHTML = `<b>${esc(def.ad)}</b>${esc(def.tanim)}${def.sinir ? '<br><br><i>Sınır:</i> ' + esc(def.sinir) : ''}`;
  gt.style.left = '-9999px';
  gt.style.top = '-9999px';
  gt.style.display = 'block';
  const r = el.getBoundingClientRect();
  const gh = gt.offsetHeight, gw = gt.offsetWidth;
  let top = r.bottom + 8;
  if (top + gh > window.innerHeight - 8) top = r.top - gh - 8;
  if (top < 8) top = 8;
  let left = Math.min(r.left, window.innerWidth - gw - 8);
  if (left < 8) left = 8;
  gt.style.top = top + 'px';
  gt.style.left = left + 'px';
}
function hideTooltip() { gt.style.display = 'none'; }

function render() {
  const h = DATA[idx];
  const lab = getLabel(h.sira);
  document.getElementById('tarih').textContent = h.tarih;
  document.getElementById('baslik').textContent = h.baslik;
  document.getElementById('metin').innerHTML = paragraflar(h.metin);
  document.getElementById('metin').scrollTop = 0;
  document.getElementById('progress').textContent = `#${idx+1} / ${DATA.length}`;

  const anaWrap = document.getElementById('ana-chips');
  anaWrap.innerHTML = KATEGORILER.map(k => chipHtml(k.ad, lab.ana === k.ad, false)).join('');
  anaWrap.querySelectorAll('.chip').forEach(el => {
    el.addEventListener('mouseenter', () => showTooltip(el));
    el.addEventListener('mouseleave', hideTooltip);
    el.addEventListener('click', () => {
      hideTooltip();
      const cat = el.dataset.cat;
      lab.ana = (lab.ana === cat) ? null : cat;
      lab.ikincil = lab.ikincil.filter(c => c !== lab.ana);
      labels[h.sira] = lab;
      save(); render();
    });
  });

  const ikWrap = document.getElementById('ikincil-chips');
  ikWrap.innerHTML = KATEGORILER
    .filter(k => k.ad !== lab.ana)
    .map(k => chipHtml(k.ad, lab.ikincil.includes(k.ad), !lab.ikincil.includes(k.ad) && lab.ikincil.length >= 2))
    .join('');
  ikWrap.querySelectorAll('.chip').forEach(el => {
    el.addEventListener('mouseenter', () => showTooltip(el));
    el.addEventListener('mouseleave', hideTooltip);
    el.addEventListener('click', () => {
      hideTooltip();
      if (el.classList.contains('disabled')) return;
      const cat = el.dataset.cat;
      if (lab.ikincil.includes(cat)) lab.ikincil = lab.ikincil.filter(c => c !== cat);
      else if (lab.ikincil.length < 2) lab.ikincil.push(cat);
      labels[h.sira] = lab;
      save(); render();
    });
  });

  document.getElementById('prev').disabled = idx === 0;
  document.getElementById('next').disabled = idx === DATA.length - 1;
  renderStrip();
}

document.getElementById('prev').onclick = () => { if (idx>0){ idx--; save(); render(); } };
document.getElementById('next').onclick = () => { if (idx<DATA.length-1){ idx++; save(); render(); } };
document.getElementById('reset').onclick = () => {
  const h = DATA[idx];
  if (confirm('Bu hutbenin etiketini temizlemek istediğinize emin misiniz?')) {
    delete labels[h.sira]; save(); render();
  }
};

document.getElementById('indir').onclick = () => {
  const eksik = DATA.filter(h => !getLabel(h.sira).ana).length;
  const uyari = document.getElementById('uyari');
  uyari.textContent = eksik > 0 ? `Uyarı: ${eksik} hutbe hâlâ etiketlenmedi — CSV yine de indirilecek (eksikler boş bırakılacak).` : '';
  const rows = ['sira,ana_kategori,ikincil_kategoriler'];
  DATA.forEach(h => {
    const lab = getLabel(h.sira);
    const ana = lab.ana || '';
    const ik = (lab.ikincil || []).join('; ');
    rows.push(`"${h.sira}","${ana.replace(/"/g,'""')}","${ik.replace(/"/g,'""')}"`);
  });
  const blob = new Blob([rows.join('\n')], {type:'text/csv;charset=utf-8'});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'tur2_etiketler.csv';
  a.click();
};

renderGenelKurallar();
render();
</script>
</body>
</html>
"""

kategoriler_js = json.dumps(
    [{"ad": ad, "tanim": tanim, "sinir": sinir} for ad, tanim, sinir in KATEGORILER],
    ensure_ascii=False)
genel_js = json.dumps(GENEL_KURALLAR, ensure_ascii=False)
veri_js = json.dumps(veri, ensure_ascii=False)

html = html.replace("__VERI__", veri_js).replace("__KATEGORILER__", kategoriler_js).replace("__GENEL_KURALLAR__", genel_js)

(kok / "tur2_etiketleme_araci.html").write_text(html, encoding="utf-8")
print("Yazildi:", kok / "tur2_etiketleme_araci.html")
print("Boyut:", (kok / "tur2_etiketleme_araci.html").stat().st_size, "byte")
