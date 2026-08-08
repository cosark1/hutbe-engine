// charts.js — Chart.js kurulum ve güncelleme + KPI sparkline
window.App = window.App || {};
App.charts = (function(){
  const BASE_COLORS = ["#b8863a","#3f7d6b","#c96a4a","#446b9e","#8f6a3e","#d4a24a","#557a8c","#a8552f","#375d6e","#7d8f5a","#9e5a6d","#5a7d8f","#8a6b9e","#6b8a5a","#a67d4a"];
  function palette(n){
    const c = BASE_COLORS.slice();
    for (let i = BASE_COLORS.length; i < n; i++){
      const hue = Math.round((i * 137.508) % 360);
      c.push(`hsl(${hue}, 50%, 45%)`);
    }
    return c;
  }
  let instances = {};
  function destroy(id){ if (instances[id]){ instances[id].destroy(); delete instances[id]; } }
  function make(id, config){ destroy(id); instances[id] = new Chart(document.getElementById(id).getContext('2d'), config); return instances[id]; }

  function renderYearly(id, yearly){
    const colors = palette(yearly.categories.length);
    make(id, { type:'bar', data:{ labels: yearly.years, datasets: yearly.categories.map((cat,i)=>({ label:cat, data: yearly.matrix.map(row=>row[i]), backgroundColor: colors[i] })) },
      options:{ responsive:true, maintainAspectRatio:false, plugins:{ legend:{position:'bottom', labels:{boxWidth:12,font:{size:10}}}}, scales:{ x:{stacked:true, grid:{display:false}}, y:{stacked:true, beginAtZero:true} } } });
  }
  function renderDoughnut(id, overall){
    const colors = palette(overall.labels.length);
    make(id, { type:'doughnut', data:{ labels: overall.labels, datasets:[{ data: overall.values, backgroundColor: colors, borderColor: 'var(--bg-card)', borderWidth:2 }] },
      options:{ responsive:true, maintainAspectRatio:false, cutout:'55%', plugins:{ legend:{position:'right', labels:{boxWidth:10,font:{size:10}}}, tooltip:{ callbacks:{ label:(ctx)=>{ const t = ctx.dataset.data.reduce((a,b)=>a+b,0); return `${ctx.label}: ${ctx.parsed} (%${(ctx.parsed/t*100).toFixed(1)})`; } } } } } });
  }
  function renderHBar(id, labels, values, color, tooltipFn){
    make(id, { type:'bar', data:{ labels, datasets:[{ data: values, backgroundColor: color, borderRadius:4 }] },
      options:{ indexAxis:'y', responsive:true, maintainAspectRatio:false, plugins:{ legend:{display:false}, tooltip: tooltipFn ? { callbacks:{ label: tooltipFn } } : {} }, scales:{ x:{beginAtZero:true}, y:{ticks:{font:{size:10.5}}} } } });
  }
  function sparkline(canvas, values, color){
    if (canvas._chart) canvas._chart.destroy();
    canvas._chart = new Chart(canvas.getContext('2d'), {
      type:'line', data:{ labels: values.map((_,i)=>i), datasets:[{ data: values, borderColor: color, backgroundColor:'transparent', borderWidth:2, pointRadius:0, tension:.35 }] },
      options:{ responsive:true, maintainAspectRatio:false, plugins:{legend:{display:false},tooltip:{enabled:false}}, scales:{ x:{display:false}, y:{display:false} } }
    });
  }
  return { palette, make, destroy, renderYearly, renderDoughnut, renderHBar, sparkline };
})();
