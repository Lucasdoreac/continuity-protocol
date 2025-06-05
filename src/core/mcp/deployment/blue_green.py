#!/usr/bin/env python3
"""
Blue-Green Deployment - Continuity Protocol
Implementação de estratégia de deployment Blue-Green para o Continuity Protocol
"""

import os
import sys
import json
import time
import shutil
import subprocess
from datetime import datetime
from typing import Dict, List, Any, Optional, Union

# Adicionar diretório pai ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Importar componentes
try:
    from core.mcp.backup import backup_system
    from core.mcp.notification import notification_system
except ImportError:
    print("Erro ao importar componentes do Continuity Protocol")
    sys.exit(1)

class BlueGreenDeployment:
    """
    Implementação de estratégia de deployment Blue-Green para o Continuity Protocol
    """
    
    def __init__(self, base_dir: str = None):
        """
        Inicializa o sistema de deployment Blue-Green
        
        Args:
            base_dir: Diretório base do Continuity Protocol
        """
        # Configurar diretório base
        if base_dir:
            self.base_dir = base_dir
        else:
            self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        
        # Diretórios de ambiente
        self.blue_dir = os.path.join(self.base_dir, "environments", "blue")
        self.green_dir = os.path.join(self.base_dir, "environments", "green")
        self.staging_dir = os.path.join(self.base_dir, "environments", "staging")
        
        # Arquivo de configuração
        self.config_file = os.path.join(self.base_dir, "environments", "deployment_config.json")
        
        # Criar diretórios se não existirem
        for directory in [os.path.join(self.base_dir, "environments"), self.blue_dir, self.green_dir, self.staging_dir]:
            os.makedirs(directory, exist_ok=True)
        
        # Carregar ou criar configuração
        self.config = self._load_or_create_config()
    
    def _load_or_create_config(self) -> Dict[str, Any]:
        """
        Carrega ou cria configuração de deployment
        
        Returns:
            Dict: Configuração de deployment
        """
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        # Criar configuração padrão
        config = {
            "active_environment": "blue",
            "last_deployment": None,
            "deployments": [],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # Salvar configuração
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        return config
    
    def _save_config(self) -> None:
        """Salva configuração de deployment"""
        self.config["updated_at"] = datetime.now().isoformat()
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def _run_command(self, command: List[str], cwd: str = None) -> Dict[str, Any]:
        """
        Executa comando
        
        Args:
            command: Lista de argumentos para comando
            cwd: Diretório de trabalho
            
        Returns:
            Dict: Resultado da execução
        """
        try:
            result = subprocess.run(
                command,
                cwd=cwd or self.base_dir,
                capture_output=True,
                text=True,
                timeout=60
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
                "error": "Timeout ao executar comando"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro ao executar comando: {str(e)}"
            }
    
    def prepare_deployment(self, version: str, source_dir: str = None) -> Dict[str, Any]:
        """
        Prepara deployment para staging
        
        Args:
            version: Versão do deployment
            source_dir: Diretório de origem (usa base_dir se None)
            
        Returns:
            Dict: Resultado da preparação
        """
        # Criar backup antes do deployment
        backup_result = backup_system.create_backup(
            "pre_deployment",
            f"Backup antes do deployment da versão {version}"
        )
        
        if not backup_result["success"]:
            return {
                "success": False,
                "error": f"Falha ao criar backup: {backup_result.get('error', 'Erro desconhecido')}"
            }
        
        # Diretório de origem
        if source_dir is None:
            source_dir = self.base_dir
        
        # Limpar diretório de staging
        try:
            if os.path.exists(self.staging_dir):
                shutil.rmtree(self.staging_dir)
            os.makedirs(self.staging_dir, exist_ok=True)
        except Exception as e:
            return {
                "success": False,
                "error": f"Falha ao limpar diretório de staging: {str(e)}"
            }
        
        # Copiar arquivos para staging
        try:
            # Arquivos e diretórios a serem copiados
            items_to_copy = [
                "core",
                "shared_context",
                "environments",
                "*.py",
                "*.sh",
                "README*.md"
            ]
            
            # Copiar cada item
            for item in items_to_copy:
                if "*" in item:
                    # Usar glob para arquivos com wildcard
                    import glob
                    for file_path in glob.glob(os.path.join(source_dir, item)):
                        if os.path.isfile(file_path):
                            dest_path = os.path.join(self.staging_dir, os.path.basename(file_path))
                            shutil.copy2(file_path, dest_path)
                else:
                    # Copiar diretório ou arquivo específico
                    src_path = os.path.join(source_dir, item)
                    dest_path = os.path.join(self.staging_dir, item)
                    
                    if os.path.exists(src_path):
                        if os.path.isdir(src_path):
                            shutil.copytree(src_path, dest_path, dirs_exist_ok=True)
                        else:
                            shutil.copy2(src_path, dest_path)
        except Exception as e:
            return {
                "success": False,
                "error": f"Falha ao copiar arquivos para staging: {str(e)}"
            }
        
        # Criar arquivo de versão
        version_file = os.path.join(self.staging_dir, "VERSION")
        try:
            with open(version_file, 'w') as f:
                f.write(f"{version}\n")
                f.write(f"Prepared: {datetime.now().isoformat()}\n")
        except Exception as e:
            return {
                "success": False,
                "error": f"Falha ao criar arquivo de versão: {str(e)}"
            }
        
        # Notificar sobre preparação
        notification_system.create_notification(
            f"Deployment {version} preparado",
            f"Deployment da versão {version} preparado para staging",
            "info",
            "deployment",
            {
                "version": version,
                "stage": "prepared",
                "backup_id": backup_result["backup_info"]["id"]
            }
        )
        
        return {
            "success": True,
            "version": version,
            "staging_dir": self.staging_dir,
            "backup_id": backup_result["backup_info"]["id"]
        }
    
    def test_deployment(self, version: str) -> Dict[str, Any]:
        """
        Testa deployment em staging
        
        Args:
            version: Versão do deployment
            
        Returns:
            Dict: Resultado dos testes
        """
        # Verificar se versão está em staging
        version_file = os.path.join(self.staging_dir, "VERSION")
        if not os.path.exists(version_file):
            return {
                "success": False,
                "error": f"Versão {version} não encontrada em staging"
            }
        
        # Verificar se é a versão correta
        try:
            with open(version_file, 'r') as f:
                staging_version = f.readline().strip()
                if staging_version != version:
                    return {
                        "success": False,
                        "error": f"Versão em staging ({staging_version}) não corresponde à versão solicitada ({version})"
                    }
        except Exception as e:
            return {
                "success": False,
                "error": f"Falha ao ler arquivo de versão: {str(e)}"
            }
        
        # Executar testes
        test_script = os.path.join(self.staging_dir, "core", "mcp", "testing", "run_tests.py")
        if not os.path.exists(test_script):
            return {
                "success": False,
                "error": f"Script de testes não encontrado: {test_script}"
            }
        
        # Executar testes de integração
        integration_result = self._run_command(
            ["python3", test_script, "--type", "integration"],
            self.staging_dir
        )
        
        if not integration_result["success"]:
            return {
                "success": False,
                "error": f"Falha nos testes de integração: {integration_result.get('stderr', 'Erro desconhecido')}"
            }
        
        # Executar testes funcionais
        functional_result = self._run_command(
            ["python3", test_script, "--type", "functional"],
            self.staging_dir
        )
        
        if not functional_result["success"]:
            return {
                "success": False,
                "error": f"Falha nos testes funcionais: {functional_result.get('stderr', 'Erro desconhecido')}"
            }
        
        # Notificar sobre testes
        notification_system.create_notification(
            f"Testes do deployment {version} concluídos",
            f"Testes do deployment da versão {version} concluídos com sucesso",
            "success",
            "deployment",
            {
                "version": version,
                "stage": "tested"
            }
        )
        
        return {
            "success": True,
            "version": version,
            "integration_tests": integration_result["success"],
            "functional_tests": functional_result["success"]
        }
    
    def deploy(self, version: str) -> Dict[str, Any]:
        """
        Realiza deployment da versão em staging para ambiente inativo
        
        Args:
            version: Versão do deployment
            
        Returns:
            Dict: Resultado do deployment
        """
        # Verificar se versão está em staging
        version_file = os.path.join(self.staging_dir, "VERSION")
        if not os.path.exists(version_file):
            return {
                "success": False,
                "error": f"Versão {version} não encontrada em staging"
            }
        
        # Verificar se é a versão correta
        try:
            with open(version_file, 'r') as f:
                staging_version = f.readline().strip()
                if staging_version != version:
                    return {
                        "success": False,
                        "error": f"Versão em staging ({staging_version}) não corresponde à versão solicitada ({version})"
                    }
        except Exception as e:
            return {
                "success": False,
                "error": f"Falha ao ler arquivo de versão: {str(e)}"
            }
        
        # Determinar ambiente inativo
        active_env = self.config["active_environment"]
        inactive_env = "green" if active_env == "blue" else "blue"
        inactive_dir = self.green_dir if inactive_env == "green" else self.blue_dir
        
        # Limpar ambiente inativo
        try:
            if os.path.exists(inactive_dir):
                shutil.rmtree(inactive_dir)
            os.makedirs(inactive_dir, exist_ok=True)
        except Exception as e:
            return {
                "success": False,
                "error": f"Falha ao limpar ambiente inativo: {str(e)}"
            }
        
        # Copiar arquivos de staging para ambiente inativo
        try:
            for item in os.listdir(self.staging_dir):
                src_path = os.path.join(self.staging_dir, item)
                dest_path = os.path.join(inactive_dir, item)
                
                if os.path.isdir(src_path):
                    shutil.copytree(src_path, dest_path, dirs_exist_ok=True)
                else:
                    shutil.copy2(src_path, dest_path)
        except Exception as e:
            return {
                "success": False,
                "error": f"Falha ao copiar arquivos para ambiente inativo: {str(e)}"
            }
        
        # Registrar deployment
        deployment_info = {
            "version": version,
            "environment": inactive_env,
            "deployed_at": datetime.now().isoformat(),
            "deployed_by": "blue_green_deployment",
            "status": "deployed"
        }
        
        self.config["deployments"].append(deployment_info)
        self.config["last_deployment"] = deployment_info
        self._save_config()
        
        # Notificar sobre deployment
        notification_system.create_notification(
            f"Deployment {version} concluído",
            f"Deployment da versão {version} concluído no ambiente {inactive_env}",
            "success",
            "deployment",
            {
                "version": version,
                "environment": inactive_env,
                "stage": "deployed"
            }
        )
        
        return {
            "success": True,
            "version": version,
            "environment": inactive_env,
            "deployed_at": deployment_info["deployed_at"]
        }
    
    def switch(self) -> Dict[str, Any]:
        """
        Alterna entre ambientes blue e green
        
        Returns:
            Dict: Resultado da alternância
        """
        # Verificar se há deployment recente
        if not self.config["last_deployment"]:
            return {
                "success": False,
                "error": "Nenhum deployment recente encontrado"
            }
        
        # Ambiente atual e novo
        current_env = self.config["active_environment"]
        new_env = "green" if current_env == "blue" else "blue"
        
        # Verificar se novo ambiente está pronto
        new_env_dir = self.green_dir if new_env == "green" else self.blue_dir
        version_file = os.path.join(new_env_dir, "VERSION")
        
        if not os.path.exists(version_file):
            return {
                "success": False,
                "error": f"Ambiente {new_env} não está pronto para switch"
            }
        
        # Ler versão do novo ambiente
        try:
            with open(version_file, 'r') as f:
                new_version = f.readline().strip()
        except Exception as e:
            return {
                "success": False,
                "error": f"Falha ao ler arquivo de versão: {str(e)}"
            }
        
        # Atualizar configuração
        self.config["active_environment"] = new_env
        self._save_config()
        
        # Criar links simbólicos para ambiente ativo
        active_link = os.path.join(self.base_dir, "active")
        try:
            if os.path.exists(active_link) or os.path.islink(active_link):
                os.unlink(active_link)
            os.symlink(new_env_dir, active_link)
        except Exception as e:
            return {
                "success": False,
                "error": f"Falha ao criar link simbólico: {str(e)}"
            }
        
        # Notificar sobre switch
        notification_system.create_notification(
            f"Switch para ambiente {new_env}",
            f"Switch para ambiente {new_env} com versão {new_version}",
            "success",
            "deployment",
            {
                "version": new_version,
                "previous_environment": current_env,
                "new_environment": new_env,
                "stage": "switched"
            }
        )
        
        return {
            "success": True,
            "previous_environment": current_env,
            "new_environment": new_env,
            "version": new_version
        }
    
    def rollback(self) -> Dict[str, Any]:
        """
        Realiza rollback para ambiente anterior
        
        Returns:
            Dict: Resultado do rollback
        """
        # Verificar se há deployment anterior
        if len(self.config["deployments"]) < 2:
            return {
                "success": False,
                "error": "Não há deployment anterior para rollback"
            }
        
        # Ambiente atual e anterior
        current_env = self.config["active_environment"]
        previous_env = "green" if current_env == "blue" else "blue"
        
        # Verificar se ambiente anterior está disponível
        previous_env_dir = self.green_dir if previous_env == "green" else self.blue_dir
        version_file = os.path.join(previous_env_dir, "VERSION")
        
        if not os.path.exists(version_file):
            return {
                "success": False,
                "error": f"Ambiente {previous_env} não está disponível para rollback"
            }
        
        # Ler versão do ambiente anterior
        try:
            with open(version_file, 'r') as f:
                previous_version = f.readline().strip()
        except Exception as e:
            return {
                "success": False,
                "error": f"Falha ao ler arquivo de versão: {str(e)}"
            }
        
        # Atualizar configuração
        self.config["active_environment"] = previous_env
        
        # Remover último deployment
        last_deployment = self.config["deployments"].pop()
        
        # Atualizar último deployment
        if self.config["deployments"]:
            self.config["last_deployment"] = self.config["deployments"][-1]
        else:
            self.config["last_deployment"] = None
        
        self._save_config()
        
        # Criar links simbólicos para ambiente ativo
        active_link = os.path.join(self.base_dir, "active")
        try:
            if os.path.exists(active_link) or os.path.islink(active_link):
                os.unlink(active_link)
            os.symlink(previous_env_dir, active_link)
        except Exception as e:
            return {
                "success": False,
                "error": f"Falha ao criar link simbólico: {str(e)}"
            }
        
        # Notificar sobre rollback
        notification_system.create_notification(
            f"Rollback para ambiente {previous_env}",
            f"Rollback para ambiente {previous_env} com versão {previous_version}",
            "warning",
            "deployment",
            {
                "version": previous_version,
                "previous_environment": current_env,
                "new_environment": previous_env,
                "stage": "rollback"
            }
        )
        
        return {
            "success": True,
            "previous_environment": current_env,
            "new_environment": previous_env,
            "version": previous_version,
            "rolled_back_deployment": last_deployment
        }
    
    def get_status(self) -> Dict[str, Any]:
        """
        Obtém status do deployment
        
        Returns:
            Dict: Status do deployment
        """
        # Ambiente ativo
        active_env = self.config["active_environment"]
        active_dir = self.green_dir if active_env == "green" else self.blue_dir
        
        # Ambiente inativo
        inactive_env = "green" if active_env == "blue" else "blue"
        inactive_dir = self.green_dir if inactive_env == "green" else self.blue_dir
        
        # Versões
        active_version = "unknown"
        inactive_version = "unknown"
        staging_version = "unknown"
        
        # Ler versão do ambiente ativo
        active_version_file = os.path.join(active_dir, "VERSION")
        if os.path.exists(active_version_file):
            try:
                with open(active_version_file, 'r') as f:
                    active_version = f.readline().strip()
            except:
                pass
        
        # Ler versão do ambiente inativo
        inactive_version_file = os.path.join(inactive_dir, "VERSION")
        if os.path.exists(inactive_version_file):
            try:
                with open(inactive_version_file, 'r') as f:
                    inactive_version = f.readline().strip()
            except:
                pass
        
        # Ler versão do ambiente de staging
        staging_version_file = os.path.join(self.staging_dir, "VERSION")
        if os.path.exists(staging_version_file):
            try:
                with open(staging_version_file, 'r') as f:
                    staging_version = f.readline().strip()
            except:
                pass
        
        return {
            "active_environment": active_env,
            "active_version": active_version,
            "inactive_environment": inactive_env,
            "inactive_version": inactive_version,
            "staging_version": staging_version,
            "last_deployment": self.config["last_deployment"],
            "deployments_count": len(self.config["deployments"]),
            "updated_at": self.config["updated_at"]
        }

# Instância global para uso em todo o sistema
blue_green_deployment = BlueGreenDeployment()
