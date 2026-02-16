document.addEventListener('DOMContentLoaded', function() {
    
    const navLinks = document.querySelectorAll('.nav-links a, 
.guide-link');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            
            if (href.startsWith('#')) {
                e.preventDefault();
                const targetId = href.substring(1);
                const targetSection = document.getElementById(targetId);
                
                if (targetSection) {
                    const navbarHeight = 
document.querySelector('.navbar').offsetHeight;
                    "alabama": {
  name: "Alabama",
  abbreviation: "AL",
  // ADD THESE NEW FIELDS:
  introHTML: `<p>Your HTML content here...</p>`,
  drivewayTypes: [
    { title: "Concrete Driveways", description: "..." },
    { title: "Asphalt Driveways", description: "..." }
  ],
  localFacts: [
    { title: "Climate Considerations", description: "..." },
    { title: "Soil Types", description: "..." }
  ],
  references: ["Reference 1", "Reference 2"],
  relatedResources: [
    { title: "Resource Name", url: "https://..." }
  ],
  // KEEP YOUR EXISTING FIELDS:
  cities: [...],
  services: [...],
  averageCost: "...",
  climate: "..."
}

