#!/usr/bin/env python3
"""
Unified Continuity Protocol Server

Servidor MCP unificado que combina todas as funcionalidades dos servidores anteriores
em uma única implementação coesa e robusta.
"""

import os
import sys
import json
import time
import subprocess
from datetime import datetime
from typing import Dict, List, Any, Optional, Union

# Base paths
CONTINUITY_BASE = "/Users/lucascardoso/apps/MCP/CONTINUITY"
CONTINUITY_PROTOCOL_BASE = "/Users/lucascardoso/continuity-protocol"
SCRIPTS_PATH = CONTINUITY_BASE
VERSION = "1.0.0"

# Configurar logs
import logging
LOG_DIR = os.path.join(CONTINUITY_BASE, "logs")
os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=os.path.join(LOG_DIR, "unified-server.log"),
    filemode="a"
)
logger = logging.getLogger("unified-continuity")

# Adicionar diretórios ao sys.path para permitir importações
sys.path.append(CONTINUITY_BASE)
sys.path.append(CONTINUITY_PROTOCOL_BASE)

# Importar FastMCP
try:
    from mcp.server.fastmcp import FastMCP
    logger.info("FastMCP importado com sucesso")
except ImportError:
    logger.warning("Instalando pacote MCP...")
    subprocess.run([sys.executable, "-m", "pip", "install", "mcp"])
    from mcp.server.fastmcp import FastMCP

# Verificar se módulos avançados estão disponíveis
ENHANCED_FEATURES = False
try:
    if os.path.exists(os.path.join(CONTINUITY_PROTOCOL_BASE, "core/mcp/integration_v2.py")):
        # Adicionar o diretório ao path
        sys.path.append(os.path.join(CONTINUITY_PROTOCOL_BASE, "core"))
        from core.mcp.integration_v2 import enhanced_context_protocol
        ENHANCED_FEATURES = True
        logger.info("Módulos avançados disponíveis")
except ImportError:
    logger.warning("Módulos avançados não disponíveis")
    ENHANCED_FEATURES = False

