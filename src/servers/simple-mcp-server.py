#!/usr/bin/env python3
"""
Simple MCP Server - Versão básica do servidor MCP unificado
"""

import os
import sys
import json
import subprocess
from typing import Dict, List, Any

# Base paths
CONTINUITY_BASE = "/Users/lucascardoso/apps/MCP/CONTINUITY"
SCRIPTS_PATH = "/Users/lucascardoso/apps/MCP/CONTINUITY"

# Try to import FastMCP
try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    print("Instalando MCP...")
    subprocess.run([sys.executable, "-m", "pip", "install", "mcp"])
    from mcp.server.fastmcp import FastMCP

# Inicializar FastMCP
mcp = FastMCP("simple-continuity-protocol")

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

@mcp.tool()
def continuity_where_stopped() -> str:
    """Execute 'onde paramos?' - automatic recovery and context loading"""
    result = run_bash_script("autonomous-recovery.sh")
    
    if result.get("success"):
        response = f"✅ SUCCESS\n\n{result.get('stdout', '')}"
        if result.get('stderr'):
            response += f"\n\n⚠️ WARNINGS:\n{result['stderr']}"
        return response
    else:
        response = f"❌ ERROR: {result.get('error', 'Unknown error')}"
        if result.get('stderr'):
            response += f"\n\nSTDERR: {result['stderr']}"
        if result.get('stdout'):
            response += f"\n\nSTDOUT: {result['stdout']}"
        return response

@mcp.tool()
def continuity_magic_system(user_input: str) -> str:
    """Process user input through magic detection system"""
    result = run_bash_script("magic-system.sh", [user_input])
    
    if result.get("success"):
        response = f"✅ SUCCESS\n\n{result.get('stdout', '')}"
        if result.get('stderr'):
            response += f"\n\n⚠️ WARNINGS:\n{result['stderr']}"
        return response
    else:
        response = f"❌ ERROR: {result.get('error', 'Unknown error')}"
        if result.get('stderr'):
            response += f"\n\nSTDERR: {result['stderr']}"
        if result.get('stdout'):
            response += f"\n\nSTDOUT: {result['stdout']}"
        return response

@mcp.tool()
def continuity_emergency_freeze() -> str:
    """Create emergency backup freeze of current state"""
    result = run_bash_script("emergency-absolute.sh", ["freeze"])
    
    if result.get("success"):
        response = f"✅ SUCCESS\n\n{result.get('stdout', '')}"
        if result.get('stderr'):
            response += f"\n\n⚠️ WARNINGS:\n{result['stderr']}"
        return response
    else:
        response = f"❌ ERROR: {result.get('error', 'Unknown error')}"
        if result.get('stderr'):
            response += f"\n\nSTDERR: {result['stderr']}"
        if result.get('stdout'):
            response += f"\n\nSTDOUT: {result['stdout']}"
        return response

@mcp.tool()
def continuity_emergency_unfreeze() -> str:
    """Restore from emergency backup freeze"""
    result = run_bash_script("emergency-absolute.sh", ["unfreeze"])
    
    if result.get("success"):
        response = f"✅ SUCCESS\n\n{result.get('stdout', '')}"
        if result.get('stderr'):
            response += f"\n\n⚠️ WARNINGS:\n{result['stderr']}"
        return response
    else:
        response = f"❌ ERROR: {result.get('error', 'Unknown error')}"
        if result.get('stderr'):
            response += f"\n\nSTDERR: {result['stderr']}"
        if result.get('stdout'):
            response += f"\n\nSTDOUT: {result['stdout']}"
        return response

@mcp.tool()
def continuity_system_status() -> str:
    """Get complete system status and project overview"""
    result = run_bash_script("emergency-absolute.sh", ["status"])
    
    if result.get("success"):
        response = f"✅ SUCCESS\n\n{result.get('stdout', '')}"
        if result.get('stderr'):
            response += f"\n\n⚠️ WARNINGS:\n{result['stderr']}"
        return response
    else:
        response = f"❌ ERROR: {result.get('error', 'Unknown error')}"
        if result.get('stderr'):
            response += f"\n\nSTDERR: {result['stderr']}"
        if result.get('stdout'):
            response += f"\n\nSTDOUT: {result['stdout']}"
        return response

if __name__ == "__main__":
    # Salvar PID para gerenciamento
    pid_file = os.path.join(CONTINUITY_BASE, "simple-mcp-server.pid")
    with open(pid_file, "w") as f:
        f.write(str(os.getpid()))
    
    print("Starting Simple MCP Server")
    print(f"CONTINUITY base: {CONTINUITY_BASE}")
    
    # Executar servidor MCP
    mcp.run(transport="stdio")