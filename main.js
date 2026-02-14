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

