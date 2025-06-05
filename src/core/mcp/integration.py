#!/usr/bin/env python3
"""
Integration Module - Continuity Protocol
Integração dos componentes de segurança e safeguards com o sistema principal
"""

import os
import sys
import json
from typing import Dict, List, Any, Optional, Callable, Union

# Importar componentes
try:
    from core.mcp.safeguards import safeguards, apply_safeguards
    from core.mcp.schema_validation import SchemaValidator
    from core.mcp.rate_limiting import rate_limiter, rate_limit
    from core.mcp.auth import auth_system, require_auth
except ImportError:
    # Adicionar diretório pai ao path
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
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

class SecureContextSharingProtocol(ContextSharingProtocol):
    """
    Versão segura do ContextSharingProtocol com safeguards, validação e rate limiting
    """
    
    def __init__(self):
        """Inicializa o protocolo de compartilhamento de contexto seguro"""
        super().__init__()
        print("Initializing SecureContextSharingProtocol with safeguards and security features")
    
    @rate_limit("register_project", 50, 3600)  # 50 projetos por hora
    @apply_safeguards
    def register_project(self, project_id: str, project_name: str, description: str) -> Dict[str, Any]:
        """
        Registra um projeto no protocolo (com validação e safeguards)
        
        Args:
            project_id: ID do projeto
            project_name: Nome do projeto
            description: Descrição do projeto
            
        Returns:
            Dict: Informações do projeto registrado
        """
        # Validar dados do projeto
        project_data = {
            "id": project_id,
            "name": project_name,
            "description": description
        }
        
        validation_result = SchemaValidator.validate_project(project_data)
        if not validation_result["valid"]:
            raise ValueError(f"Invalid project data: {validation_result['errors']}")
        
        # Sanitizar project_id para evitar problemas de path
        project_id = SchemaValidator.sanitize_path(project_id)
        
        # Registrar projeto usando implementação original
        return super().register_project(project_id, project_name, description)
    
    @rate_limit("store_artifact", 100, 3600)  # 100 artefatos por hora
    @apply_safeguards
    def store_artifact(self, content: str, artifact_type: str, project_id: str, 
                      agent_id: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Armazena um artefato no protocolo (com validação e safeguards)
        
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
        
        # Sanitizar metadata
        if metadata is None:
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
        
        # Armazenar artefato usando implementação original
        return super().store_artifact(content, artifact_type, project_id, agent_id, metadata)
    
    @rate_limit("get_artifact", 300, 3600)  # 300 consultas por hora
    @apply_safeguards
    def get_artifact(self, artifact_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtém um artefato pelo ID (com rate limiting e safeguards)
        
        Args:
            artifact_id: ID do artefato
            
        Returns:
            Optional[Dict]: Informações do artefato e seu conteúdo
        """
        # Sanitizar artifact_id para evitar problemas de path
        artifact_id = SchemaValidator.sanitize_path(artifact_id)
        
        # Obter artefato usando implementação original
        return super().get_artifact(artifact_id)
    
    @rate_limit("get_project_artifacts", 200, 3600)  # 200 consultas por hora
    @apply_safeguards
    def get_project_artifacts(self, project_id: str, artifact_type: str = None) -> List[Dict[str, Any]]:
        """
        Obtém todos os artefatos de um projeto (com rate limiting e safeguards)
        
        Args:
            project_id: ID do projeto
            artifact_type: Tipo de artefato para filtrar
            
        Returns:
            List[Dict]: Lista de artefatos do projeto
        """
        # Sanitizar project_id e artifact_type para evitar problemas de path
        project_id = SchemaValidator.sanitize_path(project_id)
        if artifact_type:
            artifact_type = SchemaValidator.sanitize_path(artifact_type)
        
        # Obter artefatos usando implementação original
        return super().get_project_artifacts(project_id, artifact_type)
    
    @rate_limit("get_latest_project_artifact", 200, 3600)  # 200 consultas por hora
    @apply_safeguards
    def get_latest_project_artifact(self, project_id: str, artifact_type: str) -> Optional[Dict[str, Any]]:
        """
        Obtém o artefato mais recente de um projeto por tipo (com rate limiting e safeguards)
        
        Args:
            project_id: ID do projeto
            artifact_type: Tipo de artefato
            
        Returns:
            Optional[Dict]: Artefato mais recente
        """
        # Sanitizar project_id e artifact_type para evitar problemas de path
        project_id = SchemaValidator.sanitize_path(project_id)
        artifact_type = SchemaValidator.sanitize_path(artifact_type)
        
        # Obter artefato mais recente usando implementação original
        return super().get_latest_project_artifact(project_id, artifact_type)
    
    @rate_limit("get_project_context", 200, 3600)  # 200 consultas por hora
    @apply_safeguards
    def get_project_context(self, project_id: str) -> Dict[str, Any]:
        """
        Obtém o contexto completo de um projeto (com rate limiting e safeguards)
        
        Args:
            project_id: ID do projeto
            
        Returns:
            Dict: Contexto completo do projeto
        """
        # Sanitizar project_id para evitar problemas de path
        project_id = SchemaValidator.sanitize_path(project_id)
        
        # Obter contexto do projeto usando implementação original
        return super().get_project_context(project_id)
    
    @rate_limit("sync_artifact_to_file", 50, 3600)  # 50 sincronizações por hora
    @apply_safeguards
    def sync_artifact_to_file(self, artifact_id: str, file_path: str) -> bool:
        """
        Sincroniza um artefato para um arquivo no sistema (com rate limiting e safeguards)
        
        Args:
            artifact_id: ID do artefato
            file_path: Caminho do arquivo
            
        Returns:
            bool: True se sucesso, False caso contrário
        """
        # Sanitizar artifact_id e file_path para evitar problemas de path
        artifact_id = SchemaValidator.sanitize_path(artifact_id)
        file_path = SchemaValidator.sanitize_path(file_path)
        
        # Sincronizar artefato para arquivo usando implementação original
        return super().sync_artifact_to_file(artifact_id, file_path)
    
    @rate_limit("sync_file_to_artifact", 50, 3600)  # 50 sincronizações por hora
    @apply_safeguards
    def sync_file_to_artifact(self, file_path: str, artifact_id: str) -> bool:
        """
        Sincroniza um arquivo do sistema para um artefato (com rate limiting e safeguards)
        
        Args:
            file_path: Caminho do arquivo
            artifact_id: ID do artefato
            
        Returns:
            bool: True se sucesso, False caso contrário
        """
        # Sanitizar file_path e artifact_id para evitar problemas de path
        file_path = SchemaValidator.sanitize_path(file_path)
        artifact_id = SchemaValidator.sanitize_path(artifact_id)
        
        # Sincronizar arquivo para artefato usando implementação original
        return super().sync_file_to_artifact(file_path, artifact_id)
    
    @rate_limit("create_artifact_from_file", 50, 3600)  # 50 criações por hora
    @apply_safeguards
    def create_artifact_from_file(self, file_path: str, artifact_type: str, project_id: str, 
                                 agent_id: str, metadata: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """
        Cria um artefato a partir de um arquivo (com rate limiting e safeguards)
        
        Args:
            file_path: Caminho do arquivo
            artifact_type: Tipo do artefato
            project_id: ID do projeto
            agent_id: ID do agente
            metadata: Metadados adicionais
            
        Returns:
            Optional[Dict]: Informações do artefato criado
        """
        # Sanitizar file_path, artifact_type e project_id para evitar problemas de path
        file_path = SchemaValidator.sanitize_path(file_path)
        artifact_type = SchemaValidator.sanitize_path(artifact_type)
        project_id = SchemaValidator.sanitize_path(project_id)
        
        # Sanitizar metadata
        if metadata is None:
            metadata = {}
        
        # Validar metadados
        validation_result = SchemaValidator.validate_artifact_metadata(metadata)
        if not validation_result["valid"]:
            # Se metadados inválidos, sanitizar
            print(f"[WARNING] Invalid metadata: {validation_result['errors']}. Sanitizing...")
            metadata = SchemaValidator.sanitize_metadata(metadata)
        
        # Criar artefato a partir do arquivo usando implementação original
        return super().create_artifact_from_file(file_path, artifact_type, project_id, agent_id, metadata)

# Função para criar instância segura do protocolo
def create_secure_context_protocol() -> SecureContextSharingProtocol:
    """
    Cria uma instância segura do protocolo de compartilhamento de contexto
    
    Returns:
        SecureContextSharingProtocol: Instância segura do protocolo
    """
    return SecureContextSharingProtocol()

# Instância global para uso em todo o sistema
secure_context_protocol = create_secure_context_protocol()
