#!/bin/bash
#
# CLCL Quick Setup - Run this on your Mac
# One command to activate everything
#

set -e

echo "=================================="
echo "CLCL Quick Setup"
echo "=================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Step 1: Install dependency
echo -e "${YELLOW}Step 1: Installing imapclient...${NC}"
pip3 install --quiet imapclient
echo -e "${GREEN}✓ Done${NC}"

# Step 2: Create directories
echo -e "${YELLOW}Step 2: Creating directories...${NC}"
mkdir -p ~/ERA_Admin/clcl_inbox
mkdir -p ~/Library/LaunchAgents
echo -e "${GREEN}✓ Done${NC}"

# Step 3: Get App Password
echo ""
echo -e "${YELLOW}Step 3: App Password needed${NC}"
echo ""
echo "You need a Google App Password for claude@ecorestorationalliance.org"
echo ""
echo "If you don't have one:"
echo "  1. Go to https://myaccount.google.com/apppasswords"
echo "  2. Create one for 'Mail'"
echo "  3. Copy the 16-character password"
echo ""
read -p "Paste your App Password (or press Enter to skip): " APP_PASSWORD

if [ -n "$APP_PASSWORD" ]; then
    # Save to environment
    echo "export CLCL_APP_PASSWORD='$APP_PASSWORD'" >> ~/.zshrc
    echo "export CLCL_EMAIL='claude@ecorestorationalliance.org'" >> ~/.zshrc
    export CLCL_APP_PASSWORD="$APP_PASSWORD"
    export CLCL_EMAIL="claude@ecorestorationalliance.org"
    echo -e "${GREEN}✓ Saved to ~/.zshrc${NC}"
else
    echo -e "${YELLOW}! Skipped - set CLCL_APP_PASSWORD later${NC}"
fi

# Step 4: Copy plist
echo -e "${YELLOW}Step 4: Installing launchd service...${NC}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cp "$SCRIPT_DIR/com.era.clcl-listener.plist" ~/Library/LaunchAgents/
echo -e "${GREEN}✓ Done${NC}"

# Step 5: Load service (if password was set)
if [ -n "$APP_PASSWORD" ]; then
    echo -e "${YELLOW}Step 5: Starting CLCL listener...${NC}"
    launchctl load ~/Library/LaunchAgents/com.era.clcl-listener.plist 2>/dev/null || true
    echo -e "${GREEN}✓ CLCL is now running${NC}"
else
    echo -e "${YELLOW}Step 5: Skipped (no password)${NC}"
    echo "  Run: launchctl load ~/Library/LaunchAgents/com.era.clcl-listener.plist"
fi

echo ""
echo "=================================="
echo -e "${GREEN}Setup Complete!${NC}"
echo "=================================="
echo ""
echo "CLCL is listening for [CLCL-WAKE] emails."
echo ""
echo "Test it by emailing claude@ecorestorationalliance.org"
echo "with subject: [CLCL-WAKE] Hello from setup"
echo ""
echo "GitHub Action Setup (one-time, in browser):"
echo "  1. Go to your repo Settings → Secrets → Actions"
echo "  2. Add CLCL_SMTP_USERNAME (your gmail)"
echo "  3. Add CLCL_SMTP_PASSWORD (app password for that gmail)"
echo ""