class UnifiedContinuityServer:
    """
    Servidor unificado que integra todas as funcionalidades dos servidores anteriores
    """
    
    def __init__(self, server_name="continuity-protocol"):
        """
        Inicializa o servidor unificado
        
        Args:
            server_name (str): Nome do servidor MCP
        """
        self.server_name = server_name
        logger.info(f"Inicializando servidor: {server_name}")
        
        # Inicializar FastMCP
        self.mcp = FastMCP(server_name)
        
        # Armazenar caminhos base
        self.continuity_base = CONTINUITY_BASE
        self.scripts_path = SCRIPTS_PATH
        
        # Verificar recursos avançados
        self.enhanced_features = ENHANCED_FEATURES
        
        # Salvar PID para gerenciamento
        self._save_pid()
        
        # Registrar ferramentas
        self._register_tools()
        
        logger.info("Servidor inicializado com sucesso")
        print(f"Unified Continuity Protocol Server v{VERSION}")
        print(f"- Base: {self.continuity_base}")
        print(f"- Recursos avançados: {'Disponíveis' if self.enhanced_features else 'Indisponíveis'}")
    
    def _save_pid(self):
        """Salva o PID do processo para gerenciamento"""
        pid_file = os.path.join(self.continuity_base, "unified-continuity-server.pid")
        with open(pid_file, "w") as f:
            f.write(str(os.getpid()))
        logger.info(f"PID salvo: {os.getpid()}")
    
    def _register_tools(self):
        """Registra todas as ferramentas do servidor"""
        # Registrar ferramentas básicas
        self._register_basic_tools()
        
        # Registrar ferramentas de script bash
        self._register_bash_tools()
    
    def _register_basic_tools(self):
        """Registra ferramentas básicas do servidor"""
        
        @self.mcp.tool()
        def continuity_status() -> str:
            """Verifica o status do servidor"""
            logger.info("Verificando status")
            return json.dumps({
                "status": "running",
                "version": VERSION,
                "timestamp": datetime.now().isoformat(),
                "enhanced_features": self.enhanced_features,
                "server_name": self.server_name
            }, indent=2)
        
        @self.mcp.tool()
        def continuity_test() -> str:
            """Testa o funcionamento do servidor"""
            logger.info("Teste de funcionamento executado")
            return "✅ Unified Continuity Protocol está funcionando corretamente!"
    
    def _register_bash_tools(self):
        """Registra ferramentas baseadas em scripts bash"""
        
        def run_bash_script(script_name: str, args: List[str] = None) -> Dict[str, Any]:
            """Executa um script bash e retorna o resultado estruturado"""
            try:
                script_path = f"{self.scripts_path}/{script_name}"
                
                if not os.path.exists(script_path):
                    logger.error(f"Script não encontrado: {script_path}")
                    return {
                        "error": f"Script not found: {script_path}",
                        "success": False
                    }
                
                cmd = [script_path]
                if args:
                    cmd.extend(args)
                
                logger.info(f"Executando script: {' '.join(cmd)}")
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                return {
                    "success": result.returncode == 0,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "returncode": result.returncode
                }
                
            except subprocess.TimeoutExpired:
                logger.error(f"Timeout ao executar script: {script_name}")
                return {
                    "error": "Script execution timeout",
                    "success": False
                }
            except Exception as e:
                logger.error(f"Erro ao executar script {script_name}: {str(e)}")
                return {
                    "error": f"Execution error: {str(e)}",
                    "success": False
                }
        
        @self.mcp.tool()
        def continuity_where_stopped() -> str:
            """Execute 'onde paramos?' - recuperação automática e carregamento de contexto"""
            logger.info("Executando recuperação automática")
            result = run_bash_script("autonomous-recovery.sh")
            
            if result.get("success"):
                response = f"✅ SUCCESS\n\n{result.get('stdout', '')}"
                if result.get('stderr'):
                    response += f"\n\n⚠️ WARNINGS:\n{result['stderr']}"
                return response
            else:
                response = f"❌ ERROR: {result.get('error', 'Unknown error')}"
                if result.get('stderr'):
                    response += f"\n\nSTDERR: {result['stderr']}"
                if result.get('stdout'):
                    response += f"\n\nSTDOUT: {result['stdout']}"
                return response
        
        @self.mcp.tool()
        def continuity_magic_system(user_input: str) -> str:
            """Processa a entrada do usuário através do sistema de detecção mágica"""
            logger.info("Executando sistema mágico")
            result = run_bash_script("magic-system.sh", [user_input])
            
            if result.get("success"):
                response = f"✅ SUCCESS\n\n{result.get('stdout', '')}"
                if result.get('stderr'):
                    response += f"\n\n⚠️ WARNINGS:\n{result['stderr']}"
                return response
            else:
                response = f"❌ ERROR: {result.get('error', 'Unknown error')}"
                if result.get('stderr'):
                    response += f"\n\nSTDERR: {result['stderr']}"
                if result.get('stdout'):
                    response += f"\n\nSTDOUT: {result['stdout']}"
                return response
        
        @self.mcp.tool()
        def continuity_emergency_freeze() -> str:
            """Cria backup de emergência do estado atual"""
            logger.info("Executando congelamento de emergência")
            result = run_bash_script("emergency-absolute.sh", ["freeze"])
            
            if result.get("success"):
                response = f"✅ SUCCESS\n\n{result.get('stdout', '')}"
                if result.get('stderr'):
                    response += f"\n\n⚠️ WARNINGS:\n{result['stderr']}"
                return response
            else:
                response = f"❌ ERROR: {result.get('error', 'Unknown error')}"
                if result.get('stderr'):
                    response += f"\n\nSTDERR: {result['stderr']}"
                if result.get('stdout'):
                    response += f"\n\nSTDOUT: {result['stdout']}"
                return response
        
        @self.mcp.tool()
        def continuity_emergency_unfreeze() -> str:
            """Restaura a partir de backup de emergência"""
            logger.info("Executando descongelamento de emergência")
            result = run_bash_script("emergency-absolute.sh", ["unfreeze"])
            
            if result.get("success"):
                response = f"✅ SUCCESS\n\n{result.get('stdout', '')}"
                if result.get('stderr'):
                    response += f"\n\n⚠️ WARNINGS:\n{result['stderr']}"
                return response
            else:
                response = f"❌ ERROR: {result.get('error', 'Unknown error')}"
                if result.get('stderr'):
                    response += f"\n\nSTDERR: {result['stderr']}"
                if result.get('stdout'):
                    response += f"\n\nSTDOUT: {result['stdout']}"
                return response
        
        @self.mcp.tool()
        def continuity_system_status() -> str:
            """Obtém status completo do sistema e visão geral do projeto"""
            logger.info("Verificando status do sistema")
            result = run_bash_script("emergency-absolute.sh", ["status"])
            
            if result.get("success"):
                response = f"✅ SUCCESS\n\n{result.get('stdout', '')}"
                if result.get('stderr'):
                    response += f"\n\n⚠️ WARNINGS:\n{result['stderr']}"
                return response
            else:
                response = f"❌ ERROR: {result.get('error', 'Unknown error')}"
                if result.get('stderr'):
                    response += f"\n\nSTDERR: {result['stderr']}"
                if result.get('stdout'):
                    response += f"\n\nSTDOUT: {result['stdout']}"
                return response
    
    def run(self) -> None:
        """Executa o servidor MCP"""
        try:
            logger.info("Iniciando servidor")
            print("Iniciando Unified Continuity Protocol Server...")
            self.mcp.run()
        except KeyboardInterrupt:
            logger.info("Servidor interrompido pelo usuário")
            print("\nServidor interrompido pelo usuário")
        except Exception as e:
            logger.error(f"Erro ao executar servidor: {str(e)}")
            print(f"ERRO: {str(e)}")

if __name__ == "__main__":
    # Criar e executar servidor
    server = UnifiedContinuityServer()
    server.run()