#!/data/data/com.termux/files/usr/bin/bash

echo "================================="
echo "       MMK SECURITY CHECK"
echo "================================="

FOUND=0

echo
echo "[1] Checking tracked files for common secrets..."

if git grep -n -I -E 'ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----' -- ':!scripts/security-check.sh'; then
    FOUND=1
fi

echo
echo "[2] Checking protected files..."

if git ls-files --error-unmatch .env >/dev/null 2>&1; then
    echo "WARNING: .env is tracked by Git!"
    FOUND=1
else
    echo "OK: .env is NOT tracked."
fi

echo
echo "[3] Checking private directory..."

if git ls-files private/ | grep -q .; then
    echo "WARNING: private/ contains tracked files!"
    FOUND=1
else
    echo "OK: private/ is NOT tracked."
fi

echo
echo "================================="

if [ "$FOUND" -eq 0 ]; then
    echo "RESULT: MMK SECURITY CHECK PASSED"
    echo "Safe to continue reviewing your Git changes."
    exit 0
else
    echo "RESULT: WARNING - CHECK FAILED"
    echo "Do NOT push until the problem is investigated."
    exit 1
fi
