#!/bin/bash
# Code Quality Check Script (similar to ESLint for Python)

echo "🔍 Python Code Quality Checker"
echo "==============================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if tools are installed
check_tool() {
    if ! command -v $1 &> /dev/null; then
        print_error "$1 is not installed. Run: pip install -r requirements-dev.txt"
        return 1
    fi
    return 0
}

# Initialize counters
total_errors=0
total_warnings=0

print_status "Checking if linting tools are available..."

# Check required tools
tools=("black" "flake8" "isort" "mypy" "bandit")
for tool in "${tools[@]}"; do
    if ! check_tool $tool; then
        exit 1
    fi
done

echo ""
print_status "All tools available! Starting code quality checks..."
echo ""

# 1. Black - Code Formatting Check
print_status "Running Black (Code Formatter)..."
if black --check --diff .; then
    print_success "Black: Code formatting is correct"
else
    print_warning "Black: Code formatting issues found. Run 'black .' to fix them."
    ((total_warnings++))
fi
echo ""

# 2. isort - Import Sorting Check
print_status "Running isort (Import Sorting)..."
if isort --check-only --diff .; then
    print_success "isort: Import sorting is correct"
else
    print_warning "isort: Import sorting issues found. Run 'isort .' to fix them."
    ((total_warnings++))
fi
echo ""

# 3. Flake8 - Python Linting
print_status "Running Flake8 (Python Linter)..."
flake8_output=$(flake8 . 2>&1)
if [ $? -eq 0 ]; then
    print_success "Flake8: No linting errors found"
else
    print_error "Flake8: Linting errors found:"
    echo "$flake8_output"
    ((total_errors++))
fi
echo ""

# 4. mypy - Type Checking
print_status "Running mypy (Type Checker)..."
mypy_output=$(mypy . 2>&1)
if [ $? -eq 0 ]; then
    print_success "mypy: Type checking passed"
else
    print_warning "mypy: Type checking issues found:"
    echo "$mypy_output"
    ((total_warnings++))
fi
echo ""

# 5. Bandit - Security Linting
print_status "Running Bandit (Security Linter)..."
bandit_output=$(bandit -r . -f txt --configfile .bandit.yaml 2>&1)
if [ $? -eq 0 ]; then
    print_success "Bandit: No security issues found"
else
    print_warning "Bandit: Security issues found:"
    echo "$bandit_output"
    ((total_warnings++))
fi
echo ""

# Summary
echo "==============================="
print_status "Code Quality Check Summary"
echo "==============================="

if [ $total_errors -eq 0 ] && [ $total_warnings -eq 0 ]; then
    print_success "🎉 All checks passed! Your code quality is excellent!"
    exit 0
elif [ $total_errors -eq 0 ]; then
    print_warning "⚠️  Code passed with $total_warnings warning(s). Consider fixing them."
    exit 0
else
    print_error "❌ Code quality check failed with $total_errors error(s) and $total_warnings warning(s)"
    print_error "Please fix the errors before committing."
    exit 1
fi
