#!/data/data/com.termux/files/usr/bin/bash

set -e

MMK_ROOT="$HOME/MMK"
VAULT_DIR="$MMK_ROOT/private/mmk-vault"
PROTECTED_DIR="$MMK_ROOT/protected-products"

ARCHIVE="$VAULT_DIR/MMK-PRODUCTS.tar.gz"
ENCRYPTED="$PROTECTED_DIR/MMK-PRODUCTS.enc"
RESTORE_DIR="$VAULT_DIR/restore"

echo "================================"
echo "        MMK PRODUCT VAULT"
echo "================================"

case "${1:-status}" in

  lock)
    echo "[1/3] Creating product archive..."
    rm -f "$ARCHIVE"

    tar -czf "$ARCHIVE" \
      --exclude='digital-products/mmk-business-starter/.git' \
      digital-products/mmk-business-starter \
      mmk-product-factory/website/stock-calculator \
      mmk-product-factory/data/products.json

    echo "[2/3] Encrypting product archive..."
    openssl enc -aes-256-cbc -salt -pbkdf2 -iter 600000 \
      -in "$ARCHIVE" \
      -out "$ENCRYPTED"

    chmod 600 "$ENCRYPTED"

    echo "[3/3] Removing temporary plaintext archive..."
    rm -f "$ARCHIVE"

    echo
    echo "MMK PRODUCTS LOCKED."
    echo "Protected file:"
    ls -lh "$ENCRYPTED"
    ;;

  unlock)
    echo "[1/3] Preparing restore directory..."
    rm -rf "$RESTORE_DIR"
    mkdir -p "$RESTORE_DIR"

    echo "[2/3] Decrypting protected products..."
    TEMP_ARCHIVE="$RESTORE_DIR/MMK-PRODUCTS.tar.gz"

    openssl enc -d -aes-256-cbc -pbkdf2 -iter 600000 \
      -in "$ENCRYPTED" \
      -out "$TEMP_ARCHIVE"

    echo "[3/3] Restoring product files..."
    tar -xzf "$TEMP_ARCHIVE" -C "$RESTORE_DIR"

    rm -f "$TEMP_ARCHIVE"

    echo
    echo "MMK PRODUCTS UNLOCKED INTO:"
    echo "$RESTORE_DIR"
    ;;

  status)
    echo "Protected vault:"
    if [ -f "$ENCRYPTED" ]; then
      ls -lh "$ENCRYPTED"
      echo "STATUS: LOCKED VAULT EXISTS"
    else
      echo "STATUS: NO ENCRYPTED VAULT FOUND"
    fi
    ;;

  *)
    echo "Usage:"
    echo "  ./security/mmk-vault.sh lock"
    echo "  ./security/mmk-vault.sh unlock"
    echo "  ./security/mmk-vault.sh status"
    exit 1
    ;;

esac
