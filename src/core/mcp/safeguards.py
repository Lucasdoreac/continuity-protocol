#!/usr/bin/env python3
"""
MCP Safeguards - Continuity Protocol
Implementação de safeguards contra operações extensas para evitar interrupções
"""

import os
import time
import json
import threading
import signal
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable, Union

class MCPSafeguards:
    """
    Implementa safeguards contra operações extensas para o Continuity Protocol
    """
    
    def __init__(self, 
                 max_lines_per_operation: int = 500,
                 max_session_time_minutes: int = 25,
                 checkpoint_interval_minutes: int = 5,
                 backup_dir: str = None):
        """
        Inicializa os safeguards
        
        Args:
            max_lines_per_operation: Número máximo de linhas por operação
            max_session_time_minutes: Tempo máximo de sessão em minutos
            checkpoint_interval_minutes: Intervalo entre checkpoints em minutos
            backup_dir: Diretório para backups automáticos
        """
        self.max_lines_per_operation = max_lines_per_operation
        self.max_session_time_minutes = max_session_time_minutes
        self.checkpoint_interval_minutes = checkpoint_interval_minutes
        
        # Configurar diretório de backup
        if backup_dir:
            self.backup_dir = backup_dir
        else:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            self.backup_dir = os.path.join(base_dir, "backups", "safeguards")
        
        # Criar diretório de backup se não existir
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # Estado interno
        self.session_start_time = datetime.now()
        self.last_checkpoint_time = datetime.now()
        self.operation_count = 0
        self.checkpoint_count = 0
        self.warnings_issued = []
        
        # Iniciar timer para checkpoint automático
        self._start_checkpoint_timer()
        
        # Registrar handler para sinais de término
        signal.signal(signal.SIGINT, self._handle_termination)
        signal.signal(signal.SIGTERM, self._handle_termination)
        
        print(f"[SAFEGUARD] Initialized with: max_lines={max_lines_per_operation}, "
              f"max_session_time={max_session_time_minutes}min, "
              f"checkpoint_interval={checkpoint_interval_minutes}min")
    
    def _start_checkpoint_timer(self) -> None:
        """Inicia timer para checkpoint automático"""
        self.checkpoint_timer = threading.Timer(
            self.checkpoint_interval_minutes * 60, 
            self._auto_checkpoint
        )
        self.checkpoint_timer.daemon = True
        self.checkpoint_timer.start()
    
    def _auto_checkpoint(self) -> None:
        """Executa checkpoint automático"""
        self.create_checkpoint("auto")
        self._start_checkpoint_timer()  # Reiniciar timer
    
    def _handle_termination(self, signum, frame) -> None:
        """Handler para sinais de término"""
        self.create_checkpoint("termination")
        # Continuar com o comportamento padrão após o checkpoint
        signal.default_int_handler(signum, frame)
    
    def check_content_size(self, content: str) -> Dict[str, Any]:
        """
        Verifica se o conteúdo excede o limite de linhas
        
        Args:
            content: Conteúdo a ser verificado
            
        Returns:
            Dict: Resultado da verificação
        """
        lines = content.splitlines()
        line_count = len(lines)
        
        result = {
            "passed": line_count <= self.max_lines_per_operation,
            "line_count": line_count,
            "max_lines": self.max_lines_per_operation,
            "timestamp": datetime.now().isoformat()
        }
        
        if not result["passed"]:
            result["warning"] = (f"Content exceeds maximum line count: {line_count} > "
                                f"{self.max_lines_per_operation}")
            self.warnings_issued.append({
                "type": "content_size",
                "timestamp": datetime.now().isoformat(),
                "details": result
            })
        
        return result
    
    def check_session_time(self) -> Dict[str, Any]:
        """
        Verifica se a sessão excedeu o tempo máximo
        
        Returns:
            Dict: Resultado da verificação
        """
        current_time = datetime.now()
        elapsed_minutes = (current_time - self.session_start_time).total_seconds() / 60
        
        result = {
            "passed": elapsed_minutes <= self.max_session_time_minutes,
            "elapsed_minutes": elapsed_minutes,
            "max_minutes": self.max_session_time_minutes,
            "session_start": self.session_start_time.isoformat(),
            "current_time": current_time.isoformat()
        }
        
        if not result["passed"]:
            result["warning"] = (f"Session time exceeded: {elapsed_minutes:.1f}min > "
                                f"{self.max_session_time_minutes}min")
            self.warnings_issued.append({
                "type": "session_time",
                "timestamp": current_time.isoformat(),
                "details": result
            })
        
        return result
    
    def create_checkpoint(self, checkpoint_type: str = "manual") -> Dict[str, Any]:
        """
        Cria um checkpoint do estado atual
        
        Args:
            checkpoint_type: Tipo de checkpoint ("manual", "auto", "termination")
            
        Returns:
            Dict: Informações do checkpoint
        """
        current_time = datetime.now()
        elapsed_minutes = (current_time - self.session_start_time).total_seconds() / 60
        minutes_since_last = (current_time - self.last_checkpoint_time).total_seconds() / 60
        
        checkpoint_id = f"checkpoint_{int(time.time())}_{checkpoint_type}"
        checkpoint_file = os.path.join(self.backup_dir, f"{checkpoint_id}.json")
        
        checkpoint_data = {
            "id": checkpoint_id,
            "type": checkpoint_type,
            "timestamp": current_time.isoformat(),
            "session_stats": {
                "start_time": self.session_start_time.isoformat(),
                "elapsed_minutes": elapsed_minutes,
                "operation_count": self.operation_count,
                "checkpoint_count": self.checkpoint_count,
                "minutes_since_last_checkpoint": minutes_since_last
            },
            "warnings": self.warnings_issued
        }
        
        # Salvar checkpoint
        try:
            with open(checkpoint_file, 'w') as f:
                json.dump(checkpoint_data, f, indent=2)
            
            self.last_checkpoint_time = current_time
            self.checkpoint_count += 1
            
            checkpoint_data["success"] = True
            checkpoint_data["file"] = checkpoint_file
        except Exception as e:
            checkpoint_data["success"] = False
            checkpoint_data["error"] = str(e)
        
        return checkpoint_data
    
    def chunk_content(self, content: str) -> List[str]:
        """
        Divide conteúdo em chunks menores que o limite de linhas
        
        Args:
            content: Conteúdo a ser dividido
            
        Returns:
            List[str]: Lista de chunks
        """
        lines = content.splitlines()
        chunks = []
        
        for i in range(0, len(lines), self.max_lines_per_operation):
            chunk = lines[i:i + self.max_lines_per_operation]
            chunks.append('\n'.join(chunk))
        
        return chunks
    
    def wrap_operation(self, operation_func: Callable, *args, **kwargs) -> Any:
        """
        Wrapper para operações que aplica safeguards
        
        Args:
            operation_func: Função a ser executada
            *args, **kwargs: Argumentos para a função
            
        Returns:
            Resultado da função
        """
        # Verificar tempo de sessão
        session_check = self.check_session_time()
        if not session_check["passed"]:
            print(f"[SAFEGUARD WARNING] {session_check['warning']}")
            print("[SAFEGUARD] Creating checkpoint before continuing...")
            self.create_checkpoint("time_exceeded")
        
        # Executar operação
        self.operation_count += 1
        start_time = time.time()
        
        try:
            result = operation_func(*args, **kwargs)
            
            # Registrar operação bem-sucedida
            elapsed = time.time() - start_time
            print(f"[SAFEGUARD] Operation completed in {elapsed:.2f}s")
            
            return result
        except Exception as e:
            # Criar checkpoint em caso de erro
            print(f"[SAFEGUARD ERROR] Operation failed: {str(e)}")
            self.create_checkpoint("error")
            raise
    
    def get_status(self) -> Dict[str, Any]:
        """
        Obtém status atual dos safeguards
        
        Returns:
            Dict: Status atual
        """
        current_time = datetime.now()
        elapsed_minutes = (current_time - self.session_start_time).total_seconds() / 60
        minutes_since_last = (current_time - self.last_checkpoint_time).total_seconds() / 60
        
        return {
            "session_start": self.session_start_time.isoformat(),
            "elapsed_minutes": elapsed_minutes,
            "max_session_minutes": self.max_session_time_minutes,
            "last_checkpoint": self.last_checkpoint_time.isoformat(),
            "minutes_since_last_checkpoint": minutes_since_last,
            "checkpoint_interval_minutes": self.checkpoint_interval_minutes,
            "operation_count": self.operation_count,
            "checkpoint_count": self.checkpoint_count,
            "warnings_count": len(self.warnings_issued),
            "max_lines_per_operation": self.max_lines_per_operation,
            "backup_dir": self.backup_dir
        }

# Instância global para uso em todo o sistema
safeguards = MCPSafeguards()

def apply_safeguards(func):
    """
    Decorator para aplicar safeguards a uma função
    
    Args:
        func: Função a ser decorada
        
    Returns:
        Função decorada
    """
    def wrapper(*args, **kwargs):
        return safeguards.wrap_operation(func, *args, **kwargs)
    
    return wrapper
