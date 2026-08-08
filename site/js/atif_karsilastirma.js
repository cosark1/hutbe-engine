// atif_karsilastirma.js — İP-7: Diyanet ile BAE ayet/hadis kullanım oranı karşılaştırması
window.App = window.App || {};

App.atifKarsilastirma = (function(){
  const SURE_ADLARI = {1:"Fatiha",2:"Bakara",3:"Al-i İmran",4:"Nisa",5:"Maide",6:"En'am",7:"A'raf",8:"Enfal",9:"Tevbe",10:"Yunus",11:"Hud",12:"Yusuf",13:"Ra'd",14:"İbrahim",15:"Hicr",16:"Nahl",17:"İsra",18:"Kehf",19:"Meryem",20:"Taha",21:"Enbiya",22:"Hac",23:"Mü'minun",24:"Nur",25:"Furkan",26:"Şuara",27:"Neml",28:"Kasas",29:"Ankebut",30:"Rum",31:"Lokman",32:"Secde",33:"Ahzab",34:"Sebe",35:"Fatır",36:"Yasin",37:"Saffat",38:"Sad",39:"Zümer",40:"Mü'min",41:"Fussilet",42:"Şura",43:"Zuhruf",44:"Duhan",45:"Casiye",46:"Ahkaf",47:"Muhammed",48:"Fetih",49:"Hucurat",50:"Kaf",51:"Zariyat",52:"Tur",53:"Necm",54:"Kamer",55:"Rahman",56:"Vakıa",57:"Hadid",58:"Mücadele",59:"Haşr",60:"Mümtehine",61:"Saff",62:"Cuma",63:"Münafikun",64:"Tegabun",65:"Talak",66:"Tahrim",67:"Mülk",68:"Kalem",69:"Hakka",70:"Mearic",71:"Nuh",72:"Cin",73:"Müzzemmil",74:"Müddessir",75:"Kıyamet",76:"İnsan",77:"Mürselat",78:"Nebe",79:"Naziat",80:"Abese",81:"Tekvir",82:"İnfitar",83:"Mutaffifin",84:"İnşikak",85:"Buruc",86:"Tarık",87:"Ala",88:"Gaşiye",89:"Fecr",90:"Beled",91:"Şems",92:"Leyl",93:"Duha",94:"İnşirah",95:"Tin",96:"Alak",97:"Kadir",98:"Beyyine",99:"Zilzal",100:"Adiyat",101:"Karia",102:"Tekasür",103:"Asr",104:"Hümeze",105:"Fil",106:"Kureyş",107:"Maun",108:"Kevser",109:"Kafirun",110:"Nasr",111:"Tebbet",112:"İhlas",113:"Felak",114:"Nas"};

  async function render(opts){
    const { statElId, noteElId, ayetTableElId, hadisTableElId } = opts;
    const data = await App.data.loadJSON('data/atif_karsilastirma_diyanet_bae.json');
    const d = data.diyanet, b = data.bae;

    const statEl = document.getElementById(statElId);
    statEl.innerHTML = `
      <div class="kpi-card">
        <div class="kpi-label">Ayet İçeren Hutbe</div>
        <div class="kpi-value" style="font-size:19px;">Diyanet %${d.ayet_yuzde} <span style="color:var(--ink-soft);font-size:13px;">·</span> <span style="color:var(--warm-2);">BAE %${b.ayet_yuzde}</span></div>
        <div class="kpi-sub">hutbe başına ortalama: Diyanet ${d.ayet_ortalama} · BAE ${b.ayet_ortalama} ayet</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Hadis İçeren Hutbe</div>
        <div class="kpi-value" style="font-size:19px;">Diyanet %${d.hadis_yuzde} <span style="color:var(--ink-soft);font-size:13px;">·</span> <span style="color:var(--warm-2);">BAE %${b.hadis_yuzde}</span></div>
        <div class="kpi-sub">hutbe başına ortalama: Diyanet ${d.hadis_ortalama} · BAE ${b.hadis_ortalama} hadis</div>
      </div>`;

    const noteEl = document.getElementById(noteElId);
    noteEl.innerHTML = `<b>Not:</b> BAE hutbeleri hutbe başına ${b.ayet_ortalama}/${d.ayet_ortalama} ≈ ${(b.ayet_ortalama/d.ayet_ortalama).toFixed(1)} kat daha fazla ayet, ${(b.hadis_ortalama/d.hadis_ortalama).toFixed(1)} kat daha fazla hadis alıntısı içeriyor — resmi İngilizce çeviride her alıntının köşeli parantezle ayrıca işaretlenmesi, Diyanet'in serbest-akan Türkçe metnine göre çok daha yoğun bir kaynak-gösterme editoryal üslubuna işaret ediyor (BAE ${b.toplam_hutbe} İngilizce çevirili hutbe üzerinden; Kur'an 4:59 — sabit kapanış formülü — sayıma dahil edilmedi). Diyanet'teki "count" alanının anlamı belirsiz olduğundan (hutbe-içi tekrar mı, kaynak numarası mı) karşılaştırma yalnızca benzersiz ayet/hadis-hutbe kayıt sayısına dayanıyor.`;

    const ayetEl = document.getElementById(ayetTableElId);
    let ayetHtml = '<table class="data-table" style="width:100%;"><thead><tr><th>Sûre:Ayet</th><th style="text-align:right;">Adet</th><th>Örnek (BAE)</th></tr></thead><tbody>';
    data.bae_en_cok_ayet.forEach(a => {
      const sureAd = SURE_ADLARI[a.sure_no] || a.sure_no;
      const ornek = a.ornekler[0];
      const ornekHtml = ornek ? `<span class="cmp-ex-item atif-bae-link" data-yil="${ornek.yil}" data-id="${ornek.id}" style="color:var(--accent);cursor:pointer;">${ornek.tarih} — ${App.util.esc(ornek.baslik)}</span>` : '—';
      ayetHtml += `<tr><td>${sureAd} ${a.sure_no}:${a.ayet_no}</td><td style="text-align:right;">${a.adet}</td><td>${ornekHtml}</td></tr>`;
    });
    ayetHtml += '</tbody></table>';
    ayetEl.innerHTML = ayetHtml;
    ayetEl.querySelectorAll('.atif-bae-link[data-id]').forEach(el => el.addEventListener('click', () => App.uaeReading.open(el.dataset.yil, el.dataset.id)));

    const hadisEl = document.getElementById(hadisTableElId);
    let hadisHtml = '<table class="data-table" style="width:100%;"><thead><tr><th>Kaynak</th><th style="text-align:right;">Diyanet</th><th style="text-align:right;">BAE</th></tr></thead><tbody>';
    data.hadis_kaynak_karsilastirma.slice(0, 12).forEach(k => {
      hadisHtml += `<tr><td>${App.util.esc(k.kaynak)}</td><td style="text-align:right;">${k.diyanet_sayi} <span style="color:var(--ink-soft);">(%${k.diyanet_yuzde})</span></td><td style="text-align:right;color:var(--warm-2);">${k.bae_sayi} <span style="color:var(--ink-soft);">(%${k.bae_yuzde})</span></td></tr>`;
    });
    hadisHtml += '</tbody></table>';
    hadisEl.innerHTML = hadisHtml;
  }
  return { render };
})();
