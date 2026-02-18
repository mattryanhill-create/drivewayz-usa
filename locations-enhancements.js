(function() {
'use strict';

// ===== STYLES =====
function injectStyles() {
  if (document.getElementById('loc-enhancements')) return;
  const s = document.createElement('style');
  s.id = 'loc-enhancements';
  s.textContent = `
    /* ---- Hero: compact ---- */
    .hero { padding: 3.5rem 2rem 3rem !important; min-height: 0 !important; }
    .hero h1 { font-size: clamp(1.8rem,4vw,2.8rem) !important; margin-bottom: 0.5rem !important; }
    .hero-subtitle { margin-bottom: 1.5rem !important; font-size: 1.05rem !important; }
    .loc-breadcrumb { font-size: 0.85rem; opacity: 0.8; margin-bottom: 0.75rem; }
    .loc-breadcrumb a { color: rgba(255,255,255,0.85); text-decoration: none; }
    .loc-breadcrumb a:hover { text-decoration: underline; }
    .loc-breadcrumb span { color: white; }
    .hero-search-wrap { max-width: 560px; margin: 0 auto 1.5rem; position: relative; }
    .hero-search-wrap input {
      width: 100%; padding: 0.9rem 1rem 0.9rem 3.2rem;
      border-radius: 50px; border: none; font-size: 1rem;
      box-shadow: 0 4px 20px rgba(0,0,0,0.2); outline: none;
      color: #1f2937;
    }
    .hero-search-wrap .search-icon {
      position: absolute; left: 1.1rem; top: 50%; transform: translateY(-50%);
      font-size: 1.1rem; pointer-events: none;
    }
    .hero-search-results {
      position: absolute; top: calc(100% + 6px); left: 0; right: 0;
      background: white; border-radius: 12px; box-shadow: 0 8px 30px rgba(0,0,0,0.15);
      max-height: 260px; overflow-y: auto; z-index: 100; display: none;
    }
    .hero-search-results.open { display: block; }
    .hero-search-results a {
      display: flex; align-items: center; gap: 0.75rem;
      padding: 0.65rem 1rem; text-decoration: none; color: #1f2937;
      font-size: 0.95rem; border-bottom: 1px solid #f3f4f6;
      transition: background 0.15s;
    }
    .hero-search-results a:last-child { border-bottom: none; }
    .hero-search-results a:hover { background: #f0f7ff; }
    .hero-search-results .res-abbr {
      background: #2B5797; color: white; border-radius: 6px;
      padding: 0.15rem 0.5rem; font-weight: 700; font-size: 0.8rem; min-width: 36px;
      text-align: center;
    }
    .loc-trust-bar {
      display: flex; gap: 1rem; justify-content: center;
      flex-wrap: wrap; margin-top: 1rem;
    }
    .loc-trust-pill {
      background: rgba(255,255,255,0.15); backdrop-filter: blur(8px);
      border: 1px solid rgba(255,255,255,0.3); border-radius: 20px;
      padding: 0.35rem 0.9rem; font-size: 0.8rem; color: white;
    }
    .stats-container { gap: 2.5rem !important; }
    .stat-number { font-size: 2.2rem !important; }
    .stat-label { font-size: 0.85rem !important; }

    /* ---- Hide old sections ---- */
    .map-section { display: none !important; }
    .regions-section { display: none !important; }
    .benefits-section { display: none !important; }

    /* ---- New layout wrapper ---- */
    .loc-page-body {
      display: grid;
      grid-template-columns: 1fr 300px;
      gap: 2rem;
      max-width: 1280px;
      margin: 0 auto;
      padding: 2.5rem 2rem;
    }
    .loc-main { min-width: 0; }
    .loc-sidebar { position: relative; }
    .loc-sidebar-inner {
      position: sticky; top: 160px;
      display: flex; flex-direction: column; gap: 1.25rem;
    }

    /* ---- Sidebar cards ---- */
    .sidebar-card {
      background: white; border-radius: 16px; padding: 1.25rem;
      box-shadow: 0 4px 6px -1px rgba(0,0,0,0.08);
      border: 1px solid #e5e7eb;
    }
    .sidebar-card h3 {
      font-size: 0.75rem; text-transform: uppercase;
      letter-spacing: 0.08em; color: #6b7280;
      margin-bottom: 0.75rem; padding-bottom: 0.5rem;
      border-bottom: 2px solid #5B9BD5;
    }
    .sidebar-popular a {
      display: flex; align-items: center; justify-content: space-between;
      padding: 0.4rem 0.5rem; border-radius: 8px;
      text-decoration: none; color: #1f2937;
      font-size: 0.9rem; transition: background 0.15s;
    }
    .sidebar-popular a:hover { background: #f0f7ff; color: #2B5797; }
    .sidebar-popular .pop-abbr {
      font-size: 0.75rem; font-weight: 700; color: #5B9BD5;
      background: #eff6ff; border-radius: 4px;
      padding: 0.1rem 0.4rem;
    }
    .sidebar-form-card {
      background: linear-gradient(135deg, #5B9BD5 0%, #2B5797 100%);
      border-radius: 16px; padding: 1.25rem; color: white;
    }
    .sidebar-form-card h3 {
      font-size: 1rem; margin-bottom: 0.4rem;
      border-bottom: 1px solid rgba(255,255,255,0.2);
      padding-bottom: 0.5rem; color: white; letter-spacing: 0;
      text-transform: none;
    }
    .sidebar-form-card p { font-size: 0.82rem; opacity: 0.9; margin-bottom: 0.85rem; }
    .sidebar-form-card input {
      width: 100%; padding: 0.6rem 0.75rem;
      border: 1px solid rgba(255,255,255,0.35);
      border-radius: 8px; background: rgba(255,255,255,0.95);
      font-size: 0.88rem; margin-bottom: 0.5rem; box-sizing: border-box;
      color: #1f2937;
    }
    .sidebar-form-card button {
      width: 100%; padding: 0.65rem;
      background: white; color: #2B5797;
      border: none; border-radius: 8px;
      font-weight: 700; cursor: pointer; font-size: 0.9rem;
      transition: all 0.2s;
    }
    .sidebar-form-card button:hover { background: #f0f7ff; transform: translateY(-1px); }

    /* ---- Region tabs + state grid ---- */
    .loc-region-header {
      display: flex; align-items: center; justify-content: space-between;
      flex-wrap: wrap; gap: 0.75rem; margin-bottom: 1.25rem;
    }
    .loc-region-tabs { display: flex; gap: 0.4rem; flex-wrap: wrap; }
    .loc-tab {
      padding: 0.45rem 1rem; border: 1.5px solid #5B9BD5;
      background: transparent; color: #5B9BD5;
      border-radius: 20px; cursor: pointer;
      font-weight: 600; font-size: 0.82rem; transition: all 0.2s;
    }
    .loc-tab:hover, .loc-tab.active {
      background: #5B9BD5; color: white;
    }
    .loc-result-count {
      font-size: 0.82rem; color: #6b7280;
    }

    /* ---- State grid: compact clickable pills ---- */
    .loc-states-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
      gap: 0.65rem;
    }
    .loc-state-pill {
      display: flex; align-items: center; gap: 0.5rem;
      padding: 0.6rem 0.85rem;
      background: white; border: 1.5px solid #e5e7eb;
      border-radius: 10px; text-decoration: none;
      color: #1f2937; font-size: 0.88rem;
      transition: all 0.18s; cursor: pointer;
      box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    }
    .loc-state-pill:hover {
      border-color: #5B9BD5; color: #2B5797;
      background: #f0f7ff;
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(91,155,213,0.2);
    }
    .loc-state-pill .pill-abbr {
      font-weight: 800; font-size: 0.8rem;
      color: #2B5797; min-width: 24px;
    }
    .loc-state-pill .pill-name {
      font-size: 0.83rem; color: #374151;
      white-space: nowrap; overflow: hidden;
      text-overflow: ellipsis;
    }
    .loc-state-pill.hidden { display: none; }

    /* ---- Region label headers ---- */
    .loc-region-label {
      grid-column: 1 / -1;
      font-size: 0.72rem; font-weight: 700;
      text-transform: uppercase; letter-spacing: 0.1em;
      color: #9ca3af; padding: 0.25rem 0;
      border-bottom: 1px solid #f3f4f6;
      margin-top: 0.5rem;
    }
    .loc-region-label:first-child { margin-top: 0; }

    /* ---- Territories strip ---- */
    .loc-territories {
      margin-top: 2rem; padding: 1.5rem;
      background: #f9fafb; border-radius: 14px;
      border: 1px solid #e5e7eb;
    }
    .loc-territories h3 {
      font-size: 0.85rem; font-weight: 700;
      color: #6b7280; text-transform: uppercase;
      letter-spacing: 0.07em; margin-bottom: 1rem;
    }
    .loc-territories-list {
      display: flex; flex-wrap: wrap; gap: 0.5rem;
    }
    .loc-territory-pill {
      display: inline-flex; align-items: center; gap: 0.4rem;
      padding: 0.4rem 0.85rem;
      background: white; border: 1.5px solid #d1d5db;
      border-radius: 20px; text-decoration: none;
      color: #374151; font-size: 0.82rem;
      transition: all 0.18s;
    }
    .loc-territory-pill:hover {
      border-color: #5B9BD5; color: #2B5797;
      background: #f0f7ff;
    }

    /* ---- Bottom CTA restyled ---- */
    .cta-section {
      padding: 4rem 2rem !important;
    }
    .cta-section h2 { font-size: 2rem !important; }

    /* ---- No results ---- */
    .loc-no-results {
      grid-column: 1/-1; text-align: center;
      padding: 2rem; color: #6b7280; font-size: 0.95rem;
    }

    /* ---- Responsive ---- */
    @media (max-width: 900px) {
      .loc-page-body { grid-template-columns: 1fr; }
      .loc-sidebar-inner { position: static; }
      .loc-sidebar { order: -1; }
      .sidebar-form-card { display: none; }
    }
    @media (max-width: 600px) {
      .loc-states-grid { grid-template-columns: repeat(auto-fill, minmax(120px, 1fr)); }
      .hero { padding: 2.5rem 1rem 2rem !important; }
    }
  `;
  document.head.appendChild(s);
}
