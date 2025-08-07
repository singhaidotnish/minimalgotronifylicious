#!/bin/bash

echo "🔍 Validating minimalgotronifylicious structure..."

# Helper function
check() {
  if [ -e "$1" ]; then
    echo "✅ Found: $1"
  else
    echo "❌ Missing: $1"
    MISSING=1
  fi
}

MISSING=0

# Check backend structure
echo "📦 Checking apps/backend..."
check apps/backend/main.py
check apps/backend/requirements.txt
check apps/backend/pyproject.toml
check apps/backend/src/algomin
check apps/backend/tests

# Check frontend structure
echo "🎨 Checking apps/ui..."
check apps/ui/package.json
check apps/ui/app/page.tsx
check apps/ui/components
check apps/ui/public
check apps/ui/src

# Check top-level files
echo "📁 Checking root files..."
check README.md
check minimalgotronifylicious_architecture.png

if [ "$1" == "--strict" ] && [ $MISSING -ne 0 ]; then
  echo "🚨 One or more files are missing. Exiting with code 1 (strict mode)."
  exit 1
else
  echo "✅ Structure validation completed."
fi
