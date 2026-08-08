// metrics.js — Faz 3.7: söylem/dil metrikleri (yıllara göre uzunluk ve kelime çeşitliliği)
window.App = window.App || {};
App.metrics = (function(){
  function trLower(s){ return s.replace(/İ/g,'i').replace(/I/g,'ı').toLocaleLowerCase('tr'); }
  function tokenize(text){ return trLower(text).replace(/[^\p{L}\s]/gu,' ').split(/\s+/).filter(w => w.length > 1); }

  async function compute(years){
    const perYear = {};
    for (const y of years){
      const data = await App.data.loadYearText(y);
      let totalWords = 0, totalSentences = 0, totalDocs = 0, vocab = new Set(), totalTokens = 0;
      Object.values(data).forEach(rec => {
        const text = rec.text || '';
        const sentences = text.split(/(?<=[.!?])\s+/).filter(s => s.trim().length > 3);
        const words = tokenize(text);
        totalWords += words.length;
        totalSentences += sentences.length;
        totalDocs += 1;
        totalTokens += words.length;
        words.forEach(w => vocab.add(w));
      });
      perYear[y] = {
        avgWordsPerHutbe: totalDocs ? totalWords/totalDocs : 0,
        avgWordsPerSentence: totalSentences ? totalWords/totalSentences : 0,
        ttr: totalTokens ? vocab.size/totalTokens : 0,
      };
    }
    return perYear;
  }

  async function render(canvasLenId, canvasTtrId, years){
    const perYear = await compute(years);
    App.charts.make(canvasLenId, {
      type:'line',
      data:{ labels: years, datasets:[
        { label:'Ort. kelime/hutbe', data: years.map(y=>Math.round(perYear[y].avgWordsPerHutbe)), borderColor:'#b8863a', backgroundColor:'transparent', tension:.3 },
        { label:'Ort. kelime/cümle', data: years.map(y=>+perYear[y].avgWordsPerSentence.toFixed(1)), borderColor:'#3f7d6b', backgroundColor:'transparent', tension:.3, yAxisID:'y1' },
      ]},
      options:{ responsive:true, maintainAspectRatio:false, plugins:{legend:{position:'bottom'}},
        scales:{ y:{beginAtZero:true, title:{display:true,text:'kelime/hutbe'}}, y1:{beginAtZero:true, position:'right', grid:{drawOnChartArea:false}, title:{display:true,text:'kelime/cümle'}} } }
    });
    App.charts.make(canvasTtrId, {
      type:'line',
      data:{ labels: years, datasets:[{ label:'Kelime çeşitliliği (type-token oranı)', data: years.map(y=>+perYear[y].ttr.toFixed(3)), borderColor:'#a8552f', backgroundColor:'#a8552f22', fill:true, tension:.3 }] },
      options:{ responsive:true, maintainAspectRatio:false, plugins:{legend:{display:false}}, scales:{ y:{beginAtZero:true} } }
    });
  }
  return { compute, render };
})();
