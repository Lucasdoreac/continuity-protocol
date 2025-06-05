#!/usr/bin/env python3
"""
Minimal MCP Server
"""

from mcp.server.fastmcp import FastMCP

# Inicializar FastMCP
mcp = FastMCP("continuity-minimal")

@mcp.tool()
def continuity_test() -> str:
    """Test if the continuity protocol is working"""
    return "✅ Continuity Protocol Minimal Server is running!"

if __name__ == "__main__":
    print("Starting Minimal MCP Server")
    mcp.run()