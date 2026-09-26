#!/bin/bash

ENVIRONMENT="$1"

case "$ENVIRONMENT" in
    training)
        echo "MMK: Training environment"
        ;;
    staging)
        echo "MMK: Staging environment"
        ;;
    production)
        echo "MMK: Production environment"
        ;;
    *)
        echo "ERROR: Unknown environment"
        exit 1
        ;;
esac

exit 0
