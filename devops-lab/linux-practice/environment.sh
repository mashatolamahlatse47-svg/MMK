#!/bin/bash

ENVIRONMENT="$1"

show_environment() {
    echo "MMK Environment: $1"
}

case "$ENVIRONMENT" in
    training)
        show_environment "Training"
        ;;
    staging)
        show_environment "Staging"
        ;;
    production)
        show_environment "Production"
        ;;
    *)
        echo "ERROR: Unknown environment"
        exit 1
        ;;
esac

exit 0

