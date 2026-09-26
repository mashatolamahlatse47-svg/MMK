#!/bin/bash

ENVIRONMENT="$1"

check_environment() {
    case "$1" in
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
            return 1
            ;;
    esac
}

if [ -z "$ENVIRONMENT" ]; then
    echo "ERROR: Environment is required"
    exit 1
fi

check_environment "$ENVIRONMENT"

if [ $? -ne 0 ]; then
    exit 1
fi

echo "MMK: Environment check completed successfully"
exit 0
