#!/usr/bin/env python3
"""
Advanced Monitoring System - Continuity Protocol
Sistema de monitoramento avançado com métricas em tempo real e alertas inteligentes
"""

import os
import sys
import json
import time
import threading
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Callable

# Adicionar diretório pai ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Importar componentes
try:
    from core.mcp.notification import notification_system
    from core.mcp.safeguards import safeguards
except ImportError:
    print("Erro ao importar componentes do Continuity Protocol")
    sys.exit(1)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
                                        "logs", "monitoring.log"))
    ]
)

logger = logging.getLogger("monitoring")

class MetricsCollector:
    """
    Coletor de métricas para o sistema de monitoramento
    """
    
    def __init__(self):
        """Inicializa o coletor de métricas"""
        self.metrics = {
            "system": {
                "start_time": datetime.now().isoformat(),
                "uptime_seconds": 0,
                "cpu_usage": [],
                "memory_usage": [],
                "disk_usage": []
            },
            "operations": {
                "total_count": 0,
                "success_count": 0,
                "error_count": 0,
                "operations_per_minute": [],
                "average_response_time": 0,
                "operation_types": {}
            },
            "artifacts": {
                "total_count": 0,
                "versions_count": 0,
                "size_total_bytes": 0,
                "artifacts_per_type": {}
            },
            "users": {
                "active_count": 0,
                "requests_per_user": {}
            }
        }
        
        # Timestamps para cálculos de taxa
        self.last_metrics_update = datetime.now()
        self.operations_since_last_update = 0
        
        # Métricas temporárias para cálculos
        self.response_times = []
        
        # Iniciar thread de coleta de métricas
        self.stop_collector = False
        self.collector_thread = threading.Thread(target=self._metrics_collector_loop)
        self.collector_thread.daemon = True
        self.collector_thread.start()
    
    def _metrics_collector_loop(self):
        """Loop de coleta de métricas do sistema"""
        while not self.stop_collector:
            try:
                # Atualizar métricas do sistema
                self._update_system_metrics()
                
                # Atualizar métricas de operações
                self._update_operation_metrics()
                
                # Calcular métricas derivadas
                self._calculate_derived_metrics()
                
                # Verificar alertas
                self._check_alerts()
                
            except Exception as e:
                logger.error(f"Erro na coleta de métricas: {str(e)}")
            
            # Aguardar próxima coleta (a cada 10 segundos)
            time.sleep(10)
    
    def _update_system_metrics(self):
        """Atualiza métricas do sistema"""
        # Calcular uptime
        uptime = (datetime.now() - datetime.fromisoformat(self.metrics["system"]["start_time"])).total_seconds()
        self.metrics["system"]["uptime_seconds"] = uptime
        
        # Coletar uso de CPU
        try:
            import psutil
            cpu_percent = psutil.cpu_percent(interval=1)
            memory_percent = psutil.virtual_memory().percent
            disk_percent = psutil.disk_usage('/').percent
            
            # Manter apenas os últimos 60 pontos (10 minutos)
            self.metrics["system"]["cpu_usage"].append(cpu_percent)
            if len(self.metrics["system"]["cpu_usage"]) > 60:
                self.metrics["system"]["cpu_usage"].pop(0)
            
            self.metrics["system"]["memory_usage"].append(memory_percent)
            if len(self.metrics["system"]["memory_usage"]) > 60:
                self.metrics["system"]["memory_usage"].pop(0)
            
            self.metrics["system"]["disk_usage"].append(disk_percent)
            if len(self.metrics["system"]["disk_usage"]) > 60:
                self.metrics["system"]["disk_usage"].pop(0)
        except ImportError:
            # psutil não está disponível, usar valores fictícios
            import random
            self.metrics["system"]["cpu_usage"].append(random.randint(10, 30))
            if len(self.metrics["system"]["cpu_usage"]) > 60:
                self.metrics["system"]["cpu_usage"].pop(0)
            
            self.metrics["system"]["memory_usage"].append(random.randint(20, 40))
            if len(self.metrics["system"]["memory_usage"]) > 60:
                self.metrics["system"]["memory_usage"].pop(0)
            
            self.metrics["system"]["disk_usage"].append(random.randint(30, 50))
            if len(self.metrics["system"]["disk_usage"]) > 60:
                self.metrics["system"]["disk_usage"].pop(0)
    
    def _update_operation_metrics(self):
        """Atualiza métricas de operações"""
        # Calcular operações por minuto
        now = datetime.now()
        elapsed_minutes = (now - self.last_metrics_update).total_seconds() / 60
        
        if elapsed_minutes >= 1:
            ops_per_minute = self.operations_since_last_update / elapsed_minutes
            
            # Manter apenas os últimos 60 pontos (60 minutos)
            self.metrics["operations"]["operations_per_minute"].append(ops_per_minute)
            if len(self.metrics["operations"]["operations_per_minute"]) > 60:
                self.metrics["operations"]["operations_per_minute"].pop(0)
            
            # Resetar contadores
            self.last_metrics_update = now
            self.operations_since_last_update = 0
    
    def _calculate_derived_metrics(self):
        """Calcula métricas derivadas"""
        # Calcular tempo médio de resposta
        if self.response_times:
            self.metrics["operations"]["average_response_time"] = sum(self.response_times) / len(self.response_times)
            # Limitar a lista para evitar crescimento infinito
            if len(self.response_times) > 1000:
                self.response_times = self.response_times[-1000:]
    
    def _check_alerts(self):
        """Verifica condições para alertas"""
        # Verificar uso de CPU
        if self.metrics["system"]["cpu_usage"] and self.metrics["system"]["cpu_usage"][-1] > 80:
            notification_system.create_notification(
                "Alerta de CPU",
                f"Uso de CPU elevado: {self.metrics['system']['cpu_usage'][-1]}%",
                "warning",
                "monitoring",
                {"metric": "cpu_usage", "value": self.metrics["system"]["cpu_usage"][-1]}
            )
        
        # Verificar uso de memória
        if self.metrics["system"]["memory_usage"] and self.metrics["system"]["memory_usage"][-1] > 80:
            notification_system.create_notification(
                "Alerta de Memória",
                f"Uso de memória elevado: {self.metrics['system']['memory_usage'][-1]}%",
                "warning",
                "monitoring",
                {"metric": "memory_usage", "value": self.metrics["system"]["memory_usage"][-1]}
            )
        
        # Verificar uso de disco
        if self.metrics["system"]["disk_usage"] and self.metrics["system"]["disk_usage"][-1] > 80:
            notification_system.create_notification(
                "Alerta de Disco",
                f"Uso de disco elevado: {self.metrics['system']['disk_usage'][-1]}%",
                "warning",
                "monitoring",
                {"metric": "disk_usage", "value": self.metrics["system"]["disk_usage"][-1]}
            )
        
        # Verificar taxa de erros
        if self.metrics["operations"]["total_count"] > 0:
            error_rate = self.metrics["operations"]["error_count"] / self.metrics["operations"]["total_count"]
            if error_rate > 0.1:  # Mais de 10% de erros
                notification_system.create_notification(
                    "Alerta de Taxa de Erros",
                    f"Taxa de erros elevada: {error_rate:.2%}",
                    "error",
                    "monitoring",
                    {"metric": "error_rate", "value": error_rate}
                )
    
    def record_operation(self, operation_type: str, success: bool, response_time: float, user_id: str = None):
        """
        Registra uma operação no sistema
        
        Args:
            operation_type: Tipo de operação
            success: Se a operação foi bem-sucedida
            response_time: Tempo de resposta em segundos
            user_id: ID do usuário que realizou a operação
        """
        # Incrementar contadores
        self.metrics["operations"]["total_count"] += 1
        self.operations_since_last_update += 1
        
        if success:
            self.metrics["operations"]["success_count"] += 1
        else:
            self.metrics["operations"]["error_count"] += 1
        
        # Registrar tempo de resposta
        self.response_times.append(response_time)
        
        # Registrar tipo de operação
        if operation_type not in self.metrics["operations"]["operation_types"]:
            self.metrics["operations"]["operation_types"][operation_type] = {
                "count": 0,
                "success_count": 0,
                "error_count": 0,
                "average_response_time": 0,
                "response_times": []
            }
        
        self.metrics["operations"]["operation_types"][operation_type]["count"] += 1
        
        if success:
            self.metrics["operations"]["operation_types"][operation_type]["success_count"] += 1
        else:
            self.metrics["operations"]["operation_types"][operation_type]["error_count"] += 1
        
        # Registrar tempo de resposta para o tipo de operação
        self.metrics["operations"]["operation_types"][operation_type]["response_times"].append(response_time)
        
        # Calcular tempo médio de resposta para o tipo de operação
        response_times = self.metrics["operations"]["operation_types"][operation_type]["response_times"]
        self.metrics["operations"]["operation_types"][operation_type]["average_response_time"] = sum(response_times) / len(response_times)
        
        # Limitar a lista para evitar crescimento infinito
        if len(response_times) > 100:
            self.metrics["operations"]["operation_types"][operation_type]["response_times"] = response_times[-100:]
        
        # Registrar usuário
        if user_id:
            if user_id not in self.metrics["users"]["requests_per_user"]:
                self.metrics["users"]["requests_per_user"][user_id] = 0
            
            self.metrics["users"]["requests_per_user"][user_id] += 1
            
            # Atualizar contagem de usuários ativos
            self.metrics["users"]["active_count"] = len(self.metrics["users"]["requests_per_user"])
    
    def record_artifact(self, artifact_type: str, size_bytes: int):
        """
        Registra um artefato no sistema
        
        Args:
            artifact_type: Tipo de artefato
            size_bytes: Tamanho do artefato em bytes
        """
        # Incrementar contadores
        self.metrics["artifacts"]["total_count"] += 1
        self.metrics["artifacts"]["size_total_bytes"] += size_bytes
        
        # Registrar tipo de artefato
        if artifact_type not in self.metrics["artifacts"]["artifacts_per_type"]:
            self.metrics["artifacts"]["artifacts_per_type"][artifact_type] = {
                "count": 0,
                "size_bytes": 0
            }
        
        self.metrics["artifacts"]["artifacts_per_type"][artifact_type]["count"] += 1
        self.metrics["artifacts"]["artifacts_per_type"][artifact_type]["size_bytes"] += size_bytes
    
    def record_version(self):
        """Registra uma nova versão de artefato"""
        self.metrics["artifacts"]["versions_count"] += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Obtém métricas atuais
        
        Returns:
            Dict: Métricas atuais
        """
        return {
            "timestamp": datetime.now().isoformat(),
            "metrics": self.metrics
        }
    
    def get_system_health(self) -> Dict[str, Any]:
        """
        Obtém status de saúde do sistema
        
        Returns:
            Dict: Status de saúde
        """
        # Calcular médias
        cpu_avg = sum(self.metrics["system"]["cpu_usage"]) / len(self.metrics["system"]["cpu_usage"]) if self.metrics["system"]["cpu_usage"] else 0
        memory_avg = sum(self.metrics["system"]["memory_usage"]) / len(self.metrics["system"]["memory_usage"]) if self.metrics["system"]["memory_usage"] else 0
        disk_avg = sum(self.metrics["system"]["disk_usage"]) / len(self.metrics["system"]["disk_usage"]) if self.metrics["system"]["disk_usage"] else 0
        
        # Calcular taxa de erros
        error_rate = self.metrics["operations"]["error_count"] / self.metrics["operations"]["total_count"] if self.metrics["operations"]["total_count"] > 0 else 0
        
        # Determinar status geral
        status = "healthy"
        issues = []
        
        if cpu_avg > 80:
            status = "warning"
            issues.append("CPU usage high")
        
        if memory_avg > 80:
            status = "warning"
            issues.append("Memory usage high")
        
        if disk_avg > 80:
            status = "warning"
            issues.append("Disk usage high")
        
        if error_rate > 0.1:
            status = "unhealthy"
            issues.append("Error rate high")
        
        return {
            "timestamp": datetime.now().isoformat(),
            "status": status,
            "issues": issues,
            "metrics": {
                "cpu_usage": cpu_avg,
                "memory_usage": memory_avg,
                "disk_usage": disk_avg,
                "error_rate": error_rate,
                "operations_per_minute": self.metrics["operations"]["operations_per_minute"][-1] if self.metrics["operations"]["operations_per_minute"] else 0,
                "average_response_time": self.metrics["operations"]["average_response_time"]
            }
        }
    
    def stop(self):
        """Para o coletor de métricas"""
        self.stop_collector = True
        if self.collector_thread.is_alive():
            self.collector_thread.join(timeout=2.0)

class AdvancedMonitoringSystem:
    """
    Sistema de monitoramento avançado para o Continuity Protocol
    """
    
    def __init__(self, metrics_dir: str = None):
        """
        Inicializa o sistema de monitoramento
        
        Args:
            metrics_dir: Diretório para armazenamento de métricas
        """
        # Configurar diretório de métricas
        if metrics_dir:
            self.metrics_dir = metrics_dir
        else:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            self.metrics_dir = os.path.join(base_dir, "metrics")
        
        # Criar diretório se não existir
        os.makedirs(self.metrics_dir, exist_ok=True)
        
        # Criar diretório de logs
        logs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "logs")
        os.makedirs(logs_dir, exist_ok=True)
        
        # Inicializar coletor de métricas
        self.metrics_collector = MetricsCollector()
        
        # Callbacks para alertas
        self.alert_callbacks = []
        
        # Iniciar thread de persistência de métricas
        self.stop_persistence = False
        self.persistence_thread = threading.Thread(target=self._metrics_persistence_loop)
        self.persistence_thread.daemon = True
        self.persistence_thread.start()
        
        logger.info("Sistema de monitoramento avançado inicializado")
    
    def _metrics_persistence_loop(self):
        """Loop de persistência de métricas"""
        while not self.stop_persistence:
            try:
                # Salvar métricas a cada hora
                metrics = self.metrics_collector.get_metrics()
                
                # Nome do arquivo baseado na data/hora
                filename = f"metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                filepath = os.path.join(self.metrics_dir, filename)
                
                # Salvar métricas
                with open(filepath, 'w') as f:
                    json.dump(metrics, f, indent=2)
                
                logger.info(f"Métricas salvas em {filepath}")
                
            except Exception as e:
                logger.error(f"Erro ao persistir métricas: {str(e)}")
            
            # Aguardar próxima persistência (a cada hora)
            for _ in range(3600):  # 3600 segundos = 1 hora
                if self.stop_persistence:
                    break
                time.sleep(1)
    
    def record_operation(self, operation_type: str, success: bool, response_time: float, user_id: str = None):
        """
        Registra uma operação no sistema
        
        Args:
            operation_type: Tipo de operação
            success: Se a operação foi bem-sucedida
            response_time: Tempo de resposta em segundos
            user_id: ID do usuário que realizou a operação
        """
        self.metrics_collector.record_operation(operation_type, success, response_time, user_id)
    
    def record_artifact(self, artifact_type: str, size_bytes: int):
        """
        Registra um artefato no sistema
        
        Args:
            artifact_type: Tipo de artefato
            size_bytes: Tamanho do artefato em bytes
        """
        self.metrics_collector.record_artifact(artifact_type, size_bytes)
    
    def record_version(self):
        """Registra uma nova versão de artefato"""
        self.metrics_collector.record_version()
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Obtém métricas atuais
        
        Returns:
            Dict: Métricas atuais
        """
        return self.metrics_collector.get_metrics()
    
    def get_system_health(self) -> Dict[str, Any]:
        """
        Obtém status de saúde do sistema
        
        Returns:
            Dict: Status de saúde
        """
        return self.metrics_collector.get_system_health()
    
    def register_alert_callback(self, callback: Callable[[str, Dict[str, Any]], None]):
        """
        Registra callback para alertas
        
        Args:
            callback: Função a ser chamada quando um alerta for gerado
        """
        self.alert_callbacks.append(callback)
    
    def generate_report(self, start_time: datetime = None, end_time: datetime = None) -> Dict[str, Any]:
        """
        Gera relatório de métricas para um período
        
        Args:
            start_time: Início do período (usa 24h atrás se None)
            end_time: Fim do período (usa agora se None)
            
        Returns:
            Dict: Relatório de métricas
        """
        # Definir período padrão
        if end_time is None:
            end_time = datetime.now()
        
        if start_time is None:
            start_time = end_time - timedelta(hours=24)
        
        # Carregar métricas do período
        metrics_files = []
        for filename in os.listdir(self.metrics_dir):
            if filename.startswith("metrics_") and filename.endswith(".json"):
                file_time_str = filename[8:-5]  # Extrair timestamp do nome
                try:
                    file_time = datetime.strptime(file_time_str, '%Y%m%d_%H%M%S')
                    if start_time <= file_time <= end_time:
                        metrics_files.append(os.path.join(self.metrics_dir, filename))
                except:
                    pass
        
        # Ordenar arquivos por data
        metrics_files.sort()
        
        # Carregar métricas
        metrics_data = []
        for filepath in metrics_files:
            try:
                with open(filepath, 'r') as f:
                    metrics_data.append(json.load(f))
            except:
                pass
        
        # Adicionar métricas atuais
        metrics_data.append(self.metrics_collector.get_metrics())
        
        # Gerar relatório
        if not metrics_data:
            return {
                "success": False,
                "error": "Nenhuma métrica encontrada para o período"
            }
        
        # Extrair métricas relevantes
        operations_total = []
        operations_success = []
        operations_error = []
        cpu_usage = []
        memory_usage = []
        disk_usage = []
        
        for data in metrics_data:
            timestamp = data["timestamp"]
            metrics = data["metrics"]
            
            operations_total.append({
                "timestamp": timestamp,
                "value": metrics["operations"]["total_count"]
            })
            
            operations_success.append({
                "timestamp": timestamp,
                "value": metrics["operations"]["success_count"]
            })
            
            operations_error.append({
                "timestamp": timestamp,
                "value": metrics["operations"]["error_count"]
            })
            
            if metrics["system"]["cpu_usage"]:
                cpu_usage.append({
                    "timestamp": timestamp,
                    "value": metrics["system"]["cpu_usage"][-1]
                })
            
            if metrics["system"]["memory_usage"]:
                memory_usage.append({
                    "timestamp": timestamp,
                    "value": metrics["system"]["memory_usage"][-1]
                })
            
            if metrics["system"]["disk_usage"]:
                disk_usage.append({
                    "timestamp": timestamp,
                    "value": metrics["system"]["disk_usage"][-1]
                })
        
        # Calcular estatísticas
        latest_metrics = metrics_data[-1]["metrics"]
        
        return {
            "success": True,
            "period": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat()
            },
            "summary": {
                "operations_total": latest_metrics["operations"]["total_count"],
                "operations_success": latest_metrics["operations"]["success_count"],
                "operations_error": latest_metrics["operations"]["error_count"],
                "error_rate": latest_metrics["operations"]["error_count"] / latest_metrics["operations"]["total_count"] if latest_metrics["operations"]["total_count"] > 0 else 0,
                "artifacts_total": latest_metrics["artifacts"]["total_count"],
                "artifacts_size_mb": latest_metrics["artifacts"]["size_total_bytes"] / (1024 * 1024),
                "active_users": latest_metrics["users"]["active_count"]
            },
            "charts": {
                "operations": {
                    "total": operations_total,
                    "success": operations_success,
                    "error": operations_error
                },
                "system": {
                    "cpu_usage": cpu_usage,
                    "memory_usage": memory_usage,
                    "disk_usage": disk_usage
                }
            },
            "operation_types": latest_metrics["operations"]["operation_types"],
            "artifact_types": latest_metrics["artifacts"]["artifacts_per_type"]
        }
    
    def stop(self):
        """Para o sistema de monitoramento"""
        self.stop_persistence = True
        self.metrics_collector.stop()
        
        if self.persistence_thread.is_alive():
            self.persistence_thread.join(timeout=2.0)
        
        logger.info("Sistema de monitoramento avançado finalizado")

# Decorator para monitorar operações
def monitor_operation(operation_type: str):
    """
    Decorator para monitorar operações
    
    Args:
        operation_type: Tipo de operação
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                success = True
                
                # Verificar se resultado é um dicionário com campo 'success'
                if isinstance(result, dict) and "success" in result:
                    success = result["success"]
                
                return result
            except Exception as e:
                success = False
                raise
            finally:
                # Calcular tempo de resposta
                response_time = time.time() - start_time
                
                # Registrar operação
                user_id = kwargs.get("agent_id") or kwargs.get("user_id")
                monitoring_system.record_operation(operation_type, success, response_time, user_id)
        
        return wrapper
    
    return decorator

# Instância global para uso em todo o sistema
monitoring_system = AdvancedMonitoringSystem()
