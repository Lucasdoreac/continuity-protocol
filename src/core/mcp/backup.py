#!/usr/bin/env python3
"""
Backup System - Continuity Protocol
Sistema de backup automático para repositórios externos
"""

import os
import sys
import json
import time
import shutil
import subprocess
from datetime import datetime
from typing import Dict, List, Any, Optional, Union

class BackupSystem:
    """
    Sistema de backup automático para o Continuity Protocol
    """
    
    def __init__(self, backup_dir: str = None, git_enabled: bool = True):
        """
        Inicializa o sistema de backup
        
        Args:
            backup_dir: Diretório para armazenamento de backups
            git_enabled: Se True, habilita integração com Git
        """
        # Configurar diretório de backup
        if backup_dir:
            self.backup_dir = backup_dir
        else:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            self.backup_dir = os.path.join(base_dir, "backups")
        
        # Criar diretório se não existir
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # Configurar integração com Git
        self.git_enabled = git_enabled
        self.git_repo_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # Arquivo de registro de backups
        self.registry_file = os.path.join(self.backup_dir, "backup_registry.json")
        
        # Carregar ou criar registro de backups
        self.backup_registry = self._load_or_create_registry()
        
        # Verificar se Git está disponível
        if self.git_enabled:
            self.git_available = self._check_git_available()
        else:
            self.git_available = False
    
    def _load_or_create_registry(self) -> Dict[str, Any]:
        """
        Carrega ou cria registro de backups
        
        Returns:
            Dict: Registro de backups
        """
        if os.path.exists(self.registry_file):
            try:
                with open(self.registry_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        # Criar registro vazio
        registry = {
            "backups": [],
            "git_commits": [],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "last_backup": None,
            "last_git_commit": None
        }
        
        # Salvar registro
        with open(self.registry_file, 'w') as f:
            json.dump(registry, f, indent=2)
        
        return registry
    
    def _save_registry(self) -> None:
        """Salva registro de backups"""
        self.backup_registry["updated_at"] = datetime.now().isoformat()
        with open(self.registry_file, 'w') as f:
            json.dump(self.backup_registry, f, indent=2)
    
    def _check_git_available(self) -> bool:
        """
        Verifica se Git está disponível
        
        Returns:
            bool: True se Git está disponível, False caso contrário
        """
        try:
            # Verificar se git está instalado
            result = subprocess.run(
                ["git", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                print("Git não está disponível")
                return False
            
            # Verificar se diretório é um repositório Git
            result = subprocess.run(
                ["git", "rev-parse", "--is-inside-work-tree"],
                cwd=self.git_repo_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0 or result.stdout.strip() != "true":
                print(f"Diretório {self.git_repo_path} não é um repositório Git")
                return False
            
            return True
        except:
            print("Erro ao verificar disponibilidade do Git")
            return False
    
    def _run_git_command(self, command: List[str]) -> Dict[str, Any]:
        """
        Executa comando Git
        
        Args:
            command: Lista de argumentos para comando Git
            
        Returns:
            Dict: Resultado da execução
        """
        if not self.git_available:
            return {
                "success": False,
                "error": "Git não está disponível"
            }
        
        try:
            result = subprocess.run(
                ["git"] + command,
                cwd=self.git_repo_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Timeout ao executar comando Git"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro ao executar comando Git: {str(e)}"
            }
    
    def create_backup(self, backup_type: str = "full", description: str = None) -> Dict[str, Any]:
        """
        Cria backup do sistema
        
        Args:
            backup_type: Tipo de backup ("full", "incremental")
            description: Descrição do backup
            
        Returns:
            Dict: Informações do backup criado
        """
        # Gerar ID do backup
        backup_id = f"backup_{int(time.time())}_{backup_type}"
        backup_dir = os.path.join(self.backup_dir, backup_id)
        
        # Criar diretório do backup
        os.makedirs(backup_dir, exist_ok=True)
        
        # Determinar diretórios a serem copiados
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        shared_context_dir = os.path.join(base_dir, "shared_context")
        
        # Criar informações do backup
        backup_info = {
            "id": backup_id,
            "type": backup_type,
            "created_at": datetime.now().isoformat(),
            "description": description or f"Backup {backup_type} automático",
            "directory": backup_dir,
            "files_count": 0,
            "size_bytes": 0
        }
        
        try:
            # Copiar diretório shared_context
            if os.path.exists(shared_context_dir):
                dest_dir = os.path.join(backup_dir, "shared_context")
                shutil.copytree(shared_context_dir, dest_dir)
                
                # Contar arquivos e tamanho
                files_count = 0
                size_bytes = 0
                
                for root, _, files in os.walk(dest_dir):
                    for file in files:
                        files_count += 1
                        size_bytes += os.path.getsize(os.path.join(root, file))
                
                backup_info["files_count"] = files_count
                backup_info["size_bytes"] = size_bytes
            
            # Adicionar backup ao registro
            self.backup_registry["backups"].append(backup_info)
            self.backup_registry["last_backup"] = backup_info["created_at"]
            self._save_registry()
            
            return {
                "success": True,
                "backup_info": backup_info
            }
        except Exception as e:
            # Remover diretório do backup em caso de erro
            if os.path.exists(backup_dir):
                shutil.rmtree(backup_dir)
            
            return {
                "success": False,
                "error": f"Erro ao criar backup: {str(e)}"
            }
    
    def git_commit_changes(self, message: str = None) -> Dict[str, Any]:
        """
        Commit de alterações no repositório Git
        
        Args:
            message: Mensagem do commit
            
        Returns:
            Dict: Resultado do commit
        """
        if not self.git_available:
            return {
                "success": False,
                "error": "Git não está disponível"
            }
        
        # Verificar se há alterações
        status_result = self._run_git_command(["status", "--porcelain"])
        
        if not status_result["success"]:
            return status_result
        
        if not status_result["stdout"].strip():
            return {
                "success": False,
                "error": "Não há alterações para commit"
            }
        
        # Adicionar alterações
        add_result = self._run_git_command(["add", "."])
        
        if not add_result["success"]:
            return add_result
        
        # Criar commit
        commit_message = message or f"Backup automático - {datetime.now().isoformat()}"
        commit_result = self._run_git_command(["commit", "-m", commit_message])
        
        if not commit_result["success"]:
            return commit_result
        
        # Obter hash do commit
        hash_result = self._run_git_command(["rev-parse", "HEAD"])
        
        if not hash_result["success"]:
            return hash_result
        
        commit_hash = hash_result["stdout"].strip()
        
        # Registrar commit
        commit_info = {
            "hash": commit_hash,
            "message": commit_message,
            "created_at": datetime.now().isoformat(),
            "files_changed": len(status_result["stdout"].strip().splitlines())
        }
        
        self.backup_registry["git_commits"].append(commit_info)
        self.backup_registry["last_git_commit"] = commit_info["created_at"]
        self._save_registry()
        
        return {
            "success": True,
            "commit_info": commit_info
        }
    
    def git_push_changes(self, remote: str = "origin", branch: str = "main") -> Dict[str, Any]:
        """
        Push de alterações para repositório remoto
        
        Args:
            remote: Nome do repositório remoto
            branch: Nome da branch
            
        Returns:
            Dict: Resultado do push
        """
        if not self.git_available:
            return {
                "success": False,
                "error": "Git não está disponível"
            }
        
        # Verificar se há commits para push
        status_result = self._run_git_command(["status", "-sb"])
        
        if not status_result["success"]:
            return status_result
        
        if "ahead" not in status_result["stdout"]:
            return {
                "success": False,
                "error": "Não há commits para push"
            }
        
        # Push para repositório remoto
        push_result = self._run_git_command(["push", remote, branch])
        
        return {
            "success": push_result["success"],
            "stdout": push_result.get("stdout", ""),
            "stderr": push_result.get("stderr", ""),
            "remote": remote,
            "branch": branch
        }
    
    def restore_backup(self, backup_id: str) -> Dict[str, Any]:
        """
        Restaura backup
        
        Args:
            backup_id: ID do backup
            
        Returns:
            Dict: Resultado da restauração
        """
        # Verificar se backup existe
        backup_info = None
        for backup in self.backup_registry["backups"]:
            if backup["id"] == backup_id:
                backup_info = backup
                break
        
        if backup_info is None:
            return {
                "success": False,
                "error": f"Backup {backup_id} não encontrado"
            }
        
        backup_dir = backup_info["directory"]
        
        if not os.path.exists(backup_dir):
            return {
                "success": False,
                "error": f"Diretório do backup {backup_id} não encontrado"
            }
        
        try:
            # Determinar diretórios a serem restaurados
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            shared_context_dir = os.path.join(base_dir, "shared_context")
            backup_shared_context_dir = os.path.join(backup_dir, "shared_context")
            
            # Criar backup do estado atual antes de restaurar
            current_backup_result = self.create_backup("pre_restore", f"Backup automático antes de restaurar {backup_id}")
            
            if not current_backup_result["success"]:
                return {
                    "success": False,
                    "error": f"Erro ao criar backup do estado atual: {current_backup_result.get('error', 'Erro desconhecido')}"
                }
            
            # Remover diretório atual
            if os.path.exists(shared_context_dir):
                shutil.rmtree(shared_context_dir)
            
            # Copiar diretório do backup
            if os.path.exists(backup_shared_context_dir):
                shutil.copytree(backup_shared_context_dir, shared_context_dir)
            
            return {
                "success": True,
                "backup_info": backup_info,
                "pre_restore_backup": current_backup_result["backup_info"]
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro ao restaurar backup: {str(e)}"
            }
    
    def get_backups_list(self) -> Dict[str, Any]:
        """
        Obtém lista de backups
        
        Returns:
            Dict: Lista de backups
        """
        return {
            "success": True,
            "backups": self.backup_registry["backups"],
            "last_backup": self.backup_registry["last_backup"],
            "count": len(self.backup_registry["backups"])
        }
    
    def get_git_commits_list(self) -> Dict[str, Any]:
        """
        Obtém lista de commits Git
        
        Returns:
            Dict: Lista de commits
        """
        return {
            "success": True,
            "git_commits": self.backup_registry["git_commits"],
            "last_git_commit": self.backup_registry["last_git_commit"],
            "count": len(self.backup_registry["git_commits"]),
            "git_available": self.git_available
        }
    
    def setup_automatic_backup(self, interval_minutes: int = 60) -> Dict[str, Any]:
        """
        Configura backup automático
        
        Args:
            interval_minutes: Intervalo entre backups em minutos
            
        Returns:
            Dict: Resultado da configuração
        """
        # Criar script de backup
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        script_path = os.path.join(base_dir, "auto_backup.py")
        
        script_content = f"""#!/usr/bin/env python3
import os
import sys
import time
from datetime import datetime

# Adicionar diretório pai ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar sistema de backup
from core.mcp.backup import BackupSystem

def run_backup():
    print(f"[{{datetime.now().isoformat()}}] Iniciando backup automático...")
    
    # Criar sistema de backup
    backup_system = BackupSystem()
    
    # Criar backup
    backup_result = backup_system.create_backup("auto", "Backup automático agendado")
    
    if backup_result["success"]:
        print(f"[{{datetime.now().isoformat()}}] Backup criado com sucesso: {{backup_result['backup_info']['id']}}")
    else:
        print(f"[{{datetime.now().isoformat()}}] Erro ao criar backup: {{backup_result.get('error', 'Erro desconhecido')}}")
    
    # Commit de alterações
    if backup_system.git_available:
        commit_result = backup_system.git_commit_changes("Backup automático agendado")
        
        if commit_result["success"]:
            print(f"[{{datetime.now().isoformat()}}] Commit criado com sucesso: {{commit_result['commit_info']['hash']}}")
        else:
            print(f"[{{datetime.now().isoformat()}}] Erro ao criar commit: {{commit_result.get('error', 'Erro desconhecido')}}")

if __name__ == "__main__":
    # Intervalo entre backups em segundos
    interval = {interval_minutes * 60}
    
    while True:
        try:
            run_backup()
        except Exception as e:
            print(f"[{{datetime.now().isoformat()}}] Erro ao executar backup: {{str(e)}}")
        
        print(f"[{{datetime.now().isoformat()}}] Próximo backup em {{interval // 60}} minutos...")
        time.sleep(interval)
"""
        
        try:
            # Salvar script
            with open(script_path, 'w') as f:
                f.write(script_content)
            
            # Tornar script executável
            os.chmod(script_path, 0o755)
            
            # Criar script de inicialização
            start_script_path = os.path.join(base_dir, "start_auto_backup.sh")
            
            start_script_content = f"""#!/bin/bash
cd {base_dir}
nohup python3 auto_backup.py > backups/auto_backup.log 2>&1 &
echo $! > backups/auto_backup.pid
echo "Backup automático iniciado com PID $(cat backups/auto_backup.pid)"
"""
            
            with open(start_script_path, 'w') as f:
                f.write(start_script_content)
            
            # Tornar script executável
            os.chmod(start_script_path, 0o755)
            
            # Criar script para parar backup automático
            stop_script_path = os.path.join(base_dir, "stop_auto_backup.sh")
            
            stop_script_content = """#!/bin/bash
if [ -f backups/auto_backup.pid ]; then
    pid=$(cat backups/auto_backup.pid)
    if ps -p $pid > /dev/null; then
        kill $pid
        echo "Backup automático parado (PID $pid)"
    else
        echo "Processo de backup automático não está rodando"
    fi
    rm backups/auto_backup.pid
else
    echo "Arquivo PID não encontrado"
fi
"""
            
            with open(stop_script_path, 'w') as f:
                f.write(stop_script_content)
            
            # Tornar script executável
            os.chmod(stop_script_path, 0o755)
            
            return {
                "success": True,
                "interval_minutes": interval_minutes,
                "script_path": script_path,
                "start_script_path": start_script_path,
                "stop_script_path": stop_script_path,
                "message": f"Backup automático configurado para executar a cada {interval_minutes} minutos"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro ao configurar backup automático: {str(e)}"
            }

# Instância global para uso em todo o sistema
backup_system = BackupSystem()
