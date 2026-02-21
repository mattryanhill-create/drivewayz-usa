// ============================================
// DRIVEWAYZ USA - MAIN JAVASCRIPT
// ============================================

// ----- STATES DATA (with new expanded fields) -----
const statesData = {
  "alabama": {
    name: "Alabama",
    abbreviation: "AL",
    introHTML: `
      <p>Alabama's diverse climate, ranging from humid subtropical in the south to temperate in the north, 
      presents unique challenges for driveway installation. From the Gulf Coast's sandy soils to the 
      Appalachian foothills' clay-rich terrain, homeowners need driveway solutions that can withstand 
      heavy rainfall, occasional freezing, and intense summer heat.</p>
      <p>Whether you're in Birmingham, Montgomery, or Mobile, choosing the right driveway material 
      and contractor is essential for long-lasting performance and curb appeal.</p>
    `,
    drivewayTypes: [
      {
        title: "Concrete Driveways",
        description: "The most popular choice in Alabama due to durability and low maintenance. Ideal for handling heavy rain and occasional freeze-thaw cycles. Expect 20-30 year lifespan with proper care."
      },
      {
        title: "Asphalt Driveways",
        description: "Cost-effective option that performs well in Alabama's heat. Requires resealing every 2-3 years. Best for homeowners seeking affordability and quick installation."
      },
      {
        title: "Gravel Driveways",
        description: "Excellent for rural areas and large properties. Provides superior drainage and easy repairs. Popular in Alabama's countryside for affordability and rustic appearance."
      },
      {
        title: "Paver Driveways",
        description: "Premium option offering unmatched aesthetic appeal. Brick and concrete pavers handle Alabama's climate well and allow for easy spot repairs. Higher upfront cost but adds significant home value."
      },
      {
        title: "Chip Seal Driveways",
        description: "Budget-friendly alternative to asphalt, popular in rural Alabama. Provides a textured surface with good traction. Requires periodic refreshing."
      }
    ],
    localFacts: [
      {
        title: "Climate Considerations",
        description: "Alabama averages 55-65 inches of rainfall annually. Proper drainage is critical—consider permeable options or ensure adequate slope (minimum 1%) to prevent standing water."
      },
      {
        title: "Soil Types",
        description: "Northern Alabama features clay-heavy soils that expand and contract, potentially cracking rigid driveways. Southern coastal areas have sandy soils requiring proper base preparation."
      },
      {
        title: "Permit Requirements",
        description: "Most Alabama municipalities require permits for new driveway installation. Check with your local building department—fees typically range from $50-$200."
      },
      {
        title: "HOA Regulations",
        description: "Many Alabama neighborhoods have HOA restrictions on driveway materials and colors. Always verify approved options before installation."
      },
      {
        title: "Average Costs (2024)",
        description: "Concrete: $8-15/sq ft | Asphalt: $3-7/sq ft | Gravel: $1-3/sq ft | Pavers: $12-25/sq ft. Prices vary by location and project complexity."
      }
    ],
    references: [
      "Alabama Department of Transportation - Driveway Standards",
      "National Asphalt Pavement Association - Climate Guidelines",
      "American Concrete Institute - Residential Paving Standards"
    ],
    relatedResources: [
      { title: "Alabama Contractor License Board", url: "https://www.genconb.state.al.us/" },
      { title: "Better Business Bureau of Alabama", url: "https://www.bbb.org/alabama" },
      { title: "Home Builders Association of Alabama", url: "https://www.hbaal.com/" }
    ],
    cities: ["Birmingham", "Montgomery", "Mobile", "Huntsville", "Tuscaloosa"],
    services: ["Concrete Driveways", "Asphalt Paving", "Gravel Installation", "Driveway Repair", "Sealcoating"],
    averageCost: "$3,500 - $8,500",
    climate: "Humid subtropical with hot summers and mild winters"
  },
  
  "alaska": {
    name: "Alaska",
    abbreviation: "AK",
    introHTML: `
      <p>Alaska's extreme climate demands driveway solutions built to withstand freeze-thaw cycles, 
      permafrost conditions, and heavy snow loads. From Anchorage's coastal climate to Fairbanks' 
      interior extremes, driveway installation requires specialized knowledge and materials.</p>
      <p>Proper base preparation and drainage are critical to prevent frost heave and ensure 
      year-round usability in the Last Frontier.</p>
    `,
    drivewayTypes: [
      {
        title: "Heated Concrete Driveways",
        description: "Essential for many Alaskan homeowners. Embedded heating elements prevent ice buildup and eliminate shoveling. Higher installation cost but invaluable during long winters."
      },
      {
        title: "Reinforced Asphalt",
        description: "Modified asphalt mixtures designed for extreme cold. Flexible enough to handle ground movement from freeze-thaw cycles. Regular sealcoating extends lifespan."
      },
      {
        title: "Gravel with Geotextile",
        description: "Cost-effective option for rural Alaska. Geotextile fabric prevents mixing with subgrade and improves stability. Easy to maintain and repair."
      },
      {
        title: "Permeable Pavers",
        description: "Allows water drainage to prevent ice formation. Excellent for areas with frequent freeze-thaw. Requires proper base depth for load-bearing capacity."
      }
    ],
    localFacts: [
      {
        title: "Frost Heave Prevention",
        description: "Alaska's freeze-thaw cycles can lift driveways by several inches. Proper base depth (12-18 inches minimum) and non-frost-susceptible materials are essential."
      },
      {
        title: "Permafrost Considerations",
        description: "In permafrost zones, insulated foundations or thermosyphons may be required to maintain ground stability. Consult with engineers familiar with arctic construction."
      },
      {
        title: "Snow Load Capacity",
        description: "Driveways must support snow removal equipment. Design for minimum 10,000 lb load capacity in residential areas, higher for commercial."
      },
      {
        title: "Seasonal Installation Windows",
        description: "Most driveway work occurs May-September. Winter installations are possible with heated enclosures but significantly more expensive."
      },
      {
        title: "Average Costs (2024)",
        description: "Standard concrete: $10-18/sq ft | Heated systems: add $15-25/sq ft | Reinforced asphalt: $5-10/sq ft | Gravel: $2-5/sq ft. Remote locations increase costs 20-50%."
      }
    ],
    references: [
      "Alaska Department of Transportation - Cold Region Paving Standards",
      "University of Alaska Fairbanks - Permafrost Engineering Guidelines",
      "American Society of Civil Engineers - Arctic Construction Manual"
    ],
    relatedResources: [
      { title: "Alaska Department of Commerce - Contractor Licensing", url: "https://www.commerce.alaska.gov/" },
      { title: "Anchorage Better Business Bureau", url: "https://www.bbb.org/alaska" },
      { title: "Alaska Home Builders Association", url: "https://www.akhba.com/" }
    ],
    cities: ["Anchorage", "Fairbanks", "Juneau", "Wasilla", "Sitka"],
    services: ["Heated Driveways", "Frost-Resistant Concrete", "Snow-Melt Systems", "Permafrost Solutions", "Driveway Repair"],
    averageCost: "$6,500 - $15,000",
    climate: "Subarctic with extreme temperature variations"
  },
  
  "arizona": {
    name: "Arizona",
    abbreviation: "AZ",
    introHTML: `
      <p>Arizona's desert climate brings intense heat, monsoon rains, and minimal freezing—creating 
      unique driveway challenges. From Phoenix's urban heat island to Flagstaff's mountain conditions, 
      material selection must account for thermal expansion and UV exposure.</p>
      <p>The Grand Canyon State's diverse elevations mean driveway requirements vary significantly 
      between desert lowlands and high-country communities.</p>
    `,
    drivewayTypes: [
      {
        title: "Stained/Stamped Concrete",
        description: "Extremely popular in Arizona for aesthetic versatility. Light-colored stains reflect heat. Stamped patterns complement Southwest architecture. Requires periodic resealing against UV damage."
      },
      {
        title: "Interlocking Pavers",
        description: "Excellent for handling thermal expansion without cracking. Allows for easy repairs and offers design flexibility. Permeable options help with monsoon drainage."
      },
      {
        title: "Exposed Aggregate Concrete",
        description: "Textured surface provides natural slip resistance and hides dust. Decorative stone options complement desert landscapes. Very durable in dry climates."
      },
      {
        title: "Decomposed Granite",
        description: "Eco-friendly option that blends with natural surroundings. Stabilized versions offer solid surface. Popular for Tucson and Phoenix area homes seeking desert aesthetics."
      }
    ],
    localFacts: [
      {
        title: "Heat Reflection",
        description: "Dark surfaces can reach 150°F+ in Arizona summers. Light-colored materials reduce heat absorption and can lower surrounding temperatures by 10-20°F."
      },
      {
        title: "Monsoon Drainage",
        description: "Arizona's summer monsoons bring intense rainfall. Proper grading (2% minimum slope) and drainage channels prevent flooding and erosion damage."
      },
      {
        title: "UV Protection",
        description: "Intense sun exposure degrades sealers and fades colors. Use UV-resistant sealers and plan for reapplication every 2-3 years in exposed areas."
      },
      {
        title: "Soil Conditions",
        description: "Desert soils are often expansive clay or caliche (cemented calcium carbonate). Both require removal and replacement with proper base materials for stable installation."
      },
      {
        title: "Average Costs (2024)",
        description: "Standard concrete: $6-12/sq ft | Stamped concrete: $10-18/sq ft | Pavers: $12-22/sq ft | Exposed aggregate: $8-15/sq ft. Flagstaff/northern areas cost 15-25% more."
      }
    ],
    references: [
      "Arizona Registrar of Contractors - Paving Standards",
      "Arizona Department of Transportation - Desert Climate Guidelines",
      "Portland Cement Association - Hot Weather Concreting"
    ],
    relatedResources: [
      { title: "Arizona Registrar of Contractors", url: "https://roc.az.gov/" },
      { title: "Better Business Bureau of Arizona", url: "https://www.bbb.org/arizona" },
      { title: "Home Builders Association of Central Arizona", url: "https://www.hbaca.org/" }
    ],
    cities: ["Phoenix", "Tucson", "Mesa", "Scottsdale", "Flagstaff"],
    services: ["Stamped Concrete", "Paver Installation", "Exposed Aggregate", "Heat-Resistant Coatings", "Monsoon Drainage"],
    averageCost: "$4,500 - $9,500",
    climate: "Desert with extreme heat and minimal precipitation"
  },
  
  "arkansas": {
    name: "Arkansas",
    abbreviation: "AR",
    introHTML: `
      <p>The Natural State's varied topography—from the Ozark Mountains to the Mississippi Delta—
      creates diverse driveway installation challenges. Arkansas experiences all four seasons with 
      hot, humid summers and occasional winter ice storms.</p>
      <p>Homeowners must balance durability, cost, and aesthetics while accounting for clay-heavy 
      soils and significant rainfall throughout the year.</p>
    `,
    drivewayTypes: [
      {
        title: "Concrete Driveways",
        description: "Reliable choice for Arkansas' climate. Handles temperature swings well and resists damage from occasional ice. Control joints every 10 feet prevent cracking from soil movement."
      },
      {
        title: "Asphalt Driveways",
        description: "Popular for affordability and flexibility. Performs well in Arkansas winters but may soften during extreme summer heat. Requires periodic sealcoating."
      },
      {
        title: "Gravel Driveways",
        description: "Ideal for rural properties and long driveways. Excellent drainage for heavy rainfall areas. Cost-effective for large areas common in Arkansas countryside."
      },
      {
        title: "Chip Seal Driveways",
        description: "Budget-friendly option combining asphalt base with stone aggregate. Popular in rural Arkansas for its rustic appearance and good traction."
      }
    ],
    localFacts: [
      {
        title: "Clay Soil Challenges",
        description: "Much of Arkansas has expansive clay soil that swells when wet and shrinks when dry. Proper base preparation with 6-8 inches of compacted aggregate is essential."
      },
      {
        title: "Drainage Requirements",
        description: "Arkansas averages 45-55 inches of rainfall annually. French drains or swales alongside driveways prevent water accumulation and base erosion."
      },
      {
        title: "Freeze Protection",
        description: "While Arkansas winters are mild, ice storms occur. Avoid de-icing salts on concrete—they cause surface damage. Use sand or calcium chloride instead."
      },
      {
        title: "Ozark Terrain",
        description: "Mountainous areas require careful grading and may need retaining walls. Steep driveways benefit from textured surfaces for winter traction."
      },
      {
        title: "Average Costs (2024)",
        description: "Concrete: $7-13/sq ft | Asphalt: $3-6/sq ft | Gravel: $1-3/sq ft | Chip seal: $2-4/sq ft. Rural areas may have higher transportation costs."
      }
    ],
    references: [
      "Arkansas State Highway and Transportation Department - Driveway Standards",
      "Arkansas Contractors Licensing Board - Residential Paving Guidelines"
    ],
    relatedResources: [
      { title: "Arkansas Contractors Licensing Board", url: "https://www.arkansas.gov/aclb/" },
      { title: "Better Business Bureau of Arkansas", url: "https://www.bbb.org/arkansas" },
      { title: "Arkansas Home Builders Association", url: "https://www.arkansashba.com/" }
    ],
    cities: ["Little Rock", "Fayetteville", "Fort Smith", "Springdale", "Jonesboro"],
    services: ["Concrete Installation", "Asphalt Paving", "Gravel Driveways", "Drainage Solutions", "Driveway Repair"],
    averageCost: "$3,800 - $8,000",
    climate: "Humid subtropical with four distinct seasons"
  },
  
  "california": {
    name: "California",
    abbreviation: "CA",
    introHTML: `
      <p>California's incredible diversity—from coastal fog to desert heat, mountain snow to valley 
      sun—means driveway requirements vary dramatically by region. Environmental regulations, 
      seismic considerations, and water restrictions also influence material choices.</p>
      <p>Whether you're in Los Angeles, San Francisco, or Sacramento, understanding local conditions 
      and codes is essential for a successful driveway project.</p>
    `,
    drivewayTypes: [
      {
        title: "Permeable Pavers",
        description: "California's water regulations make permeable options increasingly popular. Reduces runoff and may qualify for rebates. Excellent for areas with drainage restrictions."
      },
      {
        title: "Decorative Concrete",
        description: "Stamped, stained, and exposed aggregate concrete dominate California driveways. Unlimited design options complement any architectural style. UV-resistant sealers essential."
      },
      {
        title: "Interlocking Pavers",
        description: "Handles seismic movement better than monolithic concrete. Easy repairs and design flexibility. Many California municipalities offer permeable paver incentives."
      },
      {
        title: "Decomposed Granite",
        description: "Eco-friendly, permeable option popular in drought-conscious areas. Stabilized versions provide solid driving surface. Complements California's natural landscapes."
      },
      {
        title: "Asphalt with Reflective Coating",
        description: "Cool pavement coatings reduce heat absorption by 10-20°F. Helps combat urban heat island effect. Required in some jurisdictions for new construction."
      }
    ],
    localFacts: [
      {
        title: "Seismic Considerations",
        description: "California's earthquake risk favors flexible paving systems. Pavers and properly jointed concrete handle ground movement better than rigid monolithic surfaces."
      },
      {
        title: "Water Restrictions",
        description: "Many areas restrict runoff from impervious surfaces. Permeable driveways may be required for new construction and can qualify for water district rebates ($2-5/sq ft)."
      },
      {
        title: "Cool Roof/Pavement Requirements",
        description: "Some cities (LA, San Diego) require reflective surfaces for new driveways. SRI (Solar Reflectance Index) ratings of 29+ may be mandated."
      },
      {
        title: "Coastal Salt Air",
        description: "Coastal areas require corrosion-resistant reinforcement and sealers. Salt air accelerates deterioration of untreated concrete and metal components."
      },
      {
        title: "Average Costs (2024)",
        description: "Standard concrete: $8-16/sq ft | Stamped: $12-22/sq ft | Pavers: $14-28/sq ft | Permeable systems: $16-32/sq ft. Bay Area and coastal cities 20-40% higher."
      }
    ],
    references: [
      "California Building Standards Code - Driveway Requirements",
      "California Department of Transportation - Paving Standards",
      "USGBC California - Green Paving Guidelines"
    ],
    relatedResources: [
      { title: "California Contractors State License Board", url: "https://www.cslb.ca.gov/" },
      { title: "Better Business Bureau of California", url: "https://www.bbb.org/california" },
      { title: "California Home Builders Association", url: "https://www.chbaf.com/" }
    ],
    cities: ["Los Angeles", "San Francisco", "San Diego", "Sacramento", "San Jose"],
    services: ["Permeable Pavers", "Stamped Concrete", "Cool Pavement Systems", "Seismic-Resistant Installation", "Eco-Friendly Options"],
    averageCost: "$6,000 - $14,000",
    climate: "Mediterranean to desert, varies dramatically by region"
  }
  // Add more states here...
};

