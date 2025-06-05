#!/usr/bin/env python3
"""
Basic MCP Server - Versão mais básica possível do servidor MCP
"""

import sys
import subprocess

# Try to import FastMCP
try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    print("Instalando MCP...")
    subprocess.run([sys.executable, "-m", "pip", "install", "mcp"])
    from mcp.server.fastmcp import FastMCP

# Inicializar FastMCP
mcp = FastMCP("basic-continuity-protocol")

@mcp.tool()
def hello_world(name: str = "World") -> str:
    """Return a greeting message"""
    return f"Hello, {name}! This is the basic MCP server."

@mcp.tool()
def continuity_status() -> str:
    """Get current status"""
    return "✅ Continuity Protocol is running!"

if __name__ == "__main__":
    print("Starting Basic MCP Server")
    
    # Executar servidor MCP
    mcp.run(transport="stdio")