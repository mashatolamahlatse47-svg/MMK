#!/data/data/com.termux/files/usr/bin/bash
set -eu
test -s index.html
grep -q 'saveProduct' index.html
grep -q 'id="send"' index.html
grep -q 'function persist' index.html
grep -q 'function loadShop' index.html
test -s README.md
test -s SELLING-GUIDE.md
echo "MMK CHECK: PASS"
