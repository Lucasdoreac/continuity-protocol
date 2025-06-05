#!/bin/bash

# Install MCP Continuity for Claude Desktop
# Creates proper MCP server compatible with Claude Desktop config

set -e

CONTINUITY_BASE="/Users/lucascardoso/apps/MCP/CONTINUITY"
MCP_SERVER_FILE="${CONTINUITY_BASE}/mcp-continuity-server.py"
CLAUDE_CONFIG="$HOME/Library/Application Support/Claude/claude_desktop_config.json"

echo "🚀 Installing MCP Continuity for Claude Desktop..."

# Backup current Claude config
if [ -f "${CLAUDE_CONFIG}" ]; then
    echo "💾 Backing up Claude config..."
    cp "${CLAUDE_CONFIG}" "${CLAUDE_CONFIG}.backup.$(date +%Y%m%d_%H%M%S)"
fi

# Update Claude Desktop config properly
echo "⚙️ Updating Claude Desktop configuration..."

# Create config directory if it doesn't exist
mkdir -p "$(dirname "${CLAUDE_CONFIG}")"

# Create updated config with proper JSON
cat > "${CLAUDE_CONFIG}" << 'JSONEOF'
{
  "mcpServers": {
    "memory": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-memory"
      ]
    },
    "desktop-commander": {
      "command": "npx",
      "args": [
        "-y",
        "@wonderwhy-er/desktop-commander"
      ]
    },
    "applescript_execute": {
      "command": "npx",
      "args": [
        "@peakmojo/applescript-mcp"
      ]
    },
    "playwright": {
      "command": "npx",
      "args": [
        "@playwright/mcp@latest"
      ]
    },
    "everything": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-everything"
      ]
    },
    "fetch": {
      "command": "uvx",
      "args": [
        "mcp-server-fetch"
      ]
    },
    "puppeteer": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-puppeteer"
      ]
    },
    "obsidian-mcp": {
      "command": "npx",
      "args": [
        "-y",
        "@smithery/cli@latest",
        "run",
        "obsidian-mcp",
        "--key",
        "06e8d1c8-b01d-4704-b9dc-b8df037e359b",
        "--profile",
        "quickest-crane-17oCcu"
      ]
    },
    "mcp-continuity": {
      "command": "python3",
      "args": [
        "/Users/lucascardoso/apps/MCP/CONTINUITY/mcp-continuity-server.py"
      ]
    }
  }
}
JSONEOF

echo "✅ MCP Continuity configuration added to Claude Desktop!"
echo ""
echo "📋 Configuration added:"
echo "   Server: mcp-continuity" 
echo "   Command: python3 /Users/lucascardoso/apps/MCP/CONTINUITY/mcp-continuity-server.py"
echo ""
echo "⚠️  NOTE: The MCP server file needs to be created separately"
echo "🔄 Please restart Claude Desktop to load the new MCP server."
