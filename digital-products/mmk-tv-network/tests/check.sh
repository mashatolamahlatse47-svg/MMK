#!/data/data/com.termux/files/usr/bin/sh
set -eu

test -s index.html
test -s assets/css/style.css
test -s assets/js/app.js
test -s README.md

grep -q 'id="episodes"' index.html
grep -q 'id="community"' index.html
grep -q 'id="contact"' index.html
grep -q 'assets/css/style.css' index.html
grep -q 'assets/js/app.js' index.html
grep -q 'menuToggle' assets/js/app.js

printf 'PASS: required website files exist.\n'
printf 'PASS: episodes, community and contact sections exist.\n'
printf 'PASS: CSS and JavaScript are linked.\n'

grep -q '<title>MMK DONKERHOEK TV NETWORK LETHABONG' index.html
grep -q 'DONKERHOEK TV NETWORK LETHABONG' index.html
grep -q 'MMK long-name branding: mobile-safe layout' assets/css/style.css

printf 'PASS: official page title and brand are present.\n'
printf 'PASS: mobile-safe branding styles are present.\n'
