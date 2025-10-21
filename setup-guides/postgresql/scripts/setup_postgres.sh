#!/bin/bash

###############################################################################
# 🐘 PostgreSQL Auto Setup Script
###############################################################################
# Mục đích: Tự động setup PostgreSQL cho Flask app
# Cách dùng: ./setup_postgres.sh
###############################################################################

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
DB_NAME="${DB_NAME:-flask_dev}"
DB_USER="${DB_USER:-flask_user}"
DB_PASSWORD="${DB_PASSWORD:-flask_password_123}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"

###############################################################################
# Functions
###############################################################################

print_header() {
    echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

###############################################################################
# Step 1: Check PostgreSQL Installation
###############################################################################

print_header "Bước 1: Kiểm tra PostgreSQL"

if ! command -v psql &> /dev/null; then
    print_error "PostgreSQL chưa được cài đặt!"
    print_info "Cài đặt PostgreSQL:"
    echo "  brew install postgresql@15"
    echo "  brew services start postgresql@15"
    exit 1
fi

print_success "PostgreSQL đã cài đặt: $(psql --version)"

###############################################################################
# Step 2: Check PostgreSQL Service
###############################################################################

print_header "Bước 2: Kiểm tra PostgreSQL Service"

if brew services list | grep postgresql | grep started &> /dev/null; then
    print_success "PostgreSQL service đang chạy"
elif pgrep -x postgres > /dev/null; then
    print_success "PostgreSQL đang chạy (Postgres.app)"
else
    print_warning "PostgreSQL service không chạy"
    print_info "Đang khởi động PostgreSQL..."
    brew services start postgresql@15
    sleep 3
    print_success "PostgreSQL đã khởi động"
fi

###############################################################################
# Step 3: Create Database User
###############################################################################

print_header "Bước 3: Tạo Database User"

# Check if user exists
if psql postgres -tAc "SELECT 1 FROM pg_roles WHERE rolname='$DB_USER'" | grep -q 1; then
    print_warning "User '$DB_USER' đã tồn tại"
    read -p "Bạn có muốn reset password? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        psql postgres -c "ALTER USER $DB_USER WITH PASSWORD '$DB_PASSWORD';" > /dev/null
        print_success "Password đã được reset"
    fi
else
    print_info "Đang tạo user '$DB_USER'..."
    psql postgres -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';" > /dev/null
    print_success "User '$DB_USER' đã được tạo"
fi

###############################################################################
# Step 4: Create Database
###############################################################################

print_header "Bước 4: Tạo Database"

# Check if database exists
if psql -lqt | cut -d \| -f 1 | grep -qw "$DB_NAME"; then
    print_warning "Database '$DB_NAME' đã tồn tại"
    read -p "Bạn có muốn xóa và tạo lại? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Terminate connections
        psql postgres -c "SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE pg_stat_activity.datname = '$DB_NAME' AND pid <> pg_backend_pid();" > /dev/null

        # Drop and recreate
        dropdb "$DB_NAME" > /dev/null
        createdb "$DB_NAME" > /dev/null
        print_success "Database '$DB_NAME' đã được tạo lại"
    fi
else
    print_info "Đang tạo database '$DB_NAME'..."
    createdb "$DB_NAME" > /dev/null
    print_success "Database '$DB_NAME' đã được tạo"
fi

###############################################################################
# Step 5: Grant Permissions
###############################################################################

print_header "Bước 5: Cấp quyền"

print_info "Đang cấp quyền cho '$DB_USER' trên '$DB_NAME'..."

psql postgres -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;" > /dev/null
psql "$DB_NAME" -c "GRANT ALL ON SCHEMA public TO $DB_USER;" > /dev/null

print_success "Quyền đã được cấp"

###############################################################################
# Step 6: Create .env.local
###############################################################################

print_header "Bước 6: Tạo file .env.local"

ENV_FILE="../../.env.local"

if [ -f "$ENV_FILE" ]; then
    print_warning ".env.local đã tồn tại"
    read -p "Bạn có muốn backup và tạo mới? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cp "$ENV_FILE" "$ENV_FILE.backup.$(date +%Y%m%d_%H%M%S)"
        print_success "Đã backup file cũ"
    else
        print_info "Giữ nguyên file .env.local hiện tại"
        ENV_FILE=""
    fi
fi

if [ -n "$ENV_FILE" ]; then
    cat > "$ENV_FILE" <<EOF
# PostgreSQL Local Configuration
# Auto-generated by setup_postgres.sh

# Database URL
DATABASE_URL=postgresql://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/$DB_NAME

# Flask Settings
FLASK_ENV=development
FLASK_DEBUG=1

# Security Keys (CHANGE THESE IN PRODUCTION!)
SECRET_KEY=dev-secret-key-$(openssl rand -hex 16)
JWT_SECRET_KEY=dev-jwt-secret-$(openssl rand -hex 16)

# Optional: Override host/port
# FLASK_HOST=0.0.0.0
# FLASK_PORT=8888
EOF
    print_success ".env.local đã được tạo"
fi

###############################################################################
# Step 7: Run Migrations
###############################################################################

print_header "Bước 7: Chạy Database Migrations"

cd ../..

# Export environment variables
export $(grep -v '^#' .env.local | xargs)

if [ ! -d "migrations" ]; then
    print_info "Khởi tạo migrations..."
    flask db init
    print_success "Migrations đã được khởi tạo"
fi

print_info "Tạo migration scripts..."
flask db migrate -m "Initial migration with PostgreSQL" || print_warning "Không có thay đổi mới"

print_info "Áp dụng migrations..."
flask db upgrade

print_success "Migrations đã hoàn thành"

###############################################################################
# Step 8: Test Connection
###############################################################################

print_header "Bước 8: Test kết nối"

print_info "Đang test kết nối..."

if psql -U "$DB_USER" -d "$DB_NAME" -c "SELECT 1;" > /dev/null 2>&1; then
    print_success "Kết nối thành công!"
else
    print_error "Không thể kết nối!"
    exit 1
fi

# Show tables
print_info "Tables trong database:"
psql -U "$DB_USER" -d "$DB_NAME" -c "\dt"

###############################################################################
# Summary
###############################################################################

print_header "🎉 Setup Hoàn Thành!"

echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ PostgreSQL Setup Summary${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "  Database:     ${BLUE}$DB_NAME${NC}"
echo -e "  User:         ${BLUE}$DB_USER${NC}"
echo -e "  Password:     ${BLUE}$DB_PASSWORD${NC}"
echo -e "  Host:         ${BLUE}$DB_HOST${NC}"
echo -e "  Port:         ${BLUE}$DB_PORT${NC}"
echo ""
echo -e "  Connection:   ${BLUE}postgresql://$DB_USER:***@$DB_HOST:$DB_PORT/$DB_NAME${NC}"
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

###############################################################################
# Next Steps
###############################################################################

print_header "📚 Next Steps"

echo "1️⃣  Kết nối vào database:"
echo "    psql -U $DB_USER -d $DB_NAME"
echo ""
echo "2️⃣  Start Flask app:"
echo "    export \$(cat .env.local | xargs)"
echo "    python app.py"
echo ""
echo "3️⃣  Test API:"
echo "    curl http://localhost:8888/health"
echo ""
echo "4️⃣  View data:"
echo "    psql -U $DB_USER -d $DB_NAME -c 'SELECT * FROM users;'"
echo ""

print_success "Happy coding! 🚀"
