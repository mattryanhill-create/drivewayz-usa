#!/usr/bin/env node
/**
 * Apply performance & design standards across all HTML pages:
 * 1. Add preconnect for googletagmanager.com
 * 2. Update logo to optimized picture/srcset (WebP + responsive)
 * 3. Update hero-driveway to optimized srcset
 */

const fs = require('fs');
const path = require('path');

const OPTIMIZED_LOGO = `<picture><source srcset="/images/logov3-640.webp 640w, /images/logov3-1280.webp 1280w" type="image/webp"><img src="/images/logov3-640.png" srcset="/images/logov3-640.png 640w, /images/logov3-800.png 800w" alt="Drivewayz USA" width="1536" height="1024" loading="eager" onerror="this.style.display='none'"></picture>`;

// Logo patterns to replace (without srcset - old format)
const OLD_LOGO_PATTERNS = [
  /<picture><source srcset="\/images\/logov3\.webp" type="image\/webp"><img src="\/images\/logov3\.png(?:\?v=\d+)?" alt="Drivewayz USA" width="1536" height="1024" loading="eager"(?: onerror="this\.style\.display='none'")?><\/picture>/g,
  /<picture><source srcset="\/images\/logov3\.webp" type="image\/webp"><img src="\/images\/logov3\.png(?:\?v=\d+)?" alt="Drivewayz USA" width="1536" height="1024" loading="eager"><\/picture>/g,
];

// Hero picture with unoptimized hero-driveway
const OLD_HERO_PICTURE = /<picture class="hero-bg-picture"[^>]*><source srcset="\/hero-driveway\.webp" type="image\/webp"><img src="\/hero-driveway\.jpg"[^>]*><\/picture>/g;
const OPTIMIZED_HERO_PICTURE = `<picture class="hero-bg-picture" style="position:absolute;inset:0;z-index:0;width:100%;height:100%;margin:0;padding:0;display:block;"><source srcset="/hero-driveway-640.webp 640w, /hero-driveway-1280.webp 1280w" type="image/webp"><img src="/hero-driveway-640.jpg" srcset="/hero-driveway-640.jpg 640w, /hero-driveway-900.jpg 900w" alt="" width="7360" height="4912" loading="eager" fetchpriority="high" style="width:100%;height:100%;object-fit:cover;display:block;"></picture>`;

// Preconnect - insert before gtag script
const PRECONNECT = '<link rel="preconnect" href="https://www.googletagmanager.com">';
const PRECONNECT_NEEDLE = /<script async src="https:\/\/www\.googletagmanager\.com\/gtag\/js/;
const PRECONNECT_EXISTS = /<link rel="preconnect" href="https:\/\/www\.googletagmanager\.com">/;

function findAllHtml(dir, files = []) {
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  for (const e of entries) {
    const full = path.join(dir, e.name);
    if (e.isDirectory()) {
      if (!e.name.startsWith('.') && e.name !== 'node_modules') {
        findAllHtml(full, files);
      }
    } else if (e.name.endsWith('.html')) {
      files.push(full);
    }
  }
  return files;
}

function processFile(filePath) {
  let html = fs.readFileSync(filePath, 'utf8');
  let changed = false;

  // 1. Add preconnect if gtag present and preconnect missing
  if (PRECONNECT_NEEDLE.test(html) && !PRECONNECT_EXISTS.test(html)) {
    html = html.replace(/(\s*)(<script async src="https:\/\/www\.googletagmanager\.com\/gtag\/js)/, `$1${PRECONNECT}\n$1$2`);
    changed = true;
  }

  // 2. Update logo (skip if already optimized)
  if (!html.includes('logov3-640.webp')) {
    for (const pat of OLD_LOGO_PATTERNS) {
      const next = html.replace(pat, OPTIMIZED_LOGO);
      if (next !== html) {
        html = next;
        changed = true;
        break;
      }
    }
  }

  // 3. Update hero-driveway picture (skip if already optimized)
  if (html.includes('/hero-driveway.webp"') && !html.includes('hero-driveway-640.webp')) {
    const next = html.replace(OLD_HERO_PICTURE, OPTIMIZED_HERO_PICTURE);
    if (next !== html) {
      html = next;
      changed = true;
    }
  }

  if (changed) {
    fs.writeFileSync(filePath, html);
    return true;
  }
  return false;
}

const root = path.join(__dirname, '..');
const files = findAllHtml(root);
let updated = 0;
for (const f of files) {
  try {
    if (processFile(f)) updated++;
  } catch (err) {
    console.error(`Error processing ${f}:`, err.message);
  }
}
console.log(`Updated ${updated} of ${files.length} HTML files`);
