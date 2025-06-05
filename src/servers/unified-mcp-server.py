#!/usr/bin/env python3
"""
Unified MCP Server - Combines functionality from both CONTINUITY and continuity-protocol
"""

import os
import sys
import json
import time
import subprocess
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from pathlib import Path

# Base paths
CONTINUITY_BASE = "/Users/lucascardoso/apps/MCP/CONTINUITY"
SCRIPTS_PATH = os.path.join(CONTINUITY_BASE, "src")

# Add paths to sys.path
sys.path.append(CONTINUITY_BASE)
sys.path.append(os.path.join(CONTINUITY_BASE, "src"))

# Try to import FastMCP
try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    print("Installing MCP...")
    subprocess.run([sys.executable, "-m", "pip", "install", "mcp"])
    from mcp.server.fastmcp import FastMCP

# Try to import enhanced context protocol
try:
    from core.mcp.integration_v2 import enhanced_context_protocol
    from core.mcp.versioning import versioning_system
    from core.mcp.backup import backup_system
    from core.mcp.notification import notification_system
    from core.mcp.search import search_system
    from core.mcp.safeguards import safeguards
    ENHANCED_CONTEXT_AVAILABLE = True
except ImportError:
    print("Enhanced context protocol not available, some features will be limited")
    ENHANCED_CONTEXT_AVAILABLE = False

