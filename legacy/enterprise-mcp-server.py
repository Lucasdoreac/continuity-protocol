#!/usr/bin/env python3
"""
Enterprise MCP Server
Servidor MCP dedicado para expor ferramentas enterprise como ferramentas nativas do Claude Desktop
"""

import os
import sys
import json
from pathlib import Path

# Adicionar paths necessários
current_dir = Path(__file__).parent
sys.path.append(str(current_dir / "project-states" / "mcp-continuity-service" / "src" / "mcp_tools"))

try:
    from mcp.server.fastmcp import FastMCP
    from enterprise_wrapper import enterprise_tools
except ImportError as e:
    print(f"Erro ao importar dependências: {e}")
    print("Instalando dependências...")
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "mcp"])
    from mcp.server.fastmcp import FastMCP
    from enterprise_wrapper import enterprise_tools

# Criar servidor MCP
mcp = FastMCP("Enterprise Continuity Tools")

@mcp.tool()
def context_register_project(project_id: str, name: str, description: str) -> dict:
    """
    Registra um novo projeto no sistema de continuidade
    
    Args:
        project_id: ID único do projeto
        name: Nome do projeto
        description: Descrição do projeto
        
    Returns:
        dict: Dados do projeto criado
    """
    return enterprise_tools.context_register_project(project_id, name, description)

@mcp.tool()
def context_store_artifact(content: str, artifact_type: str, project_id: str, metadata: str = "") -> dict:
    """
    Armazena um novo artefato no sistema compartilhado
    
    Args:
        content: Conteúdo do artefato
        artifact_type: Tipo do artefato (document, code, analysis, etc.)
        project_id: ID do projeto
        metadata: Metadados do artefato (JSON string)
        
    Returns:
        dict: Dados do artefato criado
    """
    return enterprise_tools.context_store_artifact(content, artifact_type, project_id, metadata)

@mcp.tool()
def context_get_project_context(project_id: str) -> dict:
    """
    Obtém o contexto completo de um projeto
    
    Args:
        project_id: ID do projeto
        
    Returns:
        dict: Contexto completo do projeto incluindo artefatos
    """
    return enterprise_tools.context_get_project_context(project_id)

@mcp.tool()
def context_get_available_tools() -> dict:
    """
    Lista todas as ferramentas enterprise disponíveis
    
    Returns:
        dict: Lista de ferramentas disponíveis
    """
    return enterprise_tools.get_available_tools()

@mcp.tool()
def context_system_status() -> dict:
    """
    Obtém status do sistema de continuidade
    
    Returns:
        dict: Status completo do sistema
    """
    try:
        # Verificar se sistema está funcionando
        test_result = enterprise_tools.get_available_tools()
        
        return {
            "success": True,
            "status": "operational",
            "enterprise_available": test_result.get("available", False),
            "tools_count": test_result.get("count", 0),
            "server_pid": os.getpid(),
            "working_directory": str(current_dir),
            "system_type": "hybrid_experimental_enterprise"
        }
    except Exception as e:
        return {
            "success": False,
            "status": "error",
            "error": str(e)
        }

if __name__ == "__main__":
    print("🚀 Iniciando Enterprise MCP Server...")
    print(f"📍 Working directory: {current_dir}")
    print(f"🔧 Server PID: {os.getpid()}")
    
    # Testar se enterprise tools estão disponíveis
    try:
        status = enterprise_tools.get_available_tools()
        print(f"✅ Enterprise tools: {status}")
    except Exception as e:
        print(f"❌ Erro ao carregar enterprise tools: {e}")
        sys.exit(1)
    
    print("🎯 Ferramentas MCP disponíveis:")
    print("   - context_register_project")
    print("   - context_store_artifact") 
    print("   - context_get_project_context")
    print("   - context_get_available_tools")
    print("   - context_system_status")
    print("")
    print("🔄 Servidor pronto para conectar com Claude Desktop...")
    
    # Iniciar servidor
    mcp.run()
