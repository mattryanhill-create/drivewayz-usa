#!/usr/bin/env node
/**
 * Fix malformed HTML: stray </nav> that should be </header>
 * Pattern: </div> (nav-container) followed by </nav> followed by <section class="guide-hero">
 */

const fs = require('fs');
const path = require('path');

const GUIDES_DIR = path.join(__dirname, '..', 'guides');

// Match: </div> (nav-container) + stray </nav> + <section class="guide-hero">
const BAD_PATTERN1 = /(\s*<\/div>)\n(<\/nav>)\n(\s*\n<section class="guide-hero">)/;
const BAD_PATTERN2 = /(<\/div><\/nav>)\s*\n(<section class="guide-hero">)/;
const GOOD_REPLACE1 = '$1\n</header>\n$3';
const GOOD_REPLACE2 = '</div></header>\n$2';

function fixFile(filePath) {
  let html = fs.readFileSync(filePath, 'utf8');
  let changed = false;
  if (BAD_PATTERN1.test(html)) {
    html = html.replace(BAD_PATTERN1, GOOD_REPLACE1);
    changed = true;
  }
  if (BAD_PATTERN2.test(html)) {
    html = html.replace(BAD_PATTERN2, GOOD_REPLACE2);
    changed = true;
  }
  if (changed) {
    fs.writeFileSync(filePath, html);
    return true;
  }
  return false;
}

function findGuides(dir, files = []) {
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  for (const e of entries) {
    const full = path.join(dir, e.name);
    if (e.isDirectory()) {
      const idx = path.join(full, 'index.html');
      if (fs.existsSync(idx)) files.push(idx);
      findGuides(full, files);
    }
  }
  return files;
}

const files = findGuides(GUIDES_DIR);
let fixed = 0;
for (const f of files) {
  if (fixFile(f)) fixed++;
}
console.log(`Fixed ${fixed} of ${files.length} guides`);
