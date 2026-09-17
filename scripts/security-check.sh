#!/data/data/com.termux/files/usr/bin/bash

echo "================================="
echo "       MMK SECURITY CHECK"
echo "================================="

FOUND=0

echo
echo "[1] Checking tracked files for common secrets..."

if git grep -n -I -E \
'ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----|sk-[A-Za-z0-9_-]{20,}' \
-- ':!scripts/security-check.sh'; then
    FOUND=1
else
    echo "OK: No common secret patterns found in tracked files."
fi

echo
echo "[2] Checking protected files..."

for file in .env .env.local .env.production; do
    if git ls-files --error-unmatch "$file" >/dev/null 2>&1; then
        echo "WARNING: $file is tracked by Git!"
        FOUND=1
    fi
done

if [ "$FOUND" -eq 0 ]; then
    echo "OK: Protected environment files are not tracked."
fi

echo
echo "[3] Checking protected directories..."

for directory in private/ secrets/ credentials/; do
    if git ls-files "$directory" | grep -q .; then
        echo "WARNING: $directory contains tracked files!"
        FOUND=1
    else
        echo "OK: $directory is not tracked."
    fi
done

echo
echo "[4] Checking tracked backup files..."

if git ls-files | grep -E '(^|/)(BACKUPS|backups)/|\.backup(-|$)|\.step.*-backup$' >/dev/null; then
    echo "WARNING: Backup/recovery files are tracked by Git!"
    git ls-files | grep -E '(^|/)(BACKUPS|backups)/|\.backup(-|$)|\.step.*-backup$'
    FOUND=1
else
    echo "OK: No tracked backup/recovery files found."
fi

echo
echo "[5] Checking suspicious credential filenames..."

if git ls-files | grep -Ei '(^|/)(credentials?|passwords?|tokens?|secrets?)(\.[^/]*)?$' >/dev/null; then
    echo "WARNING: Suspicious credential-related filename detected:"
    git ls-files | grep -Ei '(^|/)(credentials?|passwords?|tokens?|secrets?)(\.[^/]*)?$'
    FOUND=1
else
    echo "OK: No suspicious credential filenames found."
fi

echo
echo "[6] Checking repository metadata..."

if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "OK: Git repository detected."
else
    echo "WARNING: Not inside a Git repository."
    FOUND=1
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
