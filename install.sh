#!/bin/bash
#
# Install Continuity Protocol
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
echo -e "${BLUE}     Continuity Protocol Install       ${NC}"
echo -e "${BLUE}=======================================${NC}"
echo -e "${GREEN}Version: 0.1.0${NC}"
echo -e "${GREEN}Directory: ${SCRIPT_DIR}${NC}"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is required but not installed.${NC}"
    exit 1
fi

# Check Python version
python_version=$(python3 --version | cut -d' ' -f2)
required_version="3.8.0"

if [[ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]]; then
    echo -e "${RED}Error: Python 3.8 or higher is required. Found version $python_version.${NC}"
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}Error: pip3 is required but not installed.${NC}"
    exit 1
fi

# Create virtual environment
echo -e "${BLUE}Creating virtual environment...${NC}"
if [ ! -d "${SCRIPT_DIR}/venv" ]; then
    python3 -m venv "${SCRIPT_DIR}/venv"
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}Error: Failed to create virtual environment.${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}Virtual environment created successfully.${NC}"
else
    echo -e "${YELLOW}Virtual environment already exists. Skipping creation.${NC}"
fi

# Activate virtual environment
echo -e "${BLUE}Activating virtual environment...${NC}"
source "${SCRIPT_DIR}/venv/bin/activate"

# Install dependencies
echo -e "${BLUE}Installing dependencies...${NC}"
pip install -e "${SCRIPT_DIR}"

if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to install dependencies.${NC}"
    exit 1
fi

echo -e "${GREEN}Dependencies installed successfully.${NC}"

# Create necessary directories
echo -e "${BLUE}Creating necessary directories...${NC}"
mkdir -p "${SCRIPT_DIR}/data/sessions"
mkdir -p "${SCRIPT_DIR}/data/contexts"
mkdir -p "${SCRIPT_DIR}/logs"
mkdir -p "${SCRIPT_DIR}/data/temp"

# Create a legacy directory for compatibility
mkdir -p "${SCRIPT_DIR}/legacy"

# If we have old server scripts, move them to legacy
for file in "${SCRIPT_DIR}"/*.py; do
    if [[ "$file" != *"/src/"* && "$file" != *"/tests/"* ]]; then
        echo -e "${YELLOW}Moving legacy file: ${file}${NC}"
        cp "$file" "${SCRIPT_DIR}/legacy/"
    fi
done

# Make scripts executable
echo -e "${BLUE}Making scripts executable...${NC}"
chmod +x "${SCRIPT_DIR}/start-server.sh"
chmod +x "${SCRIPT_DIR}/run-claude-server.sh"
chmod +x "${SCRIPT_DIR}/examples/basic/simple_client.py"

# Print success message
echo -e "${BLUE}=======================================${NC}"
echo -e "${GREEN}Continuity Protocol installed successfully!${NC}"
echo -e "${BLUE}=======================================${NC}"
echo ""
echo -e "To start the server, run:"
echo -e "${YELLOW}./start-server.sh${NC}"
echo ""
echo -e "To run with Claude Desktop, run:"
echo -e "${YELLOW}./run-claude-server.sh${NC}"
echo ""
echo -e "To try the example client, run:"
echo -e "${YELLOW}./examples/basic/simple_client.py${NC}"
echo ""