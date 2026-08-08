// tagcloud.js — anahtar kelime bulutu
window.App = window.App || {};
App.tagcloud = {
  render(elId, topKeywords, onClick){
    const top = topKeywords.slice(0, 60);
    if (!top.length) return;
    const maxC = top[0].count, minC = top[top.length-1].count;
    const wrap = document.getElementById(elId);
    wrap.innerHTML = top.map(k => {
      const scale = maxC === minC ? 1 : (k.count - minC) / (maxC - minC);
      const size = (12 + scale*22).toFixed(1);
      return `<span class="tag" style="font-size:${size}px" data-kw="${App.util.esc(k.keyword)}" title="${k.count} kez">${App.util.esc(k.keyword)}</span>`;
    }).join('');
    wrap.querySelectorAll('.tag').forEach(el => el.addEventListener('click', () => onClick(el.dataset.kw)));
  }
};
