#!/data/data/com.termux/files/usr/bin/bash
set -e

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WEBSITE="$ROOT/website"
CONFIG="$WEBSITE/data/site.json"
DEMO="$ROOT/demo/MMK_WORKSHOP"

echo "=== MMK BUSINESS WEBSITE TEMPLATE TEST ==="

test -f "$ROOT/README.md"
echo "PASS: README"

test -f "$ROOT/CUSTOMER-GUIDE.md"
echo "PASS: customer guide"

test -f "$ROOT/VERSION"
echo "PASS: version"

test -f "$WEBSITE/index.html"
echo "PASS: index.html"

test -f "$WEBSITE/script.js"
echo "PASS: script.js"

test -f "$WEBSITE/style.css"
echo "PASS: style.css"

test -f "$CONFIG"
echo "PASS: site.json"

python -m json.tool "$CONFIG" >/dev/null
echo "PASS: site.json valid JSON"

grep -q '"YOUR BUSINESS NAME"' "$CONFIG"
echo "PASS: generic business configuration"

grep -q '"FOUNDER NAME"' "$CONFIG"
echo "PASS: generic founder configuration"

node --check "$WEBSITE/script.js"
echo "PASS: JavaScript syntax"

for section in home about services products gallery projects contact; do
  grep -q "id=\"$section\"" "$WEBSITE/index.html"
  echo "PASS: section $section"
done

test -f "$DEMO/website/data/site.json"
echo "PASS: MMK_WORKSHOP demo"

python -m json.tool "$DEMO/website/data/site.json" >/dev/null
echo "PASS: MMK_WORKSHOP demo JSON"

grep -q '"MMK_WORKSHOP"' "$DEMO/website/data/site.json"
echo "PASS: MMK_WORKSHOP identity"

echo "=== ALL TEMPLATE TESTS PASSED ==="
