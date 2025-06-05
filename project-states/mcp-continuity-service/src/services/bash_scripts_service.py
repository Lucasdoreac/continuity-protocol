"""
Bash Scripts Integration Service
Integrates the professional MCP service with the working bash scripts
"""

import subprocess
import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional

class BashScriptsService:
    """Service to integrate with existing bash scripts"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Path to bash scripts
        self.bash_scripts_path = "/Users/lucascardoso/apps/MCP/CONTINUITY"
        
        # Verify scripts exist
        self._verify_scripts()
    
    def _verify_scripts(self):
        """Verify that required bash scripts exist"""
        required_scripts = [
            "autonomous-recovery.sh",
            "magic-system.sh", 
            "emergency-absolute.sh"
        ]
        
        for script in required_scripts:
            script_path = os.path.join(self.bash_scripts_path, script)
            if not os.path.exists(script_path):
                self.logger.warning(f"Script not found: {script_path}")
    
    async def process_continuity_request(self, user_input: str) -> Dict[str, Any]:
        """Process continuity request using bash scripts"""
        try:
            # Use magic-system.sh for processing
            script_path = os.path.join(self.bash_scripts_path, "magic-system.sh")
            
            result = subprocess.run(
                [script_path, user_input],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr if result.stderr else None,
                "method": "bash_scripts",
                "script_used": "magic-system.sh"
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Script execution timeout",
                "method": "bash_scripts"
            }
        except Exception as e:
            self.logger.error(f"Bash script execution error: {e}")
            return {
                "success": False,
                "error": str(e),
                "method": "bash_scripts"
            }
    
    async def recovery_where_stopped(self) -> Dict[str, Any]:
        """Execute 'onde paramos?' using autonomous-recovery.sh"""
        try:
            script_path = os.path.join(self.bash_scripts_path, "autonomous-recovery.sh")
            
            result = subprocess.run(
                [script_path],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr if result.stderr else None,
                "method": "bash_scripts",
                "script_used": "autonomous-recovery.sh"
            }
            
        except Exception as e:
            self.logger.error(f"Recovery script error: {e}")
            return {
                "success": False,
                "error": str(e),
                "method": "bash_scripts"
            }
    
    async def emergency_freeze(self) -> Dict[str, Any]:
        """Execute emergency freeze using bash scripts"""
        try:
            script_path = os.path.join(self.bash_scripts_path, "emergency-absolute.sh")
            
            result = subprocess.run(
                [script_path, "freeze"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr if result.stderr else None,
                "method": "bash_scripts",
                "script_used": "emergency-absolute.sh freeze"
            }
            
        except Exception as e:
            self.logger.error(f"Emergency freeze error: {e}")
            return {
                "success": False,
                "error": str(e),
                "method": "bash_scripts"
            }
    
    async def emergency_unfreeze(self) -> Dict[str, Any]:
        """Execute emergency unfreeze using bash scripts"""
        try:
            script_path = os.path.join(self.bash_scripts_path, "emergency-absolute.sh")
            
            result = subprocess.run(
                [script_path, "unfreeze"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr if result.stderr else None,
                "method": "bash_scripts",
                "script_used": "emergency-absolute.sh unfreeze"
            }
            
        except Exception as e:
            self.logger.error(f"Emergency unfreeze error: {e}")
            return {
                "success": False,
                "error": str(e),
                "method": "bash_scripts"
            }
    
    async def system_status(self) -> Dict[str, Any]:
        """Get system status using bash scripts"""
        try:
            script_path = os.path.join(self.bash_scripts_path, "emergency-absolute.sh")
            
            result = subprocess.run(
                [script_path, "status"],
                capture_output=True,
                text=True,
                timeout=15
            )
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr if result.stderr else None,
                "method": "bash_scripts",
                "script_used": "emergency-absolute.sh status"
            }
            
        except Exception as e:
            self.logger.error(f"System status error: {e}")
            return {
                "success": False,
                "error": str(e),
                "method": "bash_scripts"
            }
