#!/usr/bin/env python3
"""
Context Sharing Protocol - Continuity Protocol
Sistema para compartilhamento automático de contexto entre diferentes agentes de IA
"""

import os
import json
import time
import shutil
import hashlib
from datetime import datetime
from typing import Dict, List, Any, Optional, Union

# Diretórios para armazenamento de contexto compartilhado
SHARED_CONTEXT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "shared_context")
ARTIFACTS_DIR = os.path.join(SHARED_CONTEXT_DIR, "artifacts")
PROJECTS_DIR = os.path.join(SHARED_CONTEXT_DIR, "projects")
AGENTS_DIR = os.path.join(SHARED_CONTEXT_DIR, "agents")

# Garantir que os diretórios existam
for directory in [SHARED_CONTEXT_DIR, ARTIFACTS_DIR, PROJECTS_DIR, AGENTS_DIR]:
    os.makedirs(directory, exist_ok=True)

class ContextSharingProtocol:
    """
    Protocolo de compartilhamento de contexto entre agentes de IA
    """
    
    def __init__(self):
        """Inicializa o protocolo de compartilhamento de contexto"""
        self.agents_registry = self._load_agents_registry()
        self.projects_registry = self._load_projects_registry()
        self.artifacts_registry = self._load_artifacts_registry()
    
    def _load_agents_registry(self) -> Dict[str, Any]:
        """Carrega o registro de agentes"""
        registry_file = os.path.join(AGENTS_DIR, "registry.json")
        if os.path.exists(registry_file):
            try:
                with open(registry_file, 'r') as f:
                    return json.load(f)
            except:
                return {"agents": {}}
        else:
            return {"agents": {}}
    
    def _save_agents_registry(self) -> None:
        """Salva o registro de agentes"""
        registry_file = os.path.join(AGENTS_DIR, "registry.json")
        with open(registry_file, 'w') as f:
            json.dump(self.agents_registry, f, indent=2)
    
    def _load_projects_registry(self) -> Dict[str, Any]:
        """Carrega o registro de projetos"""
        registry_file = os.path.join(PROJECTS_DIR, "registry.json")
        if os.path.exists(registry_file):
            try:
                with open(registry_file, 'r') as f:
                    return json.load(f)
            except:
                return {"projects": {}}
        else:
            return {"projects": {}}
    
    def _save_projects_registry(self) -> None:
        """Salva o registro de projetos"""
        registry_file = os.path.join(PROJECTS_DIR, "registry.json")
        with open(registry_file, 'w') as f:
            json.dump(self.projects_registry, f, indent=2)
    
    def _load_artifacts_registry(self) -> Dict[str, Any]:
        """Carrega o registro de artefatos"""
        registry_file = os.path.join(ARTIFACTS_DIR, "registry.json")
        if os.path.exists(registry_file):
            try:
                with open(registry_file, 'r') as f:
                    return json.load(f)
            except:
                return {"artifacts": {}}
        else:
            return {"artifacts": {}}
    
    def _save_artifacts_registry(self) -> None:
        """Salva o registro de artefatos"""
        registry_file = os.path.join(ARTIFACTS_DIR, "registry.json")
        with open(registry_file, 'w') as f:
            json.dump(self.artifacts_registry, f, indent=2)
    
    def register_agent(self, agent_id: str, agent_type: str, capabilities: List[str]) -> Dict[str, Any]:
        """
        Registra um agente no protocolo
        
        Args:
            agent_id: ID do agente
            agent_type: Tipo do agente (e.g., "amazon_q_cli", "claude_desktop")
            capabilities: Lista de capacidades do agente
            
        Returns:
            Dict: Informações do agente registrado
        """
        agent_info = {
            "id": agent_id,
            "type": agent_type,
            "capabilities": capabilities,
            "registered_at": datetime.now().isoformat(),
            "last_active": datetime.now().isoformat(),
            "projects": []
        }
        
        self.agents_registry["agents"][agent_id] = agent_info
        self._save_agents_registry()
        
        return agent_info
    
    def update_agent_activity(self, agent_id: str) -> bool:
        """
        Atualiza o timestamp de última atividade do agente
        
        Args:
            agent_id: ID do agente
            
        Returns:
            bool: True se sucesso, False caso contrário
        """
        if agent_id in self.agents_registry["agents"]:
            self.agents_registry["agents"][agent_id]["last_active"] = datetime.now().isoformat()
            self._save_agents_registry()
            return True
        return False
    
    def register_project(self, project_id: str, project_name: str, description: str) -> Dict[str, Any]:
        """
        Registra um projeto no protocolo
        
        Args:
            project_id: ID do projeto
            project_name: Nome do projeto
            description: Descrição do projeto
            
        Returns:
            Dict: Informações do projeto registrado
        """
        project_info = {
            "id": project_id,
            "name": project_name,
            "description": description,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "artifacts": [],
            "agents": []
        }
        
        self.projects_registry["projects"][project_id] = project_info
        self._save_projects_registry()
        
        # Criar diretório do projeto
        project_dir = os.path.join(PROJECTS_DIR, project_id)
        os.makedirs(project_dir, exist_ok=True)
        
        return project_info
    
    def associate_agent_with_project(self, agent_id: str, project_id: str) -> bool:
        """
        Associa um agente a um projeto
        
        Args:
            agent_id: ID do agente
            project_id: ID do projeto
            
        Returns:
            bool: True se sucesso, False caso contrário
        """
        if agent_id not in self.agents_registry["agents"]:
            return False
        
        if project_id not in self.projects_registry["projects"]:
            return False
        
        # Adicionar projeto à lista de projetos do agente
        if project_id not in self.agents_registry["agents"][agent_id]["projects"]:
            self.agents_registry["agents"][agent_id]["projects"].append(project_id)
            self._save_agents_registry()
        
        # Adicionar agente à lista de agentes do projeto
        if agent_id not in self.projects_registry["projects"][project_id]["agents"]:
            self.projects_registry["projects"][project_id]["agents"].append(agent_id)
            self._save_projects_registry()
        
        return True
    
    def store_artifact(self, content: str, artifact_type: str, project_id: str, 
                      agent_id: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Armazena um artefato no protocolo
        
        Args:
            content: Conteúdo do artefato
            artifact_type: Tipo do artefato (e.g., "plan", "code", "document")
            project_id: ID do projeto
            agent_id: ID do agente que criou o artefato
            metadata: Metadados adicionais (opcional)
            
        Returns:
            Dict: Informações do artefato armazenado
        """
        # Gerar ID único para o artefato
        artifact_id = f"{artifact_type}_{int(time.time())}_{hashlib.md5(content.encode()).hexdigest()[:8]}"
        
        # Criar metadados se não fornecidos
        if metadata is None:
            metadata = {}
        
        # Informações do artefato
        artifact_info = {
            "id": artifact_id,
            "type": artifact_type,
            "project_id": project_id,
            "created_by": agent_id,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "file_path": os.path.join(ARTIFACTS_DIR, f"{artifact_id}.txt"),
            "metadata": metadata
        }
        
        # Salvar conteúdo do artefato
        with open(artifact_info["file_path"], 'w') as f:
            f.write(content)
        
        # Registrar artefato
        self.artifacts_registry["artifacts"][artifact_id] = artifact_info
        self._save_artifacts_registry()
        
        # Adicionar artefato ao projeto
        if project_id in self.projects_registry["projects"]:
            if artifact_id not in self.projects_registry["projects"][project_id]["artifacts"]:
                self.projects_registry["projects"][project_id]["artifacts"].append(artifact_id)
                self.projects_registry["projects"][project_id]["updated_at"] = datetime.now().isoformat()
                self._save_projects_registry()
        
        return artifact_info
    
    def get_artifact(self, artifact_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtém um artefato pelo ID
        
        Args:
            artifact_id: ID do artefato
            
        Returns:
            Optional[Dict]: Informações do artefato e seu conteúdo, ou None se não encontrado
        """
        if artifact_id not in self.artifacts_registry["artifacts"]:
            return None
        
        artifact_info = self.artifacts_registry["artifacts"][artifact_id]
        
        try:
            with open(artifact_info["file_path"], 'r') as f:
                content = f.read()
            
            return {
                **artifact_info,
                "content": content
            }
        except:
            return None
    
    def get_project_artifacts(self, project_id: str, artifact_type: str = None) -> List[Dict[str, Any]]:
        """
        Obtém todos os artefatos de um projeto
        
        Args:
            project_id: ID do projeto
            artifact_type: Tipo de artefato para filtrar (opcional)
            
        Returns:
            List[Dict]: Lista de artefatos do projeto
        """
        if project_id not in self.projects_registry["projects"]:
            return []
        
        artifacts = []
        for artifact_id in self.projects_registry["projects"][project_id]["artifacts"]:
            if artifact_id in self.artifacts_registry["artifacts"]:
                artifact_info = self.artifacts_registry["artifacts"][artifact_id]
                
                # Filtrar por tipo se especificado
                if artifact_type and artifact_info["type"] != artifact_type:
                    continue
                
                try:
                    with open(artifact_info["file_path"], 'r') as f:
                        content = f.read()
                    
                    artifacts.append({
                        **artifact_info,
                        "content": content
                    })
                except:
                    continue
        
        return artifacts
    
    def get_latest_project_artifact(self, project_id: str, artifact_type: str) -> Optional[Dict[str, Any]]:
        """
        Obtém o artefato mais recente de um projeto por tipo
        
        Args:
            project_id: ID do projeto
            artifact_type: Tipo de artefato
            
        Returns:
            Optional[Dict]: Artefato mais recente, ou None se não encontrado
        """
        artifacts = self.get_project_artifacts(project_id, artifact_type)
        
        if not artifacts:
            return None
        
        # Ordenar por data de criação (mais recente primeiro)
        artifacts.sort(key=lambda x: x["created_at"], reverse=True)
        
        return artifacts[0]
    
    def get_project_context(self, project_id: str) -> Dict[str, Any]:
        """
        Obtém o contexto completo de um projeto
        
        Args:
            project_id: ID do projeto
            
        Returns:
            Dict: Contexto completo do projeto
        """
        if project_id not in self.projects_registry["projects"]:
            return {"error": "Project not found"}
        
        project_info = self.projects_registry["projects"][project_id]
        
        # Obter artefatos do projeto
        artifacts = self.get_project_artifacts(project_id)
        
        # Obter agentes associados ao projeto
        agents = []
        for agent_id in project_info["agents"]:
            if agent_id in self.agents_registry["agents"]:
                agents.append(self.agents_registry["agents"][agent_id])
        
        return {
            "project": project_info,
            "artifacts": artifacts,
            "agents": agents,
            "last_updated": project_info["updated_at"]
        }
    
    def sync_artifact_to_file(self, artifact_id: str, file_path: str) -> bool:
        """
        Sincroniza um artefato para um arquivo no sistema
        
        Args:
            artifact_id: ID do artefato
            file_path: Caminho do arquivo
            
        Returns:
            bool: True se sucesso, False caso contrário
        """
        artifact = self.get_artifact(artifact_id)
        if not artifact:
            return False
        
        try:
            # Criar diretório se não existir
            os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
            
            # Salvar conteúdo no arquivo
            with open(file_path, 'w') as f:
                f.write(artifact["content"])
            
            return True
        except:
            return False
    
    def sync_file_to_artifact(self, file_path: str, artifact_id: str) -> bool:
        """
        Sincroniza um arquivo do sistema para um artefato
        
        Args:
            file_path: Caminho do arquivo
            artifact_id: ID do artefato
            
        Returns:
            bool: True se sucesso, False caso contrário
        """
        if not os.path.exists(file_path):
            return False
        
        if artifact_id not in self.artifacts_registry["artifacts"]:
            return False
        
        try:
            # Ler conteúdo do arquivo
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Atualizar artefato
            artifact_info = self.artifacts_registry["artifacts"][artifact_id]
            with open(artifact_info["file_path"], 'w') as f:
                f.write(content)
            
            # Atualizar timestamp
            self.artifacts_registry["artifacts"][artifact_id]["updated_at"] = datetime.now().isoformat()
            self._save_artifacts_registry()
            
            return True
        except:
            return False
    
    def create_artifact_from_file(self, file_path: str, artifact_type: str, project_id: str, 
                                 agent_id: str, metadata: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """
        Cria um artefato a partir de um arquivo
        
        Args:
            file_path: Caminho do arquivo
            artifact_type: Tipo do artefato
            project_id: ID do projeto
            agent_id: ID do agente
            metadata: Metadados adicionais (opcional)
            
        Returns:
            Optional[Dict]: Informações do artefato criado, ou None se falhar
        """
        if not os.path.exists(file_path):
            return None
        
        try:
            # Ler conteúdo do arquivo
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Criar artefato
            return self.store_artifact(content, artifact_type, project_id, agent_id, metadata)
        except:
            return None