// ============================================
// UTILITY FUNCTIONS
// ============================================

function getStateFromURL() {
  const path = window.location.pathname;
  const match = path.match(/\/state\/([a-z-]+)/);
  return match ? match[1].replace(/-/g, '') : null;
}

function toggleFact(index) {
  const content = document.getElementById(`fact-${index}`);
  const toggle = document.getElementById(`toggle-${index}`);
  
  if (content && toggle) {
    if (content.style.display === 'none' || content.style.display === '') {
      content.style.display = 'block';
      toggle.textContent = '−';
    } else {
      content.style.display = 'none';
      toggle.textContent = '+';
    }
  }
}

function showQuoteForm() {
  // Your existing quote form logic
  alert('Quote form would open here');
}

// ============================================
// RENDER FUNCTIONS
// ============================================

function renderHomePage() {
  // Your existing home page rendering logic
  console.log('Rendering home page...');
}

function renderPage() {
  const stateKey = getStateFromURL();
  const state = statesData[stateKey];
  
  if (!state) {
    renderHomePage();
    return;
  }
  
  const contentHTML = `
    <!-- HERO SECTION -->
    <section class="state-hero">
      <div class="hero-content">
        <h1>Driveway Contractors in ${state.name}</h1>
        <p class="hero-subtitle">Find top-rated driveway installation and repair services</p>
        <div class="hero-stats">
          <span class="stat">${state.cities.length}+ Cities Served</span>
          <span class="stat">${state.services.length}+ Services</span>
          <span class="stat">${state.averageCost} Avg. Cost</span>
        </div>
      </div>
    </section>

    <!-- INTRO SECTION -->
    <section class="state-intro">
      <div class="container">
        <div class="intro-content">
          <h2>Driveway Installation in ${state.name}</h2>
          <div class="intro-text">
            ${state.introHTML}
          </div>
        </div>
        <div class="intro-climate">
          <div class="climate-card">
            <span class="climate-icon">🌤️</span>
            <h3>Climate</h3>
            <p>${state.climate}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- CITIES SECTION -->
    <section class="state-cities">
      <div class="container">
        <h2>Top Cities We Serve in ${state.name}</h2>
        <div class="cities-grid">
          ${state.cities.map(city => `
            <div class="city-card">
              <h3>${city}</h3>
              <a href="#${city.toLowerCase().replace(/\s+/g, '-')}" class="city-link">View Contractors →</a>
            </div>
          `).join('')}
        </div>
      </div>
    </section>

    <!-- SERVICES SECTION -->
    <section class="state-services">
      <div class="container">
        <h2>Driveway Services in ${state.name}</h2>
        <div class="services-grid">
          ${state.services.map(service => `
            <div class="service-card">
              <span class="service-icon">🏗️</span>
              <h3>${service}</h3>
              <p>Professional ${service.toLowerCase()} services throughout ${state.name}</p>
            </div>
          `).join('')}
        </div>
      </div>
    </section>

    <!-- DRIVEWAY TYPES SECTION -->
    <section class="driveway-types">
      <div class="container">
        <h2>Best Driveway Types for ${state.name}</h2>
        <p class="section-intro">Choose the right material for your climate, soil conditions, and budget</p>
        <div class="driveway-types-grid">
          ${state.drivewayTypes.map((type, index) => `
            <div class="driveway-type-card">
              <div class="type-number">${index + 1}</div>
              <h3>${type.title}</h3>
              <p>${type.description}</p>
            </div>
          `).join('')}
        </div>
      </div>
    </section>

    <!-- LOCAL FACTS SECTION -->
    <section class="local-facts">
      <div class="container">
        <h2>Local Facts & Considerations</h2>
        <p class="section-intro">Important information for ${state.name} homeowners planning a driveway project</p>
        <div class="facts-accordion">
          ${state.localFacts.map((fact, index) => `
            <div class="fact-item">
              <button class="fact-header" onclick="toggleFact(${index})">
                <span class="fact-title">${fact.title}</span>
                <span class="fact-toggle" id="toggle-${index}">+</span>
              </button>
              <div class="fact-content" id="fact-${index}" style="display: none;">
                <p>${fact.description}</p>
              </div>
            </div>
          `).join('')}
        </div>
      </div>
    </section>

    <!-- REFERENCES SECTION -->
    <section class="references">
      <div class="container">
        <h3>References & Standards</h3>
        <ul class="references-list">
          ${state.references.map(ref => `<li>${ref}</li>`).join('')}
        </ul>
      </div>
    </section>

    <!-- RELATED RESOURCES SECTION -->
    <section class="related-resources">
      <div class="container">
        <h3>Related Resources</h3>
        <div class="resources-links">
          ${state.relatedResources.map(resource => `
            <a href="${resource.url}" target="_blank" rel="noopener" class="resource-link">
              ${resource.title} ↗
            </a>
          `).join('')}
        </div>
      </div>
    </section>

    <!-- CTA SECTION -->
    <section class="state-cta">
      <div class="container">
        <h2>Ready to Start Your Driveway Project?</h2>
        <p>Get free quotes from top-rated ${state.name} driveway contractors</p>
        <button class="cta-button" onclick="showQuoteForm()">Get Free Quotes</button>
      </div>
    </section>
  `;
  
  const appElement = document.getElementById('app');
  if (appElement) {
    appElement.innerHTML = contentHTML;
  }
  document.title = `Driveway Contractors in ${state.name} - Drivewayz USA`;
}

