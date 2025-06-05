#!/bin/bash
#
# Configure Claude Desktop to use Continuity Protocol
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
echo -e "${BLUE}   Claude Desktop Configuration       ${NC}"
echo -e "${BLUE}=======================================${NC}"
echo -e "${GREEN}Version: 0.1.0${NC}"
echo -e "${GREEN}Directory: ${SCRIPT_DIR}${NC}"
echo ""

# Determine Claude Desktop config directory
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    CONFIG_DIR="$HOME/Library/Application Support/Claude Desktop"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    CONFIG_DIR="$HOME/.config/Claude Desktop"
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows
    CONFIG_DIR="$APPDATA/Claude Desktop"
else
    echo -e "${RED}Unsupported operating system: $OSTYPE${NC}"
    exit 1
fi

# Check if config directory exists
if [ ! -d "$CONFIG_DIR" ]; then
    echo -e "${RED}Claude Desktop config directory not found: $CONFIG_DIR${NC}"
    echo -e "${YELLOW}Please install Claude Desktop first.${NC}"
    exit 1
fi

echo -e "${BLUE}Claude Desktop config directory: $CONFIG_DIR${NC}"
echo ""

# Create MCP config
echo -e "${BLUE}Creating MCP configuration...${NC}"

# Determine server path
SERVER_PATH="$SCRIPT_DIR/run-claude-server.sh"
if [ ! -f "$SERVER_PATH" ]; then
    echo -e "${RED}Server script not found: $SERVER_PATH${NC}"
    exit 1
fi

# Create config file
CONFIG_FILE="$CONFIG_DIR/mcp_config.json"
cat > "$CONFIG_FILE" << EOL
{
  "enabled": true,
  "serverType": "subprocess",
  "subprocessPath": "$SERVER_PATH",
  "subprocessArgs": [],
  "httpUrl": "",
  "toolSuggestions": true
}
EOL

echo -e "${GREEN}✅ Created MCP configuration: $CONFIG_FILE${NC}"
echo ""

# Create tool definitions
echo -e "${BLUE}Creating tool definitions...${NC}"

TOOLS_DIR="$CONFIG_DIR/tools"
mkdir -p "$TOOLS_DIR"

# Session tools
cat > "$TOOLS_DIR/session_tools.json" << EOL
[
  {
    "name": "session_create",
    "description": "Create a new continuity session",
    "parameters": {
      "type": "object",
      "properties": {
        "name": {
          "type": "string",
          "description": "Name of the session"
        },
        "metadata": {
          "type": "object",
          "description": "Additional metadata for the session"
        }
      },
      "required": ["name"]
    }
  },
  {
    "name": "session_save",
    "description": "Save the current state of a session",
    "parameters": {
      "type": "object",
      "properties": {
        "session_id": {
          "type": "string",
          "description": "Session identifier"
        },
        "content": {
          "type": "object",
          "description": "Session content to save"
        },
        "compression_level": {
          "type": "integer",
          "enum": [0, 1, 2, 3],
          "description": "Compression level (0=none, 3=maximum)"
        }
      },
      "required": ["session_id", "content"]
    }
  },
  {
    "name": "session_restore",
    "description": "Restore a previously saved session",
    "parameters": {
      "type": "object",
      "properties": {
        "session_id": {
          "type": "string",
          "description": "Session identifier"
        },
        "version": {
          "type": "integer",
          "description": "Specific version to restore (optional)"
        }
      },
      "required": ["session_id"]
    }
  },
  {
    "name": "session_list",
    "description": "List all available sessions",
    "parameters": {
      "type": "object",
      "properties": {}
    }
  }
]
EOL

