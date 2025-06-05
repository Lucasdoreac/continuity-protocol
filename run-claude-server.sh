#!/bin/bash
#
# Run Continuity Protocol Server for Claude Desktop
#

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Print banner
echo -e "${BLUE}=======================================${NC}"
echo -e "${BLUE}   Continuity Protocol Claude Server   ${NC}"
echo -e "${BLUE}=======================================${NC}"
echo -e "${GREEN}Version: 0.1.0${NC}"
echo -e "${GREEN}Directory: ${SCRIPT_DIR}${NC}"
echo ""

# Start the server with Claude Desktop compatible configuration
echo -e "${BLUE}Starting server for Claude Desktop...${NC}"
echo -e "${YELLOW}This server uses stdio transport. Connect Claude Desktop to this process.${NC}"
echo ""

# Run the server with default configuration
"${SCRIPT_DIR}/start-server.sh" --name "Claude-Continuity-Server" --transport stdio --log-level INFO