#!/usr/bin/env python3
"""
Monitoring System - Continuity Protocol
Sistema de monitoramento em tempo real para o Continuity Protocol
"""

import os
import sys
import json
import time
import threading
import psutil
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Callable

# Adicionar diretório pai ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Importar componentes
try:
    from core.mcp.notification import notification_system
except ImportError:
    print("Erro ao importar componentes do Continuity Protocol")
    sys.exit(1)

class MonitoringSystem:
    """
    Sistema de monitoramento em tempo real para o Continuity Protocol
    """
    
    def __init__(self, monitoring_dir: str = None):
        """
        Inicializa o sistema de monitoramento
        
        Args:
            monitoring_dir: Diretório para armazenamento de dados de monitoramento
        """
        # Configurar diretório de monitoramento
        if monitoring_dir:
            self.monitoring_dir = monitoring_dir
        else:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            self.monitoring_dir = os.path.join(base_dir, "monitoring")
        
        # Criar diretório se não existir
        os.makedirs(self.monitoring_dir, exist_ok=True)
        
        # Arquivo de métricas
        self.metrics_file = os.path.join(self.monitoring_dir, "metrics.json")
        
        # Arquivo de alertas
        self.alerts_file = os.path.join(self.monitoring_dir, "alerts.json")
        
        # Arquivo de configuração
        self.config_file = os.path.join(self.monitoring_dir, "monitoring_config.json")
        
        # Carregar ou criar métricas
        self.metrics = self._load_or_create_metrics()
        
        # Carregar ou criar alertas
        self.alerts = self._load_or_create_alerts()
        
        # Carregar ou criar configuração
        self.config = self._load_or_create_config()
        
        # Thread de monitoramento
        self.monitoring_thread = None
        self.stop_monitoring = False
        
        # Callbacks para alertas
        self.alert_callbacks = {}
    
    def _load_or_create_metrics(self) -> Dict[str, Any]:
        """
        Carrega ou cria métricas
        
        Returns:
            Dict: Métricas
        """
        if os.path.exists(self.metrics_file):
            try:
                with open(self.metrics_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        # Criar métricas padrão
        metrics = {
            "system": {
                "cpu": [],
                "memory": [],
                "disk": []
            },
            "application": {
                "operations": [],
                "errors": [],
                "response_times": []
            },
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # Salvar métricas
        with open(self.metrics_file, 'w') as f:
            json.dump(metrics, f, indent=2)
        
        return metrics
    
    def _load_or_create_alerts(self) -> Dict[str, Any]:
        """
        Carrega ou cria alertas
        
        Returns:
            Dict: Alertas
        """
        if os.path.exists(self.alerts_file):
            try:
                with open(self.alerts_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        # Criar alertas padrão
        alerts = {
            "alerts": [],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # Salvar alertas
        with open(self.alerts_file, 'w') as f:
            json.dump(alerts, f, indent=2)
        
        return alerts
    
    def _load_or_create_config(self) -> Dict[str, Any]:
        """
        Carrega ou cria configuração
        
        Returns:
            Dict: Configuração
        """
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        # Criar configuração padrão
        config = {
            "monitoring_interval": 60,  # segundos
            "metrics_retention": 24,  # horas
            "alerts_retention": 72,  # horas
            "thresholds": {
                "cpu_high": 80,  # porcentagem
                "memory_high": 80,  # porcentagem
                "disk_high": 80,  # porcentagem
                "response_time_high": 1.0,  # segundos
                "error_rate_high": 5.0  # porcentagem
            },
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # Salvar configuração
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        return config
    
    def _save_metrics(self) -> None:
        """Salva métricas"""
        self.metrics["updated_at"] = datetime.now().isoformat()
        with open(self.metrics_file, 'w') as f:
            json.dump(self.metrics, f, indent=2)
    
    def _save_alerts(self) -> None:
        """Salva alertas"""
        self.alerts["updated_at"] = datetime.now().isoformat()
        with open(self.alerts_file, 'w') as f:
            json.dump(self.alerts, f, indent=2)
    
    def _save_config(self) -> None:
        """Salva configuração"""
        self.config["updated_at"] = datetime.now().isoformat()
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def _collect_system_metrics(self) -> Dict[str, Any]:
        """
        Coleta métricas do sistema
        
        Returns:
            Dict: Métricas do sistema
        """
        # Coletar métricas de CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Coletar métricas de memória
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        
        # Coletar métricas de disco
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent
        
        return {
            "timestamp": datetime.now().isoformat(),
            "cpu": cpu_percent,
            "memory": memory_percent,
            "disk": disk_percent
        }
    
    def _collect_application_metrics(self) -> Dict[str, Any]:
        """
        Coleta métricas da aplicação
        
        Returns:
            Dict: Métricas da aplicação
        """
        # Obter processos relacionados ao Continuity Protocol
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if 'python' in proc.info['name'].lower() and any('continuity-protocol' in cmd.lower() for cmd in proc.info['cmdline'] if cmd):
                    processes.append(proc)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        # Coletar métricas dos processos
        process_metrics = []
        for proc in processes:
            try:
                process_metrics.append({
                    "pid": proc.pid,
                    "cpu_percent": proc.cpu_percent(),
                    "memory_percent": proc.memory_percent(),
                    "status": proc.status()
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        return {
            "timestamp": datetime.now().isoformat(),
            "processes": process_metrics,
            "process_count": len(process_metrics)
        }
    
    def _check_thresholds(self, system_metrics: Dict[str, Any], app_metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Verifica se métricas ultrapassaram thresholds
        
        Args:
            system_metrics: Métricas do sistema
            app_metrics: Métricas da aplicação
            
        Returns:
            List[Dict]: Alertas gerados
        """
        alerts = []
        thresholds = self.config["thresholds"]
        
        # Verificar CPU
        if system_metrics["cpu"] > thresholds["cpu_high"]:
            alerts.append({
                "type": "cpu_high",
                "severity": "warning",
                "message": f"CPU usage is high: {system_metrics['cpu']}% (threshold: {thresholds['cpu_high']}%)",
                "value": system_metrics["cpu"],
                "threshold": thresholds["cpu_high"],
                "timestamp": datetime.now().isoformat()
            })
        
        # Verificar memória
        if system_metrics["memory"] > thresholds["memory_high"]:
            alerts.append({
                "type": "memory_high",
                "severity": "warning",
                "message": f"Memory usage is high: {system_metrics['memory']}% (threshold: {thresholds['memory_high']}%)",
                "value": system_metrics["memory"],
                "threshold": thresholds["memory_high"],
                "timestamp": datetime.now().isoformat()
            })
        
        # Verificar disco
        if system_metrics["disk"] > thresholds["disk_high"]:
            alerts.append({
                "type": "disk_high",
                "severity": "warning",
                "message": f"Disk usage is high: {system_metrics['disk']}% (threshold: {thresholds['disk_high']}%)",
                "value": system_metrics["disk"],
                "threshold": thresholds["disk_high"],
                "timestamp": datetime.now().isoformat()
            })
        
        # Verificar processos
        if app_metrics["process_count"] == 0:
            alerts.append({
                "type": "no_processes",
                "severity": "critical",
                "message": "No Continuity Protocol processes found",
                "value": 0,
                "threshold": 1,
                "timestamp": datetime.now().isoformat()
            })
        
        return alerts
    
    def _monitoring_loop(self) -> None:
        """Loop de monitoramento"""
        while not self.stop_monitoring:
            try:
                # Coletar métricas do sistema
                system_metrics = self._collect_system_metrics()
                
                # Coletar métricas da aplicação
                app_metrics = self._collect_application_metrics()
                
                # Adicionar métricas ao histórico
                self.metrics["system"]["cpu"].append({
                    "timestamp": system_metrics["timestamp"],
                    "value": system_metrics["cpu"]
                })
                
                self.metrics["system"]["memory"].append({
                    "timestamp": system_metrics["timestamp"],
                    "value": system_metrics["memory"]
                })
                
                self.metrics["system"]["disk"].append({
                    "timestamp": system_metrics["timestamp"],
                    "value": system_metrics["disk"]
                })
                
                self.metrics["application"]["operations"].append({
                    "timestamp": app_metrics["timestamp"],
                    "value": app_metrics["process_count"]
                })
                
                # Limitar tamanho do histórico
                retention_hours = self.config["metrics_retention"]
                retention_limit = datetime.now() - timedelta(hours=retention_hours)
                retention_limit_str = retention_limit.isoformat()
                
                for metric_type in ["cpu", "memory", "disk"]:
                    self.metrics["system"][metric_type] = [
                        m for m in self.metrics["system"][metric_type]
                        if m["timestamp"] > retention_limit_str
                    ]
                
                for metric_type in ["operations", "errors", "response_times"]:
                    self.metrics["application"][metric_type] = [
                        m for m in self.metrics["application"][metric_type]
                        if m["timestamp"] > retention_limit_str
                    ]
                
                # Verificar thresholds
                new_alerts = self._check_thresholds(system_metrics, app_metrics)
                
                # Adicionar novos alertas
                for alert in new_alerts:
                    self.alerts["alerts"].append(alert)
                    
                    # Executar callbacks para alertas
                    self._execute_alert_callbacks(alert)
                    
                    # Notificar sobre alerta
                    notification_system.create_notification(
                        f"Alerta: {alert['type']}",
                        alert["message"],
                        "warning" if alert["severity"] == "warning" else "error",
                        "monitoring",
                        {
                            "alert_type": alert["type"],
                            "severity": alert["severity"],
                            "value": alert["value"],
                            "threshold": alert["threshold"]
                        }
                    )
                
                # Limitar tamanho dos alertas
                alerts_retention_hours = self.config["alerts_retention"]
                alerts_retention_limit = datetime.now() - timedelta(hours=alerts_retention_hours)
                alerts_retention_limit_str = alerts_retention_limit.isoformat()
                
                self.alerts["alerts"] = [
                    a for a in self.alerts["alerts"]
                    if a["timestamp"] > alerts_retention_limit_str
                ]
                
                # Salvar métricas e alertas
                self._save_metrics()
                self._save_alerts()
                
                # Aguardar próxima coleta
                time.sleep(self.config["monitoring_interval"])
            except Exception as e:
                print(f"Erro no loop de monitoramento: {str(e)}")
                time.sleep(10)  # Aguardar um pouco antes de tentar novamente
    
    def start_monitoring(self) -> Dict[str, Any]:
        """
        Inicia monitoramento
        
        Returns:
            Dict: Resultado do início do monitoramento
        """
        if self.monitoring_thread is not None and self.monitoring_thread.is_alive():
            return {
                "success": False,
                "error": "Monitoramento já está em execução"
            }
        
        self.stop_monitoring = False
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
        
        # Notificar sobre início do monitoramento
        notification_system.create_notification(
            "Monitoramento iniciado",
            f"Sistema de monitoramento iniciado com intervalo de {self.config['monitoring_interval']} segundos",
            "info",
            "monitoring",
            {
                "interval": self.config["monitoring_interval"],
                "metrics_retention": self.config["metrics_retention"],
                "alerts_retention": self.config["alerts_retention"]
            }
        )
        
        return {
            "success": True,
            "monitoring_thread": self.monitoring_thread.ident,
            "interval": self.config["monitoring_interval"],
            "started_at": datetime.now().isoformat()
        }
    
    def stop_monitoring(self) -> Dict[str, Any]:
        """
        Para monitoramento
        
        Returns:
            Dict: Resultado da parada do monitoramento
        """
        if self.monitoring_thread is None or not self.monitoring_thread.is_alive():
            return {
                "success": False,
                "error": "Monitoramento não está em execução"
            }
        
        self.stop_monitoring = True
        self.monitoring_thread.join(timeout=10.0)
        
        # Notificar sobre parada do monitoramento
        notification_system.create_notification(
            "Monitoramento parado",
            "Sistema de monitoramento foi parado",
            "info",
            "monitoring",
            {}
        )
        
        return {
            "success": True,
            "stopped_at": datetime.now().isoformat()
        }
    
    def get_metrics(self, metric_type: str = None, limit: int = 100) -> Dict[str, Any]:
        """
        Obtém métricas
        
        Args:
            metric_type: Tipo de métrica (cpu, memory, disk, operations, errors, response_times)
            limit: Número máximo de métricas
            
        Returns:
            Dict: Métricas
        """
        if metric_type is None:
            # Retornar todas as métricas
            return {
                "success": True,
                "metrics": self.metrics,
                "updated_at": self.metrics["updated_at"]
            }
        
        # Verificar se tipo de métrica é válido
        if metric_type in ["cpu", "memory", "disk"]:
            category = "system"
        elif metric_type in ["operations", "errors", "response_times"]:
            category = "application"
        else:
            return {
                "success": False,
                "error": f"Tipo de métrica inválido: {metric_type}"
            }
        
        # Obter métricas do tipo especificado
        metrics = self.metrics[category][metric_type]
        
        # Limitar número de métricas
        if limit > 0:
            metrics = metrics[-limit:]
        
        return {
            "success": True,
            "metric_type": metric_type,
            "metrics": metrics,
            "count": len(metrics),
            "updated_at": self.metrics["updated_at"]
        }
    
    def get_alerts(self, severity: str = None, limit: int = 100) -> Dict[str, Any]:
        """
        Obtém alertas
        
        Args:
            severity: Severidade dos alertas (warning, critical)
            limit: Número máximo de alertas
            
        Returns:
            Dict: Alertas
        """
        # Filtrar alertas por severidade
        if severity is not None:
            alerts = [a for a in self.alerts["alerts"] if a["severity"] == severity]
        else:
            alerts = self.alerts["alerts"]
        
        # Ordenar alertas por timestamp (mais recentes primeiro)
        alerts = sorted(alerts, key=lambda a: a["timestamp"], reverse=True)
        
        # Limitar número de alertas
        if limit > 0:
            alerts = alerts[:limit]
        
        return {
            "success": True,
            "alerts": alerts,
            "count": len(alerts),
            "updated_at": self.alerts["updated_at"]
        }
    
    def update_config(self, monitoring_interval: int = None, metrics_retention: int = None,
                     alerts_retention: int = None, thresholds: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Atualiza configuração de monitoramento
        
        Args:
            monitoring_interval: Intervalo de monitoramento em segundos
            metrics_retention: Retenção de métricas em horas
            alerts_retention: Retenção de alertas em horas
            thresholds: Thresholds para alertas
            
        Returns:
            Dict: Configuração atualizada
        """
        # Atualizar intervalo de monitoramento
        if monitoring_interval is not None:
            if monitoring_interval < 10:
                return {
                    "success": False,
                    "error": "Intervalo de monitoramento deve ser pelo menos 10 segundos"
                }
            
            self.config["monitoring_interval"] = monitoring_interval
        
        # Atualizar retenção de métricas
        if metrics_retention is not None:
            if metrics_retention < 1:
                return {
                    "success": False,
                    "error": "Retenção de métricas deve ser pelo menos 1 hora"
                }
            
            self.config["metrics_retention"] = metrics_retention
        
        # Atualizar retenção de alertas
        if alerts_retention is not None:
            if alerts_retention < 1:
                return {
                    "success": False,
                    "error": "Retenção de alertas deve ser pelo menos 1 hora"
                }
            
            self.config["alerts_retention"] = alerts_retention
        
        # Atualizar thresholds
        if thresholds is not None:
            for key, value in thresholds.items():
                if key in self.config["thresholds"]:
                    self.config["thresholds"][key] = value
        
        # Salvar configuração
        self._save_config()
        
        # Notificar sobre atualização de configuração
        notification_system.create_notification(
            "Configuração de monitoramento atualizada",
            "Configuração do sistema de monitoramento foi atualizada",
            "info",
            "monitoring",
            {
                "monitoring_interval": self.config["monitoring_interval"],
                "metrics_retention": self.config["metrics_retention"],
                "alerts_retention": self.config["alerts_retention"]
            }
        )
        
        return {
            "success": True,
            "config": self.config
        }
    
    def register_alert_callback(self, alert_type: str, callback: Callable[[Dict[str, Any]], None]) -> bool:
        """
        Registra callback para alertas
        
        Args:
            alert_type: Tipo de alerta
            callback: Função a ser chamada quando um alerta for gerado
            
        Returns:
            bool: True se callback foi registrado, False caso contrário
        """
        # Inicializar lista de callbacks se não existir
        if alert_type not in self.alert_callbacks:
            self.alert_callbacks[alert_type] = []
        
        # Adicionar callback
        self.alert_callbacks[alert_type].append(callback)
        
        return True
    
    def _execute_alert_callbacks(self, alert: Dict[str, Any]) -> None:
        """
        Executa callbacks para um alerta
        
        Args:
            alert: Informações do alerta
        """
        alert_type = alert["type"]
        
        # Executar callbacks específicos para o tipo de alerta
        if alert_type in self.alert_callbacks:
            for callback in self.alert_callbacks[alert_type]:
                try:
                    callback(alert)
                except Exception as e:
                    print(f"Erro ao executar callback para alerta {alert_type}: {str(e)}")
        
        # Executar callbacks para todos os tipos de alerta
        if "all" in self.alert_callbacks:
            for callback in self.alert_callbacks["all"]:
                try:
                    callback(alert)
                except Exception as e:
                    print(f"Erro ao executar callback para alerta {alert_type}: {str(e)}")
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Obtém status do sistema
        
        Returns:
            Dict: Status do sistema
        """
        # Coletar métricas do sistema
        system_metrics = self._collect_system_metrics()
        
        # Coletar métricas da aplicação
        app_metrics = self._collect_application_metrics()
        
        # Verificar processos
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
            try:
                if 'python' in proc.info['name'].lower() and any('continuity-protocol' in cmd.lower() for cmd in proc.info['cmdline'] if cmd):
                    processes.append({
                        "pid": proc.pid,
                        "name": proc.info['name'],
                        "cmdline": ' '.join(proc.info['cmdline']),
                        "create_time": datetime.fromtimestamp(proc.info['create_time']).isoformat(),
                        "running_time": (datetime.now() - datetime.fromtimestamp(proc.info['create_time'])).total_seconds() / 60,  # minutos
                        "status": proc.status()
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        # Verificar alertas ativos
        active_alerts = [a for a in self.alerts["alerts"] if datetime.fromisoformat(a["timestamp"]) > datetime.now() - timedelta(hours=1)]
        
        return {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "system": {
                "cpu": system_metrics["cpu"],
                "memory": system_metrics["memory"],
                "disk": system_metrics["disk"]
            },
            "processes": processes,
            "process_count": len(processes),
            "active_alerts": active_alerts,
            "active_alerts_count": len(active_alerts),
            "monitoring_active": self.monitoring_thread is not None and self.monitoring_thread.is_alive(),
            "config": {
                "monitoring_interval": self.config["monitoring_interval"],
                "metrics_retention": self.config["metrics_retention"],
                "alerts_retention": self.config["alerts_retention"]
            }
        }

# Instância global para uso em todo o sistema
monitoring_system = MonitoringSystem()
