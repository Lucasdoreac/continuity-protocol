#!/bin/bash
#
# Run Continuity Protocol HTTP Server
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
echo -e "${BLUE}   Continuity Protocol HTTP Server    ${NC}"
echo -e "${BLUE}=======================================${NC}"
echo -e "${GREEN}Version: 0.1.0${NC}"
echo -e "${GREEN}Directory: ${SCRIPT_DIR}${NC}"
echo ""

# Parse command line arguments
HOST="127.0.0.1"
PORT="8000"

while [[ $# -gt 0 ]]; do
    case $1 in
        --host)
            HOST="$2"
            shift 2
            ;;
        --port)
            PORT="$2"
            shift 2
            ;;
        *)
            echo -e "${YELLOW}Warning: Unknown argument: $1${NC}"
            shift
            ;;
    esac
done

# Start the server with HTTP transport
echo -e "${BLUE}Starting HTTP server on ${HOST}:${PORT}...${NC}"
echo -e "${YELLOW}API will be available at: http://${HOST}:${PORT}/execute${NC}"
echo -e "${YELLOW}Tools list will be available at: http://${HOST}:${PORT}/tools${NC}"
echo -e "${YELLOW}Health check will be available at: http://${HOST}:${PORT}/health${NC}"
echo ""

# Run the server with HTTP transport
"${SCRIPT_DIR}/start-server.sh" --name "HTTP-Continuity-Server" --transport http --host "${HOST}" --port "${PORT}" --log-level INFO