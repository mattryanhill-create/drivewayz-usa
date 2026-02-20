/**
 * Guides Hub Page Enhancements
 * Applies Kimi UX mockup design to guides-hub.html
 * Adds: breadcrumb, search bar, category filters, popular guides section, improved layout
 */

document.addEventListener('DOMContentLoaded', function() {
  // Inject enhanced CSS
  injectCSS();
  // Build breadcrumb in hero
  buildBreadcrumb();
  // Enhance hero subtitle
  enhanceHeroSubtitle();
  // Build search bar
  buildSearchBar();
  // Build category filter pills
  buildCategoryFilters();
  // Create Popular Guides section
  buildPopularGuides();
  // Rename and restructure All Guides section
  restructureAllGuides();
  // Enhance footer
  enhanceFooter();
});

function injectCSS() {
  var style = document.createElement('style');
  style.textContent = `
    /* Breadcrumb in hero */
    .guides-breadcrumb {
      color: rgba(255,255,255,0.85);
      font-size: 0.95rem;
      margin-bottom: 1rem;
    }
    .guides-breadcrumb a {
      color: rgba(255,255,255,0.85);
      text-decoration: none;
    }
    .guides-breadcrumb a:hover {
      color: #fff;
      text-decoration: underline;
    }
    .guides-breadcrumb .separator {
      margin: 0 0.5rem;
    }

    /* Search bar area */
    .guides-search-wrapper {
      max-width: 800px;
      margin: -30px auto 0;
      position: relative;
      z-index: 10;
      padding: 0 1rem;
    }
    .guides-search-inner {
      display: flex;
      background: #fff;
      border-radius: 12px;
      box-shadow: 0 4px 20px rgba(0,0,0,0.12);
      overflow: hidden;
    }
    .guides-search-inner input {
      flex: 1;
      border: none;
      padding: 1rem 1.5rem;
      font-size: 1rem;
      outline: none;
      color: #333;
    }
    .guides-search-inner input::placeholder {
      color: #999;
    }
    .guides-search-inner button {
      background: var(--primary-color, #4A90D9);
      color: #fff;
      border: none;
      padding: 1rem 2rem;
      font-size: 1rem;
      font-weight: 600;
      cursor: pointer;
      transition: background 0.3s;
    }
    .guides-search-inner button:hover {
      background: var(--primary-dark, #3570B0);
    }

    /* Category filter pills */
    .guides-filter-wrapper {
      text-align: center;
      padding: 2rem 1rem 1rem;
      max-width: 900px;
      margin: 0 auto;
    }
    .guides-filter-label {
      display: block;
      color: #666;
      margin-bottom: 0.75rem;
      font-size: 0.95rem;
    }
    .guides-filter-pills {
      display: flex;
      flex-wrap: wrap;
      justify-content: center;
      gap: 0.5rem;
    }
    .filter-pill {
      padding: 0.5rem 1.2rem;
      border-radius: 25px;
      border: 1.5px solid #ddd;
      background: #fff;
      color: #444;
      font-size: 0.9rem;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.25s;
    }
    .filter-pill:hover {
      border-color: var(--primary-color, #4A90D9);
      color: var(--primary-color, #4A90D9);
    }
    .filter-pill.active {
      background: var(--primary-color, #4A90D9);
      color: #fff;
      border-color: var(--primary-color, #4A90D9);
    }

    /* Popular Guides section */
    .popular-guides-section {
      padding: 3rem 0 2rem;
      background: var(--bg-light, #f8f9fa);
    }
    .popular-guides-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      max-width: 1200px;
      margin: 0 auto 1.5rem;
      padding: 0 2rem;
    }
    .popular-guides-header h2 {
      font-size: 1.8rem;
      font-weight: 700;
      color: var(--text-dark, #1a1a2e);
      margin: 0;
    }
    .popular-guides-header a {
      color: var(--primary-color, #4A90D9);
      text-decoration: none;
      font-weight: 600;
      font-size: 0.95rem;
    }
    .popular-guides-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
      gap: 1.5rem;
      max-width: 1200px;
      margin: 0 auto;
      padding: 0 2rem;
    }
    .popular-card {
      background: #fff;
      border-radius: 12px;
      overflow: hidden;
      box-shadow: 0 2px 12px rgba(0,0,0,0.08);
      transition: all 0.3s;
      text-decoration: none;
      color: inherit;
      display: block;
    }
    .popular-card:hover {
      transform: translateY(-6px);
      box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    .popular-card-image {
      height: 180px;
      background-size: cover;
      background-position: center;
      position: relative;
    }
    .popular-card-badge {
      position: absolute;
      top: 0.75rem;
      left: 0.75rem;
      padding: 0.35rem 0.75rem;
      border-radius: 20px;
      font-size: 0.7rem;
      font-weight: 700;
      text-transform: uppercase;
      color: #fff;
      letter-spacing: 0.5px;
    }
    .popular-card-content {
      padding: 1.25rem;
    }
    .popular-card-content h3 {
      font-size: 1.15rem;
      margin: 0 0 0.6rem;
      color: var(--text-dark, #1a1a2e);
    }
    .popular-card-content p {
      color: #666;
      font-size: 0.9rem;
      line-height: 1.5;
      margin: 0 0 0.75rem;
    }
    .popular-card-meta {
      display: flex;
      gap: 1rem;
      font-size: 0.8rem;
      color: #888;
      margin-bottom: 0.6rem;
    }
    .popular-card-link {
      color: var(--primary-color, #4A90D9);
      font-weight: 600;
      font-size: 0.9rem;
    }

    /* All Guides section overrides */
    .guides-section .section-header-row h2 {
      font-size: 1.8rem;
      font-weight: 700;
    }
    .guides-section .guides-grid {
      grid-template-columns: repeat(2, 1fr) !important;
    }

    /* Enhanced footer */
    .enhanced-footer {
      background: var(--primary-dark, #1a1a2e);
      color: #ccc;
      padding: 3rem 2rem 1.5rem;
    }
    .footer-grid {
      display: grid;
      grid-template-columns: 2fr 1fr 1fr 1fr;
      gap: 2rem;
      max-width: 1200px;
      margin: 0 auto 2rem;
    }
    .footer-brand p {
      margin-top: 0.75rem;
      line-height: 1.6;
      font-size: 0.9rem;
    }
    .footer-col h4 {
      color: #fff;
      font-size: 1rem;
      margin-bottom: 1rem;
    }
    .footer-col ul {
      list-style: none;
      padding: 0;
      margin: 0;
    }
    .footer-col ul li {
      margin-bottom: 0.5rem;
    }
    .footer-col ul li a {
      color: #aaa;
      text-decoration: none;
      font-size: 0.9rem;
    }
    .footer-col ul li a:hover {
      color: #fff;
    }
    .footer-bottom {
      border-top: 1px solid rgba(255,255,255,0.1);
      padding-top: 1.5rem;
      text-align: center;
      font-size: 0.85rem;
      max-width: 1200px;
      margin: 0 auto;
    }
    .footer-bottom a {
      color: #aaa;
      text-decoration: none;
      margin: 0 0.5rem;
    }
    .footer-bottom a:hover {
      color: #fff;
    }

    /* Hide old footer */
    footer.site-footer {
      display: none !important;
    }

    @media (max-width: 768px) {
      .guides-section .guides-grid {
        grid-template-columns: 1fr !important;
      }
      .popular-guides-grid {
        grid-template-columns: 1fr;
      }
      .footer-grid {
        grid-template-columns: 1fr;
      }
      .popular-guides-header {
        flex-direction: column;
        gap: 0.5rem;
        align-items: flex-start;
      }
    }
  `;
  document.head.appendChild(style);
}

