#!/usr/bin/env python3
"""
Gerenciador de Projetos
Sistema para gerenciar projetos e seus contextos
"""

import os
import json
import shutil
import threading
import re
from datetime import datetime
from typing import Dict, Any, List, Optional, Set

# Suporte condicional para Git
try:
    import git
    GIT_AVAILABLE = True
except ImportError:
    GIT_AVAILABLE = False

# Constantes
MAX_HISTORY_SIZE = 100  # Número máximo de entradas no histórico
CLEANUP_INTERVAL = 3600  # Intervalo de limpeza em segundos (1 hora)

class ProjectManager:
    """
    Gerenciador de projetos escalável com suporte a integração com Git
    """
    
    def __init__(self, base_path: str):
        """
        Inicializa o gerenciador de projetos
        
        Args:
            base_path: Caminho base para armazenamento
        """
        self.base_path = base_path
        self.projects_dir = os.path.join(base_path, "projects")
        self.backups_dir = os.path.join(base_path, "project_backups")
        
        # Criar diretórios se não existirem
        os.makedirs(self.projects_dir, exist_ok=True)
        os.makedirs(self.backups_dir, exist_ok=True)
        
        # Cache de projetos ativos com lock para thread safety
        self.active_projects: Dict[str, Dict[str, Any]] = {}
        self.project_lock = threading.RLock()
        
        # Conjunto de projetos modificados que precisam ser salvos
        self.modified_projects: Set[str] = set()
        
        # Iniciar thread de salvamento periódico
        self.save_thread = threading.Thread(target=self._periodic_save, daemon=True)
        self.save_thread.start()
    
    def get_project(self, project_name: str) -> Dict[str, Any]:
        """
        Obtém ou cria um projeto
        
        Args:
            project_name: Nome do projeto
            
        Returns:
            Dict: Dados do projeto
        """
        with self.project_lock:
            # Normalizar nome do projeto
            project_id = self._normalize_project_name(project_name)
            
            # Verificar cache
            if project_id in self.active_projects:
                return self.active_projects[project_id]
            
            # Verificar arquivo
            project_file = os.path.join(self.projects_dir, f"{project_id}.json")
            if os.path.exists(project_file):
                try:
                    with open(project_file, 'r') as f:
                        project = json.load(f)
                        self.active_projects[project_id] = project
                        return project
                except Exception as e:
                    print(f"Erro ao carregar projeto {project_id}: {e}")
            
            # Criar novo projeto
            project = {
                "id": project_id,
                "name": project_name,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "description": f"Projeto {project_name}",
                "status": "active",
                "access_count": 1,
                "metadata": {},
                "context": {
                    "current_task": "Initial setup",
                    "progress": 0
                },
                "history": [
                    {
                        "timestamp": datetime.now().isoformat(),
                        "type": "creation",
                        "description": f"Projeto criado"
                    }
                ],
                "files": []
            }
            
            self.active_projects[project_id] = project
            self.modified_projects.add(project_id)
            return project
    
    def save_project(self, project_id: str) -> bool:
        """
        Salva projeto em disco
        
        Args:
            project_id: ID do projeto
            
        Returns:
            bool: True se sucesso, False caso contrário
        """
        with self.project_lock:
            if project_id not in self.active_projects:
                return False
            
            project = self.active_projects[project_id]
            project["updated_at"] = datetime.now().isoformat()
            
            project_file = os.path.join(self.projects_dir, f"{project_id}.json")
            try:
                # Criar backup antes de salvar
                if os.path.exists(project_file):
                    backup_file = os.path.join(self.backups_dir, f"{project_id}_{int(datetime.now().timestamp())}.json")
                    shutil.copy2(project_file, backup_file)
                
                # Salvar projeto
                with open(project_file, 'w') as f:
                    json.dump(project, f, indent=2)
                
                # Remover da lista de modificados
                if project_id in self.modified_projects:
                    self.modified_projects.remove(project_id)
                
                return True
            except Exception as e:
                print(f"Erro ao salvar projeto {project_id}: {e}")
                return False
    
    def update_project(self, project_id: str, updates: Dict[str, Any]) -> bool:
        """
        Atualiza informações do projeto
        
        Args:
            project_id: ID do projeto
            updates: Atualizações
            
        Returns:
            bool: True se sucesso, False caso contrário
        """
        with self.project_lock:
            # Verificar se projeto existe
            if project_id not in self.active_projects and not os.path.exists(os.path.join(self.projects_dir, f"{project_id}.json")):
                return False
            
            # Obter projeto
            project = self.get_project(project_id)
            
            # Atualizar campos permitidos
            allowed_fields = ["description", "status", "metadata", "context"]
            for field in allowed_fields:
                if field in updates:
                    if field in ["metadata", "context"] and isinstance(updates[field], dict):
                        deep_update(project[field], updates[field])
                    else:
                        project[field] = updates[field]
            
            # Adicionar entrada ao histórico
            project["history"].append({
                "timestamp": datetime.now().isoformat(),
                "type": "update",
                "description": f"Projeto atualizado"
            })
            
            # Limitar tamanho do histórico
            if len(project["history"]) > MAX_HISTORY_SIZE:
                project["history"] = project["history"][-MAX_HISTORY_SIZE:]
            
            project["access_count"] += 1
            
            self.modified_projects.add(project_id)
            return True
    
    def add_project_file(self, project_id: str, file_path: str, description: Optional[str] = None) -> bool:
        """
        Adiciona arquivo ao projeto
        
        Args:
            project_id: ID do projeto
            file_path: Caminho do arquivo
            description: Descrição do arquivo (opcional)
            
        Returns:
            bool: True se sucesso, False caso contrário
        """
        with self.project_lock:
            # Verificar se projeto existe
            if project_id not in self.active_projects and not os.path.exists(os.path.join(self.projects_dir, f"{project_id}.json")):
                return False
            
            # Obter projeto
            project = self.get_project(project_id)
            
            # Verificar se arquivo já existe
            for file in project["files"]:
                if file["path"] == file_path:
                    file["last_modified"] = datetime.now().isoformat()
                    if description:
                        file["description"] = description
                    
                    self.modified_projects.add(project_id)
                    return True
            
            # Adicionar novo arquivo
            project["files"].append({
                "path": file_path,
                "description": description or "Arquivo adicionado",
                "last_modified": datetime.now().isoformat()
            })
            
            self.modified_projects.add(project_id)
            return True
    
    def get_git_context(self, project_path: str) -> Dict[str, Any]:
        """
        Obtém contexto do Git para um projeto
        
        Args:
            project_path: Caminho do projeto
            
        Returns:
            Dict: Contexto do Git
        """
        if not GIT_AVAILABLE:
            return {
                "error": "Git não disponível. Instale com 'pip install GitPython'."
            }
        
        try:
            repo = git.Repo(project_path)
            
            # Obter commits recentes
            commits = []
            for commit in repo.iter_commits(max_count=10):
                commits.append({
                    "hash": commit.hexsha,
                    "author": commit.author.name,
                    "message": commit.message,
                    "date": commit.committed_datetime.isoformat()
                })
            
            # Obter arquivos modificados recentemente
            modified_files = []
            for commit in repo.iter_commits(max_count=5):
                for file in commit.stats.files:
                    if file not in modified_files:
                        modified_files.append(file)
            
            # Obter branches
            branches = []
            for branch in repo.branches:
                branches.append({
                    "name": branch.name,
                    "is_active": branch.name == repo.active_branch.name
                })
            
            # Obter status
            status = {
                "untracked": [],
                "modified": [],
                "staged": []
            }
            
            for file in repo.untracked_files:
                status["untracked"].append(file)
            
            for file, file_status in repo.index.diff(None):
                status["modified"].append(file.a_path)
            
            for file, file_status in repo.index.diff("HEAD"):
                status["staged"].append(file.a_path)
            
            return {
                "commits": commits,
                "modified_files": modified_files,
                "branches": branches,
                "active_branch": repo.active_branch.name,
                "status": status,
                "remote_url": repo.remotes.origin.url if repo.remotes else None
            }
        except Exception as e:
            return {
                "error": str(e)
            }
    
    def analyze_project_structure(self, project_path: str) -> Dict[str, Any]:
        """
        Analisa estrutura do projeto
        
        Args:
            project_path: Caminho do projeto
            
        Returns:
            Dict: Estrutura do projeto
        """
        if not os.path.exists(project_path) or not os.path.isdir(project_path):
            return {
                "error": f"Caminho inválido: {project_path}"
            }
        
        try:
            # Estatísticas de arquivos
            file_stats = {
                "total_files": 0,
                "by_extension": {},
                "largest_files": []
            }
            
            # Diretórios importantes
            important_dirs = []
            
            # Percorrer diretórios
            for root, dirs, files in os.walk(project_path):
                # Ignorar diretórios ocultos e node_modules
                dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'node_modules']
                
                # Verificar se é um diretório importante
                rel_path = os.path.relpath(root, project_path)
                if rel_path != '.' and (
                    'src' in rel_path or 
                    'lib' in rel_path or 
                    'test' in rel_path or 
                    'docs' in rel_path
                ):
                    important_dirs.append({
                        "path": rel_path,
                        "files_count": len(files)
                    })
                
                # Processar arquivos
                for file in files:
                    if file.startswith('.'):
                        continue
                    
                    file_stats["total_files"] += 1
                    
                    # Obter extensão
                    _, ext = os.path.splitext(file)
                    ext = ext.lower()
                    
                    if ext in file_stats["by_extension"]:
                        file_stats["by_extension"][ext] += 1
                    else:
                        file_stats["by_extension"][ext] = 1
                    
                    # Verificar tamanho do arquivo
                    file_path = os.path.join(root, file)
                    try:
                        size = os.path.getsize(file_path)
                        
                        # Adicionar à lista de maiores arquivos
                        file_stats["largest_files"].append({
                            "path": os.path.relpath(file_path, project_path),
                            "size": size
                        })
                        
                        # Manter apenas os 10 maiores
                        file_stats["largest_files"].sort(key=lambda x: x["size"], reverse=True)
                        file_stats["largest_files"] = file_stats["largest_files"][:10]
                    except:
                        pass
            
            # Detectar tipo de projeto
            project_type = "unknown"
            project_language = "unknown"
            
            # Verificar arquivos de configuração comuns
            config_files = {
                "package.json": ("javascript", "npm"),
                "requirements.txt": ("python", "pip"),
                "pom.xml": ("java", "maven"),
                "build.gradle": ("java", "gradle"),
                "Cargo.toml": ("rust", "cargo"),
                "go.mod": ("go", "go"),
                "Gemfile": ("ruby", "bundler"),
                "composer.json": ("php", "composer")
            }
            
            for config_file, (language, type_) in config_files.items():
                if os.path.exists(os.path.join(project_path, config_file)):
                    project_language = language
                    project_type = type_
                    break
            
            return {
                "path": project_path,
                "type": project_type,
                "language": project_language,
                "file_stats": file_stats,
                "important_dirs": important_dirs
            }
        except Exception as e:
            return {
                "error": str(e)
            }
    
    def get_all_projects(self) -> List[Dict[str, Any]]:
        """
        Obtém todos os projetos
        
        Returns:
            List[Dict]: Lista de metadados de projetos
        """
        projects = []
        
        # Listar arquivos de projeto
        for filename in os.listdir(self.projects_dir):
            if filename.endswith(".json"):
                project_id = filename[:-5]  # Remover extensão .json
                
                try:
                    # Carregar projeto
                    with open(os.path.join(self.projects_dir, filename), 'r') as f:
                        project = json.load(f)
                    
                    # Adicionar metadados à lista
                    projects.append({
                        "id": project_id,
                        "name": project.get("name", project_id),
                        "description": project.get("description", ""),
                        "status": project.get("status", "unknown"),
                        "created_at": project.get("created_at", ""),
                        "updated_at": project.get("updated_at", ""),
                        "access_count": project.get("access_count", 0)
                    })
                except Exception as e:
                    print(f"Erro ao carregar projeto {project_id}: {e}")
        
        # Ordenar por data de atualização (mais recente primeiro)
        projects.sort(key=lambda p: p.get("updated_at", ""), reverse=True)
        
        return projects
    
    def search_projects(self, query: str) -> List[Dict[str, Any]]:
        """
        Pesquisa projetos
        
        Args:
            query: Termo de pesquisa
            
        Returns:
            List[Dict]: Lista de projetos correspondentes
        """
        query = query.lower()
        results = []
        
        for project in self.get_all_projects():
            # Verificar correspondência no nome ou descrição
            if (query in project["name"].lower() or 
                query in project.get("description", "").lower()):
                results.append(project)
        
        return results
    
    def _normalize_project_name(self, name: str) -> str:
        """
        Normaliza nome do projeto para uso como ID
        
        Args:
            name: Nome do projeto
            
        Returns:
            str: Nome normalizado
        """
        # Remover caracteres especiais e substituir espaços por hífens
        normalized = re.sub(r'[^a-zA-Z0-9\s-]', '', name)
        normalized = re.sub(r'\s+', '-', normalized)
        return normalized.lower()
    
    def _periodic_save(self) -> None:
        """Thread para salvamento periódico de projetos modificados"""
        while True:
            try:
                # Dormir primeiro
                import time
                time.sleep(30)  # Salvar a cada 30 segundos
                
                with self.project_lock:
                    # Salvar projetos modificados
                    modified = list(self.modified_projects)
                    
                    for project_id in modified:
                        self.save_project(project_id)
                
                if modified:
                    print(f"Salvamento periódico concluído. Salvos {len(modified)} projetos.")
            except Exception as e:
                print(f"Erro durante salvamento periódico: {e}")

def deep_update(d: Dict[str, Any], u: Dict[str, Any]) -> Dict[str, Any]:
    """
    Atualiza dicionário de forma recursiva
    
    Args:
        d: Dicionário a ser atualizado
        u: Dicionário com atualizações
        
    Returns:
        Dict: Dicionário atualizado
    """
    for k, v in u.items():
        if isinstance(v, dict) and k in d and isinstance(d[k], dict):
            deep_update(d[k], v)
        else:
            d[k] = v
    return d
