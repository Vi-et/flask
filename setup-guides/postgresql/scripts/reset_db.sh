#!/bin/bash

###############################################################################
# 🔄 Database Reset Script
###############################################################################
# Mục đích: Xóa và tạo lại database (NGUY HIỂM!)
# Cách dùng: ./reset_db.sh
###############################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Config
DB_NAME="${DB_NAME:-flask_dev}"
DB_USER="${DB_USER:-flask_user}"

echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${RED}⚠️  DATABASE RESET WARNING ⚠️${NC}"
echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${YELLOW}This will DELETE ALL DATA in database: ${RED}$DB_NAME${NC}"
echo ""
read -p "Are you SURE? Type 'yes' to continue: " -r
echo ""

if [[ ! $REPLY == "yes" ]]; then
    echo -e "${GREEN}✅ Cancelled. Database unchanged.${NC}"
    exit 0
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}🔄 Resetting Database${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Step 1: Backup (just in case)
echo -e "${YELLOW}📦 Creating backup first...${NC}"
./backup_db.sh || true

# Step 2: Terminate connections
echo -e "${YELLOW}🔌 Terminating active connections...${NC}"
psql postgres -c "SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE pg_stat_activity.datname = '$DB_NAME' AND pid <> pg_backend_pid();" > /dev/null

# Step 3: Drop database
echo -e "${YELLOW}🗑️  Dropping database...${NC}"
dropdb "$DB_NAME" > /dev/null
echo -e "${GREEN}✅ Database dropped${NC}"

# Step 4: Create database
echo -e "${YELLOW}🏗️  Creating database...${NC}"
createdb "$DB_NAME" > /dev/null
echo -e "${GREEN}✅ Database created${NC}"

# Step 5: Grant permissions
echo -e "${YELLOW}🔐 Granting permissions...${NC}"
psql postgres -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;" > /dev/null
psql "$DB_NAME" -c "GRANT ALL ON SCHEMA public TO $DB_USER;" > /dev/null
echo -e "${GREEN}✅ Permissions granted${NC}"

# Step 6: Run migrations
echo -e "${YELLOW}🚀 Running migrations...${NC}"
cd ../..
export $(grep -v '^#' .env.local | xargs)
flask db upgrade
echo -e "${GREEN}✅ Migrations complete${NC}"

# Step 7: Seed data (optional)
if [ -f "seed.py" ]; then
    read -p "Run seed script? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}🌱 Seeding data...${NC}"
        python seed.py
        echo -e "${GREEN}✅ Data seeded${NC}"
    fi
fi

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ Database reset complete!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "Next steps:"
echo "  1. psql -U $DB_USER -d $DB_NAME"
echo "  2. python app.py"
