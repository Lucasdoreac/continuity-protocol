#!/bin/bash
# reorganize-continuity.sh
# Script para reorganizar e unificar o Continuity Protocol

set -euo pipefail

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Caminhos principais
HOME_DIR="/Users/lucascardoso"
CONTINUITY_DIR="${HOME_DIR}/apps/MCP/CONTINUITY"
CONTINUITY_PROTOCOL_DIR="${HOME_DIR}/continuity-protocol"
BACKUP_DIR="${CONTINUITY_DIR}/backups/reorganization_$(date +%Y%m%d_%H%M%S)"

# Função para logging
log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Função para criar diretórios
create_directories() {
    log "Criando estrutura de diretórios..."

    # Criar diretórios principais
    mkdir -p "${CONTINUITY_DIR}/src/core"
    mkdir -p "${CONTINUITY_DIR}/src/servers"
    mkdir -p "${CONTINUITY_DIR}/src/adapters"
    mkdir -p "${CONTINUITY_DIR}/src/utilities"
    mkdir -p "${CONTINUITY_DIR}/tools/dark-mode"
    mkdir -p "${CONTINUITY_DIR}/tools/accessibility"
    mkdir -p "${CONTINUITY_DIR}/config/system-prompts"
    mkdir -p "${CONTINUITY_DIR}/bin"
    mkdir -p "${CONTINUITY_DIR}/scripts"
    mkdir -p "${CONTINUITY_DIR}/docs/integration"
    mkdir -p "${CONTINUITY_DIR}/docs/user-guides"
    mkdir -p "${CONTINUITY_DIR}/docs/technical"
    mkdir -p "${BACKUP_DIR}"

    log_success "Estrutura de diretórios criada"
}

