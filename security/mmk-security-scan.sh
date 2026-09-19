#!/data/data/com.termux/files/usr/bin/bash

set -u

MMK_ROOT="$HOME/MMK"
cd "$MMK_ROOT" || exit 1

FOUND=0

echo "================================="
echo "      MMK SECURITY SCANNER v0.3"
echo "================================="

echo
echo "[1] Checking secret-file permissions..."

for file in .env .env.local .env.production ai-tools/flux/.env; do
    if [ -f "$file" ]; then
        perms=$(stat -c '%a' "$file")
        if [ "$perms" != "600" ]; then
            echo "WARNING: $file has permissions $perms (expected 600)"
            FOUND=1
        else
            echo "OK: $file permissions are 600."
        fi
    fi
done

echo
echo "[2] Checking protected directories..."

for directory in private private/secrets private/mmk-vault secrets credentials; do
    if [ -d "$directory" ]; then
        perms=$(stat -c '%a' "$directory")
        if [ "$perms" != "700" ]; then
            echo "WARNING: $directory has permissions $perms (expected 700)"
            FOUND=1
        else
            echo "OK: $directory permissions are 700."
        fi
    fi
done

echo
echo "[3] Checking tracked protected files..."

TRACKED_PROTECTED=$(git ls-files | grep -E '(^|/)\.env$|(^|/)\.env\.(local|production)$|(^|/).*\.pem$|(^|/).*\.key$' || true)

if [ -n "$TRACKED_PROTECTED" ]; then
    echo "WARNING: Protected credential/key file is tracked by Git!"
    printf '%s\\n' "$TRACKED_PROTECTED"
    FOUND=1
else
    echo "OK: No tracked protected .env, PEM, or key files found."
    echo "OK: .env.example is allowed as a template."
fi

echo
echo "[4] Checking file contents for common secret patterns..."

CONTENT_FOUND=0

while IFS= read -r -d "" file; do
    case "$file" in
        .git/*|private/*|BACKUPS/*|automation/logs/mmk-security-test/*|*.db|*.png|*.jpg|*.jpeg|*.gif|*.webp|*.zip|*.tar|*.gz|*.enc)
            continue
            ;;
    esac

    if grep -I -n -E         'ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----|sk-[A-Za-z0-9_-]{20,}'         "$file" >/dev/null 2>&1; then
        echo "WARNING: Possible secret detected in: $file"
        CONTENT_FOUND=1
    fi
done < <(find . -type f -print0)

if [ "$CONTENT_FOUND" -eq 0 ]; then
    echo "OK: No common secret patterns found in scanned file contents."
else
    FOUND=1
fi

echo
echo "[5] Checking tracked backup files..."

if git ls-files | grep -E '(^|/)(BACKUPS|backups)/|\.backup(-|$)|\.step.*-backup$' >/dev/null; then
    echo "WARNING: Backup/recovery file is tracked by Git!"
    git ls-files | grep -E '(^|/)(BACKUPS|backups)/|\.backup(-|$)|\.step.*-backup$'
    FOUND=1
else
    echo "OK: No tracked backup/recovery files found."
fi

echo
echo "================================="

if [ "$FOUND" -eq 0 ]; then
    echo "RESULT: MMK SECURITY SCAN PASSED"
    exit 0
else
    echo "RESULT: MMK SECURITY SCAN FAILED"
    exit 1
fi
