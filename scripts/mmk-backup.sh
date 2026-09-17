#!/usr/bin/env bash

set -e

MMK_ROOT="$HOME/MMK"
BACKUP_DIR="$HOME/MMK/backups"
TIMESTAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP_FILE="$BACKUP_DIR/MMK-backup-$TIMESTAMP.tar.gz"

mkdir -p "$BACKUP_DIR"

echo "=============================="
echo "       MMK BACKUP"
echo "=============================="

echo
echo "Source:"
echo "$MMK_ROOT"

echo
echo "Creating backup..."

tar -czf "$BACKUP_FILE" \
  --exclude='.git' \
  --exclude='*/.git' \
  --exclude='.env' \
  --exclude='*/.env' \
  --exclude='.env.*' \
  --exclude='*/.env.*' \
  --exclude='*.db' \
  --exclude='*/BACKUPS' \
  --exclude='BACKUPS' \
  --exclude='backups' \
  --exclude='*/backups' \
  --exclude='*.backup*' \
  --exclude='__pycache__' \
  --exclude='*/__pycache__' \
  --exclude='.termux' \
  --exclude='*.log' \
  --exclude='private' \
  --exclude='*/private' \
  -C "$HOME" MMK

echo
echo "Backup created:"
echo "$BACKUP_FILE"

echo
echo "Backup size:"
du -h "$BACKUP_FILE"

echo
echo "MMK BACKUP COMPLETE"
