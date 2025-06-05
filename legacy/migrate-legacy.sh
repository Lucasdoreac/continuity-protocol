#!/bin/bash
#
# Migrate Legacy Continuity Protocol to New Format
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
echo -e "${BLUE}     Legacy Migration Utility          ${NC}"
echo -e "${BLUE}=======================================${NC}"
echo -e "${GREEN}Version: 0.1.0${NC}"
echo -e "${GREEN}Directory: ${SCRIPT_DIR}${NC}"
echo ""

# Create legacy directory if it doesn't exist
mkdir -p "${SCRIPT_DIR}/legacy"

# Function to migrate a legacy file
migrate_file() {
    local file="$1"
    local basename=$(basename "$file")
    local target="${SCRIPT_DIR}/legacy/$basename"
    
    echo -e "${YELLOW}Migrating: $basename${NC}"
    
    # Copy file to legacy directory
    cp "$file" "$target"
    
    # Make legacy file executable if original was executable
    if [[ -x "$file" ]]; then
        chmod +x "$target"
    fi
    
    echo -e "${GREEN}✓ Migrated to: $target${NC}"
}

# Find and migrate Python scripts
echo -e "${BLUE}Migrating Python scripts...${NC}"
for file in "${SCRIPT_DIR}"/*.py; do
    if [[ -f "$file" && "$file" != *"/src/"* && "$file" != *"/tests/"* ]]; then
        migrate_file "$file"
    fi
done

# Find and migrate shell scripts
echo -e "${BLUE}Migrating shell scripts...${NC}"
for file in "${SCRIPT_DIR}"/*.sh; do
    if [[ -f "$file" && "$file" != "install.sh" && "$file" != "start-server.sh" && "$file" != "run-claude-server.sh" && "$file" != "migrate-legacy.sh" ]]; then
        migrate_file "$file"
    fi
done

# Find and migrate other files
echo -e "${BLUE}Migrating other files...${NC}"
for ext in md txt json; do
    for file in "${SCRIPT_DIR}"/*.$ext; do
        if [[ -f "$file" && "$file" != "README.md" && "$file" != *"/src/"* && "$file" != *"/docs/"* ]]; then
            migrate_file "$file"
        fi
    done
done

# Migrate legacy data
echo -e "${BLUE}Migrating legacy data...${NC}"

# Check for emergency freeze directories
if [[ -d "${SCRIPT_DIR}/emergency-freeze" ]]; then
    echo -e "${YELLOW}Migrating emergency freeze data...${NC}"
    
    # Create legacy emergency freeze directory
    mkdir -p "${SCRIPT_DIR}/legacy/emergency-freeze"
    
    # Copy all emergency freeze data
    cp -r "${SCRIPT_DIR}/emergency-freeze"/* "${SCRIPT_DIR}/legacy/emergency-freeze/"
    
    echo -e "${GREEN}✓ Emergency freeze data migrated${NC}"
fi

# Check for emergency backup directories
if [[ -d "${SCRIPT_DIR}/emergency-backups" ]]; then
    echo -e "${YELLOW}Migrating emergency backup data...${NC}"
    
    # Create legacy emergency backup directory
    mkdir -p "${SCRIPT_DIR}/legacy/emergency-backups"
    
    # Copy all emergency backup data
    cp -r "${SCRIPT_DIR}/emergency-backups"/* "${SCRIPT_DIR}/legacy/emergency-backups/"
    
    echo -e "${GREEN}✓ Emergency backup data migrated${NC}"
fi

# Check for project states
if [[ -d "${SCRIPT_DIR}/project-states" ]]; then
    echo -e "${YELLOW}Migrating project states...${NC}"
    
    # Create legacy project states directory
    mkdir -p "${SCRIPT_DIR}/legacy/project-states"
    
    # Copy all project states
    cp -r "${SCRIPT_DIR}/project-states"/* "${SCRIPT_DIR}/legacy/project-states/"
    
    echo -e "${GREEN}✓ Project states migrated${NC}"
    
    # Convert project states to new format
    echo -e "${BLUE}Converting project states to new format...${NC}"
    
    # Create new data directory
    mkdir -p "${SCRIPT_DIR}/data/sessions"
    
    # For each JSON file in project states
    for file in "${SCRIPT_DIR}/project-states"/*.json; do
        if [[ -f "$file" ]]; then
            basename=$(basename "$file" .json)
            echo -e "${YELLOW}Converting: $basename${NC}"
            
            # Create session directory
            session_id="legacy-${basename}"
            mkdir -p "${SCRIPT_DIR}/data/sessions/${session_id}"
            
            # Create metadata file
            cat > "${SCRIPT_DIR}/data/sessions/${session_id}/metadata.json" << EOL
{
  "session_id": "${session_id}",
  "name": "Legacy: ${basename}",
  "created_at": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "updated_at": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "metadata": {
    "source": "legacy",
    "original_file": "${file}"
  },
  "versions": [
    {
      "version": 1,
      "saved_at": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
      "compression_level": 0,
      "size": $(wc -c < "$file")
    }
  ]
}
EOL
            
            # Copy content as version 1
            cp "$file" "${SCRIPT_DIR}/data/sessions/${session_id}/version_1.json"
            
            echo -e "${GREEN}✓ Converted to new format${NC}"
        fi
    done
fi

# Create symbolic links for compatibility
echo -e "${BLUE}Creating compatibility links...${NC}"

# Link old emergency scripts to new commands
if [[ -f "${SCRIPT_DIR}/legacy/emergency-absolute.sh" ]]; then
    echo -e "${YELLOW}Creating link for emergency-absolute.sh${NC}"
    
    cat > "${SCRIPT_DIR}/emergency-absolute.sh" << 'EOL'
#!/bin/bash
# Compatibility script for emergency-absolute.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Print warning
echo -e "\033[0;33mWarning: Using legacy emergency-absolute.sh via compatibility layer\033[0m"
echo -e "\033[0;33mConsider updating to use the new continuity protocol tools\033[0m"
echo ""

# Map legacy commands to new tools
case "$1" in
    freeze)
        echo "Creating emergency backup..."
        "${SCRIPT_DIR}/start-server.sh" --name "Emergency-Backup" --transport stdio << EOT
{"jsonrpc":"2.0","id":"1","method":"execute","params":{"tool":"session_create","parameters":{"name":"Emergency Backup","metadata":{"type":"emergency","created_by":"legacy-compatibility"}}}}
EOT
        ;;
    unfreeze)
        echo "Restoring from emergency backup..."
        "${SCRIPT_DIR}/start-server.sh" --name "Emergency-Restore" --transport stdio << EOT
{"jsonrpc":"2.0","id":"1","method":"execute","params":{"tool":"session_list","parameters":{}}}
EOT
        ;;
    status)
        echo "Getting system status..."
        "${SCRIPT_DIR}/start-server.sh" --name "System-Status" --transport stdio << EOT
{"jsonrpc":"2.0","id":"1","method":"execute","params":{"tool":"system_status","parameters":{"include_sessions":true,"include_metrics":true}}}
EOT
        ;;
    *)
        echo "Unknown command: $1"
        echo "Usage: emergency-absolute.sh [freeze|unfreeze|status]"
        exit 1
        ;;
esac
EOL
    
    chmod +x "${SCRIPT_DIR}/emergency-absolute.sh"
    echo -e "${GREEN}✓ Created compatibility script for emergency-absolute.sh${NC}"
fi

# Print success message
echo -e "${BLUE}=======================================${NC}"
echo -e "${GREEN}Legacy migration completed successfully!${NC}"
echo -e "${BLUE}=======================================${NC}"
echo ""
echo -e "Legacy files and data have been moved to:"
echo -e "${YELLOW}${SCRIPT_DIR}/legacy/${NC}"
echo ""
echo -e "Some compatibility scripts have been created to ease the transition."
echo -e "You can now run the new Continuity Protocol server:"
echo -e "${YELLOW}./start-server.sh${NC}"
echo ""