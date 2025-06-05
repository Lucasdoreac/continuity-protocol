#!/usr/bin/env python3
"""
Authentication System - Continuity Protocol
Implementação de autenticação básica para o sistema
"""

import os
import json
import time
import hashlib
import secrets
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union

class AuthenticationSystem:
    """
    Sistema de autenticação básica para o Continuity Protocol
    """
    
    def __init__(self, auth_dir: str = None):
        """
        Inicializa o sistema de autenticação
        
        Args:
            auth_dir: Diretório para armazenamento de dados de autenticação
        """
        # Configurar diretório de autenticação
        if auth_dir:
            self.auth_dir = auth_dir
        else:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            self.auth_dir = os.path.join(base_dir, "auth")
        
        # Criar diretório se não existir
        os.makedirs(self.auth_dir, exist_ok=True)
        
        # Arquivo de configuração
        self.config_file = os.path.join(self.auth_dir, "auth_config.json")
        self.agents_file = os.path.join(self.auth_dir, "agents.json")
        self.tokens_file = os.path.join(self.auth_dir, "tokens.json")
        
        # Carregar ou criar configuração
        self.config = self._load_or_create_config()
        
        # Carregar ou criar registro de agentes
        self.agents = self._load_or_create_agents()
        
        # Carregar ou criar registro de tokens
        self.tokens = self._load_or_create_tokens()
    
    def _load_or_create_config(self) -> Dict[str, Any]:
        """
        Carrega ou cria configuração de autenticação
        
        Returns:
            Dict: Configuração de autenticação
        """
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        # Criar configuração padrão
        config = {
            "token_expiration_days": 30,
            "min_password_length": 8,
            "hash_algorithm": "sha256",
            "hash_iterations": 100000,
            "salt_length": 16,
            "token_length": 32,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # Salvar configuração
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        return config
    
    def _load_or_create_agents(self) -> Dict[str, Any]:
        """
        Carrega ou cria registro de agentes
        
        Returns:
            Dict: Registro de agentes
        """
        if os.path.exists(self.agents_file):
            try:
                with open(self.agents_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        # Criar registro vazio
        agents = {
            "agents": {},
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # Salvar registro
        with open(self.agents_file, 'w') as f:
            json.dump(agents, f, indent=2)
        
        return agents
    
    def _load_or_create_tokens(self) -> Dict[str, Any]:
        """
        Carrega ou cria registro de tokens
        
        Returns:
            Dict: Registro de tokens
        """
        if os.path.exists(self.tokens_file):
            try:
                with open(self.tokens_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        # Criar registro vazio
        tokens = {
            "tokens": {},
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # Salvar registro
        with open(self.tokens_file, 'w') as f:
            json.dump(tokens, f, indent=2)
        
        return tokens
    
    def _save_agents(self) -> None:
        """Salva registro de agentes"""
        self.agents["updated_at"] = datetime.now().isoformat()
        with open(self.agents_file, 'w') as f:
            json.dump(self.agents, f, indent=2)
    
    def _save_tokens(self) -> None:
        """Salva registro de tokens"""
        self.tokens["updated_at"] = datetime.now().isoformat()
        with open(self.tokens_file, 'w') as f:
            json.dump(self.tokens, f, indent=2)
    
    def _generate_salt(self) -> str:
        """
        Gera um salt aleatório
        
        Returns:
            str: Salt em formato base64
        """
        salt_length = self.config["salt_length"]
        salt = secrets.token_bytes(salt_length)
        return base64.b64encode(salt).decode('utf-8')
    
    def _hash_password(self, password: str, salt: str = None) -> Dict[str, str]:
        """
        Gera hash de senha
        
        Args:
            password: Senha a ser hasheada
            salt: Salt para hash (opcional)
            
        Returns:
            Dict: Hash e salt
        """
        # Gerar salt se não fornecido
        if salt is None:
            salt = self._generate_salt()
        else:
            # Decodificar salt se fornecido como string
            try:
                base64.b64decode(salt)
            except:
                salt = self._generate_salt()
        
        # Configurações de hash
        algorithm = self.config["hash_algorithm"]
        iterations = self.config["hash_iterations"]
        
        # Gerar hash
        password_bytes = password.encode('utf-8')
        salt_bytes = base64.b64decode(salt)
        
        hash_bytes = hashlib.pbkdf2_hmac(
            algorithm,
            password_bytes,
            salt_bytes,
            iterations
        )
        
        hash_b64 = base64.b64encode(hash_bytes).decode('utf-8')
        
        return {
            "hash": hash_b64,
            "salt": salt,
            "algorithm": algorithm,
            "iterations": iterations
        }
    
    def _generate_token(self) -> str:
        """
        Gera um token aleatório
        
        Returns:
            str: Token em formato base64
        """
        token_length = self.config["token_length"]
        token = secrets.token_bytes(token_length)
        return base64.b64encode(token).decode('utf-8')
    
    def register_agent(self, agent_id: str, agent_type: str, password: str) -> Dict[str, Any]:
        """
        Registra um novo agente
        
        Args:
            agent_id: ID do agente
            agent_type: Tipo do agente
            password: Senha do agente
            
        Returns:
            Dict: Informações do agente registrado
        """
        # Verificar se agente já existe
        if agent_id in self.agents["agents"]:
            raise ValueError(f"Agent {agent_id} already exists")
        
        # Verificar comprimento mínimo da senha
        min_length = self.config["min_password_length"]
        if len(password) < min_length:
            raise ValueError(f"Password must be at least {min_length} characters long")
        
        # Gerar hash da senha
        password_data = self._hash_password(password)
        
        # Criar registro do agente
        agent_info = {
            "id": agent_id,
            "type": agent_type,
            "password": {
                "hash": password_data["hash"],
                "salt": password_data["salt"],
                "algorithm": password_data["algorithm"],
                "iterations": password_data["iterations"]
            },
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "last_login": None
        }
        
        # Adicionar ao registro
        self.agents["agents"][agent_id] = agent_info
        self._save_agents()
        
        # Retornar informações (sem senha)
        return {
            "id": agent_info["id"],
            "type": agent_info["type"],
            "created_at": agent_info["created_at"],
            "updated_at": agent_info["updated_at"]
        }
    
    def authenticate_agent(self, agent_id: str, password: str) -> Dict[str, Any]:
        """
        Autentica um agente
        
        Args:
            agent_id: ID do agente
            password: Senha do agente
            
        Returns:
            Dict: Token de autenticação
        """
        # Verificar se agente existe
        if agent_id not in self.agents["agents"]:
            raise ValueError(f"Agent {agent_id} not found")
        
        agent_info = self.agents["agents"][agent_id]
        
        # Verificar senha
        password_data = agent_info["password"]
        hash_check = self._hash_password(
            password,
            password_data["salt"]
        )
        
        if hash_check["hash"] != password_data["hash"]:
            raise ValueError("Invalid password")
        
        # Gerar token
        token = self._generate_token()
        expiration = datetime.now() + timedelta(days=self.config["token_expiration_days"])
        
        # Registrar token
        token_info = {
            "token": token,
            "agent_id": agent_id,
            "created_at": datetime.now().isoformat(),
            "expires_at": expiration.isoformat()
        }
        
        self.tokens["tokens"][token] = token_info
        self._save_tokens()
        
        # Atualizar último login
        self.agents["agents"][agent_id]["last_login"] = datetime.now().isoformat()
        self._save_agents()
        
        return {
            "token": token,
            "agent_id": agent_id,
            "expires_at": expiration.isoformat()
        }
    
    def validate_token(self, token: str) -> Dict[str, Any]:
        """
        Valida um token de autenticação
        
        Args:
            token: Token a ser validado
            
        Returns:
            Dict: Informações do token
        """
        # Verificar se token existe
        if token not in self.tokens["tokens"]:
            raise ValueError("Invalid token")
        
        token_info = self.tokens["tokens"][token]
        
        # Verificar expiração
        expires_at = datetime.fromisoformat(token_info["expires_at"])
        if expires_at < datetime.now():
            # Remover token expirado
            del self.tokens["tokens"][token]
            self._save_tokens()
            raise ValueError("Token expired")
        
        return {
            "valid": True,
            "agent_id": token_info["agent_id"],
            "expires_at": token_info["expires_at"]
        }
    
    def revoke_token(self, token: str) -> bool:
        """
        Revoga um token de autenticação
        
        Args:
            token: Token a ser revogado
            
        Returns:
            bool: True se token foi revogado, False caso contrário
        """
        if token in self.tokens["tokens"]:
            del self.tokens["tokens"][token]
            self._save_tokens()
            return True
        return False
    
    def change_password(self, agent_id: str, current_password: str, new_password: str) -> bool:
        """
        Altera a senha de um agente
        
        Args:
            agent_id: ID do agente
            current_password: Senha atual
            new_password: Nova senha
            
        Returns:
            bool: True se senha foi alterada, False caso contrário
        """
        # Verificar se agente existe
        if agent_id not in self.agents["agents"]:
            raise ValueError(f"Agent {agent_id} not found")
        
        agent_info = self.agents["agents"][agent_id]
        
        # Verificar senha atual
        password_data = agent_info["password"]
        hash_check = self._hash_password(
            current_password,
            password_data["salt"]
        )
        
        if hash_check["hash"] != password_data["hash"]:
            raise ValueError("Invalid current password")
        
        # Verificar comprimento mínimo da nova senha
        min_length = self.config["min_password_length"]
        if len(new_password) < min_length:
            raise ValueError(f"New password must be at least {min_length} characters long")
        
        # Gerar hash da nova senha
        new_password_data = self._hash_password(new_password)
        
        # Atualizar senha
        self.agents["agents"][agent_id]["password"] = {
            "hash": new_password_data["hash"],
            "salt": new_password_data["salt"],
            "algorithm": new_password_data["algorithm"],
            "iterations": new_password_data["iterations"]
        }
        self.agents["agents"][agent_id]["updated_at"] = datetime.now().isoformat()
        self._save_agents()
        
        # Revogar todos os tokens do agente
        tokens_to_revoke = []
        for token, token_info in self.tokens["tokens"].items():
            if token_info["agent_id"] == agent_id:
                tokens_to_revoke.append(token)
        
        for token in tokens_to_revoke:
            del self.tokens["tokens"][token]
        
        if tokens_to_revoke:
            self._save_tokens()
        
        return True
    
    def get_agent_info(self, agent_id: str) -> Dict[str, Any]:
        """
        Obtém informações de um agente
        
        Args:
            agent_id: ID do agente
            
        Returns:
            Dict: Informações do agente
        """
        if agent_id not in self.agents["agents"]:
            raise ValueError(f"Agent {agent_id} not found")
        
        agent_info = self.agents["agents"][agent_id]
        
        # Retornar informações (sem senha)
        return {
            "id": agent_info["id"],
            "type": agent_info["type"],
            "created_at": agent_info["created_at"],
            "updated_at": agent_info["updated_at"],
            "last_login": agent_info["last_login"]
        }
    
    def cleanup_expired_tokens(self) -> int:
        """
        Remove tokens expirados
        
        Returns:
            int: Número de tokens removidos
        """
        tokens_to_remove = []
        now = datetime.now()
        
        for token, token_info in self.tokens["tokens"].items():
            expires_at = datetime.fromisoformat(token_info["expires_at"])
            if expires_at < now:
                tokens_to_remove.append(token)
        
        for token in tokens_to_remove:
            del self.tokens["tokens"][token]
        
        if tokens_to_remove:
            self._save_tokens()
        
        return len(tokens_to_remove)

# Instância global para uso em todo o sistema
auth_system = AuthenticationSystem()

def require_auth(func):
    """
    Decorator para exigir autenticação
    
    Args:
        func: Função a ser decorada
        
    Returns:
        Função decorada
    """
    def wrapper(*args, **kwargs):
        # Verificar se token está presente nos argumentos
        token = kwargs.get("token")
        if not token:
            # Procurar token no primeiro argumento (se for dict)
            if args and isinstance(args[0], dict) and "token" in args[0]:
                token = args[0]["token"]
        
        if not token:
            raise ValueError("Authentication token required")
        
        # Validar token
        try:
            auth_info = auth_system.validate_token(token)
            # Adicionar informações de autenticação aos kwargs
            kwargs["auth_info"] = auth_info
            return func(*args, **kwargs)
        except ValueError as e:
            raise ValueError(f"Authentication failed: {str(e)}")
    
    return wrapper
