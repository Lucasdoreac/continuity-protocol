#!/usr/bin/env python3
"""
Notification System - Continuity Protocol
Sistema de notificações em tempo real para colaboradores
"""

import os
import json
import time
import threading
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional, Union, Callable

class NotificationSystem:
    """
    Sistema de notificações para o Continuity Protocol
    """
    
    def __init__(self, notifications_dir: str = None):
        """
        Inicializa o sistema de notificações
        
        Args:
            notifications_dir: Diretório para armazenamento de notificações
        """
        # Configurar diretório de notificações
        if notifications_dir:
            self.notifications_dir = notifications_dir
        else:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            self.notifications_dir = os.path.join(base_dir, "shared_context", "notifications")
        
        # Criar diretório se não existir
        os.makedirs(self.notifications_dir, exist_ok=True)
        
        # Arquivo de registro de notificações
        self.registry_file = os.path.join(self.notifications_dir, "notifications_registry.json")
        
        # Carregar ou criar registro de notificações
        self.notifications_registry = self._load_or_create_registry()
        
        # Callbacks para notificações
        self.callbacks = {}
        
        # Configurações de integração
        self.integrations = {
            "slack": {
                "enabled": False,
                "webhook_url": None
            },
            "email": {
                "enabled": False,
                "smtp_server": None,
                "smtp_port": None,
                "username": None,
                "password": None,
                "from_email": None
            }
        }
        
        # Iniciar thread de processamento de notificações
        self.processing_thread = None
        self.stop_processing = False
    
    def _load_or_create_registry(self) -> Dict[str, Any]:
        """
        Carrega ou cria registro de notificações
        
        Returns:
            Dict: Registro de notificações
        """
        if os.path.exists(self.registry_file):
            try:
                with open(self.registry_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        # Criar registro vazio
        registry = {
            "notifications": [],
            "unread_count": 0,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # Salvar registro
        with open(self.registry_file, 'w') as f:
            json.dump(registry, f, indent=2)
        
        return registry
    
    def _save_registry(self) -> None:
        """Salva registro de notificações"""
        self.notifications_registry["updated_at"] = datetime.now().isoformat()
        with open(self.registry_file, 'w') as f:
            json.dump(self.notifications_registry, f, indent=2)
    
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
        # Gerar ID da notificação
        notification_id = f"notification_{int(time.time())}_{notification_type}"
        
        # Criar informações da notificação
        notification_info = {
            "id": notification_id,
            "title": title,
            "message": message,
            "type": notification_type,
            "source": source,
            "created_at": datetime.now().isoformat(),
            "read": False,
            "metadata": metadata or {}
        }
        
        # Adicionar notificação ao registro
        self.notifications_registry["notifications"].append(notification_info)
        self.notifications_registry["unread_count"] += 1
        self._save_registry()
        
        # Salvar notificação em arquivo separado
        notification_file = os.path.join(self.notifications_dir, f"{notification_id}.json")
        with open(notification_file, 'w') as f:
            json.dump(notification_info, f, indent=2)
        
        # Processar notificação
        self._process_notification(notification_info)
        
        return {
            "success": True,
            "notification_info": notification_info
        }
    
    def _process_notification(self, notification_info: Dict[str, Any]) -> None:
        """
        Processa uma notificação
        
        Args:
            notification_info: Informações da notificação
        """
        # Executar callbacks registrados
        notification_type = notification_info["type"]
        
        if notification_type in self.callbacks:
            for callback in self.callbacks[notification_type]:
                try:
                    callback(notification_info)
                except Exception as e:
                    print(f"Erro ao executar callback para notificação {notification_info['id']}: {str(e)}")
        
        # Executar callbacks para todos os tipos
        if "all" in self.callbacks:
            for callback in self.callbacks["all"]:
                try:
                    callback(notification_info)
                except Exception as e:
                    print(f"Erro ao executar callback para notificação {notification_info['id']}: {str(e)}")
        
        # Enviar notificação para integrações externas
        self._send_to_integrations(notification_info)
    
    def _send_to_integrations(self, notification_info: Dict[str, Any]) -> None:
        """
        Envia notificação para integrações externas
        
        Args:
            notification_info: Informações da notificação
        """
        # Enviar para Slack
        if self.integrations["slack"]["enabled"] and self.integrations["slack"]["webhook_url"]:
            try:
                self._send_to_slack(notification_info)
            except Exception as e:
                print(f"Erro ao enviar notificação para Slack: {str(e)}")
        
        # Enviar por email
        if self.integrations["email"]["enabled"] and self.integrations["email"]["smtp_server"]:
            try:
                self._send_by_email(notification_info)
            except Exception as e:
                print(f"Erro ao enviar notificação por email: {str(e)}")
    
    def _send_to_slack(self, notification_info: Dict[str, Any]) -> None:
        """
        Envia notificação para Slack
        
        Args:
            notification_info: Informações da notificação
        """
        webhook_url = self.integrations["slack"]["webhook_url"]
        
        # Determinar cor com base no tipo
        color = {
            "info": "#3498db",
            "warning": "#f39c12",
            "error": "#e74c3c",
            "success": "#2ecc71"
        }.get(notification_info["type"], "#3498db")
        
        # Criar payload
        payload = {
            "attachments": [
                {
                    "fallback": notification_info["title"],
                    "color": color,
                    "title": notification_info["title"],
                    "text": notification_info["message"],
                    "fields": [
                        {
                            "title": "Tipo",
                            "value": notification_info["type"],
                            "short": True
                        },
                        {
                            "title": "Fonte",
                            "value": notification_info["source"],
                            "short": True
                        }
                    ],
                    "footer": "Continuity Protocol",
                    "ts": int(time.time())
                }
            ]
        }
        
        # Adicionar campos de metadados
        if notification_info["metadata"]:
            for key, value in notification_info["metadata"].items():
                if isinstance(value, (str, int, float, bool)):
                    payload["attachments"][0]["fields"].append({
                        "title": key,
                        "value": str(value),
                        "short": True
                    })
        
        # Enviar para Slack
        requests.post(webhook_url, json=payload)
    
    def _send_by_email(self, notification_info: Dict[str, Any]) -> None:
        """
        Envia notificação por email
        
        Args:
            notification_info: Informações da notificação
        """
        # Esta é uma implementação simplificada
        # Para uma implementação completa, seria necessário usar smtplib
        print(f"Enviando notificação por email: {notification_info['title']}")
    
    def mark_as_read(self, notification_id: str) -> Dict[str, Any]:
        """
        Marca notificação como lida
        
        Args:
            notification_id: ID da notificação
            
        Returns:
            Dict: Resultado da operação
        """
        # Procurar notificação
        for notification in self.notifications_registry["notifications"]:
            if notification["id"] == notification_id and not notification["read"]:
                notification["read"] = True
                self.notifications_registry["unread_count"] -= 1
                self._save_registry()
                
                # Atualizar arquivo da notificação
                notification_file = os.path.join(self.notifications_dir, f"{notification_id}.json")
                if os.path.exists(notification_file):
                    with open(notification_file, 'w') as f:
                        json.dump(notification, f, indent=2)
                
                return {
                    "success": True,
                    "notification_info": notification
                }
        
        return {
            "success": False,
            "error": f"Notificação {notification_id} não encontrada ou já está marcada como lida"
        }
    
    def mark_all_as_read(self) -> Dict[str, Any]:
        """
        Marca todas as notificações como lidas
        
        Returns:
            Dict: Resultado da operação
        """
        count = 0
        
        for notification in self.notifications_registry["notifications"]:
            if not notification["read"]:
                notification["read"] = True
                count += 1
                
                # Atualizar arquivo da notificação
                notification_file = os.path.join(self.notifications_dir, f"{notification['id']}.json")
                if os.path.exists(notification_file):
                    with open(notification_file, 'w') as f:
                        json.dump(notification, f, indent=2)
        
        if count > 0:
            self.notifications_registry["unread_count"] = 0
            self._save_registry()
        
        return {
            "success": True,
            "count": count
        }
    
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
        notifications = self.notifications_registry["notifications"]
        
        # Filtrar notificações não lidas se necessário
        if unread_only:
            notifications = [n for n in notifications if not n["read"]]
        
        # Ordenar por data de criação (mais recentes primeiro)
        notifications.sort(key=lambda x: x["created_at"], reverse=True)
        
        # Aplicar paginação
        paginated = notifications[offset:offset + limit]
        
        return {
            "success": True,
            "notifications": paginated,
            "total": len(notifications),
            "unread_count": self.notifications_registry["unread_count"],
            "limit": limit,
            "offset": offset
        }
    
    def get_notification(self, notification_id: str) -> Dict[str, Any]:
        """
        Obtém uma notificação específica
        
        Args:
            notification_id: ID da notificação
            
        Returns:
            Dict: Informações da notificação
        """
        # Verificar se existe arquivo específico
        notification_file = os.path.join(self.notifications_dir, f"{notification_id}.json")
        if os.path.exists(notification_file):
            try:
                with open(notification_file, 'r') as f:
                    notification_info = json.load(f)
                
                return {
                    "success": True,
                    "notification_info": notification_info
                }
            except:
                pass
        
        # Procurar no registro
        for notification in self.notifications_registry["notifications"]:
            if notification["id"] == notification_id:
                return {
                    "success": True,
                    "notification_info": notification
                }
        
        return {
            "success": False,
            "error": f"Notificação {notification_id} não encontrada"
        }
    
    def delete_notification(self, notification_id: str) -> Dict[str, Any]:
        """
        Remove uma notificação
        
        Args:
            notification_id: ID da notificação
            
        Returns:
            Dict: Resultado da operação
        """
        # Procurar notificação
        for i, notification in enumerate(self.notifications_registry["notifications"]):
            if notification["id"] == notification_id:
                # Remover do registro
                removed = self.notifications_registry["notifications"].pop(i)
                
                # Atualizar contador de não lidas
                if not removed["read"]:
                    self.notifications_registry["unread_count"] -= 1
                
                self._save_registry()
                
                # Remover arquivo da notificação
                notification_file = os.path.join(self.notifications_dir, f"{notification_id}.json")
                if os.path.exists(notification_file):
                    os.remove(notification_file)
                
                return {
                    "success": True,
                    "notification_info": removed
                }
        
        return {
            "success": False,
            "error": f"Notificação {notification_id} não encontrada"
        }
    
    def register_callback(self, callback: Callable[[Dict[str, Any]], None], 
                         notification_type: str = "all") -> None:
        """
        Registra callback para notificações
        
        Args:
            callback: Função a ser chamada quando uma notificação for criada
            notification_type: Tipo de notificação para o callback
        """
        if notification_type not in self.callbacks:
            self.callbacks[notification_type] = []
        
        self.callbacks[notification_type].append(callback)
    
    def configure_slack_integration(self, webhook_url: str, enabled: bool = True) -> Dict[str, Any]:
        """
        Configura integração com Slack
        
        Args:
            webhook_url: URL do webhook do Slack
            enabled: Se True, habilita a integração
            
        Returns:
            Dict: Resultado da configuração
        """
        self.integrations["slack"]["webhook_url"] = webhook_url
        self.integrations["slack"]["enabled"] = enabled
        
        return {
            "success": True,
            "integration": "slack",
            "enabled": enabled
        }
    
    def configure_email_integration(self, smtp_server: str, smtp_port: int, 
                                  username: str, password: str, 
                                  from_email: str, enabled: bool = True) -> Dict[str, Any]:
        """
        Configura integração com email
        
        Args:
            smtp_server: Servidor SMTP
            smtp_port: Porta do servidor SMTP
            username: Nome de usuário
            password: Senha
            from_email: Email de origem
            enabled: Se True, habilita a integração
            
        Returns:
            Dict: Resultado da configuração
        """
        self.integrations["email"]["smtp_server"] = smtp_server
        self.integrations["email"]["smtp_port"] = smtp_port
        self.integrations["email"]["username"] = username
        self.integrations["email"]["password"] = password
        self.integrations["email"]["from_email"] = from_email
        self.integrations["email"]["enabled"] = enabled
        
        return {
            "success": True,
            "integration": "email",
            "enabled": enabled
        }
    
    def start_processing_thread(self) -> None:
        """Inicia thread de processamento de notificações"""
        if self.processing_thread is not None and self.processing_thread.is_alive():
            return
        
        self.stop_processing = False
        self.processing_thread = threading.Thread(target=self._notification_processing_loop)
        self.processing_thread.daemon = True
        self.processing_thread.start()
    
    def stop_processing_thread(self) -> None:
        """Para thread de processamento de notificações"""
        self.stop_processing = True
        if self.processing_thread is not None:
            self.processing_thread.join(timeout=2.0)
    
    def _notification_processing_loop(self) -> None:
        """Loop de processamento de notificações"""
        while not self.stop_processing:
            # Verificar se há novas notificações
            # Este é um placeholder para uma implementação real
            # que poderia verificar uma fila de notificações
            time.sleep(1.0)

# Instância global para uso em todo o sistema
notification_system = NotificationSystem()
