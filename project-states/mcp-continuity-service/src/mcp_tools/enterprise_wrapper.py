"""
Enterprise MCP Tools Wrapper
Integra ferramentas enterprise ao sistema experimental
"""

import os
import sys
import json
from typing import Dict, Any, Optional

# Adicionar path para ferramentas enterprise
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'enterprise_tools'))

try:
    from context_sharing import ContextSharingProtocol
    ENTERPRISE_AVAILABLE = True
except ImportError:
    ENTERPRISE_AVAILABLE = False

class EnterpriseMCPTools:
    def __init__(self):
        self.available = ENTERPRISE_AVAILABLE
        if self.available:
            self.protocol = ContextSharingProtocol()
    
    def context_register_project(self, project_id: str, name: str, description: str) -> Dict[str, Any]:
        """Registra um novo projeto no sistema"""
        if not self.available:
            return {"error": "Enterprise tools not available"}
        
        try:
            result = self.protocol.register_project(project_id, name, description)
            return {"success": True, "data": result}
        except Exception as e:
            return {"error": str(e)}
    
    def context_store_artifact(self, content: str, artifact_type: str, project_id: str, metadata: str = "") -> Dict[str, Any]:
        """Armazena novo artefato no sistema compartilhado"""
        if not self.available:
            return {"error": "Enterprise tools not available"}
        
        try:
            result = self.protocol.store_artifact(content, artifact_type, project_id, metadata)
            return {"success": True, "data": result}
        except Exception as e:
            return {"error": str(e)}
    
    def context_get_project_context(self, project_id: str) -> Dict[str, Any]:
        """Obtém contexto completo de um projeto"""
        if not self.available:
            return {"error": "Enterprise tools not available"}
        
        try:
            result = self.protocol.get_project_context(project_id)
            return {"success": True, "data": result}
        except Exception as e:
            return {"error": str(e)}
    
    def get_available_tools(self) -> Dict[str, Any]:
        """Lista ferramentas enterprise disponíveis"""
        tools = [
            "context_register_project",
            "context_store_artifact", 
            "context_get_project_context",
            "context_get_artifact",
            "context_get_project_artifacts"
        ]
        
        return {
            "available": self.available,
            "tools": tools,
            "count": len(tools) if self.available else 0
        }

# Instância global
enterprise_tools = EnterpriseMCPTools()