function buildBreadcrumb() {
  var heroContent = document.querySelector('.guides-hero-content');
  if (!heroContent) return;
  var h1 = heroContent.querySelector('h1');
  if (!h1) return;
  var bc = document.createElement('div');
  bc.className = 'guides-breadcrumb';
  bc.innerHTML = '<a href="index.html">Home</a><span class="separator">\u203A</span><span>Driveway Guides</span>';
  heroContent.insertBefore(bc, h1);
}

function enhanceHeroSubtitle() {
  var heroP = document.querySelector('.guides-hero-content p');
  if (heroP) {
    heroP.textContent = 'Learn from our 15+ years of American driveway expertise. Comprehensive tutorials and cost breakdowns for every driveway type.';
  }
}

function buildSearchBar() {
  var hero = document.querySelector('.guides-hero');
  if (!hero) return;
  var wrapper = document.createElement('div');
  wrapper.className = 'guides-search-wrapper';
  wrapper.innerHTML = '<div class="guides-search-inner"><input type="text" id="guideSearch" placeholder="Search guides (e.g., \'concrete repair\', \'cost calculator\')..." aria-label="Search guides"><button type="button" onclick="filterGuides()">Search</button></div>';
  hero.parentNode.insertBefore(wrapper, hero.nextSibling);
}

