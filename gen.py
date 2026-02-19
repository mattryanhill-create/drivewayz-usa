import os, re

# Read the basalt template as our base
with open("guides/basalt-driveway.html", "r") as f:
    TEMPLATE = f.read()

def make_page(filename, title, meta_desc, breadcrumb, h1, subtitle, meta1, meta2, meta3, primary, primary_light, primary_dark, accent, bg1, bg2, bg3, hg1, hg2, hero_img, hover_bg, active_bg, toc_items, main_content, quick_facts, related_guides):
    css = TEMPLATE.split("<style>")[1].split("</style>")[0]
    # Replace colors
    css = re.sub(r'--guide-primary:#[0-9a-fA-F]+', f'--guide-primary:{primary}', css)
    css = re.sub(r'--guide-primary-light:#[0-9a-fA-F]+', f'--guide-primary-light:{primary_light}', css)
    css = re.sub(r'--guide-primary-dark:#[0-9a-fA-F]+', f'--guide-primary-dark:{primary_dark}', css)
    css = re.sub(r'--guide-accent:#[0-9a-fA-F]+', f'--guide-accent:{accent}', css)
    css = css.replace("#f9fafb 0%,#f3f4f6 50%,#e5e7eb 100%", f"{bg1} 0%,{bg2} 50%,{bg3} 100%")
    css = css.replace("rgba(55,65,81,.85)", hg1).replace("rgba(31,41,55,.85)", hg2)
    css = css.replace("pexels-pixabay-259588.webp", hero_img)
    css = css.replace("#f3f4f6", hover_bg).replace("#e5e7eb", active_bg)
    
    toc_html = "".join(f'<li><a href="#{tid}" class="toc-link" data-section="{tid}">{tlabel}</a></li>' for tid, tlabel in toc_items)
    
    qf_html = "".join(f'<div class="quick-stat"><span class="quick-stat-label">{ql}</span><span class="quick-stat-value">{qv}</span></div>' for ql, qv in quick_facts)
    
    rg_html = "".join(f'<a href="{rfile}" class="related-guide"><div class="related-guide-icon">{ricon}</div><div class="related-guide-content"><h5>{rname}</h5><span>{rtime}</span></div></a>' for rfile, ricon, rname, rtime in related_guides)
    
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="description" content="{meta_desc}">
    <link rel="stylesheet" href="../main.css">
    <style>{css}</style>
