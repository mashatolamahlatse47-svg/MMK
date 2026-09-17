#!/usr/bin/env bash

set -e

echo "=============================="
echo "       MMK SYSTEM CHECK"
echo "=============================="

echo
echo "Git:"
git --version

echo
echo "Node:"
node --version

echo
echo "npm:"
npm --version

echo
echo "Python:"
python --version

echo
echo "GitHub CLI:"
gh --version | head -n 1

echo
echo "MMK directory:"
pwd

echo
echo "Git status:"
git status --short

echo
echo "MMK SYSTEM CHECK COMPLETE"
