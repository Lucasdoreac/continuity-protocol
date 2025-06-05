#!/usr/bin/env python3
"""
Secure MCP Server Extension - Continuity Protocol
Versão segura da extensão do servidor MCP com safeguards e melhorias de segurança
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

# Importar componentes de segurança
try:
    from core.mcp.integration import secure_context_protocol
    from core.mcp.safeguards import safeguards, apply_safeguards
    from core.mcp.schema_validation import SchemaValidator
    from core.mcp.rate_limiting import rate_limiter, rate_limit
    from core.mcp.auth import auth_system, require_auth
except ImportError:
    # Adicionar diretório pai ao path
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from core.mcp.integration import secure_context_protocol
    from core.mcp.safeguards import safeguards, apply_safeguards
    from core.mcp.schema_validation import SchemaValidator
    from core.mcp.rate_limiting import rate_limiter, rate_limit
    from core.mcp.auth import auth_system, require_auth

class SecureMCPServerExtension:
    """
    Versão segura da extensão do servidor MCP com safeguards e melhorias de segurança
    """
    
    def __init__(self, server_name: str, agent_type: str):
        """
        Inicializa a extensão segura do servidor MCP
        
        Args:
            server_name: Nome do servidor MCP
            agent_type: Tipo de agente (e.g., "amazon_q_cli", "claude_desktop")
        """
        self.server_name = server_name
        self.agent_type = agent_type
        self.agent_id = f"{agent_type}_{os.getpid()}"
        
        # Inicializar FastMCP
        self.mcp = FastMCP(server_name)
        
        # Usar protocolo de compartilhamento de contexto seguro
        self.context_protocol = secure_context_protocol
        
        # Registrar agente
        self.context_protocol.register_agent(
            self.agent_id,
            self.agent_type,
            ["context_sharing", "artifact_storage", "project_management"]
        )
        
        # Registrar ferramentas MCP
        self._register_tools()
        
        print(f"Secure MCP Server Extension initialized for {agent_type} with PID {os.getpid()}")
        print(f"Safeguards active: max_lines={safeguards.max_lines_per_operation}, "
              f"max_session_time={safeguards.max_session_time_minutes}min")
    
    def _register_tools(self) -> None:
        """Registra as ferramentas MCP para compartilhamento de contexto seguro"""
        
        @self.mcp.tool()
        @rate_limit("context_register_project", 50, 3600)  # 50 projetos por hora
        @apply_safeguards
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
            
            try:
                # Validar dados do projeto
                project_data = {
                    "id": project_id,
                    "name": project_name,
                    "description": description
                }
                
                validation_result = SchemaValidator.validate_project(project_data)
                if not validation_result["valid"]:
                    return json.dumps({
                        "error": f"Invalid project data: {validation_result['errors']}"
                    }, indent=2)
                
                # Sanitizar project_id para evitar problemas de path
                project_id = SchemaValidator.sanitize_path(project_id)
                
                # Registrar projeto
                project_info = self.context_protocol.register_project(project_id, project_name, description)
                
                # Associar agente ao projeto
                self.context_protocol.associate_agent_with_project(self.agent_id, project_id)
                
                return json.dumps(project_info, indent=2)
            except Exception as e:
                return json.dumps({
                    "error": str(e)
                }, indent=2)
        
        @self.mcp.tool()
        @rate_limit("context_store_artifact", 100, 3600)  # 100 artefatos por hora
        @apply_safeguards
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
            
            try:
                # Verificar tamanho do conteúdo
                content_check = safeguards.check_content_size(content)
                if not content_check["passed"]:
                    # Se conteúdo for muito grande, dividir em chunks
                    print(f"[WARNING] Content too large ({content_check['line_count']} lines). Chunking...")
                    chunks = safeguards.chunk_content(content)
                    
                    # Armazenar apenas o primeiro chunk e avisar
                    content = chunks[0]
                    print(f"[WARNING] Only storing first chunk ({len(chunks[0].splitlines())} lines). "
                         f"Content truncated from {content_check['line_count']} lines.")
                
                # Parsear metadados
                try:
                    metadata = json.loads(metadata_json)
                except:
                    metadata = {}
                
                # Validar metadados
                validation_result = SchemaValidator.validate_artifact_metadata(metadata)
                if not validation_result["valid"]:
                    # Se metadados inválidos, sanitizar
                    print(f"[WARNING] Invalid metadata: {validation_result['errors']}. Sanitizing...")
                    metadata = SchemaValidator.sanitize_metadata(metadata)
                
                # Sanitizar project_id e artifact_type para evitar problemas de path
                project_id = SchemaValidator.sanitize_path(project_id)
                artifact_type = SchemaValidator.sanitize_path(artifact_type)
                
                # Armazenar artefato
                artifact_info = self.context_protocol.store_artifact(
                    content,
                    artifact_type,
                    project_id,
                    self.agent_id,
                    metadata
                )
                
                return json.dumps(artifact_info, indent=2)
            except Exception as e:
                return json.dumps({
                    "error": str(e)
                }, indent=2)
        
        @self.mcp.tool()
        @rate_limit("context_get_artifact", 300, 3600)  # 300 consultas por hora
        @apply_safeguards
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
            
            try:
                # Sanitizar artifact_id para evitar problemas de path
                artifact_id = SchemaValidator.sanitize_path(artifact_id)
                
                # Obter artefato
                artifact = self.context_protocol.get_artifact(artifact_id)
                
                if artifact:
                    return json.dumps(artifact, indent=2)
                else:
                    return json.dumps({"error": "Artifact not found"}, indent=2)
            except Exception as e:
                return json.dumps({
                    "error": str(e)
                }, indent=2)
        
        @self.mcp.tool()
        @rate_limit("context_get_project_artifacts", 200, 3600)  # 200 consultas por hora
        @apply_safeguards
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
            
            try:
                # Sanitizar project_id e artifact_type para evitar problemas de path
                project_id = SchemaValidator.sanitize_path(project_id)
                if artifact_type:
                    artifact_type = SchemaValidator.sanitize_path(artifact_type)
                
                # Obter artefatos
                artifacts = self.context_protocol.get_project_artifacts(project_id, artifact_type)
                
                return json.dumps(artifacts, indent=2)
            except Exception as e:
                return json.dumps({
                    "error": str(e)
                }, indent=2)
        
        @self.mcp.tool()
        @rate_limit("context_get_latest_artifact", 200, 3600)  # 200 consultas por hora
        @apply_safeguards
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
            
            try:
                # Sanitizar project_id e artifact_type para evitar problemas de path
                project_id = SchemaValidator.sanitize_path(project_id)
                artifact_type = SchemaValidator.sanitize_path(artifact_type)
                
                # Obter artefato mais recente
                artifact = self.context_protocol.get_latest_project_artifact(project_id, artifact_type)
                
                if artifact:
                    return json.dumps(artifact, indent=2)
                else:
                    return json.dumps({"error": "No artifacts found"}, indent=2)
            except Exception as e:
                return json.dumps({
                    "error": str(e)
                }, indent=2)
        
        @self.mcp.tool()
        @rate_limit("context_get_project_context", 200, 3600)  # 200 consultas por hora
        @apply_safeguards
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
            
            try:
                # Sanitizar project_id para evitar problemas de path
                project_id = SchemaValidator.sanitize_path(project_id)
                
                # Obter contexto do projeto
                context = self.context_protocol.get_project_context(project_id)
                
                return json.dumps(context, indent=2)
            except Exception as e:
                return json.dumps({
                    "error": str(e)
                }, indent=2)
        
        @self.mcp.tool()
        @rate_limit("context_sync_artifact_to_file", 50, 3600)  # 50 sincronizações por hora
        @apply_safeguards
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
            
            try:
                # Sanitizar artifact_id e file_path para evitar problemas de path
                artifact_id = SchemaValidator.sanitize_path(artifact_id)
                file_path = SchemaValidator.sanitize_path(file_path)
                
                # Sincronizar artefato para arquivo
                success = self.context_protocol.sync_artifact_to_file(artifact_id, file_path)
                
                if success:
                    return json.dumps({"success": True, "file_path": file_path}, indent=2)
                else:
                    return json.dumps({"success": False, "error": "Failed to sync artifact to file"}, indent=2)
            except Exception as e:
                return json.dumps({
                    "error": str(e)
                }, indent=2)
        
        @self.mcp.tool()
        @rate_limit("context_sync_file_to_artifact", 50, 3600)  # 50 sincronizações por hora
        @apply_safeguards
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
            
            try:
                # Sanitizar file_path e artifact_id para evitar problemas de path
                file_path = SchemaValidator.sanitize_path(file_path)
                artifact_id = SchemaValidator.sanitize_path(artifact_id)
                
                # Sincronizar arquivo para artefato
                success = self.context_protocol.sync_file_to_artifact(file_path, artifact_id)
                
                if success:
                    return json.dumps({"success": True, "artifact_id": artifact_id}, indent=2)
                else:
                    return json.dumps({"success": False, "error": "Failed to sync file to artifact"}, indent=2)
            except Exception as e:
                return json.dumps({
                    "error": str(e)
                }, indent=2)
        
        @self.mcp.tool()
        @rate_limit("context_create_artifact_from_file", 50, 3600)  # 50 criações por hora
        @apply_safeguards
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
            
            try:
                # Sanitizar file_path, artifact_type e project_id para evitar problemas de path
                file_path = SchemaValidator.sanitize_path(file_path)
                artifact_type = SchemaValidator.sanitize_path(artifact_type)
                project_id = SchemaValidator.sanitize_path(project_id)
                
                # Parsear metadados
                try:
                    metadata = json.loads(metadata_json)
                except:
                    metadata = {}
                
                # Validar metadados
                validation_result = SchemaValidator.validate_artifact_metadata(metadata)
                if not validation_result["valid"]:
                    # Se metadados inválidos, sanitizar
                    print(f"[WARNING] Invalid metadata: {validation_result['errors']}. Sanitizing...")
                    metadata = SchemaValidator.sanitize_metadata(metadata)
                
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
            except Exception as e:
                return json.dumps({
                    "error": str(e)
                }, indent=2)
        
        @self.mcp.tool()
        @apply_safeguards
        def safeguards_status() -> str:
            """
            Obtém status atual dos safeguards
            
            Returns:
                str: Status dos safeguards em formato JSON
            """
            try:
                status = safeguards.get_status()
                return json.dumps(status, indent=2)
            except Exception as e:
                return json.dumps({
                    "error": str(e)
                }, indent=2)
        
        @self.mcp.tool()
        @apply_safeguards
        def rate_limiter_status(operation: str = None) -> str:
            """
            Obtém status atual do rate limiter
            
            Args:
                operation: Nome da operação (opcional)
                
            Returns:
                str: Status do rate limiter em formato JSON
            """
            try:
                status = rate_limiter.get_status(operation)
                return json.dumps(status, indent=2)
            except Exception as e:
                return json.dumps({
                    "error": str(e)
                }, indent=2)
        
        @self.mcp.tool()
        @apply_safeguards
        def create_checkpoint(checkpoint_type: str = "manual") -> str:
            """
            Cria um checkpoint do estado atual
            
            Args:
                checkpoint_type: Tipo de checkpoint ("manual", "auto", "termination")
                
            Returns:
                str: Informações do checkpoint em formato JSON
            """
            try:
                checkpoint = safeguards.create_checkpoint(checkpoint_type)
                return json.dumps(checkpoint, indent=2)
            except Exception as e:
                return json.dumps({
                    "error": str(e)
                }, indent=2)
    
    def run(self, transport: str = "stdio") -> None:
        """
        Executa o servidor MCP
        
        Args:
            transport: Tipo de transporte ("stdio" ou "http")
        """
        print(f"Starting Secure MCP Server Extension ({self.server_name}) with agent ID: {self.agent_id}")
        print(f"Agent type: {self.agent_type}")
        print(f"Transport: {transport}")
        print(f"Safeguards: max_lines={safeguards.max_lines_per_operation}, "
              f"max_session_time={safeguards.max_session_time_minutes}min, "
              f"checkpoint_interval={safeguards.checkpoint_interval_minutes}min")
        
        # Criar checkpoint inicial
        safeguards.create_checkpoint("startup")
        
        # Executar servidor MCP
        self.mcp.run(transport=transport)

# Função para criar e executar o servidor MCP estendido seguro
def create_and_run_secure_server(server_name: str, agent_type: str, transport: str = "stdio") -> None:
    """
    Cria e executa um servidor MCP estendido seguro
    
    Args:
        server_name: Nome do servidor MCP
        agent_type: Tipo de agente
        transport: Tipo de transporte ("stdio" ou "http")
    """
    server = SecureMCPServerExtension(server_name, agent_type)
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
    create_and_run_secure_server(server_name, agent_type, transport)