</head>
<body>
    <nav class="navbar" id="navbar"><div class="container nav-container"><div class="logo"><a href="../index.html"><img src="../logov3.jpg" alt="Drivewayz USA" onerror="this.style.display=&apos;none&apos;"></a></div><ul class="nav-links"><li><a href="../index.html">Home</a></li><li><a href="../index.html#services">Services</a></li><li><a href="../index.html#why-choose">Why Us</a></li><li><a href="../locations.html">Locations</a></li><li><a href="../guides-hub.html">Guides</a></li><li><a href="../index.html#contact">Contact</a></li></ul><a href="../index.html#contact" class="cta-button-sm">Free Estimate</a></div></nav>

    <section class="guide-hero"><div class="container"><div class="guide-hero-content"><div class="guide-breadcrumb"><a href="../index.html">Home</a> / <a href="../guides-hub.html">Guides</a> / <span>{breadcrumb}</span></div><h1>{h1}</h1><p class="guide-hero-subtitle">{subtitle}</p><div class="guide-meta-bar"><div class="guide-meta-item">{meta1}</div><div class="guide-meta-item">{meta2}</div><div class="guide-meta-item">{meta3}</div></div><div class="guide-actions"><a href="../index.html#contact" class="action-btn action-btn-primary">Get Free Estimate</a><button class="action-btn action-btn-secondary" onclick="saveGuide()"><span id="saveIcon">&#128278;</span> <span id="saveText">Save Guide</span></button></div></div></div></section>

    <div class="toc-mobile-toggle" onclick="toggleMobileToc()">&#128203; Table of Contents <span>&#9660;</span></div>

    <div class="guide-page-layout">
        <aside class="toc-sidebar-col"><div class="toc-sidebar"><div class="toc-progress"><div class="toc-progress-bar" id="tocProgress"></div></div><h4>On This Page</h4><ul>{toc_html}</ul></div></aside>

        <main class="guide-main">{main_content}</main>

        <aside class="guide-sidebar-col"><div class="guide-sidebar">
            <div class="sidebar-card"><h4>&#128202; Quick Facts</h4>{qf_html}</div>
            <div class="sidebar-card sidebar-cta"><h4>&#128640; Get Started Today</h4><p>Ready to transform your driveway? Get a free estimate from our experts.</p><form onsubmit="handleSidebarSubmit(event)"><input type="text" placeholder="Your Name" required aria-label="Your Name"><input type="tel" placeholder="Phone Number" required aria-label="Phone Number"><button type="submit">Request Free Estimate</button></form></div>
            <div class="sidebar-card"><h4>&#128218; Related Guides</h4>{rg_html}</div>
        </div></aside>
    </div>

    <footer style="text-align:center;padding:2rem;color:var(--text-light);font-size:.9rem;margin-top:2rem"><p>&copy; 2026 Drivewayz USA. Licensed &amp; Insured. Serving the United States with Pride.</p><p><a href="../index.html#services">Services</a> &bull; <a href="../guides-hub.html">Guides</a> &bull; <a href="../index.html#contact">Contact</a></p></footer>

    <script src="../main.js"></script>
    <script>
document.addEventListener('DOMContentLoaded',function(){{var sections=document.querySelectorAll('main section[id]');var tocLinks=document.querySelectorAll('.toc-link');var progressBar=document.getElementById('tocProgress');window.addEventListener('scroll',function(){{var winH=document.documentElement.scrollHeight-window.innerHeight;var scrolled=(window.scrollY/winH)*100;if(progressBar)progressBar.style.width=scrolled+'%'}});var observer=new IntersectionObserver(function(entries){{entries.forEach(function(entry){{if(entry.isIntersecting){{tocLinks.forEach(function(link){{link.classList.remove('active')}});var activeLink=document.querySelector('.toc-link[data-section="'+entry.target.id+'"]');if(activeLink)activeLink.classList.add('active')}}})}},{{rootMargin:'-20% 0px -60% 0px',threshold:0}});sections.forEach(function(section){{observer.observe(section)}});tocLinks.forEach(function(link){{link.addEventListener('click',function(e){{e.preventDefault();var target=document.getElementById(this.getAttribute('data-section'));if(target){{target.scrollIntoView({{behavior:'smooth',block:'start'}});var mobileToc=document.querySelector('.toc-sidebar-col');var toggle=document.querySelector('.toc-mobile-toggle');if(mobileToc)mobileToc.classList.remove('mobile-open');if(toggle)toggle.classList.remove('open')}}}})}})}});
function toggleMobileToc(){{var tocCol=document.querySelector('.toc-sidebar-col');var toggle=document.querySelector('.toc-mobile-toggle');tocCol.classList.toggle('mobile-open');toggle.classList.toggle('open')}}
function toggleFaq(btn){{btn.parentElement.classList.toggle('open')}}
function saveGuide(){{var si=document.getElementById('saveIcon'),st=document.getElementById('saveText');if(st.textContent==='Save Guide'){{si.innerHTML='&#10084;&#65039;';st.textContent='Saved!'}}else{{si.innerHTML='&#128278;';st.textContent='Save Guide'}}}}
function handleSidebarSubmit(e){{e.preventDefault();alert('Thank you! We will contact you shortly with your free estimate.');e.target.reset()}}
    </script>
</body>
</html>'''

print("Template engine ready. Generating pages...")
