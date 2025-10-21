#!/bin/bash

###############################################################################
# 💾 Database Backup Script
###############################################################################
# Mục đích: Backup PostgreSQL database
# Cách dùng: ./backup_db.sh
###############################################################################

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Config
DB_NAME="${DB_NAME:-flask_dev}"
DB_USER="${DB_USER:-flask_user}"
BACKUP_DIR="../../backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/${DB_NAME}_${DATE}.sql"

# Create backup directory
mkdir -p "$BACKUP_DIR"

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}💾 Database Backup${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Backup
echo -e "${BLUE}📦 Backing up database: $DB_NAME${NC}"
pg_dump -U "$DB_USER" "$DB_NAME" > "$BACKUP_FILE"

# Compress
echo -e "${BLUE}🗜️  Compressing...${NC}"
gzip "$BACKUP_FILE"

BACKUP_FILE="$BACKUP_FILE.gz"
BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)

echo ""
echo -e "${GREEN}✅ Backup complete!${NC}"
echo -e "   File: ${BLUE}$BACKUP_FILE${NC}"
echo -e "   Size: ${BLUE}$BACKUP_SIZE${NC}"
echo ""

# Cleanup old backups (keep last 7 days)
echo -e "${YELLOW}🧹 Cleaning up old backups (>7 days)...${NC}"
find "$BACKUP_DIR" -name "${DB_NAME}_*.sql.gz" -mtime +7 -delete
echo -e "${GREEN}✅ Cleanup complete${NC}"

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "To restore:"
echo "  gunzip $BACKUP_FILE"
echo "  psql -U $DB_USER $DB_NAME < ${BACKUP_FILE%.gz}"
