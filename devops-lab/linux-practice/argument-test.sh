#!/bin/bash

ENVIRONMENT="$1"

if [ -z "$ENVIRONMENT" ]; then
    echo "ERROR: Environment is required"
    exit 1
fi

if [ "$ENVIRONMENT" != "training" ] &&
   [ "$ENVIRONMENT" != "staging" ] &&
   [ "$ENVIRONMENT" != "production" ]; then
    echo "ERROR: Invalid environment: $ENVIRONMENT"
    echo "Allowed: training, staging, production"
    exit 1
fi

echo "MMK DevOps System"
echo "================="
echo "Environment: $ENVIRONMENT"

exit 0
