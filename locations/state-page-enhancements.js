/**
 * State Page Quick Win Enhancements
 * Adds: breadcrumbs, sticky nav, quick facts sidebar, lead form,
 * styled icons, FAQ schema, city links, testimonials, mid-page CTA
 * 
 * Include AFTER the base state-page.html renders:
 * <script src="state-page-enhancements.js" defer><\/script>
 */

(function() {
  'use strict';

  // Wait for base page to render first
  const originalRender = window.renderPage || function(){};
  let enhancementsApplied = false;

  function applyEnhancements() {
    const stateKey = window.location.hash ? window.location.hash.substring(1).toLowerCase() : null;
    if (!stateKey || typeof statesData === 'undefined' || !statesData[stateKey]) return;
    const state = statesData[stateKey];

    // Prevent double-application
    if (document.querySelector('.breadcrumb-nav')) return;

    injectStyles();
    addBreadcrumbs(state);
    addStickyNav(state);
    wrapContentWithSidebar(state);
    upgradeServiceIcons();
    addMidPageCTA(state);
    addTestimonials(state);
    makeCityCardsClickable(state);
    addFAQSchema(state);
        addSectionImages(state);
        initScrollSpy();
  }

  // ===== 1. INJECT ENHANCEMENT STYLES =====
  function injectStyles() {
    if (document.getElementById('enhancement-styles')) return;
    const style = document.createElement('style');
    style.id = 'enhancement-styles';
    style.textContent = `
      /* Quick Win 1: Breadcrumbs */
      .breadcrumb-nav { padding: 0.75rem 2rem; background: var(--bg-light); border-bottom: 1px solid #e5e7eb; margin-top: 140px; }
      .breadcrumb-nav ol { list-style: none; display: flex; gap: 0.5rem; max-width: 1200px; margin: 0 auto; padding: 0; font-size: 0.9rem; }
      .breadcrumb-nav li::after { content: '/'; margin-left: 0.5rem; color: #9ca3af; }
      .breadcrumb-nav li:last-child::after { display: none; }
      .breadcrumb-nav a { color: var(--primary); text-decoration: none; }
      .breadcrumb-nav a:hover { text-decoration: underline; }
      .breadcrumb-nav span { color: var(--text-light); }
      .state-hero { margin-top: 0 !important; }

      /* Quick Win 2: Hero photo overlay */
      .state-hero { background-size: cover !important; background-position: center !important; position: relative; }
      .state-hero .hero-overlay { position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: linear-gradient(to bottom, rgba(43,87,151,0.85), rgba(91,155,213,0.75)); z-index: 2; }
      .state-hero .state-hero-content { position: relative; z-index: 3; }
      .trust-pills { display: flex; gap: 0.75rem; justify-content: center; flex-wrap: wrap; margin-top: 1.5rem; }
      .trust-pill { background: rgba(255,255,255,0.15); backdrop-filter: blur(8px); border: 1px solid rgba(255,255,255,0.25); padding: 0.4rem 1rem; border-radius: 20px; font-size: 0.85rem; color: white; display: flex; align-items: center; gap: 0.4rem; }

      /* Quick Win 3 & 4: Sidebar layout */
      .content-with-sidebar { display: grid; grid-template-columns: 1fr 320px; gap: 2rem; max-width: 1300px; margin: 0 auto; padding: 2rem; }
      .content-main { min-width: 0; }
      .content-sidebar { position: relative; }
      .sidebar-inner { position: sticky; top: 160px; display: flex; flex-direction: column; gap: 1.5rem; }
      .quick-facts-card { background: white; border-radius: 16px; padding: 1.5rem; box-shadow: var(--shadow); border: 1px solid #e5e7eb; }
      .quick-facts-card h3 { font-size: 1.1rem; color: var(--primary-dark); margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem; }
      .quick-facts-card .fact-row { display: flex; justify-content: space-between;align-items: baseline; gap: 0.5rem;  padding: 0.6rem 0; border-bottom: 1px solid #f3f4f6; }
      .quick-facts-card .fact-row:last-child { border-bottom: none; }
      .quick-facts-card .fact-label { color: var(--text-light); font-size: 0.9rem; flex-shrink: 0; white-space: nowrap; }
      .quick-facts-card .fact-value { color: var(--primary-dark); font-weight: 600; font-size: 0.9rem; text-align: right; }
      .sidebar-form { background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%); border-radius: 16px; padding: 1.5rem; color: white; }
      .sidebar-form h3 { font-size: 1.1rem; margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.5rem; }
      .sidebar-form p { font-size: 0.85rem; opacity: 0.9; margin-bottom: 1rem; }
      .sidebar-form input { width: 100%; padding: 0.65rem 0.75rem; border: 1px solid rgba(255,255,255,0.3); border-radius: 8px; background: rgba(255,255,255,0.95); font-size: 0.9rem; margin-bottom: 0.6rem; box-sizing: border-box; }
      .sidebar-form button { width: 100%; padding: 0.7rem; background: white; color: var(--primary-dark); border: none; border-radius: 8px; font-weight: 600; cursor: pointer; font-size: 0.95rem; transition: all 0.3s; }
      .sidebar-form button:hover { background: var(--bg-light); transform: translateY(-1px); }

      /* Quick Win 5: Sticky section nav */
      .section-nav { background: white; border-radius: 16px; padding: 1.25rem; box-shadow: var(--shadow); border: 1px solid #e5e7eb; }
      .section-nav h4 { font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.1em; color: var(--text-light); margin-bottom: 0.75rem; padding-bottom: 0.5rem; border-bottom: 2px solid var(--primary); }
      .section-nav ul { list-style: none; padding: 0; margin: 0; }
      .section-nav li { margin-bottom: 0.25rem; }
      .section-nav a { display: block; padding: 0.4rem 0.75rem; color: var(--text-light); text-decoration: none; font-size: 0.85rem; border-left: 3px solid transparent; border-radius: 0 4px 4px 0; transition: all 0.2s; }
      .section-nav a:hover, .section-nav a.active { color: var(--primary-dark); background: rgba(91,155,213,0.08); border-left-color: var(--primary); font-weight: 500; }

      /* Quick Win 6: Styled icons */
      .styled-icon { width: 56px; height: 56px; background: linear-gradient(135deg, var(--primary), var(--primary-dark)); border-radius: 14px; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; color: white; margin-bottom: 1rem; box-shadow: 0 4px 12px rgba(91,155,213,0.3); }

      /* Quick Win 9: Testimonials */
      .testimonials-section { padding: 4rem 2rem; background: var(--bg-light); }
      .testimonials-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1.5rem; margin-top: 2rem; }
      .testimonial-card { background: white; border-radius: 16px; padding: 2rem; box-shadow: var(--shadow); border: 1px solid #e5e7eb; position: relative; }
      .testimonial-card::before { content: '\\201C'; font-size: 4rem; color: var(--primary); opacity: 0.15; position: absolute; top: 0.5rem; left: 1rem; line-height: 1; font-family: Georgia, serif; }
      .testimonial-stars { color: #f59e0b; font-size: 1rem; margin-bottom: 0.75rem; }
      .testimonial-text { color: var(--text-light); line-height: 1.7; font-style: italic; margin-bottom: 1rem; }
      .testimonial-author { display: flex; align-items: center; gap: 0.75rem; }
      .testimonial-avatar { width: 40px; height: 40px; background: var(--primary); border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-weight: 600; font-size: 0.9rem; }
      .testimonial-name { font-weight: 600; color: var(--text-dark); font-size: 0.9rem; }
      .testimonial-location { color: var(--text-light); font-size: 0.8rem; }

      /* Quick Win 10: Mid-page CTA */
      .mid-cta-banner { padding: 3rem 2rem; background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%); text-align: center; color: white; }
      .mid-cta-banner h3 { font-size: 1.6rem; margin-bottom: 0.75rem; }
      .mid-cta-banner p { opacity: 0.9; margin-bottom: 1.25rem; max-width: 500px; margin-left: auto; margin-right: auto; }
      .mid-cta-banner .btn-primary { background: white; color: var(--primary-dark); }
      .mid-cta-banner .btn-primary:hover { background: var(--bg-light); }
      .mid-cta-banner .cta-phone { display: inline-flex; align-items: center; gap: 0.5rem; color: white; text-decoration: none; font-weight: 500; margin-left: 1rem; font-size: 1.05rem; }

      /* Quick Win 8: City card links */
      .city-card a { text-decoration: none; color: inherit; display: block; }
      .city-card.clickable { cursor: pointer; }
      .city-card.clickable:hover h4::after { content: ' \\2192'; }

      /* Responsive sidebar */
      @media (max-width: 968px) {
        .content-with-sidebar { grid-template-columns: 1fr; }
              /* Section images */
      .section-img { width: 100%; height: 220px; object-fit: cover; border-radius: 12px; margin: 1.5rem 0; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
        .content-sidebar { position: static; }
        .sidebar-inner { position: static; }
        .breadcrumb-nav { margin-top: 90px; padding: 0.5rem 1rem; }
        .trust-pills { gap: 0.5rem; }
        .trust-pill { font-size: 0.75rem; padding: 0.3rem 0.75rem; }
      }
    `;
    document.head.appendChild(style);
  }

  // ===== Quick Win 1: BREADCRUMBS =====
  function addBreadcrumbs(state) {
    const hero = document.querySelector('.state-hero');
    if (!hero) return;
    const nav = document.createElement('nav');
    nav.className = 'breadcrumb-nav';
    nav.setAttribute('aria-label', 'Breadcrumb');
    nav.innerHTML = `<ol><li><a href="../index.html">Home</a></li><li><a href="../locations.html">Locations</a></li><li><span>${state.name}</span></li></ol>`;
    hero.parentNode.insertBefore(nav, hero);

    // Quick Win 2: Add trust pills to hero
    const heroContent = hero.querySelector('.state-hero-content');
    if (heroContent) {
      const pills = document.createElement('div');
      pills.className = 'trust-pills';
      pills.innerHTML = '<span class="trust-pill">Licensed & Insured</span><span class="trust-pill">Free Estimates</span><span class="trust-pill">Satisfaction Guaranteed</span>';
      heroContent.appendChild(pills);
    }
  }

  // ===== Quick Win 5: STICKY SECTION NAV =====
  function addStickyNav(state) {
    // This will be placed inside the sidebar
  }

  // ===== Quick Wins 3,4,5: SIDEBAR =====
  function wrapContentWithSidebar(state) {
    // Find the intro section to start wrapping
    const introSection = document.querySelector('.intro-section');
    const servicesSection = document.querySelector('.services-section');
    const typesSection = document.querySelector('.driveway-types-section');
    const whySection = document.querySelector('.why-section');
    if (!introSection) return;

    // Create wrapper
    const wrapper = document.createElement('div');
    wrapper.className = 'content-with-sidebar';
    const mainCol = document.createElement('div');
    mainCol.className = 'content-main';
    const sidebarCol = document.createElement('div');
    sidebarCol.className = 'content-sidebar';
    const sidebarInner = document.createElement('div');
    sidebarInner.className = 'sidebar-inner';

    // Section nav
    sidebarInner.innerHTML = `
      <div class="section-nav">
        <h4>On This Page</h4>
        <ul>
          <li><a href="#intro">Overview</a></li>
          <li><a href="#services">Services</a></li>
          <li><a href="#types">Driveway Types</a></li>
          <li><a href="#why">Why Choose Us</a></li>
          <li><a href="#facts">Local Facts</a></li>
          <li><a href="#areas">Service Areas</a></li>
        </ul>
      </div>
      <div class="quick-facts-card">
        <h3>Quick Facts</h3>
        <div class="fact-row"><span class="fact-label">Climate</span><span class="fact-value">${state.climate || 'Varies'}</span></div>
        <div class="fact-row"><span class="fact-label">Top Service</span><span class="fact-value">${state.services[0] || ''}</span></div>
        <div class="fact-row"><span class="fact-label">Cities Served</span><span class="fact-value">${state.cities ? state.cities.length + '+' : '6+'}</span></div>
        <div class="fact-row"><span class="fact-label">Top Material</span><span class="fact-value">${state.drivewayTypes && state.drivewayTypes[0] ? state.drivewayTypes[0].title : 'Concrete'}</span></div>
      </div>
      <div class="sidebar-form">
        <h3>Get Started Today</h3>
        <p>Ready to transform your driveway? Get a free estimate from our experts.</p>
        <input type="text" placeholder="Your Name" aria-label="Your Name">
        <input type="tel" placeholder="Phone Number" aria-label="Phone Number">
        <button type="button" onclick="window.location.href='../index.html#contact'">Request Free Estimate</button>
      </div>
    `;
    sidebarCol.appendChild(sidebarInner);

    // Add IDs for scroll nav
    if (introSection) introSection.id = 'intro';
    if (servicesSection) servicesSection.id = 'services';
    if (typesSection) typesSection.id = 'types';
    if (whySection) whySection.id = 'why';
    const factsSection = document.querySelector('.local-facts-section');
    if (factsSection) factsSection.id = 'facts';
    const areasSection = document.querySelector('.areas-section');
    if (areasSection) areasSection.id = 'areas';

    // Move sections into main column
    const sectionsToWrap = [introSection, servicesSection, typesSection, whySection].filter(Boolean);
    const parent = introSection.parentNode;
    parent.insertBefore(wrapper, introSection);
    wrapper.appendChild(mainCol);
    wrapper.appendChild(sidebarCol);
    sectionsToWrap.forEach(s => {
      mainCol.appendChild(s);
      // Reset padding since now inside grid
      s.style.padding = '2rem 0';
    });
  }

  // ===== Quick Win 6: STYLED ICONS =====
  function upgradeServiceIcons() {
    document.querySelectorAll('.service-icon').forEach(icon => {
      icon.classList.add('styled-icon');
    });
  }

  // ===== Quick Win 10: MID-PAGE CTA =====
  function addMidPageCTA(state) {
    const whySection = document.querySelector('.why-section');
    if (!whySection) return;
    const cta = document.createElement('section');
    cta.className = 'mid-cta-banner';
    cta.innerHTML = `<h3>Get Your Free ${state.name} Driveway Estimate</h3><p>No obligation. Expert advice tailored to your local climate and conditions.</p><a href="../index.html#contact" class="btn-primary">Get Free Estimate</a><a href="tel:+18005551234" class="cta-phone">Or Call Now</a>`;
    whySection.parentNode.insertBefore(cta, whySection.nextSibling);
  }

  // ===== Quick Win 9: TESTIMONIALS =====
  function addTestimonials(state) {
    const factsSection = document.querySelector('.local-facts-section');
    const insertBefore = factsSection || document.querySelector('.areas-section');
    if (!insertBefore) return;
    const city1 = state.cities && state.cities[0] ? state.cities[0].name : state.name;
    const city2 = state.cities && state.cities[1] ? state.cities[1].name : state.name;
    const section = document.createElement('section');
    section.className = 'testimonials-section';
    section.innerHTML = `<div class="container"><div class="section-header"><h2>What ${state.name} Homeowners Say</h2><p>Trusted by homeowners across the state</p></div><div class="testimonials-grid"><div class="testimonial-card"><div class="testimonial-stars">&#9733;&#9733;&#9733;&#9733;&#9733;</div><div class="testimonial-text">Outstanding work on our driveway. The team was professional, on time, and the result exceeded our expectations. Highly recommend for anyone in ${state.name}!</div><div class="testimonial-author"><div class="testimonial-avatar">JM</div><div><div class="testimonial-name">James M.</div><div class="testimonial-location">${city1}, ${state.abbreviation}</div></div></div></div><div class="testimonial-card"><div class="testimonial-stars">&#9733;&#9733;&#9733;&#9733;&#9733;</div><div class="testimonial-text">They really understood the local climate challenges and recommended the perfect material for our property. Great value and beautiful results.</div><div class="testimonial-author"><div class="testimonial-avatar">SR</div><div><div class="testimonial-name">Sarah R.</div><div class="testimonial-location">${city2}, ${state.abbreviation}</div></div></div></div></div></div>`;
    insertBefore.parentNode.insertBefore(section, insertBefore);
  }

  // ===== Quick Win 8: CITY CARD LINKS =====
  function makeCityCardsClickable(state) {
    document.querySelectorAll('.city-card').forEach(card => {
      card.classList.add('clickable');
      card.style.cursor = 'pointer';
      card.addEventListener('click', function() {
        window.location.href = '../index.html#contact';
      });
    });
  }

  // ===== Quick Win 7: FAQ SCHEMA =====
  function addFAQSchema(state) {
    if (!state.localFacts || state.localFacts.length === 0) return;
    const faqSchema = {
      "@context": "https://schema.org",
      "@type": "FAQPage",
      "mainEntity": state.localFacts.map(fact => ({
        "@type": "Question",
        "name": fact.title,
        "acceptedAnswer": {
          "@type": "Answer",
          "text": fact.description
        }
      }))
    };
    const script = document.createElement('script');
    script.type = 'application/ld+json';
    script.textContent = JSON.stringify(faqSchema);
    document.head.appendChild(script);
  }

    // ===== SCROLL SPY FOR SIDEBAR NAV =====
  function initScrollSpy() {
    const navLinks = document.querySelectorAll('.section-nav a');
    if (!navLinks.length) return;
    const sections = [];
    navLinks.forEach(link => {
      const id = link.getAttribute('href');
      if (id && id.startsWith('#')) {
        const el = document.getElementById(id.substring(1));
        if (el) sections.push({ el: el, link: link });
      }
    });
    if (!sections.length) return;
    let ticking = false;
    window.addEventListener('scroll', () => {
      if (!ticking) {
        window.requestAnimationFrame(() => {
          const scrollPos = window.scrollY + 200;
          let current = sections[0];
          sections.forEach(s => {
            if (s.el.offsetTop <= scrollPos) current = s;
          });
          navLinks.forEach(l => l.classList.remove('active'));
          if (current) current.link.classList.add('active');
          ticking = false;
        });
        ticking = true;
      }
    });
  }

  // ===== INITIALIZATION =====
  // Override the original renderPage to add enhancements after render
  const checkAndApply = () => {
    setTimeout(() => {

        // ===== SECTION IMAGES =====
  function addSectionImages(state) {
    if (document.querySelector('.section-img')) return;
    var stKey = window.location.hash ? window.location.hash.substring(1).toLowerCase() : '';
    var imgMap = {
      california: [
        {src:'https://images.unsplash.com/photo-1449034446853-66c86144b0ad?w=800&q=80',alt:'California suburban neighborhood with driveways',after:'.intro-section'},
        {src:'https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=800&q=80',alt:'Modern California home with paved driveway',after:'.services-section'},
        {src:'https://images.unsplash.com/photo-1564013799919-ab600027ffc6?w=800&q=80',alt:'Beautiful California home exterior',after:'.driveway-types-section'}
      ]
    };
    var defImgs = [
      {src:'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=800&q=80',alt:'Modern home with driveway',after:'.intro-section'},
      {src:'https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=800&q=80',alt:'Residential home exterior',after:'.services-section'},
      {src:'https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?w=800&q=80',alt:'Luxury home with driveway',after:'.driveway-types-section'}
    ];
    var imgs = imgMap[stKey] || defImgs;
    imgs.forEach(function(item) {
      var sec = document.querySelector(item.after);
      if (!sec) return;
      var el = document.createElement('img');
      el.className = 'section-img';
      el.src = item.src;
      el.alt = item.alt;
      el.loading = 'lazy';
            el.style.cssText = 'width:100%;height:220px;object-fit:cover;border-radius:12px;margin:1.5rem 0;box-shadow:0 4px 12px rgba(0,0,0,0.1)';
      sec.parentNode.insertBefore(el, sec.nextSibling);
    });
  }
      if (document.querySelector('.state-hero') && !document.querySelector('.breadcrumb-nav')) {
              nhancements();
      }
    }, 100);
  };

  // Run after DOM content loaded and after hash changes
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', checkAndApply);
  } else {
    checkAndApply();
  }
  window.addEventListener('hashchange', () => {
    // Remove previous enhancements
    const oldBreadcrumb = document.querySelector('.breadcrumb-nav');
    if (oldBreadcrumb) oldBreadcrumb.remove();
    const oldWrapper = document.querySelector('.content-with-sidebar');
    if (oldWrapper) oldWrapper.remove();
    const oldMidCTA = document.querySelector('.mid-cta-banner');
    if (oldMidCTA) oldMidCTA.remove();
    const oldTestimonials = document.querySelector('.testimonials-section');
    if (oldTestimonials) oldTestimonials.remove();
    const oldSchema = document.querySelector('script[type="application/ld+json"]');
    if (oldSchema) oldSchema.remove();
    setTimeout(checkAndApply, 200);
  });

})();
