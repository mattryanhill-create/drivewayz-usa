#!/usr/bin/env node
/**
 * Adds crawlable <img> tags to guide hero sections for SEO and accessibility.
 * Extracts hero image from .guide-hero CSS, generates alt from <title>, inserts
 * <img> after <section class="guide-hero"> and before <div class="container guide-hero-content">.
 * Skips files that use color gradients instead of a photo (no url('/images/...') in CSS).
 */

const fs = require('fs');
const path = require('path');

const GUIDES_DIR = path.join(__dirname, '..', 'guides');
const IMG_PREFIX = '/images/';

// Regex: url('/images/' followed by any chars up to ')  inside .guide-hero rule
const HERO_IMG_REGEX = /\.guide-hero\s*\{[^}]*url\s*\(\s*'\.\.\/images\/([^']+)'\s*\)/;

// Regex: <title>...</title>
const TITLE_REGEX = /<title>([^<]+)<\/title>/;

// Insert after <section class="guide-hero">, before <div class="container guide-hero-content">
const GUIDE_HERO_SECTION_REGEX = /(<section class="guide-hero">)\s*\n(\s*<div class="container guide-hero-content">)/;

// Skip inserting if img already exists
const HERO_IMG_EXISTS_REGEX = /<img[^>]+class="guide-hero-img"/;

function processFile(filePath) {
  let html = fs.readFileSync(filePath, 'utf8');

  // Extract page title first (needed for both insert and update)
  const titleMatch = html.match(TITLE_REGEX);
  if (!titleMatch) {
    return { status: 'error', reason: 'no <title> tag found' };
  }
  const fullTitle = titleMatch[1].trim();
  const titleText = fullTitle.split(' | ')[0].trim() || fullTitle;
  const altText = `${titleText} — Drivewayz USA`;

  // If img already exists, update alt attribute to new format
  const existingImgMatch = html.match(/<img[^>]+class="guide-hero-img"[^>]*>/);
  if (existingImgMatch) {
    const oldAltMatch = existingImgMatch[0].match(/alt="([^"]*)"/);
    if (oldAltMatch && oldAltMatch[1] !== altText) {
      const newImgTag = existingImgMatch[0].replace(/alt="[^"]*"/, `alt="${escapeHtml(altText)}"`);
      html = html.replace(existingImgMatch[0], newImgTag);
      fs.writeFileSync(filePath, html, 'utf8');
      return { status: 'updated', filename: 'alt-only' };
    }
    return { status: 'skipped', reason: 'img already exists' };
  }

  // Extract hero image filename from CSS - skip files with gradient-only (no url)
  const heroMatch = html.match(HERO_IMG_REGEX);
  if (!heroMatch) {
    return { status: 'skipped', reason: 'no hero image in .guide-hero CSS (gradient only)' };
  }
  const filename = heroMatch[1];

  // Build img tag
  const imgTag = `<img src="${IMG_PREFIX}${filename}" alt="${escapeHtml(altText)}" class="guide-hero-img" width="1200" height="630" loading="eager" fetchpriority="high">`;

  // Insert img after <section class="guide-hero">, before <div class="container guide-hero-content">
  const sectionMatch = html.match(GUIDE_HERO_SECTION_REGEX);
  if (!sectionMatch) {
    return { status: 'error', reason: 'no <section class="guide-hero"> or guide-hero-content div found' };
  }

  // Use function form of replace to avoid $ in alt text (e.g. $10000) being interpreted as capture group
  const newHtml = html.replace(GUIDE_HERO_SECTION_REGEX, (_, openTag, nextDiv) => {
    return `${openTag}\n  ${imgTag}\n${nextDiv}`;
  });

  fs.writeFileSync(filePath, newHtml, 'utf8');
  return { status: 'updated', filename };
}

function escapeHtml(str) {
  return str
    .replace(/&/g, '&amp;')
    .replace(/"/g, '&quot;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}

function main() {
  const files = fs.readdirSync(GUIDES_DIR)
    .filter(f => f.endsWith('.html'))
    .map(f => path.join(GUIDES_DIR, f));

  let updated = 0;
  let skippedNoImg = 0;
  let skippedExisting = 0;
  let errors = [];

  for (const filePath of files) {
    const result = processFile(filePath);
    const basename = path.basename(filePath);

    if (result.status === 'updated') {
      updated++;
      console.log(`Updated: ${basename}`);
    } else if (result.status === 'skipped') {
      if (result.reason.includes('gradient')) {
        skippedNoImg++;
        console.log(`Skipped (no hero image): ${basename}`);
      } else {
        skippedExisting++;
      }
    } else {
      errors.push({ file: basename, reason: result.reason });
    }
  }

  if (errors.length > 0) {
    console.error('\nErrors:');
    errors.forEach(({ file, reason }) => console.error(`  ${file}: ${reason}`));
  }

  console.log(`\nDone. Updated: ${updated}, Skipped (no image): ${skippedNoImg}, Skipped (already has img): ${skippedExisting}, Errors: ${errors.length}`);
  process.exit(errors.length > 0 ? 1 : 0);
}

main();
