// ===========================================
// DRIVEWAYZ USA - SEO & ANALYTICS
// Canonical tags + GA4 for all pages
// ===========================================

(function() {
  'use strict';

  var DOMAIN = 'https://drivewayzusa.co';
  var GA_ID = 'G-V08M9YKRR7';

  // --- Canonical Tag ---
  // Only add if not already present
  if (!document.querySelector('link[rel="canonical"]')) {
    var canonical = document.createElement('link');
    canonical.rel = 'canonical';
    // Build canonical URL from current path
    var path = window.location.pathname;
    canonical.href = DOMAIN + path;
    document.head.appendChild(canonical);
  }

  // --- GA4 / gtag.js ---
  // Only add if gtag is not already loaded
  if (typeof window.gtag === 'undefined') {
    // Load gtag.js script
    var gtagScript = document.createElement('script');
    gtagScript.async = true;
    gtagScript.src = 'https://www.googletagmanager.com/gtag/js?id=' + GA_ID;
    document.head.appendChild(gtagScript);

    // Initialize gtag
    window.dataLayer = window.dataLayer || [];
    window.gtag = function() { window.dataLayer.push(arguments); };
    window.gtag('js', new Date());
    window.gtag('config', GA_ID);
  }
})();

// ===========================================
// NAV TOGGLE - Responsive hamburger menu
// ===========================================
document.addEventListener('DOMContentLoaded', function() {
  var header = document.querySelector('.site-header, .navbar');
  var toggle = document.querySelector('.nav-toggle, .hamburger');
  var nav = document.querySelector('.main-nav, .nav-links#main-nav-menu, .nav-links');
  var overlay = document.getElementById('nav-overlay');

  if (!header || !toggle) return;

  function toggleNav() {
    var isOpen = header.classList.toggle('nav-open');
    toggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
    if (nav) nav.classList.toggle('active', isOpen);
    toggle.classList.toggle('active', isOpen);
    if (overlay) {
      overlay.classList.toggle('active', isOpen);
    }
    document.body.style.overflow = isOpen ? 'hidden' : '';
  }

  toggle.addEventListener('click', function() {
    toggleNav();
  });

  if (overlay) {
    overlay.addEventListener('click', toggleNav);
  }

  if (nav) {
    nav.querySelectorAll('a').forEach(function(link) {
      link.addEventListener('click', function() {
        if (header.classList.contains('nav-open')) {
          toggleNav();
        }
      });
    });
  }
});
