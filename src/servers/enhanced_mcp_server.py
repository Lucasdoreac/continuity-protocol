#!/usr/bin/env python3
"""
Enhanced MCP Server - Continuity Protocol
Servidor MCP aprimorado com recursos da Etapa 2
"""

import os
import sys
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Union

# Importar componentes
try:
    from core.mcp.integration_v2 import enhanced_context_protocol
    from core.mcp.versioning import versioning_system
    from core.mcp.backup import backup_system
    from core.mcp.notification import notification_system
    from core.mcp.search import search_system
    from core.mcp.safeguards import safeguards
except ImportError:
    # Adicionar diretório pai ao path
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from core.mcp.integration_v2 import enhanced_context_protocol
    from core.mcp.versioning import versioning_system
    from core.mcp.backup import backup_system
    from core.mcp.notification import notification_system
    from core.mcp.search import search_system
    from core.mcp.safeguards import safeguards

# Importar FastMCP
try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    print("Instalando MCP...")
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "mcp"])
    from mcp.server.fastmcp import FastMCP

class EnhancedMCPServer:
    """
    Servidor MCP aprimorado com recursos da Etapa 2
    """
    
    def __init__(self, server_name: str = "enhanced-continuity-protocol"):
        """
        Inicializa o servidor MCP aprimorado
        
        Args:
            server_name: Nome do servidor MCP
        """
        self.server_name = server_name
        
        # Inicializar FastMCP
        self.mcp = FastMCP(server_name)
        
        # Usar protocolo de compartilhamento de contexto aprimorado
        self.context_protocol = enhanced_context_protocol
        
        # Registrar ferramentas MCP
        self._register_tools()
        
        print(f"Enhanced MCP Server initialized with name: {server_name}")
        print(f"Safeguards active: max_lines={safeguards.max_lines_per_operation}, "
              f"max_session_time={safeguards.max_session_time_minutes}min")
    
    def _register_tools(self) -> None:
        """Registra as ferramentas MCP aprimoradas"""
        
        # Ferramentas de artefatos
        self._register_artifact_tools()
        
        # Ferramentas de versionamento
        self._register_versioning_tools()
        
        # Ferramentas de backup
        self._register_backup_tools()
        
        # Ferramentas de notificação
        self._register_notification_tools()
        
        # Ferramentas de busca
        self._register_search_tools()
        
        # Ferramentas de sistema
        self._register_system_tools()
    
    def _register_artifact_tools(self) -> None:
        """Registra ferramentas relacionadas a artefatos"""
        
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
            try:
                project_info = self.context_protocol.register_project(project_id, project_name, description)
                return json.dumps(project_info, indent=2)
            except Exception as e:
                return json.dumps({"error": str(e)}, indent=2)
        
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
            try:
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
                    "enhanced_mcp_server",
                    metadata
                )
                
                return json.dumps(artifact_info, indent=2)
            except Exception as e:
                return json.dumps({"error": str(e)}, indent=2)
        
        @self.mcp.tool()
        def context_update_artifact(artifact_id: str, content: str, metadata_json: str = "{}", 
                                  change_level: str = None, changes: str = None) -> str:
            """
            Atualiza um artefato existente
            
            Args:
                artifact_id: ID do artefato
                content: Novo conteúdo do artefato
                metadata_json: Metadados atualizados em formato JSON (opcional)
                change_level: Nível de mudança ("major", "minor", "patch")
                changes: Descrição das mudanças
                
            Returns:
                str: Resultado da operação em formato JSON
            """
            try:
                # Parsear metadados
                try:
                    metadata = json.loads(metadata_json)
                except:
                    metadata = {}
                
                # Atualizar artefato
                result = self.context_protocol.update_artifact(
                    artifact_id,
                    content,
                    "enhanced_mcp_server",
                    metadata,
                    change_level,
                    changes
                )
                
                return json.dumps(result, indent=2)
            except Exception as e:
                return json.dumps({"error": str(e)}, indent=2)
        
        @self.mcp.tool()
        def context_get_artifact(artifact_id: str) -> str:
            """
            Obtém um artefato pelo ID
            
            Args:
                artifact_id: ID do artefato
                
            Returns:
                str: Conteúdo e informações do artefato em formato JSON
            """
            try:
                artifact = self.context_protocol.get_artifact(artifact_id)
                
                if artifact:
                    return json.dumps(artifact, indent=2)
                else:
                    return json.dumps({"error": "Artifact not found"}, indent=2)
            except Exception as e:
                return json.dumps({"error": str(e)}, indent=2)
        
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
            try:
                artifacts = self.context_protocol.get_project_artifacts(project_id, artifact_type)
                return json.dumps(artifacts, indent=2)
            except Exception as e:
                return json.dumps({"error": str(e)}, indent=2)
        
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
            try:
                artifact = self.context_protocol.get_latest_project_artifact(project_id, artifact_type)
                
                if artifact:
                    return json.dumps(artifact, indent=2)
                else:
                    return json.dumps({"error": "No artifacts found"}, indent=2)
            except Exception as e:
                return json.dumps({"error": str(e)}, indent=2)
        
        @self.mcp.tool()
        def context_get_project_context(project_id: str) -> str:
            """
            Obtém o contexto completo de um projeto
            
            Args:
                project_id: ID do projeto
                
            Returns:
                str: Contexto completo do projeto em formato JSON
            """
            try:
                context = self.context_protocol.get_project_context(project_id)
                return json.dumps(context, indent=2)
            except Exception as e:
                return json.dumps({"error": str(e)}, indent=2)
    
    def _register_versioning_tools(self) -> None:
        """Registra ferramentas relacionadas a versionamento"""
        
        @self.mcp.tool()
        def context_get_artifact_version(artifact_id: str, version: str = None) -> str:
            """
            Obtém versão específica de um artefato
            
            Args:
                artifact_id: ID do artefato
                version: Versão específica (usa versão atual se None)
                
            Returns:
                str: Informações e conteúdo da versão em formato JSON
            """
            try:
                result = self.context_protocol.get_artifact_version(artifact_id, version)
                return json.dumps(result, indent=2)
            except Exception as e:
                return json.dumps({"error": str(e)}, indent=2)
        
        @self.mcp.tool()
        def context_get_artifact_history(artifact_id: str) -> str:
            """
            Obtém histórico de versões de um artefato
            
            Args:
                artifact_id: ID do artefato
                
            Returns:
                str: Histórico de versões em formato JSON
            """
            try:
                result = self.context_protocol.get_artifact_history(artifact_id)
                return json.dumps(result, indent=2)
            except Exception as e:
                return json.dumps({"error": str(e)}, indent=2)
        
        @self.mcp.tool()
        def context_compare_artifact_versions(artifact_id: str, version1: str, version2: str) -> str:
            """
            Compara duas versões de um artefato
            
            Args:
                artifact_id: ID do artefato
                version1: Primeira versão
                version2: Segunda versão
                
            Returns:
                str: Resultado da comparação em formato JSON
            """
            try:
                result = self.context_protocol.compare_artifact_versions(artifact_id, version1, version2)
                return json.dumps(result, indent=2)
            except Exception as e:
                return json.dumps({"error": str(e)}, indent=2)
        
        @self.mcp.tool()
        def context_revert_artifact(artifact_id: str, version: str) -> str:
            """
            Reverte artefato para versão específica
            
            Args:
                artifact_id: ID do artefato
                version: Versão para reverter
                
            Returns:
                str: Informações da nova versão criada em formato JSON
            """
            try:
                result = self.context_protocol.revert_artifact(artifact_id, version)
                return json.dumps(result, indent=2)
            except Exception as e:
                return json.dumps({"error": str(e)}, indent=2)
    
    def _register_backup_tools(self) -> None:
        """Registra ferramentas relacionadas a backup"""
        
        @self.mcp.tool()
        def context_create_backup(backup_type: str = "full", description: str = None) -> str:
            """
            Cria backup do sistema
            
            Args:
                backup_type: Tipo de backup ("full", "incremental")
                description: Descrição do backup
                
            Returns:
                str: Informações do backup criado em formato JSON
            """
            try:
                result = self.context_protocol.create_backup(backup_type, description)
                return json.dumps(result, indent=2)
            except Exception as e:
                return json.dumps({"error": str(e)}, indent=2)
        
        @self.mcp.tool()
        def context_git_commit_changes(message: str = None) -> str:
            """
            Commit de alterações no repositório Git
            
            Args:
                message: Mensagem do commit
                
            Returns:
                str: Resultado do commit em formato JSON
            """
            try:
                result = self.context_protocol.git_commit_changes(message)
                return json.dumps(result, indent=2)
            except Exception as e:
                return json.dumps({"error": str(e)}, indent=2)
        
        @self.mcp.tool()
        def context_get_backups_list() -> str:
            """
            Obtém lista de backups
            
            Returns:
                str: Lista de backups em formato JSON
            """
            try:
                result = backup_system.get_backups_list()
                return json.dumps(result, indent=2)
            except Exception as e:
                return json.dumps({"error": str(e)}, indent=2)
        
        @self.mcp.tool()
        def context_restore_backup(backup_id: str) -> str:
            """
            Restaura backup
            
            Args:
                backup_id: ID do backup
                
            Returns:
                str: Resultado da restauração em formato JSON
            """
            try:
                result = backup_system.restore_backup(backup_id)
                return json.dumps(result, indent=2)
            except Exception as e:
                return json.dumps({"error": str(e)}, indent=2)
    
    def _register_notification_tools(self) -> None:
        """Registra ferramentas relacionadas a notificações"""
        
        @self.mcp.tool()
        def context_create_notification(title: str, message: str, notification_type: str = "info",
                                      source: str = "system", metadata_json: str = "{}") -> str:
            """
            Cria uma notificação
            
            Args:
                title: Título da notificação
                message: Mensagem da notificação
                notification_type: Tipo da notificação ("info", "warning", "error", "success")
                source: Fonte da notificação
                metadata_json: Metadados adicionais em formato JSON (opcional)
                
            Returns:
                str: Informações da notificação criada em formato JSON
            """
            try:
                # Parsear metadados
                try:
                    metadata = json.loads(metadata_json)
                except:
                    metadata = {}
                
                result = self.context_protocol.create_notification(title, message, notification_type, source, metadata)
                return json.dumps(result, indent=2)
            except Exception as e:
                return json.dumps({"error": str(e)}, indent=2)
        
        @self.mcp.tool()
        def context_get_notifications(limit: int = 10, offset: int = 0, unread_only: bool = False) -> str:
            """
            Obtém lista de notificações
            
            Args:
                limit: Número máximo de notificações
                offset: Deslocamento para paginação
                unread_only: Se True, retorna apenas notificações não lidas
                
            Returns:
                str: Lista de notificações em formato JSON
            """
            try:
                result = self.context_protocol.get_notifications(limit, offset, unread_only)
                return json.dumps(result, indent=2)
            except Exception as e:
                return json.dumps({"error": str(e)}, indent=2)
        
        @self.mcp.tool()
        def context_mark_notification_as_read(notification_id: str) -> str:
            """
            Marca notificação como lida
            
            Args:
                notification_id: ID da notificação
                
            Returns:
                str: Resultado da operação em formato JSON
            """
            try:
                result = self.context_protocol.mark_notification_as_read(notification_id)
                return json.dumps(result, indent=2)
            except Exception as e:
                return json.dumps({"error": str(e)}, indent=2)
        
        @self.mcp.tool()
        def context_mark_all_notifications_as_read() -> str:
            """
            Marca todas as notificações como lidas
            
            Returns:
                str: Resultado da operação em formato JSON
            """
            try:
                result = notification_system.mark_all_as_read()
                return json.dumps(result, indent=2)
            except Exception as e:
                return json.dumps({"error": str(e)}, indent=2)
    
    def _register_search_tools(self) -> None:
        """Registra ferramentas relacionadas a busca"""
        
        @self.mcp.tool()
        def context_search_artifacts(query: str, artifact_type: str = None, 
                                   created_by: str = None, limit: int = 10) -> str:
            """
            Busca artefatos por termos
            
            Args:
                query: Termos de busca
                artifact_type: Filtro por tipo de artefato
                created_by: Filtro por criador
                limit: Número máximo de resultados
                
            Returns:
                str: Resultados da busca em formato JSON
            """
            try:
                result = self.context_protocol.search_artifacts(query, artifact_type, created_by, limit)
                return json.dumps(result, indent=2)
            except Exception as e:
                return json.dumps({"error": str(e)}, indent=2)
        
        @self.mcp.tool()
        def context_search_by_metadata(metadata_json: str, limit: int = 10) -> str:
            """
            Busca artefatos por metadados
            
            Args:
                metadata_json: Filtros de metadados em formato JSON
                limit: Número máximo de resultados
                
            Returns:
                str: Resultados da busca em formato JSON
            """
            try:
                # Parsear metadados
                try:
                    metadata_filters = json.loads(metadata_json)
                except:
                    return json.dumps({"error": "Invalid metadata JSON"}, indent=2)
                
                result = self.context_protocol.search_by_metadata(metadata_filters, limit)
                return json.dumps(result, indent=2)
            except Exception as e:
                return json.dumps({"error": str(e)}, indent=2)
        
        @self.mcp.tool()
        def context_reindex_all_artifacts() -> str:
            """
            Reindexar todos os artefatos
            
            Returns:
                str: Resultado da reindexação em formato JSON
            """
            try:
                result = self.context_protocol.reindex_all_artifacts()
                return json.dumps(result, indent=2)
            except Exception as e:
                return json.dumps({"error": str(e)}, indent=2)
        
        @self.mcp.tool()
        def context_get_search_stats() -> str:
            """
            Obtém estatísticas do índice de busca
            
            Returns:
                str: Estatísticas do índice em formato JSON
            """
            try:
                result = search_system.get_index_stats()
                return json.dumps(result, indent=2)
            except Exception as e:
                return json.dumps({"error": str(e)}, indent=2)
    
    def _register_system_tools(self) -> None:
        """Registra ferramentas relacionadas ao sistema"""
        
        @self.mcp.tool()
        def context_get_safeguards_status() -> str:
            """
            Obtém status atual dos safeguards
            
            Returns:
                str: Status dos safeguards em formato JSON
            """
            try:
                status = safeguards.get_status()
                return json.dumps(status, indent=2)
            except Exception as e:
                return json.dumps({"error": str(e)}, indent=2)
        
        @self.mcp.tool()
        def context_create_checkpoint(checkpoint_type: str = "manual") -> str:
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
                return json.dumps({"error": str(e)}, indent=2)
        
        @self.mcp.tool()
        def context_get_system_status() -> str:
            """
            Obtém status completo do sistema
            
            Returns:
                str: Status do sistema em formato JSON
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
        Executa o servidor MCP
        
        Args:
            transport: Tipo de transporte ("stdio" ou "http")
        """
        print(f"Starting Enhanced MCP Server ({self.server_name})")
        print(f"Transport: {transport}")
        
        # Criar checkpoint inicial
        safeguards.create_checkpoint("startup")
        
        # Executar servidor MCP
        self.mcp.run(transport=transport)

if __name__ == "__main__":
    # Parâmetros padrão
    server_name = "enhanced-continuity-protocol"
    transport = "stdio"
    
    # Processar argumentos de linha de comando
    if len(sys.argv) > 1:
        server_name = sys.argv[1]
    if len(sys.argv) > 2:
        transport = sys.argv[2]
    
    # Criar e executar servidor
    server = EnhancedMCPServer(server_name)
    server.run(transport=transport)