class UnifiedMCPServer:
    """
    Unified MCP Server that combines functionality from CONTINUITY and continuity-protocol
    """
    
    def __init__(self, server_name: str = "unified-continuity-protocol"):
        """
        Initialize the unified MCP server
        
        Args:
            server_name: Name of the MCP server
        """
        self.server_name = server_name
        
        # Initialize FastMCP
        self.mcp = FastMCP(server_name)
        
        # Store base paths
        self.continuity_base = CONTINUITY_BASE
        self.scripts_path = SCRIPTS_PATH
        
        # Initialize enhanced context protocol if available
        self.enhanced_context_available = ENHANCED_CONTEXT_AVAILABLE
        if self.enhanced_context_available:
            self.context_protocol = enhanced_context_protocol
        
        # Register tools
        self._register_tools()
        
        # Save PID for management
        self._save_pid()
        
        print(f"Unified MCP Server initialized with name: {server_name}")
        print(f"CONTINUITY base: {self.continuity_base}")
        print(f"Enhanced context available: {self.enhanced_context_available}")
    
    def _save_pid(self):
        """Save PID to file for management"""
        pid_file = os.path.join(self.continuity_base, "unified-mcp-server.pid")
        with open(pid_file, "w") as f:
            f.write(str(os.getpid()))
    
    def _register_tools(self) -> None:
        """Register all MCP tools"""
        
        # Register CONTINUITY bash tools
        self._register_continuity_bash_tools()
        
        # Register enhanced context tools if available
        if self.enhanced_context_available:
            self._register_enhanced_context_tools()
    
    def _register_continuity_bash_tools(self) -> None:
        """Register CONTINUITY bash script tools"""
        
        def run_bash_script(script_name: str, args: List[str] = None) -> Dict[str, Any]:
            """Execute bash script and return structured result"""
            try:
                script_path = f"{self.scripts_path}/{script_name}"
                
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
        
        @self.mcp.tool()
        def continuity_where_stopped() -> str:
            """Execute 'onde paramos?' - automatic recovery and context loading"""
            result = run_bash_script("core/autonomous-recovery.sh")
            
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
        
        @self.mcp.tool()
        def continuity_magic_system(user_input: str) -> str:
            """Process user input through magic detection system"""
            result = run_bash_script("utilities/smart-context-detector.sh", [user_input])
            
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
        
        @self.mcp.tool()
        def continuity_emergency_freeze() -> str:
            """Create emergency backup freeze of current state"""
            result = run_bash_script("emergency/emergency-freeze.sh")
            
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
        
        @self.mcp.tool()
        def continuity_emergency_unfreeze() -> str:
            """Restore from emergency backup freeze"""
            result = run_bash_script("emergency/emergency-unfreeze.sh")
            
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
        
        @self.mcp.tool()
        def continuity_system_status() -> str:
            """Get complete system status and project overview"""
            result = run_bash_script("utilities/smart-context-detector.sh", ["status"])
            
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
    
    def _register_enhanced_context_tools(self) -> None:
        """Register enhanced context protocol tools if available"""
        if not self.enhanced_context_available:
            return
        
        # Artifact tools
        @self.mcp.tool()
        def context_register_project(project_id: str, project_name: str, description: str) -> str:
            """
            Register a project in the context sharing protocol
            
            Args:
                project_id: Project ID
                project_name: Project name
                description: Project description
                
            Returns:
                str: Operation result in JSON format
            """
            try:
                project_info = self.context_protocol.register_project(project_id, project_name, description)
                return json.dumps(project_info, indent=2)
            except Exception as e:
                return json.dumps({"error": str(e)}, indent=2)
        
        @self.mcp.tool()
        def context_store_artifact(content: str, artifact_type: str, project_id: str, metadata_json: str = "{}") -> str:
            """
            Store an artifact in the context sharing protocol
            
            Args:
                content: Artifact content
                artifact_type: Artifact type (e.g., "plan", "code", "document")
                project_id: Project ID
                metadata_json: Additional metadata in JSON format (optional)
                
            Returns:
                str: Operation result in JSON format
            """
            try:
                # Parse metadata
                try:
                    metadata = json.loads(metadata_json)
                except:
                    metadata = {}
                
                # Store artifact
                artifact_info = self.context_protocol.store_artifact(
                    content,
                    artifact_type,
                    project_id,
                    "unified_mcp_server",
                    metadata
                )
                
                return json.dumps(artifact_info, indent=2)
            except Exception as e:
                return json.dumps({"error": str(e)}, indent=2)
        
        @self.mcp.tool()
        def context_get_project_context(project_id: str) -> str:
            """
            Get the complete context of a project
            
            Args:
                project_id: Project ID
                
            Returns:
                str: Complete project context in JSON format
            """
            try:
                context = self.context_protocol.get_project_context(project_id)
                return json.dumps(context, indent=2)
            except Exception as e:
                return json.dumps({"error": str(e)}, indent=2)
        
        @self.mcp.tool()
        def context_create_backup(backup_type: str = "auto") -> str:
            """
            Create system backup
            
            Args:
                backup_type: Backup type ("full", "auto", "incremental")
                
            Returns:
                str: Created backup information in JSON format
            """
            try:
                result = backup_system.create_backup(backup_type)
                return json.dumps(result, indent=2)
            except Exception as e:
                return json.dumps({"error": str(e)}, indent=2)
        
        @self.mcp.tool()
        def context_get_system_status() -> str:
            """
            Get complete system status
            
            Returns:
                str: System status in JSON format
            """
            try:
                status = {
                    "safeguards": safeguards.get_status(),
                    "search": search_system.get_index_stats(),
                    "backups": backup_system.get_backups_list(),
                    "notifications": notification_system.get_notifications(limit=5)["notifications"],
                    "server_name": self.server_name,
                    "timestamp": datetime.now().isoformat()
                }
                return json.dumps(status, indent=2)
            except Exception as e:
                return json.dumps({"error": str(e)}, indent=2)
    
    def run(self, transport: str = "stdio") -> None:
        """
        Run the MCP server
        
        Args:
            transport: Transport type ("stdio" or "http")
        """
        print(f"Starting Unified MCP Server ({self.server_name})")
        print(f"Transport: {transport}")
        
        # Create initial checkpoint if enhanced context is available
        if self.enhanced_context_available:
            safeguards.create_checkpoint("startup")
        
        # Run MCP server
        self.mcp.run(transport=transport)

if __name__ == "__main__":
    # Default parameters
    server_name = "unified-continuity-protocol"
    transport = "stdio"
    
    # Process command line arguments
    if len(sys.argv) > 1:
        server_name = sys.argv[1]
    if len(sys.argv) > 2:
        transport = sys.argv[2]
    
    # Create and run server
    server = UnifiedMCPServer(server_name)
    server.run(transport=transport)
