#!/usr/bin/env python3
"""
Versioning System - Continuity Protocol
Sistema de versionamento automático para artefatos
"""

import os
import json
import time
import difflib
import hashlib
from datetime import datetime
from typing import Dict, List, Any, Optional, Union

class VersioningSystem:
    """
    Sistema de versionamento automático para artefatos do Continuity Protocol
    """
    
    def __init__(self, versions_dir: str = None):
        """
        Inicializa o sistema de versionamento
        
        Args:
            versions_dir: Diretório para armazenamento de versões
        """
        # Configurar diretório de versões
        if versions_dir:
            self.versions_dir = versions_dir
        else:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            self.versions_dir = os.path.join(base_dir, "shared_context", "versions")
        
        # Criar diretório se não existir
        os.makedirs(self.versions_dir, exist_ok=True)
        
        # Arquivo de registro de versões
        self.registry_file = os.path.join(self.versions_dir, "versions_registry.json")
        
        # Carregar ou criar registro de versões
        self.versions_registry = self._load_or_create_registry()
    
    def _load_or_create_registry(self) -> Dict[str, Any]:
        """
        Carrega ou cria registro de versões
        
        Returns:
            Dict: Registro de versões
        """
        if os.path.exists(self.registry_file):
            try:
                with open(self.registry_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        # Criar registro vazio
        registry = {
            "artifact_versions": {},
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # Salvar registro
        with open(self.registry_file, 'w') as f:
            json.dump(registry, f, indent=2)
        
        return registry
    
    def _save_registry(self) -> None:
        """Salva registro de versões"""
        self.versions_registry["updated_at"] = datetime.now().isoformat()
        with open(self.registry_file, 'w') as f:
            json.dump(self.versions_registry, f, indent=2)
    
    def _parse_version(self, version_str: str) -> List[int]:
        """
        Converte string de versão em lista de inteiros
        
        Args:
            version_str: String de versão (e.g., "1.0.0")
            
        Returns:
            List[int]: Lista de componentes da versão
        """
        try:
            return [int(x) for x in version_str.split('.')]
        except:
            return [0, 0, 0]
    
    def _format_version(self, version_components: List[int]) -> str:
        """
        Formata lista de componentes de versão como string
        
        Args:
            version_components: Lista de componentes da versão
            
        Returns:
            str: String de versão formatada
        """
        # Garantir que há pelo menos 2 componentes
        while len(version_components) < 2:
            version_components.append(0)
        
        # Limitar a 3 componentes
        version_components = version_components[:3]
        
        return '.'.join(str(x) for x in version_components)
    
    def _increment_version(self, current_version: str, level: str = "patch") -> str:
        """
        Incrementa versão seguindo semver (major.minor.patch)
        
        Args:
            current_version: Versão atual
            level: Nível de incremento ("major", "minor", "patch")
            
        Returns:
            str: Nova versão
        """
        components = self._parse_version(current_version)
        
        # Garantir que há pelo menos 3 componentes
        while len(components) < 3:
            components.append(0)
        
        if level == "major":
            components[0] += 1
            components[1] = 0
            components[2] = 0
        elif level == "minor":
            components[1] += 1
            components[2] = 0
        else:  # patch
            components[2] += 1
        
        return self._format_version(components)
    
    def _calculate_content_hash(self, content: str) -> str:
        """
        Calcula hash do conteúdo
        
        Args:
            content: Conteúdo para calcular hash
            
        Returns:
            str: Hash do conteúdo
        """
        return hashlib.md5(content.encode()).hexdigest()
    
    def _generate_diff(self, old_content: str, new_content: str) -> str:
        """
        Gera diff entre conteúdos
        
        Args:
            old_content: Conteúdo antigo
            new_content: Conteúdo novo
            
        Returns:
            str: Diff formatado
        """
        old_lines = old_content.splitlines()
        new_lines = new_content.splitlines()
        
        diff = difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
            n=3  # Contexto de 3 linhas
        )
        
        return '\n'.join(diff)
    
    def _determine_change_level(self, old_content: str, new_content: str) -> str:
        """
        Determina nível de mudança com base no diff
        
        Args:
            old_content: Conteúdo antigo
            new_content: Conteúdo novo
            
        Returns:
            str: Nível de mudança ("major", "minor", "patch")
        """
        # Calcular diferença
        old_lines = old_content.splitlines()
        new_lines = new_content.splitlines()
        
        # Calcular estatísticas de mudança
        added = 0
        removed = 0
        changed = 0
        
        matcher = difflib.SequenceMatcher(None, old_lines, new_lines)
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'replace':
                changed += max(i2 - i1, j2 - j1)
            elif tag == 'delete':
                removed += (i2 - i1)
            elif tag == 'insert':
                added += (j2 - j1)
        
        total_lines = max(len(old_lines), len(new_lines))
        change_ratio = (added + removed + changed) / total_lines if total_lines > 0 else 0
        
        # Determinar nível com base na proporção de mudança
        if change_ratio > 0.5:  # Mais de 50% mudou
            return "major"
        elif change_ratio > 0.2:  # Entre 20% e 50% mudou
            return "minor"
        else:  # Menos de 20% mudou
            return "patch"
    
    def create_initial_version(self, artifact_id: str, content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cria versão inicial para um artefato
        
        Args:
            artifact_id: ID do artefato
            content: Conteúdo do artefato
            metadata: Metadados do artefato
            
        Returns:
            Dict: Informações da versão criada
        """
        # Verificar se artefato já tem versões
        if artifact_id in self.versions_registry["artifact_versions"]:
            return {
                "error": f"Artifact {artifact_id} already has versions",
                "success": False
            }
        
        # Inicializar registro de versões para o artefato
        self.versions_registry["artifact_versions"][artifact_id] = {
            "current_version": "1.0.0",
            "versions": {},
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # Calcular hash do conteúdo
        content_hash = self._calculate_content_hash(content)
        
        # Criar informações da versão
        version_info = {
            "version": "1.0.0",
            "artifact_id": artifact_id,
            "content_hash": content_hash,
            "created_at": datetime.now().isoformat(),
            "created_by": metadata.get("created_by", "unknown"),
            "file_path": os.path.join(self.versions_dir, f"{artifact_id}_v1.0.0.txt"),
            "metadata": metadata,
            "changes": "Initial version"
        }
        
        # Salvar conteúdo da versão
        with open(version_info["file_path"], 'w') as f:
            f.write(content)
        
        # Adicionar versão ao registro
        self.versions_registry["artifact_versions"][artifact_id]["versions"]["1.0.0"] = version_info
        self._save_registry()
        
        return {
            "success": True,
            "version_info": version_info
        }
    
    def create_new_version(self, artifact_id: str, content: str, metadata: Dict[str, Any], 
                          change_level: str = None, changes: str = None) -> Dict[str, Any]:
        """
        Cria nova versão para um artefato existente
        
        Args:
            artifact_id: ID do artefato
            content: Novo conteúdo do artefato
            metadata: Metadados atualizados do artefato
            change_level: Nível de mudança ("major", "minor", "patch")
            changes: Descrição das mudanças
            
        Returns:
            Dict: Informações da versão criada
        """
        # Verificar se artefato tem versões
        if artifact_id not in self.versions_registry["artifact_versions"]:
            # Criar versão inicial
            return self.create_initial_version(artifact_id, content, metadata)
        
        # Obter informações de versão atual
        artifact_versions = self.versions_registry["artifact_versions"][artifact_id]
        current_version = artifact_versions["current_version"]
        current_version_info = artifact_versions["versions"][current_version]
        
        # Carregar conteúdo atual
        try:
            with open(current_version_info["file_path"], 'r') as f:
                current_content = f.read()
        except:
            current_content = ""
        
        # Calcular hash do novo conteúdo
        new_content_hash = self._calculate_content_hash(content)
        
        # Verificar se conteúdo mudou
        if new_content_hash == current_version_info["content_hash"]:
            return {
                "success": False,
                "error": "Content has not changed",
                "version_info": current_version_info
            }
        
        # Determinar nível de mudança se não especificado
        if change_level is None:
            change_level = self._determine_change_level(current_content, content)
        
        # Incrementar versão
        new_version = self._increment_version(current_version, change_level)
        
        # Gerar diff
        diff = self._generate_diff(current_content, content)
        
        # Criar informações da nova versão
        version_info = {
            "version": new_version,
            "artifact_id": artifact_id,
            "content_hash": new_content_hash,
            "created_at": datetime.now().isoformat(),
            "created_by": metadata.get("created_by", "unknown"),
            "file_path": os.path.join(self.versions_dir, f"{artifact_id}_v{new_version}.txt"),
            "metadata": metadata,
            "changes": changes or f"Updated from version {current_version}",
            "previous_version": current_version,
            "diff": diff
        }
        
        # Salvar conteúdo da nova versão
        with open(version_info["file_path"], 'w') as f:
            f.write(content)
        
        # Atualizar registro de versões
        artifact_versions["current_version"] = new_version
        artifact_versions["updated_at"] = datetime.now().isoformat()
        artifact_versions["versions"][new_version] = version_info
        self._save_registry()
        
        return {
            "success": True,
            "version_info": version_info,
            "previous_version": current_version,
            "change_level": change_level
        }
    
    def get_version(self, artifact_id: str, version: str = None) -> Dict[str, Any]:
        """
        Obtém versão específica de um artefato
        
        Args:
            artifact_id: ID do artefato
            version: Versão específica (usa versão atual se None)
            
        Returns:
            Dict: Informações e conteúdo da versão
        """
        # Verificar se artefato tem versões
        if artifact_id not in self.versions_registry["artifact_versions"]:
            return {
                "success": False,
                "error": f"Artifact {artifact_id} has no versions"
            }
        
        artifact_versions = self.versions_registry["artifact_versions"][artifact_id]
        
        # Determinar versão a obter
        if version is None:
            version = artifact_versions["current_version"]
        
        # Verificar se versão existe
        if version not in artifact_versions["versions"]:
            return {
                "success": False,
                "error": f"Version {version} not found for artifact {artifact_id}"
            }
        
        version_info = artifact_versions["versions"][version]
        
        # Carregar conteúdo da versão
        try:
            with open(version_info["file_path"], 'r') as f:
                content = f.read()
            
            return {
                "success": True,
                "version_info": version_info,
                "content": content
            }
        except:
            return {
                "success": False,
                "error": f"Failed to load content for version {version} of artifact {artifact_id}",
                "version_info": version_info
            }
    
    def get_version_history(self, artifact_id: str) -> Dict[str, Any]:
        """
        Obtém histórico de versões de um artefato
        
        Args:
            artifact_id: ID do artefato
            
        Returns:
            Dict: Histórico de versões
        """
        # Verificar se artefato tem versões
        if artifact_id not in self.versions_registry["artifact_versions"]:
            return {
                "success": False,
                "error": f"Artifact {artifact_id} has no versions"
            }
        
        artifact_versions = self.versions_registry["artifact_versions"][artifact_id]
        
        # Construir histórico de versões
        versions = []
        for version, info in artifact_versions["versions"].items():
            versions.append({
                "version": version,
                "created_at": info["created_at"],
                "created_by": info["created_by"],
                "changes": info.get("changes", ""),
                "previous_version": info.get("previous_version")
            })
        
        # Ordenar versões por data de criação
        versions.sort(key=lambda x: x["created_at"])
        
        return {
            "success": True,
            "artifact_id": artifact_id,
            "current_version": artifact_versions["current_version"],
            "versions": versions,
            "created_at": artifact_versions["created_at"],
            "updated_at": artifact_versions["updated_at"]
        }
    
    def compare_versions(self, artifact_id: str, version1: str, version2: str) -> Dict[str, Any]:
        """
        Compara duas versões de um artefato
        
        Args:
            artifact_id: ID do artefato
            version1: Primeira versão
            version2: Segunda versão
            
        Returns:
            Dict: Resultado da comparação
        """
        # Obter conteúdo das versões
        v1_result = self.get_version(artifact_id, version1)
        v2_result = self.get_version(artifact_id, version2)
        
        if not v1_result["success"]:
            return v1_result
        
        if not v2_result["success"]:
            return v2_result
        
        # Gerar diff
        diff = self._generate_diff(v1_result["content"], v2_result["content"])
        
        return {
            "success": True,
            "artifact_id": artifact_id,
            "version1": version1,
            "version2": version2,
            "diff": diff,
            "version1_info": v1_result["version_info"],
            "version2_info": v2_result["version_info"]
        }
    
    def revert_to_version(self, artifact_id: str, version: str) -> Dict[str, Any]:
        """
        Reverte artefato para versão específica
        
        Args:
            artifact_id: ID do artefato
            version: Versão para reverter
            
        Returns:
            Dict: Informações da nova versão criada
        """
        # Obter versão especificada
        version_result = self.get_version(artifact_id, version)
        
        if not version_result["success"]:
            return version_result
        
        # Obter versão atual
        current_version_result = self.get_version(artifact_id)
        
        if not current_version_result["success"]:
            return current_version_result
        
        # Verificar se já está na versão especificada
        if version == current_version_result["version_info"]["version"]:
            return {
                "success": False,
                "error": f"Already at version {version}",
                "version_info": current_version_result["version_info"]
            }
        
        # Criar nova versão com conteúdo da versão especificada
        metadata = version_result["version_info"]["metadata"]
        metadata["created_by"] = "revert_operation"
        
        return self.create_new_version(
            artifact_id,
            version_result["content"],
            metadata,
            "minor",  # Reverter é sempre uma mudança minor
            f"Reverted to version {version}"
        )

# Instância global para uso em todo o sistema
versioning_system = VersioningSystem()
