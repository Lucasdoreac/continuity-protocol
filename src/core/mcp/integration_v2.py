#!/usr/bin/env python3
"""
Integration Module V2 - Continuity Protocol
Integração dos componentes da Etapa 2 com o sistema principal
"""

import os
import sys
import json
import threading
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable, Union

# Importar componentes
try:
    from core.mcp.versioning import versioning_system
    from core.mcp.backup import backup_system
    from core.mcp.notification import notification_system
    from core.mcp.search import search_system
    from core.mcp.safeguards import safeguards, apply_safeguards
    from core.mcp.schema_validation import SchemaValidator
    from core.mcp.rate_limiting import rate_limiter, rate_limit
    from core.mcp.auth import auth_system, require_auth
except ImportError:
    # Adicionar diretório pai ao path
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from core.mcp.versioning import versioning_system
    from core.mcp.backup import backup_system
    from core.mcp.notification import notification_system
    from core.mcp.search import search_system
    from core.mcp.safeguards import safeguards, apply_safeguards
    from core.mcp.schema_validation import SchemaValidator
    from core.mcp.rate_limiting import rate_limiter, rate_limit
    from core.mcp.auth import auth_system, require_auth

# Importar ContextSharingProtocol
try:
    from core.mcp.context_sharing import ContextSharingProtocol
except ImportError:
    # Adicionar diretório pai ao path
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from core.mcp.context_sharing import ContextSharingProtocol

