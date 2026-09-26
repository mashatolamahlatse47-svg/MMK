#!/bin/bash

APP_NAME="MMK DevOps System Check"
PROJECT="MMK"
ENVIRONMENT="training"

echo "$APP_NAME"
echo "======================="
echo "Project: $PROJECT"
echo "Environment: $ENVIRONMENT"
echo

check_file() {
    if [ -f "$1" ]; then
        echo "SUCCESS: $1 exists"
    else
        echo "FAILED: $1 is missing"
    fi
}

echo "Checking required files..."

check_file "notes.txt"
check_file "notes-copy.txt"
check_file "duplicates.txt"

echo
echo "Current directory:"
pwd

echo
echo "Files:"
ls

echo
echo "Date:"
date




