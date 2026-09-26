#!/data/data/com.termux/files/usr/bin/bash
set -e
APP_DIR="$HOME/MMK/software/event-ticketing-qr-pass"
cd "$APP_DIR"
printf '\n[MMK] Event Ticketing installer\n\n'
python -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
printf '\nDependencies installed.\n'
printf 'Set an admin key before starting:\n  export MMK_ADMIN_KEY="replace-with-a-long-random-key"\n  export MMK_PUBLIC_BASE_URL="http://127.0.0.1:5055"\n  python app.py\n\n'