# Context tools
cat > "$TOOLS_DIR/context_tools.json" << EOL
[
  {
    "name": "context_store",
    "description": "Store context information",
    "parameters": {
      "type": "object",
      "properties": {
        "key": {
          "type": "string",
          "description": "Context identifier key"
        },
        "value": {
          "type": "object",
          "description": "Context value to store"
        },
        "ttl": {
          "type": "integer",
          "description": "Time to live in seconds (optional)"
        },
        "namespace": {
          "type": "string",
          "description": "Context namespace (optional)"
        }
      },
      "required": ["key", "value"]
    }
  },
  {
    "name": "context_retrieve",
    "description": "Retrieve stored context information",
    "parameters": {
      "type": "object",
      "properties": {
        "key": {
          "type": "string",
          "description": "Context identifier key"
        },
        "namespace": {
          "type": "string",
          "description": "Context namespace (optional)"
        }
      },
      "required": ["key"]
    }
  },
  {
    "name": "context_switch",
    "description": "Switch between different contexts",
    "parameters": {
      "type": "object",
      "properties": {
        "target_context": {
          "type": "string",
          "description": "Target context identifier"
        },
        "preserve_current": {
          "type": "boolean",
          "description": "Whether to preserve current context for later restoration"
        }
      },
      "required": ["target_context"]
    }
  }
]
EOL

# System tools
cat > "$TOOLS_DIR/system_tools.json" << EOL
[
  {
    "name": "system_status",
    "description": "Get system status",
    "parameters": {
      "type": "object",
      "properties": {
        "include_sessions": {
          "type": "boolean",
          "description": "Whether to include active sessions in the response"
        },
        "include_metrics": {
          "type": "boolean",
          "description": "Whether to include system metrics in the response"
        }
      }
    }
  },
  {
    "name": "memory_optimize",
    "description": "Optimize memory usage",
    "parameters": {
      "type": "object",
      "properties": {
        "target_session": {
          "type": "string",
          "description": "Target session to optimize (optional)"
        },
        "level": {
          "type": "string",
          "enum": ["light", "medium", "aggressive"],
          "description": "Optimization level"
        }
      }
    }
  }
]
EOL

# LLM Timesheet tools
cat > "$TOOLS_DIR/llm_timesheet_tools.json" << EOL
[
  {
    "name": "llm_punch_in",
    "description": "Register the start of a task for an LLM",
    "parameters": {
      "type": "object",
      "properties": {
        "llm_name": {
          "type": "string",
          "description": "Name of the LLM (e.g., 'claude', 'gpt-4')"
        },
        "task_description": {
          "type": "string",
          "description": "Description of the task"
        },
        "context": {
          "type": "string",
          "description": "Additional context (optional)"
        }
      },
      "required": ["llm_name", "task_description"]
    }
  },
  {
    "name": "llm_punch_out",
    "description": "Register the end of a task for an LLM",
    "parameters": {
      "type": "object",
      "properties": {
        "task_id": {
          "type": "string",
          "description": "Task identifier"
        },
        "summary": {
          "type": "string",
          "description": "Summary of the work done"
        },
        "detect_files": {
          "type": "boolean",
          "description": "Whether to automatically detect modified files"
        }
      },
      "required": ["task_id", "summary"]
    }
  },
  {
    "name": "llm_sprint_report",
    "description": "Generate a report for the current sprint",
    "parameters": {
      "type": "object",
      "properties": {}
    }
  },
  {
    "name": "llm_finish_sprint",
    "description": "Finish the current sprint and start a new one",
    "parameters": {
      "type": "object",
      "properties": {
        "summary": {
          "type": "string",
          "description": "Sprint summary"
        }
      },
      "required": ["summary"]
    }
  }
]
EOL

echo -e "${GREEN}✅ Created tool definitions in: $TOOLS_DIR${NC}"
echo ""

# Print success message
echo -e "${BLUE}=======================================${NC}"
echo -e "${GREEN}Claude Desktop configuration completed!${NC}"
echo -e "${BLUE}=======================================${NC}"
echo ""
echo -e "To use the Continuity Protocol with Claude Desktop:"
echo -e "1. Restart Claude Desktop"
echo -e "2. Open Claude Desktop and verify that the MCP icon is active"
echo -e "3. Use the tools with the /tools command"
echo -e ""
echo -e "Example:"
echo -e "${YELLOW}/tools system_status{\"include_sessions\": true}${NC}"
echo -e ""
echo -e "For more information, see the documentation in ${YELLOW}docs/api/README.md${NC}"