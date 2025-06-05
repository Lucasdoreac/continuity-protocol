#!/bin/bash

# Install MCP Continuity for Claude Desktop
# Creates proper MCP server compatible with Claude Desktop config

set -e

CONTINUITY_BASE="/Users/lucascardoso/apps/MCP/CONTINUITY"
MCP_SERVICE_DIR="${CONTINUITY_BASE}/project-states/mcp-continuity-service"
MCP_SERVER_FILE="${CONTINUITY_BASE}/mcp-continuity-server.py"
CLAUDE_CONFIG="$HOME/Library/Application Support/Claude/claude_desktop_config.json"

echo "🚀 Installing MCP Continuity for Claude Desktop..."

# 1. Create the MCP server file
echo "📝 Creating MCP server file..."
cat > "${MCP_SERVER_FILE}" << 'EOF'
#!/usr/bin/env python3
"""
MCP Continuity Server - Claude Desktop Compatible
Integrates bash scripts with MCP protocol for seamless continuity
"""

import asyncio
import sys
import json
import subprocess
import os
from pathlib import Path
from typing import Dict, List, Any, Optional

# Import MCP modules
from mcp.server.lowlevel import Server
from mcp.types import Tool, TextContent, CallToolRequest

# Base paths
CONTINUITY_BASE = "/Users/lucascardoso/apps/MCP/CONTINUITY"
SCRIPTS_PATH = CONTINUITY_BASE
PROJECT_STATES_PATH = f"{CONTINUITY_BASE}/project-states"

# Initialize MCP Server
server = Server("mcp-continuity")

def run_bash_script(script_name: str, args: List[str] = None) -> Dict[str, Any]:
    """Execute bash script and return structured result"""
    try:
        script_path = f"{SCRIPTS_PATH}/{script_name}"
        
        if not os.path.exists(script_path):
            return {
                "error": f"Script not found: {script_path}",
                "success": False
            }
        
        cmd = [script_path]
        if args:
            cmd.extend(args)
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
        
    except subprocess.TimeoutExpired:
        return {
            "error": "Script execution timeout",
            "success": False
        }
    except Exception as e:
        return {
            "error": f"Execution error: {str(e)}",
            "success": False
        }

@server.list_tools()
async def list_tools() -> List[Tool]:
    """List available MCP Continuity tools"""
    return [
        Tool(
            name="continuity_where_stopped",
            description="Execute 'onde paramos?' - automatic recovery and context loading",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="continuity_magic_system",
            description="Process user input through magic detection system",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_input": {
                        "type": "string",
                        "description": "User input to process through magic system"
                    }
                },
                "required": ["user_input"]
            }
        ),
        Tool(
            name="continuity_emergency_freeze",
            description="Create emergency backup freeze of current state",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="continuity_emergency_unfreeze",
            description="Restore from emergency backup freeze",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="continuity_system_status",
            description="Get complete system status and project overview",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="continuity_project_context",
            description="Load context for specific project",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_name": {
                        "type": "string",
                        "description": "Project name to load context for"
                    }
                },
                "required": ["project_name"]
            }
        ),
        Tool(
            name="continuity_mcp_guard",
            description="Execute MCP protection guard before critical operations",
            inputSchema={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "description": "Action to protect"
                    },
                    "target": {
                        "type": "string",
                        "description": "Target of the action"
                    },
                    "context": {
                        "type": "string",
                        "description": "Context for the protection"
                    }
                },
                "required": ["action", "target", "context"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls from Claude"""
    
    try:
        if name == "continuity_where_stopped":
            result = run_bash_script("autonomous-recovery.sh")
            
        elif name == "continuity_magic_system":
            user_input = arguments.get("user_input", "")
            result = run_bash_script("magic-system.sh", [user_input])
            
        elif name == "continuity_emergency_freeze":
            result = run_bash_script("emergency-absolute.sh", ["freeze"])
            
        elif name == "continuity_emergency_unfreeze":
            result = run_bash_script("emergency-absolute.sh", ["unfreeze"])
            
        elif name == "continuity_system_status":
            result = run_bash_script("emergency-absolute.sh", ["status"])
            
        elif name == "continuity_project_context":
            project_name = arguments.get("project_name", "")
            result = run_bash_script("project-finder-optimized.sh", [project_name])
            
        elif name == "continuity_mcp_guard":
            action = arguments.get("action", "")
            target = arguments.get("target", "")
            context = arguments.get("context", "")
            result = run_bash_script("claude-mcp-guard.sh", ["guard", action, target, context])
            
        else:
            result = {
                "error": f"Unknown tool: {name}",
                "success": False
            }
        
        # Format response
        if result.get("success"):
            response_text = f"✅ SUCCESS\n\n{result.get('stdout', '')}"
            if result.get('stderr'):
                response_text += f"\n\n⚠️ WARNINGS:\n{result['stderr']}"
        else:
            response_text = f"❌ ERROR: {result.get('error', 'Unknown error')}"
            if result.get('stderr'):
                response_text += f"\n\nSTDERR: {result['stderr']}"
            if result.get('stdout'):
                response_text += f"\n\nSTDOUT: {result['stdout']}"
        
        return [TextContent(type="text", text=response_text)]
        
    except Exception as e:
        error_msg = f"❌ Tool execution failed: {str(e)}"
        return [TextContent(type="text", text=error_msg)]

async def run_server():
    """Run the MCP server"""
    # Server transport setup
    async with server:
        # Keep server running
        await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(run_server())
EOF

# 2. Make executable
chmod +x "${MCP_SERVER_FILE}"

# 3. Install MCP Python package if needed
echo "📦 Checking MCP installation..."
if ! python3 -c "import mcp" 2>/dev/null; then
    echo "Installing MCP package..."
    pip3 install mcp
fi

# 4. Backup current Claude config
if [ -f "${CLAUDE_CONFIG}" ]; then
    echo "💾 Backing up Claude config..."
    cp "${CLAUDE_CONFIG}" "${CLAUDE_CONFIG}.backup.$(date +%Y%m%d_%H%M%S)"
fi

# 5. Update Claude Desktop config
echo "⚙️ Updating Claude Desktop configuration..."

# Create config directory if it doesn't exist
mkdir -p "$(dirname "${CLAUDE_CONFIG}")"

# Read current config or create empty
if [ -f "${CLAUDE_CONFIG}" ]; then
    CURRENT_CONFIG=$(cat "${CLAUDE_CONFIG}")
else
    CURRENT_CONFIG='{"mcpServers": {}}'
fi

# Add mcp-continuity server to config
python3 -c "
import json
import sys

config = json.loads('${CURRENT_CONFIG}')
if 'mcpServers' not in config:
    config['mcpServers'] = {}

config['mcpServers']['mcp-continuity'] = {
    'command': 'python3',
    'args': ['${MCP_SERVER_FILE}']
}

print(json.dumps(config, indent=2))
" > "${CLAUDE_CONFIG}"

echo "✅ MCP Continuity installed successfully!"
echo ""
echo "📋 Configuration added to Claude Desktop:"
echo "   Server: mcp-continuity"
echo "   Command: python3 ${MCP_SERVER_FILE}"
echo ""
echo "🔄 Please restart Claude Desktop to load the new MCP server."
echo ""
echo "🛠️ Available tools in Claude:"
echo "   - continuity_where_stopped"
echo "   - continuity_magic_system"
echo "   - continuity_emergency_freeze"
echo "   - continuity_emergency_unfreeze"
echo "   - continuity_system_status"
echo "   - continuity_project_context"
echo "   - continuity_mcp_guard"
