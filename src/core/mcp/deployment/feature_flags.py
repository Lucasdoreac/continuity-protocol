#!/usr/bin/env python3
"""
Feature Flags - Continuity Protocol
Sistema de feature flags para rollout controlado de funcionalidades
"""

import os
import sys
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Union, Callable

# Adicionar diretório pai ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Importar componentes
try:
    from core.mcp.notification import notification_system
except ImportError:
    print("Erro ao importar componentes do Continuity Protocol")
    sys.exit(1)

class FeatureFlags:
    """
    Sistema de feature flags para rollout controlado de funcionalidades
    """
    
    def __init__(self, flags_dir: str = None):
        """
        Inicializa o sistema de feature flags
        
        Args:
            flags_dir: Diretório para armazenamento de flags
        """
        # Configurar diretório de flags
        if flags_dir:
            self.flags_dir = flags_dir
        else:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            self.flags_dir = os.path.join(base_dir, "feature_flags")
        
        # Criar diretório se não existir
        os.makedirs(self.flags_dir, exist_ok=True)
        
        # Arquivo de flags
        self.flags_file = os.path.join(self.flags_dir, "feature_flags.json")
        
        # Carregar ou criar flags
        self.flags = self._load_or_create_flags()
        
        # Callbacks para alterações de flags
        self.callbacks = {}
    
    def _load_or_create_flags(self) -> Dict[str, Any]:
        """
        Carrega ou cria flags
        
        Returns:
            Dict: Flags
        """
        if os.path.exists(self.flags_file):
            try:
                with open(self.flags_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        # Criar flags padrão
        flags = {
            "flags": {},
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # Salvar flags
        with open(self.flags_file, 'w') as f:
            json.dump(flags, f, indent=2)
        
        return flags
    
    def _save_flags(self) -> None:
        """Salva flags"""
        self.flags["updated_at"] = datetime.now().isoformat()
        with open(self.flags_file, 'w') as f:
            json.dump(self.flags, f, indent=2)
    
    def create_flag(self, flag_name: str, enabled: bool = False, description: str = None,
                   rollout_percentage: int = 100, environments: List[str] = None) -> Dict[str, Any]:
        """
        Cria uma feature flag
        
        Args:
            flag_name: Nome da flag
            enabled: Se a flag está habilitada
            description: Descrição da flag
            rollout_percentage: Porcentagem de rollout (0-100)
            environments: Lista de ambientes onde a flag está habilitada
            
        Returns:
            Dict: Informações da flag
        """
        # Validar nome da flag
        if not flag_name or not isinstance(flag_name, str):
            return {
                "success": False,
                "error": "Nome da flag inválido"
            }
        
        # Validar porcentagem de rollout
        if not isinstance(rollout_percentage, int) or rollout_percentage < 0 or rollout_percentage > 100:
            return {
                "success": False,
                "error": "Porcentagem de rollout inválida (deve ser entre 0 e 100)"
            }
        
        # Validar ambientes
        if environments is None:
            environments = ["development", "staging", "production"]
        
        # Criar flag
        flag_info = {
            "name": flag_name,
            "enabled": enabled,
            "description": description or f"Feature flag {flag_name}",
            "rollout_percentage": rollout_percentage,
            "environments": environments,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # Adicionar flag
        self.flags["flags"][flag_name] = flag_info
        self._save_flags()
        
        # Notificar sobre criação de flag
        notification_system.create_notification(
            f"Feature flag {flag_name} criada",
            f"Feature flag {flag_name} criada com status {'habilitada' if enabled else 'desabilitada'}",
            "info",
            "feature_flags",
            {
                "flag_name": flag_name,
                "enabled": enabled,
                "rollout_percentage": rollout_percentage
            }
        )
        
        return {
            "success": True,
            "flag": flag_info
        }
    
    def update_flag(self, flag_name: str, enabled: bool = None, description: str = None,
                   rollout_percentage: int = None, environments: List[str] = None) -> Dict[str, Any]:
        """
        Atualiza uma feature flag
        
        Args:
            flag_name: Nome da flag
            enabled: Se a flag está habilitada
            description: Descrição da flag
            rollout_percentage: Porcentagem de rollout (0-100)
            environments: Lista de ambientes onde a flag está habilitada
            
        Returns:
            Dict: Informações da flag atualizada
        """
        # Verificar se flag existe
        if flag_name not in self.flags["flags"]:
            return {
                "success": False,
                "error": f"Flag {flag_name} não encontrada"
            }
        
        # Obter flag atual
        flag_info = self.flags["flags"][flag_name]
        
        # Atualizar campos
        if enabled is not None:
            flag_info["enabled"] = enabled
        
        if description is not None:
            flag_info["description"] = description
        
        if rollout_percentage is not None:
            # Validar porcentagem de rollout
            if not isinstance(rollout_percentage, int) or rollout_percentage < 0 or rollout_percentage > 100:
                return {
                    "success": False,
                    "error": "Porcentagem de rollout inválida (deve ser entre 0 e 100)"
                }
            
            flag_info["rollout_percentage"] = rollout_percentage
        
        if environments is not None:
            flag_info["environments"] = environments
        
        # Atualizar timestamp
        flag_info["updated_at"] = datetime.now().isoformat()
        
        # Salvar flags
        self._save_flags()
        
        # Executar callbacks
        self._execute_callbacks(flag_name, flag_info)
        
        # Notificar sobre atualização de flag
        notification_system.create_notification(
            f"Feature flag {flag_name} atualizada",
            f"Feature flag {flag_name} atualizada com status {'habilitada' if flag_info['enabled'] else 'desabilitada'}",
            "info",
            "feature_flags",
            {
                "flag_name": flag_name,
                "enabled": flag_info["enabled"],
                "rollout_percentage": flag_info["rollout_percentage"]
            }
        )
        
        return {
            "success": True,
            "flag": flag_info
        }
    
    def delete_flag(self, flag_name: str) -> Dict[str, Any]:
        """
        Remove uma feature flag
        
        Args:
            flag_name: Nome da flag
            
        Returns:
            Dict: Resultado da remoção
        """
        # Verificar se flag existe
        if flag_name not in self.flags["flags"]:
            return {
                "success": False,
                "error": f"Flag {flag_name} não encontrada"
            }
        
        # Remover flag
        flag_info = self.flags["flags"].pop(flag_name)
        self._save_flags()
        
        # Notificar sobre remoção de flag
        notification_system.create_notification(
            f"Feature flag {flag_name} removida",
            f"Feature flag {flag_name} foi removida do sistema",
            "info",
            "feature_flags",
            {
                "flag_name": flag_name
            }
        )
        
        return {
            "success": True,
            "flag": flag_info
        }
    
    def get_flag(self, flag_name: str) -> Dict[str, Any]:
        """
        Obtém informações de uma feature flag
        
        Args:
            flag_name: Nome da flag
            
        Returns:
            Dict: Informações da flag
        """
        # Verificar se flag existe
        if flag_name not in self.flags["flags"]:
            return {
                "success": False,
                "error": f"Flag {flag_name} não encontrada"
            }
        
        return {
            "success": True,
            "flag": self.flags["flags"][flag_name]
        }
    
    def get_all_flags(self) -> Dict[str, Any]:
        """
        Obtém todas as feature flags
        
        Returns:
            Dict: Todas as flags
        """
        return {
            "success": True,
            "flags": self.flags["flags"],
            "count": len(self.flags["flags"]),
            "updated_at": self.flags["updated_at"]
        }
    
    def is_enabled(self, flag_name: str, environment: str = "production", user_id: str = None) -> bool:
        """
        Verifica se uma feature flag está habilitada
        
        Args:
            flag_name: Nome da flag
            environment: Ambiente atual
            user_id: ID do usuário para rollout parcial
            
        Returns:
            bool: True se a flag está habilitada, False caso contrário
        """
        # Verificar se flag existe
        if flag_name not in self.flags["flags"]:
            return False
        
        flag_info = self.flags["flags"][flag_name]
        
        # Verificar se flag está habilitada
        if not flag_info["enabled"]:
            return False
        
        # Verificar se ambiente está habilitado
        if environment not in flag_info["environments"]:
            return False
        
        # Verificar porcentagem de rollout
        rollout_percentage = flag_info["rollout_percentage"]
        
        # Se rollout é 100%, flag está habilitada para todos
        if rollout_percentage == 100:
            return True
        
        # Se rollout é 0%, flag está desabilitada para todos
        if rollout_percentage == 0:
            return False
        
        # Se não há user_id, usar rollout como probabilidade
        if user_id is None:
            import random
            return random.randint(1, 100) <= rollout_percentage
        
        # Usar hash do user_id para determinar se flag está habilitada
        # Isso garante que o mesmo usuário sempre terá o mesmo resultado
        hash_value = hash(user_id) % 100
        return hash_value < rollout_percentage
    
    def register_callback(self, flag_name: str, callback: Callable[[Dict[str, Any]], None]) -> bool:
        """
        Registra callback para alterações em uma flag
        
        Args:
            flag_name: Nome da flag
            callback: Função a ser chamada quando a flag for alterada
            
        Returns:
            bool: True se callback foi registrado, False caso contrário
        """
        # Verificar se flag existe
        if flag_name not in self.flags["flags"]:
            return False
        
        # Inicializar lista de callbacks se não existir
        if flag_name not in self.callbacks:
            self.callbacks[flag_name] = []
        
        # Adicionar callback
        self.callbacks[flag_name].append(callback)
        
        return True
    
    def _execute_callbacks(self, flag_name: str, flag_info: Dict[str, Any]) -> None:
        """
        Executa callbacks para uma flag
        
        Args:
            flag_name: Nome da flag
            flag_info: Informações da flag
        """
        if flag_name not in self.callbacks:
            return
        
        for callback in self.callbacks[flag_name]:
            try:
                callback(flag_info)
            except Exception as e:
                print(f"Erro ao executar callback para flag {flag_name}: {str(e)}")
    
    def create_default_flags(self) -> Dict[str, Any]:
        """
        Cria flags padrão para o sistema
        
        Returns:
            Dict: Resultado da criação
        """
        # Lista de flags padrão
        default_flags = [
            {
                "name": "enhanced_versioning",
                "enabled": True,
                "description": "Sistema de versionamento aprimorado",
                "rollout_percentage": 100,
                "environments": ["development", "staging", "production"]
            },
            {
                "name": "automatic_backup",
                "enabled": True,
                "description": "Backup automático periódico",
                "rollout_percentage": 100,
                "environments": ["development", "staging", "production"]
            },
            {
                "name": "real_time_notifications",
                "enabled": True,
                "description": "Notificações em tempo real",
                "rollout_percentage": 100,
                "environments": ["development", "staging", "production"]
            },
            {
                "name": "advanced_search",
                "enabled": True,
                "description": "Busca avançada com indexação de conteúdo",
                "rollout_percentage": 100,
                "environments": ["development", "staging", "production"]
            },
            {
                "name": "blue_green_deployment",
                "enabled": True,
                "description": "Deployment Blue-Green",
                "rollout_percentage": 100,
                "environments": ["development", "staging", "production"]
            }
        ]
        
        # Criar flags
        created_flags = []
        
        for flag in default_flags:
            result = self.create_flag(
                flag["name"],
                flag["enabled"],
                flag["description"],
                flag["rollout_percentage"],
                flag["environments"]
            )
            
            if result["success"]:
                created_flags.append(result["flag"])
        
        return {
            "success": True,
            "flags": created_flags,
            "count": len(created_flags)
        }

# Instância global para uso em todo o sistema
feature_flags = FeatureFlags()
