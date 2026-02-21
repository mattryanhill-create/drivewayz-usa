#!/bin/bash
# ===========================================
# Inject js/seo.js into all HTML files
# Adds <script src> before </body> tag
# Safe to run multiple times (checks for existing)
# Uses perl instead of sed for macOS compatibility
# ===========================================

echo "Injecting seo.js into HTML files..."

# --- Guide pages (guides/*.html) ---
count=0
for f in guides/*.html; do
  if [ -f "$f" ] && ! grep -q 'js/seo.js' "$f"; then
    perl -pi -e 's|</body>|<script src="../js/seo.js"></script>\n</body>|' "$f"
    count=$((count + 1))
  fi
done
echo "  Guides: $count files updated"

# --- Location pages (locations/*.html) ---
count=0
for f in locations/*.html; do
  if [ -f "$f" ] && ! grep -q 'js/seo.js' "$f"; then
    perl -pi -e 's|</body>|<script src="../js/seo.js"></script>\n</body>|' "$f"
    count=$((count + 1))
  fi
done
echo "  Locations: $count files updated"

# --- Root HTML pages ---
for f in index.html guides-hub.html locations.html; do
  if [ -f "$f" ] && ! grep -q 'js/seo.js' "$f"; then
    perl -pi -e 's|</body>|<script src="js/seo.js"></script>\n</body>|' "$f"
    echo "  Updated: $f"
  fi
done

echo "Done! All HTML files now include js/seo.js"
