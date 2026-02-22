#!/usr/bin/env node
/**
 * Fix guide template issues:
 * 1. Replace TOC "What is Basalt?" with actual first h2 from #overview section
 * 2. Replace sidebar CTA "Interested in a basalt driveway?" with neutral text
 */

const fs = require('fs');
const path = require('path');

const GUIDES_DIR = path.join(__dirname, '..', 'guides');

const NEUTRAL_CTA = 'Get a free estimate from our driveway experts.';

function extractFirstH2FromOverview(html) {
  const overviewMatch = html.match(/<section id="overview"[^>]*>[\s\S]*?<h2>([^<]+)<\/h2>/);
  return overviewMatch ? overviewMatch[1].trim() : null;
}

function processFile(filePath) {
  let html = fs.readFileSync(filePath, 'utf8');
  let changed = false;

  // 1. Fix TOC - replace "What is Basalt?" with actual overview h2
  const overviewH2 = extractFirstH2FromOverview(html);
  if (overviewH2 && overviewH2 !== 'What is Basalt?' && html.includes('>What is Basalt?</a>')) {
    const escaped = overviewH2.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/\$/g, '$$$$');
    const before = html;
    html = html.replace(/(<a href="#overview" class="toc-link" data-section="overview">)What is Basalt\?(<\/a>)/g, `$1${escaped}$2`);
    if (html !== before) changed = true;
  }

  // 2. Fix sidebar CTA - basalt driveway -> neutral (keep for basalt-driveway guide)
  const isBasaltGuide = filePath.includes('basalt-driveway/');
  if (!isBasaltGuide && html.includes('basalt driveway')) {
    html = html.replace(/Interested in a basalt driveway\? Get a free estimate from our experts\./g, NEUTRAL_CTA);
    changed = true;
  }

  if (changed) {
    fs.writeFileSync(filePath, html);
    return true;
  }
  return false;
}

function findAllGuides(dir, files = []) {
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  for (const e of entries) {
    const full = path.join(dir, e.name);
    if (e.isDirectory()) {
      const idx = path.join(full, 'index.html');
      if (fs.existsSync(idx)) files.push(idx);
      findAllGuides(full, files);
    }
  }
  return files;
}

const files = findAllGuides(GUIDES_DIR);
let updated = 0;
for (const f of files) {
  try {
    if (processFile(f)) updated++;
  } catch (err) {
    console.error(`Error: ${f}:`, err.message);
  }
}
console.log(`Updated ${updated} of ${files.length} guide files`);
