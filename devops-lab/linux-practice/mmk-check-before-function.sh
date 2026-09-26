#!/bin/bash

APP_NAME="MMK DevOps System Check"
PROJECT="MMK"
ENVIRONMENT="training"

echo "$APP_NAME"
echo "======================="
echo "Project: $PROJECT"
echo "Environment: $ENVIRONMENT"
echo

echo "Checking required files..."

if [ -f "notes.txt" ]; then
    echo "SUCCESS: notes.txt exists"
else
    echo "FAILED: notes.txt is missing"
fi

echo
echo "Current directory:"
pwd

echo
echo "Files:"
ls

echo
echo "Date:"
date


