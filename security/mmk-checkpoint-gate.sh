#!/data/data/com.termux/files/usr/bin/bash
set -e

cd "$(dirname "$0")/.."

python security/mmk-checkpoint-gate.py "$@"
