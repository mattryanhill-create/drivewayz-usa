(function() {
'use strict';

// ===== STYLES =====
function injectStyles() {
  try {
    if (document.getElementById('sp-enhancements')) return;
    var s = document.createElement('style');
    s.id = 'sp-enhancements';
    s.textContent = [
      '.breadcrumb-nav{padding:0.75rem 2rem;background:#f8f9fa;border-bottom:1px solid #e5e7eb;margin-top:140px;}',
      '.breadcrumb-nav ol{list-style:none;display:flex;gap:0.5rem;max-width:1200px;margin:0 auto;padding:0;font-size:0.9rem;}',
      '.breadcrumb-nav li::after{content:"/";margin-left:0.5rem;color:#9ca3af;}',
      '.breadcrumb-nav li:last-child::after{display:none;}',
      '.breadcrumb-nav a{color:#5B9BD5;text-decoration:none;}',
      '.breadcrumb-nav a:hover{text-decoration:underline;}',
      '.breadcrumb-nav span{color:#666;}',
      '.state-hero{margin-top:0!important;}',
      '.trust-pills{display:flex;gap:0.75rem;justify-content:center;flex-wrap:wrap;margin-top:1.5rem;}',
      '.trust-pill{background:rgba(255,255,255,0.18);backdrop-filter:blur(8px);border:1px solid rgba(255,255,255,0.28);padding:0.4rem 1rem;border-radius:20px;font-size:0.85rem;color:white;display:flex;align-items:center;gap:0.4rem;}',
      '.content-with-sidebar{display:grid;grid-template-columns:1fr 320px;gap:2rem;max-width:1300px;margin:0 auto;padding:2rem;}',
      '.content-main{min-width:0;}',
      '.content-sidebar{position:relative;}',
      '.sidebar-inner{position:sticky;top:160px;display:flex;flex-direction:column;gap:1.5rem;}',
      '.section-nav-card{background:white;border-radius:16px;padding:1.25rem;box-shadow:0 4px 6px -1px rgba(0,0,0,0.08);border:1px solid #e5e7eb;}',
      '.section-nav-card h4{font-size:0.75rem;text-transform:uppercase;letter-spacing:0.1em;color:#6b7280;margin-bottom:0.75rem;padding-bottom:0.5rem;border-bottom:2px solid #5B9BD5;}',
      '.section-nav-card ul{list-style:none;padding:0;margin:0;}',
      '.section-nav-card li{margin-bottom:0.25rem;}',
      '.section-nav-card a{display:block;padding:0.4rem 0.75rem;color:#6b7280;text-decoration:none;font-size:0.85rem;border-left:3px solid transparent;border-radius:0 4px 4px 0;transition:all 0.2s;}',
      '.section-nav-card a:hover,.section-nav-card a.active{color:#2B5797;background:rgba(91,155,213,0.08);border-left-color:#5B9BD5;font-weight:500;}',
      '.quick-facts-card{background:white;border-radius:16px;padding:1.5rem;box-shadow:0 4px 6px -1px rgba(0,0,0,0.08);border:1px solid #e5e7eb;}',
      '.quick-facts-card h3{font-size:1rem;color:#2B5797;margin-bottom:1rem;display:flex;align-items:center;gap:0.5rem;}',
      '.fact-row{display:flex;justify-content:space-between;align-items:baseline;gap:1rem;padding:0.55rem 0;border-bottom:1px solid #f3f4f6;}',
      '.fact-row:last-child{border-bottom:none;}',
      '.fact-label{color:#6b7280;font-size:0.82rem;flex-shrink:0;min-width:90px;}',
      '.fact-value{color:#2B5797;font-weight:600;font-size:0.82rem;text-align:right;}',
      '.sidebar-form-card{background:linear-gradient(135deg,#5B9BD5,#2B5797);border-radius:16px;padding:1.5rem;color:white;}',
      '.sidebar-form-card h3{font-size:1rem;margin-bottom:0.4rem;}',
      '.sidebar-form-card p{font-size:0.82rem;opacity:0.9;margin-bottom:0.85rem;}',
      '.sidebar-form-card input{width:100%;padding:0.6rem 0.75rem;border:1px solid rgba(255,255,255,0.35);border-radius:8px;background:rgba(255,255,255,0.95);font-size:0.88rem;margin-bottom:0.5rem;box-sizing:border-box;color:#1f2937;}',
      '.sidebar-form-card button{width:100%;padding:0.65rem;background:white;color:#2B5797;border:none;border-radius:8px;font-weight:700;cursor:pointer;font-size:0.9rem;}',
      '.sidebar-form-card button:hover{background:#f0f7ff;}',
      '.section-img{width:100%;height:260px;object-fit:cover;border-radius:16px;margin:1.5rem 0;box-shadow:0 4px 15px rgba(0,0,0,0.1);}',
      '.mid-cta-banner{padding:3rem 2rem;background:linear-gradient(135deg,#5B9BD5,#2B5797);text-align:center;color:white;}',
      '.mid-cta-banner h3{font-size:1.6rem;margin-bottom:0.75rem;}',
      '.mid-cta-banner p{opacity:0.9;margin-bottom:1.25rem;max-width:500px;margin-left:auto;margin-right:auto;}',
      '.mid-cta-banner .btn-primary{background:white!important;color:#2B5797!important;}',
      '.mid-cta-banner .cta-phone{display:inline-flex;align-items:center;gap:0.5rem;color:white;text-decoration:none;font-weight:500;margin-left:1rem;}',
      '.testimonials-section{padding:4rem 2rem;background:#f8f9fa;}',
      '.testimonials-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:1.5rem;margin-top:2rem;}',
      '.testimonial-card{background:white;border-radius:16px;padding:2rem;box-shadow:0 4px 6px -1px rgba(0,0,0,0.08);border:1px solid #e5e7eb;position:relative;}',
      '.testimonial-stars{color:#f59e0b;margin-bottom:0.75rem;}',
      '.testimonial-text{color:#666;line-height:1.7;font-style:italic;margin-bottom:1rem;}',
      '.testimonial-author{display:flex;align-items:center;gap:0.75rem;}',
      '.testimonial-avatar{width:40px;height:40px;background:#5B9BD5;border-radius:50%;display:flex;align-items:center;justify-content:center;color:white;font-weight:700;font-size:0.9rem;flex-shrink:0;}',
      '.testimonial-name{font-weight:600;color:#1a1a1a;font-size:0.9rem;}',
      '.testimonial-loc{color:#6b7280;font-size:0.8rem;}',
      '.city-card.clickable{cursor:pointer;}',
      '@media(max-width:968px){.content-with-sidebar{grid-template-columns:1fr;}.content-sidebar{position:static;}.sidebar-inner{position:static;}.breadcrumb-nav{margin-top:90px;padding:0.5rem 1rem;}}'
    ].join('');
    document.head.appendChild(s);
  } catch(e) { console.error('SPE injectStyles:', e); }
}

// ===== BREADCRUMBS =====
function addBreadcrumbs(state) {
  try {
    if (document.querySelector('.breadcrumb-nav')) return;
    var hero = document.querySelector('.state-hero');
    if (!hero) return;
    var nav = document.createElement('nav');
    nav.className = 'breadcrumb-nav';
    nav.setAttribute('aria-label', 'Breadcrumb');
    nav.innerHTML = '<ol><li><a href="/">Home</a></li><li><a href="/locations/">Locations</a></li><li><span>' + state.name + '</span></li></ol>';
    hero.parentNode.insertBefore(nav, hero);
    var heroContent = hero.querySelector('.state-hero-content');
    if (heroContent) {
      var pills = document.createElement('div');
      pills.className = 'trust-pills';
      pills.innerHTML = '<span class="trust-pill">&#10003; Licensed &amp; Insured</span><span class="trust-pill">&#10003; Free Estimates</span><span class="trust-pill">&#10003; Satisfaction Guaranteed</span>';
      heroContent.appendChild(pills);
    }
  } catch(e) { console.error('SPE addBreadcrumbs:', e); }
}

// ===== SIDEBAR WRAPPER =====
function wrapContentWithSidebar(state) {
  try {
    if (document.querySelector('.content-with-sidebar')) return;
    var introSection = document.querySelector('.intro-section');
    var servicesSection = document.querySelector('.services-section');
    var typesSection = document.querySelector('.driveway-types-section');
    var whySection = document.querySelector('.why-section');
    if (!introSection) return;
    if (introSection.id !== 'intro') introSection.id = 'intro';
    if (servicesSection && servicesSection.id !== 'services') servicesSection.id = 'services';
    if (typesSection && typesSection.id !== 'types') typesSection.id = 'types';
    if (whySection && whySection.id !== 'why') whySection.id = 'why';
    var factsSection = document.querySelector('.local-facts-section');
    if (factsSection && factsSection.id !== 'facts') factsSection.id = 'facts';
    var areasSection = document.querySelector('.areas-section');
    if (areasSection && areasSection.id !== 'areas') areasSection.id = 'areas';
    var wrapper = document.createElement('div');
    wrapper.className = 'content-with-sidebar';
    var mainCol = document.createElement('div');
    mainCol.className = 'content-main';
    var sidebarCol = document.createElement('div');
    sidebarCol.className = 'content-sidebar';
    var sidebarInner = document.createElement('div');
    sidebarInner.className = 'sidebar-inner';
    // Section nav card
    var navCard = document.createElement('div');
    navCard.className = 'section-nav-card';
    navCard.innerHTML = '<h4>On This Page</h4><ul>' +
      '<li><a href="#intro">Overview</a></li>' +
      '<li><a href="#services">Services</a></li>' +
      '<li><a href="#types">Driveway Types</a></li>' +
      '<li><a href="#why">Why Choose Us</a></li>' +
      '<li><a href="#facts">Local Facts</a></li>' +
      '<li><a href="#areas">Service Areas</a></li>' +
      '</ul>';
    sidebarInner.appendChild(navCard);
    // Quick facts card
    var qfCard = document.createElement('div');
    qfCard.className = 'quick-facts-card';
    var topType = (state.drivewayTypes && state.drivewayTypes[0]) ? state.drivewayTypes[0].title : 'Concrete';
    var cityCount = (state.cities ? state.cities.length : 6) + '+';
    qfCard.innerHTML = '<h3>&#9999; Quick Facts</h3>' +
      '<div class="fact-row"><span class="fact-label">Climate</span><span class="fact-value">' + (state.climate || 'Varies') + '</span></div>' +
      '<div class="fact-row"><span class="fact-label">Top Service</span><span class="fact-value">' + (state.services[0] || '') + '</span></div>' +
      '<div class="fact-row"><span class="fact-label">Cities Served</span><span class="fact-value">' + cityCount + '</span></div>' +
      '<div class="fact-row"><span class="fact-label">Top Material</span><span class="fact-value">' + topType + '</span></div>';
    sidebarInner.appendChild(qfCard);
    // Lead form card
    var formCard = document.createElement('div');
    formCard.className = 'sidebar-form-card';
    formCard.innerHTML = '<h3>&#128197; Get Started Today</h3>' +
      '<p>Ready to transform your driveway? Get a free estimate.</p>' +
      '<input type="text" placeholder="Your Name" aria-label="Your Name">' +
      '<input type="tel" placeholder="Phone Number" aria-label="Phone Number">' +
      '<button onclick="window.location=\'/#contact\'">Request Free Estimate</button>';
    sidebarInner.appendChild(formCard);
    sidebarCol.appendChild(sidebarInner);
    var parent = introSection.parentNode;
    parent.insertBefore(wrapper, introSection);
    wrapper.appendChild(mainCol);
    wrapper.appendChild(sidebarCol);
    var sectionsToWrap = [introSection, servicesSection, typesSection, whySection].filter(Boolean);
    sectionsToWrap.forEach(function(s) { mainCol.appendChild(s); });
  } catch(e) { console.error('SPE wrapContentWithSidebar:', e); }
}

// ===== SECTION IMAGES =====
function addSectionImages() {
  try {
    if (document.querySelector('.section-img')) return;
    var stKey = window.location.hash ? window.location.hash.substring(1).toLowerCase() : '';
    var imgs = [
      {src:'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=900&q=80',alt:'Modern home with driveway',after:'.intro-section'},
      {src:'https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=900&q=80',alt:'Residential home exterior',after:'.services-section'},
      {src:'https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?w=900&q=80',alt:'Luxury home driveway',after:'.driveway-types-section'}
    ];
    if (stKey === 'california') {
      imgs = [
        {src:'https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=900&q=80',alt:'California home driveway',after:'.intro-section'},
        {src:'https://images.unsplash.com/photo-1564013799919-ab600027ffc6?w=900&q=80',alt:'Modern California home',after:'.services-section'},
        {src:'https://images.unsplash.com/photo-1449034446853-66c86144b0ad?w=900&q=80',alt:'California suburb',after:'.driveway-types-section'}
      ];
    } else if (stKey === 'florida') {
      imgs = [
        {src:'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=900&q=80',alt:'Florida home exterior',after:'.intro-section'},
        {src:'https://images.unsplash.com/photo-1570129477492-45c003edd2be?w=900&q=80',alt:'Florida tropical home',after:'.services-section'},
        {src:'https://images.unsplash.com/photo-1580587771525-78b9dba3b914?w=900&q=80',alt:'Florida driveway pavers',after:'.driveway-types-section'}
      ];
    }
    imgs.forEach(function(item) {
      var sec = document.querySelector(item.after);
      if (!sec) return;
      var el = document.createElement('img');
      el.className = 'section-img';
      el.src = item.src;
      el.alt = item.alt;
      el.loading = 'lazy';
      sec.parentNode.insertBefore(el, sec.nextSibling);
    });
  } catch(e) { console.error('SPE addSectionImages:', e); }
}

// ===== MID-PAGE CTA =====
function addMidPageCTA(state) {
  try {
    if (document.querySelector('.mid-cta-banner')) return;
    var whySection = document.querySelector('.why-section');
    if (!whySection) return;
    var cta = document.createElement('section');
    cta.className = 'mid-cta-banner';
    cta.innerHTML = '<h3>Get Your Free ' + state.name + ' Driveway Estimate</h3>' +
      '<p>No obligation. Expert advice tailored to your local climate and conditions.</p>' +
      '<a href="/#contact" class="btn-primary">Get Free Estimate</a>' +
      '<a href="tel:+18005551234" class="cta-phone">&#128222; Or Call Now</a>';
    whySection.parentNode.insertBefore(cta, whySection.nextSibling);
  } catch(e) { console.error('SPE addMidPageCTA:', e); }
}

// ===== TESTIMONIALS =====
function addTestimonials(state) {
  try {
    if (document.querySelector('.testimonials-section')) return;
    var insertBefore = document.querySelector('.local-facts-section') || document.querySelector('.areas-section');
    if (!insertBefore) return;
    var city1 = (state.cities && state.cities[0]) ? state.cities[0].name : state.name;
    var city2 = (state.cities && state.cities[1]) ? state.cities[1].name : state.name;
    var abbr = state.abbreviation || '';
    var section = document.createElement('section');
    section.className = 'testimonials-section';
    section.innerHTML = '<div class="container"><div class="section-header"><h2>What ' + state.name + ' Homeowners Say</h2><p>Trusted by homeowners across the state</p></div>' +
      '<div class="testimonials-grid">' +
      '<div class="testimonial-card"><div class="testimonial-stars">&#9733;&#9733;&#9733;&#9733;&#9733;</div>' +
      '<p class="testimonial-text">Outstanding work on our driveway. The team was professional, on time, and the result exceeded our expectations. Highly recommend for anyone in ' + state.name + '!</p>' +
      '<div class="testimonial-author"><div class="testimonial-avatar">JM</div><div><div class="testimonial-name">James M.</div><div class="testimonial-loc">' + city1 + ', ' + abbr + '</div></div></div></div>' +
      '<div class="testimonial-card"><div class="testimonial-stars">&#9733;&#9733;&#9733;&#9733;&#9733;</div>' +
      '<p class="testimonial-text">They really understood the local climate challenges and recommended the perfect material for our property. Great value and beautiful results.</p>' +
      '<div class="testimonial-author"><div class="testimonial-avatar">SR</div><div><div class="testimonial-name">Sarah R.</div><div class="testimonial-loc">' + city2 + ', ' + abbr + '</div></div></div></div>' +
      '</div></div>';
    insertBefore.parentNode.insertBefore(section, insertBefore);
  } catch(e) { console.error('SPE addTestimonials:', e); }
}

// ===== CITY CARD LINKS =====
function makeCityCardsClickable() {
  try {
    document.querySelectorAll('.city-card').forEach(function(card) {
      if (card.classList.contains('clickable')) return;
      card.classList.add('clickable');
      card.addEventListener('click', function() {
        window.location.href = '/#contact';
      });
    });
  } catch(e) { console.error('SPE makeCityCardsClickable:', e); }
}

// ===== FAQ SCHEMA =====
function addFAQSchema(state) {
  try {
    if (!state.localFacts || !state.localFacts.length) return;
    if (document.querySelector('script[type="application/ld+json"]')) return;
    var schema = {
      '@context': 'https://schema.org',
      '@type': 'FAQPage',
      'mainEntity': state.localFacts.map(function(fact) {
        return {
          '@type': 'Question',
          'name': fact.title,
          'acceptedAnswer': { '@type': 'Answer', 'text': fact.description }
        };
      })
    };
    var script = document.createElement('script');
    script.type = 'application/ld+json';
    script.textContent = JSON.stringify(schema);
    document.head.appendChild(script);
  } catch(e) { console.error('SPE addFAQSchema:', e); }
}

// ===== SCROLL SPY =====
function initScrollSpy() {
  try {
    var navLinks = document.querySelectorAll('.section-nav-card a');
    if (!navLinks.length) return;
    var sections = [];
    navLinks.forEach(function(link) {
      var id = link.getAttribute('href');
      if (id && id.charAt(0) === '#') {
        var el = document.getElementById(id.substring(1));
        if (el) sections.push({ el: el, link: link });
      }
    });
    if (!sections.length) return;
    var ticking = false;
    window.addEventListener('scroll', function() {
      if (!ticking) {
        window.requestAnimationFrame(function() {
          var scrollPos = window.scrollY + 200;
          var current = sections[0];
          sections.forEach(function(s) { if (s.el.offsetTop <= scrollPos) current = s; });
          navLinks.forEach(function(l) { l.classList.remove('active'); });
          if (current) current.link.classList.add('active');
          ticking = false;
        });
        ticking = true;
      }
    });
  } catch(e) { console.error('SPE initScrollSpy:', e); }
}

// ===== MAIN APPLY =====
function applyEnhancements() {
  try {
    var stateKey = window.location.hash ? window.location.hash.substring(1).toLowerCase() : null;
    if (!stateKey) return;
    if (typeof statesData === 'undefined' || !statesData[stateKey]) return;
    var state = statesData[stateKey];
    if (document.querySelector('.breadcrumb-nav')) return;
    injectStyles();
    addBreadcrumbs(state);
    wrapContentWithSidebar(state);
    addSectionImages();
    addMidPageCTA(state);
    addTestimonials(state);
    makeCityCardsClickable();
    addFAQSchema(state);
    initScrollSpy();
  } catch(e) { console.error('SPE applyEnhancements:', e); }
}

// ===== POLLING INIT =====
// Polls every 100ms until .state-hero exists (renderPage has run), then applies enhancements
function pollForRender() {
  var attempts = 0;
  var maxAttempts = 60; // 6 seconds max
  var interval = setInterval(function() {
    attempts++;
    try {
      if (document.querySelector('.state-hero') && !document.querySelector('.breadcrumb-nav')) {
        clearInterval(interval);
        applyEnhancements();
      } else if (document.querySelector('.breadcrumb-nav')) {
        clearInterval(interval); // already applied
      } else if (attempts >= maxAttempts) {
        clearInterval(interval);
        console.warn('SPE: gave up waiting for .state-hero after 6s');
      }
    } catch(e) {
      clearInterval(interval);
      console.error('SPE pollForRender:', e);
    }
  }, 100);
}

// ===== HASHCHANGE =====
window.addEventListener('hashchange', function() {
  try {
    var toRemove = ['.breadcrumb-nav', '.content-with-sidebar', '.mid-cta-banner', '.testimonials-section', '.section-img'];
    toRemove.forEach(function(sel) {
      document.querySelectorAll(sel).forEach(function(el) { el.remove(); });
    });
    var oldSchema = document.querySelector('script[type="application/ld+json"]');
    if (oldSchema) oldSchema.remove();
    setTimeout(pollForRender, 200);
  } catch(e) { console.error('SPE hashchange:', e); }
});

// ===== BOOT =====
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', pollForRender);
} else {
  pollForRender();
}

})();
