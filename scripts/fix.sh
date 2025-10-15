#!/bin/bash
# Auto-fix Code Quality Issues

echo "🔧 Python Code Auto-Fixer"
echo "========================="

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[FIXING]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[FIXED]${NC} $1"
}

# 1. Black - Auto-format code
print_status "Running Black to format code..."
black .
print_success "Code formatted with Black"
echo ""

# 2. isort - Auto-sort imports
print_status "Running isort to sort imports..."
isort .
print_success "Imports sorted with isort"
echo ""

# 3. Remove trailing whitespace and fix line endings
print_status "Fixing trailing whitespace and line endings..."
find . -name "*.py" -type f -exec sed -i '' 's/[[:space:]]*$//' {} \;
print_success "Trailing whitespace removed"
echo ""

print_success "🎉 All auto-fixable issues have been resolved!"
print_status "Run './scripts/lint.sh' to check for remaining issues."
