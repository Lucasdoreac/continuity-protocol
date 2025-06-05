#!/usr/bin/env python3
"""
Gerenciador de Sessões
Sistema para gerenciar sessões de continuidade entre diferentes clientes
"""

import os
import json
import time
import shutil
import threading
from datetime import datetime
from typing import Dict, Any, List, Optional, Set

# Constantes
MAX_HISTORY_SIZE = 100  # Número máximo de entradas no histórico
CLEANUP_INTERVAL = 3600  # Intervalo de limpeza em segundos (1 hora)
SESSION_EXPIRY = 86400 * 7  # Expiração de sessão em segundos (7 dias)

class SessionManager:
    """
    Gerenciador de sessões escalável com suporte a múltiplos clientes
    """
    
    def __init__(self, base_path: str):
        """
        Inicializa o gerenciador de sessões
        
        Args:
            base_path: Caminho base para armazenamento
        """
        self.base_path = base_path
        self.sessions_dir = os.path.join(base_path, "sessions")
        self.backups_dir = os.path.join(base_path, "backups")
        
        # Criar diretórios se não existirem
        os.makedirs(self.sessions_dir, exist_ok=True)
        os.makedirs(self.backups_dir, exist_ok=True)
        
        # Cache de sessões ativas com lock para thread safety
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.session_lock = threading.RLock()
        
        # Conjunto de sessões modificadas que precisam ser salvas
        self.modified_sessions: Set[str] = set()
        
        # Iniciar thread de limpeza periódica
        self.cleanup_thread = threading.Thread(target=self._periodic_cleanup, daemon=True)
        self.cleanup_thread.start()
        
        # Iniciar thread de salvamento periódico
        self.save_thread = threading.Thread(target=self._periodic_save, daemon=True)
        self.save_thread.start()
    
    def get_session(self, session_id: str) -> Dict[str, Any]:
        """
        Obtém ou cria uma sessão
        
        Args:
            session_id: ID da sessão
            
        Returns:
            Dict: Dados da sessão
        """
        with self.session_lock:
            # Verificar cache
            if session_id in self.active_sessions:
                return self.active_sessions[session_id]
            
            # Verificar arquivo
            session_file = os.path.join(self.sessions_dir, f"{session_id}.json")
            if os.path.exists(session_file):
                try:
                    with open(session_file, 'r') as f:
                        session = json.load(f)
                        self.active_sessions[session_id] = session
                        return session
                except Exception as e:
                    print(f"Erro ao carregar sessão {session_id}: {e}")
            
            # Criar nova sessão
            session = {
                "id": session_id,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "context": {},
                "history": [],
                "metadata": {
                    "client_type": "unknown",
                    "access_count": 1
                }
            }
            
            self.active_sessions[session_id] = session
            self.modified_sessions.add(session_id)
            return session
    
    def save_session(self, session_id: str) -> bool:
        """
        Salva sessão em disco
        
        Args:
            session_id: ID da sessão
            
        Returns:
            bool: True se sucesso, False caso contrário
        """
        with self.session_lock:
            if session_id not in self.active_sessions:
                return False
            
            session = self.active_sessions[session_id]
            session["updated_at"] = datetime.now().isoformat()
            
            session_file = os.path.join(self.sessions_dir, f"{session_id}.json")
            try:
                # Criar backup antes de salvar
                if os.path.exists(session_file):
                    backup_file = os.path.join(self.backups_dir, f"{session_id}_{int(time.time())}.json")
                    shutil.copy2(session_file, backup_file)
                
                # Salvar sessão
                with open(session_file, 'w') as f:
                    json.dump(session, f, indent=2)
                
                # Remover da lista de modificados
                if session_id in self.modified_sessions:
                    self.modified_sessions.remove(session_id)
                
                return True
            except Exception as e:
                print(f"Erro ao salvar sessão {session_id}: {e}")
                return False
    
    def add_history_entry(self, session_id: str, entry_type: str, data: Dict[str, Any]) -> bool:
        """
        Adiciona entrada ao histórico da sessão
        
        Args:
            session_id: ID da sessão
            entry_type: Tipo de entrada
            data: Dados da entrada
            
        Returns:
            bool: True se sucesso, False caso contrário
        """
        with self.session_lock:
            session = self.get_session(session_id)
            
            entry = {
                "timestamp": datetime.now().isoformat(),
                "type": entry_type,
                **data
            }
            
            session["history"].append(entry)
            session["metadata"]["access_count"] += 1
            
            # Limitar tamanho do histórico
            if len(session["history"]) > MAX_HISTORY_SIZE:
                session["history"] = session["history"][-MAX_HISTORY_SIZE:]
            
            self.modified_sessions.add(session_id)
            
            # Salvar imediatamente se for uma entrada importante
            if entry_type in ["emergency", "critical", "recovery"]:
                return self.save_session(session_id)
            
            return True
    
    def update_context(self, session_id: str, context_updates: Dict[str, Any]) -> bool:
        """
        Atualiza contexto da sessão
        
        Args:
            session_id: ID da sessão
            context_updates: Atualizações de contexto
            
        Returns:
            bool: True se sucesso, False caso contrário
        """
        with self.session_lock:
            session = self.get_session(session_id)
            
            # Atualizar contexto
            deep_update(session["context"], context_updates)
            
            self.modified_sessions.add(session_id)
            
            # Salvar imediatamente se houver atualizações críticas
            if any(key in ["current_project", "emergency", "critical"] for key in context_updates.keys()):
                return self.save_session(session_id)
            
            return True
    
    def update_metadata(self, session_id: str, metadata_updates: Dict[str, Any]) -> bool:
        """
        Atualiza metadados da sessão
        
        Args:
            session_id: ID da sessão
            metadata_updates: Atualizações de metadados
            
        Returns:
            bool: True se sucesso, False caso contrário
        """
        with self.session_lock:
            session = self.get_session(session_id)
            
            # Atualizar metadados
            deep_update(session["metadata"], metadata_updates)
            
            self.modified_sessions.add(session_id)
            return True
    
    def create_backup(self, session_id: str, backup_type: str = "manual") -> Optional[str]:
        """
        Cria backup de uma sessão
        
        Args:
            session_id: ID da sessão
            backup_type: Tipo de backup
            
        Returns:
            Optional[str]: ID do backup ou None se falhar
        """
        with self.session_lock:
            # Garantir que a sessão está salva
            if not self.save_session(session_id):
                return None
            
            # Criar backup
            backup_id = f"{backup_type}_{int(time.time())}"
            backup_file = os.path.join(self.backups_dir, f"{session_id}_{backup_id}.json")
            
            try:
                session_file = os.path.join(self.sessions_dir, f"{session_id}.json")
                shutil.copy2(session_file, backup_file)
                return backup_id
            except Exception as e:
                print(f"Erro ao criar backup {backup_id} para sessão {session_id}: {e}")
                return None
    
    def restore_backup(self, session_id: str, backup_id: Optional[str] = None) -> bool:
        """
        Restaura sessão a partir de backup
        
        Args:
            session_id: ID da sessão
            backup_id: ID do backup (opcional)
            
        Returns:
            bool: True se sucesso, False caso contrário
        """
        with self.session_lock:
            # Se backup_id não for fornecido, usar o mais recente
            if not backup_id:
                backups = [f for f in os.listdir(self.backups_dir) if f.startswith(f"{session_id}_")]
                if not backups:
                    return False
                
                backups.sort(reverse=True)
                backup_file = os.path.join(self.backups_dir, backups[0])
            else:
                backup_file = os.path.join(self.backups_dir, f"{session_id}_{backup_id}.json")
            
            # Verificar se backup existe
            if not os.path.exists(backup_file):
                return False
            
            try:
                # Carregar backup
                with open(backup_file, 'r') as f:
                    backup_data = json.load(f)
                
                # Atualizar sessão
                self.active_sessions[session_id] = backup_data
                
                # Salvar sessão
                session_file = os.path.join(self.sessions_dir, f"{session_id}.json")
                with open(session_file, 'w') as f:
                    json.dump(backup_data, f, indent=2)
                
                return True
            except Exception as e:
                print(f"Erro ao restaurar backup para sessão {session_id}: {e}")
                return False
    
    def get_all_sessions(self) -> List[Dict[str, Any]]:
        """
        Obtém todas as sessões
        
        Returns:
            List[Dict]: Lista de metadados de sessões
        """
        sessions = []
        
        # Listar arquivos de sessão
        for filename in os.listdir(self.sessions_dir):
            if filename.endswith(".json"):
                session_id = filename[:-5]  # Remover extensão .json
                
                try:
                    # Carregar sessão
                    session = self.get_session(session_id)
                    
                    # Adicionar metadados à lista
                    sessions.append({
                        "id": session_id,
                        "created_at": session.get("created_at"),
                        "updated_at": session.get("updated_at"),
                        "client_type": session.get("metadata", {}).get("client_type", "unknown"),
                        "access_count": session.get("metadata", {}).get("access_count", 0),
                        "current_project": session.get("context", {}).get("current_project")
                    })
                except Exception as e:
                    print(f"Erro ao carregar sessão {session_id}: {e}")
        
        # Ordenar por data de atualização (mais recente primeiro)
        sessions.sort(key=lambda s: s.get("updated_at", ""), reverse=True)
        
        return sessions
    
    def _periodic_cleanup(self) -> None:
        """Thread para limpeza periódica de sessões expiradas"""
        while True:
            try:
                # Dormir primeiro para evitar limpeza imediata na inicialização
                time.sleep(CLEANUP_INTERVAL)
                
                print("Iniciando limpeza periódica de sessões...")
                
                with self.session_lock:
                    # Verificar sessões expiradas
                    now = time.time()
                    expired_sessions = []
                    
                    for session_id, session in self.active_sessions.items():
                        # Converter updated_at para timestamp
                        try:
                            updated_at = datetime.fromisoformat(session["updated_at"]).timestamp()
                        except:
                            updated_at = 0
                        
                        # Verificar se expirou
                        if now - updated_at > SESSION_EXPIRY:
                            expired_sessions.append(session_id)
                    
                    # Remover sessões expiradas do cache
                    for session_id in expired_sessions:
                        # Garantir que está salva antes de remover
                        if session_id in self.modified_sessions:
                            self.save_session(session_id)
                        
                        del self.active_sessions[session_id]
                        if session_id in self.modified_sessions:
                            self.modified_sessions.remove(session_id)
                
                print(f"Limpeza concluída. Removidas {len(expired_sessions)} sessões expiradas do cache.")
            except Exception as e:
                print(f"Erro durante limpeza periódica: {e}")
    
    def _periodic_save(self) -> None:
        """Thread para salvamento periódico de sessões modificadas"""
        while True:
            try:
                # Dormir primeiro
                time.sleep(30)  # Salvar a cada 30 segundos
                
                with self.session_lock:
                    # Salvar sessões modificadas
                    modified = list(self.modified_sessions)
                    
                    for session_id in modified:
                        self.save_session(session_id)
                
                if modified:
                    print(f"Salvamento periódico concluído. Salvas {len(modified)} sessões.")
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
