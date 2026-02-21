#!/usr/bin/env node
/**
 * Adds crawlable <img> tags to guide hero sections for SEO.
 * 1. Extracts background-image URL from .guide-hero CSS
 * 2. Extracts title (minus " | Drivewayz USA Guides")
 * 3. Inserts <img> as first child of <section class="guide-hero">
 * 4. Fixes iOS bug: background-attachment:fixed → scroll
 * 5. Keeps existing CSS background-image
 */

const fs = require('fs');
const path = require('path');

const GUIDES_DIR = path.join(__dirname, '..', 'guides');

// Regex: url('../images/FILENAME') inside .guide-hero rule
const HERO_IMG_REGEX = /\.guide-hero\s*\{[^}]*url\s*\(\s*'\.\.\/images\/([^']+)'\s*\)/;

// Regex: <title>Topic | Drivewayz USA Guides</title>
const TITLE_REGEX = /<title>([^<]+)<\/title>/;

// Insert after <section class="guide-hero">, before next child
const GUIDE_HERO_SECTION_REGEX = /(<section class="guide-hero">)\s*\n(\s*<div)/;

// Check if img already exists
const HERO_IMG_EXISTS_REGEX = /<img[^>]+class="guide-hero-img"/;

function escapeHtml(str) {
  return str
    .replace(/&/g, '&amp;')
    .replace(/"/g, '&quot;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}

function processFile(filePath) {
  let html = fs.readFileSync(filePath, 'utf8');

  // 1. Extract title, remove " | Drivewayz USA Guides"
  const titleMatch = html.match(TITLE_REGEX);
  if (!titleMatch) {
    return { status: 'error', reason: 'no <title> tag found' };
  }
  const fullTitle = titleMatch[1].trim();
  const topicName = fullTitle.replace(/\s*\|\s*Drivewayz USA Guides\s*$/i, '').trim() || fullTitle;
  const altText = `${topicName} - Drivewayz USA`;

  // 2. Extract background-image filename from .guide-hero CSS
  const heroMatch = html.match(HERO_IMG_REGEX);
  if (!heroMatch) {
    return { status: 'skipped', reason: 'no url(../images/...) in .guide-hero CSS' };
  }
  const filename = heroMatch[1];

  // 4. Fix iOS bug: background-attachment:fixed → scroll (in same inline <style> block)
  const hadFixedAttachment = html.includes('background-attachment:fixed');
  if (hadFixedAttachment) {
    html = html.replace(/background-attachment:fixed/g, 'background-attachment:scroll');
  }

  // 3. Insert img as first child of section.guide-hero
  const imgTag = `<img src="../images/${filename}" alt="${escapeHtml(altText)}" class="guide-hero-img" width="1200" height="630" loading="eager" fetchpriority="high">`;

  if (HERO_IMG_EXISTS_REGEX.test(html)) {
    // Already has img - only apply iOS fix if we changed it
    if (hadFixedAttachment) {
      fs.writeFileSync(filePath, html, 'utf8');
      return { status: 'fixed_only', reason: 'iOS fix applied, img already existed' };
    }
    return { status: 'skipped', reason: 'img already exists' };
  }

  const sectionMatch = html.match(GUIDE_HERO_SECTION_REGEX);
  if (!sectionMatch) {
    return { status: 'error', reason: 'no <section class="guide-hero"> found' };
  }

  const newHtml = html.replace(GUIDE_HERO_SECTION_REGEX, (_, openTag, nextDiv) => {
    return `${openTag}\n  ${imgTag}\n${nextDiv}`;
  });

  fs.writeFileSync(filePath, newHtml, 'utf8');
  return { status: 'updated', filename };
}

function main() {
  const files = fs.readdirSync(GUIDES_DIR)
    .filter(f => f.endsWith('.html'))
    .map(f => path.join(GUIDES_DIR, f));

  let processed = 0;
  let imgInserted = 0;
  let skipped = 0;
  let fixedOnly = 0;
  const errors = [];

  for (const filePath of files) {
    const result = processFile(filePath);
    const basename = path.basename(filePath);

    if (result.status === 'updated') {
      processed++;
      imgInserted++;
    } else if (result.status === 'fixed_only') {
      processed++;
      fixedOnly++;
    } else if (result.status === 'skipped') {
      skipped++;
    } else {
      errors.push({ file: basename, reason: result.reason });
    }
  }

  console.log('\n=== Summary ===');
  console.log(`Total files processed: ${processed + skipped + errors.length}`);
  console.log(`Total <img> tags inserted: ${imgInserted}`);
  console.log(`Files with iOS fix only (img existed): ${fixedOnly}`);
  console.log(`Files skipped: ${skipped}`);
  if (errors.length > 0) {
    console.log(`\nErrors (${errors.length}):`);
    errors.forEach(({ file, reason }) => console.log(`  ${file}: ${reason}`));
  }
}

main();
