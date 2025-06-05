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

# Parse command line arguments
SERVER_NAME="Continuity-Protocol"
TRANSPORT="stdio"
HOST="127.0.0.1"
PORT="8000"
DEFAULT_TOOLS=true
TIMESHEET=true
LOG_LEVEL="INFO"

while [[ $# -gt 0 ]]; do
    case $1 in
        --name)
            SERVER_NAME="$2"
            shift 2
            ;;
        --transport)
            TRANSPORT="$2"
            shift 2
            ;;
        --host)
            HOST="$2"
            shift 2
            ;;
        --port)
            PORT="$2"
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

# If transport is HTTP, check if FastAPI and uvicorn are installed
if [ "$TRANSPORT" == "http" ]; then
    if ! python -c "import fastapi" &> /dev/null; then
        echo -e "${YELLOW}Installing FastAPI and uvicorn for HTTP transport...${NC}"
        pip install fastapi uvicorn
    fi
fi

# Print banner
echo -e "${BLUE}=================================${NC}"
echo -e "${BLUE}   Continuity Protocol Server    ${NC}"
echo -e "${BLUE}=================================${NC}"
echo -e "${GREEN}Version: 0.1.0${NC}"
echo -e "${GREEN}Directory: ${SCRIPT_DIR}${NC}"
echo ""

# Print server configuration
echo -e "${BLUE}Server Configuration:${NC}"
echo -e "${GREEN}  Name: ${SERVER_NAME}${NC}"
echo -e "${GREEN}  Transport: ${TRANSPORT}${NC}"
if [ "$TRANSPORT" == "http" ]; then
    echo -e "${GREEN}  Host: ${HOST}${NC}"
    echo -e "${GREEN}  Port: ${PORT}${NC}"
fi
echo -e "${GREEN}  Default Tools: $([ "$DEFAULT_TOOLS" = true ] && echo "Enabled" || echo "Disabled")${NC}"
echo -e "${GREEN}  LLM Timesheet: $([ "$TIMESHEET" = true ] && echo "Enabled" || echo "Disabled")${NC}"
echo -e "${GREEN}  Log Level: ${LOG_LEVEL}${NC}"
echo ""
echo -e "${BLUE}Starting server...${NC}"
echo ""

# Build command
CMD="python -m continuity_protocol.server"
CMD="${CMD} --name \"${SERVER_NAME}\""
CMD="${CMD} --transport ${TRANSPORT}"
CMD="${CMD} --host ${HOST}"
CMD="${CMD} --port ${PORT}"

if [ "$DEFAULT_TOOLS" = false ]; then
    CMD="${CMD} --no-defaults"
fi

if [ "$TIMESHEET" = false ]; then
    CMD="${CMD} --no-timesheet"
fi

# Set log level
export PYTHONPATH="${SCRIPT_DIR}:${PYTHONPATH}"
export LOGLEVEL="${LOG_LEVEL}"

# Run the server
eval "${CMD}"