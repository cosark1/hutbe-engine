// state.js — tek merkezli filtre durumu + URL hash senkronizasyonu
window.App = window.App || {};

App.state = (function(){
  const listeners = [];
  let s = { yearMin: null, yearMax: null, category: 'all', search: '' };

  function parseHash(){
    const h = location.hash.replace(/^#/, '');
    const params = new URLSearchParams(h);
    if (params.get('yil')) {
      const [a,b] = params.get('yil').split('-').map(Number);
      if (a) s.yearMin = a;
      if (b) s.yearMax = b;
    }
    if (params.get('kategori')) s.category = decodeURIComponent(params.get('kategori'));
    if (params.get('ara')) s.search = decodeURIComponent(params.get('ara'));
  }
  function writeHash(){
    const params = new URLSearchParams();
    if (s.yearMin && s.yearMax) params.set('yil', `${s.yearMin}-${s.yearMax}`);
    if (s.category && s.category !== 'all') params.set('kategori', s.category);
    if (s.search) params.set('ara', s.search);
    const str = params.toString();
    history.replaceState(null, '', str ? ('#' + str) : location.pathname);
  }
  function get(){ return s; }
  function set(patch){
    Object.assign(s, patch);
    writeHash();
    listeners.forEach(fn => fn(s));
  }
  function onChange(fn){ listeners.push(fn); }
  parseHash();
  return { get, set, onChange, parseHash };
})();
