#!/bin/bash

###############################################################################
# 🧪 Test PostgreSQL Connection
###############################################################################
# Mục đích: Test kết nối PostgreSQL
# Cách dùng: ./test_connection.sh
###############################################################################

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Config
DB_NAME="${DB_NAME:-flask_dev}"
DB_USER="${DB_USER:-flask_user}"

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}🧪 PostgreSQL Connection Test${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Test 1: PostgreSQL installed?
echo -e "${YELLOW}1. Checking PostgreSQL installation...${NC}"
if command -v psql &> /dev/null; then
    echo -e "${GREEN}   ✅ PostgreSQL installed: $(psql --version)${NC}"
else
    echo -e "${RED}   ❌ PostgreSQL not found${NC}"
    exit 1
fi

# Test 2: Service running?
echo -e "${YELLOW}2. Checking PostgreSQL service...${NC}"
if pgrep -x postgres > /dev/null; then
    echo -e "${GREEN}   ✅ PostgreSQL service is running${NC}"
else
    echo -e "${RED}   ❌ PostgreSQL service not running${NC}"
    exit 1
fi

# Test 3: Can connect?
echo -e "${YELLOW}3. Testing connection to postgres database...${NC}"
if psql postgres -c "SELECT 1;" > /dev/null 2>&1; then
    echo -e "${GREEN}   ✅ Can connect to PostgreSQL${NC}"
else
    echo -e "${RED}   ❌ Cannot connect to PostgreSQL${NC}"
    exit 1
fi

# Test 4: Database exists?
echo -e "${YELLOW}4. Checking if database '$DB_NAME' exists...${NC}"
if psql -lqt | cut -d \| -f 1 | grep -qw "$DB_NAME"; then
    echo -e "${GREEN}   ✅ Database '$DB_NAME' exists${NC}"
else
    echo -e "${RED}   ❌ Database '$DB_NAME' not found${NC}"
    exit 1
fi

# Test 5: User exists?
echo -e "${YELLOW}5. Checking if user '$DB_USER' exists...${NC}"
if psql postgres -tAc "SELECT 1 FROM pg_roles WHERE rolname='$DB_USER'" | grep -q 1; then
    echo -e "${GREEN}   ✅ User '$DB_USER' exists${NC}"
else
    echo -e "${RED}   ❌ User '$DB_USER' not found${NC}"
    exit 1
fi

# Test 6: User can connect to database?
echo -e "${YELLOW}6. Testing connection as '$DB_USER' to '$DB_NAME'...${NC}"
if psql -U "$DB_USER" -d "$DB_NAME" -c "SELECT 1;" > /dev/null 2>&1; then
    echo -e "${GREEN}   ✅ Can connect as '$DB_USER'${NC}"
else
    echo -e "${RED}   ❌ Cannot connect as '$DB_USER'${NC}"
    exit 1
fi

# Test 7: Show tables
echo -e "${YELLOW}7. Listing tables...${NC}"
TABLES=$(psql -U "$DB_USER" -d "$DB_NAME" -tAc "\dt" | wc -l)
if [ "$TABLES" -gt 0 ]; then
    echo -e "${GREEN}   ✅ Found $TABLES table(s)${NC}"
    psql -U "$DB_USER" -d "$DB_NAME" -c "\dt"
else
    echo -e "${YELLOW}   ⚠️  No tables found (run migrations?)${NC}"
fi

# Test 8: Database size
echo -e "${YELLOW}8. Database size...${NC}"
SIZE=$(psql -U "$DB_USER" -d "$DB_NAME" -tAc "SELECT pg_size_pretty(pg_database_size('$DB_NAME'));")
echo -e "${GREEN}   ✅ Database size: $SIZE${NC}"

# Test 9: Connection count
echo -e "${YELLOW}9. Active connections...${NC}"
CONNECTIONS=$(psql postgres -tAc "SELECT COUNT(*) FROM pg_stat_activity WHERE datname = '$DB_NAME';")
echo -e "${GREEN}   ✅ Active connections: $CONNECTIONS${NC}"

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ All tests passed!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Show connection string
echo "Connection info:"
echo -e "  ${BLUE}psql -U $DB_USER -d $DB_NAME${NC}"
echo ""