function buildCategoryFilters() {
  var searchWrapper = document.querySelector('.guides-search-wrapper');
  if (!searchWrapper) return;
  var categories = ['All Guides','Beginner','Materials','Repair','Maintenance','Planning','Technical','Eco-Friendly'];
  var filterDiv = document.createElement('div');
  filterDiv.className = 'guides-filter-wrapper';
  var html = '<span class="guides-filter-label">Filter by category:</span><div class="guides-filter-pills">';
  categories.forEach(function(cat, i) {
    html += '<button class="filter-pill' + (i === 0 ? ' active' : '') + '" data-category="' + cat + '" onclick="handleFilter(this)">' + cat + '</button>';
  });
  html += '</div>';
  filterDiv.innerHTML = html;
  searchWrapper.parentNode.insertBefore(filterDiv, searchWrapper.nextSibling);
}

function buildPopularGuides() {
  var filterWrapper = document.querySelector('.guides-filter-wrapper');
  if (!filterWrapper) return;
  var popularData = [
    {
      title: 'Driveway Basics: Types, Costs & Lifespan',
      desc: 'Your complete guide to choosing the right driveway material \u2014 compare concrete, asphalt, pavers, gravel, and more.',
      badge: 'BEGINNER GUIDE',
      badgeColor: '#dc2626',
      meta1: '20 min read',
      meta2: 'Cost comparison',
      href: 'guides/driveway-basics-types-costs-lifespan.html',
      img: 'https://images.unsplash.com/photo-1552321554-5fefe8c9ef14?w=600&h=400&fit=crop'
    },
    {
      title: 'Concrete Driveway Repair Guide',
      desc: 'Expert guide to concrete driveway repair \u2014 crack filling, resurfacing, and restoration techniques to restore your driveway.',
      badge: 'REPAIR',
      badgeColor: '#dc2626',
      meta1: '15 min read',
      meta2: 'DIY friendly',
      href: 'guides/concrete-repair.html',
      img: 'https://images.unsplash.com/photo-1504307651254-35680f356dfd?w=600&h=400&fit=crop'
    },
    {
      title: 'Driveway Cost Calculator & Pricing Guide',
      desc: 'Calculate your driveway project cost by material, size, and location. Get accurate estimates for your budget planning.',
      badge: 'PLANNING',
      badgeColor: '#10b981',
      meta1: '18 min read',
      meta2: 'Interactive calculator',
      href: 'guides/driveway-costs.html',
      img: 'https://images.unsplash.com/photo-1581578731548-c64695cc6952?w=600&h=400&fit=crop'
    }
  ];

  var section = document.createElement('section');
  section.className = 'popular-guides-section';
  var headerHTML = '<div class="popular-guides-header"><h2>Popular Guides</h2><a href="#all-guides">View All \u2192</a></div>';
  var cardsHTML = '<div class="popular-guides-grid">';
  popularData.forEach(function(g) {
    cardsHTML += '<a class="popular-card" href="' + g.href + '">';
    cardsHTML += '<div class="popular-card-image" style="background-image:url(' + g.img + ')">';
    cardsHTML += '<span class="popular-card-badge" style="background:' + g.badgeColor + '">' + g.badge + '</span></div>';
    cardsHTML += '<div class="popular-card-content"><h3>' + g.title + '</h3>';
    cardsHTML += '<p>' + g.desc + '</p>';
    cardsHTML += '<div class="popular-card-meta"><span>\u23F1 ' + g.meta1 + '</span><span>\uD83D\uDCB0 ' + g.meta2 + '</span></div>';
    cardsHTML += '<span class="popular-card-link">Read Full Guide \u2192</span></div></a>';
  });
  cardsHTML += '</div>';
  section.innerHTML = headerHTML + cardsHTML;
  filterWrapper.parentNode.insertBefore(section, filterWrapper.nextSibling);
}

function restructureAllGuides() {
  var section = document.querySelector('.guides-section');
  if (!section) return;
  // Add an id for anchor linking
  section.id = 'all-guides';
  // Change the section heading from 'Our Expert Guides' to 'All Guides'
  var sectionH2 = section.querySelector('h2');
  if (sectionH2) {
    sectionH2.textContent = 'All Guides';
  }
  // Remove the subtitle paragraph
  var sectionP = section.querySelector('.container > p');
  if (sectionP && sectionP.textContent.indexOf('Comprehensive tutorials') > -1) {
    sectionP.style.display = 'none';
  }
  // Make the grid 2 columns
  var grid = section.querySelector('.guides-grid');
  if (grid) {
    grid.style.setProperty('grid-template-columns', 'repeat(2, 1fr)', 'important');
  }
}

