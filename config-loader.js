/* config-loader.js - Fetch and apply site config from site-config.json */
const CACHE_KEY = 'site_config';
let _config = null;

async function getSiteConfig() {
  if (_config) return _config;
  const cached = sessionStorage.getItem(CACHE_KEY);
  if (cached) {
    _config = JSON.parse(cached);
    return _config;
  }
  const res = await fetch('/site-config.json');
  const data = await res.json();
  sessionStorage.setItem(CACHE_KEY, JSON.stringify(data));
  _config = data;
  return data;
}

async function renderConfig() {
  const cfg = await getSiteConfig();
  window.__siteConfig = cfg;
  document.querySelectorAll('[data-config]').forEach(el => {
    const field = el.getAttribute('data-config');
    const val = field.split('.').reduce((o, k) => (o && o[k] !== undefined ? o[k] : undefined), cfg);
    if (val != null && typeof val === 'string') el.textContent = val;
  });
}

window.getSiteConfig = getSiteConfig;
window.renderConfig = renderConfig;
document.addEventListener('DOMContentLoaded', () => renderConfig());