# Função para fazer backup dos arquivos atuais
backup_current_files() {
    log "Criando backup dos arquivos atuais..."

    # Backup do CONTINUITY_DIR
    cp -r "${CONTINUITY_DIR}"/* "${BACKUP_DIR}/continuity/" 2>/dev/null || true
    
    # Backup do CONTINUITY_PROTOCOL_DIR
    if [ -d "${CONTINUITY_PROTOCOL_DIR}" ]; then
        mkdir -p "${BACKUP_DIR}/continuity-protocol"
        cp -r "${CONTINUITY_PROTOCOL_DIR}"/* "${BACKUP_DIR}/continuity-protocol/" 2>/dev/null || true
    fi
    
    log_success "Backup criado em ${BACKUP_DIR}"
}

# Função para mover os arquivos do core
move_core_files() {
    log "Movendo arquivos core..."

    # Mover arquivos de continuidade
    cp "${CONTINUITY_DIR}/continuity-manager.sh" "${CONTINUITY_DIR}/src/core/" 2>/dev/null || true
    cp "${CONTINUITY_DIR}/autonomous-recovery.sh" "${CONTINUITY_DIR}/src/core/" 2>/dev/null || true
    cp "${CONTINUITY_DIR}/recovery.sh" "${CONTINUITY_DIR}/src/core/" 2>/dev/null || true
    cp "${CONTINUITY_DIR}/session-init.sh" "${CONTINUITY_DIR}/src/core/" 2>/dev/null || true
    
    # Mover arquivos core do continuity-protocol
    if [ -d "${CONTINUITY_PROTOCOL_DIR}/core" ]; then
        cp -r "${CONTINUITY_PROTOCOL_DIR}/core"/* "${CONTINUITY_DIR}/src/core/" 2>/dev/null || true
    fi
    
    log_success "Arquivos core movidos"
}

# Função para mover os arquivos de servidores
move_server_files() {
    log "Movendo arquivos de servidores..."

    # Mover servidores MCP
    cp "${CONTINUITY_DIR}/mcp-continuity-server.py" "${CONTINUITY_DIR}/src/servers/" 2>/dev/null || true
    cp "${CONTINUITY_DIR}/mcp-continuity-server-fixed.py" "${CONTINUITY_DIR}/src/servers/" 2>/dev/null || true
    cp "${CONTINUITY_DIR}/mcp-continuity-server-broken.py" "${CONTINUITY_DIR}/src/servers/" 2>/dev/null || true
    cp "${CONTINUITY_DIR}/enterprise-mcp-server.py" "${CONTINUITY_DIR}/src/servers/" 2>/dev/null || true
    
    # Mover servidores do continuity-protocol
    if [ -d "${CONTINUITY_PROTOCOL_DIR}/server" ]; then
        cp -r "${CONTINUITY_PROTOCOL_DIR}/server"/* "${CONTINUITY_DIR}/src/servers/" 2>/dev/null || true
    fi
    
    # Mover enhanced_mcp_server.py
    if [ -f "${CONTINUITY_PROTOCOL_DIR}/enhanced_mcp_server.py" ]; then
        cp "${CONTINUITY_PROTOCOL_DIR}/enhanced_mcp_server.py" "${CONTINUITY_DIR}/src/servers/" 2>/dev/null || true
    fi
    
    log_success "Arquivos de servidores movidos"
}

# Função para mover os adaptadores
move_adapter_files() {
    log "Movendo arquivos de adaptadores..."

    # Mover adaptadores do Claude
    cp "${CONTINUITY_DIR}/claude-mcp-adapter.sh" "${CONTINUITY_DIR}/src/adapters/" 2>/dev/null || true
    cp "${CONTINUITY_DIR}/claude-mcp-guard.sh" "${CONTINUITY_DIR}/src/adapters/" 2>/dev/null || true
    
    # Mover adaptadores do continuity-protocol
    if [ -d "${CONTINUITY_PROTOCOL_DIR}/adapters" ]; then
        cp -r "${CONTINUITY_PROTOCOL_DIR}/adapters"/* "${CONTINUITY_DIR}/src/adapters/" 2>/dev/null || true
    fi
    
    # Mover adaptadores da continuity folder
    if [ -d "${CONTINUITY_PROTOCOL_DIR}/continuity/adapters" ]; then
        cp -r "${CONTINUITY_PROTOCOL_DIR}/continuity/adapters"/* "${CONTINUITY_DIR}/src/adapters/" 2>/dev/null || true
    fi
    
    log_success "Arquivos de adaptadores movidos"
}

# Função para mover os utilitários
move_utility_files() {
    log "Movendo utilitários..."

    # Mover utilitários do CONTINUITY
    cp "${CONTINUITY_DIR}/smart-cleanup.sh" "${CONTINUITY_DIR}/src/utilities/" 2>/dev/null || true
    cp "${CONTINUITY_DIR}/smart-context-detector.sh" "${CONTINUITY_DIR}/src/utilities/" 2>/dev/null || true
    cp "${CONTINUITY_DIR}/project-finder-optimized.sh" "${CONTINUITY_DIR}/src/utilities/project-finder.sh" 2>/dev/null || true
    cp "${CONTINUITY_DIR}/shared-memory-manager.sh" "${CONTINUITY_DIR}/src/utilities/" 2>/dev/null || true
    
    # Mover utilitários do continuity-protocol
    if [ -d "${CONTINUITY_PROTOCOL_DIR}/continuity/utils" ]; then
        cp -r "${CONTINUITY_PROTOCOL_DIR}/continuity/utils"/* "${CONTINUITY_DIR}/src/utilities/" 2>/dev/null || true
    fi
    
    log_success "Utilitários movidos"
}

# Função para mover os arquivos de emergência
move_emergency_files() {
    log "Movendo arquivos de emergência..."

    # Criar diretório de emergência
    mkdir -p "${CONTINUITY_DIR}/src/emergency"
    
    # Mover scripts de emergência
    cp "${CONTINUITY_DIR}/emergency-"*.sh "${CONTINUITY_DIR}/src/emergency/" 2>/dev/null || true
    
    log_success "Arquivos de emergência movidos"
}

# Função para mover arquivos de ferramentas
move_tool_files() {
    log "Movendo ferramentas específicas..."

    # Mover scripts de modo escuro
    cp "${CONTINUITY_DIR}/fix-dark-mode-systematic.sh" "${CONTINUITY_DIR}/tools/dark-mode/" 2>/dev/null || true
    cp "${CONTINUITY_DIR}/fix-all-666-colors.sh" "${CONTINUITY_DIR}/tools/dark-mode/" 2>/dev/null || true
    cp "${CONTINUITY_DIR}/integral-color-refactor.sh" "${CONTINUITY_DIR}/tools/dark-mode/" 2>/dev/null || true
    
    # Mover scripts de acessibilidade
    cp "${CONTINUITY_DIR}/accessibility-status.sh" "${CONTINUITY_DIR}/tools/accessibility/" 2>/dev/null || true
    cp "${CONTINUITY_DIR}/fix-accessibility-chapters.sh" "${CONTINUITY_DIR}/tools/accessibility/" 2>/dev/null || true
    
    log_success "Ferramentas específicas movidas"
}

# Função para mover arquivos de configuração
move_config_files() {
    log "Movendo arquivos de configuração..."

    # Mover system prompts
    cp "${CONTINUITY_DIR}/SYSTEM_PROMPT_"* "${CONTINUITY_DIR}/config/system-prompts/" 2>/dev/null || true
    cp "${CONTINUITY_DIR}/USER_"* "${CONTINUITY_DIR}/config/system-prompts/" 2>/dev/null || true
    
    # Copiar configurações do continuity-protocol
    if [ -f "${CONTINUITY_PROTOCOL_DIR}/mcp-config.json" ]; then
        cp "${CONTINUITY_PROTOCOL_DIR}/mcp-config.json" "${CONTINUITY_DIR}/config/" 2>/dev/null || true
    fi
    
    log_success "Arquivos de configuração movidos"
}

# Função para mover arquivos de scripts
move_script_files() {
    log "Movendo scripts de instalação..."

    # Mover scripts de instalação
    cp "${CONTINUITY_DIR}/install-"*.sh "${CONTINUITY_DIR}/scripts/" 2>/dev/null || true
    
    # Copiar scripts do continuity-protocol
    if [ -f "${CONTINUITY_PROTOCOL_DIR}/start_enhanced_server.sh" ]; then
        cp "${CONTINUITY_PROTOCOL_DIR}/start_"*.sh "${CONTINUITY_DIR}/scripts/" 2>/dev/null || true
    fi
    
    log_success "Scripts de instalação movidos"
}

# Função para mover arquivos de documentação
move_doc_files() {
    log "Movendo documentação..."

    # Mover READMEs para documentação
    cp "${CONTINUITY_DIR}/README"* "${CONTINUITY_DIR}/docs/" 2>/dev/null || true
    
    # Organizar documentação
    cp "${CONTINUITY_DIR}/README-CLAUDE-INTEGRATION.md" "${CONTINUITY_DIR}/docs/integration/" 2>/dev/null || true
    cp "${CONTINUITY_DIR}/README-SHARED-MEMORY.md" "${CONTINUITY_DIR}/docs/integration/" 2>/dev/null || true
    
    # Copiar documentação do continuity-protocol
    if [ -d "${CONTINUITY_PROTOCOL_DIR}/docs" ]; then
        cp -r "${CONTINUITY_PROTOCOL_DIR}/docs"/* "${CONTINUITY_DIR}/docs/" 2>/dev/null || true
    fi
    
    log_success "Documentação movida"
}

# Função para criar o servidor MCP unificado
create_unified_server() {
    log "Criando servidor MCP unificado..."

    cat > "${CONTINUITY_DIR}/src/servers/unified-mcp-server.py" << 'EOF'
#!/usr/bin/env python3
"""
Unified MCP Server - Combines functionality from both CONTINUITY and continuity-protocol
"""

import os
import sys
import json
import time
import subprocess
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from pathlib import Path

# Base paths
CONTINUITY_BASE = "/Users/lucascardoso/apps/MCP/CONTINUITY"
SCRIPTS_PATH = os.path.join(CONTINUITY_BASE, "src")

# Add paths to sys.path
sys.path.append(CONTINUITY_BASE)
sys.path.append(os.path.join(CONTINUITY_BASE, "src"))

# Try to import FastMCP
try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    print("Installing MCP...")
    subprocess.run([sys.executable, "-m", "pip", "install", "mcp"])
    from mcp.server.fastmcp import FastMCP

# Try to import enhanced context protocol
try:
    from core.mcp.integration_v2 import enhanced_context_protocol
    from core.mcp.versioning import versioning_system
    from core.mcp.backup import backup_system
    from core.mcp.notification import notification_system
    from core.mcp.search import search_system
    from core.mcp.safeguards import safeguards
    ENHANCED_CONTEXT_AVAILABLE = True
except ImportError:
    print("Enhanced context protocol not available, some features will be limited")
    ENHANCED_CONTEXT_AVAILABLE = False

class UnifiedMCPServer:
    """
    Unified MCP Server that combines functionality from CONTINUITY and continuity-protocol
    """
    
    def __init__(self, server_name: str = "unified-continuity-protocol"):
        """
        Initialize the unified MCP server
        
        Args:
            server_name: Name of the MCP server
        """
        self.server_name = server_name
        
        # Initialize FastMCP
        self.mcp = FastMCP(server_name)
        
        # Store base paths
        self.continuity_base = CONTINUITY_BASE
        self.scripts_path = SCRIPTS_PATH
        
        # Initialize enhanced context protocol if available
        self.enhanced_context_available = ENHANCED_CONTEXT_AVAILABLE
        if self.enhanced_context_available:
            self.context_protocol = enhanced_context_protocol
        
        # Register tools
        self._register_tools()
        
        # Save PID for management
        self._save_pid()
        
        print(f"Unified MCP Server initialized with name: {server_name}")
        print(f"CONTINUITY base: {self.continuity_base}")
        print(f"Enhanced context available: {self.enhanced_context_available}")
    
    def _save_pid(self):
        """Save PID to file for management"""
        pid_file = os.path.join(self.continuity_base, "unified-mcp-server.pid")
        with open(pid_file, "w") as f:
            f.write(str(os.getpid()))
    
    def _register_tools(self) -> None:
        """Register all MCP tools"""
        
        # Register CONTINUITY bash tools
        self._register_continuity_bash_tools()
        
        # Register enhanced context tools if available
        if self.enhanced_context_available:
            self._register_enhanced_context_tools()
    
    def _register_continuity_bash_tools(self) -> None:
        """Register CONTINUITY bash script tools"""
        
        def run_bash_script(script_name: str, args: List[str] = None) -> Dict[str, Any]:
            """Execute bash script and return structured result"""
            try:
                script_path = f"{self.scripts_path}/{script_name}"
                
                if not os.path.exists(script_path):
                    return {
                        "error": f"Script not found: {script_path}",
                        "success": False
                    }
                
                cmd = [script_path]
                if args:
                    cmd.extend(args)
                
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
                return {
                    "error": "Script execution timeout",
                    "success": False
                }
            except Exception as e:
                return {
                    "error": f"Execution error: {str(e)}",
                    "success": False
                }
        
        @self.mcp.tool()
        def continuity_where_stopped() -> str:
            """Execute 'onde paramos?' - automatic recovery and context loading"""
            result = run_bash_script("core/autonomous-recovery.sh")
            
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
            """Process user input through magic detection system"""
            result = run_bash_script("utilities/smart-context-detector.sh", [user_input])
            
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
            """Create emergency backup freeze of current state"""
            result = run_bash_script("emergency/emergency-freeze.sh")
            
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
            """Restore from emergency backup freeze"""
            result = run_bash_script("emergency/emergency-unfreeze.sh")
            
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
            """Get complete system status and project overview"""
            result = run_bash_script("utilities/smart-context-detector.sh", ["status"])
            
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
    
    def _register_enhanced_context_tools(self) -> None:
        """Register enhanced context protocol tools if available"""
        if not self.enhanced_context_available:
            return
        
        # Artifact tools
        @self.mcp.tool()
        def context_register_project(project_id: str, project_name: str, description: str) -> str:
            """
            Register a project in the context sharing protocol
            
            Args:
                project_id: Project ID
                project_name: Project name
                description: Project description
                
            Returns:
                str: Operation result in JSON format
            """
            try:
                project_info = self.context_protocol.register_project(project_id, project_name, description)
                return json.dumps(project_info, indent=2)
            except Exception as e:
                return json.dumps({"error": str(e)}, indent=2)
        
        @self.mcp.tool()
        def context_store_artifact(content: str, artifact_type: str, project_id: str, metadata_json: str = "{}") -> str:
            """
            Store an artifact in the context sharing protocol
            
            Args:
                content: Artifact content
                artifact_type: Artifact type (e.g., "plan", "code", "document")
                project_id: Project ID
                metadata_json: Additional metadata in JSON format (optional)
                
            Returns:
                str: Operation result in JSON format
            """
            try:
                # Parse metadata
                try:
                    metadata = json.loads(metadata_json)
                except:
                    metadata = {}
                
                # Store artifact
                artifact_info = self.context_protocol.store_artifact(
                    content,
                    artifact_type,
                    project_id,
                    "unified_mcp_server",
                    metadata
                )
                
                return json.dumps(artifact_info, indent=2)
            except Exception as e:
                return json.dumps({"error": str(e)}, indent=2)
        
        @self.mcp.tool()
        def context_get_project_context(project_id: str) -> str:
            """
            Get the complete context of a project
            
            Args:
                project_id: Project ID
                
            Returns:
                str: Complete project context in JSON format
            """
            try:
                context = self.context_protocol.get_project_context(project_id)
                return json.dumps(context, indent=2)
            except Exception as e:
                return json.dumps({"error": str(e)}, indent=2)
        
        @self.mcp.tool()
        def context_create_backup(backup_type: str = "auto") -> str:
            """
            Create system backup
            
            Args:
                backup_type: Backup type ("full", "auto", "incremental")
                
            Returns:
                str: Created backup information in JSON format
            """
            try:
                result = backup_system.create_backup(backup_type)
                return json.dumps(result, indent=2)
            except Exception as e:
                return json.dumps({"error": str(e)}, indent=2)
        
        @self.mcp.tool()
        def context_get_system_status() -> str:
            """
            Get complete system status
            
            Returns:
                str: System status in JSON format
            """
            try:
                status = {
                    "safeguards": safeguards.get_status(),
                    "search": search_system.get_index_stats(),
                    "backups": backup_system.get_backups_list(),
                    "notifications": notification_system.get_notifications(limit=5)["notifications"],
                    "server_name": self.server_name,
                    "timestamp": datetime.now().isoformat()
                }
                return json.dumps(status, indent=2)
            except Exception as e:
                return json.dumps({"error": str(e)}, indent=2)
    
    def run(self, transport: str = "stdio") -> None:
        """
        Run the MCP server
        
        Args:
            transport: Transport type ("stdio" or "http")
        """
        print(f"Starting Unified MCP Server ({self.server_name})")
        print(f"Transport: {transport}")
        
        # Create initial checkpoint if enhanced context is available
        if self.enhanced_context_available:
            safeguards.create_checkpoint("startup")
        
        # Run MCP server
        self.mcp.run(transport=transport)

if __name__ == "__main__":
    # Default parameters
    server_name = "unified-continuity-protocol"
    transport = "stdio"
    
    # Process command line arguments
    if len(sys.argv) > 1:
        server_name = sys.argv[1]
    if len(sys.argv) > 2:
        transport = sys.argv[2]
    
    # Create and run server
    server = UnifiedMCPServer(server_name)
    server.run(transport=transport)
EOF

    chmod +x "${CONTINUITY_DIR}/src/servers/unified-mcp-server.py"
    log_success "Servidor MCP unificado criado"
}

# Função para criar script de inicialização do servidor unificado
create_startup_script() {
    log "Criando script de inicialização..."

    cat > "${CONTINUITY_DIR}/scripts/start-unified-server.sh" << 'EOF'
#!/bin/bash
# Script para iniciar o servidor MCP unificado

CONTINUITY_DIR="/Users/lucascardoso/apps/MCP/CONTINUITY"
SERVER_SCRIPT="${CONTINUITY_DIR}/src/servers/unified-mcp-server.py"
LOG_FILE="${CONTINUITY_DIR}/logs/unified-server.log"
PID_FILE="${CONTINUITY_DIR}/unified-mcp-server.pid"

# Cores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Criar diretório de logs se não existir
mkdir -p "$(dirname "$LOG_FILE")"

# Verificar se o servidor já está em execução
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null; then
        echo -e "${RED}Servidor já está em execução com PID $PID${NC}"
        echo "Use: ${CONTINUITY_DIR}/scripts/stop-unified-server.sh para parar"
        exit 1
    else
        echo "Removendo PID file antigo..."
        rm -f "$PID_FILE"
    fi
fi

# Iniciar o servidor
echo -e "${BLUE}Iniciando servidor MCP unificado...${NC}"
nohup python3 "$SERVER_SCRIPT" > "$LOG_FILE" 2>&1 &
PID=$!
echo $PID > "$PID_FILE"

# Verificar se o servidor iniciou corretamente
sleep 2
if ps -p "$PID" > /dev/null; then
    echo -e "${GREEN}Servidor iniciado com sucesso!${NC}"
    echo "PID: $PID"
    echo "Log: $LOG_FILE"
    echo "Para parar o servidor: ${CONTINUITY_DIR}/scripts/stop-unified-server.sh"
else
    echo -e "${RED}Falha ao iniciar o servidor${NC}"
    echo "Verifique o log: $LOG_FILE"
    rm -f "$PID_FILE"
    exit 1
fi
EOF

    chmod +x "${CONTINUITY_DIR}/scripts/start-unified-server.sh"

    # Criar script para parar o servidor
    cat > "${CONTINUITY_DIR}/scripts/stop-unified-server.sh" << 'EOF'
#!/bin/bash
# Script para parar o servidor MCP unificado

PID_FILE="/Users/lucascardoso/apps/MCP/CONTINUITY/unified-mcp-server.pid"

# Cores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Verificar se o arquivo PID existe
if [ ! -f "$PID_FILE" ]; then
    echo -e "${RED}Servidor não está em execução (arquivo PID não encontrado)${NC}"
    exit 1
fi

# Ler o PID
PID=$(cat "$PID_FILE")

# Verificar se o processo existe
if ! ps -p "$PID" > /dev/null; then
    echo -e "${RED}Processo com PID $PID não está em execução${NC}"
    rm -f "$PID_FILE"
    exit 1
fi

# Parar o processo
echo "Parando servidor MCP com PID $PID..."
kill "$PID"

# Verificar se o processo foi encerrado
sleep 2
if ps -p "$PID" > /dev/null; then
    echo -e "${RED}Falha ao parar o servidor. Forçando encerramento...${NC}"
    kill -9 "$PID"
    sleep 1
fi

# Verificar novamente
if ps -p "$PID" > /dev/null; then
    echo -e "${RED}Não foi possível encerrar o processo com PID $PID${NC}"
    exit 1
else
    echo -e "${GREEN}Servidor parado com sucesso${NC}"
    rm -f "$PID_FILE"
fi
EOF

    chmod +x "${CONTINUITY_DIR}/scripts/stop-unified-server.sh"
    log_success "Scripts de inicialização criados"
}

# Função para criar script de integração com Claude Desktop
create_claude_integration_script() {
    log "Criando script de integração com Claude Desktop..."

    cat > "${CONTINUITY_DIR}/scripts/setup-claude-desktop.sh" << 'EOF'
#!/bin/bash
# Script para configurar a integração com Claude Desktop

HOME_DIR="/Users/lucascardoso"
CONTINUITY_DIR="${HOME_DIR}/apps/MCP/CONTINUITY"
CLAUDE_CONFIG_DIR="${HOME_DIR}/Library/Application Support/Claude"
CLAUDE_CONFIG_FILE="${CLAUDE_CONFIG_DIR}/claude_desktop_config.json"
SERVER_NAME="unified-continuity-protocol"
SERVER_PORT=3457

# Cores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar se o diretório de configuração do Claude existe
if [ ! -d "$CLAUDE_CONFIG_DIR" ]; then
    echo "Criando diretório de configuração do Claude..."
    mkdir -p "$CLAUDE_CONFIG_DIR"
fi

# Verificar se o arquivo de configuração existe
if [ ! -f "$CLAUDE_CONFIG_FILE" ]; then
    echo "Criando arquivo de configuração básico do Claude..."
    echo '{
  "mcpServers": {}
}' > "$CLAUDE_CONFIG_FILE"
fi

# Verificar se o arquivo é um JSON válido
if ! command -v jq &> /dev/null; then
    echo -e "${RED}jq não está instalado. Por favor, instale para continuar:${NC}"
    echo "brew install jq"
    exit 1
fi

if ! jq empty "$CLAUDE_CONFIG_FILE" 2>/dev/null; then
    echo -e "${RED}Arquivo de configuração do Claude não é um JSON válido${NC}"
    echo "Fazendo backup e criando um novo..."
    cp "$CLAUDE_CONFIG_FILE" "${CLAUDE_CONFIG_FILE}.bak.$(date +%Y%m%d%H%M%S)"
    echo '{
  "mcpServers": {}
}' > "$CLAUDE_CONFIG_FILE"
fi

# Adicionar ou atualizar a configuração do servidor
echo "Configurando servidor MCP no Claude Desktop..."
TMP_FILE=$(mktemp)

# Ler configuração atual e adicionar/atualizar o servidor
jq --arg name "$SERVER_NAME" --arg cmd "python3" --arg arg "${CONTINUITY_DIR}/src/servers/unified-mcp-server.py" '
.mcpServers[$name] = {
  "command": $cmd,
  "args": [$arg],
  "description": "Unified Continuity Protocol - Servidor MCP"
}
' "$CLAUDE_CONFIG_FILE" > "$TMP_FILE"

# Verificar se o JSON resultante é válido
if jq empty "$TMP_FILE" 2>/dev/null; then
    mv "$TMP_FILE" "$CLAUDE_CONFIG_FILE"
    echo -e "${GREEN}Servidor MCP configurado com sucesso no Claude Desktop!${NC}"
    echo "Nome: $SERVER_NAME"
    echo "Comando: python3 ${CONTINUITY_DIR}/src/servers/unified-mcp-server.py"
else
    echo -e "${RED}Falha ao criar configuração JSON válida${NC}"
    rm -f "$TMP_FILE"
    exit 1
fi

echo -e "${YELLOW}IMPORTANTE:${NC} Reinicie o Claude Desktop para aplicar as mudanças"
echo "Após reiniciar, você pode testar o servidor em:"
echo "Configurações > Integrações > $SERVER_NAME"
EOF

    chmod +x "${CONTINUITY_DIR}/scripts/setup-claude-desktop.sh"
    log_success "Script de integração com Claude Desktop criado"
}

# Função para criar README unificado
create_unified_readme() {
    log "Criando README unificado..."

    cat > "${CONTINUITY_DIR}/README.md" << 'EOF'
# Continuity Protocol

O Continuity Protocol é uma implementação cibernética do Model Context Protocol (MCP) projetada para manter o contexto entre diferentes LLMs (Large Language Models) e ambientes de desenvolvimento.

## Visão Geral

Este projeto unifica duas implementações:
1. CONTINUITY - Ferramentas de linha de comando e scripts bash para gerenciamento de estado
2. continuity-protocol - Implementação Python do protocolo de continuidade com recursos avançados

## Estrutura do Projeto

```
/CONTINUITY/
├── src/               # Código-fonte principal
│   ├── core/          # Funcionalidades principais
│   ├── servers/       # Implementações de servidores
│   ├── adapters/      # Adaptadores para LLMs
│   └── utilities/     # Scripts utilitários
├── tools/             # Ferramentas específicas de projeto
├── config/            # Arquivos de configuração
├── bin/               # Executáveis de linha de comando
├── scripts/           # Scripts de instalação e execução
├── docs/              # Documentação
└── backups/           # Armazenamento de backups
```

## Instalação

Para instalar e configurar o Continuity Protocol:

```bash
cd /Users/lucascardoso/apps/MCP/CONTINUITY
./scripts/setup-claude-desktop.sh   # Configurar integração com Claude Desktop
./scripts/start-unified-server.sh   # Iniciar o servidor MCP unificado
```

## Integração com Claude Desktop

Este projeto inclui integração nativa com o Claude Desktop. Após a configuração, você terá acesso às seguintes ferramentas:

- `continuity_where_stopped` - Detecta onde o trabalho foi interrompido
- `continuity_magic_system` - Processa entrada do usuário pelo sistema de detecção
- `continuity_emergency_freeze` - Cria backup de emergência
- `continuity_emergency_unfreeze` - Restaura a partir de backup de emergência
- `context_register_project` - Registra um novo projeto
- `context_store_artifact` - Armazena um artefato no contexto compartilhado
- `context_get_project_context` - Obtém o contexto completo de um projeto

## Uso

Exemplos de uso com o Claude Desktop:

1. **Iniciar uma sessão:**
   ```
   /tools continuity_where_stopped
   ```

2. **Criar um backup de emergência:**
   ```
   /tools continuity_emergency_freeze
   ```

3. **Registrar um projeto:**
   ```
   /tools context_register_project project_id="meu-projeto" project_name="Meu Projeto" description="Descrição do projeto"
   ```

## Scripts Principais

- `start-unified-server.sh` - Inicia o servidor MCP unificado
- `stop-unified-server.sh` - Para o servidor MCP unificado
- `setup-claude-desktop.sh` - Configura a integração com Claude Desktop

## Licença

MIT License
EOF

    log_success "README unificado criado"
}

# Função principal
main() {
    log "Iniciando reorganização do Continuity Protocol..."
    
    # Verificar dependências
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 não encontrado. Por favor, instale para continuar."
        exit 1
    fi
    
    # Criar diretórios
    create_directories
    
    # Backup dos arquivos atuais
    backup_current_files
    
    # Mover arquivos
    move_core_files
    move_server_files
    move_adapter_files
    move_utility_files
    move_emergency_files
    move_tool_files
    move_config_files
    move_script_files
    move_doc_files
    
    # Criar servidor unificado
    create_unified_server
    
    # Criar script de inicialização
    create_startup_script
    
    # Criar script de integração com Claude Desktop
    create_claude_integration_script
    
    # Criar README unificado
    create_unified_readme
    
    log_success "Reorganização concluída com sucesso!"
    echo ""
    echo -e "${GREEN}Próximos passos:${NC}"
    echo "1. Revisar a estrutura criada"
    echo "2. Executar o script de integração com Claude Desktop:"
    echo "   ${CONTINUITY_DIR}/scripts/setup-claude-desktop.sh"
    echo "3. Iniciar o servidor MCP unificado:"
    echo "   ${CONTINUITY_DIR}/scripts/start-unified-server.sh"
    echo ""
    echo -e "${YELLOW}NOTA:${NC} Um backup completo dos arquivos originais foi criado em:"
    echo "${BACKUP_DIR}"
}

# Executar o script
main