class EnhancedContextSharingProtocol(ContextSharingProtocol):
    """
    Versão aprimorada do ContextSharingProtocol com recursos da Etapa 2
    """
    
    def __init__(self):
        """Inicializa o protocolo de compartilhamento de contexto aprimorado"""
        super().__init__()
        print("Initializing EnhancedContextSharingProtocol with Etapa 2 features")
        
        # Iniciar thread de backup automático
        self.backup_thread = None
        self.stop_backup_thread = False
        self._start_backup_thread()
        
        # Iniciar sistema de notificações
        notification_system.start_processing_thread()
        
        # Registrar callbacks para eventos
        self._register_notification_callbacks()
    
    def _start_backup_thread(self) -> None:
        """Inicia thread de backup automático"""
        if self.backup_thread is not None and self.backup_thread.is_alive():
            return
        
        self.stop_backup_thread = False
        self.backup_thread = threading.Thread(target=self._backup_thread_loop)
        self.backup_thread.daemon = True
        self.backup_thread.start()
    
    def _backup_thread_loop(self) -> None:
        """Loop de backup automático"""
        # Intervalo de backup em segundos (1 hora)
        interval = 3600
        
        while not self.stop_backup_thread:
            try:
                # Criar backup
                backup_result = backup_system.create_backup("auto", "Backup automático periódico")
                
                if backup_result["success"]:
                    print(f"Backup automático criado: {backup_result['backup_info']['id']}")
                    
                    # Notificar sobre backup
                    notification_system.create_notification(
                        "Backup automático criado",
                        f"Backup automático periódico criado com sucesso: {backup_result['backup_info']['id']}",
                        "info",
                        "backup_system",
                        {"backup_id": backup_result["backup_info"]["id"]}
                    )
                else:
                    print(f"Erro ao criar backup automático: {backup_result.get('error', 'Erro desconhecido')}")
                    
                    # Notificar sobre erro
                    notification_system.create_notification(
                        "Erro ao criar backup automático",
                        f"Erro ao criar backup automático periódico: {backup_result.get('error', 'Erro desconhecido')}",
                        "error",
                        "backup_system"
                    )
                
                # Commit de alterações se Git disponível
                if backup_system.git_available:
                    commit_result = backup_system.git_commit_changes("Backup automático periódico")
                    
                    if commit_result["success"]:
                        print(f"Commit automático criado: {commit_result['commit_info']['hash']}")
                    else:
                        print(f"Erro ao criar commit automático: {commit_result.get('error', 'Erro desconhecido')}")
            except Exception as e:
                print(f"Erro no thread de backup: {str(e)}")
            
            # Aguardar próximo backup
            for _ in range(interval):
                if self.stop_backup_thread:
                    break
                time.sleep(1)
    
    def _register_notification_callbacks(self) -> None:
        """Registra callbacks para eventos de notificação"""
        # Callback para notificações de erro
        notification_system.register_callback(
            lambda n: print(f"ERRO: {n['title']} - {n['message']}"),
            "error"
        )
        
        # Callback para notificações de aviso
        notification_system.register_callback(
            lambda n: print(f"AVISO: {n['title']} - {n['message']}"),
            "warning"
        )
    
    def stop_backup_thread(self) -> None:
        """Para thread de backup automático"""
        self.stop_backup_thread = True
        if self.backup_thread is not None:
            self.backup_thread.join(timeout=2.0)
    
    @rate_limit("store_artifact", 100, 3600)  # 100 artefatos por hora
    @apply_safeguards
    def store_artifact(self, content: str, artifact_type: str, project_id: str, 
                      agent_id: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Armazena um artefato no protocolo (com versionamento)
        
        Args:
            content: Conteúdo do artefato
            artifact_type: Tipo do artefato
            project_id: ID do projeto
            agent_id: ID do agente
            metadata: Metadados adicionais
            
        Returns:
            Dict: Informações do artefato armazenado
        """
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
            
            # Notificar sobre truncamento
            notification_system.create_notification(
                "Conteúdo truncado",
                f"Conteúdo do artefato foi truncado de {content_check['line_count']} para {len(chunks[0].splitlines())} linhas",
                "warning",
                "safeguards",
                {"artifact_type": artifact_type, "project_id": project_id}
            )
        
        # Sanitizar metadata
        if metadata is None:
            metadata = {}
        
        # Validar metadados
        validation_result = SchemaValidator.validate_artifact_metadata(metadata)
        if not validation_result["valid"]:
            # Se metadados inválidos, sanitizar
            print(f"[WARNING] Invalid metadata: {validation_result['errors']}. Sanitizing...")
            metadata = SchemaValidator.sanitize_metadata(metadata)
            
            # Notificar sobre sanitização
            notification_system.create_notification(
                "Metadados sanitizados",
                f"Metadados do artefato foram sanitizados: {validation_result['errors']}",
                "warning",
                "schema_validation",
                {"artifact_type": artifact_type, "project_id": project_id}
            )
        
        # Sanitizar project_id e artifact_type para evitar problemas de path
        project_id = SchemaValidator.sanitize_path(project_id)
        artifact_type = SchemaValidator.sanitize_path(artifact_type)
        
        # Armazenar artefato usando implementação original
        artifact_info = super().store_artifact(content, artifact_type, project_id, agent_id, metadata)
        
        # Adicionar artefato ao sistema de versionamento
        version_result = versioning_system.create_initial_version(
            artifact_info["id"],
            content,
            {
                "title": metadata.get("title", ""),
                "type": artifact_type,
                "created_at": artifact_info["created_at"],
                "created_by": agent_id
            }
        )
        
        # Indexar artefato para busca
        search_system.index_artifact(
            artifact_info["id"],
            content,
            {
                "title": metadata.get("title", ""),
                "type": artifact_type,
                "created_at": artifact_info["created_at"],
                "created_by": agent_id,
                "metadata": metadata
            }
        )
        
        # Notificar sobre criação de artefato
        notification_system.create_notification(
            f"Novo artefato criado: {metadata.get('title', artifact_info['id'])}",
            f"Artefato do tipo {artifact_type} criado no projeto {project_id}",
            "info",
            "artifact_creation",
            {
                "artifact_id": artifact_info["id"],
                "artifact_type": artifact_type,
                "project_id": project_id,
                "created_by": agent_id
            }
        )
        
        return artifact_info
    
    @rate_limit("update_artifact", 100, 3600)  # 100 atualizações por hora
    @apply_safeguards
    def update_artifact(self, artifact_id: str, content: str, 
                       agent_id: str, metadata: Dict[str, Any] = None,
                       change_level: str = None, changes: str = None) -> Dict[str, Any]:
        """
        Atualiza um artefato existente (com versionamento)
        
        Args:
            artifact_id: ID do artefato
            content: Novo conteúdo do artefato
            agent_id: ID do agente
            metadata: Metadados atualizados
            change_level: Nível de mudança ("major", "minor", "patch")
            changes: Descrição das mudanças
            
        Returns:
            Dict: Informações do artefato atualizado
        """
        # Verificar se artefato existe
        artifact = self.get_artifact(artifact_id)
        if not artifact:
            return {
                "error": f"Artifact {artifact_id} not found",
                "success": False
            }
        
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
            
            # Notificar sobre truncamento
            notification_system.create_notification(
                "Conteúdo truncado",
                f"Conteúdo do artefato foi truncado de {content_check['line_count']} para {len(chunks[0].splitlines())} linhas",
                "warning",
                "safeguards",
                {"artifact_id": artifact_id}
            )
        
        # Sanitizar metadata
        if metadata is None:
            metadata = artifact.get("metadata", {})
        
        # Validar metadados
        validation_result = SchemaValidator.validate_artifact_metadata(metadata)
        if not validation_result["valid"]:
            # Se metadados inválidos, sanitizar
            print(f"[WARNING] Invalid metadata: {validation_result['errors']}. Sanitizing...")
            metadata = SchemaValidator.sanitize_metadata(metadata)
            
            # Notificar sobre sanitização
            notification_system.create_notification(
                "Metadados sanitizados",
                f"Metadados do artefato foram sanitizados: {validation_result['errors']}",
                "warning",
                "schema_validation",
                {"artifact_id": artifact_id}
            )
        
        # Atualizar arquivo do artefato
        try:
            with open(artifact["file_path"], 'w') as f:
                f.write(content)
            
            # Atualizar timestamp
            artifact["updated_at"] = datetime.now().isoformat()
            self.artifacts_registry["artifacts"][artifact_id]["updated_at"] = artifact["updated_at"]
            self._save_artifacts_registry()
            
            # Criar nova versão
            version_result = versioning_system.create_new_version(
                artifact_id,
                content,
                {
                    "title": metadata.get("title", ""),
                    "type": artifact.get("type", ""),
                    "created_at": artifact["created_at"],
                    "updated_at": artifact["updated_at"],
                    "created_by": agent_id
                },
                change_level,
                changes
            )
            
            # Atualizar índice de busca
            search_system.remove_from_index(artifact_id)
            search_system.index_artifact(
                artifact_id,
                content,
                {
                    "title": metadata.get("title", ""),
                    "type": artifact.get("type", ""),
                    "created_at": artifact["created_at"],
                    "updated_at": artifact["updated_at"],
                    "created_by": agent_id,
                    "metadata": metadata
                }
            )
            
            # Notificar sobre atualização de artefato
            notification_system.create_notification(
                f"Artefato atualizado: {metadata.get('title', artifact_id)}",
                f"Artefato {artifact_id} atualizado para versão {version_result['version_info']['version']}",
                "info",
                "artifact_update",
                {
                    "artifact_id": artifact_id,
                    "version": version_result["version_info"]["version"],
                    "previous_version": version_result.get("previous_version"),
                    "change_level": version_result.get("change_level"),
                    "updated_by": agent_id
                }
            )
            
            return {
                "success": True,
                "artifact_id": artifact_id,
                "updated_at": artifact["updated_at"],
                "version": version_result["version_info"]["version"],
                "previous_version": version_result.get("previous_version"),
                "change_level": version_result.get("change_level")
            }
        except Exception as e:
            # Notificar sobre erro
            notification_system.create_notification(
                "Erro ao atualizar artefato",
                f"Erro ao atualizar artefato {artifact_id}: {str(e)}",
                "error",
                "artifact_update",
                {"artifact_id": artifact_id}
            )
            
            return {
                "success": False,
                "error": f"Failed to update artifact: {str(e)}"
            }
    
    @rate_limit("get_artifact_version", 300, 3600)  # 300 consultas por hora
    @apply_safeguards
    def get_artifact_version(self, artifact_id: str, version: str = None) -> Dict[str, Any]:
        """
        Obtém versão específica de um artefato
        
        Args:
            artifact_id: ID do artefato
            version: Versão específica (usa versão atual se None)
            
        Returns:
            Dict: Informações e conteúdo da versão
        """
        return versioning_system.get_version(artifact_id, version)
    
    @rate_limit("get_artifact_history", 200, 3600)  # 200 consultas por hora
    @apply_safeguards
    def get_artifact_history(self, artifact_id: str) -> Dict[str, Any]:
        """
        Obtém histórico de versões de um artefato
        
        Args:
            artifact_id: ID do artefato
            
        Returns:
            Dict: Histórico de versões
        """
        return versioning_system.get_version_history(artifact_id)
    
    @rate_limit("compare_artifact_versions", 100, 3600)  # 100 consultas por hora
    @apply_safeguards
    def compare_artifact_versions(self, artifact_id: str, version1: str, version2: str) -> Dict[str, Any]:
        """
        Compara duas versões de um artefato
        
        Args:
            artifact_id: ID do artefato
            version1: Primeira versão
            version2: Segunda versão
            
        Returns:
            Dict: Resultado da comparação
        """
        return versioning_system.compare_versions(artifact_id, version1, version2)
    
    @rate_limit("revert_artifact", 50, 3600)  # 50 reversões por hora
    @apply_safeguards
    def revert_artifact(self, artifact_id: str, version: str) -> Dict[str, Any]:
        """
        Reverte artefato para versão específica
        
        Args:
            artifact_id: ID do artefato
            version: Versão para reverter
            
        Returns:
            Dict: Informações da nova versão criada
        """
        revert_result = versioning_system.revert_to_version(artifact_id, version)
        
        if revert_result["success"]:
            # Obter conteúdo da versão
            version_content = revert_result["version_info"]["content"]
            
            # Atualizar artefato
            artifact = self.get_artifact(artifact_id)
            if artifact:
                try:
                    with open(artifact["file_path"], 'w') as f:
                        f.write(version_content)
                    
                    # Atualizar timestamp
                    artifact["updated_at"] = datetime.now().isoformat()
                    self.artifacts_registry["artifacts"][artifact_id]["updated_at"] = artifact["updated_at"]
                    self._save_artifacts_registry()
                    
                    # Atualizar índice de busca
                    search_system.remove_from_index(artifact_id)
                    search_system.index_artifact(
                        artifact_id,
                        version_content,
                        {
                            "title": artifact.get("metadata", {}).get("title", ""),
                            "type": artifact.get("type", ""),
                            "created_at": artifact["created_at"],
                            "updated_at": artifact["updated_at"],
                            "created_by": artifact.get("created_by", ""),
                            "metadata": artifact.get("metadata", {})
                        }
                    )
                    
                    # Notificar sobre reversão
                    notification_system.create_notification(
                        f"Artefato revertido para versão {version}",
                        f"Artefato {artifact_id} foi revertido para a versão {version}",
                        "info",
                        "artifact_revert",
                        {
                            "artifact_id": artifact_id,
                            "version": version,
                            "new_version": revert_result["version_info"]["version"]
                        }
                    )
                except Exception as e:
                    # Notificar sobre erro
                    notification_system.create_notification(
                        "Erro ao reverter artefato",
                        f"Erro ao reverter artefato {artifact_id} para versão {version}: {str(e)}",
                        "error",
                        "artifact_revert",
                        {"artifact_id": artifact_id, "version": version}
                    )
                    
                    return {
                        "success": False,
                        "error": f"Failed to update artifact file: {str(e)}"
                    }
        
        return revert_result
    
    @rate_limit("search_artifacts", 200, 3600)  # 200 consultas por hora
    @apply_safeguards
    def search_artifacts(self, query: str, artifact_type: str = None, 
                        created_by: str = None, limit: int = 10) -> Dict[str, Any]:
        """
        Busca artefatos por termos
        
        Args:
            query: Termos de busca
            artifact_type: Filtro por tipo de artefato
            created_by: Filtro por criador
            limit: Número máximo de resultados
            
        Returns:
            Dict: Resultados da busca
        """
        return search_system.search(query, artifact_type, created_by, limit)
    
    @rate_limit("search_by_metadata", 200, 3600)  # 200 consultas por hora
    @apply_safeguards
    def search_by_metadata(self, metadata_filters: Dict[str, Any], 
                          limit: int = 10) -> Dict[str, Any]:
        """
        Busca artefatos por metadados
        
        Args:
            metadata_filters: Filtros de metadados
            limit: Número máximo de resultados
            
        Returns:
            Dict: Resultados da busca
        """
        return search_system.search_by_metadata(metadata_filters, limit)
    
    @rate_limit("create_backup", 10, 3600)  # 10 backups por hora
    @apply_safeguards
    def create_backup(self, backup_type: str = "full", description: str = None) -> Dict[str, Any]:
        """
        Cria backup do sistema
        
        Args:
            backup_type: Tipo de backup ("full", "incremental")
            description: Descrição do backup
            
        Returns:
            Dict: Informações do backup criado
        """
        backup_result = backup_system.create_backup(backup_type, description)
        
        if backup_result["success"]:
            # Notificar sobre backup
            notification_system.create_notification(
                "Backup criado",
                f"Backup {backup_type} criado com sucesso: {backup_result['backup_info']['id']}",
                "info",
                "backup_system",
                {"backup_id": backup_result["backup_info"]["id"]}
            )
        else:
            # Notificar sobre erro
            notification_system.create_notification(
                "Erro ao criar backup",
                f"Erro ao criar backup {backup_type}: {backup_result.get('error', 'Erro desconhecido')}",
                "error",
                "backup_system"
            )
        
        return backup_result
    
    @rate_limit("git_commit_changes", 10, 3600)  # 10 commits por hora
    @apply_safeguards
    def git_commit_changes(self, message: str = None) -> Dict[str, Any]:
        """
        Commit de alterações no repositório Git
        
        Args:
            message: Mensagem do commit
            
        Returns:
            Dict: Resultado do commit
        """
        commit_result = backup_system.git_commit_changes(message)
        
        if commit_result["success"]:
            # Notificar sobre commit
            notification_system.create_notification(
                "Commit criado",
                f"Commit criado com sucesso: {commit_result['commit_info']['hash']}",
                "info",
                "git_system",
                {"commit_hash": commit_result["commit_info"]["hash"]}
            )
        else:
            # Notificar sobre erro
            notification_system.create_notification(
                "Erro ao criar commit",
                f"Erro ao criar commit: {commit_result.get('error', 'Erro desconhecido')}",
                "error",
                "git_system"
            )
        
        return commit_result
    
    @rate_limit("create_notification", 100, 3600)  # 100 notificações por hora
    @apply_safeguards
    def create_notification(self, title: str, message: str, notification_type: str = "info",
                           source: str = "system", metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Cria uma notificação
        
        Args:
            title: Título da notificação
            message: Mensagem da notificação
            notification_type: Tipo da notificação ("info", "warning", "error", "success")
            source: Fonte da notificação
            metadata: Metadados adicionais
            
        Returns:
            Dict: Informações da notificação criada
        """
        return notification_system.create_notification(title, message, notification_type, source, metadata)
    
    @rate_limit("get_notifications", 200, 3600)  # 200 consultas por hora
    @apply_safeguards
    def get_notifications(self, limit: int = 10, offset: int = 0, 
                         unread_only: bool = False) -> Dict[str, Any]:
        """
        Obtém lista de notificações
        
        Args:
            limit: Número máximo de notificações
            offset: Deslocamento para paginação
            unread_only: Se True, retorna apenas notificações não lidas
            
        Returns:
            Dict: Lista de notificações
        """
        return notification_system.get_notifications(limit, offset, unread_only)
    
    @rate_limit("mark_notification_as_read", 200, 3600)  # 200 operações por hora
    @apply_safeguards
    def mark_notification_as_read(self, notification_id: str) -> Dict[str, Any]:
        """
        Marca notificação como lida
        
        Args:
            notification_id: ID da notificação
            
        Returns:
            Dict: Resultado da operação
        """
        return notification_system.mark_as_read(notification_id)
    
    @rate_limit("reindex_all_artifacts", 1, 3600)  # 1 reindexação por hora
    @apply_safeguards
    def reindex_all_artifacts(self) -> Dict[str, Any]:
        """
        Reindexar todos os artefatos
        
        Returns:
            Dict: Resultado da reindexação
        """
        # Função para obter todos os artefatos
        def get_all_artifacts():
            artifacts = []
            
            for artifact_id, artifact_info in self.artifacts_registry["artifacts"].items():
                try:
                    with open(artifact_info["file_path"], 'r') as f:
                        content = f.read()
                    
                    artifacts.append({
                        "id": artifact_id,
                        "content": content,
                        "title": artifact_info.get("metadata", {}).get("title", ""),
                        "type": artifact_info.get("type", ""),
                        "created_at": artifact_info.get("created_at", ""),
                        "created_by": artifact_info.get("created_by", ""),
                        "metadata": artifact_info.get("metadata", {})
                    })
                except:
                    pass
            
            return artifacts
        
        # Reindexar artefatos
        reindex_result = search_system.reindex_all(get_all_artifacts)
        
        if reindex_result["success"]:
            # Notificar sobre reindexação
            notification_system.create_notification(
                "Reindexação concluída",
                f"Reindexação de artefatos concluída: {reindex_result['indexed_count']} artefatos indexados",
                "info",
                "search_system",
                {"indexed_count": reindex_result["indexed_count"]}
            )
        else:
            # Notificar sobre erro
            notification_system.create_notification(
                "Erro na reindexação",
                f"Erro ao reindexar artefatos: {reindex_result.get('error', 'Erro desconhecido')}",
                "error",
                "search_system"
            )
        
        return reindex_result

# Instância global para uso em todo o sistema
enhanced_context_protocol = EnhancedContextSharingProtocol()
