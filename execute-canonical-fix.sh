#!/bin/bash
set -e

echo "=== STEP 1: Running fix-canonicals.py ==="
cd /Users/matthill/Desktop/drivewayz-usa
python3 fix-canonicals.py

echo ""
echo "=== STEP 2: Git status check ==="
git status --short | head -20
echo "... (truncated)"

echo ""
echo "=== STEP 3: Staging changes ==="
git add -A

echo ""
echo "=== STEP 4: Committing ==="
git commit -m "Fix canonical tags: replace septicsystemshq.com with drivewayzusa.co, add trailing slashes, inject missing canonicals for 1018+ guide pages"

echo ""
echo "=== STEP 5: Pushing to main ==="
git push origin main

echo ""
echo "=== STEP 6: Waiting for Cloudflare deploy (30s) ==="
sleep 30

echo ""
echo "=== STEP 7: Verifying deploy ==="
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" https://drivewayzusa.co/for-homeowners/)
if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ SUCCESS: Site returning 200, deploy likely complete"
    echo "✅ CLEARED FOR COMET — Proceed to Google Search Console"
else
    echo "⚠️  Site returned $HTTP_CODE, may still be deploying"
    echo "⏳ Wait 60 seconds and check https://drivewayzusa.co manually"
fi
