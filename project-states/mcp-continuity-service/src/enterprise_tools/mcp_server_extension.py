#!/usr/bin/env python3
"""
MCP Server Extension - Continuity Protocol
Extensão para o servidor MCP com funcionalidades de compartilhamento de contexto
"""

import os
import sys
import json
import importlib.util
from typing import Dict, List, Any, Optional, Callable

# Importar FastMCP
try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    print("Instalando MCP...")
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "mcp"])
    from mcp.server.fastmcp import FastMCP

# Importar ContextSharingProtocol
try:
    from core.mcp.context_sharing import ContextSharingProtocol
except ImportError:
    # Adicionar diretório pai ao path
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from core.mcp.context_sharing import ContextSharingProtocol

class MCPServerExtension:
    """
    Extensão para o servidor MCP com funcionalidades de compartilhamento de contexto
    """
    
    def __init__(self, server_name: str, agent_type: str):
        """
        Inicializa a extensão do servidor MCP
        
        Args:
            server_name: Nome do servidor MCP
            agent_type: Tipo de agente (e.g., "amazon_q_cli", "claude_desktop")
        """
        self.server_name = server_name
        self.agent_type = agent_type
        self.agent_id = f"{agent_type}_{os.getpid()}"
        
        # Inicializar FastMCP
        self.mcp = FastMCP(server_name)
        
        # Inicializar protocolo de compartilhamento de contexto
        self.context_protocol = ContextSharingProtocol()
        
        # Registrar agente
        self.context_protocol.register_agent(
            self.agent_id,
            self.agent_type,
            ["context_sharing", "artifact_storage", "project_management"]
        )
        
        # Registrar ferramentas MCP
        self._register_tools()
    
    def _register_tools(self) -> None:
        """Registra as ferramentas MCP para compartilhamento de contexto"""
        
        @self.mcp.tool()
        def context_register_project(project_id: str, project_name: str, description: str) -> str:
            """
            Registra um projeto no protocolo de compartilhamento de contexto
            
            Args:
                project_id: ID do projeto
                project_name: Nome do projeto
                description: Descrição do projeto
                
            Returns:
                str: Resultado da operação em formato JSON
            """
            # Atualizar atividade do agente
            self.context_protocol.update_agent_activity(self.agent_id)
            
            # Registrar projeto
            project_info = self.context_protocol.register_project(project_id, project_name, description)
            
            # Associar agente ao projeto
            self.context_protocol.associate_agent_with_project(self.agent_id, project_id)
            
            return json.dumps(project_info, indent=2)
        
        @self.mcp.tool()
        def context_store_artifact(content: str, artifact_type: str, project_id: str, metadata_json: str = "{}") -> str:
            """
            Armazena um artefato no protocolo de compartilhamento de contexto
            
            Args:
                content: Conteúdo do artefato
                artifact_type: Tipo do artefato (e.g., "plan", "code", "document")
                project_id: ID do projeto
                metadata_json: Metadados adicionais em formato JSON (opcional)
                
            Returns:
                str: Resultado da operação em formato JSON
            """
            # Atualizar atividade do agente
            self.context_protocol.update_agent_activity(self.agent_id)
            
            # Parsear metadados
            try:
                metadata = json.loads(metadata_json)
            except:
                metadata = {}
            
            # Armazenar artefato
            artifact_info = self.context_protocol.store_artifact(
                content,
                artifact_type,
                project_id,
                self.agent_id,
                metadata
            )
            
            return json.dumps(artifact_info, indent=2)
        
        @self.mcp.tool()
        def context_get_artifact(artifact_id: str) -> str:
            """
            Obtém um artefato pelo ID
            
            Args:
                artifact_id: ID do artefato
                
            Returns:
                str: Conteúdo e informações do artefato em formato JSON
            """
            # Atualizar atividade do agente
            self.context_protocol.update_agent_activity(self.agent_id)
            
            # Obter artefato
            artifact = self.context_protocol.get_artifact(artifact_id)
            
            if artifact:
                return json.dumps(artifact, indent=2)
            else:
                return json.dumps({"error": "Artifact not found"}, indent=2)
        
        @self.mcp.tool()
        def context_get_project_artifacts(project_id: str, artifact_type: str = None) -> str:
            """
            Obtém todos os artefatos de um projeto
            
            Args:
                project_id: ID do projeto
                artifact_type: Tipo de artefato para filtrar (opcional)
                
            Returns:
                str: Lista de artefatos em formato JSON
            """
            # Atualizar atividade do agente
            self.context_protocol.update_agent_activity(self.agent_id)
            
            # Obter artefatos
            artifacts = self.context_protocol.get_project_artifacts(project_id, artifact_type)
            
            return json.dumps(artifacts, indent=2)
        
        @self.mcp.tool()
        def context_get_latest_artifact(project_id: str, artifact_type: str) -> str:
            """
            Obtém o artefato mais recente de um projeto por tipo
            
            Args:
                project_id: ID do projeto
                artifact_type: Tipo de artefato
                
            Returns:
                str: Artefato mais recente em formato JSON
            """
            # Atualizar atividade do agente
            self.context_protocol.update_agent_activity(self.agent_id)
            
            # Obter artefato mais recente
            artifact = self.context_protocol.get_latest_project_artifact(project_id, artifact_type)
            
            if artifact:
                return json.dumps(artifact, indent=2)
            else:
                return json.dumps({"error": "No artifacts found"}, indent=2)
        
        @self.mcp.tool()
        def context_get_project_context(project_id: str) -> str:
            """
            Obtém o contexto completo de um projeto
            
            Args:
                project_id: ID do projeto
                
            Returns:
                str: Contexto completo do projeto em formato JSON
            """
            # Atualizar atividade do agente
            self.context_protocol.update_agent_activity(self.agent_id)
            
            # Obter contexto do projeto
            context = self.context_protocol.get_project_context(project_id)
            
            return json.dumps(context, indent=2)
        
        @self.mcp.tool()
        def context_sync_artifact_to_file(artifact_id: str, file_path: str) -> str:
            """
            Sincroniza um artefato para um arquivo no sistema
            
            Args:
                artifact_id: ID do artefato
                file_path: Caminho do arquivo
                
            Returns:
                str: Resultado da operação em formato JSON
            """
            # Atualizar atividade do agente
            self.context_protocol.update_agent_activity(self.agent_id)
            
            # Sincronizar artefato para arquivo
            success = self.context_protocol.sync_artifact_to_file(artifact_id, file_path)
            
            if success:
                return json.dumps({"success": True, "file_path": file_path}, indent=2)
            else:
                return json.dumps({"success": False, "error": "Failed to sync artifact to file"}, indent=2)
        
        @self.mcp.tool()
        def context_sync_file_to_artifact(file_path: str, artifact_id: str) -> str:
            """
            Sincroniza um arquivo do sistema para um artefato
            
            Args:
                file_path: Caminho do arquivo
                artifact_id: ID do artefato
                
            Returns:
                str: Resultado da operação em formato JSON
            """
            # Atualizar atividade do agente
            self.context_protocol.update_agent_activity(self.agent_id)
            
            # Sincronizar arquivo para artefato
            success = self.context_protocol.sync_file_to_artifact(file_path, artifact_id)
            
            if success:
                return json.dumps({"success": True, "artifact_id": artifact_id}, indent=2)
            else:
                return json.dumps({"success": False, "error": "Failed to sync file to artifact"}, indent=2)
        
        @self.mcp.tool()
        def context_create_artifact_from_file(file_path: str, artifact_type: str, project_id: str, metadata_json: str = "{}") -> str:
            """
            Cria um artefato a partir de um arquivo
            
            Args:
                file_path: Caminho do arquivo
                artifact_type: Tipo do artefato
                project_id: ID do projeto
                metadata_json: Metadados adicionais em formato JSON (opcional)
                
            Returns:
                str: Informações do artefato criado em formato JSON
            """
            # Atualizar atividade do agente
            self.context_protocol.update_agent_activity(self.agent_id)
            
            # Parsear metadados
            try:
                metadata = json.loads(metadata_json)
            except:
                metadata = {}
            
            # Criar artefato a partir do arquivo
            artifact = self.context_protocol.create_artifact_from_file(
                file_path,
                artifact_type,
                project_id,
                self.agent_id,
                metadata
            )
            
            if artifact:
                return json.dumps(artifact, indent=2)
            else:
                return json.dumps({"error": "Failed to create artifact from file"}, indent=2)
    
    def run(self, transport: str = "stdio") -> None:
        """
        Executa o servidor MCP
        
        Args:
            transport: Tipo de transporte ("stdio" ou "http")
        """
        print(f"Starting MCP Server Extension ({self.server_name}) with agent ID: {self.agent_id}")
        print(f"Agent type: {self.agent_type}")
        print(f"Transport: {transport}")
        
        # Executar servidor MCP
        self.mcp.run(transport=transport)

# Função para criar e executar o servidor MCP estendido
def create_and_run_server(server_name: str, agent_type: str, transport: str = "stdio") -> None:
    """
    Cria e executa um servidor MCP estendido
    
    Args:
        server_name: Nome do servidor MCP
        agent_type: Tipo de agente
        transport: Tipo de transporte ("stdio" ou "http")
    """
    server = MCPServerExtension(server_name, agent_type)
    server.run(transport=transport)

if __name__ == "__main__":
    # Parâmetros padrão
    server_name = "continuity-protocol"
    agent_type = "generic"
    transport = "stdio"
    
    # Processar argumentos de linha de comando
    if len(sys.argv) > 1:
        server_name = sys.argv[1]
    if len(sys.argv) > 2:
        agent_type = sys.argv[2]
    if len(sys.argv) > 3:
        transport = sys.argv[3]
    
    # Criar e executar servidor
    create_and_run_server(server_name, agent_type, transport)
