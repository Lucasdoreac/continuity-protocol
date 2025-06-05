#!/usr/bin/env python3
"""
API Server - Continuity Protocol
Servidor API REST para acesso remoto ao Continuity Protocol
"""

import os
import sys
import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Union

# Adicionar diretório pai ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Importar componentes
try:
    from core.mcp.integration_v2 import enhanced_context_protocol
    from core.mcp.notification import notification_system
    from core.mcp.versioning import versioning_system
    from core.mcp.backup import backup_system
    from core.mcp.search import search_system
    from core.mcp.safeguards import safeguards
    from core.mcp.auth import auth_system
    from core.mcp.monitoring_advanced import monitoring_system
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
                                        "logs", "api_server.log"))
    ]
)

logger = logging.getLogger("api_server")

class APIServer:
    """
    Servidor API REST para o Continuity Protocol
    """
    
    def __init__(self, host: str = "0.0.0.0", port: int = 8000):
        """
        Inicializa o servidor API
        
        Args:
            host: Host para o servidor
            port: Porta para o servidor
        """
        self.host = host
        self.port = port
        self.app = None
        self.server = None
        
        # Verificar dependências
        self.flask_available = self._check_flask()
        
        if not self.flask_available:
            logger.warning("Biblioteca Flask não encontrada. API REST não estará disponível.")
            notification_system.create_notification(
                "Dependência API não encontrada",
                "A biblioteca Flask não está instalada. API REST não estará disponível.",
                "warning",
                "api_server"
            )
    
    def _check_flask(self) -> bool:
        """
        Verifica se Flask está disponível
        
        Returns:
            bool: True se Flask está disponível, False caso contrário
        """
        try:
            import flask
            return True
        except ImportError:
            return False
    
    def start(self) -> Dict[str, Any]:
        """
        Inicia o servidor API
        
        Returns:
            Dict: Resultado da inicialização
        """
        if not self.flask_available:
            return {
                "success": False,
                "error": "Biblioteca Flask não encontrada"
            }
        
        try:
            from flask import Flask, request, jsonify
            from flask_cors import CORS
            
            # Criar aplicação Flask
            self.app = Flask("ContinuityProtocolAPI")
            CORS(self.app)  # Habilitar CORS
            
            # Definir rotas
            
            # Rota de status
            @self.app.route('/api/status', methods=['GET'])
            def status():
                return jsonify({
                    "status": "ok",
                    "timestamp": datetime.now().isoformat(),
                    "version": "1.0.0"
                })
            
            # Rotas de artefatos
            @self.app.route('/api/artifacts', methods=['GET'])
            def list_artifacts():
                # Autenticar
                auth_header = request.headers.get('Authorization')
                if not auth_header or not auth_header.startswith('Bearer '):
                    return jsonify({"error": "Unauthorized"}), 401
                
                token = auth_header.split(' ')[1]
                auth_result = auth_system.validate_token(token)
                
                if not auth_result["success"]:
                    return jsonify({"error": "Invalid token"}), 401
                
                # Obter parâmetros
                project_id = request.args.get('project_id')
                artifact_type = request.args.get('type')
                
                # Listar artefatos
                artifacts = enhanced_context_protocol.list_artifacts(project_id, artifact_type)
                
                # Registrar operação
                monitoring_system.record_operation(
                    "list_artifacts",
                    True,
                    time.time() - request.start_time if hasattr(request, 'start_time') else 0,
                    auth_result["user_id"]
                )
                
                return jsonify(artifacts)
            
            @self.app.route('/api/artifacts/<artifact_id>', methods=['GET'])
            def get_artifact(artifact_id):
                # Autenticar
                auth_header = request.headers.get('Authorization')
                if not auth_header or not auth_header.startswith('Bearer '):
                    return jsonify({"error": "Unauthorized"}), 401
                
                token = auth_header.split(' ')[1]
                auth_result = auth_system.validate_token(token)
                
                if not auth_result["success"]:
                    return jsonify({"error": "Invalid token"}), 401
                
                # Obter artefato
                artifact = enhanced_context_protocol.get_artifact(artifact_id)
                
                if not artifact:
                    return jsonify({"error": "Artifact not found"}), 404
                
                # Registrar operação
                monitoring_system.record_operation(
                    "get_artifact",
                    True,
                    time.time() - request.start_time if hasattr(request, 'start_time') else 0,
                    auth_result["user_id"]
                )
                
                return jsonify(artifact)
            
            @self.app.route('/api/artifacts', methods=['POST'])
            def create_artifact():
                # Autenticar
                auth_header = request.headers.get('Authorization')
                if not auth_header or not auth_header.startswith('Bearer '):
                    return jsonify({"error": "Unauthorized"}), 401
                
                token = auth_header.split(' ')[1]
                auth_result = auth_system.validate_token(token)
                
                if not auth_result["success"]:
                    return jsonify({"error": "Invalid token"}), 401
                
                # Obter dados
                data = request.json
                
                if not data or not isinstance(data, dict):
                    return jsonify({"error": "Invalid request body"}), 400
                
                # Validar campos obrigatórios
                required_fields = ["content", "artifact_type", "project_id"]
                for field in required_fields:
                    if field not in data:
                        return jsonify({"error": f"Missing required field: {field}"}), 400
                
                # Criar artefato
                artifact = enhanced_context_protocol.store_artifact(
                    data["content"],
                    data["artifact_type"],
                    data["project_id"],
                    auth_result["user_id"],
                    data.get("metadata")
                )
                
                # Registrar operação
                monitoring_system.record_operation(
                    "create_artifact",
                    True,
                    time.time() - request.start_time if hasattr(request, 'start_time') else 0,
                    auth_result["user_id"]
                )
                
                # Registrar artefato
                monitoring_system.record_artifact(
                    data["artifact_type"],
                    len(data["content"].encode('utf-8'))
                )
                
                return jsonify(artifact)
            
            @self.app.route('/api/artifacts/<artifact_id>', methods=['PUT'])
            def update_artifact(artifact_id):
                # Autenticar
                auth_header = request.headers.get('Authorization')
                if not auth_header or not auth_header.startswith('Bearer '):
                    return jsonify({"error": "Unauthorized"}), 401
                
                token = auth_header.split(' ')[1]
                auth_result = auth_system.validate_token(token)
                
                if not auth_result["success"]:
                    return jsonify({"error": "Invalid token"}), 401
                
                # Obter dados
                data = request.json
                
                if not data or not isinstance(data, dict):
                    return jsonify({"error": "Invalid request body"}), 400
                
                # Validar campos obrigatórios
                if "content" not in data:
                    return jsonify({"error": "Missing required field: content"}), 400
                
                # Atualizar artefato
                result = enhanced_context_protocol.update_artifact(
                    artifact_id,
                    data["content"],
                    auth_result["user_id"],
                    data.get("metadata"),
                    data.get("change_level"),
                    data.get("changes")
                )
                
                if not result["success"]:
                    return jsonify({"error": result.get("error", "Failed to update artifact")}), 400
                
                # Registrar operação
                monitoring_system.record_operation(
                    "update_artifact",
                    True,
                    time.time() - request.start_time if hasattr(request, 'start_time') else 0,
                    auth_result["user_id"]
                )
                
                # Registrar versão
                monitoring_system.record_version()
                
                return jsonify(result)
            
            # Rotas de versões
            @self.app.route('/api/artifacts/<artifact_id>/versions', methods=['GET'])
            def get_artifact_versions(artifact_id):
                # Autenticar
                auth_header = request.headers.get('Authorization')
                if not auth_header or not auth_header.startswith('Bearer '):
                    return jsonify({"error": "Unauthorized"}), 401
                
                token = auth_header.split(' ')[1]
                auth_result = auth_system.validate_token(token)
                
                if not auth_result["success"]:
                    return jsonify({"error": "Invalid token"}), 401
                
                # Obter histórico de versões
                history = enhanced_context_protocol.get_artifact_history(artifact_id)
                
                if not history["success"]:
                    return jsonify({"error": history.get("error", "Failed to get version history")}), 400
                
                # Registrar operação
                monitoring_system.record_operation(
                    "get_artifact_versions",
                    True,
                    time.time() - request.start_time if hasattr(request, 'start_time') else 0,
                    auth_result["user_id"]
                )
                
                return jsonify(history)
            
            @self.app.route('/api/artifacts/<artifact_id>/versions/<version>', methods=['GET'])
            def get_artifact_version(artifact_id, version):
                # Autenticar
                auth_header = request.headers.get('Authorization')
                if not auth_header or not auth_header.startswith('Bearer '):
                    return jsonify({"error": "Unauthorized"}), 401
                
                token = auth_header.split(' ')[1]
                auth_result = auth_system.validate_token(token)
                
                if not auth_result["success"]:
                    return jsonify({"error": "Invalid token"}), 401
                
                # Obter versão específica
                version_result = enhanced_context_protocol.get_artifact_version(artifact_id, version)
                
                if not version_result["success"]:
                    return jsonify({"error": version_result.get("error", "Failed to get version")}), 400
                
                # Registrar operação
                monitoring_system.record_operation(
                    "get_artifact_version",
                    True,
                    time.time() - request.start_time if hasattr(request, 'start_time') else 0,
                    auth_result["user_id"]
                )
                
                return jsonify(version_result)
            
            @self.app.route('/api/artifacts/<artifact_id>/revert/<version>', methods=['POST'])
            def revert_artifact(artifact_id, version):
                # Autenticar
                auth_header = request.headers.get('Authorization')
                if not auth_header or not auth_header.startswith('Bearer '):
                    return jsonify({"error": "Unauthorized"}), 401
                
                token = auth_header.split(' ')[1]
                auth_result = auth_system.validate_token(token)
                
                if not auth_result["success"]:
                    return jsonify({"error": "Invalid token"}), 401
                
                # Reverter para versão específica
                revert_result = enhanced_context_protocol.revert_artifact(artifact_id, version)
                
                if not revert_result["success"]:
                    return jsonify({"error": revert_result.get("error", "Failed to revert artifact")}), 400
                
                # Registrar operação
                monitoring_system.record_operation(
                    "revert_artifact",
                    True,
                    time.time() - request.start_time if hasattr(request, 'start_time') else 0,
                    auth_result["user_id"]
                )
                
                # Registrar versão
                monitoring_system.record_version()
                
                return jsonify(revert_result)
            
            # Rotas de busca
            @self.app.route('/api/search', methods=['GET'])
            def search_artifacts():
                # Autenticar
                auth_header = request.headers.get('Authorization')
                if not auth_header or not auth_header.startswith('Bearer '):
                    return jsonify({"error": "Unauthorized"}), 401
                
                token = auth_header.split(' ')[1]
                auth_result = auth_system.validate_token(token)
                
                if not auth_result["success"]:
                    return jsonify({"error": "Invalid token"}), 401
                
                # Obter parâmetros
                query = request.args.get('query')
                artifact_type = request.args.get('type')
                created_by = request.args.get('created_by')
                limit = request.args.get('limit', 10, type=int)
                
                if not query:
                    return jsonify({"error": "Missing required parameter: query"}), 400
                
                # Buscar artefatos
                search_result = enhanced_context_protocol.search_artifacts(
                    query,
                    artifact_type,
                    created_by,
                    limit
                )
                
                # Registrar operação
                monitoring_system.record_operation(
                    "search_artifacts",
                    True,
                    time.time() - request.start_time if hasattr(request, 'start_time') else 0,
                    auth_result["user_id"]
                )
                
                return jsonify(search_result)
            
            # Rotas de backup
            @self.app.route('/api/backup', methods=['POST'])
            def create_backup():
                # Autenticar
                auth_header = request.headers.get('Authorization')
                if not auth_header or not auth_header.startswith('Bearer '):
                    return jsonify({"error": "Unauthorized"}), 401
                
                token = auth_header.split(' ')[1]
                auth_result = auth_system.validate_token(token)
                
                if not auth_result["success"]:
                    return jsonify({"error": "Invalid token"}), 401
                
                # Verificar permissões de administrador
                if not auth_result.get("is_admin", False):
                    return jsonify({"error": "Admin privileges required"}), 403
                
                # Obter dados
                data = request.json or {}
                
                # Criar backup
                backup_result = enhanced_context_protocol.create_backup(
                    data.get("backup_type", "full"),
                    data.get("description")
                )
                
                # Registrar operação
                monitoring_system.record_operation(
                    "create_backup",
                    backup_result["success"],
                    time.time() - request.start_time if hasattr(request, 'start_time') else 0,
                    auth_result["user_id"]
                )
                
                return jsonify(backup_result)
            
            # Rotas de monitoramento
            @self.app.route('/api/monitoring/metrics', methods=['GET'])
            def get_metrics():
                # Autenticar
                auth_header = request.headers.get('Authorization')
                if not auth_header or not auth_header.startswith('Bearer '):
                    return jsonify({"error": "Unauthorized"}), 401
                
                token = auth_header.split(' ')[1]
                auth_result = auth_system.validate_token(token)
                
                if not auth_result["success"]:
                    return jsonify({"error": "Invalid token"}), 401
                
                # Verificar permissões de administrador
                if not auth_result.get("is_admin", False):
                    return jsonify({"error": "Admin privileges required"}), 403
                
                # Obter métricas
                metrics = monitoring_system.get_metrics()
                
                return jsonify(metrics)
            
            @self.app.route('/api/monitoring/health', methods=['GET'])
            def get_health():
                # Autenticar
                auth_header = request.headers.get('Authorization')
                if not auth_header or not auth_header.startswith('Bearer '):
                    return jsonify({"error": "Unauthorized"}), 401
                
                token = auth_header.split(' ')[1]
                auth_result = auth_system.validate_token(token)
                
                if not auth_result["success"]:
                    return jsonify({"error": "Invalid token"}), 401
                
                # Obter status de saúde
                health = monitoring_system.get_system_health()
                
                # Determinar código de status HTTP
                status_code = 200
                if health["status"] == "warning":
                    status_code = 429  # Too Many Requests
                elif health["status"] == "unhealthy":
                    status_code = 503  # Service Unavailable
                
                return jsonify(health), status_code
            
            # Middleware para registrar tempo de início
            @self.app.before_request
            def before_request():
                request.start_time = time.time()
            
            # Iniciar servidor
            self.server = self.app.run(
                host=self.host,
                port=self.port,
                debug=False,
                use_reloader=False,
                threaded=True
            )
            
            logger.info(f"Servidor API iniciado em http://{self.host}:{self.port}")
            
            return {
                "success": True,
                "host": self.host,
                "port": self.port,
                "url": f"http://{self.host}:{self.port}"
            }
        except Exception as e:
            logger.error(f"Erro ao iniciar servidor API: {str(e)}")
            
            return {
                "success": False,
                "error": f"Erro ao iniciar servidor API: {str(e)}"
            }
    
    def stop(self) -> Dict[str, Any]:
        """
        Para o servidor API
        
        Returns:
            Dict: Resultado da parada
        """
        if not self.app or not self.server:
            return {
                "success": False,
                "error": "Servidor API não está em execução"
            }
        
        try:
            # Parar servidor
            func = request.environ.get('werkzeug.server.shutdown')
            if func is None:
                raise RuntimeError('Não foi possível parar o servidor')
            func()
            
            logger.info("Servidor API parado")
            
            return {
                "success": True
            }
        except Exception as e:
            logger.error(f"Erro ao parar servidor API: {str(e)}")
            
            return {
                "success": False,
                "error": f"Erro ao parar servidor API: {str(e)}"
            }

# Instância global para uso em todo o sistema
api_server = APIServer()
