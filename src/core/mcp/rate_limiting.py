#!/usr/bin/env python3
"""
Rate Limiting - Continuity Protocol
Implementação de rate limiting para APIs do sistema
"""

import time
import threading
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable, Union

class RateLimiter:
    """
    Implementa rate limiting para APIs do Continuity Protocol
    """
    
    def __init__(self):
        """Inicializa o rate limiter"""
        self.limits = {}  # Configurações de limite por operação
        self.counters = {}  # Contadores de uso por operação
        self.lock = threading.RLock()  # Lock para thread safety
    
    def set_limit(self, operation: str, max_calls: int, window_seconds: int) -> None:
        """
        Define limite de taxa para uma operação
        
        Args:
            operation: Nome da operação
            max_calls: Número máximo de chamadas permitidas
            window_seconds: Janela de tempo em segundos
        """
        with self.lock:
            self.limits[operation] = {
                "max_calls": max_calls,
                "window_seconds": window_seconds
            }
            
            # Inicializar contador se não existir
            if operation not in self.counters:
                self.counters[operation] = []
    
    def check_limit(self, operation: str) -> Dict[str, Any]:
        """
        Verifica se uma operação excedeu o limite
        
        Args:
            operation: Nome da operação
            
        Returns:
            Dict: Resultado da verificação
        """
        with self.lock:
            # Se operação não tem limite definido, permitir
            if operation not in self.limits:
                return {
                    "allowed": True,
                    "operation": operation,
                    "limit_defined": False
                }
            
            limit = self.limits[operation]
            counter = self.counters[operation]
            current_time = time.time()
            
            # Remover timestamps antigos fora da janela
            window_start = current_time - limit["window_seconds"]
            counter = [ts for ts in counter if ts >= window_start]
            self.counters[operation] = counter
            
            # Verificar se excedeu o limite
            calls_in_window = len(counter)
            allowed = calls_in_window < limit["max_calls"]
            
            result = {
                "allowed": allowed,
                "operation": operation,
                "limit_defined": True,
                "current_count": calls_in_window,
                "max_calls": limit["max_calls"],
                "window_seconds": limit["window_seconds"],
                "remaining": max(0, limit["max_calls"] - calls_in_window)
            }
            
            # Se permitido, adicionar timestamp atual
            if allowed:
                self.counters[operation].append(current_time)
            else:
                # Calcular tempo de espera
                next_available = counter[0] + limit["window_seconds"]
                wait_seconds = next_available - current_time
                result["retry_after_seconds"] = max(0, wait_seconds)
            
            return result
    
    def record_call(self, operation: str) -> None:
        """
        Registra uma chamada para uma operação
        
        Args:
            operation: Nome da operação
        """
        with self.lock:
            # Se operação não tem contador, inicializar
            if operation not in self.counters:
                self.counters[operation] = []
            
            # Adicionar timestamp atual
            self.counters[operation].append(time.time())
    
    def get_status(self, operation: str = None) -> Dict[str, Any]:
        """
        Obtém status atual do rate limiter
        
        Args:
            operation: Nome da operação (opcional)
            
        Returns:
            Dict: Status atual
        """
        with self.lock:
            if operation:
                # Status para operação específica
                if operation not in self.limits:
                    return {
                        "operation": operation,
                        "limit_defined": False
                    }
                
                limit = self.limits[operation]
                counter = self.counters.get(operation, [])
                current_time = time.time()
                
                # Remover timestamps antigos fora da janela
                window_start = current_time - limit["window_seconds"]
                counter = [ts for ts in counter if ts >= window_start]
                
                return {
                    "operation": operation,
                    "limit_defined": True,
                    "current_count": len(counter),
                    "max_calls": limit["max_calls"],
                    "window_seconds": limit["window_seconds"],
                    "remaining": max(0, limit["max_calls"] - len(counter))
                }
            else:
                # Status para todas as operações
                status = {}
                current_time = time.time()
                
                for op in self.limits:
                    limit = self.limits[op]
                    counter = self.counters.get(op, [])
                    
                    # Remover timestamps antigos fora da janela
                    window_start = current_time - limit["window_seconds"]
                    counter = [ts for ts in counter if ts >= window_start]
                    
                    status[op] = {
                        "current_count": len(counter),
                        "max_calls": limit["max_calls"],
                        "window_seconds": limit["window_seconds"],
                        "remaining": max(0, limit["max_calls"] - len(counter))
                    }
                
                return status

# Instância global para uso em todo o sistema
rate_limiter = RateLimiter()

# Configurar limites padrão
rate_limiter.set_limit("context_store_artifact", 100, 3600)  # 100 artefatos por hora
rate_limiter.set_limit("context_get_project_context", 200, 3600)  # 200 consultas por hora
rate_limiter.set_limit("context_get_artifact", 300, 3600)  # 300 consultas por hora
rate_limiter.set_limit("context_get_project_artifacts", 200, 3600)  # 200 consultas por hora
rate_limiter.set_limit("context_get_latest_artifact", 200, 3600)  # 200 consultas por hora
rate_limiter.set_limit("context_sync_artifact_to_file", 50, 3600)  # 50 sincronizações por hora
rate_limiter.set_limit("context_sync_file_to_artifact", 50, 3600)  # 50 sincronizações por hora
rate_limiter.set_limit("context_create_artifact_from_file", 50, 3600)  # 50 criações por hora

def rate_limit(operation: str = None, max_calls: int = None, window_seconds: int = None):
    """
    Decorator para aplicar rate limiting a uma função
    
    Args:
        operation: Nome da operação (opcional, usa nome da função se não fornecido)
        max_calls: Número máximo de chamadas permitidas (opcional)
        window_seconds: Janela de tempo em segundos (opcional)
        
    Returns:
        Decorator para função
    """
    def decorator(func):
        # Determinar nome da operação
        op_name = operation or func.__name__
        
        # Configurar limite se fornecido
        if max_calls is not None and window_seconds is not None:
            rate_limiter.set_limit(op_name, max_calls, window_seconds)
        
        def wrapper(*args, **kwargs):
            # Verificar limite
            check_result = rate_limiter.check_limit(op_name)
            
            if not check_result["allowed"]:
                # Excedeu o limite
                if "retry_after_seconds" in check_result:
                    error_msg = (f"Rate limit exceeded for {op_name}. "
                                f"Try again in {check_result['retry_after_seconds']:.1f} seconds.")
                else:
                    error_msg = f"Rate limit exceeded for {op_name}."
                
                raise Exception(error_msg)
            
            # Executar função
            return func(*args, **kwargs)
        
        return wrapper
    
    return decorator
