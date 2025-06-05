#!/bin/bash
#
# Start Continuity Protocol MCP Server
#

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is required but not installed.${NC}"
    exit 1
fi

# Ensure we have a virtual environment
if [ ! -d "${SCRIPT_DIR}/venv" ]; then
    echo -e "${BLUE}Creating virtual environment...${NC}"
    python3 -m venv "${SCRIPT_DIR}/venv"
    
    # Activate virtual environment
    source "${SCRIPT_DIR}/venv/bin/activate"
    
    # Install dependencies
    echo -e "${BLUE}Installing dependencies...${NC}"
    pip install -e "${SCRIPT_DIR}"
    pip install psutil
else
    # Activate virtual environment
    source "${SCRIPT_DIR}/venv/bin/activate"
fi

# Ensure directories exist
mkdir -p "${SCRIPT_DIR}/data/sessions"
mkdir -p "${SCRIPT_DIR}/data/contexts"
mkdir -p "${SCRIPT_DIR}/logs"
mkdir -p "${SCRIPT_DIR}/data/temp"

# Print banner
echo -e "${BLUE}=================================${NC}"
echo -e "${BLUE}   Continuity Protocol Server    ${NC}"
echo -e "${BLUE}=================================${NC}"
echo -e "${GREEN}Version: 0.1.0${NC}"
echo -e "${GREEN}Directory: ${SCRIPT_DIR}${NC}"
echo ""

# Parse command line arguments
TRANSPORT="stdio"
SERVER_NAME="Continuity-Protocol"
DEFAULT_TOOLS=true
TIMESHEET=true
LOG_LEVEL="INFO"

while [[ $# -gt 0 ]]; do
    case $1 in
        --transport)
            TRANSPORT="$2"
            shift 2
            ;;
        --name)
            SERVER_NAME="$2"
            shift 2
            ;;
        --no-default-tools)
            DEFAULT_TOOLS=false
            shift
            ;;
        --no-timesheet)
            TIMESHEET=false
            shift
            ;;
        --log-level)
            LOG_LEVEL="$2"
            shift 2
            ;;
        *)
            echo -e "${YELLOW}Warning: Unknown argument: $1${NC}"
            shift
            ;;
    esac
done

# Build command
CMD="python3 ${SCRIPT_DIR}/src/continuity_server.py"
CMD="${CMD} --name \"${SERVER_NAME}\""
CMD="${CMD} --transport ${TRANSPORT}"
CMD="${CMD} --log-level ${LOG_LEVEL}"

if [ "$DEFAULT_TOOLS" = false ]; then
    CMD="${CMD} --no-default-tools"
fi

if [ "$TIMESHEET" = false ]; then
    CMD="${CMD} --no-timesheet"
fi

# Print server configuration
echo -e "${BLUE}Server Configuration:${NC}"
echo -e "${GREEN}  Name: ${SERVER_NAME}${NC}"
echo -e "${GREEN}  Transport: ${TRANSPORT}${NC}"
echo -e "${GREEN}  Default Tools: $([ "$DEFAULT_TOOLS" = true ] && echo "Enabled" || echo "Disabled")${NC}"
echo -e "${GREEN}  LLM Timesheet: $([ "$TIMESHEET" = true ] && echo "Enabled" || echo "Disabled")${NC}"
echo -e "${GREEN}  Log Level: ${LOG_LEVEL}${NC}"
echo ""
echo -e "${BLUE}Starting server...${NC}"
echo ""

# Run the server
eval "${CMD}"