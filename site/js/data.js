// data.js — fetch + önbellekleme + lazy load (yıl bazlı tam metinler)
window.App = window.App || {};

App.data = (function(){
  const cache = {};
  async function loadJSON(path){
    if (cache[path]) return cache[path];
    const res = await fetch(path);
    if (!res.ok) throw new Error('Yüklenemedi: ' + path);
    const json = await res.json();
    cache[path] = json;
    return json;
  }
  async function loadAll(){
    const [hutbeler, meta, ayetler, hadisler, sahabeler, kelimeler] = await Promise.all([
      loadJSON('data/hutbeler.json'),
      loadJSON('data/meta.json'),
      loadJSON('data/ayetler.json'),
      loadJSON('data/hadisler.json'),
      loadJSON('data/sahabeler.json'),
      loadJSON('data/kelimeler.json'),
    ]);
    return { hutbeler, meta, ayetler, hadisler, sahabeler, kelimeler };
  }
  async function loadYearText(year){
    return loadJSON(`data/metinler/${year}.json`);
  }
  async function getHutbeText(date){
    const year = date.split('.').pop();
    const yearData = await loadYearText(year);
    return yearData[date];
  }
  async function getTccbText(yil, id){
    const yearData = await loadJSON(`data/tccb_metinler/${yil}.json`);
    return yearData[id];
  }
  async function getUaeText(yil, id){
    const yearData = await loadJSON(`data/uae_metinler/${yil}.json`);
    return yearData[id];
  }
  return { loadJSON, loadAll, loadYearText, getHutbeText, getTccbText, getUaeText };
})();