// ============================================
// INITIALIZATION
// ============================================

document.addEventListener('DOMContentLoaded', function() {
  // Smooth scroll for nav links
  const navLinks = document.querySelectorAll('.nav-links a, .guide-link');
  
  navLinks.forEach(link => {
    link.addEventListener('click', function(e) {
      const href = this.getAttribute('href');
      
      if (href.startsWith('#')) {
        e.preventDefault();
        const targetId = href.substring(1);
        const targetSection = document.getElementById(targetId);
        
        if (targetSection) {
          const navbarHeight = document.querySelector('.navbar')?.offsetHeight || 0;
          const targetPosition = targetSection.offsetTop - navbarHeight - 20;
          
          window.scrollTo({
            top: targetPosition,
            behavior: 'smooth'
          });
        }
      }
    });
  });
  
  // Render page based on URL
  renderPage();

    // Handle hash scroll from external pages (e.g., /locations/ -> /#why-choose)
  if (window.location.hash) {
    setTimeout(function() {
      var targetId = window.location.hash.substring(1);
      var targetSection = document.getElementById(targetId);
      if (targetSection) {
        var navbarHeight = document.querySelector('.navbar') ? document.querySelector('.navbar').offsetHeight : 0;
        var targetPosition = targetSection.offsetTop - navbarHeight - 20;
        window.scrollTo({ top: targetPosition, behavior: 'smooth' });
      }
    }, 300);
  }
});