// Global filter handler
window.handleFilter = function(btn) {
  // Update active pill
  document.querySelectorAll('.filter-pill').forEach(function(p) {
    p.classList.remove('active');
  });
  btn.classList.add('active');
  var cat = btn.getAttribute('data-category');
  filterByCategory(cat);
};

function filterByCategory(category) {
  var cards = document.querySelectorAll('.guides-grid .guide-card');
  var catMap = {
    'Beginner': ['beginner guide', 'beginner'],
    'Materials': ['eco-friendly', 'traditional', 'premium', 'budget-friendly', 'coastal', 'concrete'],
    'Repair': ['repair'],
    'Maintenance': ['maintenance'],
    'Planning': ['planning', 'site prep'],
    'Technical': ['technical', 'foundation', 'drainage', 'structural', 'heavy duty'],
    'Eco-Friendly': ['eco-friendly']
  };
  cards.forEach(function(card) {
    if (category === 'All Guides') {
      card.style.display = '';
      return;
    }
    var badge = card.querySelector('.guide-card-badge');
    if (!badge) { card.style.display = 'none'; return; }
    var badgeText = badge.textContent.trim().toLowerCase();
    var matchArr = catMap[category] || [];
    var match = matchArr.some(function(m) { return badgeText.indexOf(m) > -1; });
    card.style.display = match ? '' : 'none';
  });
}

// Global search handler
window.filterGuides = function() {
  var input = document.getElementById('guideSearch');
  if (!input) return;
  var query = input.value.toLowerCase().trim();
  var cards = document.querySelectorAll('.guides-grid .guide-card');
  cards.forEach(function(card) {
    if (!query) { card.style.display = ''; return; }
    var text = card.textContent.toLowerCase();
    card.style.display = text.indexOf(query) > -1 ? '' : 'none';
  });
  // Reset filter pills to 'All Guides'
  document.querySelectorAll('.filter-pill').forEach(function(p) {
    p.classList.remove('active');
    if (p.getAttribute('data-category') === 'All Guides') p.classList.add('active');
  });
};

function enhanceFooter() {
  // Hide the old footer
  var oldFooter = document.querySelector('footer');
  if (oldFooter) {
    oldFooter.style.display = 'none';
  }
  // Also hide the old simple footer if it exists
  var oldSimpleFooter = document.querySelector('.simple-footer');
  if (oldSimpleFooter) {
    oldSimpleFooter.style.display = 'none';
  }

  // Build new enhanced footer
  var footer = document.createElement('footer');
  footer.className = 'enhanced-footer';
  footer.innerHTML = '<div class="footer-grid">' +
    '<div class="footer-brand">' +
    '<strong style="color:#fff;font-size:1.3rem;">D RIVEWAYZ USA</strong>' +
    '<p>Your trusted partner for professional driveway services across America. Quality craftsmanship, nationwide coverage, local expertise.</p>' +
    '</div>' +
    '<div class="footer-col"><h4>Quick Links</h4><ul>' +
    '<li><a href="index.html">Home</a></li>' +
    '<li><a href="index.html#services">Services</a></li>' +
    '<li><a href="locations.html">Locations</a></li>' +
    '<li><a href="guides-hub.html">Guides</a></li>' +
    '</ul></div>' +
    '<div class="footer-col"><h4>Services</h4><ul>' +
    '<li><a href="index.html#services">Driveway Installation</a></li>' +
    '<li><a href="index.html#services">Sealcoating</a></li>' +
    '<li><a href="index.html#services">Repairs</a></li>' +
    '<li><a href="index.html#services">Resurfacing</a></li>' +
    '</ul></div>' +
    '<div class="footer-col"><h4>Contact</h4><ul>' +
    '<li>1-800-DRIVEWAY</li>' +
    '<li>info@drivewayzusa.com</li>' +
    '<li>www.drivewayzusa.com</li>' +
    '</ul></div>' +
    '</div>' +
    '<div class="footer-bottom">' +
    '<p>\u00A9 2026 Drivewayz USA. Licensed & Insured. Serving the United States with Pride.</p>' +
    '<p><a href="#">Privacy Policy</a> | <a href="#">Terms of Service</a></p>' +
    '</div>';
  document.body.appendChild(footer);
}
