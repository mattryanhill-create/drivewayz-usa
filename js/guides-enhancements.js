/**
 * Guides Hub Page Enhancements v2
 * Sidebar layout: Popular Guides + CTA in sidebar, filters connect directly to results
 * Fixes: Enter key search, result count, search/filter coordination
 */
document.addEventListener('DOMContentLoaded', function() {
  injectCSS();
  buildBreadcrumb();
  enhanceHeroSubtitle();
  buildSearchBar();
  buildCategoryFilters();
  restructureToSidebarLayout();
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
    /* Result count bar */
    .guides-result-bar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1.5rem;
      padding-bottom: 1rem;
      border-bottom: 1px solid #e5e7eb;
    }
    .guides-result-count {
      font-size: 0.95rem;
      color: #666;
    }
    .guides-result-count strong {
      color: var(--text-dark, #1a1a2e);
    }
    .guides-no-results {
      text-align: center;
      padding: 3rem 1rem;
      color: #888;
      font-size: 1.1rem;
    }
    .guides-no-results p {
      margin-bottom: 0.5rem;
    }
    /* Sidebar layout wrapper */
    .guides-content-wrapper {
      display: grid;
      grid-template-columns: 1fr 320px;
      gap: 2rem;
      max-width: 1200px;
      margin: 0 auto;
      padding: 0 2rem;
    }
    .guides-main-content {
      min-width: 0;
    }
    .guides-main-content .guides-grid {
      grid-template-columns: repeat(2, 1fr) !important;
    }
    /* Sidebar */
    .guides-sidebar {
      position: sticky;
      top: 120px;
      align-self: start;
      display: flex;
      flex-direction: column;
      gap: 1.5rem;
    }
    .sidebar-widget {
      background: #fff;
      border-radius: 12px;
      box-shadow: 0 2px 12px rgba(0,0,0,0.08);
      overflow: hidden;
    }
    .sidebar-widget-header {
      padding: 1rem 1.25rem;
      font-size: 1rem;
      font-weight: 700;
      color: var(--text-dark, #1a1a2e);
      border-bottom: 1px solid #f0f0f0;
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }
    .sidebar-widget-header .icon {
      font-size: 1.1rem;
    }
    /* Popular Guides sidebar cards */
    .sidebar-popular-item {
      display: flex;
      gap: 0.75rem;
      padding: 1rem 1.25rem;
      border-bottom: 1px solid #f5f5f5;
      text-decoration: none;
      color: inherit;
      transition: background 0.2s;
    }
    .sidebar-popular-item:last-child {
      border-bottom: none;
    }
    .sidebar-popular-item:hover {
      background: #f8f9fa;
    }
    .sidebar-popular-thumb {
      width: 64px;
      height: 64px;
      border-radius: 8px;
      background-size: cover;
      background-position: center;
      flex-shrink: 0;
    }
    .sidebar-popular-info h4 {
      font-size: 0.85rem;
      font-weight: 600;
      color: var(--text-dark, #1a1a2e);
      margin: 0 0 0.25rem;
      line-height: 1.3;
    }
    .sidebar-popular-info .meta {
      font-size: 0.75rem;
      color: #888;
    }
    .sidebar-popular-info .badge-sm {
      display: inline-block;
      padding: 0.15rem 0.5rem;
      border-radius: 10px;
      font-size: 0.65rem;
      font-weight: 700;
      text-transform: uppercase;
      color: #fff;
      margin-bottom: 0.25rem;
    }
    /* Sidebar CTA widget */
    .sidebar-cta {
      background: linear-gradient(135deg, var(--primary-dark, #1a1a2e) 0%, var(--primary-color, #4A90D9) 100%);
      color: #fff;
      padding: 1.5rem 1.25rem;
      text-align: center;
    }
    .sidebar-cta h3 {
      font-size: 1.1rem;
      margin: 0 0 0.5rem;
      font-weight: 700;
    }
    .sidebar-cta p {
      font-size: 0.85rem;
      opacity: 0.9;
      margin: 0 0 1rem;
      line-height: 1.5;
    }
    .sidebar-cta-btn {
      display: inline-block;
      background: #fff;
      color: var(--primary-color, #4A90D9);
      padding: 0.7rem 1.5rem;
      border-radius: 8px;
      font-weight: 700;
      font-size: 0.9rem;
      text-decoration: none;
      transition: all 0.3s;
    }
    .sidebar-cta-btn:hover {
      background: #f0f0f0;
      transform: translateY(-2px);
    }
    /* Section header */
    .guides-section-header {
      margin-bottom: 1.5rem;
    }
    .guides-section-header h2 {
      font-size: 1.8rem;
      font-weight: 700;
      color: var(--text-dark, #1a1a2e);
      margin: 0;
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
    /* Hide old popular guides section if it exists */
    .popular-guides-section {
      display: none !important;
    }
    /* Responsive */
    @media (max-width: 900px) {
      .guides-content-wrapper {
        grid-template-columns: 1fr;
      }
      .guides-sidebar {
        position: static;
        order: -1;
      }
      .guides-main-content .guides-grid {
        grid-template-columns: 1fr !important;
      }
      .footer-grid {
        grid-template-columns: 1fr;
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
  bc.innerHTML = '<a href="/">Home</a><span class="separator">\u203A</span><span>Driveway Guides</span>';
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
  // Add Enter key support
  setTimeout(function() {
    var input = document.getElementById('guideSearch');
    if (input) {
      input.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
          e.preventDefault();
          filterGuides();
        }
      });
    }
  }, 100);
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

function restructureToSidebarLayout() {
  var section = document.querySelector('.guides-section');
  if (!section) return;
  section.id = 'all-guides';
  // Change section heading
  var sectionH2 = section.querySelector('h2');
  if (sectionH2) sectionH2.textContent = 'All Guides';
  // Hide old subtitle
  var sectionP = section.querySelector('.container > p');
  if (sectionP && sectionP.textContent.indexOf('Comprehensive tutorials') > -1) {
    sectionP.style.display = 'none';
  }
  // Get the container and grid
  var container = section.querySelector('.container') || section;
  if (!container) return;
      var grid = section.querySelector('.guides-grid');
    if (!grid) {
      grid = document.createElement('div');
      grid.className = 'guides-grid';
      var cards = container.querySelectorAll('.guide-card');
      if (cards.length === 0) return;
      cards.forEach(function(card) { grid.appendChild(card); });
      container.appendChild(grid);
    }
// Create the sidebar layout wrapper
  var wrapper = document.createElement('div');
  wrapper.className = 'guides-content-wrapper';
  // Create main content area
  var mainContent = document.createElement('div');
  mainContent.className = 'guides-main-content';
  // Add section header with result count
  var headerDiv = document.createElement('div');
  headerDiv.className = 'guides-section-header';
  headerDiv.innerHTML = '<h2>All Guides</h2>';
  mainContent.appendChild(headerDiv);
  // Add result count bar
  var resultBar = document.createElement('div');
  resultBar.className = 'guides-result-bar';
  resultBar.id = 'guidesResultBar';
  var totalCards = grid.querySelectorAll('.guide-card').length;
  resultBar.innerHTML = '<span class="guides-result-count">Showing <strong>' + totalCards + '</strong> of <strong>' + totalCards + '</strong> guides</span>';
  mainContent.appendChild(resultBar);
  // Move the grid into main content
  mainContent.appendChild(grid);
  // Create sidebar
  var sidebar = document.createElement('aside');
  sidebar.className = 'guides-sidebar';
  sidebar.innerHTML = buildSidebarPopularHTML() + buildSidebarCTAHTML();
  // Assemble
  wrapper.appendChild(mainContent);
  wrapper.appendChild(sidebar);
  // Hide old h2 since we have new one in mainContent
  if (sectionH2) sectionH2.style.display = 'none';
  container.appendChild(wrapper);
}

function buildSidebarPopularHTML() {
  var popularData = [
    {
      title: 'Driveway Basics: Types, Costs & Lifespan',
      badge: 'BEGINNER', badgeColor: '#dc2626',
      meta: '20 min read',
      href: '/guides/driveway-basics-types-costs-lifespan/',
      img: 'https://images.unsplash.com/photo-1552321554-5fefe8c9ef14?w=150&h=150&fit=crop'
    },
    {
      title: 'Concrete Driveway Repair Guide',
      badge: 'REPAIR', badgeColor: '#dc2626',
      meta: '15 min read',
      href: '/guides/concrete-repair/',
      img: 'https://images.unsplash.com/photo-1504307651254-35680f356dfd?w=150&h=150&fit=crop'
    },
    {
      title: 'Driveway Cost Calculator & Pricing Guide',
      badge: 'PLANNING', badgeColor: '#10b981',
      meta: '18 min read',
      href: '/guides/driveway-costs/',
      img: 'https://images.unsplash.com/photo-1581578731548-c64695cc6952?w=150&h=150&fit=crop'
    }
  ];
  var html = '<div class="sidebar-widget"><div class="sidebar-widget-header"><span class="icon">\u2B50</span> Popular Guides</div>';
  popularData.forEach(function(g) {
    html += '<a class="sidebar-popular-item" href="' + g.href + '">';
    html += '<div class="sidebar-popular-thumb" style="background-image:url(' + g.img + ')"></div>';
    html += '<div class="sidebar-popular-info">';
    html += '<span class="badge-sm" style="background:' + g.badgeColor + '">' + g.badge + '</span>';
    html += '<h4>' + g.title + '</h4>';
    html += '<span class="meta">\u23F1 ' + g.meta + '</span>';
    html += '</div></a>';
  });
  html += '</div>';
  return html;
}

function buildSidebarCTAHTML() {
  return '<div class="sidebar-widget sidebar-cta">' +
    '<h3>Need Professional Help?</h3>' +
    '<p>Get a free estimate from our driveway experts. Serving all 50 states.</p>' +
    '<a href="/#contact" class="sidebar-cta-btn">Get Free Estimate</a>' +
    '</div>';
}

// Update result count display
function updateResultCount() {
  var bar = document.getElementById('guidesResultBar');
  if (!bar) return;
  var cards = document.querySelectorAll('.guides-grid .guide-card');
  var total = cards.length;
  var visible = 0;
  cards.forEach(function(card) {
    if (card.style.display !== 'none') visible++;
  });
  if (visible === 0) {
    bar.innerHTML = '<span class="guides-result-count">No guides found</span>';
    // Show no results message in grid
    var grid = document.querySelector('.guides-grid');
    var noResults = grid.querySelector('.guides-no-results');
    if (!noResults) {
      noResults = document.createElement('div');
      noResults.className = 'guides-no-results';
      noResults.style.gridColumn = '1 / -1';
      noResults.innerHTML = '<p>No guides match your search.</p><p style="font-size:0.9rem">Try a different keyword or reset filters.</p>';
      grid.appendChild(noResults);
    }
    noResults.style.display = '';
  } else {
    bar.innerHTML = '<span class="guides-result-count">Showing <strong>' + visible + '</strong> of <strong>' + total + '</strong> guides</span>';
    // Hide no results message
    var noResults = document.querySelector('.guides-no-results');
    if (noResults) noResults.style.display = 'none';
  }
}

// Global filter handler
window.handleFilter = function(btn) {
  // Update active pill
  document.querySelectorAll('.filter-pill').forEach(function(p) {
    p.classList.remove('active');
  });
  btn.classList.add('active');
  // Clear search input when filtering
  var searchInput = document.getElementById('guideSearch');
  if (searchInput) searchInput.value = '';
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
  updateResultCount();
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
  updateResultCount();
};

function enhanceFooter() {
  var oldFooter = document.querySelector('footer');
  if (oldFooter) oldFooter.style.display = 'none';
  var oldSimpleFooter = document.querySelector('.simple-footer');
  if (oldSimpleFooter) oldSimpleFooter.style.display = 'none';
  var footer = document.createElement('footer');
  footer.className = 'enhanced-footer';
  footer.innerHTML = '<div class="footer-grid">' +
    '<div class="footer-brand">' +
    '<strong style="color:#fff;font-size:1.3rem;">DRIVEWAYZ USA</strong>' +
    '<p>Your trusted partner for professional driveway services across America. Quality craftsmanship, nationwide coverage, local expertise.</p>' +
    '</div>' +
    '<div class="footer-col"><h4>Quick Links</h4><ul>' +
    '<li><a href="/">Home</a></li>' +
    '<li><a href="/#services">Services</a></li>' +
    '<li><a href="/locations/">Locations</a></li>' +
    '<li><a href="/guides-hub/">Guides</a></li>' +
    '</ul></div>' +
    '<div class="footer-col"><h4>Services</h4><ul>' +
    '<li><a href="/#services">Driveway Installation</a></li>' +
    '<li><a href="/#services">Sealcoating</a></li>' +
    '<li><a href="/#services">Repairs</a></li>' +
    '<li><a href="/#services">Resurfacing</a></li>' +
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
